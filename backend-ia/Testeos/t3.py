import requests

url = "http://localhost:8000/analyze"

data = {
    "text": "Python es un lenguaje de programación.",
    "reference": "Python es un lenguaje muy utilizado."
}

r = requests.post(url, json=data)

print(r.json())