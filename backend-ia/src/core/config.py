import os
from pathlib import Path
from dotenv import load_dotenv

_BASE = Path(__file__).resolve().parent.parent.parent
load_dotenv(_BASE / ".env")


def _resolve_path(env_value: str) -> str:
    """Convierte rutas relativas (./models/...) en absolutas basadas en _BASE."""
    p = Path(env_value)
    if not p.is_absolute():
        p = (_BASE / p).resolve()
    return str(p)


MODEL_PATH = _resolve_path(os.getenv("MODEL_PATH", "models"))
MODEL_NAME = os.getenv("MODEL_NAME", "paraphrase-multilingual-mpnet-base-v2")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.80"))
DETECTOR_MODEL_PATH = _resolve_path(
    os.getenv("DETECTOR_MODEL_PATH", "models/modelo_detector_es_final")
)
