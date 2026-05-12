# (MT-021) Model Training & Evaluation Lifecycle Engine Configuration Documentation

# 1. Training Orchestrator Configuration

## Objective

Menyediakan pipeline training terstandarisasi untuk:

* Melatih model anomaly detection
* Menghasilkan artifact model versioned
* Menyimpan metadata training
* Mengintegrasikan model ke registry sebagai candidate

Training tidak langsung mengaktifkan model ke production.

## Training Command

Training dijalankan menggunakan CLI command:

```shellscript
python -m dcim_ai.training.training_orchestrator \
    --version v1.13 \
    --window all \
    --auto-register
```

Parameter:

| Parameter       | Penjelasan                                    |
| --------------- | --------------------------------------------- |
| `version`       | Versi model yang akan dibuat                  |
| `window`        | Dataset training window                       |
| `auto-register` | Otomatis mendaftarkan model sebagai candidate |

## Training Pipeline Flow

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

## Training Orchestrator Code

File:

`dcim_ai/training/training_orchestrator.py`

Contoh implementasi utama:

```
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



***

# 2. Artifact Storage Configuration

## Objective

Menstandarisasi struktur penyimpanan artifact model agar:

* mudah dilacak
* version-controlled
* rollback-safe

## Artifact Directory Structure

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

## Artifact Save Code

```python
artifact_path = f"dcim_ai/artifacts/models/{self.version}"

joblib.dump(models["isolation_forest"], f"{artifact_path}/isolation_forest.pkl")
joblib.dump(models["lof"], f"{artifact_path}/lof.pkl")
joblib.dump(models["ocsvm"], f"{artifact_path}/ocsvm.pkl")

joblib.dump(self.pipeline.scaler, f"{artifact_path}/scaler.pkl")

with open(f"{artifact_path}/feature_columns.json", "w") as f:
    json.dump(feature_columns, f)
```

## Metadata Structure

File:

`metadata.json`

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



***

# 3. Cross-Version Evaluation Configuration

## Objective

Membandingkan model candidate dengan model production aktif.

Digunakan untuk mendeteksi regression sebelum deployment.

## Evaluation Command

```python
from dcim_ai.models.evaluation_engine import CrossVersionEvaluationEngine

engine = CrossVersionEvaluationEngine(
    candidate_version="v1.13",
    window="all"
)

report = engine.evaluate()
```

## Evaluation Engine Code

File:

dcim\_ai/models/evaluation\_engine.py

Core logic:

```python
candidate_preds = candidate_model.predict(X)
production_preds = production_model.predict(X)

candidate_ratio = np.mean(candidate_preds == -1)
production_ratio = np.mean(production_preds == -1)

agreement = np.mean(candidate_preds == production_preds)

anomaly_delta = candidate_ratio - production_ratio
```

## Output Report

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



***

# 4. Correlation Impact Evaluation Configuration

## Objective

Mengukur dampak model terhadap sistem incident dan correlation.

## Evaluation Command

```python
from dcim_ai.models.correlation_impact_evaluator import CorrelationImpactEvaluator

evaluator = CorrelationImpactEvaluator(
    candidate_version="v1.13",
    window="all"
)

report = evaluator.evaluate()
```

## Simulation Flow

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

## Core Simulation Code

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

## Output Metrics

```json
{
 "candidate_incident_count": 536,
 "production_incident_count": 514,
 "incident_delta": 22,
 "candidate_multi_domain_ratio": 0.026,
 "production_multi_domain_ratio": 1.0
}
```



***

# 5. Drift Robustness Evaluation Configuration

## Objective

Menguji ketahanan model terhadap distribution shift.

## Evaluation Command

```python
from dcim_ai.models.drift_robustness_evaluator import DriftRobustnessEvaluator

drift_eval = DriftRobustnessEvaluator(
    "v1.13",
    window="all"
)

print(drift_eval.evaluate())
```

## Drift Simulation Code

```python
baseline_std = np.std(X, axis=0)

for drift_level in [0, 0.5, 1, 2]:

    X_drifted = X.copy()

    n_features = X.shape[1]
    drift_features = int(0.3 * n_features)

    for f in range(drift_features):
        X_drifted[:, f] += drift_level * baseline_std[f]
```

## Drift Evaluation Logic

```python
preds = []

for model in models.values():
    p = model.predict(X_drifted)
    preds.append(p)

preds = np.array(preds)

ensemble_vote = np.mean(preds == -1, axis=0)

anomaly_ratio = np.mean(ensemble_vote > 0.66)
```

## Output Example

```json
{
 "drift_level_0": 0.012,
 "drift_level_0.5": 0.038,
 "drift_level_1": 0.571,
 "drift_level_2": 0.984,
 "drift_sensitivity": 0.972
}
```



***

# 6. Promotion Gatekeeper Configuration

## Objective

Menggabungkan semua evaluasi untuk menghasilkan keputusan promotion.

## Gate Execution

```python
from dcim_ai.models.promotion_gatekeeper import PromotionGatekeeper

gate = PromotionGatekeeper("v1.13", window="all")

report = gate.evaluate()
```

## Gate Decision Logic

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

## Output Example

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



***

# Final System Configuration Summary

MT-021 menambahkan layer lifecycle governance pada sistem AI monitoring:

| Layer                    | Function                     |
| ------------------------ | ---------------------------- |
| Training Orchestrator    | Visioned model training      |
| Artifact Manager         | Model artifact storage       |
| Cross-Version Evaluation | Regression detection         |
| Correlation Impact       | Incident behavior validation |
| Drift Robustness         | Distributiob shift testing   |
| Promotion Gatekeeper     | Governance decision engine   |

Sistem kini:

* Version-controlled
* Drift-aware
* Incident-aware
* Regression-safe
* Governance-controlled

Model deployment tidak lagi bersifat manual, tetapi berbasis evaluasi multi-layer yang terstruktur.



***

