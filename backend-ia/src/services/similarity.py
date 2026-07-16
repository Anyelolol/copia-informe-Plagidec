import os
from sentence_transformers import SentenceTransformer, util
from core.config import MODEL_PATH, MODEL_NAME, SIMILARITY_THRESHOLD

_model: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    global _model
    if _model is not None:
        return _model

    if os.path.isdir(MODEL_PATH):
        print(f"[b-ia] Cargando modelo local desde: {MODEL_PATH}")
        _model = SentenceTransformer(MODEL_PATH)
    else:
        print(f"[b-ia] Descargando modelo: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)

    print("[b-ia] Modelo listo.")
    return _model


def is_model_loaded() -> bool:
    return _model is not None


def get_model_name() -> str:
    return MODEL_PATH if os.path.isdir(MODEL_PATH) else MODEL_NAME


def compute_similarity(text1: str, text2: str) -> float:
    if not text1.strip() or not text2.strip():
        return 0.0
    model = load_model()
    emb1, emb2 = model.encode([text1, text2], convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2)[0][0])


def compute_segments(text: str, reference: str, window: int = 200, step: int = 100) -> list[dict]:
    if not text.strip() or not reference.strip():
        return []

    model  = load_model()
    words  = text.split()
    result = []

    for i in range(0, max(1, len(words) - window + 1), step):
        chunk     = " ".join(words[i : i + window])
        inicio    = len(" ".join(words[:i]))
        fin       = inicio + len(chunk)
        similitud = float(util.cos_sim(
            model.encode(chunk, convert_to_tensor=True),
            model.encode(reference, convert_to_tensor=True),
        )[0][0])

        if similitud >= SIMILARITY_THRESHOLD:
            result.append({
                "inicio_documento":     inicio,
                "fin_documento":        fin,
                "texto_documento":      chunk,
                "texto_coincidente":    reference[:300],
                "porcentaje_similitud": round(similitud, 4),
            })

    return result
