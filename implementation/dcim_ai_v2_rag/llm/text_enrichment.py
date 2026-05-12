"""
MT-023 Task 1b — Text Enrichment

Mengkonversi structured JSON incident menjadi natural language explanation.
Setiap record dari raw_incidents.jsonl diubah menjadi teks penjelasan
yang bisa digunakan sebagai training data LLM.

Output: dcim_ai/llm/datasets/enriched_incidents.jsonl
"""

import json
import random
from pathlib import Path

INPUT_FILE = Path(__file__).resolve().parent / "datasets" / "raw_incidents.jsonl"
OUTPUT_FILE = Path(__file__).resolve().parent / "datasets" / "enriched_incidents.jsonl"


# =====================================================
# DOMAIN NAME MAPPING (untuk bahasa natural)
# =====================================================

DOMAIN_NAMES = {
    "compute": "komputasi (CPU)",
    "memory": "memori (RAM)",
    "storage": "penyimpanan (Disk I/O)",
    "network": "jaringan (Network)",
    "power": "daya listrik (Power)",
    "cooling": "pendinginan (Cooling)",
    "unknown": "tidak teridentifikasi"
}

SEVERITY_DESC = {
    "critical": "kondisi KRITIS yang memerlukan tindakan segera",
    "high": "kondisi TINGGI dengan potensi eskalasi",
    "warning": "kondisi PERINGATAN yang perlu dimonitor",
    "weak_signal": "sinyal lemah yang menunjukkan potensi masalah",
    "normal": "kondisi normal tanpa anomali signifikan"
}

DRIFT_DESC = {
    "stable": "stabil dan sesuai dengan baseline",
    "mild_drift": "mengalami pergeseran ringan dari baseline",
    "moderate_drift": "mengalami pergeseran moderat dari baseline",
    "severe_drift": "mengalami pergeseran berat dari baseline, menandakan perubahan pola signifikan"
}


# =====================================================
# ENRICHMENT FUNCTIONS
# =====================================================

def enrich_summary(record):
    """Generate ringkasan kondisi sistem"""
    prediction = record["prediction"]["result"]
    severity = record["incident"]["severity"]
    drift_status = record["drift"]["status"]
    active_domains = record["domain_state"]["active_domains"]
    rca = record["rca"]

    # Opening
    if prediction == "anomaly":
        opening = "Sistem mendeteksi **anomali**"
    else:
        opening = "Sistem mendeteksi **kondisi tidak biasa**"

    # Severity
    sev_text = SEVERITY_DESC.get(severity, severity)

    # Domains
    if active_domains:
        domain_names = [DOMAIN_NAMES.get(d, d) for d in active_domains]
        if len(domain_names) == 1:
            domain_text = f"pada domain {domain_names[0]}"
        else:
            domain_text = f"pada domain {', '.join(domain_names[:-1])} dan {domain_names[-1]}"
    else:
        domain_text = "tanpa domain spesifik yang terpengaruh"

    # Drift
    drift_text = DRIFT_DESC.get(drift_status, drift_status)

    summary = f"{opening} dengan {sev_text} {domain_text}. Distribusi data {drift_text}."

    return summary


def enrich_metrics_description(record):
    """Describe raw metrics in natural language"""
    metrics = record["metrics"]
    parts = []

    if "cpu_usage" in metrics:
        cpu = metrics["cpu_usage"]
        if cpu > 90:
            parts.append(f"CPU usage sangat tinggi ({cpu:.1f}%)")
        elif cpu > 70:
            parts.append(f"CPU usage tinggi ({cpu:.1f}%)")
        elif cpu > 50:
            parts.append(f"CPU usage moderat ({cpu:.1f}%)")
        else:
            parts.append(f"CPU usage rendah ({cpu:.1f}%)")

    if "memory_usage" in metrics:
        mem = metrics["memory_usage"]
        if mem > 90:
            parts.append(f"memory usage kritis ({mem:.1f}%)")
        elif mem > 70:
            parts.append(f"memory usage tinggi ({mem:.1f}%)")
        elif mem > 50:
            parts.append(f"memory usage moderat ({mem:.1f}%)")
        else:
            parts.append(f"memory usage rendah ({mem:.1f}%)")

    if "disk_io" in metrics:
        dio = metrics["disk_io"]
        if dio > 80:
            parts.append(f"disk I/O sangat tinggi ({dio:.1f})")
        elif dio > 50:
            parts.append(f"disk I/O tinggi ({dio:.1f})")
        else:
            parts.append(f"disk I/O normal ({dio:.1f})")

    if "net_rx" in metrics and "net_tx" in metrics:
        rx = metrics["net_rx"]
        tx = metrics["net_tx"]
        parts.append(f"network RX={rx:.1f}, TX={tx:.1f}")

    return "Kondisi metrik: " + "; ".join(parts) + "."


def enrich_drift_analysis(record):
    """Describe drift detection result"""
    drift = record["drift"]
    score = drift["score"]
    status = drift["status"]
    z_scores = drift["feature_z_scores"]

    text = f"Drift score: {score:.2f} ({status}). "

    # Find most drifted features
    sorted_z = sorted(z_scores.items(), key=lambda x: abs(x[1]), reverse=True)
    top_drifted = [(f, z) for f, z in sorted_z if abs(z) > 2.0]

    if top_drifted:
        parts = [f"{f} (z={z:.2f})" for f, z in top_drifted[:3]]
        text += f"Fitur dengan drift tertinggi: {', '.join(parts)}."
    else:
        text += "Tidak ada fitur dengan drift signifikan (z > 2.0)."

    return text


def enrich_domain_analysis(record):
    """Describe domain state"""
    ds = record["domain_state"]
    active = ds["active_domains"]
    scores = ds["domain_scores"]
    strength = ds["domain_strength_index"]

    if not active:
        return f"Tidak ada domain yang melewati threshold aktivasi. Domain strength index: {strength:.2f}."

    parts = []
    for d in active:
        dname = DOMAIN_NAMES.get(d, d)
        dscore = scores.get(d, 0)
        parts.append(f"{dname} (skor: {dscore:.2f})")

    text = f"Domain aktif: {', '.join(parts)}. "
    text += f"Domain strength index: {strength:.2f}."

    if len(active) >= 2:
        text += " Terdapat interaksi lintas domain yang perlu diperhatikan."

    return text


def enrich_temporal_analysis(record):
    """Describe aggregation/temporal state"""
    agg = record.get("aggregation")
    if not agg:
        return "Data temporal belum cukup untuk analisis."

    anomaly_ratio = agg["anomaly_ratio"]
    drift_ratio = agg["drift_ratio"]
    window = agg["window_size"]
    trends = agg.get("domain_trend", {})

    text = f"Dalam window {window} snapshot terakhir: "
    text += f"rasio anomali {anomaly_ratio:.0%}, rasio drift berat {drift_ratio:.0%}. "

    # Trends
    increasing = [d for d, t in trends.items() if t == "increasing"]
    if increasing:
        names = [DOMAIN_NAMES.get(d, d) for d in increasing]
        text += f"Tren meningkat pada: {', '.join(names)}. "

    # Persistence
    persistent = [
        d for d, r in agg.get("domain_persistence_ratio", {}).items()
        if r >= 0.5
    ]
    if persistent:
        names = [DOMAIN_NAMES.get(d, d) for d in persistent]
        text += f"Domain persisten (>50% window): {', '.join(names)}."

    return text


def enrich_rca_analysis(record):
    """Describe RCA result"""
    rca = record["rca"]
    root = rca["root_domain"]
    root_name = DOMAIN_NAMES.get(root, root)
    confidence = rca["confidence"]
    entropy = rca["entropy"]
    chain = rca.get("causal_chain", [])
    probs = rca.get("domain_probabilities", {})

    text = f"Root cause analysis menunjukkan domain {root_name} sebagai penyebab utama "
    text += f"dengan confidence {confidence:.0%}. "

    if chain and len(chain) > 1:
        chain_names = [DOMAIN_NAMES.get(d, d) for d in chain]
        text += f"Rantai kausal: {' → '.join(chain_names)}. "

    if entropy > 1.2:
        text += "Entropy tinggi menandakan ketidakpastian — kemungkinan multi-domain failure. "
    elif entropy < 0.5:
        text += "Entropy rendah menandakan root cause yang jelas dan terfokus. "

    # Other probable domains
    other_probs = [(d, p) for d, p in probs.items() if d != root and p > 0.15]
    if other_probs:
        parts = [f"{DOMAIN_NAMES.get(d, d)} ({p:.0%})" for d, p in sorted(other_probs, key=lambda x: -x[1])]
        text += f"Domain lain yang berpotensi: {', '.join(parts)}."

    return text


def enrich_recommendation(record):
    """Generate actionable recommendation"""
    severity = record["incident"]["severity"]
    rca = record["rca"]
    root = rca["root_domain"]
    drift_status = record["drift"]["status"]
    active_domains = record["domain_state"]["active_domains"]

    recommendations = []

    # Severity-based
    if severity == "critical":
        recommendations.append("Eskalasi segera ke tim infrastruktur untuk investigasi.")
    elif severity == "high":
        recommendations.append("Monitor intensif dan siapkan rencana mitigasi.")

    # Domain-specific
    if root == "compute" or "compute" in active_domains:
        recommendations.append("Periksa proses dengan CPU usage tinggi, pertimbangkan load balancing atau scaling.")
    if root == "memory" or "memory" in active_domains:
        recommendations.append("Periksa memory leak, pertimbangkan restart service atau penambahan RAM.")
    if root == "storage" or "storage" in active_domains:
        recommendations.append("Periksa disk I/O bottleneck, cek proses yang melakukan heavy write/read.")
    if root == "network" or "network" in active_domains:
        recommendations.append("Periksa network throughput dan packet loss, cek konfigurasi firewall/switch.")

    # Drift-based
    if drift_status in ("moderate_drift", "severe_drift"):
        recommendations.append("Distribusi data bergeser signifikan — pertimbangkan retraining model.")

    # Multi-domain
    if len(active_domains) >= 2:
        recommendations.append("Multiple domain terdampak — periksa dependensi antar komponen infrastruktur.")

    if not recommendations:
        recommendations.append("Lanjutkan monitoring rutin, tidak ada tindakan mendesak diperlukan.")

    return "Rekomendasi: " + " ".join(recommendations)


def enrich_record(record):
    """
    Enrich a single record with all natural language descriptions.
    Returns the original record + enrichment fields.
    """
    enriched = record.copy()

    enriched["nl_summary"] = enrich_summary(record)
    enriched["nl_metrics"] = enrich_metrics_description(record)
    enriched["nl_drift"] = enrich_drift_analysis(record)
    enriched["nl_domain"] = enrich_domain_analysis(record)
    enriched["nl_temporal"] = enrich_temporal_analysis(record)
    enriched["nl_rca"] = enrich_rca_analysis(record)
    enriched["nl_recommendation"] = enrich_recommendation(record)

    # Full explanation (combined)
    enriched["nl_full_explanation"] = (
        f"{enriched['nl_summary']}\n\n"
        f"{enriched['nl_metrics']}\n\n"
        f"{enriched['nl_drift']}\n\n"
        f"{enriched['nl_domain']}\n\n"
        f"{enriched['nl_temporal']}\n\n"
        f"{enriched['nl_rca']}\n\n"
        f"{enriched['nl_recommendation']}"
    )

    return enriched


# =====================================================
# MAIN
# =====================================================

def run_enrichment():
    print("=" * 60)
    print("MT-023 Task 1b — Text Enrichment")
    print("=" * 60)

    if not INPUT_FILE.exists():
        print(f"[ERROR] Input file not found: {INPUT_FILE}")
        print("Run dataset_generator.py first.")
        return []

    # Load raw records
    records = []
    with open(INPUT_FILE, "r") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    print(f"[LOADED] {len(records)} raw records")

    # Enrich
    enriched = []
    for i, record in enumerate(records):
        enriched_record = enrich_record(record)
        enriched.append(enriched_record)

        if (i + 1) % 1000 == 0:
            print(f"  [{i+1}/{len(records)}] enriched")

    # Save
    with open(OUTPUT_FILE, "w") as f:
        for record in enriched:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\n[SAVED] {OUTPUT_FILE} ({len(enriched)} records)")

    # Show sample
    if enriched:
        sample = enriched[min(5, len(enriched) - 1)]
        print("\n" + "=" * 60)
        print("SAMPLE ENRICHMENT:")
        print("=" * 60)
        print(sample["nl_full_explanation"])

    return enriched


if __name__ == "__main__":
    run_enrichment()
