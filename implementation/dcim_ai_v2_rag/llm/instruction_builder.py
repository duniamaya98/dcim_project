"""
MT-023 Task 2 — Instruction Dataset Builder

Mengkonversi enriched incidents menjadi format instruction tuning:
{
    "instruction": "...",
    "input": "...",
    "output": "..."
}

Variasi instruction sesuai MT-023:
1. Jelaskan kondisi sistem / Ringkas kondisi
2. Apa anomaly yang terdeteksi?
3. Apa root cause?
4. Apa dampaknya?
5. Apa rekomendasi tindakan?
6. Analisis drift
7. Analisis domain
8. Analisis temporal

Output: dcim_ai/llm/datasets/dcim_instructions.jsonl
"""

import json
import random
from pathlib import Path
from collections import Counter

INPUT_FILE = Path(__file__).resolve().parent / "datasets" / "enriched_incidents.jsonl"
OUTPUT_FILE = Path(__file__).resolve().parent / "datasets" / "dcim_instructions.jsonl"


# =====================================================
# INSTRUCTION TEMPLATES
# =====================================================

# Setiap kategori punya beberapa variasi prompt agar model fleksibel

INSTRUCTIONS = {
    "summary": [
        "Jelaskan kondisi sistem berdasarkan data berikut.",
        "Ringkas kondisi infrastruktur dari data monitoring ini.",
        "Berikan ringkasan status sistem berdasarkan telemetry berikut.",
        "Apa yang terjadi pada sistem berdasarkan data ini?",
        "Deskripsikan situasi infrastruktur saat ini.",
        "Berikan overview kondisi server berdasarkan metrik ini.",
    ],
    "anomaly": [
        "Apakah ada anomali yang terdeteksi? Jelaskan.",
        "Analisis apakah data ini menunjukkan anomali.",
        "Identifikasi anomali dari data monitoring berikut.",
        "Apakah sistem dalam kondisi normal atau anomali? Jelaskan alasannya.",
        "Deteksi anomali dari metrik server berikut.",
    ],
    "root_cause": [
        "Apa root cause dari masalah ini?",
        "Identifikasi penyebab utama anomali ini.",
        "Analisis root cause dari kondisi sistem berikut.",
        "Apa yang menyebabkan masalah pada infrastruktur ini?",
        "Lakukan root cause analysis dari data berikut.",
        "Tentukan domain penyebab utama masalah ini.",
    ],
    "impact": [
        "Apa dampak dari kondisi ini terhadap infrastruktur?",
        "Jelaskan dampak anomali ini terhadap sistem.",
        "Domain apa saja yang terdampak? Jelaskan.",
        "Analisis dampak lintas domain dari kondisi ini.",
        "Seberapa serius dampak masalah ini?",
    ],
    "recommendation": [
        "Apa rekomendasi tindakan untuk kondisi ini?",
        "Berikan saran penanganan untuk masalah ini.",
        "Apa langkah yang harus diambil untuk mengatasi kondisi ini?",
        "Rekomendasikan tindakan mitigasi.",
        "Apa yang harus dilakukan tim infrastruktur?",
        "Berikan action plan untuk menangani situasi ini.",
    ],
    "drift": [
        "Analisis drift dari data monitoring berikut.",
        "Apakah ada pergeseran distribusi data? Jelaskan.",
        "Evaluasi drift score dan implikasinya.",
        "Bagaimana kondisi drift pada metrik ini?",
    ],
    "domain": [
        "Domain infrastruktur mana yang terpengaruh?",
        "Analisis domain yang aktif dari data berikut.",
        "Jelaskan kondisi per domain infrastruktur.",
        "Identifikasi domain dengan gangguan tertinggi.",
    ],
    "temporal": [
        "Bagaimana tren temporal dari kondisi ini?",
        "Analisis pola waktu dari data monitoring berikut.",
        "Apakah ada pola berulang dalam data ini?",
        "Jelaskan tren anomali dalam window waktu terakhir.",
    ],
    "full_analysis": [
        "Lakukan analisis lengkap terhadap data monitoring berikut.",
        "Berikan analisis komprehensif dari kondisi infrastruktur ini.",
        "Analisis menyeluruh: anomali, root cause, dampak, dan rekomendasi.",
        "Berikan laporan lengkap kondisi sistem dari data berikut.",
    ],
}


# =====================================================
# INPUT FORMATTERS
# =====================================================

def format_input_compact(record):
    """Format input as compact JSON (for structured input)"""
    metrics = record["metrics"]
    prediction = record["prediction"]
    drift = record["drift"]
    domain_state = record["domain_state"]
    rca = record["rca"]
    agg = record.get("aggregation", {})

    return json.dumps({
        "metrics": metrics,
        "prediction": prediction["result"],
        "severity": record["incident"]["severity"],
        "anomaly_votes": prediction["anomaly_votes"],
        "drift_score": drift["score"],
        "drift_status": drift["status"],
        "active_domains": domain_state["active_domains"],
        "domain_scores": domain_state["domain_scores"],
        "anomaly_ratio": agg.get("anomaly_ratio", 0) if agg else 0,
        "root_domain": rca["root_domain"],
        "rca_confidence": rca["confidence"],
    }, ensure_ascii=False)


def format_input_natural(record):
    """Format input as natural language description of metrics"""
    metrics = record["metrics"]
    parts = []
    for key, val in metrics.items():
        parts.append(f"{key}: {val}")
    return "Data telemetry server: " + ", ".join(parts)


def format_input_mixed(record):
    """Format input as a mix of natural text + key data points"""
    metrics = record["metrics"]
    pred = record["prediction"]
    drift = record["drift"]

    text = f"Server metrics — "
    text += ", ".join(f"{k}: {v}" for k, v in metrics.items())
    text += f". Prediksi model: {pred['result']} ({pred['anomaly_votes']}/3 vote). "
    text += f"Drift: {drift['status']} (score: {drift['score']:.2f})."
    return text


# =====================================================
# OUTPUT GENERATORS (per instruction type)
# =====================================================

def generate_output(record, instruction_type):
    """Generate appropriate output based on instruction type"""

    if instruction_type == "summary":
        return record["nl_summary"]

    elif instruction_type == "anomaly":
        pred = record["prediction"]
        text = f"Hasil deteksi: {pred['result']}. "
        text += f"Voting ensemble: {pred['anomaly_votes']}/3 model mendeteksi anomali "
        text += f"(IsolationForest={pred['model_scores']['isolation_forest']}, "
        text += f"LOF={pred['model_scores']['local_outlier_factor']}, "
        text += f"OCSVM={pred['model_scores']['one_class_svm']}). "
        text += f"Severity: {pred['severity']}. "
        text += record["nl_metrics"]
        return text

    elif instruction_type == "root_cause":
        return record["nl_rca"]

    elif instruction_type == "impact":
        text = record["nl_domain"]
        if record.get("nl_temporal"):
            text += " " + record["nl_temporal"]
        return text

    elif instruction_type == "recommendation":
        return record["nl_recommendation"]

    elif instruction_type == "drift":
        return record["nl_drift"]

    elif instruction_type == "domain":
        return record["nl_domain"]

    elif instruction_type == "temporal":
        return record["nl_temporal"]

    elif instruction_type == "full_analysis":
        return record["nl_full_explanation"]

    return record["nl_summary"]


# =====================================================
# DATASET BUILDER
# =====================================================

def build_instructions(records, target_samples=1000):
    """
    Build instruction dataset from enriched records.
    
    Strategy:
    - Record anomali/active domain → lebih banyak variasi instruction (3-5 types)
    - Record normal → 1 type saja
    - Variasi instruction type + input format
    - Target: 500-1000 samples
    """

    instructions_dataset = []
    instruction_id = 0

    # Classify records by interest level
    high_interest = [r for r in records if (
        r["prediction"]["result"] == "anomaly" or
        len(r["domain_state"]["active_domains"]) > 0 or
        r["drift"]["status"] in ("moderate_drift", "severe_drift")
    )]
    low_interest = [r for r in records if r not in high_interest]

    # High-interest records get more instruction types
    hi_types = min(5, len(INSTRUCTIONS))
    lo_types = 1

    estimated = len(high_interest) * hi_types + len(low_interest) * lo_types
    print(f"[BUILD] {len(high_interest)} high-interest × {hi_types} + {len(low_interest)} low-interest × {lo_types} = ~{estimated} samples")

    # Calculate how many instruction types per record
    types_per_record = max(1, target_samples // len(records)) if records else 1
    types_per_record = min(types_per_record, len(INSTRUCTIONS))

    print(f"[BUILD] {len(records)} records × ~{types_per_record} types = ~{len(records) * types_per_record} samples")

    for record in records:
        # Determine interest level
        is_high_interest = (
            record["prediction"]["result"] == "anomaly" or
            len(record["domain_state"]["active_domains"]) > 0 or
            record["drift"]["status"] in ("moderate_drift", "severe_drift")
        )

        max_types = hi_types if is_high_interest else lo_types

        # Select instruction types for this record
        available_types = list(INSTRUCTIONS.keys())

        # Always include relevant types
        priority_types = []

        if record["prediction"]["result"] == "anomaly":
            priority_types.extend(["anomaly", "root_cause", "recommendation", "full_analysis"])
        if record["drift"]["status"] in ("moderate_drift", "severe_drift"):
            priority_types.append("drift")
        if len(record["domain_state"]["active_domains"]) >= 2:
            priority_types.extend(["domain", "impact"])
        if len(record["domain_state"]["active_domains"]) == 1:
            priority_types.append("domain")

        # Fill remaining with random types
        remaining = [t for t in available_types if t not in priority_types]
        random.shuffle(remaining)

        selected_types = list(dict.fromkeys(priority_types + remaining))[:max_types]

        # Low-interest records: just summary or temporal
        if not is_high_interest:
            selected_types = [random.choice(["summary", "temporal", "drift"])]

        for inst_type in selected_types:
            instruction_id += 1

            # Pick random instruction variant
            instruction_text = random.choice(INSTRUCTIONS[inst_type])

            # Pick random input format
            input_format = random.choice([
                format_input_compact,
                format_input_natural,
                format_input_mixed
            ])
            input_text = input_format(record)

            # Generate output
            output_text = generate_output(record, inst_type)

            sample = {
                "id": instruction_id,
                "instruction": instruction_text,
                "input": input_text,
                "output": output_text,
                "metadata": {
                    "source_id": record["id"],
                    "instruction_type": inst_type,
                    "severity": record["incident"]["severity"],
                    "prediction": record["prediction"]["result"],
                    "root_domain": record["rca"]["root_domain"],
                    "timestamp": record.get("timestamp"),
                }
            }

            instructions_dataset.append(sample)

    # Shuffle for training
    random.shuffle(instructions_dataset)

    return instructions_dataset


# =====================================================
# MAIN
# =====================================================

def run_instruction_builder(target_samples=1000):
    print("=" * 60)
    print("MT-023 Task 2 — Instruction Dataset Builder")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        print("Run text_enrichment.py first.")
        return []

    # Load enriched records
    records = []
    with open(INPUT_FILE, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"[LOADED] {len(records)} enriched records")

    # Build instructions
    dataset = build_instructions(records, target_samples=target_samples)

    print(f"[BUILT] {len(dataset)} instruction samples")

    # Save
    with open(OUTPUT_FILE, "w") as f:
        for sample in dataset:
            f.write(json.dumps(sample, ensure_ascii=False) + "\n")

    print(f"[SAVED] {OUTPUT_FILE}")

    # Stats
    type_counts = Counter(s["metadata"]["instruction_type"] for s in dataset)
    print(f"\n[STATS] Instruction type distribution:")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c} ({c/len(dataset)*100:.1f}%)")

    severity_counts = Counter(s["metadata"]["severity"] for s in dataset)
    print(f"\n[STATS] Severity distribution:")
    for s, c in sorted(severity_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c} ({c/len(dataset)*100:.1f}%)")

    # Show samples
    if dataset:
        print("\n" + "=" * 60)
        print("SAMPLE INSTRUCTIONS:")
        print("=" * 60)
        for sample in dataset[:3]:
            print(f"\n--- [{sample['metadata']['instruction_type']}] ---")
            print(f"INSTRUCTION: {sample['instruction']}")
            print(f"INPUT: {sample['input'][:200]}...")
            print(f"OUTPUT: {sample['output'][:300]}...")

    return dataset


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=1000, help="Target number of samples")
    args = parser.parse_args()

    run_instruction_builder(target_samples=args.target)
