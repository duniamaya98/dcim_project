import os
import json
import joblib
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.ensemble import IsolationForest
from datetime import datetime, UTC
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from dcim_ai.features.feature_pipeline import FeaturePipeline

def train_model():
    print("Starting baseline training...")
    
    # semua isi training kamu di sini
    


# =========================
# CONFIG
# =========================
WINDOW_INTERVAL = "30 days"
MODEL_VERSION_LEGACY = "v1.0_baseline"

DB_URL = "postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai"

ARTIFACTS_DIR = "dcim_ai/artifacts"
MODELS_DIR = os.path.join(ARTIFACTS_DIR, "models")
REGISTRY_DIR = "dcim_ai/registry"
REGISTRY_PATH = os.path.join(REGISTRY_DIR, "registry.json")

os.makedirs(ARTIFACTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(REGISTRY_DIR, exist_ok=True)

# =========================
# LOAD DATA FROM DB
# =========================
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

# =========================
# FEATURE PIPELINE
# =========================
pipeline = FeaturePipeline()
pipeline.fit(df)
X = pipeline.transform(df)

# =========================
# TRAIN MULTI-MODEL
# =========================

iso_model = IsolationForest(
    n_estimators=300,
    contamination=0.02,
    random_state=42
)

lof_model = LocalOutlierFactor(
    n_neighbors=20,
    contamination=0.02,
    novelty=True
)

svm_model = OneClassSVM(
    kernel="rbf",
    gamma="scale",
    nu=0.02
)

iso_model.fit(X)
lof_model.fit(X)
svm_model.fit(X)

models = {
    "isolation_forest": iso_model,
    "local_outlier_factor": lof_model,
    "one_class_svm": svm_model
}

# =========================
# SAVE LEGACY ARTIFACTS (Optional Backward Compatibility)
# =========================
legacy_model_path = os.path.join(
    ARTIFACTS_DIR,
    f"isolation_forest_{MODEL_VERSION_LEGACY}.pkl"
)

legacy_pipeline_path = os.path.join(
    ARTIFACTS_DIR,
    f"feature_pipeline_{MODEL_VERSION_LEGACY}.pkl"
)

joblib.dump(models, legacy_model_path)
pipeline.save(legacy_pipeline_path)

print("Legacy artifacts saved.")

# =========================
# SAVE BASELINE STATS
# =========================
baseline_stats = pipeline.get_baseline_stats()

legacy_stats_path = os.path.join(
    ARTIFACTS_DIR,
    f"feature_stats_{MODEL_VERSION_LEGACY}.json"
)

with open(legacy_stats_path, "w") as f:
    json.dump(baseline_stats, f, indent=4)

print("Baseline feature stats saved.")

# =========================
# VERSION MANAGEMENT
# =========================
def get_next_version():
    if not os.path.exists(REGISTRY_PATH):
        return "v1.0"

    if os.path.getsize(REGISTRY_PATH) == 0:
        return "v1.0"

    try:
        with open(REGISTRY_PATH, "r") as f:
            registry = json.load(f)
    except json.JSONDecodeError:
        return "v1.0"

    versions = registry.get("available_models", [])
    if not versions:
        return "v1.0"

    latest = sorted(versions)[-1]
    major, minor = latest.replace("v", "").split(".")
    return f"v{major}.{int(minor)+1}"


version = get_next_version()
model_dir = os.path.join(MODELS_DIR, version)
os.makedirs(model_dir, exist_ok=True)

# =========================
# SAVE VERSIONED ARTIFACTS
# =========================
joblib.dump(models, os.path.join(model_dir, "models.pkl"))
joblib.dump(pipeline, os.path.join(model_dir, "pipeline.pkl"))

with open(os.path.join(model_dir, "baseline_stats.json"), "w") as f:
    json.dump(baseline_stats, f, indent=4)

# =========================
# TRAINING ANOMALY RATIO (ENSEMBLE)
# =========================

iso_pred = iso_model.predict(X)
lof_pred = lof_model.predict(X)
svm_pred = svm_model.predict(X)

votes = (
    (iso_pred == -1).astype(int) +
    (lof_pred == -1).astype(int) +
    (svm_pred == -1).astype(int)
)

ensemble_pred = np.where(votes >= 2, -1, 1)

training_anomaly_ratio = float(np.mean(ensemble_pred == -1))

metadata = {
    "version": version,
    "created_at": datetime.now(UTC).isoformat(),
    "algorithm": "Ensemble(IForest+LOF+OCSVM)",
    "models": {
        "isolation_forest": {
            "n_estimators": iso_model.n_estimators,
            "contamination": iso_model.contamination
        },
        "local_outlier_factor": {
            "n_neighbors": lof_model.n_neighbors,
            "contamination": lof_model.contamination
        },
        "one_class_svm": {
            "kernel": svm_model.kernel,
            "nu": svm_model.nu
        }
    },
    "training_samples": len(X),
    "training_anomaly_ratio": training_anomaly_ratio,
    "feature_columns": pipeline.feature_columns,
    "baseline_mean": baseline_stats["mean"],
    "baseline_std": baseline_stats["std"],
    "status": "staging"
}


with open(os.path.join(model_dir, "metadata.json"), "w") as f:
    json.dump(metadata, f, indent=4)

print(f"Versioned model saved to {model_dir}")

# =========================
# UPDATE REGISTRY
# =========================
if os.path.exists(REGISTRY_PATH) and os.path.getsize(REGISTRY_PATH) > 0:
    with open(REGISTRY_PATH, "r") as f:
        registry = json.load(f)
else:
    registry = {
        "current_production": None,
        "available_models": []
    }

if version not in registry["available_models"]:
    registry["available_models"].append(version)

if registry["current_production"] is None:
    registry["current_production"] = version

with open(REGISTRY_PATH, "w") as f:
    json.dump(registry, f, indent=4)

print("Model registry updated.")
print("Training anomaly ratio:", training_anomaly_ratio)
print("Baseline training completed successfully.")

if __name__ == "__main__":
    train_model()