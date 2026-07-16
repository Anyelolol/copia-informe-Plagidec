import os, torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
from core.config import DETECTOR_MODEL_PATH

_classifier = None

def load_detector():
    global _classifier
    if _classifier is not None:
        return _classifier
    print(f"[detector] Cargando modelo desde: {DETECTOR_MODEL_PATH}")
    tokenizer = AutoTokenizer.from_pretrained(DETECTOR_MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(DETECTOR_MODEL_PATH)
    model.eval()
    _classifier = pipeline(
        "text-classification",
        model=model, tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1,
        tokenize_kwargs={"return_token_type_ids": False},
    )
    print("[detector] Modelo listo.")
    return _classifier

def is_detector_loaded() -> bool:
    return _classifier is not None

def detect_ai(text: str) -> dict:
    if not text.strip():
        return {"label": "humano", "is_ai_generated": False, "confidence": 0.0}
    result = load_detector()(text, truncation=True, max_length=256)[0]
    label = result["label"].lower()
    return {
        "label": label,
        "is_ai_generated": label == "ia",
        "confidence": round(result["score"], 4),
    }