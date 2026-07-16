import os
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent.parent

MODEL_PATH = os.getenv("MODEL_PATH", str(_BASE / "models"))
MODEL_NAME = os.getenv("MODEL_NAME", "paraphrase-multilingual-mpnet-base-v2")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.80"))
DETECTOR_MODEL_PATH = os.getenv(
    "DETECTOR_MODEL_PATH",
    "/var/home/leaf/PycharmProjects/TrainerAI/modelo_detector/final"
)
