import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig

MODEL_DIR = "modelo_detector_es_final"

def cargar_modelo(model_dir: str = MODEL_DIR):
    config = AutoConfig.from_pretrained(model_dir)
    modelo = AutoModelForSequenceClassification.from_config(config)

    # Misma cuantizacion que se aplico al entrenar, para que las keys coincidan
    modelo = torch.quantization.quantize_dynamic(
        modelo, {torch.nn.Linear}, dtype=torch.qint8
    )

    state_dict = torch.load(f"{model_dir}/pytorch_model.bin", map_location="cpu")
    modelo.load_state_dict(state_dict)
    modelo.eval()

    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    return modelo, tokenizer


def predecir(texto: str, modelo, tokenizer):
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, max_length=192)
    with torch.no_grad():
        logits = modelo(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0]
    id2label = modelo.config.id2label
    pred_id = int(probs.argmax())
    return id2label[pred_id], float(probs[pred_id])


if __name__ == "__main__":
    modelo, tokenizer = cargar_modelo()
    ejemplo = "che loco no sabes lo que me paso hoy en el laburo, un caos total"
    label, conf = predecir(ejemplo, modelo, tokenizer)
    print(f"Texto: {ejemplo}")
    print(f"Prediccion: {label} (confianza {conf:.2%})")
