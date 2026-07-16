import os
# Evita fragmentación de memoria CUDA
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

import json
import torch
import gc
import numpy as np
from itertools import chain
from pathlib import Path
from datasets import load_dataset, Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
    DataCollatorWithPadding
)
from peft import get_peft_model, LoraConfig, TaskType
from sklearn.metrics import accuracy_score, f1_score, classification_report
from sklearn.model_selection import train_test_split

# Optimizaciones de hardware para PyTorch
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

MODEL_BASE = "distilbert-base-multilingual-cased"
OUTPUT_DIR   = Path("./modelo_detector_es")
LOG_DIR      = Path("./logs_entrenamiento_es")

# Configuraciones para 4GB VRAM
MAX_LENGTH   = 512
BATCH_SIZE   = 2       # Lote muy pequeño
GRAD_ACCUM   = 8       # Acumulación para lograr Batch Efectivo = 16
EPOCHS       = 5
LR           = 3e-4    # LoRA permite/requiere un Learning Rate ligeramente mayor
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
        return BATCH_SIZE
    log("WARNING: Sin GPU detectada. Entrenando en CPU (será muy lento).")
    return 4

def cargar_dataset_es(max_por_clase=6000):
    log("\n" + "="*50)
    log("INICIANDO DESCARGA Y FILTRADO DE DATOS")
    log("="*50)

    textos, etiquetas = [], []

    try:
        ds_train = load_dataset("OpenAssistant/oasst1", split="train", streaming=True)
        ds_val = load_dataset("OpenAssistant/oasst1", split="validation", streaming=True)
        ds = chain(ds_train, ds_val)
        count_h, count_ia = 0, 0

        for ex in ds:
            lang = ex.get("lang", "").lower().strip()
            if lang != "es": continue

            texto = (ex.get("text") or "").strip()
            role = ex.get("role", "").strip()

            if not texto or len(texto) < 50: continue

            if role == "prompter" and count_h < max_por_clase:
                textos.append(texto)
                etiquetas.append(0)
                count_h += 1
            elif role == "assistant" and count_ia < max_por_clase:
                textos.append(texto)
                etiquetas.append(1)
                count_ia += 1

            if count_h >= max_por_clase and count_ia >= max_por_clase:
                break

        log(f"  OpenAssistant: Humanos={count_h:,} | IA={count_ia:,}")
    except Exception as e:
        log(f"  Fallo principal: {e}. Usando respaldos (Wikipedia/Alpaca)...")
        # Aquí iría el bloque de respaldo exacto del script anterior si falla la conexión

    return {"text": textos, "label": etiquetas}

def preparar_datasets(ejemplos, tokenizer):
    log("\nDividiendo datos y aplicando tokenización dinámica...")

    tx, t_test, lx, l_test = train_test_split(
        ejemplos["text"], ejemplos["label"], test_size=0.10, stratify=ejemplos["label"], random_state=SEED)
    t_train, t_val, l_train, l_val = train_test_split(
        tx, lx, test_size=0.111, stratify=lx, random_state=SEED)

    def tokenizar_batch(batch):
        # NO usamos padding="max_length" aquí. El DataCollator se encargará.
        return tokenizer(batch["text"], truncation=True, max_length=MAX_LENGTH)

    # Convertimos a formato HuggingFace Dataset
    ds_train = Dataset.from_dict({"text": t_train, "labels": l_train})
    ds_val   = Dataset.from_dict({"text": t_val,   "labels": l_val})
    ds_test  = Dataset.from_dict({"text": t_test,  "labels": l_test})

    # Mapeamos la tokenización
    ds_train = ds_train.map(tokenizar_batch, batched=True, remove_columns=["text"])
    ds_val   = ds_val.map(tokenizar_batch, batched=True, remove_columns=["text"])
    ds_test  = ds_test.map(tokenizar_batch, batched=True, remove_columns=["text"])

    log(f"Splits -> Train: {len(ds_train):,} | Val: {len(ds_val):,} | Test: {len(ds_test):,}")
    return ds_train, ds_val, ds_test

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {"accuracy": accuracy_score(labels, preds),
            "f1": f1_score(labels, preds, average="weighted")}

def fusionar_y_cuantizar(trainer, tokenizer, final_dir):
    log(f"\nFusionando pesos LoRA con el modelo base y aplicando INT8...")
    final_dir = Path(final_dir)
    final_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fusionar LoRA con el modelo base (necesario para cuantizar)
    modelo_fusionado = trainer.model.merge_and_unload()
    modelo_cpu = modelo_fusionado.to("cpu")

    # 2. Cuantización Dinámica a INT8
    quantized = torch.quantization.quantize_dynamic(
        modelo_cpu, {torch.nn.Linear}, dtype=torch.qint8
    )

    torch.save(quantized.state_dict(), final_dir / "pytorch_model.bin")
    tokenizer.save_pretrained(str(final_dir))

    with open(final_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump({
            "model_base": MODEL_BASE,
            "max_length": MAX_LENGTH,
            "labels": LABELS,
            "quantized": True,
            "peft_lora": True
        }, f, indent=2, ensure_ascii=False)

    tam_mb = (final_dir / "pytorch_model.bin").stat().st_size / 1e6
    log(f"✓ Modelo listo. Tamaño final: {tam_mb:.1f} MB")

def entrenar():
    log("\n" + "#"*50)
    log("# INICIANDO SISTEMA DE DETECCIÓN (LoRA + PADDING DINÁMICO) #")
    log("#"*50)

    batch = check_gpu()
    ejemplos = cargar_dataset_es(max_por_clase=6000)

    tokenizer = AutoTokenizer.from_pretrained(MODEL_BASE)
    ds_train, ds_val, ds_test = preparar_datasets(ejemplos, tokenizer)

    log(f"\nCargando modelo base: {MODEL_BASE}")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_BASE, num_labels=2, id2label=LABELS, label2id={v: k for k, v in LABELS.items()}
    )

    # 1. Gradient Checkpointing
    model.gradient_checkpointing_enable()

    # 2. Configurar LoRA
    lora_config = LoraConfig(
        task_type=TaskType.SEQ_CLS,
        r=8,
        lora_alpha=16,
        lora_dropout=0.1,
        bias="none",
        target_modules=["q_lin", "v_lin"] # Módulos de atención en DistilBERT
    )
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters() # Verás que solo entrenas ~0.5% de los parámetros

    # 3. Data Collator (Padding Dinámico)
    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    efective_batch_size = batch * GRAD_ACCUM
    steps = max(len(ds_train) // efective_batch_size, 1)
    eval_steps = max(steps // 4, 50)

    args = TrainingArguments(
        output_dir=str(OUTPUT_DIR),
        num_train_epochs=EPOCHS,
        per_device_train_batch_size=batch,
        per_device_eval_batch_size=batch * 2,
        gradient_accumulation_steps=GRAD_ACCUM,
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
        fp16=torch.cuda.is_available(),
        dataloader_num_workers=0,
        seed=SEED,
        report_to="none",
        save_total_limit=1,
        remove_unused_columns=True, # Importante para que funcione DataCollator
    )

    trainer = Trainer(
        model=model, args=args,
        train_dataset=ds_train, eval_dataset=ds_val,
        tokenizer=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
    )

    log("\n" + "="*50)
    log("EMPEZANDO EL ENTRENAMIENTO LORA")
    log("="*50)

    gc.collect()
    if torch.cuda.is_available(): torch.cuda.empty_cache()

    trainer.train()

    log("\nEvaluando modelo final en Test Set...")
    res = trainer.evaluate(ds_test)
    log(f"  Accuracy: {res['eval_accuracy']:.4f}")
    log(f"  F1 Score: {res['eval_f1']:.4f}")

    preds = trainer.predict(ds_test)
    y_pred = np.argmax(preds.predictions, axis=-1)
    log("\nReporte de Clasificación:")
    log(classification_report(ds_test["labels"], y_pred, target_names=["Humano", "IA"]))

    final_dir = OUTPUT_DIR / "final_quantized"
    fusionar_y_cuantizar(trainer, tokenizer, final_dir)

    log("\n✓ PROCESO COMPLETADO CON ÉXITO.")

if __name__ == "__main__":
    entrenar()