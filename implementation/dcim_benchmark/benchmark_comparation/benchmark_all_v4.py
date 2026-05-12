import requests
import time
import threading
import statistics
import json
import re
import hashlib
import numpy as np
import pynvml

# ==========================================================
# CONFIG
# ==========================================================
URL = "http://localhost:11434/api/generate"

MODELS = [
    "deepseek-r1:1.5b",
    "qwen3.5:9b-q8_0"
]

PROMPT = "Explain clearly in 2 sentences: What is CPU spike?"

OPTIONS = {
    "num_predict": 100,
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


# ==========================================================
# DETECT ALL GPUS
# ==========================================================
def detect_all_gpus():
    device_count = pynvml.nvmlDeviceGetCount()
    return list(range(device_count))


# ==========================================================
# HELPER: Send prompt and extract text
# ==========================================================
def extract_text(data):
    """Extract response text from various Ollama response formats."""
    if data.get("response"):
        return data["response"]
    if "thinking" in data:
        return data["thinking"]
    if "message" in data:
        return data["message"].get("content", "")
    return ""


def send_prompt(model, prompt, num_predict=800, temperature=0.7, stream=False):
    """Send a prompt to the model and return the response text."""
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "num_predict": num_predict,
            "temperature": temperature
        }
    }

    try:
        res = requests.post(URL, json=payload, timeout=120)
        data = res.json()
        return extract_text(data).strip()
    except Exception as e:
        print(f"  [ERROR] send_prompt failed: {e}")
        return ""


# ==========================================================
# Warm-up
# ==========================================================
def warmup(model):
    requests.post(URL, json={
        "model": model,
        "prompt": "Hello",
        "stream": False
    })


# ==========================================================
# Single Run (for latency)
# ==========================================================
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

        tps = tokens / latency

        latencies.append(latency)
        tps_list.append(tps)

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
        "prompt": PROMPT,
        "stream": True
    }

    start = time.time()

    with requests.post(URL, json=payload, stream=True) as r:
        for chunk in r.iter_lines():
            if chunk:
                return time.time() - start


# ==========================================================
# BENCHMARK 3: Throughput
# ==========================================================
def benchmark_throughput(model):
    print("  [3/14] Throughput...")

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


# ==========================================================
# BENCHMARK 4: Quality (from v3)
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
        text = send_prompt(model, f"Answer directly without thinking. {prompt}")
        text_lower = text.lower()

        print(f"    OUTPUT: {text_lower[:150]}")

        if len(text_lower) > 50:
            score += 1

    return score / len(tests)


# ==========================================================
# BENCHMARK 5: GPU Monitoring (Sampling)
# ==========================================================
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


def benchmark_latency_silent(model):
    """Same as benchmark_latency but without printing."""
    for _ in range(N_RUNS):
        run_once(model)


# ==========================================================
# BENCHMARK 6: Reasoning
# Evaluates multi-step logical/analytical reasoning
# ==========================================================
REASONING_TESTS = [
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "A server has 3 services: A, B, C. "
            "Service A depends on B, and B depends on C. "
            "If C goes down, which services will be affected? "
            "List all affected services and explain the chain."
        ),
        "required_keywords": ["a", "b"],
        "description": "Dependency chain reasoning"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "Server X has 64GB RAM. Process P1 uses 20GB, P2 uses 15GB, P3 uses 25GB. "
            "A new process P4 needs 10GB. Will P4 fit in memory? Show your calculation."
        ),
        "required_keywords": ["60", "no"],
        "description": "Arithmetic reasoning"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "In a data center, cooling failed at 2AM. Temperature rises 2°C per hour. "
            "Normal temperature is 22°C. Critical threshold is 35°C. "
            "At what time will the critical threshold be reached?"
        ),
        "required_keywords": ["8", "am"],
        "description": "Sequential time-based reasoning"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "A load balancer distributes traffic: Server A gets 50%, Server B gets 30%, Server C gets 20%. "
            "Server A crashes. If traffic is redistributed proportionally among B and C, "
            "what percentage does each server now handle?"
        ),
        "required_keywords": ["60", "40"],
        "description": "Proportional redistribution reasoning"
    }
]


def benchmark_reasoning(model):
    print("  [6/14] Reasoning...")
    score = 0
    total = len(REASONING_TESTS)

    for test in REASONING_TESTS:
        text = send_prompt(model, test["prompt"], num_predict=500)
        text_lower = text.lower()

        print(f"    [{test['description']}]")
        print(f"    OUTPUT: {text_lower[:200]}")

        # Check if ALL required keywords are present
        keywords_found = sum(1 for kw in test["required_keywords"] if kw in text_lower)
        keyword_score = keywords_found / len(test["required_keywords"])

        # Also require minimum length for a substantive answer
        if len(text_lower) > 30 and keyword_score > 0:
            score += keyword_score

        print(f"    KEYWORD MATCH: {keywords_found}/{len(test['required_keywords'])}")

    return round(score / total, 3)


# ==========================================================
# BENCHMARK 7: RCA (Root Cause Analysis)
# Evaluates ability to diagnose infrastructure problems
# ==========================================================
RCA_TESTS = [
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "You are an infrastructure engineer. Analyze this scenario:\n"
            "- CPU usage spiked to 98% at 3:02 AM\n"
            "- A cron job started at 3:00 AM that runs a heavy ETL process\n"
            "- No other significant activity in logs\n"
            "- CPU returned to normal at 3:45 AM when the cron job finished\n\n"
            "What is the most likely root cause of the CPU spike? Explain."
        ),
        "required_keywords": ["cron", "etl"],
        "description": "CPU spike from cron job"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "Analyze this data center incident:\n"
            "- Application response time increased from 50ms to 2000ms\n"
            "- Memory usage is at 95%\n"
            "- Swap usage jumped from 0% to 80%\n"
            "- No CPU spike observed\n"
            "- Application logs show frequent garbage collection events\n\n"
            "Identify the root cause and explain the cascade."
        ),
        "required_keywords": ["memory", "swap"],
        "description": "Memory exhaustion cascade"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "Investigate this network issue:\n"
            "- Multiple servers report intermittent connectivity\n"
            "- Packet loss is 15% on VLAN 100\n"
            "- Other VLANs are unaffected\n"
            "- A new switch was added to VLAN 100 yesterday\n"
            "- Spanning tree topology changes detected\n\n"
            "What is the root cause? What should be checked first?"
        ),
        "required_keywords": ["switch", "spanning"],
        "description": "Network loop from switch misconfiguration"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "Diagnose this storage issue:\n"
            "- Database queries suddenly became 10x slower\n"
            "- Disk I/O wait increased to 40%\n"
            "- RAID controller shows one disk in degraded state\n"
            "- No recent configuration changes\n"
            "- SMART data shows reallocated sectors on /dev/sdd\n\n"
            "What is the root cause and what action should be taken?"
        ),
        "required_keywords": ["disk", "raid"],
        "description": "Disk failure in RAID array"
    }
]


def benchmark_rca(model):
    print("  [7/14] RCA (Root Cause Analysis)...")
    score = 0
    total = len(RCA_TESTS)

    for test in RCA_TESTS:
        text = send_prompt(model, test["prompt"], num_predict=800)
        text_lower = text.lower()

        print(f"    [{test['description']}]")
        print(f"    OUTPUT: {text_lower[:200]}")

        keywords_found = sum(1 for kw in test["required_keywords"] if kw in text_lower)
        keyword_score = keywords_found / len(test["required_keywords"])

        # RCA needs substantive explanation
        length_ok = len(text_lower) > 80

        if length_ok and keyword_score > 0:
            score += keyword_score

        print(f"    KEYWORD MATCH: {keywords_found}/{len(test['required_keywords'])}")

    return round(score / total, 3)


# ==========================================================
# BENCHMARK 8: Tool Use / Function Calling
# Evaluates ability to output structured tool calls
# ==========================================================
TOOL_TESTS = [
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "You have access to these tools:\n"
            "1. check_cpu(server_name: str) - Returns CPU usage of a server\n"
            "2. check_memory(server_name: str) - Returns memory usage of a server\n"
            "3. restart_service(server_name: str, service_name: str) - Restarts a service\n"
            "4. send_alert(severity: str, message: str) - Sends an alert\n\n"
            "Task: Server 'web-prod-01' has high CPU. Check its CPU, then if needed send a critical alert.\n\n"
            "Respond with the exact function calls you would make, in order. "
            "Use the format: function_name(param1=\"value1\", param2=\"value2\")"
        ),
        "required_patterns": [r"check_cpu", r"web-prod-01", r"send_alert", r"critical"],
        "description": "Sequential tool chain"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "You have access to these tools:\n"
            "1. get_metrics(server: str, metric: str, period: str) - Gets server metrics\n"
            "2. create_ticket(title: str, priority: str, description: str) - Creates a support ticket\n"
            "3. scale_replicas(service: str, count: int) - Scales service replicas\n\n"
            "Situation: The 'api-gateway' service is receiving 5x normal traffic and response times are degrading.\n\n"
            "Which tools would you call and in what order? "
            "Show the exact function calls with parameters."
        ),
        "required_patterns": [r"get_metrics|scale_replicas", r"api-gateway"],
        "description": "Tool selection under pressure"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "You have access to these tools:\n"
            "1. query_logs(server: str, time_range: str, filter: str) - Search server logs\n"
            "2. check_disk(server: str) - Returns disk usage\n"
            "3. check_network(server: str, target: str) - Tests network connectivity\n"
            "4. run_diagnostic(server: str, test_type: str) - Runs diagnostic tests\n\n"
            "Task: Server 'db-replica-03' is not reachable from 'app-server-01'. "
            "Write the diagnostic steps using the available tools.\n\n"
            "Output exact function calls in order."
        ),
        "required_patterns": [r"check_network|run_diagnostic", r"db-replica-03"],
        "description": "Network diagnostic tool sequence"
    }
]


def benchmark_tools(model):
    print("  [8/14] Tool Use / Function Calling...")
    score = 0
    total = len(TOOL_TESTS)

    for test in TOOL_TESTS:
        text = send_prompt(model, test["prompt"], num_predict=800)
        text_lower = text.lower()

        print(f"    [{test['description']}]")
        print(f"    OUTPUT: {text_lower[:250]}")

        patterns_found = sum(
            1 for pat in test["required_patterns"]
            if re.search(pat, text_lower)
        )
        pattern_score = patterns_found / len(test["required_patterns"])

        # Must have function-call-like syntax
        has_function_syntax = bool(re.search(r"\w+\(", text))

        if has_function_syntax and pattern_score > 0:
            score += pattern_score
        elif pattern_score > 0:
            score += pattern_score * 0.5  # Partial credit without syntax

        print(f"    PATTERN MATCH: {patterns_found}/{len(test['required_patterns'])}, SYNTAX: {has_function_syntax}")

    return round(score / total, 3)


# ==========================================================
# BENCHMARK 9: Long Context
# Tests comprehension and retrieval from large context windows
# ==========================================================
def generate_long_context():
    """Generate a realistic long log context with embedded facts."""
    # Build a long server log with hidden facts the model must find
    lines = []
    hidden_facts = {
        "error_server": "srv-analytics-07",
        "error_time": "14:32:05",
        "error_type": "OutOfMemoryError",
        "restart_count": "3",
    }

    # Generate ~200 lines of normal logs
    normal_servers = ["srv-web-01", "srv-web-02", "srv-api-01", "srv-api-02",
                      "srv-db-01", "srv-cache-01", "srv-queue-01"]
    normal_messages = [
        "Health check passed",
        "Request processed successfully",
        "Connection pool refreshed",
        "Cache hit ratio: 94%",
        "Scheduled backup completed",
        "SSL certificate valid for 89 days",
        "Load balancer check: OK",
        "Disk usage: 45%",
        "Memory usage: 62%",
        "Network latency: 2ms",
    ]

    import random
    random.seed(42)  # Deterministic for reproducibility

    for i in range(200):
        hour = random.randint(10, 16)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        server = random.choice(normal_servers)
        msg = random.choice(normal_messages)
        lines.append(f"[2026-04-20 {hour:02d}:{minute:02d}:{second:02d}] [{server}] INFO: {msg}")

        # Inject hidden facts at specific positions
        if i == 67:
            lines.append(f"[2026-04-20 {hidden_facts['error_time']}] [{hidden_facts['error_server']}] "
                          f"ERROR: {hidden_facts['error_type']} - Java heap space exhausted")
        if i == 68:
            lines.append(f"[2026-04-20 14:32:10] [{hidden_facts['error_server']}] "
                          f"WARN: Service restarted automatically (restart #{hidden_facts['restart_count']})")
        if i == 130:
            lines.append(f"[2026-04-20 15:01:22] [{hidden_facts['error_server']}] "
                          f"ERROR: {hidden_facts['error_type']} - recurring after restart #{hidden_facts['restart_count']}")

    log_text = "\n".join(lines)
    return log_text, hidden_facts


LONG_CONTEXT_QUESTIONS = [
    {
        "question": "Which server experienced an ERROR? Give the exact server name.",
        "answer_key": "error_server",
        "description": "Find error server in logs"
    },
    {
        "question": "What type of error occurred? Give the exact error type.",
        "answer_key": "error_type",
        "description": "Identify error type"
    },
    {
        "question": "How many times was the service restarted according to the logs?",
        "answer_key": "restart_count",
        "description": "Count restarts from logs"
    },
    {
        "question": "At what time did the first error occur? Give the exact timestamp.",
        "answer_key": "error_time",
        "description": "Find error timestamp"
    }
]


def benchmark_long_context(model):
    print("  [9/14] Long Context...")
    log_text, hidden_facts = generate_long_context()
    score = 0
    total = len(LONG_CONTEXT_QUESTIONS)

    for test in LONG_CONTEXT_QUESTIONS:
        prompt = (
            f"Answer directly without thinking.\n"
            f"Below are server logs. Read them carefully and answer the question.\n\n"
            f"=== LOGS START ===\n{log_text}\n=== LOGS END ===\n\n"
            f"Question: {test['question']}\n"
            f"Answer concisely."
        )

        text = send_prompt(model, prompt, num_predict=200, temperature=0.3)
        text_lower = text.lower()

        expected = hidden_facts[test["answer_key"]].lower()

        print(f"    [{test['description']}]")
        print(f"    EXPECTED: {expected}")
        print(f"    OUTPUT: {text_lower[:150]}")

        if expected in text_lower:
            score += 1
            print(f"    ✅ MATCH")
        else:
            print(f"    ❌ MISS")

    return round(score / total, 3)


# ==========================================================
# BENCHMARK 10: Hallucination Detection
# Tests resistance to fabrication / making things up
# ==========================================================
HALLUCINATION_TESTS = [
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "What is the official RFC number for the 'XYZZY' protocol used in data center networking? "
            "If this protocol doesn't exist, say 'This protocol does not exist.'"
        ),
        "should_refuse": True,
        "refusal_keywords": ["not exist", "no such", "don't know", "doesn't exist",
                             "not a real", "not aware", "fictional", "no rfc",
                             "not familiar", "i cannot", "there is no"],
        "description": "Fictitious protocol RFC"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "Explain the 'Quantum Memory Defragmentation' feature in Linux kernel 6.x. "
            "If this feature doesn't exist, say 'This feature does not exist.'"
        ),
        "should_refuse": True,
        "refusal_keywords": ["not exist", "no such", "doesn't exist", "not a real",
                             "not aware", "fictional", "not familiar", "i cannot",
                             "there is no", "don't know"],
        "description": "Fictitious kernel feature"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "What does the Linux command 'top' do?"
        ),
        "should_refuse": False,
        "valid_keywords": ["process", "cpu", "memory", "monitor", "task", "resource"],
        "description": "Real command (should answer)"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "Describe the 'NeuroAdaptive Cooling Algorithm' invented by Dr. Heinrich Müller "
            "at MIT in 2019 for data center thermal management. "
            "If you cannot verify this, say 'I cannot verify this information.'"
        ),
        "should_refuse": True,
        "refusal_keywords": ["cannot verify", "not aware", "no evidence", "doesn't exist",
                             "not exist", "don't know", "unable to verify", "not familiar",
                             "fictional", "no information", "i cannot"],
        "description": "Fictitious research / person"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "What is the maximum number of CPU cores supported by the 'Intel Xeon Platinum 8490H' processor?"
        ),
        "should_refuse": False,
        "valid_keywords": ["core", "60", "thread", "processor", "xeon"],
        "description": "Real hardware spec (should answer)"
    }
]


def benchmark_hallucination(model):
    print("  [10/14] Hallucination Detection...")
    score = 0
    total = len(HALLUCINATION_TESTS)

    for test in HALLUCINATION_TESTS:
        text = send_prompt(model, test["prompt"], num_predict=400, temperature=0.3)
        text_lower = text.lower()

        print(f"    [{test['description']}]")
        print(f"    OUTPUT: {text_lower[:200]}")

        if test["should_refuse"]:
            # Model SHOULD refuse / indicate it doesn't know
            refused = any(kw in text_lower for kw in test["refusal_keywords"])
            if refused:
                score += 1
                print(f"    ✅ Correctly refused/acknowledged uncertainty")
            else:
                print(f"    ❌ May have hallucinated")
        else:
            # Model SHOULD provide a real answer with valid keywords
            valid = any(kw in text_lower for kw in test["valid_keywords"])
            has_content = len(text_lower) > 30
            if valid and has_content:
                score += 1
                print(f"    ✅ Correctly answered real question")
            else:
                print(f"    ❌ Failed to answer real question")

    return round(score / total, 3)


# ==========================================================
# BENCHMARK 11: Consistency
# Tests if model gives consistent answers across multiple runs
# ==========================================================
CONSISTENCY_PROMPTS = [
    "Answer directly without thinking. What are the 3 main types of cloud computing services? List them briefly.",
    "Answer directly without thinking. Name the default SSH port number.",
    "Answer directly without thinking. What does RAID 5 provide? Answer in one sentence.",
]


def text_to_keywords(text):
    """Extract significant keywords from text for comparison."""
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "and", "or", "but",
                  "in", "on", "at", "to", "for", "of", "with", "by", "from", "it",
                  "this", "that", "as", "be", "has", "have", "had", "not", "no",
                  "do", "does", "did", "will", "would", "can", "could", "may", "should"}

    words = re.findall(r'[a-z0-9]+', text.lower())
    return set(w for w in words if w not in stop_words and len(w) > 2)


def keyword_similarity(text_a, text_b):
    """Compute Jaccard similarity on keyword sets."""
    kw_a = text_to_keywords(text_a)
    kw_b = text_to_keywords(text_b)

    if not kw_a or not kw_b:
        return 0.0

    intersection = kw_a & kw_b
    union = kw_a | kw_b

    return len(intersection) / len(union) if union else 0.0


def benchmark_consistency(model):
    print(f"  [11/14] Consistency ({CONSISTENCY_RUNS} runs per prompt)...")
    scores = []

    for prompt in CONSISTENCY_PROMPTS:
        responses = []

        for run in range(CONSISTENCY_RUNS):
            text = send_prompt(model, prompt, num_predict=200, temperature=0.3)
            responses.append(text)

        # Compare all pairs of responses
        pair_scores = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                sim = keyword_similarity(responses[i], responses[j])
                pair_scores.append(sim)

        avg_sim = statistics.mean(pair_scores) if pair_scores else 0.0
        scores.append(avg_sim)

        print(f"    PROMPT: {prompt[:60]}...")
        print(f"    SIMILARITY: {avg_sim:.3f} (across {len(pair_scores)} pairs)")

    return round(statistics.mean(scores), 3)


# ==========================================================
# BENCHMARK 12: Domain Knowledge (Infrastructure / DCIM)
# Tests specific technical knowledge in the target domain
# ==========================================================
DOMAIN_TESTS = [
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "Explain PUE (Power Usage Effectiveness) in data center management. "
            "What is considered a good PUE value?"
        ),
        "required_keywords": ["total", "it", "1."],
        "any_keywords": ["energy", "power", "efficiency", "cooling", "1.2", "1.4", "1.5", "1.6"],
        "description": "PUE knowledge"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "What is the difference between hot aisle and cold aisle containment "
            "in data center cooling? Which is more common?"
        ),
        "required_keywords": ["hot", "cold"],
        "any_keywords": ["aisle", "containment", "cooling", "air", "temperature", "exhaust", "intake"],
        "description": "Cooling architecture"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "Explain SNMP (Simple Network Management Protocol) and its role in "
            "infrastructure monitoring. What are OIDs?"
        ),
        "required_keywords": ["snmp"],
        "any_keywords": ["oid", "monitor", "agent", "trap", "mib", "network", "management", "object identifier"],
        "description": "SNMP / Monitoring protocol"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "What is an UPS (Uninterruptible Power Supply) in a data center context? "
            "What are the common UPS topologies?"
        ),
        "required_keywords": ["ups", "power"],
        "any_keywords": ["battery", "online", "offline", "line-interactive", "double",
                         "backup", "outage", "uninterruptible"],
        "description": "UPS / Power infrastructure"
    },
    {
        "prompt": (
            "Answer directly without thinking.\n"
            "What is IPMI (Intelligent Platform Management Interface)? "
            "How is it used for remote server management?"
        ),
        "required_keywords": ["ipmi"],
        "any_keywords": ["bmc", "remote", "management", "hardware", "out-of-band",
                         "baseboard", "sensor", "console", "kvm"],
        "description": "IPMI / BMC knowledge"
    }
]


def benchmark_domain_knowledge(model):
    print("  [12/14] Domain Knowledge (Infra/DCIM)...")
    score = 0
    total = len(DOMAIN_TESTS)

    for test in DOMAIN_TESTS:
        text = send_prompt(model, test["prompt"], num_predict=600)
        text_lower = text.lower()

        print(f"    [{test['description']}]")
        print(f"    OUTPUT: {text_lower[:200]}")

        # Check required keywords (all must be present)
        required_found = all(kw in text_lower for kw in test["required_keywords"])

        # Check any-of keywords (at least 2 must be present)
        any_found = sum(1 for kw in test["any_keywords"] if kw in text_lower)

        # Minimum length for substantive answer
        length_ok = len(text_lower) > 50

        if required_found and any_found >= 2 and length_ok:
            score += 1
            print(f"    ✅ PASS (required: all, any: {any_found}/{len(test['any_keywords'])})")
        elif required_found and any_found >= 1 and length_ok:
            score += 0.5
            print(f"    ⚠️  PARTIAL (required: all, any: {any_found}/{len(test['any_keywords'])})")
        else:
            print(f"    ❌ FAIL (required: {required_found}, any: {any_found}/{len(test['any_keywords'])})")

    return round(score / total, 3)


# ==========================================================
# RESULTS FORMATTING
# ==========================================================
def calculate_final_score(r):
    score = 0.0

    # CAPABILITY (Max 65)
    score += r.get("hallucination_score", 0.0) * 12
    score += r.get("rca_score", 0.0) * 10
    score += r.get("reasoning_score", 0.0) * 10
    score += r.get("tool_use_score", 0.0) * 10
    score += r.get("quality_score", 0.0) * 8
    score += r.get("domain_knowledge_score", 0.0) * 5
    score += r.get("consistency_score", 0.0) * 5
    score += r.get("long_context_score", 0.0) * 5

    # PERFORMANCE (Max 35)
    ttft = r.get("ttft", 999.0)
    if ttft is None: ttft = 999.0
    if ttft < 0.5: score += 8
    elif ttft <= 1.5: score += 5
    elif ttft <= 3.0: score += 2

    tps = r.get("tokens_per_sec", 0.0)
    if tps > 30: score += 8
    elif tps >= 15: score += 5
    elif tps >= 5: score += 2

    lat_avg = r.get("latency_avg", 999.0)
    if lat_avg < 3.0: score += 5
    elif lat_avg <= 5.0: score += 3

    lat_p95 = r.get("latency_p95", 999.0)
    if lat_p95 < 5.0: score += 5
    elif lat_p95 <= 10.0: score += 2

    tput = r.get("throughput", 0.0)
    if tput > 2.0: score += 5
    elif tput >= 1.0: score += 3
    elif tput > 0.0: score += 1

    vram_keys = [k for k in r.keys() if k.endswith("_vram_avg_mb")]
    if vram_keys:
        avg_vram = sum(r[k] for k in vram_keys) / len(vram_keys)
        if avg_vram < 5734.0: score += 4
        elif avg_vram <= 7372.0: score += 2

    return round(score, 2)


def print_result_table(results):
    """Pretty-print a comparison table of all results."""
    if not results:
        return

    print("\n" + "=" * 80)
    print("  BENCHMARK COMPARISON TABLE")
    print("=" * 80)

    # Header
    metrics = [k for k in results[0].keys() if k != "model"]
    col_width = 18

    header = f"{'Metric':<28}"
    for r in results:
        header += f"{r['model']:>{col_width}}"
    print(header)
    print("-" * (28 + col_width * len(results)))

    # Rows
    metric_labels = {
        "latency_avg": "Latency Avg (s)",
        "latency_p95": "Latency P95 (s)",
        "tokens_per_sec": "Tokens/sec",
        "ttft": "TTFT (s)",
        "throughput": "Throughput (req/s)",
        "quality_score": "Quality",
        "reasoning_score": "Reasoning",
        "rca_score": "RCA",
        "tool_use_score": "Tool Use",
        "long_context_score": "Long Context",
        "hallucination_score": "Hallucination Resist.",
        "consistency_score": "Consistency",
        "domain_knowledge_score": "Domain Knowledge",
        "final_score": "✨ Total Score (100)",
    }

    for metric in metrics:
        if metric not in metric_labels:
            if metric.startswith("gpu") and metric.endswith("_util_avg"):
                gpu_id = metric.replace("gpu", "").replace("_util_avg", "")
                label = f"GPU {gpu_id} Util Avg (%)"
            elif metric.startswith("gpu") and metric.endswith("_vram_avg_mb"):
                gpu_id = metric.replace("gpu", "").replace("_vram_avg_mb", "")
                label = f"GPU {gpu_id} VRAM Avg (MB)"
            else:
                label = metric
        else:
            label = metric_labels[metric]

        row = f"{label:<28}"

        for r in results:
            val = r[metric]
            if isinstance(val, float):
                row += f"{val:>{col_width}.3f}"
            else:
                row += f"{str(val):>{col_width}}"

        print(row)

    print("=" * (28 + col_width * len(results)))


# ==========================================================
# MAIN
# ==========================================================
def run_all():
    results = []

    print("=" * 60)
    print("  BENCHMARK ALL v4 — Full LLM Evaluation Suite")
    print(f"  Models: {', '.join(MODELS)}")
    print(f"  Endpoint: {URL}")
    print(f"  Benchmarks: 14 (7 performance + 7 capability)")
    print("=" * 60)

    for model in MODELS:
        print(f"\n{'=' * 60}")
        print(f"  TESTING: {model}")
        print(f"{'=' * 60}")

        # --- Warm-up ---
        print("  [0/14] Warming up model...")
        warmup(model)

        # --- GPU Detection ---
        gpu_indices = detect_all_gpus()
        print(f"  Using GPU indices: {gpu_indices}")

        # ===== PERFORMANCE BENCHMARKS (from v3) =====
        latency_data = benchmark_latency(model)
        ttft = benchmark_ttft(model)
        throughput = benchmark_throughput(model)
        quality = benchmark_quality(model)
        gpu_results = monitor_gpu_during(model, gpu_indices)

        # ===== CAPABILITY BENCHMARKS (new in v4) =====
        reasoning = benchmark_reasoning(model)
        rca = benchmark_rca(model)
        tool_use = benchmark_tools(model)
        long_ctx = benchmark_long_context(model)
        hallucination = benchmark_hallucination(model)
        consistency = benchmark_consistency(model)
        domain_knowledge = benchmark_domain_knowledge(model)

        result = {
            "model": model,
            # Performance metrics
            "latency_avg": latency_data["latency_avg"],
            "latency_p95": latency_data["latency_p95"],
            "tokens_per_sec": latency_data["tokens_per_sec"],
            "ttft": ttft,
            "throughput": throughput,
            "quality_score": quality,
            **gpu_results,
            # Capability metrics (new in v4)
            "reasoning_score": reasoning,
            "rca_score": rca,
            "tool_use_score": tool_use,
            "long_context_score": long_ctx,
            "hallucination_score": hallucination,
            "consistency_score": consistency,
            "domain_knowledge_score": domain_knowledge,
        }

        result["final_score"] = calculate_final_score(result)

        print(f"\n  --- {model} RESULTS ---")
        for k, v in result.items():
            if k == "model":
                continue
            if isinstance(v, float):
                print(f"    {k}: {v:.3f}")
            else:
                print(f"    {k}: {v}")

        results.append(result)

    # ===== FINAL SUMMARY =====
    print_result_table(results)

    # ===== EXPORT TO JSON =====
    output_file = "benchmark_v4_results.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {output_file}")


if __name__ == "__main__":
    run_all()
