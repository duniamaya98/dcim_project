import requests
import time

payload = {
    "model": "mistral:7b",
    "prompt": "Explain anomaly detection",
    "stream": True
}

start = time.time()

with requests.post("http://localhost:11434/api/generate", json=payload, stream=True) as r:
    for chunk in r.iter_lines():
        if chunk:
            ttft = time.time() - start
            print("TTFT:", ttft)
            break