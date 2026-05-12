import requests
import time
import statistics

URL = "http://localhost:11434/api/generate"

MODELS = [
    "qwen3.5:4b",
    "gemma4:latest"
]

PROMPT = "Explain CPU spike in data center in 2 sentences."

OPTIONS = {
    "num_predict": 100,
    "temperature": 0.7
}

N_RUNS = 5  # biar stabil


def run_once(model):
    payload = {
        "model": model,
        "prompt": PROMPT,
        "stream": False,
        "options": OPTIONS
    }

    start = time.time()
    res = requests.post(URL, json=payload)
    end = time.time()

    latency = end - start
    text = res.json()["response"]

    tokens = len(text.split())

    return latency, tokens


def benchmark(model):
    latencies = []
    tps_list = []

    for _ in range(N_RUNS):
        latency, tokens = run_once(model)
        tps = tokens / latency

        latencies.append(latency)
        tps_list.append(tps)

    return {
        "model": model,
        "latency_avg": statistics.mean(latencies),
        "latency_p95": sorted(latencies)[int(0.95 * len(latencies)) - 1],
        "tokens_per_sec_avg": statistics.mean(tps_list)
    }


results = []

for model in MODELS:
    print(f"Testing {model}...")
    result = benchmark(model)
    results.append(result)

print("\n=== FINAL RESULT ===")
for r in results:
    print(r)