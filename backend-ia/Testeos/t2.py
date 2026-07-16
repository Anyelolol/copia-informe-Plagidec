import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "/var/home/leaf/PycharmProjects/TrainerAI/modelo_detector/final"
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

# Testear los primeros 3 casos (1 IA obvia correcta, 1 IA fallo, 1 humano correcto)
textos = [
    ("IA", "lista estructurada", "There are several key factors to consider when choosing a programming language. First, you should evaluate the language's performance characteristics."),
    ("IA", "definición formal", "Quantum computing is a type of computation that harnesses the collective properties of quantum states, such as superposition, interference, and entanglement."),
    ("humano", "typos slang", "omg i just realized i've been doing this wrong for like 3 years lmaooo no wonder my code kept breaking"),
]

print(f"Labels del modelo: {model.config.id2label}")
print()

for esperado, cat, texto in textos:
    inputs = tokenizer(texto, truncation=True, max_length=256, return_tensors="pt", return_token_type_ids=False)
    with torch.no_grad():
        logits = model(**inputs).logits
    probs = torch.softmax(logits, dim=-1)
    print(f"[{esperado}] {cat}")
    print(f"  logits: {logits[0].tolist()}")
    print(f"  probs:  {probs[0].tolist()}")
    print(f"  id2label: {model.config.id2label}")
    print()