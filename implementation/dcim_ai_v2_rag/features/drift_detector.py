import numpy as np
import json


class DriftDetector:

    def __init__(self, baseline_stats_path, threshold=2.5):
        with open(baseline_stats_path, "r") as f:
            self.baseline = json.load(f)

        self.threshold = threshold

    def check_drift(self, X_live):

        live_mean = np.mean(X_live, axis=0)
        baseline_mean = np.array(self.baseline["mean"])
        baseline_std = np.array(self.baseline["std"])

        z_scores = np.abs((live_mean - baseline_mean) / baseline_std)

        drift_flags = z_scores > self.threshold

        return {
            "drift_detected": bool(np.any(drift_flags)),
            "z_scores": z_scores.tolist()
        }
        print("Baseline mean:", baseline_mean)
        print("Live mean:", live_mean)
        print("Baseline mean:", baseline_mean)
        print("Live mean:", live_mean)
