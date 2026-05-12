import requests
import threading
import time

URL = "http://localhost:11434/api/generate"

MODELS = ["qwen3.5:4b", "gemma4:latest"]

payload_template = {
    "prompt": "Explain CPU spike briefly",
    "stream": False,
    "options": {"num_predict": 100}
}


def run_model(model):
    def hit():
        payload = payload_template.copy()
        payload["model"] = model
        requests.post(URL, json=payload)

    threads = []
    start = time.time()

    for _ in range(10):
        t = threading.Thread(target=hit)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    throughput = 10 / (time.time() - start)
    print(model, "Throughput:", throughput)


for m in MODELS:
    run_model(m)