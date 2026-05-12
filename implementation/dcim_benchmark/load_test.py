import requests
import threading
import time

URL = "http://localhost:11434/api/generate"

payload = {
    "model": "mistral:7b",
    "prompt": "Explain CPU spike",
    "stream": False
}

def hit():
    requests.post(URL, json=payload)

threads = []
start = time.time()

for _ in range(20):  # jumlah request
    t = threading.Thread(target=hit)
    t.start()
    threads.append(t)

for t in threads:
    t.join()

end = time.time()

print("Throughput:", 20 / (end - start), "req/sec")