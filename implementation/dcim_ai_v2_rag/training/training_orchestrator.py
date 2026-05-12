import os
import json
import argparse
import joblib
import numpy as np
from datetime import datetime, timezone

from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

from dcim_ai.core.data_loader import load_training_data
from dcim_ai.registry.model_registry import register_model


class TrainingOrchestrator:
    def __init__(self, version: str, window: str = "all", auto_register: bool = False):
        self.version = version
        self.window = window
        self.auto_register = auto_register

        self.artifact_path = f"dcim_ai/artifacts/models/{version}"
        os.makedirs(self.artifact_path, exist_ok=True)

        self.models = {}
        self.scaler = None

    # ------------------------------------------------
    # 1. Load Data
    # ------------------------------------------------
    def load_data(self):
        print("[INFO] Loading training data...")
        return load_training_data(window=self.window)

    # ------------------------------------------------
    # 2. Preprocess + Split
    # ------------------------------------------------
    def preprocess(self, df):
        print("[INFO] Preparing training features...")

        feature_columns = list(df.columns)

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(df)

        X_train, X_val = train_test_split(
            X_scaled,
            test_size=0.2,
            random_state=42,
            shuffle=True
        )

        self.scaler = scaler

        return X_train, X_val, feature_columns

    # ------------------------------------------------
    # 3. Train Models
    # ------------------------------------------------
    def train_models(self, X_train):
        print("[INFO] Training Isolation Forest...")
        iso = IsolationForest(
            n_estimators=200,
            contamination=0.02,
            random_state=42
        )
        iso.fit(X_train)

        print("[INFO] Training LOF...")
        lof = LocalOutlierFactor(
            n_neighbors=20,
            contamination=0.02,
            novelty=True
        )
        lof.fit(X_train)

        print("[INFO] Training One-Class SVM...")
        ocsvm = OneClassSVM(
            kernel="rbf",
            gamma="scale",
            nu=0.02
        )
        ocsvm.fit(X_train)

        self.models = {
            "isolation_forest": iso,
            "lof": lof,
            "ocsvm": ocsvm
        }

    # ------------------------------------------------
    # 4. Validation Evaluation
    # ------------------------------------------------
    def evaluate_validation(self, X_val):
        print("[INFO] Evaluating on validation set...")

        preds = []
        for model in self.models.values():
            p = model.predict(X_val)
            preds.append(p)

        preds = np.array(preds)
        ensemble_vote = np.mean(preds == -1, axis=0)

        anomaly_ratio_val = float(np.mean(ensemble_vote > 0.66))

        return anomaly_ratio_val

    # ------------------------------------------------
    # 5. Drift Baseline
    # ------------------------------------------------
    def compute_drift_baseline(self, X_train):
        baseline_mean = X_train.mean(axis=0).tolist()
        baseline_std = X_train.std(axis=0).tolist()
        return baseline_mean, baseline_std

    # ------------------------------------------------
    # 6. Save Artifacts
    # ------------------------------------------------
    def save_artifacts(self, feature_columns):
        print("[INFO] Saving model artifacts...")

        for name, model in self.models.items():
            joblib.dump(model, f"{self.artifact_path}/{name}.pkl")

        joblib.dump(self.scaler, f"{self.artifact_path}/scaler.pkl")

        with open(f"{self.artifact_path}/feature_columns.json", "w") as f:
            json.dump(feature_columns, f, indent=4)

        ensemble_config = {
            "strategy": "majority_vote",
            "models": list(self.models.keys()),
            "threshold": 0.5
        }

        with open(f"{self.artifact_path}/ensemble_config.json", "w") as f:
            json.dump(ensemble_config, f, indent=4)

    # ------------------------------------------------
    # 7. Generate Metadata
    # ------------------------------------------------
    def generate_metadata(
        self,
        feature_columns,
        anomaly_ratio_val,
        baseline_mean,
        baseline_std,
        dataset_size
    ):
        print("[INFO] Generating metadata...")

        metadata = {
            "version": self.version,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "training_window": self.window,
            "models": list(self.models.keys()),
            "ensemble_strategy": "majority_vote",
            "anomaly_ratio_validation": anomaly_ratio_val,
            "dataset_size": dataset_size,
            "feature_count": len(feature_columns),
            "drift_baseline_mean": baseline_mean,
            "drift_baseline_std": baseline_std,
            "registry_status": "candidate"
        }

        with open(f"{self.artifact_path}/metadata.json", "w") as f:
            json.dump(metadata, f, indent=4)

        return metadata

    # ------------------------------------------------
    # 8. Safety Guard + Registry
    # ------------------------------------------------
    def register_candidate(self, anomaly_ratio_val, metadata):
        if not self.auto_register:
            return

        print("[INFO] Running safety guard checks...")

        if anomaly_ratio_val < 0.01 or anomaly_ratio_val > 0.20:
            raise ValueError(
                f"Anomaly ratio {anomaly_ratio_val:.4f} outside safe bounds."
            )

        print("[INFO] Registering model in DB as candidate...")

        register_model(
            model_name="anomaly_ensemble",
            version=self.version,
            contamination=0.05,
            training_window=self.window,
            artifact_path=self.artifact_path,
            metrics=metadata
        )

    # ------------------------------------------------
    # MAIN RUN
    # ------------------------------------------------
    def run(self):
        df = self.load_data()
        X_train, X_val, feature_columns = self.preprocess(df)

        self.train_models(X_train)

        anomaly_ratio_val = self.evaluate_validation(X_val)
        baseline_mean, baseline_std = self.compute_drift_baseline(X_train)

        self.save_artifacts(feature_columns)

        metadata = self.generate_metadata(
            feature_columns,
            anomaly_ratio_val,
            baseline_mean,
            baseline_std,
            dataset_size=df.shape[0]
        )

        self.register_candidate(anomaly_ratio_val, metadata)

        print(f"[SUCCESS] Training completed for version {self.version}")


# CLI ENTRYPOINT
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--window", default="all")
    parser.add_argument("--auto-register", action="store_true")

    args = parser.parse_args()

    orchestrator = TrainingOrchestrator(
        version=args.version,
        window=args.window,
        auto_register=args.auto_register
    )
    orchestrator.run()