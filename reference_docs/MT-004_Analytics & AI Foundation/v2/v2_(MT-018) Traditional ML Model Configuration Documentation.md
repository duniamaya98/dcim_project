---
title: "(MT-018) Traditional ML Model Configuration Documentation"
created: 2026-02-13
updated: 2026-07-10
version: 2.0
type: configuration-documentation
task_id: MT-018
block: 7
assignee: Fakhri Aulia R
status: done
dcim_wiki_section: block7-analytics-ai-engine → §3 Anomaly Detection, §8 Model Training Pipeline
tags:
  - machine-learning
  - anomaly-detection
  - configuration
  - isolation-forest
  - ensemble
  - lof
  - ocsvm
  - feature-pipeline
  - model-registry
  - timescaledb
  - kafka
  - z-score
  - drift-detection
---

# (MT-018) Traditional ML Model Configuration Documentation

> **Version:** 2.0 — restructured, aligned with dcim-wiki reference design, updated berdasarkan implementasi aktual di `dcim_ai_v2_rag`.

---

## Daftar Isi

1. [System Configuration Overview](#1-system-configuration-overview)
2. [Infrastructure Configuration](#2-infrastructure-configuration)
3. [Database Configuration](#3-database-configuration)
4. [Dataset Preparation Configuration](#4-dataset-preparation-configuration)
5. [Training Script Configuration](#5-training-script-configuration)
6. [Model Configuration](#6-model-configuration)
7. [Model Artifact Configuration](#7-model-artifact-configuration)
8. [Inference Configuration](#8-inference-configuration)
9. [Adaptive Retraining Configuration](#9-adaptive-retraining-configuration)
10. [Operational Commands](#10-operational-commands)
11. [Monitoring Metrics](#11-monitoring-metrics)
12. [Configuration Summary](#12-configuration-summary)
13. [Result](#13-result)
14. [dcim-wiki Alignment](#14-dcim-wiki-alignment)
15. [Actual Code Location](#15-actual-code-location)

---

# 1. System Configuration Overview

Tujuan konfigurasi sistem ini adalah membangun pipeline anomaly detection berbasis machine learning yang terdiri dari:

1. Telemetry ingestion
2. Data preprocessing (Feature Pipeline)
3. Model training (Multi-Model Ensemble)
4. Model artifact packaging (Versioned)
5. Model Registry + Hot-Reload
6. Inference pipeline (AnomalyService + Z-score stream)
7. Adaptive retraining

Arsitektur pipeline:

```
Telemetry Collector
        ↓
PostgreSQL / TimescaleDB
        ↓
Dataset Preparation (FeaturePipeline)
        ↓
Multi-Model Training (IF + LOF + OCSVM)
        ↓
Versioned Artifact Packaging + Registry
        ↓
ModelManager (hot-reload)
        ↓
Inference Engine
  ├── AnomalyService (batch inference + drift + domain scoring)
  └── AnomalyDetectionProcessor (Z-score real-time → Kafka)
        ↓
server_anomalies / anomaly_events table
```

Arsitektur ini menjadi fondasi sistem anomaly detection yang kemudian berkembang menjadi AI monitoring platform lifecycle-aware [(MT-019) Anomaly Detection Framework](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep).

---

## 2. Infrastructure Configuration

### Operating System

```
Ubuntu 24.04 LTS
```

Digunakan sebagai host sistem ML dan database.

### Python Environment

Virtual environment:

```
ragavenv
```

Aktivasi environment:

```shellscript
source ragavenv/bin/activate
```

### Python Dependencies

Library yang digunakan (v1.0):

```
pandas
numpy
scikit-learn
sqlalchemy
psycopg2
joblib
```

**Library tambahan di v2:**

```
kafka-python       # Stream processor → Kafka publisher
psycopg2-binary    # Direct psycopg2 connector (stream processor)
```

Instalasi:

```shellscript
pip install pandas numpy scikit-learn sqlalchemy psycopg2-binary joblib kafka-python
```

---

# 3. Database Configuration

Database digunakan untuk menyimpan:

- Telemetry metrics
- Anomaly prediction
- Model registry

**Database:** PostgreSQL 16 + TimescaleDB

## Telemetry Table (v1.0)

**Table:** `server_metrics`

```sql
CREATE TABLE server_metrics (
    time TIMESTAMPTZ NOT NULL,
    hostname TEXT,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_io FLOAT,
    temperature FLOAT,
    gpu_util FLOAT,
    gpu_mem_used FLOAT,
    gpu_mem_total FLOAT,
    net_rx FLOAT,
    net_tx FLOAT
);
```

## Generic Metrics Table (v2.0 — implementasi aktual)

**Table:** `metrics` (TimescaleDB hypertable)

Sesuai dcim-wiki reference design §2.3:

```sql
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    ci_id UUID,
    asset_id UUID,
    source VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    tags JSONB DEFAULT '{}'
);

SELECT create_hypertable('metrics', 'time');
```

## Anomaly Output Table (v1.0)

**Table:** `server_anomalies`

```sql
CREATE TABLE server_anomalies (
    time TIMESTAMPTZ,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_io FLOAT,
    net_rx FLOAT,
    net_tx FLOAT,
    anomaly BOOLEAN
);
```

## Anomaly Events Table (v2.0 — implementasi aktual)

**Table:** `anomaly_events`

Sesuai dcim-wiki reference design §3.4 (Anomaly Alert Schema):

```sql
CREATE TABLE anomaly_events (
    anomaly_id UUID PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100),
    ci_id UUID,
    asset_id UUID,
    detection_method VARCHAR(50),
    current_value DOUBLE PRECISION,
    expected_min DOUBLE PRECISION,
    expected_max DOUBLE PRECISION,
    anomaly_score DOUBLE PRECISION,
    severity VARCHAR(20),
    description TEXT,
    possible_causes JSONB DEFAULT '[]',
    recommended_actions JSONB DEFAULT '[]'
);
```

## Model Registry Table (v2.0)

**Table:** `model_registry`

```sql
CREATE TABLE model_registry (
    id SERIAL PRIMARY KEY,
    model_name TEXT NOT NULL,
    version TEXT NOT NULL,
    contamination FLOAT,
    training_window TEXT,
    artifact_path TEXT NOT NULL,
    metrics_json JSONB,
    is_active BOOLEAN DEFAULT FALSE,
    -- v1.2.0 additions
    model_type TEXT,
    domain TEXT,
    inference_mode TEXT,
    data_contract_version TEXT
);
```

---

# 4. Dataset Preparation Configuration

Dataset preparation dilakukan untuk memastikan data siap digunakan oleh model machine learning.

## Tahapan v1.0

1. Drop NULL values
2. Remove non-feature columns
3. Variance filtering (< 1e-3)
4. Feature scaling (StandardScaler)
5. Train-test split (80/20)

## Tahapan v2.0 (implementasi aktual — FeaturePipeline)

1. Drop non-feature columns (`time`, `hostname`)
2. Drop NULL values (`dropna`)
3. Keep only numeric columns (`select_dtypes`)
4. Variance filtering (< 1e-3)
5. StandardScaler normalization (fit on train, transform on inference)
6. Save/load via `joblib`

Pipeline ini juga menjadi bagian dari feature pipeline dalam arsitektur anomaly detection framework [(MT-019) Anomaly Detection Framework](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep).

---

# 5. Training Script Configuration

## v1.0 Training Script

**File:** `notebooks/dataset_preparation.py`

```python
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
import numpy as np
import joblib
import os

engine = create_engine(
    "postgresql+psycopg2://infra:password@127.0.0.1/dcim_ai"
)

query = """
SELECT *
FROM server_metrics
WHERE time > NOW() - INTERVAL '30 minutes'
ORDER BY time ASC;
"""

df = pd.read_sql(query, engine)
df = df.dropna()
df = df.drop(columns=["time","hostname"])

variance = df.var()
low_variance_cols = variance[variance < 1e-3].index.tolist()
df_clean = df.drop(columns=low_variance_cols)

feature_columns = df_clean.columns.tolist()

scaler = StandardScaler()
X = scaler.fit_transform(df_clean)

X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)

model = IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)

model.fit(X_train)

joblib.dump(model, "models/isolation_forest_baseline.pkl")
joblib.dump(scaler, "models/scaler_baseline.pkl")
joblib.dump(feature_columns, "models/feature_columns.pkl")
```

## v2.0 Training Script (implementasi aktual)

**File:** `training/train_anomaly_model.py`

```python
import os
import json
import joblib
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from datetime import datetime, UTC
from dcim_ai.features.feature_pipeline import FeaturePipeline

# Config
WINDOW_INTERVAL = "30 days"
MODEL_VERSION_LEGACY = "v1.0_baseline"
DB_URL = "postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai"

ARTIFACTS_DIR = "dcim_ai/artifacts"
MODELS_DIR = os.path.join(ARTIFACTS_DIR, "models")
REGISTRY_DIR = "dcim_ai/registry"
REGISTRY_PATH = os.path.join(REGISTRY_DIR, "registry.json")

# Load data
engine = create_engine(DB_URL)
query = f"""
SELECT *
FROM server_metrics
WHERE time > NOW() - INTERVAL '{WINDOW_INTERVAL}'
ORDER BY time ASC;
"""
df = pd.read_sql(query, engine)

if len(df) < 100:
    raise Exception("Not enough data for baseline training.")

# Feature pipeline
pipeline = FeaturePipeline()
pipeline.fit(df)
X = pipeline.transform(df)

# Train multi-model
iso_model = IsolationForest(n_estimators=300, contamination=0.02, random_state=42)
lof_model = LocalOutlierFactor(n_neighbors=20, contamination=0.02, novelty=True)
svm_model = OneClassSVM(kernel="rbf", gamma="scale", nu=0.02)

iso_model.fit(X)
lof_model.fit(X)
svm_model.fit(X)

models = {
    "isolation_forest": iso_model,
    "local_outlier_factor": lof_model,
    "one_class_svm": svm_model
}

# Save versioned artifacts
# ... (version management, registry update)
```

**Perubahan kunci dari v1.0 → v2.0:**

| Aspek | v1.0 | v2.0 |
|-------|------|------|
| Model | Single Isolation Forest | Ensemble (IF + LOF + OCSVM) |
| n_estimators | 200 | 300 |
| contamination | 0.05 | 0.02 |
| Training window | 30 minutes | 30 days |
| Artifacts | 3 pkl files | Versioned directory + metadata.json |
| Feature pipeline | Inline code | FeaturePipeline class |
| Registry | None | registry.json + DB table |
| Voting | None | Majority ≥ 2/3 |

---

# 6. Model Configuration

## v1.0 — Single Model

**Model:** `Isolation Forest`

```python
IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)
```

**Penjelasan parameter:**

- **n_estimators** — Jumlah decision tree dalam model. Lebih banyak tree menghasilkan boundary anomaly yang lebih stabil.
- **contamination** — Estimasi persentase anomaly pada dataset. Digunakan untuk menentukan threshold anomaly.
- **random_state** — Seed untuk memastikan training reproducible.

## v2.0 — Multi-Model Ensemble (implementasi aktual)

| Model | Parameter | Nilai | Keterangan |
|-------|-----------|-------|------------|
| Isolation Forest | n_estimators | 300 | Jumlah decision trees (naik dari 200) |
| Isolation Forest | contamination | 0.02 | Estimasi anomaly ratio (turun dari 0.05) |
| Isolation Forest | random_state | 42 | Reproducibility |
| Local Outlier Factor | n_neighbors | 20 | Jumlah tetangga untuk density estimation |
| Local Outlier Factor | contamination | 0.02 | Estimasi anomaly ratio |
| Local Outlier Factor | novelty | True | Mode: predict on new data (bukan detect pada training data) |
| One-Class SVM | kernel | rbf | Radial basis function kernel |
| One-Class SVM | gamma | scale | Kernel coefficient |
| One-Class SVM | nu | 0.02 | Upper bound on fraction of training errors |

**Ensemble voting rule:** Prediksi = anomaly (-1) jika ≥ 2 dari 3 model vote -1.

---

# 7. Model Artifact Configuration

## v1.0 — Artifact Structure

```
models/
  isolation_forest_baseline.pkl
  scaler_baseline.pkl
  feature_columns.pkl
```

Fungsi masing-masing artifact:

| Artifact | Fungsi |
|----------|--------|
| model | anomaly detection |
| scaler | normalisasi fitur |
| feature_columns | memastikan inference konsisten |

## v2.0 — Versioned Artifact Structure (implementasi aktual)

```
dcim_ai/artifacts/
  models/
    v1.0/
      models.pkl                  # dict: {isolation_forest, local_outlier_factor, one_class_svm}
      pipeline.pkl                # FeaturePipeline instance (scaler + feature_columns)
      baseline_stats.json         # {"features": [...], "mean": [...], "std": [...]}
      metadata.json               # version, algorithm, params, training_samples, anomaly_ratio, status
    v1.1/
      ...
    v1.N/
      ...
  isolation_forest_v1.0_baseline.pkl    # legacy backward compat
  feature_pipeline_v1.0_baseline.pkl    # legacy backward compat
  feature_stats_v1.0_baseline.json      # legacy backward compat
```

**metadata.json structure:**

```json
{
    "version": "v1.0",
    "created_at": "2026-07-10T12:00:00+00:00",
    "algorithm": "Ensemble(IForest+LOF+OCSVM)",
    "models": {
        "isolation_forest": {"n_estimators": 300, "contamination": 0.02},
        "local_outlier_factor": {"n_neighbors": 20, "contamination": 0.02},
        "one_class_svm": {"kernel": "rbf", "nu": 0.02}
    },
    "training_samples": 12345,
    "training_anomaly_ratio": 0.02,
    "feature_columns": ["cpu_usage", "memory_usage", "disk_io", "net_rx", "net_tx"],
    "baseline_mean": [50.0, 60.0, 100.0, 500.0, 300.0],
    "baseline_std": [15.0, 10.0, 50.0, 200.0, 100.0],
    "status": "staging"
}
```

**registry.json structure:**

```json
{
    "current_production": "v1.0",
    "available_models": ["v1.0"],
    "correlation_config": {}
}
```

---

# 8. Inference Configuration

## v1.0 Inference

**File:** `src/anomaly_inference.py`

```python
import pandas as pd
import joblib
from sqlalchemy import create_engine

model = joblib.load("models/isolation_forest_baseline.pkl")
scaler = joblib.load("models/scaler_baseline.pkl")
feature_columns = joblib.load("models/feature_columns.pkl")

engine = create_engine("postgresql+psycopg2://infra:password@127.0.0.1/dcim_ai")

query = """
SELECT *
FROM server_metrics
WHERE time > NOW() - INTERVAL '30 minutes'
ORDER BY time ASC;
"""

df = pd.read_sql(query, engine)
original_df = df.copy()

df = df.drop(columns=["time","hostname"])
df = df.dropna()
df = df[feature_columns]

X = scaler.transform(df)
pred = model.predict(X)
anomaly_flags = pred == -1

original_df = original_df.loc[df.index]
original_df["anomaly"] = anomaly_flags

original_df[
    ["time","cpu_usage","memory_usage","disk_io","net_rx","net_tx","anomaly"]
].to_sql(
    "server_anomalies",
    engine,
    if_exists="append",
    index=False
)
```

## v2.0 AnomalyService Inference (implementasi aktual)

**File:** `services/anomaly_service.py`

```python
import joblib
import numpy as np
from dcim_ai.features.feature_pipeline import FeaturePipeline
from dcim_ai.features.drift_detector import DriftDetector
from dcim_ai.config.domain_mapping import DOMAIN_FEATURE_MAP
from dcim_ai.core.correlation_rules import evaluate_basic_rules
from dcim_ai.correlation.correlation_buffer import CorrelationBuffer


class AnomalyService:

    def __init__(self, model_path, pipeline_path, baseline_stats_path):
        self.models = joblib.load(model_path)
        self.pipeline = FeaturePipeline.load(pipeline_path)
        self.drift_detector = DriftDetector(baseline_stats_path)
        self.correlation_buffer = CorrelationBuffer(window_seconds=300)

    def predict(self, df_live):
        # 1. Data cleaning
        df_clean = self.pipeline._clean_dataframe(df_live)
        df_clean = df_clean[self.pipeline.feature_columns]
        X_raw = df_clean.values

        # 2. Drift detection (Z-score vs baseline)
        drift_result = self.drift_detector.check_drift(X_raw)
        z_scores = drift_result["z_scores"]
        drift_level = "stable"
        if drift_result["drift_detected"]:
            drift_level = "severe_drift" if max(z_scores) > 5.0 else "moderate_drift"

        # 3. Scaling
        X_scaled = self.pipeline.scaler.transform(X_raw)

        # 4. Multi-model voting
        iso_pred = self.models["isolation_forest"].predict(X_scaled)
        lof_pred = self.models["local_outlier_factor"].predict(X_scaled)
        svm_pred = self.models["one_class_svm"].predict(X_scaled)
        votes = (iso_pred == -1).astype(int) + (lof_pred == -1).astype(int) + (svm_pred == -1).astype(int)
        predictions = np.where(votes >= 2, -1, 1)

        # 5. Domain scoring
        feature_z_map = dict(zip(self.pipeline.feature_columns, z_scores))
        domain_scores = {}
        for domain, features in DOMAIN_FEATURE_MAP.items():
            scores = [abs(feature_z_map[f]) for f in features if f in feature_z_map]
            domain_scores[domain] = max(scores) if scores else 0.0

        # 6. Correlation rules
        correlation_result = evaluate_basic_rules(domain_scores, drift_level)
        self.correlation_buffer.add_snapshot(
            domain_scores=domain_scores,
            prediction=predictions[0],
            drift_level=drift_level
        )

        # 7. Return result
        return {
            "predictions": predictions.tolist(),
            "anomaly_ratio": float(np.mean(predictions == -1)),
            "drift_detected": drift_result["drift_detected"],
            "drift_level": drift_level,
            "drift_scores": z_scores,
            "domain_scores": domain_scores,
            "correlation": correlation_result
        }
```

## v2.0 Z-score Stream Processor (implementasi aktual)

**File:** `stream/anomaly_detector.py`

Sesuai dcim-wiki reference design §3.2:

```python
class AnomalyDetectionProcessor:
    def __init__(self, db_config=None, kafka_bootstrap_servers=None,
                 zscore_threshold=3.0, window_size=100, check_interval_seconds=30):
        # DB: TimescaleDB
        # Kafka: dcim.analytics.anomalies topic
        # Detection: Z-score method
        ...

    def calculate_zscore(self, values, current_value):
        arr = np.array(values)
        mean = np.mean(arr)
        std = np.std(arr)
        if std == 0:
            return 0.0
        return abs((current_value - mean) / std)

    def classify_severity(self, zscore):
        if zscore >= 5.0: return "critical"
        elif zscore >= 4.0: return "high"
        elif zscore >= 3.0: return "medium"
        else: return "low"
```

---

# 9. Adaptive Retraining Configuration

Untuk menangani data drift, sistem menggunakan rolling retraining.

Masalah drift dijelaskan dalam arsitektur anomaly framework [(MT-019) Anomaly Detection Framework](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep).

## v1.0 Retraining Script

**File:** `src/adaptive_retrain.py`

```python
import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest

engine = create_engine("postgresql+psycopg2://infra:password@127.0.0.1/dcim_ai")

query = """
SELECT *
FROM server_metrics
WHERE time > NOW() - INTERVAL '30 minutes'
ORDER BY time ASC;
"""

df = pd.read_sql(query, engine)
df = df.drop(columns=["time","hostname"])
df = df.dropna()

variance = df.var()
low_variance_cols = variance[variance < 1e-3].index.tolist()
df_clean = df.drop(columns=low_variance_cols)

scaler = StandardScaler()
X = scaler.fit_transform(df_clean)

model = IsolationForest(n_estimators=200, contamination=0.05, random_state=42)
model.fit(X)

joblib.dump(model, "models/isolation_forest_baseline.pkl")
joblib.dump(scaler, "models/scaler_baseline.pkl")
joblib.dump(df_clean.columns.tolist(), "models/feature_columns.pkl")
```

## v2.0 Retraining (implementasi aktual)

**Komponen:**

| Komponen | File | Fungsi |
|----------|------|--------|
| Training | `training/train_anomaly_model.py` | Multi-model training + versioned artifacts + registry update |
| Trigger | `automation/retrain_trigger.py` | `subprocess.Popen(["python", "-m", "dcim_ai.training.train_anomaly_model"])` |
| Orchestrator | `training/training_orchestrator.py` | Training orchestration |
| Scheduler | `services/retraining_scheduler.py` | Retraining scheduler |

**Mekanisme v2:**

1. Retrain trigger memanggil training script via subprocess
2. Training menghasilkan versioned artifacts di `dcim_ai/artifacts/models/vN.N/`
3. `registry.json` di-update dengan versi baru
4. `ModelManager` mendeteksi perubahan registry (watch setiap 10 detik)
5. Hot-reload: model baru langsung aktif tanpa restart service

---

# 10. Operational Commands

## Training

```shellscript
# v1.0
python notebooks/dataset_preparation.py

# v2.0
python -m dcim_ai.training.train_anomaly_model
```

## Inference

```shellscript
# v1.0
python src/anomaly_inference.py

# v2.0 — via API service
uvicorn dcim_ai.api.main:app --host 0.0.0.0 --port 8000
```

## Retraining

```shellscript
# v1.0
python src/adaptive_retrain.py

# v2.0
python -m dcim_ai.automation.retrain_trigger
```

## Stream Processor (Z-score real-time)

```shellscript
# v2.0 only
python -m dcim_ai.stream.anomaly_detector
```

## Model Promotion (v2.0)

```shellscript
# Promote model from staging to production
python -m dcim_ai.registry.promote_model
```

---

# 11. Monitoring Metrics

Monitoring yang disediakan sistem:

| Metric | v1.0 | v2.0 |
|--------|------|------|
| Anomaly ratio | ✅ | ✅ |
| Inference latency | ✅ | ✅ |
| Retraining count | ✅ | ✅ |
| Drift detection (Z-score) | ❌ | ✅ |
| Domain scores | ❌ | ✅ |
| Model version | ❌ | ✅ |
| Ensemble vote distribution | ❌ | ✅ |
| Severity classification | ❌ | ✅ |

Monitoring ini nantinya terintegrasi dengan observability metrics dan Prometheus monitoring dalam sistem AI platform [(MT-019) Anomaly Detection Framework](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep).

---

# 12. Configuration Summary

## v1.0

| Component | File |
|-----------|------|
| Dataset preparation | dataset_preparation.py |
| Model training | dataset_preparation.py |
| Inference engine | anomaly_inference.py |
| Adaptive retraining | adaptive_retraining.py |
| Database storage | PostgreSQL |
| Model artifact | model.*.pkl |

## v2.0 (implementasi aktual)

| Component | File | Lokasi |
|-----------|------|--------|
| Feature pipeline | FeaturePipeline | `features/feature_pipeline.py` |
| Model training | train_anomaly_model.py | `training/train_anomaly_model.py` |
| Anomaly service | AnomalyService | `services/anomaly_service.py` |
| Stream processor | AnomalyDetectionProcessor | `stream/anomaly_detector.py` |
| Model manager | ModelManager | `inference/model_manager.py` |
| Model registry | model_registry.py | `registry/model_registry.py` |
| Retrain trigger | retrain_trigger.py | `automation/retrain_trigger.py` |
| Drift detector | DriftDetector | `features/drift_detector.py` |
| Domain mapping | DOMAIN_FEATURE_MAP | `config/domain_mapping.py` |
| Correlation rules | evaluate_basic_rules | `core/correlation_rules.py` |
| Database storage | PostgreSQL 16 + TimescaleDB | — |
| Message broker | Kafka (dcim.analytics.anomalies) | — |
| Model artifacts | Versioned pkl + metadata.json | `dcim_ai/artifacts/models/vN.N/` |
| Registry state | registry.json | `dcim_ai/registry/registry.json` |

---

# 13. Result

Sistem anomaly detection berhasil:

- ✅ Mendeteksi spike CPU
- ✅ Mendeteksi drift
- ✅ Melakukan adaptive retraining
- ✅ Menyimpan hasil anomaly ke database
- ✅ Multi-model ensemble voting (v2.0)
- ✅ Model versioning + hot-reload (v2.0)
- ✅ Z-score real-time stream detection (v2.0)
- ✅ Domain scoring + correlation rules (v2.0)

Status implementasi:

```
Traditional ML Model Phase
COMPLETED (v2.0)
```

---

# 14. dcim-wiki Alignment

> Mapping konfigurasi MT-018 ke dcim-wiki reference design: `block7-analytics-ai-engine.md`.

## §3 Anomaly Detection — Configuration Alignment

| dcim-wiki Spec | Config Parameter | MT-018 Value | Status |
|---------------|-----------------|--------------|--------|
| §3.2 Z-score threshold | `zscore_threshold` | 3.0 | ✅ Aligned |
| §3.2 Z-score window | `window_size` | 100 | ✅ Aligned |
| §3.3 IF contamination | `contamination` | 0.02 (v2.0) / 0.05 (v1.0) | ✅ Aligned |
| §3.3 IF n_estimators | `n_estimators` | 300 (v2.0) / 200 (v1.0) | ✅ Aligned |
| §3.4 Anomaly alert schema | `anomaly_events` table | Full schema with severity, causes, actions | ✅ Aligned |
| §3.1 Moving Average | — | Not configured | ❌ Gap |
| §3.1 Seasonal Decomposition | — | Not configured | ❌ Gap |

## §8 Model Training Pipeline — Configuration Alignment

| dcim-wiki Spec | MT-018 Config | Status |
|---------------|---------------|--------|
| Data Collection | PostgreSQL → `server_metrics` / `metrics` table | ✅ |
| Feature Engineering | FeaturePipeline (clean + variance filter + scale) | ✅ |
| Training | Multi-model ensemble (IF + LOF + OCSVM) | ✅ Extended |
| Registry | Model Registry (versioned, multi-type, hot-reload) | ✅ Extended |

## §2 Time-Series Pipeline — Configuration Alignment

| dcim-wiki Spec | MT-018 Config | Status |
|---------------|---------------|--------|
| Kafka `dcim.analytics.anomalies` | Stream processor publishes anomalies | ✅ |
| TimescaleDB hypertable | `metrics` table with `create_hypertable` | ✅ |
| Grafana visualization | Not configured | ❌ Gap |
| Kafka consumer for metrics | `AnomalyDetectionProcessor` polls DB | ⚠️ Partial (DB polling, not Kafka consumer) |

**Alignment Score: 7/10** — Core anomaly detection configuration fully aligned with dcim-wiki. Extended beyond reference design with ensemble, versioning, hot-reload. Gaps: Moving Average, Seasonal Decomposition, Kafka metrics consumer, Grafana.

---

# 15. Actual Code Location

> File-file aktual yang mengimplementasikan konfigurasi MT-018 di `/home/infra/dcim_project/implementation/dcim_ai_v2_rag/`.

## Training & Feature Pipeline

| File | Deskripsi |
|------|-----------|
| `training/train_anomaly_model.py` | Script training multi-model ensemble + versioned artifacts |
| `features/feature_pipeline.py` | FeaturePipeline class: clean, variance filter, scale, transform, save/load |
| `features/feature_stats.py` | Feature statistics utilities |
| `features/drift_detector.py` | DriftDetector: Z-score per feature vs baseline stats |

## Inference & Service

| File | Deskripsi |
|------|-----------|
| `services/anomaly_service.py` | AnomalyService: predict, drift, domain scoring, correlation |
| `inference/model_manager.py` | ModelManager: hot-reload via registry.json watch |
| `inference/load_production_model.py` | Load production model from registry |
| `api/inference_service.py` | API inference service |
| `api/routers/anomalies.py` | Anomaly REST API endpoints |

## Stream Processing

| File | Deskripsi |
|------|-----------|
| `stream/anomaly_detector.py` | AnomalyDetectionProcessor: Z-score real-time + Kafka publisher |

## Registry & Lifecycle

| File | Deskripsi |
|------|-----------|
| `registry/model_registry.py` | Multi-model registry (legacy + v2 API) |
| `registry/promote_model.py` | Model promotion staging → production |
| `registry/sql/migrations/2026_05_20_v1_2_0_multi_model.sql` | DB migration multi-model |
| `models/model_manager.py` | Alternative model manager |

## Automation

| File | Deskripsi |
|------|-----------|
| `automation/retrain_trigger.py` | Trigger subprocess retraining |
| `training/training_orchestrator.py` | Training orchestration |
| `services/retraining_scheduler.py` | Retraining scheduler |

## Domain & Correlation

| File | Deskripsi |
|------|-----------|
| `config/domain_mapping.py` | DOMAIN_FEATURE_MAP |
| `core/correlation_rules.py` | Correlation rules evaluator |
| `correlation/correlation_buffer.py` | Temporal correlation buffer |

## Infrastructure

| File | Deskripsi |
|------|-----------|
| `k8s/deployment-anomaly-detector.yaml` | K8s deployment anomaly detector |
| `k8s/deployment-metrics-consumer.yaml` | K8s deployment metrics consumer |
| `k8s/configmap.yaml` | ConfigMap (DB, Kafka settings) |
| `docker-compose.yml` | Docker Compose configuration |
