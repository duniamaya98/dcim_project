import requests
import time
import threading
import statistics
import json
import re
import numpy as np
import pynvml

# ==========================================================
# CONFIG (LLAMA.CPP / vLLM OpenAI-Compatible API)
# ==========================================================
URL = "http://localhost:8080/v1/chat/completions"

MODELS = [
    "default-model"
]

PROMPT = "Explain clearly in 2 sentences: What is CPU spike?"

OPTIONS = {
    "max_tokens": 1500, # In llama.cpp / vLLM, use max_tokens instead of num_predict
    "temperature": 0.7,
    "top_p": 0.9
}

N_RUNS = 5
THROUGHPUT_REQUESTS = 10
CONSISTENCY_RUNS = 3

# ==========================================================
# GPU INIT
# ==========================================================
pynvml.nvmlInit()

def get_gpu_usage(handle):
    util = pynvml.nvmlDeviceGetUtilizationRates(handle)
    mem = pynvml.nvmlDeviceGetMemoryInfo(handle)

    return {
        "gpu_util": util.gpu,
        "vram_used_mb": mem.used / 1024 / 1024
    }

def detect_all_gpus():
    device_count = pynvml.nvmlDeviceGetCount()
    return list(range(device_count))

# ==========================================================
# HELPER: Send prompt and extract text
# ==========================================================
def extract_text(data):
    """Extract response text from OpenAI-compatible response format.
    
    Handles Qwen3 / thinking models where:
    - 'content' is the final answer (may be empty/null if max_tokens cut off before thinking finished)
    - 'reasoning_content' contains the chain-of-thought (always populated for thinking models)
    Falls back to reasoning_content when content is empty so benchmarks are not penalized.
    """
    if "error" in data:
        print(f"    [SERVER ERROR] {data['error']}")
        return ""
    if "choices" in data and len(data["choices"]) > 0:
        choice = data["choices"][0]
        if "message" in choice:
            msg = choice["message"]
            text = msg.get("content") or ""
            # --- Qwen3 / thinking-model fallback ---
            # When max_tokens runs out during the <think> phase, content is ""
            # but reasoning_content holds the full internal reasoning which
            # already contains the answer.  Use it as a fallback.
            if not text:
                reasoning = msg.get("reasoning_content") or ""
                if reasoning:
                    text = reasoning
                    print(f"    [THINKING FALLBACK] content empty, using reasoning_content ({len(reasoning)} chars)")
            # --- Native tool-call extraction ---
            if "tool_calls" in msg and msg["tool_calls"]:
                for tc in msg["tool_calls"]:
                    func = tc.get("function", {})
                    text += f" {func.get('name', '')}({func.get('arguments', '')})"
            return text
        if "text" in choice:  # Fallback for /v1/completions endpoint
            return choice["text"]
    return ""

def send_prompt(model, prompt, num_predict=800, temperature=0.7, stream=False):
    """Send a prompt to the model and return the response text."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful IT infrastructure assistant."},
            {"role": "user", "content": prompt}
        ],
        "stream": stream,
        "max_tokens": num_predict,
        "temperature": temperature
    }

    try:
        res = requests.post(URL, json=payload, timeout=600)
        data = res.json()
        return extract_text(data).strip()
    except Exception as e:
        print(f"  [ERROR] send_prompt failed: {e}")
        return ""

# ==========================================================
# Warm-up
# ==========================================================
def warmup(model):
    try:
        requests.post(URL, json={
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful IT infrastructure assistant."},
                {"role": "user", "content": "Hello"}
            ],
            "stream": False,
            "max_tokens": 3000
        }, timeout=600)
    except Exception:
        pass

# ==========================================================
# Single Run (for latency)
# ==========================================================
def run_once(model):
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful IT infrastructure assistant."},
            {"role": "user", "content": PROMPT}
        ],
        "stream": False,
    }
    payload.update(OPTIONS)

    start = time.time()
    try:
        res = requests.post(URL, json=payload, timeout=600)
        end = time.time()
        data = res.json()
    except Exception:
        return 0, 0

    if "choices" not in data or len(data["choices"]) == 0:
        return 0, 0

    latency = end - start
    tokens = data.get("usage", {}).get("completion_tokens", len(extract_text(data).split()))

    return latency, tokens

# ==========================================================
# BENCHMARK 1: Latency + TPS
# ==========================================================
def benchmark_latency(model):
    print("  [1/14] Latency + TPS...")
    latencies = []
    tps_list = []

    for _ in range(N_RUNS):
        latency, tokens = run_once(model)

        if latency == 0:
            continue

        tps = tokens / latency if latency > 0 else 0

        latencies.append(latency)
        tps_list.append(tps)

    if not latencies:
        return {"latency_avg": 0.0, "latency_p95": 0.0, "tokens_per_sec": 0.0}

    return {
        "latency_avg": statistics.mean(latencies),
        "latency_p95": float(np.percentile(latencies, 95)),
        "tokens_per_sec": statistics.mean(tps_list)
    }

# ==========================================================
# BENCHMARK 2: TTFT (Time To First Token)
# ==========================================================
def benchmark_ttft(model):
    print("  [2/14] TTFT...")
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a helpful IT infrastructure assistant."},
            {"role": "user", "content": PROMPT}
        ],
        "stream": True,
        "max_tokens": OPTIONS["max_tokens"],
        "temperature": OPTIONS["temperature"]
    }

    start = time.time()

    try:
        with requests.post(URL, json=payload, stream=True, timeout=600) as r:
            for chunk in r.iter_lines():
                if chunk:
                    decoded = chunk.decode('utf-8')
                    if decoded.startswith('data:') and '[DONE]' not in decoded:
                        return time.time() - start
    except Exception:
        pass
    return 0.0

# ==========================================================
# BENCHMARK 3: Throughput
# ==========================================================
def benchmark_throughput(model):
    print("  [3/14] Throughput...")

    def hit():
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful IT infrastructure assistant."},
                {"role": "user", "content": PROMPT}
            ],
            "stream": False,
        }
        payload.update(OPTIONS)
        try:
            requests.post(URL, json=payload, timeout=600)
        except Exception:
            pass

    threads = []
    start = time.time()

    for _ in range(THROUGHPUT_REQUESTS):
        t = threading.Thread(target=hit)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    return THROUGHPUT_REQUESTS / (time.time() - start)

# ==========================================================
# BENCHMARK 4: Quality
# ==========================================================
def benchmark_quality(model):
    print("  [4/14] Quality...")
    tests = [
        "What is CPU spike?",
        "Explain anomaly detection",
        "What is memory leak?"
    ]

    score = 0

    for prompt in tests:
        # /no_think suppresses Qwen3 thinking chain so tokens go to the answer
        text = send_prompt(model, f"/no_think Answer directly. {prompt}", num_predict=1500)
        text_lower = text.lower()

        print(f"    OUTPUT: {text_lower[:150]}")

        if len(text_lower) > 50:
            score += 1

    return score / len(tests)

# ==========================================================
# BENCHMARK 5: GPU Monitoring
# ==========================================================
def benchmark_latency_silent(model):
    for _ in range(N_RUNS):
        run_once(model)

def monitor_gpu_during(model, gpu_indices):
    print("  [5/14] GPU Monitoring...")
    handles = [pynvml.nvmlDeviceGetHandleByIndex(i) for i in gpu_indices]
    samples = {i: [] for i in gpu_indices}

    def collect():
        for _ in range(15):
            for i, handle in zip(gpu_indices, handles):
                samples[i].append(get_gpu_usage(handle))
            time.sleep(0.2)

    t = threading.Thread(target=collect)
    t.start()

    benchmark_latency_silent(model)

    t.join()

    results = {}
    for i in gpu_indices:
        avg_util = sum(s["gpu_util"] for s in samples[i]) / len(samples[i]) if samples[i] else 0.0
        avg_vram = sum(s["vram_used_mb"] for s in samples[i]) / len(samples[i]) if samples[i] else 0.0
        results[f"gpu{i}_util_avg"] = avg_util
        results[f"gpu{i}_vram_avg_mb"] = avg_vram

    return results

# ==========================================================
# BENCHMARK 6: Reasoning
# ==========================================================
REASONING_TESTS = [
    {
        "prompt": (
            "A server has 3 services: A, B, C. Service A depends on B, and B depends on C. "
            "If C goes down, which services will be affected? List all affected services."
        ),
        "required_keywords": ["a", "b"],
        "description": "Dependency chain"
    },
    {
        "prompt": (
            "Server X has 64GB RAM. Process P1 uses 20GB, P2 uses 15GB, P3 uses 25GB. "
            "A new process P4 needs 10GB. Will P4 fit in memory?"
        ),
        "required_keywords": ["60", "no"],
        "description": "Arithmetic"
    },
    {
        "prompt": (
            "Cooling failed at 2AM. Temp rises 2 degrees Celsius per hour. Normal is 22 degrees. "
            "Critical is 35 degrees. When will critical temperature be reached?"
        ),
        "required_keywords": ["8", "am"],
        "description": "Sequential time"
    },
    {
        "prompt": (
            "Load balancer: Server A 50%, B 30%, C 20%. Server A crashes. "
            "If redistributed proportionally, what percentage does B and C each handle?"
        ),
        "required_keywords": ["60", "40"],
        "description": "Proportional math"
    }
]

def benchmark_reasoning(model):
    print("  [6/14] Reasoning...")
    score = 0
    total = len(REASONING_TESTS)
    for test in REASONING_TESTS:
        # Allow thinking for reasoning — it helps accuracy. Give ample tokens.
        text = send_prompt(model, test["prompt"], num_predict=12000).lower()
        print(f"    [{test['description']}] OUTPUT: {text[:200]}")
        k_found = sum(1 for kw in test["required_keywords"] if kw in text)
        if len(text) > 0 and k_found > 0:
            score += k_found / len(test["required_keywords"])
    return round(score / total, 3)

# ==========================================================
# BENCHMARK 7: RCA
# ==========================================================
RCA_TESTS = [
    {
        "prompt": "CPU spike at 3:02 AM. Cron job started 3:00 AM heavy ETL. Normal at 3:45 AM. What is the root cause?",
        "required_keywords": ["cron", "etl"],
        "description": "CPU spike cron"
    },
    {
        "prompt": "App response time degraded from 50ms to 2000ms. RAM 95%. Swap 0% to 80%. No CPU spike. Frequent GC logs. What is the root cause?",
        "required_keywords": ["memory", "swap"],
        "description": "Memory exhaustion"
    },
    {
        "prompt": "Packet loss 15% on VLAN 100. New switch added yesterday. Spanning tree topology changes detected. What is the root cause?",
        "required_keywords": ["switch", "spanning"],
        "description": "Network loop"
    },
    {
        "prompt": "DB queries 10x slower than baseline. Disk IO wait 40%. RAID array degraded. SMART shows reallocated sectors. What is the root cause?",
        "required_keywords": ["disk", "raid"],
        "description": "Disk failure RAID"
    }
]

def benchmark_rca(model):
    print("  [7/14] RCA...")
    score = 0
    total = len(RCA_TESTS)
    for test in RCA_TESTS:
        # Allow thinking for RCA — reasoning chain improves accuracy
        text = send_prompt(model, test["prompt"], num_predict=12000).lower()
        print(f"    [{test['description']}] OUTPUT: {text[:200]}")
        k_found = sum(1 for kw in test["required_keywords"] if kw in text)
        if len(text) > 0 and k_found > 0:
            score += k_found / len(test["required_keywords"])
    return round(score / total, 3)

# ==========================================================
# BENCHMARK 8: Tool Use
# ==========================================================
TOOL_TESTS = [
    {
        "prompt": (
            "You have these tools available: check_cpu(server_name), send_alert(severity, message).\n"
            "Task: Server 'web-prod-01' is experiencing high CPU usage.\n"
            "Show the exact function calls you would make, step by step."
        ),
        "required_patterns": [r"check_cpu", r"web-prod-01", r"send_alert", r"critical"],
        "description": "Sequential chain"
    },
    {
        "prompt": (
            "You have these tools available: get_metrics(server), scale_replicas(service, count).\n"
            "Task: 'api-gateway' is experiencing 5x normal traffic and needs to be scaled.\n"
            "Show the exact function calls you would make."
        ),
        "required_patterns": [r"get_metrics|scale_replicas", r"api-gateway"],
        "description": "Tool selection"
    },
    {
        "prompt": (
            "You have these tools available: check_network(server, target), run_diagnostic(server).\n"
            "Task: Server 'db-replica-03' is unreachable from the network.\n"
            "Show the exact function calls you would make to diagnose the problem."
        ),
        "required_patterns": [r"check_network|run_diagnostic", r"db-replica-03"],
        "description": "Network diag"
    }
]

def benchmark_tools(model):
    print("  [8/14] Tool Use...")
    score = 0
    total = len(TOOL_TESTS)
    for test in TOOL_TESTS:
        # Give ample tokens: thinking model needs space to reason + write the answer
        text = send_prompt(model, test["prompt"], num_predict=6000).lower()
        print(f"    [{test['description']}] OUTPUT: {text[:200]}")
        p_found = sum(1 for pat in test["required_patterns"] if re.search(pat, text))
        p_score = p_found / len(test["required_patterns"])
        has_syntax = bool(re.search(r"\w+\(", text))
        if has_syntax and p_score > 0:
            score += p_score
        elif p_score > 0:
            score += p_score * 0.5
    return round(score / total, 3)

# ==========================================================
# BENCHMARK 9: Long Context
# ==========================================================
def benchmark_long_context(model):
    print("  [9/14] Long Context...")
    log_text = "[2026-04-20 14:32:05] [srv-analytics-07] ERROR: OutOfMemoryError - Java heap space exhausted\n" * 20
    log_text += "[2026-04-20 14:32:10] [srv-analytics-07] WARN: Service restarted automatically (restart #3)\n" * 20
    tests = [
        {"q": "Which server had ERROR?", "ans": "srv-analytics-07"},
        {"q": "What type of error?", "ans": "outofmemoryerror"},
        {"q": "How many times restarted?", "ans": "3"}
    ]
    score = 0
    total = len(tests)
    for test in tests:
        # /no_think + extra tokens: thinking model must produce content, not just think
        prompt = f"/no_think Answer with only the specific value requested.\nLogs:\n{log_text}\nQuestion: {test['q']}"
        text = send_prompt(model, prompt, num_predict=4000, temperature=0.1).lower()
        print(f"    [long_ctx] Q: {test['q']} | ANS_EXPECTED: {test['ans']} | GOT: {text[:100]}")
        if test["ans"] in text:
            score += 1
    return round(score / total, 3)

# ==========================================================
# BENCHMARK 10: Hallucination
# ==========================================================
HALLUCINATION_TESTS = [
    {
        # Expanded refusal keywords to catch more phrasing variants
        "prompt": "/no_think What is the RFC number for the XYZZY protocol?",
        "should_refuse": True,
        "refusal_keywords": [
            "not exist", "no such", "don't know", "doesn't exist",
            "fictional", "not a real", "no rfc", "unknown", "not aware",
            "does not exist", "no known", "isn't a real", "not standard",
            "xyzzy is not", "there is no", "cannot find"
        ],
    },
    {
        "prompt": "/no_think What does the Linux command 'top' do?",
        "should_refuse": False,
        "valid_keywords": ["process", "cpu", "memory", "monitor", "task", "system"],
    }
]

def benchmark_hallucination(model):
    print("  [10/14] Hallucination...")
    score = 0
    total = len(HALLUCINATION_TESTS)
    for test in HALLUCINATION_TESTS:
        # Give enough tokens for thinking model to finish thinking AND write content
        text = send_prompt(model, test["prompt"], num_predict=5000, temperature=0.1).lower()
        print(f"    [hallucination] should_refuse={test['should_refuse']} | OUTPUT: {text[:200]}")
        if test["should_refuse"]:
            if any(kw in text for kw in test["refusal_keywords"]): score += 1
        else:
            if any(kw in text for kw in test["valid_keywords"]): score += 1
    return round(score / total, 3)

# ==========================================================
# BENCHMARK 11: Consistency
# ==========================================================
def text_to_keywords(text):
    words = re.findall(r'[a-z0-9]+', text.lower())
    return set(w for w in words if len(w) > 2)

def benchmark_consistency(model):
    print(f"  [11/14] Consistency...")
    # /no_think for quick factual answers; enough tokens for thinking model to produce content
    prompts = ["/no_think What are the 3 main types of cloud computing services?", "/no_think What is the default SSH port number?"]
    scores = []
    for prompt in prompts:
        responses = [send_prompt(model, prompt, num_predict=3000, temperature=0.3) for _ in range(3)]
        sims = []
        for i in range(len(responses)):
            for j in range(i+1, len(responses)):
                ka, kb = text_to_keywords(responses[i]), text_to_keywords(responses[j])
                sims.append(len(ka & kb) / len(ka | kb) if (ka | kb) else 0)
        scores.append(statistics.mean(sims) if sims else 0)
    return round(statistics.mean(scores), 3)

# ==========================================================
# BENCHMARK 12: Domain Knowledge
# ==========================================================
DOMAIN_TESTS = [
    {"prompt": "/no_think Explain PUE (Power Usage Effectiveness) in data centers.", "req": ["total", "it"]},
    {"prompt": "/no_think What is UPS (Uninterruptible Power Supply)?", "req": ["ups", "power"]}
]

def benchmark_domain_knowledge(model):
    print("  [12/14] Domain Knowledge...")
    score = 0
    total = len(DOMAIN_TESTS)
    for test in DOMAIN_TESTS:
        text = send_prompt(model, test["prompt"], num_predict=4000).lower()
        if all(kw in text for kw in test["req"]): score += 1
    return round(score / total, 3)

# ==========================================================
# RESULTS FORMATTING
# ==========================================================
def calculate_final_score(r):
    score = 0.0
    score += r.get("hallucination_score", 0.0) * 12
    score += r.get("rca_score", 0.0) * 10
    score += r.get("reasoning_score", 0.0) * 10
    score += r.get("tool_use_score", 0.0) * 10
    score += r.get("quality_score", 0.0) * 8
    score += r.get("domain_knowledge_score", 0.0) * 5
    score += r.get("consistency_score", 0.0) * 5
    score += r.get("long_context_score", 0.0) * 5

    ttft = r.get("ttft", 999.0)
    if ttft < 0.5: score += 8
    elif ttft <= 1.5: score += 5

    tps = r.get("tokens_per_sec", 0.0)
    if tps > 30: score += 8
    elif tps >= 15: score += 5

    lat_avg = r.get("latency_avg", 999.0)
    if lat_avg < 3.0: score += 5

    lat_p95 = r.get("latency_p95", 999.0)
    if lat_p95 < 5.0: score += 5

    tput = r.get("throughput", 0.0)
    if tput > 2.0: score += 5
    elif tput >= 1.0: score += 3

    return round(score, 2)

def print_result_table(results):
    if not results: return
    print("\n" + "=" * 80)
    print("  BENCHMARK COMPARISON TABLE (v5)")
    print("=" * 80)
    metrics = [k for k in results[0].keys() if k != "model"]
    col_width = 18
    header = f"{'Metric':<28}"
    for r in results: header += f"{r['model']:>{col_width}}"
    print(header)
    print("-" * (28 + col_width * len(results)))
    for metric in metrics:
        row = f"{metric:<28}"
        for r in results:
            val = r[metric]
            row += f"{val:>{col_width}.3f}" if isinstance(val, float) else f"{str(val):>{col_width}}"
        print(row)
    print("=" * (28 + col_width * len(results)))

# ==========================================================
# MAIN
# ==========================================================
def run_all():
    results = []
    print("=" * 60)
    print("  BENCHMARK ALL v5 — Llama.cpp / OpenAI Compatible API")
    print(f"  Models: {', '.join(MODELS)}")
    print(f"  Endpoint: {URL}")
    print("=" * 60)

    for model in MODELS:
        print(f"\n{'=' * 60}")
        print(f"  TESTING: {model}")
        print(f"{'=' * 60}")

        print("  [0/14] Warming up model...")
        warmup(model)

        gpu_indices = detect_all_gpus()
        print(f"  Using GPU indices: {gpu_indices}")

        latency_data = benchmark_latency(model)
        ttft = benchmark_ttft(model)
        throughput = benchmark_throughput(model)
        quality = benchmark_quality(model)
        gpu_results = monitor_gpu_during(model, gpu_indices)

        reasoning = benchmark_reasoning(model)
        rca = benchmark_rca(model)
        tool_use = benchmark_tools(model)
        long_ctx = benchmark_long_context(model)
        hallucination = benchmark_hallucination(model)
        consistency = benchmark_consistency(model)
        domain_knowledge = benchmark_domain_knowledge(model)

        result = {
            "model": model,
            "latency_avg": latency_data["latency_avg"],
            "latency_p95": latency_data["latency_p95"],
            "tokens_per_sec": latency_data["tokens_per_sec"],
            "ttft": ttft,
            "throughput": throughput,
            "quality_score": quality,
            **gpu_results,
            "reasoning_score": reasoning,
            "rca_score": rca,
            "tool_use_score": tool_use,
            "long_context_score": long_ctx,
            "hallucination_score": hallucination,
            "consistency_score": consistency,
            "domain_knowledge_score": domain_knowledge,
        }
        result["final_score"] = calculate_final_score(result)

        results.append(result)

    print_result_table(results)

    safe_name = MODELS[0].replace('/', '_').replace(':', '_')
    output_file = f"benchmark_v5_{safe_name}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        MODELS = [sys.argv[1]]
    run_all()
