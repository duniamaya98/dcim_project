"""
MT-023 Task 3 (Alternative) — Synthetic Dataset Enhancement via Running LLM

Menggunakan model yang sedang berjalan di llama-server untuk:
1. Generate output yang lebih natural dan kaya dari dataset yang ada
2. Memperbanyak variasi jawaban
3. Meningkatkan kualitas dataset untuk fine-tuning nanti

Pendekatan: Teacher-Student
- Teacher: Model running di llama-server (Qwen3-VL-4B)
- Output: Enhanced instruction dataset dengan jawaban dari LLM

Usage:
    python -m dcim_ai.llm.synthetic_generator --endpoint http://localhost:8080
    python -m dcim_ai.llm.synthetic_generator --endpoint http://localhost:8080 --samples 200
"""

import json
import time
import random
import argparse
import requests
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(__file__).resolve().parent / "datasets" / "dcim_instructions.jsonl"
OUTPUT_FILE = Path(__file__).resolve().parent / "datasets" / "dcim_instructions_enhanced.jsonl"

SYSTEM_PROMPT = (
    "Kamu adalah DCIM AI Assistant, asisten cerdas untuk monitoring dan analisis "
    "infrastruktur data center. Kamu memahami anomaly detection, drift analysis, "
    "root cause analysis, dan domain correlation pada sistem DCIM.\n\n"
    "Aturan:\n"
    "- Jawab dalam Bahasa Indonesia yang jelas dan teknis\n"
    "- Berikan analisis yang spesifik berdasarkan data yang diberikan\n"
    "- Sebutkan angka/metrik yang relevan\n"
    "- Berikan rekomendasi yang actionable\n"
    "- Jangan mengarang data yang tidak ada di input"
)


def query_llm(endpoint, instruction, input_text, max_retries=2):
    """Query running LLM for enhanced output"""

    # Truncate input to avoid slow processing on long JSON
    if len(input_text) > 500:
        input_text = input_text[:500] + "..."

    prompt = f"{instruction}\n\n{input_text}"

    # Use chat completions API
    payload = {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 400,
        "stream": False,
    }

    for attempt in range(max_retries + 1):
        try:
            resp = requests.post(
                f"{endpoint}/v1/chat/completions",
                json=payload,
                timeout=30
            )

            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]

        except requests.exceptions.Timeout:
            if attempt < max_retries:
                time.sleep(1)
                continue
            print(f"    [TIMEOUT] attempt {attempt+1}")
            return None
        except Exception as e:
            if attempt < max_retries:
                time.sleep(1)
                continue
            print(f"    [ERROR] {e}")
            return None

    return None


def run_enhancement(endpoint, num_samples=200, priority="high_interest"):
    """
    Enhance dataset by generating LLM outputs for selected samples.
    
    Strategy:
    - Prioritize high-interest records (anomaly, critical, active domains)
    - Generate new outputs using the running LLM
    - Keep original template-based outputs as fallback
    """

    print("=" * 60)
    print("MT-023 — Synthetic Dataset Enhancement")
    print("=" * 60)
    print(f"Endpoint: {endpoint}")
    print(f"Target samples: {num_samples}")

    # Load existing dataset
    records = []
    with open(INPUT_FILE, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"[LOADED] {len(records)} existing instruction samples")

    # Select records to enhance
    if priority == "high_interest":
        # Prioritize anomaly + critical + root_cause records
        candidates = [
            r for r in records
            if (r["metadata"]["prediction"] == "anomaly" or
                r["metadata"]["severity"] in ("critical", "high", "warning") or
                r["metadata"]["root_domain"] != "unknown")
        ]
    else:
        candidates = records

    random.shuffle(candidates)
    selected = candidates[:num_samples]

    print(f"[SELECTED] {len(selected)} records for enhancement")

    # Generate enhanced outputs
    enhanced = []
    failed = 0

    for i, record in enumerate(selected):
        output = query_llm(endpoint, record["instruction"], record["input"])

        if output and len(output) > 50:
            enhanced_record = record.copy()
            enhanced_record["output"] = output
            enhanced_record["metadata"]["enhanced"] = True
            enhanced_record["metadata"]["enhancement_model"] = "Qwen3-VL-4B (llama-server)"
            enhanced.append(enhanced_record)
        else:
            failed += 1
            # Keep original
            record["metadata"]["enhanced"] = False
            enhanced.append(record)

        if (i + 1) % 10 == 0 or (i + 1) <= 3:
            enh_count = len([e for e in enhanced if e.get("metadata", {}).get("enhanced")])
            print(f"  [{i+1}/{len(selected)}] enhanced={enh_count}, failed={failed}")

        # Rate limiting — small delay
        time.sleep(0.2)

    # Combine: enhanced records + remaining original records
    enhanced_ids = {r["id"] for r in enhanced}
    remaining = [r for r in records if r["id"] not in enhanced_ids]

    final_dataset = enhanced + remaining
    random.shuffle(final_dataset)

    # Save
    with open(OUTPUT_FILE, "w") as f:
        for record in final_dataset:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Stats
    enhanced_count = sum(1 for r in final_dataset if r.get("metadata", {}).get("enhanced"))
    print(f"\n[DONE] Total dataset: {len(final_dataset)} samples")
    print(f"[DONE] Enhanced by LLM: {enhanced_count}")
    print(f"[DONE] Template-based: {len(final_dataset) - enhanced_count}")
    print(f"[DONE] Failed: {failed}")
    print(f"[SAVED] {OUTPUT_FILE}")

    # Show sample
    if enhanced:
        sample = next((r for r in enhanced if r["metadata"].get("enhanced")), None)
        if sample:
            print(f"\n{'=' * 60}")
            print("SAMPLE ENHANCED OUTPUT:")
            print(f"{'=' * 60}")
            print(f"INSTRUCTION: {sample['instruction']}")
            print(f"INPUT: {sample['input'][:200]}...")
            print(f"OUTPUT (LLM): {sample['output'][:500]}")

    return final_dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--endpoint", type=str, default="http://localhost:8080")
    parser.add_argument("--samples", type=int, default=200,
                        help="Number of samples to enhance with LLM")
    parser.add_argument("--priority", type=str, default="high_interest",
                        choices=["high_interest", "all"])

    args = parser.parse_args()
    run_enhancement(args.endpoint, num_samples=args.samples, priority=args.priority)
