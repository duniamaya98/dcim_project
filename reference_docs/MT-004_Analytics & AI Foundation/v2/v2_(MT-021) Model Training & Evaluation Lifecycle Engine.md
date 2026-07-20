---
title: "MT-021 Model Training & Evaluation Lifecycle Engine"
created: 2026-05-20
updated: 2026-07-10
version: 2.0
type: task-documentation
task_id: MT-021
block: 7
assignee: Fakhri Aulia R
status: done
dcim_wiki_section: "block7-analytics-ai-engine.md — Section 8: Model Training Pipeline"
tags:
  - model-training
  - evaluation-engine
  - anomaly-detection
  - lifecycle-governance
  - promotion-gatekeeper
  - drift-robustness
  - ensemble-model
  - model-registry
  - ml-ops
  - block7
---

# (MT-021) Model Training & Evaluation Lifecycle Engine

> **Versi:** 2.0  
> **Status:** Done  
> **Assignee:** Fakhri Aulia R  
> **Block:** 7 — Analytics & AI Engine  
> **dcim-wiki Alignment:** Section 8: Model Training Pipeline

---

## Daftar Isi

1. [Unified Training & Artifact Management Engine](#1-unified-training--artifact-management-engine)
2. [Cross-Version Benchmark & Evaluation Engine](#2-cross-version-benchmark--evaluation-engine)
3. [Correlation & Incident Impact Validation](#3-correlation--incident-impact-validation)
4. [Drift Robustness & Ensemble Optimization](#4-drift-robustness--ensemble-optimization)
5. [Promotion Gatekeeper & Simulation Framework](#5-promotion-gatekeeper--simulation-framework)
6. [System Evolution Summary](#6-system-evolution-summary)
7. [Addendum v1.2.0 — Multi-Task Training Profile](#7-addendum-v120--multi-task-training-profile)
8. [dcim-wiki Alignment](#8-dcim-wiki-alignment)
9. [Actual Code Location](#9-actual-code-location)
10. [Alignment Score](#10-alignment-score)
11. [Changelog](#11-changelog)

---

## Referensi

- **dcim-wiki:** [block7-analytics-ai-engine.md — Section 8](../../dcim-wiki/reference-designs/block7-analytics-ai-engine.md#8-model-training-pipeline)
- **Task Dependency:** [(MT-018) Traditional Machine Learning Model](./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/I44pKpyLLU9mmFHCLBRgw)
- **Task Dependency:** [(MT-019) Anomaly Detection Framework](./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep)
- **Task Dependency:** [(MT-020) Cross-Domain Correlation Engine](./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/dnYp6l89De)

---

## 1. Unified Training & Artifact Management Engine

### 1.1 Objective

Membangun sistem training yang version-controlled, reproducible, dan lifecycle-aware untuk memastikan setiap model anomaly:

* Dapat dilacak versinya
* Memiliki baseline statistik drift
* Tersimpan dalam struktur artifact yang konsisten
* Tidak langsung aktif ke production

Fase ini menyelesaikan keterbatasan pada fase sebelumnya yang belum memiliki full version lifecycle governance [(MT-018) Traditional Machine Learning Model](./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/I44pKpyLLU9mmFHCLBRgw).

### 1.2 Architectural Concept

```
Monitoring Dataset
        ↓
Training Orchestrator
        ↓
Feature Pipeline
        ↓
Ensemble Model Training
        ↓
Artifact Packaging
        ↓
Model Registry (Candidate)
```

### 1.3 Implementation — Training Orchestrator

**File:**

```
dcim_ai/training/training_orchestrator.py
```

**Fungsi:**

* Load dataset berdasarkan time-window
* Train / validation split
* Ensemble training:
  * Isolation Forest
  * Local Outlier Factor
  * One-Class SVM
* Validation anomaly ratio check
* Drift baseline calculation
* Artifact packaging
* Candidate auto-registration (optional)

### 1.4 Artifact Structure (Per Version)

```
dcim_ai/artifacts/models/vX.Y/
    isolation_forest.pkl
    lof.pkl
    ocsvm.pkl
    scaler.pkl
    feature_columns.json
    metadata.json
```

### 1.5 Metadata Specification

Metadata menyimpan:

| Field | Deskripsi |
|---|---|
| `version` | Versi model (e.g., v1.13) |
| `training_window` | Parameter yang menentukan rentang waktu dataset training (e.g., `last_30_minutes`, `all`). Berfungsi untuk: mengontrol adaptasi model terhadap data terbaru, membedakan full historical retrain vs rolling retrain, menghindari contamination akibat data lama |
| `validation_anomaly_ratio` | Proporsi data pada validation set yang diklasifikasikan sebagai anomaly. Rumus: `validation_anomaly_ratio = anomaly_count / total_validation_samples`. Digunakan untuk: memastikan model tidak terlalu agresif, mendeteksi anomaly explosion saat retraining, membandingkan stabilitas antar versi model. Jika terlalu tinggi → model over-sensitive. Jika terlalu rendah → model terlalu tumpul |
| `drift_baseline_mean` | Rata-rata nilai setiap fitur pada dataset training. Disimpan sebagai baseline referensi untuk evaluasi drift pada fase inference dan drift robustness testing. Digunakan untuk: perhitungan Z-score, drift simulation, distribution comparison antar versi |
| `drift_baseline_std` | Standar deviasi setiap fitur pada dataset training. Digunakan untuk: mengukur deviasi distribusi, simulasi drift berbasis sigma (0.5σ, 1σ, 2σ). Nilai ini menjadi dasar dalam mengukur ketahanan model terhadap distribution shift |
| `timestamp` | Waktu training dilakukan |

### 1.6 Outcome

* Model training kini reproducible
* Artifact terstruktur
* Tidak ada overwrite manual
* Version governance siap untuk promotion control

---

## 2. Cross-Version Benchmark & Evaluation Engine

### 2.1 Objective

Mencegah regression dengan membandingkan model candidate terhadap model production aktif. Fase ini memperluas model registry dan lifecycle management yang telah dibangun sebelumnya [(MT-019) Anomaly Detection Framework](./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep).

### 2.2 Architectural Concept

```
Candidate Model
        +
Production Model
        ↓
Evaluation Engine
        ↓
Regression Metrics
```

### 2.3 Evaluation Metrics

| Metric | Deskripsi |
|---|---|
| `anomaly_ratio_candidate` | Proporsi anomaly yang dihasilkan model candidate pada dataset evaluasi. Digunakan untuk: mengukur agresivitas model baru, membandingkan perubahan perilaku terhadap production |
| `anomaly_ratio_production` | Proporsi anomaly yang dihasilkan model production aktif. Menjadi baseline pembanding untuk regression analysis |
| `anomaly_delta` | Selisih antara `anomaly_ratio_candidate` dan `anomaly_ratio_production`. Rumus: `anomaly_delta = candidate_ratio - production_ratio`. Digunakan untuk: mendeteksi regression, mengidentifikasi anomaly explosion, menentukan `anomaly_safe` flag. Semakin besar delta → semakin berisiko model baru |
| `agreement_rate` | Presentase kesamaan prediksi antara model candidate dan production. Rumus: `agreement_rate = same_prediction / total_samples`. Digunakan untuk: mengukur stabilitas antar versi, mendeteksi perubahan boundary decision, menilai consistency model behavior |
| `dataset_size` | Jumlah sampel yang digunakan dalam evaluasi. Berfungsi untuk: memberikan konteks statistik, menghindari evaluasi pada dataset terlalu kecil, menentukan reliabilitas hasil perbandingan |

### 2.4 Safety Rule

* `anomaly_delta` harus dalam threshold aman
* `agreement_rate` tinggi
* Tidak terjadi anomaly explosion atau anomaly saturation

### 2.5 Output

```
evaluation_report.json
```

### 2.6 Outcome

* Regression terdeteksi sebelum deployment
* Model baru tidak langsung dipercaya
* Production stability terjaga

---

## 3. Correlation & Incident Impact Validation

### 3.1 Objective

Mengukur dampak perubahan model terhadap sistem incident & domain correlation. Fase ini terintegrasi langsung dengan arsitektur correlation engine [(MT-020) Cross-Domain Correlation Engine](./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/dnYp6l89De). Evaluasi tidak berhenti pada anomaly detection, tetapi dilanjutkan hingga pembentukan incident yang bersifat operasional.

### 3.2 Architectural Concept

```
Anomaly Prediction
        ↓
Domain Engine
        ↓
Correlation Engine
        ↓
Incident Simulation
        ↓
Impact Comparison
```

### 3.3 Evaluated Metrics

| Metric | Deskripsi |
|---|---|
| `incident_delta` | Selisih jumlah incident antara model candidate dan production. Digunakan untuk: mengukur dampak operasional, mendeteksi escalation tidak terkontrol, menghindari incident explosion di production |
| `candidate_incident_count` | Jumlah total incident yang dihasilkan oleh model candidate |
| `production_incident_count` | Jumlah total incident yang dihasilkan oleh model production. Menjadi indikator utama perubahan perilaku sistem monitoring |
| `multi_domain_ratio` | Proporsi incident yang melibatkan lebih dari satu domain aktif. Rumus: `multi_domain_ratio = multi_domain_incidents / total_incidents`. Digunakan untuk: mendeteksi interaksi lintas domain, mengidentifikasi kompleksitas gangguan, menilai perubahan correlation behavior |
| `severity_distribution` | Distribusi tingkat severity (normal, warning, critical). Digunakan untuk: mengukur perubahan eskalasi, mendeteksi peningkatan severity profile, menilai potensi alert fatigue |
| `average_confidence` | Rata-rata confidence score dari incident. Confidence dihitung dari kombinasi: anomaly_ratio, drift_ratio, domain persistence. Digunakan untuk: mengukur keyakinan sistem terhadap incident, menilai reliability output |
| `domain_activation_intensity` | Rata-rata jumlah domain aktif per incident. Digunakan untuk: mengukur kompleksitas gangguan, mendeteksi perubahan domain behavior, menganalisis interaksi lintas domain |
| `correlation_safe` | Boolean indicator yang menyatakan apakah perubahan correlation behavior masih dalam batas aman. `True` → perubahan terkendali, `False` → perubahan signifikan, perlu review |

### 3.4 Insight Layer

Sistem kini mampu:

* Mendeteksi perubahan severity profile
* Mengidentifikasi pergeseran multi-domain interaction
* Mengukur intensitas aktivasi domain
* Menghitung potensi escalation

### 3.5 Outcome

* Model tidak hanya dievaluasi dari anomaly
* Dampak operasional dianalisis
* Incident stability terjaga

---

## 4. Drift Robustness & Ensemble Optimization

### 4.1 Objective

Menguji ketahanan model terhadap distribution shift.

Mengatasi keterbatasan drift sensitivity yang teridentifikasi pada fase awal [(MT-018) Traditional Machine Learning Model](./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/I44pKpyLLU9mmFHCLBRgw).

### 4.2 Drift Simulation Strategy

**Partial Feature Drift:**

* Drift hanya pada sebagian fitur (realistic simulation)
* Level:
  * 0σ
  * 0.5σ
  * 1σ
  * 2σ

### 4.3 Evaluation Metrics

| Metric | Deskripsi |
|---|---|
| `drift_level_0` | Anomaly ratio pada dataset tanpa drift. Menjadi baseline stabilitas model |
| `drift_level_0.5` | Anomaly ratio saat sebagian fitur digeser 0.5σ. Digunakan untuk: mengukur toleransi terhadap mild shift, mendeteksi over-sensitivity |
| `drift_level_1` | Anomaly ratio saat sebagian fitur digeser 1σ. Mewakili moderate distribution shift. Jika terlalu tinggi → model terlalu sensitif |
| `drift_level_2` | Anomaly ratio saat sebagian fitur digeser 2σ. Mewakili severe distribution shift. Seharusnya meningkat signifikan dibanding `drift_level_0` |
| `drift_sensitivity` | Perbedaan antara `drift_level_2` dan `drift_level_0`. Rumus: `drift_sensitivity = drift_level_2 - drift_level_0`. Digunakan untuk: mengukur respons model terhadap shift besar, menilai ketahanan model |

### 4.4 Ensemble Optimization

| Parameter | Deskripsi |
|---|---|
| Voting threshold (≥2/3 model) | Parameter ensemble decision rule. Minimal dua dari tiga model harus menyetujui anomaly agar dianggap valid. Digunakan untuk: mengurangi false positive, meningkatkan robustness, menjaga konsistensi prediksi |
| contamination / nu tuning | Parameter pada model anomaly detection yang menentukan estimasi proporsi anomaly dalam data training. Digunakan untuk: mengontrol boundary decision, menghindari model terlalu agresif, menyesuaikan sensitivitas terhadap distribusi data |
| Progressive drift response validation | Validasi respons model secara bertahap terhadap peningkatan level drift |

### 4.5 Outcome

* Tidak terjadi anomaly saturation
* Respons drift menjadi gradual
* Model lebih tahan terhadap noise
* Robust terhadap severe shift

---

## 5. Promotion Gatekeeper & Simulation Framework

### 5.1 Objective

Menyatukan seluruh layer evaluasi menjadi sistem keputusan semi-automatic sebelum activation.

Mengatasi keterbatasan "manual promotion tanpa evaluasi terstruktur".

### 5.2 Architectural Concept

```
Anomaly Evaluation
        +
Correlation Impact
        +
Drift Robustness
        ↓
Promotion Gatekeeper
        ↓
APPROVE / REVIEW / REJECT
```

### 5.3 Decision Inputs

| Flag | Deskripsi |
|---|---|
| `anomaly_safe` | `True` jika `anomaly_delta` dalam batas aman dan `agreement_rate` tinggi. Menandakan tidak terjadi regression signifikan |
| `correlation_safe` | `True` jika incident behavior dan severity profile masih dalam batas toleransi. Menandakan dampak operasional terkendali |
| `drift_safe` | `True` jika `drift_level_0.5` dan `drift_level_1` tidak menunjukkan over-sensitivity. Menandakan model stabil terhadap mild shift |

### 5.4 Decision Output

```json
{
  "candidate_version": "v1.13",
  "promotion_recommendation": "APPROVE | REVIEW | REJECT",
  "risk_level": "LOW | MEDIUM | HIGH"
}
```

### 5.5 Decision Categories

| Kategori | Kondisi |
|---|---|
| **APPROVE** | Aman di semua layer |
| **REVIEW** | Ada perubahan signifikan tapi terkendali |
| **REJECT** | Risiko tinggi atau regression terdeteksi |

### 5.6 Governance Result

* Model tidak lagi self-activate
* Lifecycle terkontrol
* Promotion berbasis evaluasi multi-layer
* Risk-aware AI deployment

---

## 6. System Evolution Summary

Sistem telah berevolusi dari:

> **Feature-level anomaly detection** → **Lifecycle-Governed Monitoring Intelligence Platform**

| Aspek | Sebelum | Sesudah |
|---|---|---|
| Training | Manual, tanpa versioning | Version-controlled, reproducible |
| Evaluasi | Single-metric | Multi-layer (anomaly, correlation, drift) |
| Promotion | Manual, tanpa evaluasi terstruktur | Semi-automatic, gatekeeper-based |
| Drift Awareness | Tidak ada | Baseline-aware, progressive validation |
| Incident Impact | Tidak terukur | Correlation & severity tracked |

---

## 7. Addendum v1.2.0 — Multi-Task Training Profile

> **Tanggal:** 20 Mei 2026
> **Tujuan:** Membuat training & evaluation lifecycle multi-task agar mendukung anomaly detection, forecasting (UC1), clustering (UC2), dan energy anomaly (UC3).
> **Sifat:** Addendum non-destruktif — bagian 1–6 di atas tetap berlaku.

### 7.1 Ringkasan Gap

| Area | Kondisi Saat Ini | Kebutuhan UC | Status |
| --- | --- | --- | --- |
| Training profile | Hanya tahu ensemble anomaly (IF/LOF/OCSVM) | UC1 forecast, UC2 clustering, UC3 energy anomaly | ❌ Tambah |
| Evaluation metric | `validation_anomaly_ratio` saja | MAPE/RMSE (forecast), silhouette (clustering), detection latency (energy) | ❌ Tambah |
| Scheduled retraining | Manual / drift-based saja | Semua UC butuh schedule + drift trigger eksplisit | ⚠️ Diperjelas |
| Data window strategy | Single window (mis. 30 menit) | UC1 failure-event window, UC2 90d rolling, UC3 7d rolling | ⚠️ Diperluas |
| Reproducibility | Ada metadata, tapi tanpa dataset hash & seed konsisten | Semua UC perlu audit & rollback | ⚠️ Diperketat |

### 7.2 Multi-Task Training Profile

Training Orchestrator diberi konsep `training_profile` sebagai opsi konfigurasi.

```python
class TrainingProfile:
    name: str                 # 'anomaly' | 'forecast' | 'clustering' | 'energy_anomaly'
    domain: str               # 'server' | 'power' | 'cooling' | 'compute'
    feature_group: str        # dari MT-018 §11.2
    algorithms: list[str]
    training_window: str      # '30m' | '7d' | '30d' | '90d' | 'failure_event'
    eval_metrics: list[str]
    promotion_rules: dict
```

**Profil bawaan:**

| Profil | Domain | Algoritma | Window | Eval |
| --- | --- | --- | --- | --- |
| `anomaly` (existing) | server | IF + LOF + OCSVM | 30m rolling | `anomaly_delta`, `agreement_rate` |
| `forecast` (UC1 baseline) | server | XGBoost / Prophet | 30d + lag | `MAPE`, `RMSE`, `coverage_95` |
| `forecast_advanced` (UC1) | server | LSTM / TFT | 90d sequence | `MAPE`, `failure_recall_24h`, `failure_precision_24h` |
| `clustering` (UC2) | compute / storage | KMeans + Silhouette | 90d aggregate | `silhouette`, `inertia`, `davies_bouldin` |
| `energy_anomaly` (UC3) | power / cooling | IF + Z-score | 7d streaming | `detection_latency_p95`, `false_positive_rate` |

**Backward compatibility:** Bila `training_profile` tidak diset, default ke `anomaly` (perilaku lama).

### 7.3 Evaluation Metric Catalog (Tambahan)

Selain metrik existing (`anomaly_delta`, `agreement_rate`, `drift_level_*`), tambahkan:

| Metric | Profil | Definisi |
| --- | --- | --- |
| `MAPE` | forecast | Mean Absolute Percentage Error |
| `RMSE` | forecast | Root Mean Squared Error |
| `coverage_95` | forecast | % observasi aktual berada di dalam confidence interval 95% |
| `failure_recall_24h` | forecast_advanced | TP / (TP+FN) untuk window 24 jam sebelum failure |
| `failure_precision_24h` | forecast_advanced | TP / (TP+FP) |
| `silhouette` | clustering | Kohesi vs separasi cluster, range [-1, 1] |
| `inertia` | clustering | Sum of squared distances ke centroid |
| `davies_bouldin` | clustering | Cluster similarity ratio (lower better) |
| `detection_latency_p95` | energy_anomaly | P95 latency dari event sampai alert (target ≤ 15 menit) |
| `false_positive_rate` | energy_anomaly | FP / (FP+TN) terhadap baseline tervalidasi |

### 7.4 Scheduled Retraining (Diperjelas)

Existing: drift-based retrain dengan cooldown. Diperluas:

```python
class TrainingSchedule:
    profile: str
    cron: str                # '0 2 * * *' = harian jam 02:00
    drift_trigger: bool      # tetap aktif sebagai trigger sekunder
    on_demand: bool = True   # via CLI / API
    cooldown_hours: int = 1
```

**Default schedule rekomendasi:**

| Profil | Cron | Trigger Drift |
| --- | --- | --- |
| `anomaly` | `*/30 * * * *` (30 menit, existing) | ✅ |
| `forecast` | `0 2 * * *` (harian) | ✅ |
| `forecast_advanced` | `0 3 * * 0` (mingguan) | ✅ |
| `clustering` | `0 4 * * 0` (mingguan) | ⚠️ PSI-based |
| `energy_anomaly` | `0 1 * * *` (harian) | ✅ |

### 7.5 Data Window Strategy (Diperluas)

| Window Type | Cocok Untuk | Behavior |
| --- | --- | --- |
| `rolling_30m` | anomaly online | Existing |
| `rolling_7d` | energy_anomaly | UC3 |
| `rolling_30d` | forecast baseline | UC1 |
| `rolling_90d` | clustering, forecast advanced | UC2/UC1 |
| `failure_event_centered` | supervised forecast | Window N jam sebelum `failure_events.event_time` (UC1) |

Window strategy dipasangkan dengan **dataset snapshot** (lihat 7.6).

### 7.6 Reproducibility (Diperketat)

Setiap artifact wajib menyimpan tambahan metadata:

```json
{
  "version": "v1.5",
  "profile": "energy_anomaly",
  "dataset_snapshot": {
    "source": "power_metrics",
    "window": "rolling_7d",
    "row_count": 432891,
    "sha256": "<hash>"
  },
  "random_seed": 42,
  "code_revision": "<git_sha>",
  "training_window": "...",
  "validation_anomaly_ratio": "...",
  "drift_baseline_mean": [...],
  "drift_baseline_std":  [...],
  "timestamp": "..."
}
```

**Manfaat:**
* Audit trail penuh.
* Rollback by hash.
* Re-run training bit-perfect.

### 7.7 Promotion Gatekeeper (Diperluas per Profil)

Existing gatekeeper memutuskan APPROVE/REVIEW/REJECT berbasis 3 layer (`anomaly_safe`, `correlation_safe`, `drift_safe`). Untuk profil baru, decision input ditambah:

| Profil | Tambahan Gate |
| --- | --- |
| `forecast` | `mape_safe` (MAPE candidate ≤ MAPE production × 1.1), `coverage_safe` (coverage_95 ≥ 0.9) |
| `forecast_advanced` | `failure_recall_safe` (≥ 0.7), `failure_precision_safe` (≥ 0.6) |
| `clustering` | `silhouette_safe` (≥ 0.3) |
| `energy_anomaly` | `latency_safe` (detection_latency_p95 ≤ 15m), `fpr_safe` (false_positive_rate ≤ 0.1) |

### 7.8 Mapping ke Use Case

| UC | Bagian Addendum yang Dipakai |
| --- | --- |
| UC1 | 7.2 (`forecast`, `forecast_advanced`), 7.3 (MAPE, failure_recall_24h), 7.4 (cron harian/mingguan), 7.5 (`failure_event_centered`), 7.7 (gates forecast) |
| UC2 | 7.2 (`clustering`), 7.3 (silhouette, davies_bouldin), 7.4 (mingguan), 7.5 (`rolling_90d`), 7.7 (`silhouette_safe`) |
| UC3 | 7.2 (`energy_anomaly`), 7.3 (detection_latency_p95, FPR), 7.4 (harian + drift), 7.5 (`rolling_7d`), 7.7 (`latency_safe`, `fpr_safe`) |

---

## 8. dcim-wiki Alignment

### 8.1 Mapping ke dcim-wiki Section 8: Model Training Pipeline

MT-021 ter-mapping langsung ke **Section 8: Model Training Pipeline** pada `block7-analytics-ai-engine.md`. Berikut adalah alignment detail antara spesifikasi referensi dcim-wiki dan implementasi aktual MT-021:

| dcim-wiki Section 8 Spec | MT-021 Implementation | Alignment | Catatan |
|---|---|---|---|
| **8.1 Pipeline Stages — Data Collection** | Training Orchestrator: `load_data()` query dari database berdasarkan time-window | ✅ Aligned | Menggunakan `training_window` parameter |
| **8.1 Pipeline Stages — Feature Engineering** | Feature Pipeline (`features/feature_pipeline.py`) melakukan transformasi raw metrics ke fitur | ✅ Aligned | Tersimpan di `feature_columns.json` |
| **8.1 Pipeline Stages — Data Splitting** | Training Orchestrator: Train/Validation split | ⚠️ Partial | dcim-wiki spec: 70/15/15 (train/val/test). Implementasi saat ini: train/validation saja, belum explicit test split |
| **8.1 Pipeline Stages — Model Training** | Ensemble training: Isolation Forest, LOF, One-Class SVM | ✅ Aligned | Multi-model ensemble, extended dengan multi-task profiles |
| **8.1 Pipeline Stages — Evaluation** | Cross-Version Evaluation Engine, Correlation Impact, Drift Robustness | ✅ Aligned (Extended) | dcim-wiki spec: accuracy/precision/recall/F1. MT-021 menambahkan: anomaly_delta, agreement_rate, incident metrics, drift metrics |
| **8.1 Pipeline Stages — Model Registry** | Model Registry (`registry/model_registry.py`) + Candidate auto-registration | ✅ Aligned | Artifact versioned, metadata lengkap |
| **8.1 Pipeline Stages — Deployment** | Promotion Gatekeeper: APPROVE/REVIEW/REJECT sebelum activation | ✅ Aligned (Extended) | Semi-automatic governance, bukan direct deployment |
| **8.1 Pipeline Stages — A/B Testing** | Cross-Version Benchmark: candidate vs production comparison | ⚠️ Partial | Bukan real-time A/B, tapi comparative evaluation sebelum deployment |
| **8.1 Pipeline Stages — Monitoring** | Drift Robustness Evaluator + Drift Detector (`features/drift_detector.py`) | ✅ Aligned | Progressive drift simulation (0σ, 0.5σ, 1σ, 2σ) |
| **8.2 Model Registry Schema** | Metadata JSON per artifact version | ⚠️ Partial | dcim-wiki spec: SQL table `ml_models`. MT-021: file-based `metadata.json`. Perlu harmonisasi ke DB-backed registry |

### 8.2 Gap Analysis

| Gap | dcim-wiki Spec | MT-021 Actual | Rekomendasi |
|---|---|---|---|
| Test split | 70/15/15 train/val/test | Train/validation only | Tambahkan explicit test split pada Training Orchestrator |
| A/B Testing | Real-time A/B comparison | Pre-deployment comparative eval | Sesuai governance model, tapi perlu dokumentasi perbedaan approach |
| Registry backend | SQL table (PostgreSQL) | File-based JSON | Pertimbangkan migrasi ke DB-backed registry untuk scalability |
| Evaluation metrics | accuracy, precision, recall, F1, AUC-ROC | anomaly_delta, agreement_rate, drift metrics | Sudah extended, perlu tambahkan standard ML metrics untuk completeness |

### 8.3 Alignment Summary

| Aspek | Alignment Score |
|---|---|
| Pipeline stages coverage | 85% |
| Model registry | 70% |
| Evaluation approach | 80% |
| Deployment governance | 90% |
| Monitoring & drift | 85% |
| **Overall** | **~80%** |

---

## 9. Actual Code Location

| Komponen | File Path | Deskripsi |
|---|---|---|
| Training Orchestrator | `training/training_orchestrator.py` | Pipeline training utama: data loading, preprocessing, ensemble training, artifact packaging |
| Anomaly Model Trainer | `training/train_anomaly_model.py` | Training spesifik untuk model anomaly detection |
| Ensemble Engine | `models/ensemble_engine.py` | Ensemble decision logic (voting threshold ≥2/3) |
| Evaluation Engine | `models/evaluation_engine.py` | Cross-version benchmark: anomaly_delta, agreement_rate, regression detection |
| Correlation Impact Evaluator | `models/correlation_impact_evaluator.py` | Evaluasi dampak model terhadap incident & correlation behavior |
| Drift Robustness Evaluator | `models/drift_robustness_evaluator.py` | Drift simulation (0σ, 0.5σ, 1σ, 2σ) dan robustness scoring |
| Model Manager | `models/model_manager.py` | Model lifecycle management: load, switch, archive |
| Promotion Gatekeeper | `models/promotion_gatekeeper.py` | Decision engine: APPROVE/REVIEW/REJECT berdasarkan multi-layer evaluation |
| Model Registry | `registry/model_registry.py` | Version-controlled model registry dengan candidate management |
| Model Promotion | `registry/promote_model.py` | Promotion workflow dari candidate ke production |
| Feature Pipeline | `features/feature_pipeline.py` | Feature engineering: transformasi raw metrics ke fitur model |
| Drift Detector | `features/drift_detector.py` | Runtime drift detection untuk trigger retraining |
| Retrain Trigger | `automation/retrain_trigger.py` | Automated retrain scheduling berdasarkan drift detection dan cron |

---

## 10. Alignment Score

| Komponen | Alignment | Catatan |
|---|---|---|
| Pipeline Stages | 85% | Semua stages terwakili, minor gap di test split |
| Model Registry | 70% | File-based vs DB-backed spec |
| Evaluation Framework | 80% | Extended beyond spec dengan multi-layer evaluation |
| Promotion Governance | 90% | Exceeds spec dengan semi-automatic gatekeeper |
| Drift Monitoring | 85% | Progressive simulation lebih detail dari spec |
| Multi-Task Support | 75% | Addendum v1.2.0 menambahkan multi-profile, belum semua profile fully implemented |
| Reproducibility | 80% | Dataset hash & seed sudah ditambahkan, perlu git SHA integration |
| **Overall Alignment** | **~80%** | |

---

## 11. Changelog

| Date | Version | Author | Note |
|---|---|---|---|
| 2026-05-20 | 1.0 | DCIM AI Team | Initial release: sections 1-6 |
| 2026-05-20 | 1.2.0 | DCIM AI Team | Addendum: multi-task training profile, evaluation catalog, scheduled retraining, reproducibility |
| 2026-07-10 | 2.0 | Fakhri Aulia R | v2 restructure: YAML frontmatter, dcim-wiki alignment, actual code location, alignment score |
