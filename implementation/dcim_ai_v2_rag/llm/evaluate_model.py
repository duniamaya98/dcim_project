"""
MT-023 Task 3b — Evaluate Fine-Tuned Model

Evaluasi model fine-tuned terhadap test prompts DCIM.
Bisa dijalankan terhadap:
1. Model lokal (adapter LoRA + base model)
2. llama-server endpoint (setelah export ke GGUF)

Usage:
    # Evaluate via llama-server (default, model sudah running)
    python -m dcim_ai.llm.evaluate_model --endpoint http://localhost:8080

    # Evaluate LoRA adapter langsung
    python -m dcim_ai.llm.evaluate_model --adapter dcim_ai/llm/models/v1.0/adapter
"""

import json
import time
import argparse
import requests
from pathlib import Path

# =====================================================
# TEST PROMPTS (DCIM Domain)
# =====================================================

TEST_PROMPTS = [
    {
        "id": 1,
        "category": "anomaly_detection",
        "instruction": "Apakah ada anomali yang terdeteksi? Jelaskan.",
        "input": json.dumps({
            "metrics": {"cpu_usage": 92.5, "memory_usage": 88.3, "disk_io": 45.2, "net_rx": 120.5, "net_tx": 80.3},
            "prediction": "anomaly",
            "severity": "critical",
            "anomaly_votes": 3,
            "drift_score": 3.8,
            "drift_status": "severe_drift",
            "active_domains": ["compute", "memory"],
            "domain_scores": {"compute": 4.5, "memory": 3.8, "storage": 0.5, "network": 0.3},
            "anomaly_ratio": 0.85,
            "root_domain": "compute",
            "rca_confidence": 0.92,
        }),
        "expected_keywords": ["anomali", "critical", "compute", "memory", "drift"],
    },
    {
        "id": 2,
        "category": "root_cause",
        "instruction": "Apa root cause dari masalah ini?",
        "input": "Server metrics — cpu_usage: 95.2, memory_usage: 45.0, disk_io: 30.0, net_rx: 50.0, net_tx: 20.0. Prediksi model: anomaly (3/3 vote). Drift: severe_drift (score: 4.2). Domain aktif: compute (skor: 4.5).",
        "expected_keywords": ["compute", "CPU", "root cause", "penyebab"],
    },
    {
        "id": 3,
        "category": "recommendation",
        "instruction": "Apa rekomendasi tindakan untuk kondisi ini?",
        "input": json.dumps({
            "metrics": {"cpu_usage": 15.0, "memory_usage": 95.8, "disk_io": 20.0, "net_rx": 30.0, "net_tx": 10.0},
            "prediction": "anomaly",
            "severity": "warning",
            "anomaly_votes": 2,
            "drift_score": 2.5,
            "drift_status": "moderate_drift",
            "active_domains": ["memory"],
            "root_domain": "memory",
        }),
        "expected_keywords": ["memory", "memori", "RAM", "rekomendasi", "leak"],
    },
    {
        "id": 4,
        "category": "drift_analysis",
        "instruction": "Analisis drift dari data monitoring berikut.",
        "input": "Data telemetry: cpu_usage: 50.0, memory_usage: 60.0, disk_io: 40.0, net_rx: 100.0, net_tx: 50.0. Drift score: 1.8 (mild_drift). Feature z-scores: cpu_usage=1.2, memory_usage=2.1, disk_io=0.8, net_rx=3.5, net_tx=1.4.",
        "expected_keywords": ["drift", "z-score", "net_rx", "pergeseran"],
    },
    {
        "id": 5,
        "category": "normal_condition",
        "instruction": "Jelaskan kondisi sistem berdasarkan data berikut.",
        "input": json.dumps({
            "metrics": {"cpu_usage": 25.0, "memory_usage": 40.0, "disk_io": 15.0, "net_rx": 50.0, "net_tx": 20.0},
            "prediction": "normal",
            "severity": "normal",
            "anomaly_votes": 0,
            "drift_score": 0.5,
            "drift_status": "stable",
            "active_domains": [],
        }),
        "expected_keywords": ["normal", "stabil", "tidak ada anomali"],
    },
    {
        "id": 6,
        "category": "multi_domain",
        "instruction": "Lakukan analisis lengkap terhadap data monitoring berikut.",
        "input": "Server metrics — cpu_usage: 88.0, memory_usage: 91.0, disk_io: 85.0, net_rx: 200.0, net_tx: 150.0. Prediksi: anomaly (3/3). Drift: severe_drift (4.5). Domain aktif: compute (4.2), memory (3.9), storage (3.5). Anomaly ratio: 0.9. Root cause: compute. Causal chain: compute → memory → storage.",
        "expected_keywords": ["compute", "memory", "storage", "chain", "critical"],
    },
]

SYSTEM_PROMPT = (
    "Kamu adalah DCIM AI Assistant, asisten cerdas untuk monitoring dan analisis "
    "infrastruktur data center. Kamu memahami anomaly detection, drift analysis, "
    "root cause analysis, dan domain correlation pada sistem DCIM. "
    "Jawab dalam Bahasa Indonesia yang jelas dan teknis."
)


# =====================================================
# EVALUATION VIA ENDPOINT (llama-server / Ollama)
# =====================================================

def evaluate_via_endpoint(endpoint, model=None):
    """Evaluate using OpenAI-compatible API endpoint"""

    print(f"[EVAL] Endpoint: {endpoint}")

    results = []

    for test in TEST_PROMPTS:
        prompt = f"{test['instruction']}\n\n{test['input']}"

        # Try OpenAI chat completions format first
        payload = {
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "max_tokens": 512,
            "stream": False,
        }

        if model:
            payload["model"] = model

        start = time.time()

        try:
            # Try /v1/chat/completions
            resp = requests.post(
                f"{endpoint}/v1/chat/completions",
                json=payload,
                timeout=120
            )

            if resp.status_code != 200:
                # Fallback to /completion (llama.cpp native)
                payload_native = {
                    "prompt": f"<|im_start|>system\n{SYSTEM_PROMPT}<|im_end|>\n<|im_start|>user\n{prompt}<|im_end|>\n<|im_start|>assistant\n",
                    "temperature": 0.3,
                    "n_predict": 512,
                    "stop": ["<|im_end|>"],
                }
                resp = requests.post(
                    f"{endpoint}/completion",
                    json=payload_native,
                    timeout=120
                )
                data = resp.json()
                output = data.get("content", "")
            else:
                data = resp.json()
                output = data["choices"][0]["message"]["content"]

        except Exception as e:
            output = f"[ERROR] {e}"

        latency = time.time() - start

        # Score: keyword matching
        output_lower = output.lower()
        keywords_found = sum(
            1 for kw in test["expected_keywords"]
            if kw.lower() in output_lower
        )
        keyword_score = keywords_found / len(test["expected_keywords"])

        # Length check (should be substantive)
        length_ok = len(output) > 50

        # Relevance heuristic
        relevance = 1.0 if keyword_score >= 0.6 and length_ok else (0.5 if keyword_score >= 0.3 else 0.0)

        result = {
            "id": test["id"],
            "category": test["category"],
            "instruction": test["instruction"],
            "output": output[:500],
            "latency": round(latency, 2),
            "keyword_score": round(keyword_score, 2),
            "keywords_found": keywords_found,
            "keywords_total": len(test["expected_keywords"]),
            "length": len(output),
            "relevance": relevance,
        }
        results.append(result)

        status = "✅" if relevance >= 0.5 else "❌"
        print(f"  {status} [{test['category']}] keywords={keywords_found}/{len(test['expected_keywords'])}, "
              f"latency={latency:.1f}s, len={len(output)}")

    return results


# =====================================================
# EVALUATION VIA LOCAL ADAPTER
# =====================================================

def evaluate_via_adapter(adapter_path, gpu=0):
    """Evaluate using local LoRA adapter + base model"""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu)

    print(f"[EVAL] Loading adapter from: {adapter_path}")

    # Load base + adapter
    tokenizer = AutoTokenizer.from_pretrained(adapter_path, trust_remote_code=True)
    base_model = AutoModelForCausalLM.from_pretrained(
        BASE_MODEL,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True,
    )
    model = PeftModel.from_pretrained(base_model, adapter_path)
    model.eval()

    results = []

    for test in TEST_PROMPTS:
        prompt = f"{test['instruction']}\n\n{test['input']}"

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = tokenizer(text, return_tensors="pt").to(model.device)

        start = time.time()
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.3,
                do_sample=True,
                pad_token_id=tokenizer.pad_token_id,
            )

        output_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        latency = time.time() - start

        # Score
        output_lower = output_text.lower()
        keywords_found = sum(1 for kw in test["expected_keywords"] if kw.lower() in output_lower)
        keyword_score = keywords_found / len(test["expected_keywords"])
        length_ok = len(output_text) > 50
        relevance = 1.0 if keyword_score >= 0.6 and length_ok else (0.5 if keyword_score >= 0.3 else 0.0)

        result = {
            "id": test["id"],
            "category": test["category"],
            "instruction": test["instruction"],
            "output": output_text[:500],
            "latency": round(latency, 2),
            "keyword_score": round(keyword_score, 2),
            "keywords_found": keywords_found,
            "keywords_total": len(test["expected_keywords"]),
            "length": len(output_text),
            "relevance": relevance,
        }
        results.append(result)

        status = "✅" if relevance >= 0.5 else "❌"
        print(f"  {status} [{test['category']}] keywords={keywords_found}/{len(test['expected_keywords'])}, "
              f"latency={latency:.1f}s")

    return results


# =====================================================
# REPORT
# =====================================================

def print_report(results, output_path=None):
    """Print evaluation report"""
    print("\n" + "=" * 60)
    print("EVALUATION REPORT")
    print("=" * 60)

    total_relevance = sum(r["relevance"] for r in results) / len(results)
    total_keyword = sum(r["keyword_score"] for r in results) / len(results)
    avg_latency = sum(r["latency"] for r in results) / len(results)

    print(f"\n  Overall Relevance Score: {total_relevance:.2f} / 1.0")
    print(f"  Overall Keyword Score:   {total_keyword:.2f} / 1.0")
    print(f"  Average Latency:         {avg_latency:.1f}s")
    print(f"  Tests Passed (≥0.5):     {sum(1 for r in results if r['relevance'] >= 0.5)}/{len(results)}")

    print("\n  Per-category:")
    for r in results:
        status = "✅" if r["relevance"] >= 0.5 else "❌"
        print(f"    {status} {r['category']}: relevance={r['relevance']}, "
              f"keywords={r['keyword_score']:.0%}, latency={r['latency']:.1f}s")

    # Thresholds (from MT-023 benchmark)
    print("\n  Quality Assessment:")
    if total_relevance >= 0.75:
        print("    🟢 GOOD — Model memahami domain DCIM dengan baik")
    elif total_relevance >= 0.5:
        print("    🟡 ACCEPTABLE — Model cukup memahami, perlu improvement")
    else:
        print("    🔴 POOR — Model belum memahami domain DCIM")

    # Save report
    if output_path:
        report = {
            "timestamp": datetime.now().isoformat() if 'datetime' in dir() else None,
            "overall_relevance": total_relevance,
            "overall_keyword_score": total_keyword,
            "avg_latency": avg_latency,
            "results": results,
        }
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n  Report saved: {output_path}")


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":
    import os
    from datetime import datetime

    BASE_MODEL = "Qwen/Qwen2.5-7B-Instruct-AWQ"

    parser = argparse.ArgumentParser(description="Evaluate DCIM AI model")
    parser.add_argument("--endpoint", type=str, default="http://localhost:8080",
                        help="API endpoint (llama-server or Ollama)")
    parser.add_argument("--adapter", type=str, default=None,
                        help="Path to LoRA adapter (for local eval)")
    parser.add_argument("--gpu", type=int, default=0)
    parser.add_argument("--output", type=str, default=None,
                        help="Path to save evaluation report JSON")

    args = parser.parse_args()

    if args.adapter:
        results = evaluate_via_adapter(args.adapter, gpu=args.gpu)
    else:
        results = evaluate_via_endpoint(args.endpoint)

    output_path = args.output or str(
        Path(__file__).resolve().parent / "datasets" / "eval_report.json"
    )
    print_report(results, output_path=output_path)
