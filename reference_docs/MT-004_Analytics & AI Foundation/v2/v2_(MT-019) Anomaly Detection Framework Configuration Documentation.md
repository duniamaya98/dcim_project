---
title: "MT-019 Anomaly Detection Framework Configuration Documentation"
created: 2026-05-20
updated: 2026-07-10
version: 2.0
type: configuration-doc
task_id: MT-019
block: 7
assignee: Fakhri Aulia R
status: done
dcim_wiki_section: "block7-analytics-ai-engine.md → Section 3: Anomaly Detection, Section 12: Monitoring & Alerting"
tags:
  - anomaly-detection
  - configuration
  - ensemble-learning
  - drift-detection
  - model-registry
  - fastapi
  - prometheus
  - feature-pipeline
  - hot-reload
  - analytics-ai-engine
---

# (MT-019) Anomaly Detection Framework Configuration Documentation v2.0

> **Dokumen ini merupakan v2 dari MT-019 Anomaly Detection Framework Configuration Document.**
> Seluruh konten asli dipertahankan, ditambah penambahan section dcim-wiki alignment, actual code mapping, dan penstrukturan ulang untuk clarity.

---

## Daftar Isi

1. [System Overview](#1-system-overview)
2. [System Architecture](#2-system-architecture)
3. [Project Directory Structure](#3-project-directory-structure)
4. [Model Artifact Structure](#4-model-artifact-structure)
5. [Model Registry Configuration](#5-model-registry-configuration)
6. [Feature Pipeline Configuration](#6-feature-pipeline-configuration)
7. [Drift Detection Configuration](#7-drift-detection-configuration)
8. [Multi-Model Ensemble Configuration](#8-multi-model-ensemble-configuration)
9. [Ensemble Voting Logic](#9-ensemble-voting-logic)
10. [Inference API Configuration](#10-inference-api-configuration)
11. [Automation Configuration](#11-automation-configuration)
12. [Monitor Configuration](#12-monitor-configuration)
13. [Model Manager (Hot Reload)](#13-model-manager-hot-reload)
14. [Resilience Features](#14-resilience-features)
15. [Final System Capabilities](#15-final-system-capabilities)
16. [dcim-wiki Alignment](#16-dcim-wiki-alignment)
17. [Actual Code Location](#17-actual-code-location)
18. [Configuration Gap Analysis](#18-configuration-gap-analysis)

---

## 1. System Overview

Berikut merupakan fase implementasi Anomaly Detection Framework pada sistem DCIM.

Framework ini menyediakan:

* Multi-model anomaly detection
* Drift detection
* Model version registry
* Real-time inference API
* Alert intelligence
* Automation & monitoring

Sistem ini menjadi fondasi untuk komponen lanjutan seperti:

* Model Lifecycle Engine (MT-021)
* Cross-Domain Correlation Engine (MT-020)
* Root Cause Analysis Engine (MT-022)

Arsitektur ini dirancang untuk production-ready AI monitoring system.

---

## 2. System Architecture

```
Telemetry Metrics
        ↓
Feature Pipeline
        ↓
Multi-Model Ensemble
        ↓
Drift Detection
        ↓
Inference API (FastAPI)
        ↓
Alert Layer
        ↓
Event Logging
        ↓
Automation & Retraining
```

Komponen utama:

1. Model Registry
2. Feature Engineering
3. Ensemble Detection
4. Real-Time Inference
5. Automation & Monitoring

---

## 3. Project Directory Structure

```
dcim_ai/
│
├── api/
│   └── inference_service.py
│
├── features/
│   ├── feature_pipeline.py
│   └── drift_detection.py
│
├── inference/
│   ├── load_production_model.py
│   └── model_manager.py
│
├── monitoring/
│   └── event_logger.py
│
├── training/
│   └── train_anomaly_model.py
│
├── registry/
│   └── registry.json
│
└── artifacts/
    └── models/
        ├── v1.0/
        ├── v1.1/
        ├── v1.2/
        ├── v1.3/
        └── v1.4/
```

---

## 4. Model Artifact Structure

Setiap model disimpan dalam folder versi.

`dcim_ai/artifact/models/v1.4/`

Isi artifact:

```
isolation_forest.pkl
lof.pkl
ocsvm.pkl
pipeline.pkl
baseline_stats.json
metadata.json
feature_columns.json
```

Metadata menyimpan konfigurasi training.

Contoh metadata:

```json
{
 "version": "v1.4",
 "algorithm": "Ensemble(IForest+LOF+OCSVM)",
 "training_samples": 19347,
 "training_anomaly_ratio": 0.0115,
 "feature_columns": [
   "cpu_usage",
   "memory_usage",
   "disk_io",
   "net_rx",
   "net_tx"
 ]
}
```

---

## 5. Model Registry Configuration

File:

`dcim_ai/registry/registry.json`

Contoh konfigurasi:

```json
{
 "current_production": "v1.4",
 "available_models": [
   "v1.0",
   "v1.1",
   "v1.2",
   "v1.3",
   "v1.4"
 ]
}
```

Fungsi registry:

* Menentukan model production
* Mendukung rollback
* Version tracking

Promote model:

```shellscript
python -m dcim_ai.registry.promote_model v1.4
```

---

## 6. Feature Pipeline Configuration

File:

`dcim_ai/features/feature_pipeline.py`

Pipeline bertanggung jawab untuk:

* cleaning
* feature selection
* scaling

Contoh implementasi:

```python
from sklearn.preprocessing import StandardScaler

class FeaturePipeline:

    def __init__(self, feature_columns):
        self.feature_columns = feature_columns
        self.scaler = StandardScaler()

    def fit(self, df):
        X = df[self.feature_columns]
        self.scaler.fit(X)

    def transform(self, df):
        X = df[self.feature_columns]
        return self.scaler.transform(X)
```

---

## 7. Drift Detection Configuration

File:

`dcim_ai/features/drift_detection.py`

Metode menggunakan Z-Score detection.

Formula:

```
z = (x - μ) / σ
```

Implementasi:

```python
import numpy as np

def calculate_drift_score(values, mean, std):

    z_scores = (values - mean) / std
    drift_score = float(np.mean(np.abs(z_scores)))

    return drift_score, z_scores
```

Klasifikasi drift:

| Drift Score Range | Status | Action |
|---|---|---|
| Z-score < 2.0 | stable | Normal operation |
| 2.0 ≤ Z-score < 3.5 | moderate_drift | Monitor closely |
| Z-score ≥ 3.5 | severe_drift | Trigger auto-retraining |

---

## 8. Multi-Model Ensemble Configuration

Framework menggunakan 3 model.

### Isolation Forest

```python
IsolationForest(
    n_estimators=300,
    contamination=0.02,
    random_state=42
)
```

### Local Outlier Factor

```python
LocalOutlierFactor(
    n_neighbors=20,
    contamination=0.02
)
```

### One-Class SVM

```python
OneClassSVM(
    kernel="rbf",
    nu=0.02
)
```

---

## 9. Ensemble Voting Logic

Voting strategy:

```
>=2 anomaly votes → anomaly
<2 anomaly votes → normal
```

Severity classification:

| Votes | Severity     |
| ----- | ------------ |
| 0     | normal       |
| 1     | weak\_signal |
| 2     | warning      |
| 3     | critical     |

Contoh implementasi:

```python
votes = [
  1 if iso_pred == -1 else 0,
  1 if lof_pred == -1 else 0,
  1 if svm_pred == -1 else 0
]

anomaly_votes = sum(votes)

if anomaly_votes >= 2:
    final_prediction = "anomaly"
else:
    final_prediction = "normal"
```

---

## 10. Inference API Configuration

File:

`dcim_ai/api/inference_service.py`

Framework menggunakan **FastAPI**.

Endpoint tersedia:

```
GET /
POST /predict
GET /metrics
```

Input schema:

```python
class MetricsInput(BaseModel):
    cpu_usage: float
    memory_usage: float
    disk_io: float
    net_rx: float
    net_tx: float
```

Contoh response:

```json
{
 "model_version": "v1.4",
 "prediction": "anomaly",
 "severity": "critical",
 "ensemble_score": -58.12,
 "drift_score": 329.37,
 "drift_status": "severe_drift"
}
```

---

## 11. Automation Configuration

Retraining otomatis terjadi ketika:

`drift_status == severe_drift`

Dengan cooldown:

`RETRAIN_COOLDOWN = 30`

Contoh implementasi:

```python
if drift_status == "severe_drift":
    threading.Thread(target=trigger_retraining).start()
```

---

## 12. Monitor Configuration

Prometheus metrics digunakan.

Metrics yang tersedia:

```
dcim_requests_total
dcim_anomalies_total
dcim_normals_total
dcim_inference_latency_seconds
```

Contoh konfigurasi:

```python
REQUEST_COUNT = Counter(
 "dcim_requests_total",
 "Total inference requests"
)
```

Endpoint metrics:

```
GET /metrics
```

---

## 13. Model Manager (Hot Reload)

File:

`dcim_ai/inference/model_manager.py`

Fungsi:

* memonitor registry.json
* reload model jika versi berubah
* thread-safe swap model

Contoh:

```python
class ModelManager:

    def get(self):
        return models, pipeline, baseline_stats, model_version
```

---

## 14. Resilience Features

Framework memiliki fitur production safety:

* alert cooldown
* retrain cooldown
* thread-safe model reload
* background retrain worker
* version rollback

Ini memastikan sistem tetap stabil saat running.

---

## 15. Final System Capabilities

MT-019 menghasilkan sistem dengan kemampuan:

* multi-model anomaly detection
* drift-aware monitoring
* real-time inference API
* automatic retraining
* production model registry
* monitoring via Prometheus
* hot model reload

Semua subsystem telah mencapai status production ready.

---

## 16. dcim-wiki Alignment

Bagian ini memetakan konfigurasi MT-019 ke dcim-wiki Block 7 reference design (`block7-analytics-ai-engine.md`).

### 16.1 Mapping ke Section 3: Anomaly Detection — Konfigurasi

| dcim-wiki Reference | MT-019 Config | Status |
|---|---|---|
| Z-score threshold: `3.0` | Z-score threshold: configurable via `calculate_drift_score()` | ✅ Aligned |
| IsolationForest: `contamination=0.01`, `n_estimators=100` | IsolationForest: `contamination=0.02`, `n_estimators=300` — parameter berbeda, tuning lebih agresif | ⚠️ Deviation |
| `ZScoreDetector` class dengan `window_size=100` | Drift detection per-feature, bukan windowed class — arsitektur berbeda | ⚠️ Deviation |
| Anomaly Alert Schema dengan `anomaly_id`, `possible_causes`, `recommended_actions` | Output schema ada tapi belum lengkap — `possible_causes` dan `recommended_actions` belum ter-automate | ⚠️ Partial |

### 16.2 Mapping ke Section 12: Monitoring & Alerting — Konfigurasi

| dcim-wiki Reference | MT-019 Config | Status |
|---|---|---|
| Metric: `analytics_anomalies_detected_total` (Counter) | Metric: `dcim_anomalies_total` (Counter) — fungsi sama, prefix berbeda | ⚠️ Naming Gap |
| Metric: `analytics_model_drift_score` (Gauge) | Metric: `dcim_drift_score{model_id, feature}` (Histogram) — tipe berbeda | ⚠️ Type Gap |
| Metric: `analytics_model_accuracy` (Gauge) | Belum dikonfigurasi | ❌ Gap |
| Alert: `AnalyticsAnomalyRateHigh` (`rate > 50/hour`) | Belum didefinisikan sebagai Prometheus alerting rule | ❌ Gap |
| Alert: `AnalyticsModelDrift` (`drift_score > 0.15, 7d`) | Drift threshold ada tapi bukan Prometheus alert rule format | ⚠️ Partial |
| Alert: `AnalyticsModelAccuracyLow` (`< 0.8, 7d`) | Belum ada model accuracy tracking | ❌ Gap |

### 16.3 Konfigurasi Parameter Comparison

| Parameter | dcim-wiki Spec | MT-019 Config | Catatan |
|---|---|---|---|
| IF n_estimators | 100 | 300 | MT-019 lebih robust |
| IF contamination | 0.01 | 0.02 | MT-019 lebih toleran |
| IF random_state | 42 | 42 | ✅ Match |
| OCSVM kernel | rbf | rbf | ✅ Match |
| OCSVM nu | 0.02 | 0.02 | ✅ Match |
| LOF contamination | - | 0.02 | dcim-wiki tidak spesifikasi LOF |
| Z-score threshold | 3.0 | configurable | Lebih fleksibel |
| Voting threshold | - | ≥ 2 / 3 models | Ensemble-specific |

---

## 17. Actual Code Location

Berikut mapping aktual file Python pada implementasi v2 di `/home/infra/dcim_project/implementation/dcim_ai_v2_rag/`:

### 17.1 Core Services

| File Path | Deskripsi | Relates to Config Section |
|---|---|---|
| `services/anomaly_service.py` | Multi-model voting ensemble (IF + LOF + OCSVM). Implementasi training, prediction, severity classification | §8 (Multi-Model Ensemble), §9 (Voting Logic) |

### 17.2 Feature Engineering

| File Path | Deskripsi | Relates to Config Section |
|---|---|---|
| `features/feature_pipeline.py` | Feature pipeline — cleaning, selection, StandardScaler scaling | §6 (Feature Pipeline) |
| `features/drift_detection.py` | Z-score drift detection, aggregate drift score, classification | §7 (Drift Detection) |
| `features/drift_detector.py` | Extended drift detector — PSI, KS test untuk long-window analysis | §7 (Drift Detection) — extended |

### 17.3 Streaming & Real-Time

| File Path | Deskripsi | Relates to Config Section |
|---|---|---|
| `stream/anomaly_detector.py` | Real-time anomaly detection untuk streaming pipeline | §10 (Inference API) — streaming mode |

### 17.4 API Layer

| File Path | Deskripsi | Relates to Config Section |
|---|---|---|
| `api/routers/anomalies.py` | FastAPI router — /predict, anomaly history, drift status endpoints | §10 (Inference API) |

### 17.5 Model Registry

| File Path | Deskripsi | Relates to Config Section |
|---|---|---|
| `registry/model_registry.py` | Versioned model registry — storage, promotion, rollback, multi-type tracking | §5 (Model Registry) |

### 17.6 Monitoring & Drift

| File Path | Deskripsi | Relates to Config Section |
|---|---|---|
| `monitoring/drift_detector.py` | Runtime drift watcher — periodic calculation, Prometheus export, retrain trigger | §12 (Monitor), §13 (Model Manager) |

### 17.7 Training & Deployment

| File Path | Deskripsi | Relates to Config Section |
|---|---|---|
| `training/train_anomaly_model.py` | Training pipeline untuk ensemble model | §4 (Model Artifact) |
| `k8s/deployment-anomaly-detector.yaml` | Kubernetes deployment manifest | Infrastructure |

---

## 18. Configuration Gap Analysis

### Overall Alignment Score: ~70%

### Gap Summary

| # | Gap | Impact | Recommendation |
|---|---|---|---|
| 1 | Prometheus metric naming (`dcim_*` vs `analytics_*`) | Dashboard & alert compatibility | Create metric alias atau rename ke `analytics_*` prefix |
| 2 | Model accuracy gauge metric belum ada | Tidak bisa monitor model degradation | Tambahkan `dcim_model_accuracy` Gauge metric |
| 3 | Prometheus alerting rules YAML belum didefinisikan | Tidak ada automated alerting | Buat alert rules file sesuai dcim-wiki Section 12.2 |
| 4 | LOF configuration tidak ada di dcim-wiki spec | Tidak terdokumentasi di reference design | Tambahkan LOF spec ke dcim-wiki atau dokumentasikan sebagai enhancement |
| 5 | IF parameter deviation (n_estimators, contamination) | Potensi behavior difference | Document rationale untuk parameter tuning |
| 6 | `possible_causes` / `recommended_actions` belum ter-automate | Alert kurang actionable | Integrasikan dengan RCA engine (MT-022) |
| 7 | Feature drift heatmap belum ada | Observability gap untuk drift visualization | Implementasi pada monitoring dashboard |

### Recommendations for v2.1

1. **Metric Alignment** — Rename Prometheus metrics ke `analytics_*` prefix untuk kompatibilitas dengan dcim-wiki Grafana dashboard
2. **Model Accuracy Tracker** — Implementasi background accuracy calculation metric
3. **Alert Rules File** — Buat `prometheus/alerts/analytics-ai.yml` sesuai dcim-wiki spec
4. **Parameter Documentation** — Document rationale untuk IF parameter deviation (300 estimators vs 100, 0.02 contamination vs 0.01)

---

> **Catatan:** Dokumen ini merupakan v2 restructured dari MT-019 Anomaly Detection Framework Configuration Document original. Seluruh konten asli (§1–§15) dipertahankan tanpa perubahan. Section 16–18 merupakan penambahan baru untuk alignment tracking.
