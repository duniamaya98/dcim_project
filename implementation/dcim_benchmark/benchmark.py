import requests
import time

URL = "http://localhost:11434/api/generate"

payload = {
    "model": "mistral:7b",
    "prompt": "Explain anomaly detection in data center",
    "stream": False
}

start = time.time()
response = requests.post(URL, json=payload)
end = time.time()

latency = end - start
text = response.json()["response"]

tokens = len(text.split())

print("Latency:", latency)
print("Tokens:", tokens)
print("Tokens/sec:", tokens / latency)