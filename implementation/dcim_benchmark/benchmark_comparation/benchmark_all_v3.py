import requests
import time
import threading
import statistics
import numpy as np
import pynvml

# =========================
# CONFIG
# =========================
URL = "http://localhost:11434/api/generate"

MODELS = [
    "qwen3.5:4b",
    "gemma4:latest"
]

PROMPT = "Explain clearly in 2 sentences: What is CPU spike?"

OPTIONS = {
    "num_predict": 100,
    "temperature": 0.7,
    "top_p": 0.9
}

N_RUNS = 5
THROUGHPUT_REQUESTS = 10

# =========================
# GPU INIT
# =========================
pynvml.nvmlInit()


def get_gpu_usage(handle):
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)

    return {
        "gpu_util": util.gpu,
        "vram_used_mb": mem.used / 1024 / 1024
    }


# =========================
# AUTO DETECT ACTIVE GPU
# =========================
def detect_active_gpu():
    device_count = pynvml.nvmlDeviceGetCount()

    best_gpu = 0
    max_mem = 0

    for i in range(device_count):
        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
        mem = pynvml.nvmlDeviceGetMemoryInfo(handle)

        if mem.used > max_mem:
            max_mem = mem.used
            best_gpu = i

    return best_gpu


# =========================
# Warm-up
# =========================
def warmup(model):
    requests.post(URL, json={
        "model": model,
        "prompt": "Hello",
        "stream": False
    })


# =========================
# Single Run
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
        return 0, 0

    latency = end - start
    tokens = data.get("eval_count", len(data["response"].split()))

    return latency, tokens


# =========================
# Latency + TPS
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
        "tokens_per_sec": statistics.mean(tps_list)
    }


# =========================
# TTFT
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
# Throughput
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
# Quality Test (IMPROVED)
# =========================
def extract_text(data):
    if data.get("response"):
        return data["response"]
    if "thinking" in data:
        return data["thinking"]
    if "message" in data:
        return data["message"].get("content", "")
    return ""


def benchmark_quality(model):
    tests = [
        "What is CPU spike?",
        "Explain anomaly detection",
        "What is memory leak?"
    ]

    score = 0

    for prompt in tests:
        payload = {
            "model": model,
            "prompt": f"Answer directly without thinking. {prompt}",
            "stream": False,
            "options": {
                "num_predict": 800,   # 🔥 FIX DI SINI
                "temperature": 0.7
            }
        }

        res = requests.post(URL, json=payload)
        data = res.json()

        text = extract_text(data).lower().strip()

        print("\nOUTPUT:", text[:200])

        if len(text) > 50:
            score += 1

    return score / len(tests)


# =========================
# GPU MONITORING (SAMPLING)
# =========================
def monitor_gpu_during(model, gpu_index):
    handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
    samples = []

    def collect():
        for _ in range(15):
            samples.append(get_gpu_usage(handle))
            time.sleep(0.2)

    t = threading.Thread(target=collect)
    t.start()

    benchmark_latency(model)

    t.join()

    avg_util = sum(s["gpu_util"] for s in samples) / len(samples)
    avg_vram = sum(s["vram_used_mb"] for s in samples) / len(samples)

    return avg_util, avg_vram


# =========================
# MAIN
# =========================
def run_all():
    results = []

    for model in MODELS:
        print(f"\n===== TESTING {model} =====")

        warmup(model)

        gpu_index = detect_active_gpu()
        print(f"Using GPU index: {gpu_index}")

        latency_data = benchmark_latency(model)
        ttft = benchmark_ttft(model)
        throughput = benchmark_throughput(model)
        quality = benchmark_quality(model)

        gpu_util, gpu_vram = monitor_gpu_during(model, gpu_index)

        result = {
            "model": model,
            "latency_avg": latency_data["latency_avg"],
            "latency_p95": latency_data["latency_p95"],
            "tokens_per_sec": latency_data["tokens_per_sec"],
            "ttft": ttft,
            "throughput": throughput,
            "quality_score": quality,
            "gpu_util_avg": gpu_util,
            "gpu_vram_avg_mb": gpu_vram
        }

        print(result)
        results.append(result)

    print("\n===== FINAL SUMMARY =====")
    for r in results:
        print(r)


if __name__ == "__main__":
    run_all()