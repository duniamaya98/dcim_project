---
title: "MT-021 Model Training & Evaluation Lifecycle Engine Configuration Documentation"
created: 2026-05-20
updated: 2026-07-10
version: 2.0
type: configuration-documentation
task_id: MT-021
block: 7
assignee: Fakhri Aulia R
status: done
dcim_wiki_section: "block7-analytics-ai-engine.md — Section 8: Model Training Pipeline"
tags:
  - configuration
  - model-training
  - evaluation-engine
  - promotion-gatekeeper
  - drift-robustness
  - artifact-storage
  - model-registry
  - ml-ops
  - block7
---

# (MT-021) Model Training & Evaluation Lifecycle Engine Configuration Documentation

> **Versi:** 2.0  
> **Status:** Done  
> **Assignee:** Fakhri Aulia R  
> **Block:** 7 — Analytics & AI Engine  
> **dcim-wiki Alignment:** Section 8: Model Training Pipeline

---

## Daftar Isi

1. [Training Orchestrator Configuration](#1-training-orchestrator-configuration)
2. [Artifact Storage Configuration](#2-artifact-storage-configuration)
3. [Cross-Version Evaluation Configuration](#3-cross-version-evaluation-configuration)
4. [Correlation Impact Evaluation Configuration](#4-correlation-impact-evaluation-configuration)
5. [Drift Robustness Evaluation Configuration](#5-drift-robustness-evaluation-configuration)
6. [Promotion Gatekeeper Configuration](#6-promotion-gatekeeper-configuration)
7. [System Configuration Summary](#7-system-configuration-summary)
8. [dcim-wiki Alignment](#8-dcim-wiki-alignment)
9. [Actual Code Location](#9-actual-code-location)
10. [Alignment Score](#10-alignment-score)
11. [Changelog](#11-changelog)

---

## Referensi

- **dcim-wiki:** [block7-analytics-ai-engine.md — Section 8](../../dcim-wiki/reference-designs/block7-analytics-ai-engine.md#8-model-training-pipeline)
- **Main Doc:** [v2_(MT-021) Model Training & Evaluation Lifecycle Engine](./v2_(MT-021)%20Model%20Training%20&%20Evaluation%20Lifecycle%20Engine.md)

---

## 1. Training Orchestrator Configuration

### 1.1 Objective

Menyediakan pipeline training terstandarisasi untuk:

* Melatih model anomaly detection
* Menghasilkan artifact model versioned
* Menyimpan metadata training
* Mengintegrasikan model ke registry sebagai candidate

Training tidak langsung mengaktifkan model ke production.

### 1.2 Training Command

Training dijalankan menggunakan CLI command:

```shellscript
python -m dcim_ai.training.training_orchestrator \
    --version v1.13 \
    --window all \
    --auto-register
```

**Parameter:**

| Parameter | Penjelasan |
|---|---|
| `version` | Versi model yang akan dibuat |
| `window` | Dataset training window |
| `auto-register` | Otomatis mendaftarkan model sebagai candidate |

### 1.3 Training Pipeline Flow

```
Database Dataset
        ↓
Data Loader
        ↓
Feature Pipeline
        ↓
Train / Validation Split
        ↓
Model Training
        ↓
Validation Metrics
        ↓
Artifact Packaging
        ↓
Candidate Registration
```

### 1.4 Training Orchestrator Code

**File:**

`dcim_ai/training/training_orchestrator.py`

Contoh implementasi utama:

```python
class TrainingOrchestrator:

    def __init__(self, version, window):
        self.version = version
        self.window = window
        self.pipeline = FeaturePipeline()

    def load_data(self):
        df = load_training_data(window=self.window)
        return df

    def preprocess(self, df):
        X = self.pipeline.transform(df)
        feature_columns = self.pipeline.feature_columns
        return X, feature_columns

    def train_models(self, X):

        models = {}

        models["isolation_forest"] = IsolationForest(
            n_estimators=200,
            contamination=0.02,
            random_state=42
        ).fit(X)

        models["lof"] = LocalOutlierFactor(
            novelty=True,
            contamination=0.02
        ).fit(X)

        models["ocsvm"] = OneClassSVM(
            nu=0.02,
            kernel="rbf",
            gamma="scale"
        ).fit(X)

        return models
```

---

## 2. Artifact Storage Configuration

### 2.1 Objective

Menstandarisasi struktur penyimpanan artifact model agar:

* mudah dilacak
* version-controlled
* rollback-safe

### 2.2 Artifact Directory Structure

```
dcim_ai/artifacts/models/

v1.13/
 ├── isolation_forest.pkl
 ├── lof.pkl
 ├── ocsvm.pkl
 ├── scaler.pkl
 ├── feature_columns.json
 └── metadata.json
```

### 2.3 Artifact Save Code

```python
artifact_path = f"dcim_ai/artifacts/models/{self.version}"

joblib.dump(models["isolation_forest"], f"{artifact_path}/isolation_forest.pkl")
joblib.dump(models["lof"], f"{artifact_path}/lof.pkl")
joblib.dump(models["ocsvm"], f"{artifact_path}/ocsvm.pkl")

joblib.dump(self.pipeline.scaler, f"{artifact_path}/scaler.pkl")

with open(f"{artifact_path}/feature_columns.json", "w") as f:
    json.dump(feature_columns, f)
```

### 2.4 Metadata Structure

**File:** `metadata.json`

Contoh isi metadata:

```json
{
  "version": "v1.13",
  "training_window": "all",
  "validation_anomaly_ratio": 0.012,
  "drift_baseline_mean": [...],
  "drift_baseline_std": [...],
  "created_at": "2026-03-10T08:14:22"
}
```

**Extended metadata (v1.2.0+):**

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
  "training_window": "rolling_7d",
  "validation_anomaly_ratio": 0.015,
  "drift_baseline_mean": [...],
  "drift_baseline_std": [...],
  "created_at": "2026-05-20T02:00:00"
}
```

---

## 3. Cross-Version Evaluation Configuration

### 3.1 Objective

Membandingkan model candidate dengan model production aktif.

Digunakan untuk mendeteksi regression sebelum deployment.

### 3.2 Evaluation Command

```python
from dcim_ai.models.evaluation_engine import CrossVersionEvaluationEngine

engine = CrossVersionEvaluationEngine(
    candidate_version="v1.13",
    window="all"
)

report = engine.evaluate()
```

### 3.3 Evaluation Engine Code

**File:** `dcim_ai/models/evaluation_engine.py`

Core logic:

```python
candidate_preds = candidate_model.predict(X)
production_preds = production_model.predict(X)

candidate_ratio = np.mean(candidate_preds == -1)
production_ratio = np.mean(production_preds == -1)

agreement = np.mean(candidate_preds == production_preds)

anomaly_delta = candidate_ratio - production_ratio
```

### 3.4 Output Report

```json
{
 "candidate_version": "v1.13",
 "candidate_anomaly_ratio": 0.0277,
 "production_anomaly_ratio": 0.0265,
 "anomaly_delta": 0.0011,
 "agreement_rate": 0.996,
 "dataset_size": 19347
}
```

---

## 4. Correlation Impact Evaluation Configuration

### 4.1 Objective

Mengukur dampak model terhadap sistem incident dan correlation.

### 4.2 Evaluation Command

```python
from dcim_ai.models.correlation_impact_evaluator import CorrelationImpactEvaluator

evaluator = CorrelationImpactEvaluator(
    candidate_version="v1.13",
    window="all"
)

report = evaluator.evaluate()
```

### 4.3 Simulation Flow

```
Dataset
    ↓
Model Prediction
    ↓
Domain Engine
    ↓
Correlation Engine
    ↓
Incident Simulation
```

### 4.4 Core Simulation Code

```python
for row in df.itertuples():

    prediction = model.predict(features)

    domain_state = domain_engine.process(features)

    incident = correlation_engine.build_incident(
        prediction,
        domain_state
    )

    incidents.append(incident)
```

### 4.5 Output Metrics

```json
{
 "candidate_incident_count": 536,
 "production_incident_count": 514,
 "incident_delta": 22,
 "candidate_multi_domain_ratio": 0.026,
 "production_multi_domain_ratio": 1.0
}
```

---

## 5. Drift Robustness Evaluation Configuration

### 5.1 Objective

Menguji ketahanan model terhadap distribution shift.

### 5.2 Evaluation Command

```python
from dcim_ai.models.drift_robustness_evaluator import DriftRobustnessEvaluator

drift_eval = DriftRobustnessEvaluator(
    "v1.13",
    window="all"
)

print(drift_eval.evaluate())
```

### 5.3 Drift Simulation Code

```python
baseline_std = np.std(X, axis=0)

for drift_level in [0, 0.5, 1, 2]:

    X_drifted = X.copy()

    n_features = X.shape[1]
    drift_features = int(0.3 * n_features)

    for f in range(drift_features):
        X_drifted[:, f] += drift_level * baseline_std[f]
```

### 5.4 Drift Evaluation Logic

```python
preds = []

for model in models.values():
    p = model.predict(X_drifted)
    preds.append(p)

preds = np.array(preds)

ensemble_vote = np.mean(preds == -1, axis=0)

anomaly_ratio = np.mean(ensemble_vote > 0.66)
```

### 5.5 Output Example

```json
{
 "drift_level_0": 0.012,
 "drift_level_0.5": 0.038,
 "drift_level_1": 0.571,
 "drift_level_2": 0.984,
 "drift_sensitivity": 0.972
}
```

---

## 6. Promotion Gatekeeper Configuration

### 6.1 Objective

Menggabungkan semua evaluasi untuk menghasilkan keputusan promotion.

### 6.2 Gate Execution

```python
from dcim_ai.models.promotion_gatekeeper import PromotionGatekeeper

gate = PromotionGatekeeper("v1.13", window="all")

report = gate.evaluate()
```

### 6.3 Gate Decision Logic

```python
if anomaly_safe and correlation_safe and drift_safe:
    recommendation = "APPROVE"
    risk_level = "LOW"

elif anomaly_safe and drift_safe:
    recommendation = "REVIEW"
    risk_level = "MEDIUM"

else:
    recommendation = "REJECT"
    risk_level = "HIGH"
```

### 6.4 Output Example

```json
{
 "candidate_version": "v1.13",
 "anomaly_safe": true,
 "correlation_safe": false,
 "drift_safe": true,
 "promotion_recommendation": "REVIEW",
 "risk_level": "MEDIUM"
}
```

### 6.5 Extended Gate per Profile (v1.2.0+)

Untuk profil non-anomaly, tambahan gate tersedia:

```python
# Forecast profile gates
mape_safe = candidate_mape <= production_mape * 1.1
coverage_safe = coverage_95 >= 0.9

# Forecast advanced profile gates
failure_recall_safe = failure_recall_24h >= 0.7
failure_precision_safe = failure_precision_24h >= 0.6

# Clustering profile gates
silhouette_safe = silhouette >= 0.3

# Energy anomaly profile gates
latency_safe = detection_latency_p95 <= 900  # 15 menit dalam detik
fpr_safe = false_positive_rate <= 0.1
```

---

## 7. System Configuration Summary

### 7.1 Layer Architecture

MT-021 menambahkan layer lifecycle governance pada sistem AI monitoring:

| Layer | Function | File |
|---|--- |---|
| Training Orchestrator | Versioned model training | `training/training_orchestrator.py` |
| Artifact Manager | Model artifact storage | `artifacts/models/` |
| Cross-Version Evaluation | Regression detection | `models/evaluation_engine.py` |
| Correlation Impact | Incident behavior validation | `models/correlation_impact_evaluator.py` |
| Drift Robustness | Distribution shift testing | `models/drift_robustness_evaluator.py` |
| Promotion Gatekeeper | Governance decision engine | `models/promotion_gatekeeper.py` |

### 7.2 Capabilities

Sistem kini:

* **Version-controlled** — Setiap model teridentifikasi versi dan metadata lengkap
* **Drift-aware** — Baseline statistik tersimpan, progressive drift simulation tersedia
* **Incident-aware** — Dampak model terhadap incident dan correlation terukur
* **Regression-safe** — Cross-version benchmark mendeteksi regression sebelum deployment
* **Governance-controlled** — Promotion berbasis evaluasi multi-layer, bukan manual

Model deployment tidak lagi bersifat manual, tetapi berbasis evaluasi multi-layer yang terstruktur.

### 7.3 Multi-Task Training Profiles (v1.2.0+)

| Profil | Algoritma | Window | Eval Metrics |
|---|---|---|---|
| `anomaly` | IF + LOF + OCSVM | 30m rolling | anomaly_delta, agreement_rate |
| `forecast` | XGBoost / Prophet | 30d + lag | MAPE, RMSE, coverage_95 |
| `forecast_advanced` | LSTM / TFT | 90d sequence | MAPE, failure_recall_24h, failure_precision_24h |
| `clustering` | KMeans + Silhouette | 90d aggregate | silhouette, inertia, davies_bouldin |
| `energy_anomaly` | IF + Z-score | 7d streaming | detection_latency_p95, false_positive_rate |

### 7.4 Scheduled Retraining

| Profil | Cron | Trigger Drift |
|---|---|---|
| `anomaly` | `*/30 * * * *` (30 menit) | ✅ |
| `forecast` | `0 2 * * *` (harian) | ✅ |
| `forecast_advanced` | `0 3 * * 0` (mingguan) | ✅ |
| `clustering` | `0 4 * * 0` (mingguan) | ⚠️ PSI-based |
| `energy_anomaly` | `0 1 * * *` (harian) | ✅ |

---

## 8. dcim-wiki Alignment

### 8.1 Mapping ke dcim-wiki Section 8: Model Training Pipeline

Konfigurasi MT-021 ter-mapping ke **Section 8** pada `block7-analytics-ai-engine.md`:

| dcim-wiki Section 8 | MT-021 Config Component | Alignment | Catatan |
|---|---|---|---|
| **8.1 — Data Collection** | `TrainingOrchestrator.load_data()` | ✅ Aligned | Query database berdasarkan time-window |
| **8.1 — Feature Engineering** | `FeaturePipeline.transform()` | ✅ Aligned | Feature columns tersimpan di artifact |
| **8.1 — Data Splitting** | Train/validation split | ⚠️ Partial | Spec: 70/15/15. Actual: train/val only |
| **8.1 — Model Training** | `TrainingOrchestrator.train_models()` | ✅ Aligned | Ensemble: IF + LOF + OCSVM |
| **8.1 — Evaluation** | `CrossVersionEvaluationEngine` | ✅ Aligned (Extended) | Ditambah multi-layer evaluation |
| **8.1 — Model Registry** | `model_registry.py` + auto-register | ✅ Aligned | File-based artifact registry |
| **8.1 — Deployment** | `PromotionGatekeeper` | ✅ Aligned (Extended) | Semi-automatic governance |
| **8.1 — A/B Testing** | Cross-version benchmark | ⚠️ Partial | Pre-deployment comparative eval |
| **8.1 — Monitoring** | `DriftRobustnessEvaluator` + `drift_detector.py` | ✅ Aligned | Progressive drift simulation |
| **8.2 — Model Registry Schema** | `metadata.json` per artifact | ⚠️ Partial | File-based vs SQL spec |

### 8.2 Gap Summary

| Gap | Impact | Rekomendasi |
|---|---|---|
| Test split missing | Low | Tambahkan explicit test split parameter |
| File-based registry | Medium | Pertimbangkan DB-backed registry |
| Standard ML metrics | Low | Tambahkan accuracy/precision/recall/F1 |
| Real-time A/B | Low | Document approach difference |

---

## 9. Actual Code Location

| Komponen | File Path | Fungsi Utama |
|---|---|---|
| Training Orchestrator | `training/training_orchestrator.py` | Pipeline training: load, preprocess, train, package |
| Anomaly Model Trainer | `training/train_anomaly_model.py` | Training spesifik anomaly detection model |
| Ensemble Engine | `models/ensemble_engine.py` | Voting logic (≥2/3 threshold) |
| Evaluation Engine | `models/evaluation_engine.py` | Cross-version: anomaly_delta, agreement_rate |
| Correlation Impact Evaluator | `models/correlation_impact_evaluator.py` | Incident & correlation impact scoring |
| Drift Robustness Evaluator | `models/drift_robustness_evaluator.py` | Drift simulation & robustness scoring |
| Model Manager | `models/model_manager.py` | Load, switch, archive models |
| Promotion Gatekeeper | `models/promotion_gatekeeper.py` | APPROVE/REVIEW/REJECT decision logic |
| Model Registry | `registry/model_registry.py` | Version-controlled model registry |
| Model Promotion | `registry/promote_model.py` | Candidate → production promotion workflow |
| Feature Pipeline | `features/feature_pipeline.py` | Feature engineering & transformation |
| Drift Detector | `features/drift_detector.py` | Runtime drift detection for retrain trigger |
| Retrain Trigger | `automation/retrain_trigger.py` | Scheduled & drift-based retrain automation |

---

## 10. Alignment Score

| Komponen | Alignment | Catatan |
|---|---|---|
| Training Orchestrator Config | 85% | CLI, parameter, pipeline flow sesuai spec |
| Artifact Storage | 80% | Structure aligned, metadata extended |
| Evaluation Engine Config | 80% | Core metrics aligned, extended dengan multi-layer |
| Correlation Impact Config | 85% | Simulation flow & metrics sesuai spec |
| Drift Robustness Config | 85% | Simulation levels & evaluation logic aligned |
| Promotion Gatekeeper Config | 90% | Decision logic exceeds spec dengan per-profile gates |
| Multi-Task Profiles | 75% | Config defined, implementation partial |
| Reproducibility Config | 80% | Dataset hash & seed added, git SHA pending |
| **Overall Alignment** | **~80%** | |

---

## 11. Changelog

| Date | Version | Author | Note |
|---|---|---|---|
| 2026-05-20 | 1.0 | DCIM AI Team | Initial configuration documentation |
| 2026-07-10 | 2.0 | Fakhri Aulia R | v2 restructure: YAML frontmatter, dcim-wiki alignment, actual code location, alignment score, extended metadata |
