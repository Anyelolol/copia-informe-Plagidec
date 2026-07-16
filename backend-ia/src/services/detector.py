import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoConfig
from core.config import DETECTOR_MODEL_PATH

MAX_LENGTH = 192

_modelo = None
_tokenizer = None

def load_detector():
    global _modelo, _tokenizer
    if _modelo is not None:
        return _modelo, _tokenizer

    print(f"[detector] Cargando modelo desde: {DETECTOR_MODEL_PATH}")
    config = AutoConfig.from_pretrained(DETECTOR_MODEL_PATH)
    modelo = AutoModelForSequenceClassification.from_config(config)
    modelo = torch.quantization.quantize_dynamic(
        modelo, {torch.nn.Linear}, dtype=torch.qint8
    )
    state_dict = torch.load(f"{DETECTOR_MODEL_PATH}/pytorch_model.bin", map_location="cpu")
    modelo.load_state_dict(state_dict)
    modelo.eval()

    tokenizer = AutoTokenizer.from_pretrained(DETECTOR_MODEL_PATH)

    _modelo, _tokenizer = modelo, tokenizer
    print("[detector] Modelo listo.")
    return _modelo, _tokenizer

def is_detector_loaded() -> bool:
    return _modelo is not None

def detect_ai(text: str) -> dict:
    if not text.strip():
        return {"label": "humano", "is_ai_generated": False, "confidence": 0.0, "prob_ia": 0.0}

    modelo, tokenizer = load_detector()
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=MAX_LENGTH)
    with torch.no_grad():
        logits = modelo(**inputs).logits
    probs = torch.softmax(logits, dim=-1)[0]
    id2label = modelo.config.id2label
    label2id = modelo.config.label2id
    pred_id = int(probs.argmax())
    label = id2label[pred_id].lower()

    ia_id = label2id.get("IA", label2id.get("ia", 1))
    prob_ia = float(probs[ia_id])

    return {
        "label": label,
        "is_ai_generated": label == "ia",
        "confidence": round(float(probs[pred_id]), 4),
        "prob_ia": round(prob_ia, 4),
    }