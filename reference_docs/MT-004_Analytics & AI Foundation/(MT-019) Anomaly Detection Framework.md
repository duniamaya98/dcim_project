# (MT-019) Anomaly Detection Framework

# 1 . Architecture & Model Registry Foundation

## Objective

Membangun fondasi arsitektur AI monitoring yang versioned, modular, dan production-ready.

## Implemented Components

### Model Versioning System

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

### Model Registry

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

### Model Promotion System

Command:

```
python -m dcim_ai.registry.promote_model v1.4
```

Fitur:

* Safe production switching
* Version archival
* Metadata update

### Production Loader

File:

```
load_production_model.py
```

Fungsi:

* Load model bedasarkan registry
* Fail-safe loading
* Separation between training & inference

## Outcome

* Model lifecycle terkontrol
* No hardcoded model
* Production ready version management
* Clean seperation training vs inference



***

# 2 . Unified Feature Engineering & Drift Detection

## Objective

Standarisasi preprocessing dan deteksi perubahan distribusi data.

## Implemented Components

### Feature Pipeline

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

### Baseline Feature Statistics

Setiap model menyimpan:

```json
{
  "mean": [...],
  "std": [...]
}
```

Digunakan untuk drift detection.

### Drift Detection Engine

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

### Drift Behavior

Contoh hasil:

```json
{
  "drift_score": 329.37,
  "drift_status": "severe_drift"
}
```

## Outcome

* Feature standardization konsisten
* Model aware terhadap data distribution shift
* Drift-aware retraining trigger



***

# 3 . Multi-Model & Ensemble Detection Engine

## Objective

Mengurangi false positive & meningkatkan robustness dengan ensemble learning.

## Implemented Models

* Isolation Forest
  * Tree-based isolation
* Local Outlier Factor
  * Density-based anomaly detection
  * Cocok untuk local cluster detection
* One-Class SVM
  * Boundary-based classification.
  * Cocok untuk margin-based detection.

## Ensemble Strategy

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

## Example Output

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

## Outcome

* False positive reduction
* Robust detection
* Interpretable vote breakdown
* Scalable model expansion



***

# 4 . Real-Time Inference & Intelligent Alert Layer

## Objective

Menyediakan real-time AI monitoring API dengan alert intelligence.

## FastAPI Inference Service

Endpoint:

```
POST /predict
GET /
GET /metrics
```

## Intelligent Alert System

Fitur:

* Saverity grading
* Alert cooldown (anti-spam)
* Alert threshold logic
* Drift-based escalation

## Example Behavior

| **Condition**    | **Output**    |
| ---------------- | ------------- |
| Slight deviation | weak\_signal  |
| Strong anomaly   | warning       |
| Extreme anomaly  | critical      |
| Data shift       | severe\_drift |

## Outcome

* Real-time decision engine
* Smart alerting
* Noise reduction
* API production ready



***

# 5 . Automation, Monitoring & Resilience System

## Objective

Membuat sistem self-healing, observable, dan production resilient.

## Automation

### Auto Retraining

Trigger ketika:

```
drift_status == severe_drift
```

Dengan cooldown protection.

## Safe Retrain Worker

* Background thread
* Exeption-safe wrapper
* Non-blocking Inference

## Hot Model Reload

File:

```
model_manager.py
```

Fitur:

* Watch registry.json
* Auto reload production model
* No API restart required
* Thread-safe locking

## Prometheus Monitoring

Metrics:

* dcim\_requests\_total
* dcim\_anomalies\_total
* dcim\_normals\_total
* dcim\_retrain\_total
* dcim\_inference\_latency\_seconds

## Resilience Features

* Cooldown retrain protection
* Alert anti-spam
* Thread-safe model swap
* Safe fallback handling
* Versioned deployment

## Outcome

* Self-healing AI Monitoring
* Observable metrics
* Production-safe hot swap
* Controlled automation



***

