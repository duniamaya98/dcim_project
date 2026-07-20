---
title: "(MT-018) Traditional Machine Learning Model"
created: 2026-02-13
updated: 2026-07-10
version: 2.0
type: documentation
task_id: MT-018
block: 7
assignee: Fakhri Aulia R
status: done
dcim_wiki_section: block7-analytics-ai-engine → §3 Anomaly Detection
tags:
  - machine-learning
  - anomaly-detection
  - isolation-forest
  - ensemble
  - lof
  - ocsvm
  - z-score
  - drift-detection
  - adaptive-retrain
  - timescaledb
  - scikit-learn
  - feature-pipeline
  - model-registry
---

# (MT-018) Traditional Machine Learning Model

> **Version:** 2.0 — restructured, aligned with dcim-wiki reference design, updated berdasarkan implementasi aktual di `dcim_ai_v2_rag`.

---

## Daftar Isi

1. [Overview](#1-overview)
2. [System Architecture](#2-system-architecture)
3. [ML Environment Setup](#3-ml-environment-setup)
4. [Dataset Preparation](#4-dataset-preparation)
5. [Baseline Model Development](#5-baseline-model-development)
6. [Model Benchmarking](#6-model-benchmarking)
7. [Model Packaging](#7-model-packaging)
8. [Adaptive Model Lifecycle Management](#8-adaptive-model-lifecycle-management)
9. [System Status](#9-system-status)
10. [Phase Completion Summary](#10-phase-completion-summary)
11. [Addendum v1.2.0 — Penyesuaian Use Case](#11-addendum-v120--penyesuaian-use-case)
12. [dcim-wiki Alignment](#12-dcim-wiki-alignment)
13. [Actual Code Location](#13-actual-code-location)

---

# 1. Overview

## Objective

Membangun sistem anomaly detection berbasis Traditional Machine Learning untuk:

- Monitoring server metrics real-time
- Mendeteksi abnormal behavior
- Menyimpan hasil anomaly ke database
- Menyediakan fondasi AI DCIM adaptif

---

# 2. System Architecture

## Arsitektur Awal (v1.0)

```
Telemetry Collector
        ↓
PostgreSQL + TimescaleDB
        ↓
Dataset Preparation
        ↓
Baseline Model Training (Isolation Forest)
        ↓
Model Artifacts (pkl bundle)
        ↓
Inference Engine
        ↓
server_anomalies table
```

## Arsitektur Terkini (v2.0 — implementasi aktual)

```
TimescaleDB (metrics table)
        ↓
FeaturePipeline (clean → variance filter → scale)
        ↓
Multi-Model Ensemble Training
  ├── Isolation Forest (n_estimators=300)
  ├── Local Outlier Factor (n_neighbors=20, novelty=True)
  └── One-Class SVM (kernel=rbf, nu=0.02)
        ↓
Model Registry (versioned artifacts + metadata.json)
        ↓
ModelManager (hot-reload via registry.json watch)
        ↓
AnomalyService
  ├── Drift Detection (Z-score vs baseline stats)
  ├── Multi-model Voting (majority ≥ 2/3)
  ├── Domain Scoring (per-domain z-score mapping)
  └── Correlation Rules + Temporal Buffer
        ↓
API / Stream Processor
  ├── Z-score real-time detection → Kafka (dcim.analytics.anomalies)
  └── REST API inference endpoint
```

---

# 3. ML Environment Setup

## Infrastructure

- **OS:** Ubuntu 24.04 LTS
- **Python venv:** ragavenv
- **Database:** PostgreSQL 16 + TimescaleDB
- **GPU:** 2x RTX 3070 TI (not used for baseline ML)

## Python Dependencies

```
pandas
numpy
scikit-learn
sqlalchemy
psycopg2
joblib
```

**Dependencies tambahan di v2 (stream processor):**

```
kafka-python
psycopg2-binary
```

---

# 4. Dataset Preparation

## Data Source

**Table:** `server_metrics`

**Columns:**

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| time | TIMESTAMPTZ | Timestamp data |
| hostname | TEXT | Identifier server |
| cpu_usage | FLOAT | Persentase utilisasi CPU (%) |
| memory_usage | FLOAT | Persentase penggunaan RAM (%) |
| disk_io | FLOAT | Aktivitas read/write disk |
| temperature | FLOAT | Suhu server |
| gpu_util | FLOAT | GPU utilization (%) |
| gpu_mem_used | FLOAT | GPU memory used |
| gpu_mem_total | FLOAT | GPU memory total |
| net_rx | FLOAT | Network receive throughput (MB) |
| net_tx | FLOAT | Network transmit throughput (MB) |

## Cleaning Pipeline

Tahapan (diimplementasikan di `FeaturePipeline`):

1. Drop non-feature columns (`time`, `hostname`)
2. Drop NULL values
3. Keep only numeric columns
4. Variance analysis — remove low-variance features (`< 1e-3`)
5. StandardScaler normalization
6. Train-test split (80/20)

## Feature Selection Result

**Initial feature set (v1.0):**

```
['cpu_usage', 'memory_usage', 'disk_io', 'net_rx', 'net_tx']
```

**Adaptive retrain feature set:**

```
['cpu_usage', 'memory_usage', 'net_rx', 'net_tx']
```

## Penjelasan Feature

- **cpu_usage (%)** — Persentase utilisasi CPU. Indikator beban komputasi server. Spike mendadak → indikasi runaway process / overload. Variance tinggi → kandidat utama anomaly detection.
- **memory_usage (%)** — Persentase penggunaan RAM. Drift baseline sering terjadi akibat perubahan workload. Penting untuk mendeteksi memory leak.
- **disk_io (bytes/sec atau cumulative IO)** — Aktivitas read/write disk. Burst tinggi → backup, indexing, database write storm. Variance rendah → di-drop oleh variance filter.
- **net_rx (MB)** — Network receive throughput. Mendeteksi traffic spike. Digunakan untuk mendeteksi DDoS / traffic anomaly.
- **net_tx (MB)** — Network transmit throughput. Indikator outgoing burst (backup sync, upload, replication).

---

# 5. Baseline Model Development

## v1.0 — Single Model

**Algorithm:** Isolation Forest

**Parameters:**

```python
IsolationForest(
    n_estimators=200,
    contamination=0.05,
    random_state=42
)
```

**Penjelasan parameter:**

- **n_estimators (200)** — Jumlah decision tree. Lebih banyak tree → boundary lebih stabil. Tradeoff: waktu training vs robustness.
- **contamination (0.05)** — Perkiraan proporsi anomaly. Mengatur threshold decision. Tidak memaksa output 5%, hanya mengatur cut-off saat training.
- **random_state (42)** — Reproducibility. Menjamin hasil konsisten saat retraining.

## v2.0 — Multi-Model Ensemble (implementasi aktual)

**Algoritma:** Ensemble majority voting dari 3 model:

| Model | Parameter Kunci | Keterangan |
|-------|----------------|------------|
| Isolation Forest | n_estimators=300, contamination=0.02 | Multivariate anomaly detection |
| Local Outlier Factor | n_neighbors=20, novelty=True, contamination=0.02 | Density-based anomaly detection |
| One-Class SVM | kernel=rbf, gamma=scale, nu=0.02 | Boundary-based anomaly detection |

**Voting rule:** Prediksi = anomaly jika ≥ 2 dari 3 model vote -1.

## Validation

✔ CPU Spike Injection Test — Manual spike → anomaly detected
✔ Training Anomaly Ratio — ≈ 2-5% (as configured)

---

# 6. Model Benchmarking

| Contamination | Train Time | Inference Time | Test Ratio |
|--------------|------------|----------------|------------|
| 0.01 | ~0.13s | ~0.008s | ~1% |
| 0.05 | ~0.13s | ~0.008s | ~5% |
| 0.10 | ~0.13s | ~0.008s | ~13% |

- **Inference latency:** < 10ms → cocok untuk real-time DCIM monitoring
- **Train Time (~0.13s)** — Mengukur computational overhead. Indikator kelayakan retraining frequent.
- **Inference Time (~0.008s)** — Latency per batch. <10ms → cocok real-time monitoring.

---

# 7. Model Packaging

## Artifact Structure (v1.0)

```
models/
  isolation_forest_baseline.pkl
  scaler_baseline.pkl
  feature_columns.pkl
```

## Artifact Structure (v2.0 — implementasi aktual)

```
dcim_ai/artifacts/
  models/
    v1.0/
      models.pkl              # dict: {isolation_forest, local_outlier_factor, one_class_svm}
      pipeline.pkl            # FeaturePipeline instance
      baseline_stats.json     # mean, std per feature
      metadata.json           # version, algorithm, training_anomaly_ratio, status
    v1.1/
      ...
  isolation_forest_v1.0_baseline.pkl    # legacy backward compat
  feature_pipeline_v1.0_baseline.pkl    # legacy backward compat
  feature_stats_v1.0_baseline.json      # legacy backward compat

dcim_ai/registry/
  registry.json               # current_production, available_models, correlation_config
```

## Inference Pipeline (v2.0)

**File:** `services/anomaly_service.py`

**Flow:**

1. Load models (multi-model dict), pipeline, baseline stats
2. Data cleaning via `FeaturePipeline._clean_dataframe()`
3. Drift detection (Z-score vs baseline stats)
4. Scaling via fitted scaler
5. Multi-model voting (majority ≥ 2/3)
6. Domain scoring (per-domain z-score mapping)
7. Correlation rules + temporal buffer aggregation
8. Return structured result dict

## Output Tables

**`server_anomalies`** (v1.0):

| Kolom | Tipe |
|-------|------|
| time | TIMESTAMPTZ |
| cpu_usage | FLOAT |
| memory_usage | FLOAT |
| disk_io | FLOAT |
| net_rx | FLOAT |
| net_tx | FLOAT |
| anomaly | BOOLEAN |

**`anomaly_events`** (v2.0 — implementasi aktual):

| Kolom | Tipe |
|-------|------|
| anomaly_id | UUID |
| timestamp | TIMESTAMPTZ |
| metric_name | VARCHAR |
| ci_id | UUID |
| asset_id | UUID |
| detection_method | VARCHAR |
| current_value | DOUBLE |
| expected_min | DOUBLE |
| expected_max | DOUBLE |
| anomaly_score | DOUBLE |
| severity | VARCHAR |
| description | TEXT |
| possible_causes | JSONB |
| recommended_actions | JSONB |

---

# 8. Adaptive Model Lifecycle Management

## Problem Encountered

Data drift:
- Memory baseline: 23% → 16%
- Anomaly ratio: 5% → 45%

## Solution Implemented (v1.0)

Rolling retraining (30-minute window) via `src/adaptive_retrain.py`:
- Fetch last 30 minutes
- Full retrain
- Overwrite artifact
- Maintain contamination=0.05

## Solution Implemented (v2.0 — implementasi aktual)

**Komponen:**

| Komponen | File | Fungsi |
|----------|------|--------|
| Training script | `training/train_anomaly_model.py` | Multi-model training + versioned artifact saving |
| Retrain trigger | `automation/retrain_trigger.py` | Trigger subprocess retraining |
| Model Manager | `inference/model_manager.py` | Hot-reload model via registry.json file watch |
| Model Registry | `registry/model_registry.py` | Multi-model registry (v1 + v2 API) |
| Drift Detector | `features/drift_detector.py` | Z-score drift detection vs baseline stats |

**Mekanisme v2:**

1. Training menghasilkan versioned artifacts (`v1.0`, `v1.1`, ...) + metadata.json
2. `registry.json` di-update dengan `current_production` dan `available_models`
3. `ModelManager` watch `registry.json` setiap 10 detik
4. Jika versi berubah → hot-reload model, pipeline, baseline stats
5. Drift detector membandingkan data live vs baseline stats → Z-score per feature
6. Domain scoring memetakan drift ke domain (compute, network, dll.)

## Key Insights Learned

- Static models fail in dynamic environments
- Isolation Forest sensitive to low variance
- Snapshot-based detection unstable for highly stable servers
- Distribution shift drastically impacts threshold
- **Ensemble voting (2/3 majority) mengurangi false positive vs single model**

---

# 9. System Status

## Completed (v1.0)

- ✅ Environment Setup
- ✅ Dataset Preparation
- ✅ Baseline Model Development
- ✅ Model Benchmarking
- ✅ Model Packaging
- ✅ Adaptive Retraining

## Completed (v2.0 additions)

- ✅ Multi-model ensemble (IF + LOF + OCSVM)
- ✅ Model versioning + registry
- ✅ Hot-reload model manager
- ✅ Drift detection (Z-score based)
- ✅ Domain scoring
- ✅ Correlation rules engine
- ✅ Stream processor (Z-score real-time → Kafka)
- ✅ FeaturePipeline abstraction

## Limitations

- Snapshot detection too sensitive
- No trend-based detection
- No drift scoring metric (aggregate)
- No rollback mechanism
- No supervised failure labeling
- No forecasting (Prophet/LSTM)

---

# 10. Phase Completion Summary

**Traditional ML Phase Status:**

- ✅ Functional
- ✅ Drift-aware (basic)
- ✅ Production-testable
- ✅ Multi-model ensemble
- ✅ Model versioning
- ⚠️ Needs intelligence upgrade (forecasting, supervised labeling)

## Changelog

| Date | Versi | Author | Note |
|------|-------|--------|------|
| 13/02/2026 | 1.0 | Fakhri | Initial documentation |
| 02/03/2026 | 1.1.2 | Fakhri | Perubahan tambahan penjelasan metrics |
| 20/05/2026 | 1.2.0 | DCIM AI Team | Addendum v1.2.0 — koreksi untuk UC1/UC2/UC3 |
| 10/07/2026 | 2.0 | DCIM AI Team | Restructured, dcim-wiki alignment, updated ke implementasi aktual |

---

# 11. Addendum v1.2.0 — Penyesuaian Use Case

> **Tanggal:** 20 Mei 2026
> **Tujuan:** Menyelaraskan MT-018 dengan kebutuhan tiga use case Analytics & AI Engine (Predictive Failure Alerting, Capacity Optimization, Energy/PUE Drift).
> **Sifat:** Addendum non-destruktif — isi bagian 1–10 di atas tetap dipertahankan sebagai rekam jejak.

## 11.1 Ringkasan Gap

| Area | Kondisi Saat Ini (Bagian 1–10) | Kebutuhan UC | Status |
| --- | --- | --- | --- |
| Feature scope | `cpu_usage, memory_usage, disk_io, net_rx, net_tx` | UC1 perlu `temperature, smart_*, fan_speed`; UC3 perlu `power_w, voltage, pue`, `temp_inlet/outlet`, `humidity` | ⚠️ Diperluas |
| Data source | Hardcoded ke `server_metrics` | UC2/UC3 butuh sumber tambahan (NetBox, PDU, environment) | ⚠️ Generalisasi |
| Algoritma | Hanya anomaly classification (IF/LOF/OCSVM) | UC1 butuh time-series forecasting | ❌ Tambah |
| Labeling | Unsupervised only | UC1 butuh supervised failure labels | ❌ Tambah |
| Data quality | `dropna` saja | UC3 sensor noisy → butuh imputation & outlier filtering | ❌ Tambah |

## 11.2 Perluasan Feature Scope

Tambahkan **feature group** terpisah agar tidak mencampur metrik server dengan metrik energi/lingkungan.

| Group | Domain | Fitur | Sumber |
| --- | --- | --- | --- |
| `server_compute` | compute, memory, network | `cpu_usage, memory_usage, disk_io, net_rx, net_tx, gpu_util, gpu_mem_used, temperature` | `server_metrics` (existing) |
| `server_health` (baru) | storage, hardware | `smart_reallocated_sectors, smart_temp, smart_pending_sectors, fan_speed, hwmon_temp` | SNMP/IPMI/Redfish (UC1) |
| `power_metrics` (baru) | power | `power_w, voltage, current, energy_kwh, pue` | PDU/UPS (UC3) |
| `environment_metrics` (baru) | cooling | `temp_inlet, temp_outlet, humidity, dewpoint` | Sensor lingkungan (UC3) |
| `capacity_metrics` (baru) | compute, storage, network | rolling 7d/30d/90d aggregates dari `server_compute` + rack occupancy dari NetBox | Aggregate + NetBox (UC2) |

> **Catatan:** Variance filter `<1e-3` yang sebelumnya men-drop `disk_io` perlu **dievaluasi ulang per-group**. Pada konteks energy, deviasi kecil tetap signifikan.

## 11.3 Generalisasi Data Source

Pipeline `dataset_preparation` saat ini terikat ke `server_metrics`. Refactor menjadi **abstract loader** dengan kontrak minimal:

```python
class MetricSource:
    domain: str             # 'server' | 'power' | 'environment'
    table: str
    feature_columns: list[str]
    timestamp_column: str = 'time'
    asset_id_column: str = 'hostname'  # atau 'device_id'
    def load(window: TimeWindow) -> pd.DataFrame: ...
```

Implementasi konkret per UC:

- `ServerMetricsSource` (existing, untuk UC1/UC2)
- `PowerMetricsSource` (baru, untuk UC3 — query tabel TimescaleDB `power_metrics`)
- `EnvironmentMetricsSource` (baru, untuk UC3)
- `NetBoxAssetSource` (baru, untuk UC2 — read-only NetBox API)

## 11.4 Forecasting Profile (Baru)

UC1 mensyaratkan deteksi **24–48 jam sebelum kegagalan**. Anomaly detection saja tidak cukup.

| Layer | Algoritma | Output | Use For |
| --- | --- | --- | --- |
| Baseline forecast | Prophet / XGBoost regression dengan lag features (1h, 6h, 24h) | `forecast_value`, `forecast_ci_low`, `forecast_ci_high` per metrik | UC1 quick-win |
| Advanced forecast | LSTM / Temporal Fusion Transformer | `failure_probability_24h`, `failure_probability_48h` | UC1 production |

**Integrasi:** output forecast disuntikkan sebagai *forecasted feature* ke ensemble anomaly existing. Anomaly pada `forecast_value` = early warning.

## 11.5 Supervised Labeling untuk Failure Events

Tambahkan tabel `failure_events` dengan kontrak:

```sql
failure_events (
  event_id UUID PK,
  asset_id TEXT,
  event_time TIMESTAMPTZ,
  failure_type TEXT,    -- 'disk', 'fan', 'thermal', 'memory', 'power'
  severity TEXT,        -- 'minor', 'major', 'critical'
  source TEXT,          -- 'manual', 'incident_ticket', 'sensor_threshold'
  evidence JSONB
)
```

Digunakan untuk:
- Training supervised model (Gradient Boosting / Random Forest) dengan window features sebelum event.
- Backtesting forecast model terhadap failure history.

## 11.6 Imputation & Noise Handling

Pipa cleaning sekarang hanya `dropna`. Tambahkan strategi per-feature:

| Strategi | Cocok Untuk | Catatan |
| --- | --- | --- |
| Forward-fill (max gap 5 menit) | Streaming sensor (PDU, environment) | Hindari gap-fill pada gap besar |
| Linear interpolation | Metrik kontinu (suhu, voltage) | Tandai sebagai imputed di kolom `_imputed_flag` |
| Median per-window | Outlier filtering pada SMART data | Lebih robust dari mean |
| Drop | Schema invalid / corrupt rows | Logged ke `data_quality_log` |

## 11.7 Backward Compatibility

Semua perubahan di addendum ini **opt-in**:
- Pipeline existing `server_metrics → IF/LOF/OCSVM` tetap berjalan tanpa perubahan.
- Feature group baru dipanggil hanya bila profil `forecast`, `energy`, atau `capacity` di-aktifkan via konfigurasi training.
- Schema `failure_events` & sumber data baru bersifat **additive**.

## 11.8 Mapping ke Use Case

| UC | Bagian Addendum yang Dipakai |
| --- | --- |
| UC1 | 11.2 (`server_health`), 11.4 (forecasting), 11.5 (labeling), 11.6 (imputation SMART) |
| UC2 | 11.2 (`capacity_metrics`), 11.3 (`NetBoxAssetSource`) |
| UC3 | 11.2 (`power_metrics`, `environment_metrics`), 11.3 (`PowerMetricsSource`, `EnvironmentMetricsSource`), 11.6 (imputation sensor) |

---

# 12. dcim-wiki Alignment

> Mapping fitur MT-018 ke dcim-wiki reference design: `block7-analytics-ai-engine.md`, Section 3: Anomaly Detection.

## Alignment Summary

| dcim-wiki §3 Reference | MT-018 Status | Keterangan |
|------------------------|---------------|------------|
| **§3.1 Detection Methods — Z-score** | ✅ Implemented | `stream/anomaly_detector.py` — Z-score real-time detection dengan severity classification |
| **§3.1 Detection Methods — Isolation Forest** | ✅ Implemented | `training/train_anomaly_model.py` — IF sebagai salah satu dari 3-model ensemble |
| **§3.1 Detection Methods — Moving Average** | ❌ Not implemented | Slow drift detection belum ada |
| **§3.1 Detection Methods — Seasonal Decomposition** | ❌ Not implemented | Daily/weekly pattern detection belum ada |
| **§3.2 Z-score Implementation** | ✅ Implemented | `AnomalyDetectionProcessor.calculate_zscore()` — sesuai spec (window=100, threshold=3.0) |
| **§3.3 Isolation Forest Implementation** | ✅ Implemented + Extended | Multi-model ensemble (IF + LOF + OCSVM) dengan majority voting |
| **§3.4 Anomaly Alert Schema** | ✅ Implemented | `anomaly_events` table + Kafka `dcim.analytics.anomalies` topic — schema sesuai reference |
| **Anomaly latency < 500ms** | ✅ Met | Inference < 10ms per batch |
| **Severity classification** | ✅ Implemented | `classify_severity()`: critical ≥5.0, high ≥4.0, medium ≥3.0, low <3.0 |

## Fitur yang Melampaui Reference Design

| Fitur | dcim-wiki Spec | MT-018 Implementasi |
|-------|---------------|---------------------|
| Ensemble voting | Tidak ada (single IF) | 3-model majority voting (≥ 2/3) |
| Model versioning | Tidak ada | Versioned artifacts + registry.json |
| Hot-reload | Tidak ada | ModelManager watch registry.json setiap 10 detik |
| Drift detection | Disebut di §4 (Predictive) | Z-score vs baseline stats per feature |
| Domain scoring | Tidak ada | Per-domain z-score mapping (compute, network, dll.) |
| Correlation rules | Tidak ada (di §5 RCA) | Basic correlation rules + temporal buffer |
| Multi-model registry | Tidak ada | Model registry v2 API (type, domain, inference_mode) |

## Gap yang Perlu Diisi

| Gap | Referensi | Prioritas |
|-----|-----------|-----------|
| Moving Average detection | §3.1 | Medium |
| Seasonal Decomposition | §3.1 | Low |
| Failure probability scoring | §4 | High (UC1) |
| RCA integration | §5 | Medium |
| Capacity forecasting | §6 | Medium |
| Energy/PUE optimization | §7 | Medium |

**Alignment Score: 7/10** — Core anomaly detection (Z-score, Isolation Forest, Alert Schema) fully aligned. Extended dengan ensemble, versioning, drift detection. Gap pada moving average, seasonal decomposition, dan predictive maintenance integration.

---

# 13. Actual Code Location

> File-file Python aktual yang mengimplementasikan modul MT-018 di `/home/infra/dcim_project/implementation/dcim_ai_v2_rag/`.

## Core Training & Inference

| File | Fungsi |
|------|--------|
| `training/train_anomaly_model.py` | Multi-model training (IF + LOF + OCSVM), versioned artifact saving, registry update |
| `services/anomaly_service.py` | AnomalyService — predict, drift detection, domain scoring, correlation rules |
| `inference/model_manager.py` | ModelManager — hot-reload model via registry.json watch |
| `inference/load_production_model.py` | Load production model from registry |
| `api/inference_service.py` | API inference service |

## Feature Pipeline

| File | Fungsi |
|------|--------|
| `features/feature_pipeline.py` | FeaturePipeline — clean, variance filter, scale, transform |
| `features/feature_stats.py` | Feature statistics utilities |
| `core/feature_pipeline.py` | Core feature pipeline (alternative path) |

## Stream Processing (Z-score real-time)

| File | Fungsi |
|------|--------|
| `stream/anomaly_detector.py` | AnomalyDetectionProcessor — Z-score real-time, severity classification, Kafka publisher |
| `api/routers/anomalies.py` | Anomaly API endpoints |

## Model Registry & Lifecycle

| File | Fungsi |
|------|--------|
| `registry/model_registry.py` | Multi-model registry (legacy + v2 API) |
| `registry/promote_model.py` | Model promotion (staging → production) |
| `registry/sql/migrations/2026_05_20_v1_2_0_multi_model.sql` | DB migration untuk multi-model registry |
| `models/model_manager.py` | Alternative model manager |

## Automation & Scheduling

| File | Fungsi |
|------|--------|
| `automation/retrain_trigger.py` | Trigger subprocess retraining |
| `services/retraining_scheduler.py` | Retraining scheduler (currently empty) |
| `training/training_orchestrator.py` | Training orchestration |

## Demo & Testing

| File | Fungsi |
|------|--------|
| `examples/demo_anomaly_detection.py` | Demo anomaly detection |
| `tests/test_inference.py` | Inference tests |

## Infrastructure (K8s)

| File | Fungsi |
|------|--------|
| `k8s/deployment-anomaly-detector.yaml` | K8s deployment for anomaly detector stream processor |
| `k8s/deployment-metrics-consumer.yaml` | K8s deployment for metrics consumer |
| `k8s/configmap.yaml` | ConfigMap (DB, Kafka settings) |

## Domain Configuration

| File | Fungsi |
|------|--------|
| `config/domain_mapping.py` | DOMAIN_FEATURE_MAP — pemetaan feature ke domain |
| `core/correlation_rules.py` | Correlation rules evaluator |
| `correlation/correlation_buffer.py` | Temporal correlation buffer (300s window) |
