import joblib
import numpy as np
from dcim_ai.features.feature_pipeline import FeaturePipeline
from dcim_ai.features.drift_detector import DriftDetector
from dcim_ai.config.domain_mapping import DOMAIN_FEATURE_MAP
from dcim_ai.core.correlation_rules import evaluate_basic_rules
from dcim_ai.correlation.correlation_buffer import CorrelationBuffer


class AnomalyService:

    def __init__(self,
                 model_path,
                 pipeline_path,
                 baseline_stats_path):

        self.models = joblib.load(model_path)
        self.pipeline = FeaturePipeline.load(pipeline_path)
        self.drift_detector = DriftDetector(baseline_stats_path)
        self.correlation_buffer = CorrelationBuffer(window_seconds=300)

        print("AnomalyService initialized.")

    def predict(self, df_live):

        # =========================
        # 1️⃣ Data Cleaning
        # =========================
        df_clean = self.pipeline._clean_dataframe(df_live)
        df_clean = df_clean[self.pipeline.feature_columns]

        X_raw = df_clean.values

        # =========================
        # 2️⃣ Drift Detection
        # =========================
        drift_result = self.drift_detector.check_drift(X_raw)
        z_scores = drift_result["z_scores"]

        if drift_result["drift_detected"]:
            if max(z_scores) > 5.0:
                drift_level = "severe_drift"
            else:
                drift_level = "moderate_drift"
        else:
            drift_level = "stable"

        # =========================
        # 3️⃣ Scaling
        # =========================
        X_scaled = self.pipeline.scaler.transform(X_raw)

        # =========================
        # 4️⃣ Multi-model Voting
        # =========================
        iso_model = self.models["isolation_forest"]
        lof_model = self.models["local_outlier_factor"]
        svm_model = self.models["one_class_svm"]

        iso_pred = iso_model.predict(X_scaled)
        lof_pred = lof_model.predict(X_scaled)
        svm_pred = svm_model.predict(X_scaled)

        votes = (
            (iso_pred == -1).astype(int)
            + (lof_pred == -1).astype(int)
            + (svm_pred == -1).astype(int)
        )

        predictions = np.where(votes >= 2, -1, 1)

        # =========================
        # 5️⃣ Domain Scoring (DRIFT-BASED)
        # =========================
        feature_z_map = dict(zip(self.pipeline.feature_columns, z_scores))

        domain_scores = {}

        for domain, features in DOMAIN_FEATURE_MAP.items():
            scores = [
                abs(feature_z_map[f])
                for f in features
                if f in feature_z_map
            ]

            domain_scores[domain] = max(scores) if scores else 0.0

        # =========================
        # 6️⃣ Correlation Rules
        # =========================
        correlation_result = evaluate_basic_rules(domain_scores, drift_level)
        # Add snapshot to rolling buffer
        self.correlation_buffer.add_snapshot(
            domain_scores=domain_scores,
            prediction=predictions[0],
            drift_level=drift_level
        )

        # Aggregate temporal correlation
        temporal_features = self.correlation_buffer.aggregate()

        # =========================
        # 7️⃣ Final Response
        # =========================
        return {
            "predictions": predictions.tolist(),
            "anomaly_ratio": float(np.mean(predictions == -1)),
            "drift_detected": drift_result["drift_detected"],
            "drift_level": drift_level,
            "drift_scores": z_scores,
            "domain_scores": domain_scores,
            "correlation": correlation_result,
            "temporal_features": temporal_features,
        }
