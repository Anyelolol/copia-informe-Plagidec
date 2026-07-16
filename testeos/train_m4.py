import os
import json
import torch
import numpy as np
from itertools import chain
from pathlib import Path
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split

MODEL_BASE   = "mrm8488/electricidad-small-discriminator"
OUTPUT_DIR   = Path("./modelo_detector_es")
LOG_DIR      = Path("./logs_entrenamiento_es")
MAX_LENGTH   = 192
BATCH_SIZE   = 16
EPOCHS       = 4
LR           = 3e-5
WARMUP_RATIO = 0.1
SEED         = 42
LABELS       = {0: "humano", 1: "IA"}

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

def log(m): print(m, flush=True)

def check_gpu():
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1e9
        log(f"GPU detectada: {name} ({vram:.1f} GB VRAM)")
        return BATCH_SIZE if vram >= 3.5 else 8
    log("WARNING: Sin GPU detectada. Entrenando en CPU (será muy lento).")
    return 4

def cargar_dataset_es(max_por_clase=6000):
    log("\n" + "="*50)
    log("INICIANDO DESCARGA Y FILTRADO DE DATOS")
    log("="*50)
    log("Conectando con HuggingFace para descargar OpenAssistant...")

    textos, etiquetas = [], []

    try:
        ds_train = load_dataset("OpenAssistant/oasst1", split="train", streaming=True)
        ds_val = load_dataset("OpenAssistant/oasst1", split="validation", streaming=True)
        ds = chain(ds_train, ds_val)
        count_h, count_ia = 0, 0
        vistos = 0

        for ex in ds:
            vistos += 1
            if vistos % 5000 == 0:
                log(f"  -> Revisados {vistos:,} mensajes... (ES: {count_h} humanos, {count_ia} IA)")

            lang = ex.get("lang", "").lower().strip()
            if lang != "es":
                continue

            texto = (ex.get("text") or "").strip()
            role = ex.get("role", "").strip()

            if not texto or len(texto) < 50:
                continue

            if role == "prompter" and count_h < max_por_clase:
                textos.append(texto)
                etiquetas.append(0)
                count_h += 1
            elif role == "assistant" and count_ia < max_por_clase:
                textos.append(texto)
                etiquetas.append(1)
                count_ia += 1

            if count_h >= max_por_clase and count_ia >= max_por_clase:
                log(f"  ¡Objetivo alcanzado! Total revisado: {vistos:,}")
                break

        log(f"\n  Filtrado completado:")
        log(f"  Textos humanos (ES): {count_h:,}")
        log(f"  Textos IA (ES):      {count_ia:,}")

    except Exception as e:
        log(f"\nOpenAssistant falló: {e}")
        log("Iniciando dataset de RESPALDO (Alpaca-es vs Wikipedia-es)...")

        try:
            ds_ia = load_dataset("somosnlp/somos-clean-alpaca-es", split="train", streaming=True)
            count_ia = 0
            for ex in ds_ia:
                resp = (ex.get("output") or "").strip()
                if resp and len(resp) > 50 and count_ia < max_por_clase:
                    textos.append(resp)
                    etiquetas.append(1)
                    count_ia += 1
                if count_ia >= max_por_clase: break
        except Exception as e:
            log(f"  Respaldo IA (Alpaca) falló: {e}")

        try:
            ds_h = load_dataset("wikimedia/wikipedia", "20231101.es", split="train", streaming=True)
            count_h = 0
            for ex in ds_h:
                t = (ex.get("text") or "").strip().split("\n")[0][:1500]
                if t and len(t) > 80 and count_h < max_por_clase:
                    textos.append(t)
                    etiquetas.append(0)
                    count_h += 1
                if count_h >= max_por_clase: break
        except Exception as e:
            log(f"  Respaldo Humano (Wikipedia) falló: {e}")

        log(f"  Respaldo: Humanos={count_h:,} | IA={count_ia:,}")

    if len(textos) < 1000:
        raise RuntimeError("No se pudieron descargar suficientes datos en español.")

    return {"text": textos, "label": etiquetas}

def crear_splits(ejemplos):
    log("\nDividiendo datos en Train/Val/Test...")
    tx, t_test, lx, l_test = train_test_split(
        ejemplos["text"], ejemplos["label"],
        test_size=0.10, stratify=ejemplos["label"], random_state=SEED)
    t_train, t_val, l_train, l_val = train_test_split(
        tx, lx, test_size=0.111, stratify=lx, random_state=SEED)
    log(f"Splits -> Train: {len(t_train):,} | Val: {len(t_val):,} | Test: {len(t_test):,}")
    return (t_train, l_train), (t_val, l_val), (t_test, l_test)

class TextDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __len__(self): return len(self.labels)
    def __getitem__(self, i):
        item = {k: torch.tensor(v[i]) for k, v in self.encodings.items()}
        item["labels"] = torch.tensor(self.labels[i])
        return item

def tokenizar(tokenizer, textos, labels):
    log("  Convirtiendo texto a números (Tokenizando)...")
    enc = tokenizer(textos, truncation=True, padding="max_length",
                    max_length=MAX_LENGTH, return_tensors=None)
    return TextDataset(enc, labels)

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": accuracy_score(labels, preds),
            "f1": f1_score(labels, preds, average="weighted")}

def cuantizar_y_guardar(modelo, tokenizer, final_dir):
    log(f"\nAplicando cuantización INT8 para reducir tamaño...")
    final_dir = Path(final_dir)
    final_dir.mkdir(parents=True, exist_ok=True)

    modelo_cpu = modelo.to("cpu")

    quantized = torch.quantization.quantize_dynamic(
        modelo_cpu,
        {torch.nn.Linear},
        dtype=torch.qint8
    )

    torch.save(quantized.state_dict(), final_dir / "pytorch_model.bin")
    tokenizer.save_pretrained(str(final_dir))

    with open(final_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "model_base": MODEL_BASE,
            "max_length": MAX_LENGTH,
            "labels": LABELS,
            "quantized": True,
            "dataset": "OpenAssistant-ES (o respaldo)"
        }, f, indent=2, ensure_ascii=False)

    tam_mb = (final_dir / "pytorch_model.bin").stat().st_size / 1e6
    log(f"✓ Modelo guardado. Tamaño final: {tam_mb:.1f} MB")
    return tam_mb

def entrenar():
    log("\n" + "#"*50)
    log("# INICIANDO SISTEMA DE DETECCIÓN IA vs HUMANO #")
    log("#"*50)

    batch = check_gpu()
    ejemplos = cargar_dataset_es(max_por_clase=6000)
    train_data, val_data, test_data = crear_splits(ejemplos)

    log(f"\nCargando modelo base: {MODEL_BASE}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_BASE)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_BASE, num_labels=2,
        id2label=LABELS,
        label2id={v: k for k, v in LABELS.items()},
    )

    log("\nPreparando datasets para la GPU...")
    ds_train = tokenizar(tokenizer, train_data[0], train_data[1])
    ds_val   = tokenizar(tokenizer, val_data[0],   val_data[1])
    ds_test  = tokenizar(tokenizer, test_data[0],  test_data[1])

    steps = max(len(ds_train) // batch, 1)
    eval_steps = max(steps // 4, 50)

    args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=batch,
        per_device_eval_batch_size=batch * 2,
        learning_rate=LR,
        warmup_ratio=WARMUP_RATIO,
        weight_decay=0.01,
        eval_strategy="steps",
        eval_steps=eval_steps,
        save_strategy="steps",
        save_steps=eval_steps,
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        logging_dir=str(LOG_DIR),
        logging_steps=10,
        logging_first_step=True,
        fp16=torch.cuda.is_available(),
        dataloader_num_workers=2,
        seed=SEED,
        report_to="none",
        save_total_limit=1,
        disable_tqdm=False
    )

    trainer = Trainer(
        model=model, args=args,
        train_dataset=ds_train,
        eval_dataset=ds_val,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )

    log("\n" + "="*50)
    log("EMPEZANDO EL ENTRENAMIENTO DE LA RED NEURONAL")
    log("="*50)
    trainer.train()

    log("\nEvaluando modelo final en Test Set...")
    res = trainer.evaluate(ds_test)
    log(f"  Accuracy: {res['eval_accuracy']:.4f}")
    log(f"  F1 Score: {res['eval_f1']:.4f}")

    preds = trainer.predict(ds_test)
    y_pred = np.argmax(preds.predictions, axis=-1)
    log("\nReporte de Clasificación:")
    log(classification_report(test_data[1], y_pred, target_names=["Humano", "IA"]))

    final_dir = OUTPUT_DIR / "final"
    cuantizar_y_guardar(trainer.model, tokenizer, final_dir)

    log("\n" + "="*50)
    log("✓ PROCESO COMPLETADO CON ÉXITO.")
    log(f"✓ Modelo disponible en: {final_dir.resolve()}")
    log("="*50)

if __name__ == "__main__":
    entrenar()
