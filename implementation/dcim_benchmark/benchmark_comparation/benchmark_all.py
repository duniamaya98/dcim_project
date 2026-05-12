import requests
import time
import threading
import statistics
import numpy as np

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

N_RUNS = 5
THROUGHPUT_REQUESTS = 10


# =========================
# 🔥 Warm-up
# =========================
def warmup(model):
    print(f"Warming up {model}...")
    requests.post(URL, json={
        "model": model,
        "prompt": "Hello",
        "stream": False
    })


# =========================
# ⏱️ Single Run
# =========================
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

    data = res.json()

    if "response" not in data:
        print("ERROR:", data)
        return 0, 0

    latency = end - start

    tokens = data.get("eval_count", len(data["response"].split()))

    return latency, tokens


# =========================
# 📊 Latency + TPS
# =========================
def benchmark_latency(model):
    latencies = []
    tps_list = []

    for _ in range(N_RUNS):
        latency, tokens = run_once(model)

        if latency == 0:
            continue

        tps = tokens / latency

        latencies.append(latency)
        tps_list.append(tps)

    return {
        "latency_avg": statistics.mean(latencies),
        "latency_p95": float(np.percentile(latencies, 95)),
        "tokens_per_sec_avg": statistics.mean(tps_list)
    }


# =========================
# ⚡ TTFT
# =========================
def benchmark_ttft(model):
    payload = {
        "model": model,
        "prompt": PROMPT,
        "stream": True
    }

    start = time.time()

    with requests.post(URL, json=payload, stream=True) as r:
        for chunk in r.iter_lines():
            if chunk:
                return time.time() - start


# =========================
# 🚀 Throughput
# =========================
def benchmark_throughput(model):
    def hit():
        payload = {
            "model": model,
            "prompt": PROMPT,
            "stream": False,
            "options": OPTIONS
        }
        requests.post(URL, json=payload)

    threads = []
    start = time.time()

    for _ in range(THROUGHPUT_REQUESTS):
        t = threading.Thread(target=hit)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return THROUGHPUT_REQUESTS / (time.time() - start)


# =========================
# 🧠 Quality Test
# =========================
def benchmark_quality(model):
    tests = [
        ("What is CPU spike?", "cpu"),
        ("What is anomaly detection?", "anomaly"),
    ]

    score = 0

    for prompt, keyword in tests:
        res = requests.post(URL, json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": OPTIONS
        }).json()

        text = res.get("response", "").lower()

        if keyword in text:
            score += 1

    return score / len(tests)


# =========================
# 🔥 MAIN
# =========================
def run_all():
    final_results = []

    for model in MODELS:
        print(f"\n===== TESTING {model} =====")

        warmup(model)

        latency_data = benchmark_latency(model)
        ttft = benchmark_ttft(model)
        throughput = benchmark_throughput(model)
        quality = benchmark_quality(model)

        result = {
            "model": model,
            "latency_avg": latency_data["latency_avg"],
            "latency_p95": latency_data["latency_p95"],
            "tokens_per_sec": latency_data["tokens_per_sec_avg"],
            "ttft": ttft,
            "throughput": throughput,
            "quality_score": quality
        }

        final_results.append(result)

        print(result)

    print("\n===== FINAL SUMMARY =====")
    for r in final_results:
        print(r)


if __name__ == "__main__":
    run_all()