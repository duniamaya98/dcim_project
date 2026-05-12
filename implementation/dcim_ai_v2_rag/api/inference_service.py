from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_client import Counter, Histogram, generate_latest, Gauge
from fastapi.responses import Response

import numpy as np
import pandas as pd
import time
import threading

from dcim_ai.monitoring.event_logger import log_event
from dcim_ai.features.drift_detection import calculate_drift_score, classify_drift
from dcim_ai.training.train_anomaly_model import train_model as trigger_retraining
from dcim_ai.inference.model_manager import ModelManager

from dcim_ai.correlation.correlation_buffer import CorrelationBuffer
from dcim_ai.config.domain_mapping import DOMAIN_FEATURE_MAP

from dcim_ai.domain.domain_engine import DomainEngine
from dcim_ai.correlation.aggregation_engine import AggregationEngine

from dcim_ai.correlation.correlation_engine import CorrelationEngine

correlation_engine = CorrelationEngine()

domain_engine = DomainEngine()
aggregation_engine = AggregationEngine()

# =====================================================
# INIT APP
# =====================================================

app = FastAPI(title="DCIM AI Anomaly Detection API")

model_manager = ModelManager()

correlation_buffer = CorrelationBuffer(window_seconds=300)
# =====================================================
# PROMETHEUS METRICS
# =====================================================

REQUEST_COUNT = Counter("dcim_requests_total", "Total inference requests")
ANOMALY_COUNT = Counter("dcim_anomalies_total", "Total anomalies detected")
NORMAL_COUNT = Counter("dcim_normals_total", "Total normal predictions")
RETRAIN_COUNT = Counter("dcim_retrain_total", "Total retraining events")
INFERENCE_LATENCY = Histogram("dcim_inference_latency_seconds", "Inference latency")
CORRELATION_INCIDENT_TOTAL = Counter(
    "dcim_correlation_incidents_total",
    "Total correlation incidents generated"
)

CRITICAL_INCIDENT_TOTAL = Counter(
    "dcim_critical_incidents_total",
    "Total critical incidents"
)

MULTI_DOMAIN_INCIDENT_TOTAL = Counter(
    "dcim_multi_domain_incidents_total",
    "Total multi-domain incidents"
)

CORRELATION_CONFIDENCE = Histogram(
    "dcim_correlation_confidence",
    "Distribution of incident confidence"
)

DOMAIN_ACTIVITY_GAUGE = Gauge(
    "dcim_domain_active_count",
    "Number of active domains in latest incident"
)

ANOMALY_RATIO_GAUGE = Gauge(
    "dcim_temporal_anomaly_ratio",
    "Anomaly ratio in rolling window"
)



@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")


# =====================================================
# GLOBAL STATE (Cooldown Control)
# =====================================================


last_alert_time = 0
ALERT_COOLDOWN = 60  # seconds

last_retrain_time = 0
RETRAIN_COOLDOWN = 300  # seconds


# =====================================================
# SAFE RETRAIN WRAPPER
# =====================================================

def safe_retrain():
    try:
        trigger_retraining()
        print("[AUTO-RETRAIN] Completed successfully.")
    except Exception as e:
        print("[AUTO-RETRAIN-ERROR]", e)


# =====================================================
# INPUT SCHEMA
# =====================================================

class MetricsInput(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_io: float
    net_rx: float
    net_tx: float


# =====================================================
# HEALTH CHECK
# =====================================================

@app.get("/")
def health_check():
    _, _, _, model_version = model_manager.get()
    return {
        "status": "running",
        "model_version": model_version
    }


# =====================================================
# PREDICTION ENDPOINT
# =====================================================

@app.post("/predict")
def predict(data: MetricsInput):

    global last_alert_time
    global last_retrain_time

    start_time = time.time()
    REQUEST_COUNT.inc()

    # 🔥 ALWAYS GET LATEST MODEL (HOT RELOAD SUPPORT)
    models, pipeline, baseline_stats, model_version, correlation_config = model_manager.get()

    input_dict = data.dict()
    df = pd.DataFrame([input_dict])

    # =========================
    # FEATURE TRANSFORM
    # =========================
    X = pipeline.transform(df)

    # =========================
    # MULTI-MODEL PREDICTION
    # =========================
    iso_pred = models["isolation_forest"].predict(X)[0]
    lof_pred = models["local_outlier_factor"].predict(X)[0]
    svm_pred = models["one_class_svm"].predict(X)[0]

    iso_score = models["isolation_forest"].decision_function(X)[0]
    lof_score = models["local_outlier_factor"].decision_function(X)[0]
    svm_score = models["one_class_svm"].decision_function(X)[0]

    votes = [
        1 if iso_pred == -1 else 0,
        1 if lof_pred == -1 else 0,
        1 if svm_pred == -1 else 0
    ]

    anomaly_votes = sum(votes)

    # =========================
    # FINAL DECISION
    # =========================
    final_prediction = "anomaly" if anomaly_votes >= 2 else "normal"

    if final_prediction == "anomaly":
        ANOMALY_COUNT.inc()
    else:
        NORMAL_COUNT.inc()

    # =========================
    # SEVERITY CLASSIFICATION
    # =========================
    if anomaly_votes == 3:
        severity = "critical"
    elif anomaly_votes == 2:
        severity = "warning"
    elif anomaly_votes == 1:
        severity = "weak_signal"
    else:
        severity = "normal"

    # =========================
    # DRIFT DETECTION
    # =========================
    raw_values = df[pipeline.feature_columns].values[0]

    drift_score, feature_z_scores = calculate_drift_score(
        raw_values,
        baseline_stats["mean"],
        baseline_stats["std"]
    )

    drift_status = classify_drift(drift_score)

    current_time = time.time()

    

    # =========================
    # DOMAIN SCORING (Drift-based)
    # =========================

    feature_z_map = dict(zip(pipeline.feature_columns, feature_z_scores))
    domain_state = domain_engine.compute(feature_z_map)

    domain_scores = {}

    for domain, features in DOMAIN_FEATURE_MAP.items():
        scores = [
            abs(feature_z_map[f])
            for f in features
            if f in feature_z_map
        ]

        domain_scores[domain] = max(scores) if scores else 0.0
    
    # =========================
    # TEMPORAL CORRELATION
    # =========================

    correlation_buffer.add_snapshot(
        domain_scores=domain_scores,
        prediction=-1 if final_prediction == "anomaly" else 1,
        drift_level=drift_status
    )

    # =========================
    # AGGREGATION
    # =========================
    aggregation_state = aggregation_engine.compute(
        correlation_buffer.get_buffer()
    )
    incident = correlation_engine.evaluate(
        domain_state=domain_state,
        aggregation_state=aggregation_state,
        snapshot_severity=severity
    )
    # =========================
    # CORRELATION METRICS (FIXED)
    # =========================

    CORRELATION_INCIDENT_TOTAL.inc()

    if incident["severity"] == "critical":
        CRITICAL_INCIDENT_TOTAL.inc()

    if len(incident["active_domains"]) >= 2:
        MULTI_DOMAIN_INCIDENT_TOTAL.inc()

    CORRELATION_CONFIDENCE.observe(incident["confidence"])

    DOMAIN_ACTIVITY_GAUGE.set(len(incident["active_domains"]))

    if aggregation_state:
        ANOMALY_RATIO_GAUGE.set(aggregation_state.anomaly_ratio)

    temporal_features = correlation_buffer.aggregate()
    if aggregation_state and aggregation_state.anomaly_ratio >= 0.8:
        if current_time - last_retrain_time > RETRAIN_COOLDOWN:
            print("[AUTO-RETRAIN] High anomaly ratio detected.")
            RETRAIN_COUNT.inc()
            threading.Thread(target=safe_retrain, daemon=True).start()
            last_retrain_time = current_time
    
    if aggregation_state and aggregation_state.anomaly_ratio == 1.0:
        if aggregation_state.window_size >= 5:
            print("[ESCALATION] Critical burst pattern detected.")

    # =========================
    # AUTO RETRAIN (COOLDOWN SAFE)
    # =========================
    if drift_status == "severe_drift" and current_time - last_retrain_time > RETRAIN_COOLDOWN:
        print("[AUTO-RETRAIN] Severe drift detected.")
        RETRAIN_COUNT.inc()
        threading.Thread(target=safe_retrain, daemon=True).start()
        last_retrain_time = current_time

    # =========================
    # ALERT CONTROL (ANTI-SPAM)
    # =========================
    should_alert = severity in ["critical", "warning"]

    ensemble_score = float((iso_score + lof_score + svm_score) / 3)

    if should_alert and current_time - last_alert_time > ALERT_COOLDOWN:
        print(f"[ALERT] {severity.upper()} | Score={ensemble_score}")
        last_alert_time = current_time

    # =========================
    # EVENT LOGGING
    # =========================
    event_payload = {
        "model_version": model_version,
        "prediction": final_prediction,
        "severity": severity,
        "ensemble_score": ensemble_score,
        "drift_score": float(drift_score),
        "drift_status": drift_status,
        **input_dict
    }

    log_event(event_payload)

    # =========================
    # LATENCY METRIC
    # =========================
    INFERENCE_LATENCY.observe(time.time() - start_time)

    return {
        "model_version": model_version,
        "prediction": final_prediction,
        "severity": severity,
        "ensemble_score": ensemble_score,
        "model_votes": {
            "isolation_forest": int(iso_pred),
            "local_outlier_factor": int(lof_pred),
            "one_class_svm": int(svm_pred)
        },
        "drift_score": float(drift_score),
        "drift_status": drift_status,
        "domain_scores": domain_scores,
        "temporal_correlation": temporal_features,
        "feature_z_scores": [float(x) for x in feature_z_scores],
        "domain_scores": domain_state.domain_scores,
        "active_domains": domain_state.active_domains,
        "domain_strength_index": domain_state.domain_strength_index,
        "aggregation": aggregation_state.__dict__ if aggregation_state else None,
        "incident": incident,
        "correlation_version": correlation_config.get("correlation_version"),
        "correlation_strategy": correlation_config.get("correlation_strategy")
    }