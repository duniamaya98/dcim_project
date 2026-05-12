import requests
import time

MODELS = ["qwen3.5:4b", "gemma4:latest"]

for model in MODELS:
    payload = {
        "model": model,
        "prompt": "Explain anomaly detection briefly",
        "stream": True
    }

    start = time.time()

    with requests.post("http://localhost:11434/api/generate", json=payload, stream=True) as r:
        for chunk in r.iter_lines():
            if chunk:
                ttft = time.time() - start
                print(model, "TTFT:", ttft)
                break