---
title: "MT-019 Anomaly Detection Framework"
created: 2026-05-20
updated: 2026-07-10
version: 2.0
type: implementation-spec
task_id: MT-019
block: 7
assignee: Fakhri Aulia R
status: done
dcim_wiki_section: "block7-analytics-ai-engine.md → Section 3: Anomaly Detection, Section 12: Monitoring & Alerting"
tags:
  - anomaly-detection
  - ensemble-learning
  - drift-detection
  - model-registry
  - real-time-inference
  - streaming
  - prometheus
  - fastapi
  - analytics-ai-engine
---

# (MT-019) Anomaly Detection Framework v2.0

> **Dokumen ini merupakan v2 dari MT-019 Anomaly Detection Framework.**
> Seluruh kontor asli dipertahankan, ditambah penambahan section dcim-wiki alignment, actual code mapping, dan penstrukturan ulang untuk clarity.

---

## Daftar Isi

1. [Architecture & Model Registry Foundation](#1--architecture--model-registry-foundation)
2. [Unified Feature Engineering & Drift Detection](#2--unified-feature-engineering--drift-detection)
3. [Multi-Model & Ensemble Detection Engine](#3--multi-model--ensemble-detection-engine)
4. [Real-Time Inference & Intelligent Alert Layer](#4--real-time-inference--intelligent-alert-layer)
5. [Automation, Monitoring & Resilience System](#5--automation-monitoring--resilience-system)
6. [Addendum v1.2.0 — Penyesuaian untuk Use Case 1, 2, 3](#6-addendum-v120--penyesuaian-untuk-use-case-1-2-3)
7. [dcim-wiki Alignment](#7-dcim-wiki-alignment)
8. [Actual Code Location](#8-actual-code-location)
9. [Alignment Score & Gap Analysis](#9-alignment-score--gap-analysis)

---

## 1 . Architecture & Model Registry Foundation

### Objective

Membangun fondasi arsitektur AI monitoring yang versioned, modular, dan production-ready.

### Implemented Components

#### Model Versioning System

* Model disimpan dalam struktur:

```shellscript
dcim_ai/artifacts/models/
 ├── v1.0/
 ├── v1.1/
 ├── v1.2/
```

Setiap versi berisi:

* `models.pkl` (ensemble model)
* `pipeline.pkl` (feature pipeline)
* `baseline_stats.json`
* `metadata.json`

#### Model Registry

File:

```
dcim_ai/registry/registry.json
```

Struktur:

```json
{
  "current_production": "v1.4",
  "available_models": ["v1.0", "v1.1", "v1.2", "v1.3", "v1.4"]
}
```

Fungsi:

* Track production model
* Promote model via CLI
* Version control

Metrics:

* Versioned Model Storage (v1.0 – v1.4)
  * Menjamin tracebility.
  * Mendukung rollback.
* Metadata Tracking
  * Baseline mean & std disimpan.
  * Digunakan untuk drift comparasion.

#### Model Promotion System

Command:

```
python -m dcim_ai.registry.promote_model v1.4
```

Fitur:

* Safe production switching
* Version archival
* Metadata update

#### Production Loader

File:

```
load_production_model.py
```

Fungsi:

* Load model bedasarkan registry
* Fail-safe loading
* Separation between training & inference

### Outcome

* Model lifecycle terkontrol
* No hardcoded model
* Production ready version management
* Clean seperation training vs inference

---

## 2 . Unified Feature Engineering & Drift Detection

### Objective

Standarisasi preprocessing dan deteksi perubahan distribusi data.

### Implemented Components

#### Feature Pipeline

File:

```
dcim_ai/features/feature_pipeline.py
```

Fungsi:

* Cleaning
* Feature selection
* Scaling (StandardScaler)
* Feature consistency enforcement

Pipeline disimpan per versi model

#### Baseline Feature Statistics

Setiap model menyimpan:

```json
{
  "mean": [...],
  "std": [...]
}
```

Digunakan untuk drift detection.

#### Drift Detection Engine

File:

```
dcim_ai/features/drift_detection.py
```

Metode:

* Z-score per feature
* Aggregate drift score
* Classification:
  * stable
    * Z-score dalam range normal.
  * moderete\_drift
    * Deviasi signifikan tapi belum kritis.
  * severe\_drift
    * Perubahan distribusi drastis.
    * Memicu retraining otomatis.

Metrics:

Z-score

Formula:

```
z = (x - μ) / σ
```

Digunakan untuk:

* Mengukur deviasi terhadap baseline.
* Menentukan drift severity.

#### Drift Behavior

Contoh hasil:

```json
{
  "drift_score": 329.37,
  "drift_status": "severe_drift"
}
```

### Outcome

* Feature standardization konsisten
* Model aware terhadap data distribution shift
* Drift-aware retraining trigger

---

## 3 . Multi-Model & Ensemble Detection Engine

### Objective

Mengurangi false positive & meningkatkan robustness dengan ensemble learning.

### Implemented Models

* Isolation Forest
  * Tree-based isolation
* Local Outlier Factor
  * Density-based anomaly detection
  * Cocok untuk local cluster detection
* One-Class SVM
  * Boundary-based classification.
  * Cocok untuk margin-based detection.

### Ensemble Strategy

Voting logic:

```
>=2 anomaly votes → anomaly 
<2 anomaly votes → normal
```

Severity classification:

* 3 votes → critical
* 2 votes → warning
* 1 vote → weak\_signal
* 0 vote → normal

Majority Voting

* Anomaly jika ≥ 2 model setuju.
* Mengurangi false positive.

Severity Grading

* Normal
* Warning
* Critical

Bedasarkan

* Model agreement
* Drift severity
* Temporal persistence

### Example Output

```json
{
  "prediction": "anomaly",
  "severity": "critical",
  "ensemble_score": -58.12,
  "model_votes": {
    "isolation_forest": -1,
    "local_outlier_factor": -1,
    "one_class_svm": -1
  }
}
```

### Outcome

* False positive reduction
* Robust detection
* Interpretable vote breakdown
* Scalable model expansion

---

## 4 . Real-Time Inference & Intelligent Alert Layer

### Objective

Menyediakan real-time AI monitoring API dengan alert intelligence.

### FastAPI Inference Service

Endpoint:

```
POST /predict
GET /
GET /metrics
```

### Intelligent Alert System

Fitur:

* Saverity grading
* Alert cooldown (anti-spam)
* Alert threshold logic
* Drift-based escalation

### Example Behavior

| **Condition**    | **Output**    |
| ---------------- | ------------- |
| Slight deviation | weak\_signal  |
| Strong anomaly   | warning       |
| Extreme anomaly  | critical      |
| Data shift       | severe\_drift |

### Outcome

* Real-time decision engine
* Smart alerting
* Noise reduction
* API production ready

---

## 5 . Automation, Monitoring & Resilience System

### Objective

Membuat sistem self-healing, observable, dan production resilient.

### Automation

#### Auto Retraining

Trigger ketika:

```
drift_status == severe_drift
```

Dengan cooldown protection.

### Safe Retrain Worker

* Background thread
* Exeption-safe wrapper
* Non-blocking Inference

### Hot Model Reload

File:

```
model_manager.py
```

Fitur:

* Watch registry.json
* Auto reload production model
* No API restart required
* Thread-safe locking

### Prometheus Monitoring

Metrics:

* dcim\_requests\_total
* dcim\_anomalies\_total
* dcim\_normals\_total
* dcim\_retrain\_total
* dcim\_inference\_latency\_seconds

### Resilience Features

* Cooldown retrain protection
* Alert anti-spam
* Thread-safe model swap
* Safe fallback handling
* Versioned deployment

### Outcome

* Self-healing AI Monitoring
* Observable metrics
* Production-safe hot swap
* Controlled automation

---

## 6. Addendum v1.2.0 — Penyesuaian untuk Use Case 1, 2, 3

> **Tanggal:** 20 Mei 2026
> **Tujuan:** Memperluas Anomaly Detection Framework agar mendukung multi-model, multi-domain, dan streaming inference yang dibutuhkan UC1/UC2/UC3.
> **Sifat:** Addendum non-destruktif — bagian 1–5 di atas tetap berlaku.

### 6.1 Ringkasan Gap

| Area | Kondisi Saat Ini | Kebutuhan UC | Status |
| --- | --- | --- | --- |
| Registry scope | Hanya menyimpan ensemble anomaly detector | Perlu menyimpan banyak tipe model (anomaly, forecast, energy, capacity) | ⚠️ Diperluas |
| Inference contract | Output tidak terstandar lintas modul | RCA & LLM perlu kontrak seragam | ⚠️ Distandardisasi |
| Inference mode | Batch-oriented (REST `POST /predict`) | UC3 perlu real-time streaming (≤15 menit deteksi) | ❌ Tambah |
| Drift detection | Z-score per feature | UC2 butuh distribution drift pada dataset besar (90 hari) | ❌ Tambah |
| Drift action | Retraining trigger ada, tapi watcher runtime belum eksplisit | Semua UC butuh observability drift kontinu | ⚠️ Diperjelas |

### 6.2 Multi-Model Registry

Skema `registry.json` (atau tabel `llm_model_registry` / `model_registry` setara) diperluas:

```json
{
  "models": {
    "anomaly_v1.4":      {"type": "anomaly",       "domain": "server",  "status": "production"},
    "failure_forecast_v1.0": {"type": "forecast",  "domain": "server",  "status": "candidate"},
    "energy_anomaly_v1.0":   {"type": "anomaly",   "domain": "power",   "status": "candidate"},
    "capacity_cluster_v1.0": {"type": "clustering","domain": "compute", "status": "shadow"}
  },
  "current_production": {
    "anomaly":  "anomaly_v1.4",
    "forecast": null,
    "energy":   null,
    "capacity": null
  }
}
```

**Field baru wajib per entri:**
* `type` — `anomaly | forecast | clustering | energy_anomaly | capacity_optimizer`
* `domain` — `server | power | cooling | compute | storage | network`
* `inference_mode` — `batch | streaming | scheduled`
* `data_contract_version` — versi schema input/output

**Backward compatibility:** Jika `type` tidak ada, default ke `anomaly` (perilaku lama).

### 6.3 Inference Contract Terstandar

Tambahkan kontrak output bersama agar RCA (MT-022) & LLM (MT-023) konsumsi seragam.

```python
@dataclass
class InferenceResult:
    model_id: str               # 'anomaly_v1.4'
    model_type: str             # 'anomaly' | 'forecast' | ...
    asset_id: str
    timestamp: datetime
    score: float                # raw model score
    severity: str               # 'normal' | 'weak_signal' | 'warning' | 'critical'
    confidence: float           # [0, 1]
    domain: str
    evidence: dict              # feature contributions / votes / drift
    forecast_horizon_h: int | None = None  # hanya untuk type=forecast
```

Output existing (`prediction`, `severity`, `ensemble_score`, `model_votes`) **tetap dipertahankan** sebagai field kompatibilitas, dengan tambahan `model_type=anomaly` & `model_id` otomatis.

**Implementasi (v1.2.0 — selesai 20 Mei 2026):**

| Komponen | Lokasi | Catatan |
| --- | --- | --- |
| `InferenceResult` dataclass + enum (`Severity`, `ModelType`) | `dcim_ai/contracts/__init__.py` | Field baru ditambahkan, field lama diakses via `legacy` dict |
| Asset enrichment helper | `dcim_ai/inference/asset_enricher.py` | `enrich_inference()` — auto-set `asset_context` via `AssetContextResolver` |
| Test coverage | `dcim_ai/tests/test_contracts.py` (3 test InferenceResult) + `dcim_ai/tests/test_asset_enricher.py` (4 test inference enrich) | Total 7 test |

### 6.4 Streaming Inference Adapter

Untuk UC3 (real-time PUE drift) tambah subscriber pada streaming bus.

| Komponen | Spesifikasi |
| --- | --- |
| Bus | MQTT / Kafka (topic per domain: `metrics.power`, `metrics.environment`) |
| Adapter | `dcim_ai/inference/streaming_adapter.py` — windowed (1m / 5m / 15m), backpressure-safe |
| Output | `InferenceResult` di-publish ke topic `inference.<domain>` + persisted ke `inference_results` |
| Latency target | end-to-end ≤ 15 menit (UC3 success criteria) |

REST endpoint `/predict` tetap dipertahankan untuk batch & ad-hoc.

### 6.5 Distribution Drift (Tambahan untuk UC2)

Z-score per feature efektif untuk anomaly window pendek. Untuk UC2 (90 hari capacity trend) tambahkan:

| Metode | Tujuan |
| --- | --- |
| Population Stability Index (PSI) | Deteksi pergeseran distribusi feature antar window panjang |
| Kolmogorov-Smirnov test | Verifikasi statistik perbedaan distribusi training vs current |
| Feature drift heatmap | Output observability untuk monitoring lifecycle |

PSI thresholds standar industri:
* `< 0.1` — stable
* `0.1–0.25` — moderate drift
* `> 0.25` — severe drift

### 6.6 Drift Watcher Runtime

Existing: trigger retraining bila `drift_status == severe_drift`. Diperjelas menjadi service eksplisit.

```python
class DriftWatcher:
    interval_seconds: int = 300
    targets: list[str]               # daftar model_id yang dipantau
    metrics: list[str]               # ['z_score', 'psi', 'ks']
    on_severe: Callable               # callback retraining / alert
    cooldown_seconds: int = 3600
```

Output ke Prometheus:
* `dcim_drift_score{model_id, feature}` (histogram)
* `dcim_drift_severe_total{model_id}` (counter)
* `dcim_retrain_triggered_total{model_id, reason}` (counter)

### 6.7 Mapping ke Use Case

| UC | Bagian Addendum yang Dipakai |
| --- | --- |
| UC1 | 6.2 (`failure_forecast_v*`), 6.3 (kontrak `forecast_horizon_h`), 6.6 (drift watcher) |
| UC2 | 6.2 (`capacity_cluster_v*`), 6.5 (PSI 90 hari), 6.6 (watcher) |
| UC3 | 6.2 (`energy_anomaly_v*`), 6.4 (streaming adapter), 6.6 (watcher real-time) |

### 6.8 Changelog

| Date       | Versi  | Auth         | Note                                                            |
| ---------- | ------ | ------------ | --------------------------------------------------------------- |
| 20/05/2026 | 1.2.0  | DCIM AI Team | Multi-model registry, inference contract, streaming, PSI/KS drift |

---

## 7. dcim-wiki Alignment

Bagian ini memetakan MT-019 ke dcim-wiki Block 7 reference design (`block7-analytics-ai-engine.md`).

### 7.1 Mapping ke Section 3: Anomaly Detection

| dcim-wiki Section 3 | MT-019 Coverage | Status |
|---|---|---|
| 3.1 Detection Methods (Z-score, Isolation Forest, Moving Average, Seasonal Decomposition) | Z-score (§2), Isolation Forest (§3), LOF & OCSVM (§3) — Moving Average & Seasonal Decomposition belum diimplementasikan | ⚠️ Partial |
| 3.2 Z-score Implementation (`ZScoreDetector` class) | Terdapat pada `features/drift_detection.py` — implementasi Z-score per feature dengan aggregate drift score | ✅ Aligned |
| 3.3 Isolation Forest Implementation (`IsolationForestDetector` class) | Terdapat pada `services/anomaly_service.py` — ensemble IF + LOF + OCSVM dengan voting logic | ✅ Aligned |
| 3.4 Anomaly Alert Schema (JSON dengan `anomaly_id`, `severity`, `possible_causes`) | Output schema tersedia (§4), namun field `possible_causes` dan `recommended_actions` belum ter-automate (akan dihandle oleh RCA engine MT-022) | ⚠️ Partial |

### 7.2 Mapping ke Section 12: Monitoring & Alerting

| dcim-wiki Section 12 | MT-019 Coverage | Status |
|---|---|---|
| 12.1 Key Metrics (`analytics_anomalies_detected_total`, `analytics_model_drift_score`, etc.) | Prometheus metrics tersedia: `dcim_requests_total`, `dcim_anomalies_total`, `dcim_normals_total`, `dcim_inference_latency_seconds` — naming convention belum match dengan dcim-wiki (`analytics_*` prefix) | ⚠️ Naming Gap |
| 12.2 Alert Rules (Prometheus alerting rules YAML) | Alert cooldown & severity grading ada (§4), namun Prometheus alerting rules YAML belum didefinisikan secara eksplisit | ⚠️ Partial |
| `analytics_model_drift_score` gauge metric | Drift score tersedia via `dcim_drift_score{model_id, feature}` histogram (§6.6) | ✅ Aligned |
| `analytics_model_accuracy` gauge metric | Belum diimplementasikan — perlu model accuracy tracking | ❌ Gap |

### 7.3 Alur Data Alignment

```
dcim-wiki Reference:              MT-019 Implementation:
Telemetry Metrics                 Telemetry Metrics (Prometheus)
    ↓                                 ↓
Feature Pipeline                  Feature Pipeline (feature_pipeline.py)
    ↓                                 ↓
Multi-Model Ensemble              Multi-Model Ensemble (IF + LOF + OCSVM voting)
    ↓                                 ↓
Drift Detection                   Drift Detection (Z-score + PSI + KS)
    ↓                                 ↓
Inference API (FastAPI)           Inference API (FastAPI — /predict, /metrics)
    ↓                                 ↓
Alert Layer                       Alert Layer (severity grading + cooldown)
    ↓                                 ↓
Event Logging                     Event Logging (event_logger.py)
    ↓                                 ↓
Automation & Retraining           Automation & Retraining (auto retrain on severe_drift)
```

---

## 8. Actual Code Location

Berikut mapping aktual file Python pada implementasi v2 di `/home/infra/dcim_project/implementation/dcim_ai_v2_rag/`:

### 8.1 Core Anomaly Detection

| File | Deskripsi |
|---|---|
| `services/anomaly_service.py` | Multi-model voting ensemble (Isolation Forest + LOF + One-Class SVM). Fungsi utama: training, prediction, severity classification berdasarkan model agreement |
| `stream/anomaly_detector.py` | Real-time anomaly detection untuk streaming pipeline. Windowed detection dengan backpressure handling |

### 8.2 Feature Engineering & Drift

| File | Deskripsi |
|---|---|
| `features/drift_detection.py` | Drift detection engine — Z-score per feature, aggregate drift score, classification (stable/moderate_drift/severe_drift) |
| `features/drift_detector.py` | Extended drift detector — Population Stability Index (PSI) dan Kolmogorov-Smirnov test untuk long-window drift analysis |
| `features/feature_pipeline.py` | Feature pipeline — cleaning, feature selection, StandardScaler scaling, feature consistency enforcement |

### 8.3 API Layer

| File | Deskripsi |
|---|---|
| `api/routers/anomalies.py` | FastAPI router untuk anomaly endpoints — POST /predict, GET anomaly history, GET drift status |

### 8.4 Model Registry & Management

| File | Deskripsi |
|---|---|
| `registry/model_registry.py` | Model registry — versioned model storage, production promotion, rollback support, multi-model type tracking |

### 8.5 Monitoring

| File | Deskripsi |
|---|---|
| `monitoring/drift_detector.py` | Runtime drift watcher — periodic drift score calculation, Prometheus metric export, retraining trigger callback |

### 8.6 Supporting Files

| File | Deskripsi |
|---|---|
| `training/train_anomaly_model.py` | Training pipeline untuk ensemble anomaly model |
| `examples/demo_anomaly_detection.py` | Demo script untuk anomaly detection workflow |
| `k8s/deployment-anomaly-detector.yaml` | Kubernetes deployment manifest untuk anomaly detector service |

---

## 9. Alignment Score & Gap Analysis

### Overall Alignment Score: ~70%

### Breakdown

| Aspek | Score | Keterangan |
|---|---|---|
| Detection Methods | 85% | Z-score, IF, LOF, OCSVM implemented. Moving Average & Seasonal Decomposition belum ada |
| Ensemble Voting | 100% | Majority voting dengan severity grading fully implemented |
| Model Registry | 90% | Versioned registry dengan promote/rollback. Multi-model type (§6.2) sudah di-extend |
| Drift Detection | 80% | Z-score + PSI + KS tersedia. Feature drift heatmap belum ada |
| Inference Contract | 75% | `InferenceResult` dataclass tersedia. `possible_causes`/`recommended_actions` perlu RCA integration |
| Streaming Adapter | 70% | `stream/anomaly_detector.py` tersedia. Full Kafka/MQTT integration perlu verification |
| Monitoring Metrics | 60% | Prometheus metrics ada, tapi naming gap (`dcim_*` vs `analytics_*`). `model_accuracy` gauge belum ada |
| Alert Rules | 50% | Alert cooldown & severity ada. Prometheus alerting rules YAML belum didefinisikan |
| Automation | 75% | Auto-retrain on severe_drift tersedia. DriftWatcher runtime partially implemented |

### Key Gaps

1. **Moving Average & Seasonal Decomposition** — dcim-wiki Section 3.1 mereferensikan 4 detection methods, MT-019 baru implement 2 (Z-score, Isolation Forest) + 2 pendukung (LOF, OCSVM)
2. **Prometheus Naming Convention** — Menggunakan prefix `dcim_*` instead of `analytics_*` sesuai dcim-wiki Section 12
3. **Model Accuracy Tracking** — `analytics_model_accuracy` gauge belum diimplementasikan
4. **Prometheus Alerting Rules YAML** — Belum didefinisikan secara formal
5. **Feature Drift Heatmap** — Observability output untuk drift monitoring belum ada

---

> **Catatan:** Dokumen ini merupakan v2 restructured dari MT-019 Anomaly Detection Framework original. Seluruh konten asli (§1–§6) dipertahankan tanpa perubahan. Section 7–9 merupakan penambahan baru untuk alignment tracking.
