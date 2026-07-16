import torch
from pathlib import Path
from collections import Counter
from pypdf import PdfReader
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    AutoConfig,
)

# ==========================================================
# CONFIGURACIÓN
# ==========================================================

MODEL_DIR = "/var/home/leaf/PycharmProjects/Proyecto-Plagiec/backend-ia/models/modelo_detector_es_final"

PDF = "/home/leaf/Imágenes/eval DFDanterior _2.pdf"

# Aproximadamente 180 palabras por bloque
PALABRAS_POR_BLOQUE = 180


# ==========================================================
# CARGAR MODELO INT8
# ==========================================================

def cargar_modelo(model_dir):

    print("Cargando configuración...")

    config = AutoConfig.from_pretrained(model_dir)

    modelo = AutoModelForSequenceClassification.from_config(config)

    print("Aplicando cuantización dinámica...")

    modelo = torch.quantization.quantize_dynamic(
        modelo,
        {torch.nn.Linear},
        dtype=torch.qint8
    )

    print("Cargando pesos...")

    state_dict = torch.load(
        f"{model_dir}/pytorch_model.bin",
        map_location="cpu"
    )

    modelo.load_state_dict(state_dict)

    modelo.eval()

    tokenizer = AutoTokenizer.from_pretrained(model_dir)

    return modelo, tokenizer


# ==========================================================
# PREDECIR
# ==========================================================

def predecir(texto, modelo, tokenizer):

    inputs = tokenizer(
        texto,
        return_tensors="pt",
        truncation=True,
        max_length=192,
    )

    with torch.no_grad():
        logits = modelo(**inputs).logits

    probs = torch.softmax(logits, dim=-1)[0]

    pred = int(torch.argmax(probs))

    return (
        modelo.config.id2label[pred],
        float(probs[pred]),
    )


# ==========================================================
# EXTRAER TEXTO DEL PDF
# ==========================================================

def extraer_pdf(pdf):

    reader = PdfReader(pdf)

    texto = ""

    for pagina in reader.pages:

        contenido = pagina.extract_text()

        if contenido:
            texto += contenido + "\n"

    return texto


# ==========================================================
# DIVIDIR TEXTO
# ==========================================================

def dividir(texto, tam=180):

    palabras = texto.split()

    bloques = []

    for i in range(0, len(palabras), tam):
        bloques.append(" ".join(palabras[i:i + tam]))

    return bloques


# ==========================================================
# MAIN
# ==========================================================

print("=" * 70)
print("DETECTOR DE IA PARA PDF")
print("=" * 70)

modelo, tokenizer = cargar_modelo(MODEL_DIR)

print("\nLeyendo PDF...")

texto = extraer_pdf(PDF)

if len(texto.strip()) == 0:
    print("No se pudo extraer texto del PDF.")
    print("Si es un PDF escaneado necesitarás OCR.")
    exit()

print(f"Caracteres extraídos : {len(texto):,}")

bloques = dividir(texto, PALABRAS_POR_BLOQUE)

print(f"Bloques generados    : {len(bloques)}")

print()

conteo = Counter()
conf_total = 0

for i, bloque in enumerate(bloques):

    pred, conf = predecir(bloque, modelo, tokenizer)

    conteo[pred] += 1
    conf_total += conf

    print(
        f"Bloque {i+1:03d} | "
        f"{pred:<10} | "
        f"{conf:.2%}"
    )

print("\n" + "=" * 70)

print("RESUMEN")

for clase, cantidad in conteo.items():
    print(f"{clase:<10}: {cantidad} bloques")

resultado = conteo.most_common(1)[0][0]

print("\n" + "=" * 70)
print("RESULTADO FINAL")
print("=" * 70)

print("Documento           :", Path(PDF).name)
print("Clasificación final :", resultado)
print(f"Confianza promedio  : {conf_total/len(bloques):.2%}")

print("=" * 70)