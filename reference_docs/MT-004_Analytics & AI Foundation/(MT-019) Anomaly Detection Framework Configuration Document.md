# (MT-019) Anomaly Detection Framework Configuration Document

# 1. System Overview

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

Arsitektur ini dirancang untuk production-ready AI monitoring system. [(MT-019) Anomaly Detection Framework](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep)



***

# 2. System Architecture

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



***

# 3. Project Directory Structure

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



***

# 4. Model Artifact Structure

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



***

# 5. Model Registry Configuration

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



***

# 6. Feature Pipeline Configuration

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



***

# 7. Drift Detection Configuration

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

```python
import numpy as np

def calculate_drift_score(values, mean, std):

    z_scores = (values - mean) / std
    drift_score = float(np.mean(np.abs(z_scores)))

    return drift_score, z_scores
```



***

# 8. Multi-Model Ensemble Configuration

Framework menggunakan 3 model.

Isolation Forest

```python
IsolationForest(
    n_estimators=300,
    contamination=0.02,
    random_state=42
)
```

Local Outlier Factor

```python
IsolationForest(
    n_estimators=300,
    contamination=0.02,
    random_state=42
)
```

One-Class SVM

```python
OneClassSVM(
    kernel="rbf",
    nu=0.02
)
```



***

# 9. Ensemble Voting Logic

Voting strategy:

```
>=2 anomaly votes → anomaly
<2 anomaly votes → normal
```

Saverity classification:

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



***

# 10. Inference API Configuration

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



***

# 11. Automation Configuration

Retraining otomatis terjadi ketika:

`drift_status == severe_drift`

Dengan cooldown:

`RETRAIN_COOLDONW = 30`

Contoh implementasi:

```python
if drift_status == "severe_drift":
    threading.Thread(target=trigger_retraining).start()
```



***

# 12. Monitor Configuration

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



***

# 13. Model Manager (Hot Reload)

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



***

# 14. Resilience Features

Framework memiliki fitur production safety:

* alert cooldown
* retrain cooldown
* thread-safe model reload
* background retrain worker
* version rollback

Ini memastikan sistem tetap stabil saat running.



***

# 15. Final System Capabilities

MT-019 menghasilkan sistem dengan kemampuan:

* multi-model anomaly detection
* drift-aware monitoring
* real-time inference API
* automatic retraining
* production model registry
* monitoring via Prometheus
* hot model reload

Semua subsystem telah mencapai status production ready. [(MT-019) Anomaly Detection Framework](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep)
