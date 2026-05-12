"""
MT-023 Task 1 — Dataset Generator

Mensimulasikan seluruh pipeline DCIM AI (MT-018 s.d MT-022) terhadap
data server_metrics untuk menghasilkan dataset structured JSON.

Output: dcim_ai/llm/datasets/raw_incidents.jsonl

Setiap baris berisi:
- input metrics (raw telemetry)
- prediction result (ensemble vote)
- drift detection
- domain state
- aggregation state (temporal)
- incident + RCA result
"""

import os
import sys
import json
import time
import numpy as np
import pandas as pd
from datetime import datetime
from collections import deque
from pathlib import Path

# Ensure project root is in path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from sqlalchemy import create_engine, text

# =====================================================
# CONFIGURATION
# =====================================================

DB_URL = "postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai"
OUTPUT_DIR = Path(__file__).resolve().parent / "datasets"
OUTPUT_FILE = OUTPUT_DIR / "raw_incidents.jsonl"

# Sliding window for correlation simulation
WINDOW_SIZE = 20  # snapshots (simulating 5-min window with batch data)

# Features used by the production model
FEATURE_COLUMNS = ["cpu_usage", "memory_usage", "disk_io", "net_rx", "net_tx"]

# Domain config (matching domain/domain_config.py)
DOMAIN_FEATURE_MAP = {
    "compute": ["cpu_usage"],
    "memory": ["memory_usage"],
    "storage": ["disk_io"],
    "network": ["net_rx", "net_tx"],
}

DOMAIN_SEVERITY_WEIGHT = {
    "compute": 1.0,
    "memory": 1.2,
    "storage": 0.9,
    "network": 0.8,
}

DOMAIN_ACTIVATION_THRESHOLD = 3.0

# Causal topology (matching root_cause/causal_topology.py)
CAUSAL_GRAPH = {
    "power": {"cooling": 0.9, "compute": 0.7},
    "cooling": {"compute": 0.8},
    "compute": {"memory": 0.6, "network": 0.5, "storage": 0.4},
    "storage": {"compute": 0.3},
    "network": {},
    "memory": {}
}


# =====================================================
# LOAD MODEL ARTIFACTS
# =====================================================

def load_production_model():
    """Load model artifacts from registry"""
    import joblib

    registry_path = PROJECT_ROOT / "dcim_ai" / "registry" / "registry.json"
    models_dir = PROJECT_ROOT / "dcim_ai" / "artifacts" / "models"

    with open(registry_path, "r") as f:
        registry = json.load(f)

    version = registry["current_production"]
    model_dir = models_dir / version

    models = joblib.load(model_dir / "models.pkl")
    pipeline = joblib.load(model_dir / "pipeline.pkl")

    with open(model_dir / "baseline_stats.json", "r") as f:
        baseline_stats = json.load(f)

    print(f"[LOADED] Model version: {version}")
    print(f"[LOADED] Features: {baseline_stats.get('features', FEATURE_COLUMNS)}")

    return models, pipeline, baseline_stats, version


# =====================================================
# PIPELINE COMPONENTS (Standalone, no imports needed)
# =====================================================

def calculate_drift_score(input_array, baseline_mean, baseline_std):
    baseline_mean = np.array(baseline_mean)
    baseline_std = np.array(baseline_std)
    baseline_std = np.where(baseline_std == 0, 1e-6, baseline_std)
    z_scores = np.abs((input_array - baseline_mean) / baseline_std)
    drift_score = float(np.mean(z_scores))
    return drift_score, z_scores.tolist()


def classify_drift(drift_score):
    if drift_score < 1:
        return "stable"
    elif drift_score < 2:
        return "mild_drift"
    elif drift_score < 3:
        return "moderate_drift"
    else:
        return "severe_drift"


def compute_domain_state(feature_z_map):
    """Compute domain scores from feature z-scores"""
    domain_scores = {}

    for domain, features in DOMAIN_FEATURE_MAP.items():
        scores = [abs(feature_z_map[f]) for f in features if f in feature_z_map]
        domain_scores[domain] = max(scores) if scores else 0.0

    active_domains = [
        d for d, score in domain_scores.items()
        if score >= DOMAIN_ACTIVATION_THRESHOLD
    ]

    weighted_sum = sum(
        domain_scores[d] * DOMAIN_SEVERITY_WEIGHT.get(d, 1.0)
        for d in domain_scores
    )
    domain_strength_index = weighted_sum / max(len(domain_scores), 1)

    return {
        "domain_scores": domain_scores,
        "active_domains": active_domains,
        "domain_strength_index": round(domain_strength_index, 4)
    }


def compute_aggregation(buffer):
    """Compute temporal aggregation from sliding window buffer"""
    if not buffer:
        return None

    window_size = len(buffer)
    anomaly_count = sum(1 for s in buffer if s["prediction"] == -1)
    severe_drift_count = sum(1 for s in buffer if s["drift_level"] == "severe_drift")

    domain_activity = {}
    domain_time_series = {}

    for entry in buffer:
        for domain, score in entry["domain_scores"].items():
            if domain not in domain_time_series:
                domain_time_series[domain] = []
            domain_time_series[domain].append(score)

            if score >= DOMAIN_ACTIVATION_THRESHOLD:
                domain_activity[domain] = domain_activity.get(domain, 0) + 1

    domain_persistence_ratio = {
        d: domain_activity.get(d, 0) / window_size
        for d in domain_time_series
    }

    # Domain trend
    domain_trend = {}
    for domain, series in domain_time_series.items():
        if len(series) < 3:
            domain_trend[domain] = "stable"
            continue
        slope = np.polyfit(range(len(series)), series, 1)[0]
        if slope > 0.5:
            domain_trend[domain] = "increasing"
        elif slope < -0.5:
            domain_trend[domain] = "decreasing"
        else:
            domain_trend[domain] = "stable"

    # Co-occurrence
    co_occurrence = {}
    for entry in buffer:
        active = [d for d, s in entry["domain_scores"].items() if s >= DOMAIN_ACTIVATION_THRESHOLD]
        for d1 in active:
            if d1 not in co_occurrence:
                co_occurrence[d1] = {}
            for d2 in active:
                if d1 != d2:
                    co_occurrence[d1][d2] = co_occurrence[d1].get(d2, 0) + 1

    return {
        "window_size": window_size,
        "anomaly_count": anomaly_count,
        "anomaly_ratio": round(anomaly_count / window_size, 4),
        "severe_drift_count": severe_drift_count,
        "drift_ratio": round(severe_drift_count / window_size, 4),
        "domain_activity_count": domain_activity,
        "domain_persistence_ratio": {k: round(v, 4) for k, v in domain_persistence_ratio.items()},
        "co_occurrence_matrix": co_occurrence,
        "domain_trend": domain_trend
    }


def compute_severity(domain_state, aggregation_state, snapshot_severity):
    """Severity matrix escalation"""
    if aggregation_state and aggregation_state["anomaly_ratio"] >= 0.6:
        return "critical"

    if aggregation_state:
        persistent = [
            d for d, ratio in aggregation_state["domain_persistence_ratio"].items()
            if ratio >= 0.5
        ]
        if len(persistent) >= 2:
            return "high"

    if domain_state["domain_strength_index"] > 5:
        return "warning"

    return snapshot_severity


def softmax(scores):
    if not scores:
        return {"unknown": 1.0}
    values = np.array(list(scores.values()))
    exp_values = np.exp(values - np.max(values))
    probs = exp_values / exp_values.sum()
    return dict(zip(scores.keys(), [round(float(p), 4) for p in probs]))


def get_downstream(domain):
    return CAUSAL_GRAPH.get(domain, {})


def get_upstream(domain):
    upstream = {}
    for src, targets in CAUSAL_GRAPH.items():
        if domain in targets:
            upstream[src] = targets[domain]
    return upstream


def run_rca(incident):
    """Simplified RCA engine"""
    active_domains = incident.get("active_domains", [])

    if not active_domains:
        return {
            "root_domain": "unknown",
            "domain_probabilities": {"unknown": 1.0},
            "ranked_domains": ["unknown"],
            "causal_chain": [],
            "confidence": 1.0,
            "explanation": "No active domains detected.",
            "entropy": 0.0
        }

    domain_scores = incident.get("domain_scores", {})
    domain_strength_index = incident.get("domain_strength_index", 0)
    anomaly_ratio = incident.get("anomaly_ratio", 0)
    drift_ratio = incident.get("drift_ratio", 0)
    persistence = incident.get("domain_persistence_ratio", {})
    domain_trend = incident.get("domain_trend", {})

    raw_scores = {}

    for domain in active_domains:
        upstream = get_upstream(domain)
        downstream = get_downstream(domain)

        topology_score = sum(downstream.values()) * 0.6 + sum(upstream.values()) * 0.4
        strength_score = domain_scores.get(domain, 0) / (domain_strength_index + 1e-6)
        persistence_score = persistence.get(domain, 0)

        trend_value = domain_trend.get(domain, "stable")
        trend_score = 1.0 if trend_value == "increasing" else (-0.5 if trend_value == "decreasing" else 0.2)

        score = (
            0.30 * topology_score +
            0.25 * strength_score +
            0.20 * persistence_score +
            0.10 * trend_score +
            0.10 * anomaly_ratio +
            0.05 * drift_ratio
        )
        raw_scores[domain] = score

    domain_probabilities = softmax(raw_scores)
    ranked_domains = sorted(domain_probabilities, key=domain_probabilities.get, reverse=True)
    root_domain = ranked_domains[0]
    confidence = max(domain_probabilities.values())

    # Causal chain (DFS, max depth 3)
    chain = []
    visited = set()

    def dfs(d, depth=0):
        if depth > 3 or d in visited:
            return
        visited.add(d)
        if domain_probabilities.get(d, 0) < 0.15:
            return
        if d in active_domains:
            chain.append(d)
        for nxt in get_downstream(d):
            if nxt in active_domains:
                dfs(nxt, depth + 1)

    dfs(root_domain)

    # Explanation
    if len(chain) <= 1:
        explanation = f"{root_domain} identified as primary root cause based on composite scoring."
    else:
        chain_text = " → ".join(chain)
        explanation = f"Root cause chain: {chain_text}. Composite scoring applied."

    # Entropy
    probs = list(domain_probabilities.values())
    entropy = round(-sum(p * np.log(p + 1e-12) for p in probs), 4)

    return {
        "root_domain": root_domain,
        "domain_probabilities": domain_probabilities,
        "ranked_domains": ranked_domains,
        "causal_chain": chain,
        "confidence": round(confidence, 4),
        "explanation": explanation,
        "entropy": entropy
    }


# =====================================================
# MAIN PIPELINE SIMULATION
# =====================================================

def run_simulation():
    """
    Run full DCIM pipeline simulation on all server_metrics data.
    Produces one JSONL record per data point that triggers an incident.
    """

    print("=" * 60)
    print("MT-023 Task 1 — DCIM Dataset Generator")
    print("=" * 60)

    # Load model
    models, pipeline, baseline_stats, model_version = load_production_model()

    feature_columns = baseline_stats.get("features", FEATURE_COLUMNS)
    baseline_mean = np.array(baseline_stats["mean"])
    baseline_std = np.array(baseline_stats["std"])

    # Load data from DB
    print("\n[DB] Loading server_metrics...")
    engine = create_engine(DB_URL)

    with engine.connect() as conn:
        df = pd.read_sql(
            text("SELECT * FROM server_metrics ORDER BY time ASC"),
            conn
        )

    print(f"[DB] Loaded {len(df)} rows")
    print(f"[DB] Columns: {list(df.columns)}")
    print(f"[DB] Date range: {df['time'].min()} → {df['time'].max()}")

    # Prepare features
    df_features = df[feature_columns].copy()
    df_features = df_features.dropna()

    print(f"[PREP] Valid rows after dropna: {len(df_features)}")

    # Transform
    X = pipeline.transform(df_features)

    # Sliding window buffer
    buffer = deque(maxlen=WINDOW_SIZE)

    # Output
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_records = []

    total_anomalies = 0
    total_incidents = 0

    print(f"\n[SIM] Running pipeline simulation on {len(X)} samples...")
    print(f"[SIM] Window size: {WINDOW_SIZE}")
    print(f"[SIM] Model: {model_version}")
    print()

    for idx in range(len(X)):
        row = X[idx]
        raw_values = df_features.iloc[idx].values
        timestamp = str(df.iloc[idx]["time"]) if "time" in df.columns else None
        hostname = df.iloc[idx].get("hostname", "unknown") if "hostname" in df.columns else "unknown"

        # ─── 1. Ensemble Prediction ───
        iso_pred = models["isolation_forest"].predict(row.reshape(1, -1))[0]
        lof_pred = models["local_outlier_factor"].predict(row.reshape(1, -1))[0]
        svm_pred = models["one_class_svm"].predict(row.reshape(1, -1))[0]

        votes = [
            1 if iso_pred == -1 else 0,
            1 if lof_pred == -1 else 0,
            1 if svm_pred == -1 else 0
        ]
        anomaly_votes = sum(votes)
        prediction = -1 if anomaly_votes >= 2 else 1
        final_prediction = "anomaly" if prediction == -1 else "normal"

        if prediction == -1:
            total_anomalies += 1

        # Severity from votes
        if anomaly_votes == 3:
            snapshot_severity = "critical"
        elif anomaly_votes == 2:
            snapshot_severity = "warning"
        elif anomaly_votes == 1:
            snapshot_severity = "weak_signal"
        else:
            snapshot_severity = "normal"

        # ─── 2. Drift Detection ───
        drift_score, feature_z_scores = calculate_drift_score(
            raw_values, baseline_mean, baseline_std
        )
        drift_status = classify_drift(drift_score)

        # ─── 3. Domain Scoring ───
        feature_z_map = dict(zip(feature_columns, feature_z_scores))
        domain_state = compute_domain_state(feature_z_map)

        # ─── 4. Add to buffer ───
        buffer.append({
            "domain_scores": domain_state["domain_scores"],
            "prediction": prediction,
            "drift_level": drift_status
        })

        # ─── 5. Aggregation ───
        aggregation_state = compute_aggregation(list(buffer))

        # ─── 6. Severity Matrix ───
        final_severity = compute_severity(domain_state, aggregation_state, snapshot_severity)

        # ─── 7. Build Incident ───
        confidence = 0.5
        if aggregation_state:
            confidence = min(1.0, aggregation_state["anomaly_ratio"] + aggregation_state["drift_ratio"])

        incident = {
            "severity": final_severity,
            "confidence": round(confidence, 4),
            "active_domains": domain_state["active_domains"],
            "domain_scores": domain_state["domain_scores"],
            "domain_strength_index": domain_state["domain_strength_index"],
            "anomaly_ratio": aggregation_state["anomaly_ratio"] if aggregation_state else 0,
            "drift_ratio": aggregation_state["drift_ratio"] if aggregation_state else 0,
            "domain_persistence_ratio": aggregation_state["domain_persistence_ratio"] if aggregation_state else {},
            "domain_trend": aggregation_state["domain_trend"] if aggregation_state else {},
            "co_occurrence_matrix": aggregation_state["co_occurrence_matrix"] if aggregation_state else {}
        }

        # ─── 8. RCA ───
        rca_result = run_rca(incident)

        # ─── 9. Compose full record ───
        # Only save records that have some signal (anomaly, drift, or active domains)
        has_signal = (
            prediction == -1 or
            drift_status != "stable" or
            len(domain_state["active_domains"]) > 0
        )

        if has_signal:
            total_incidents += 1

            record = {
                "id": total_incidents,
                "timestamp": timestamp,
                "hostname": hostname,
                "model_version": model_version,

                # Raw input
                "metrics": {col: round(float(raw_values[i]), 4) for i, col in enumerate(feature_columns)},

                # Prediction
                "prediction": {
                    "result": final_prediction,
                    "anomaly_votes": anomaly_votes,
                    "severity": snapshot_severity,
                    "model_scores": {
                        "isolation_forest": int(iso_pred),
                        "local_outlier_factor": int(lof_pred),
                        "one_class_svm": int(svm_pred)
                    }
                },

                # Drift
                "drift": {
                    "score": round(drift_score, 4),
                    "status": drift_status,
                    "feature_z_scores": {col: round(float(feature_z_scores[i]), 4) for i, col in enumerate(feature_columns)}
                },

                # Domain
                "domain_state": domain_state,

                # Temporal
                "aggregation": aggregation_state,

                # Incident
                "incident": {
                    "severity": final_severity,
                    "confidence": round(confidence, 4),
                },

                # RCA
                "rca": rca_result
            }

            output_records.append(record)

        # Progress
        if (idx + 1) % 2000 == 0:
            print(f"  [{idx+1}/{len(X)}] anomalies={total_anomalies}, incidents={total_incidents}")

    # ─── Write output ───
    print(f"\n[DONE] Total samples processed: {len(X)}")
    print(f"[DONE] Total anomalies: {total_anomalies}")
    print(f"[DONE] Total records with signal: {total_incidents}")

    with open(OUTPUT_FILE, "w") as f:
        for record in output_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"[SAVED] {OUTPUT_FILE} ({total_incidents} records)")

    # Stats summary
    if output_records:
        severities = [r["incident"]["severity"] for r in output_records]
        from collections import Counter
        sev_counts = Counter(severities)
        print(f"\n[STATS] Severity distribution:")
        for sev, count in sorted(sev_counts.items(), key=lambda x: -x[1]):
            print(f"  {sev}: {count} ({count/len(output_records)*100:.1f}%)")

        rca_roots = [r["rca"]["root_domain"] for r in output_records]
        root_counts = Counter(rca_roots)
        print(f"\n[STATS] Root cause distribution:")
        for root, count in sorted(root_counts.items(), key=lambda x: -x[1]):
            print(f"  {root}: {count} ({count/len(output_records)*100:.1f}%)")

    return output_records


if __name__ == "__main__":
    run_simulation()
