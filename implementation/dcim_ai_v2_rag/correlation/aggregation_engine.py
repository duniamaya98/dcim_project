# dcim_ai/correlation/aggregation_engine.py

import numpy as np
from collections import defaultdict
from .aggregation_models import AggregationState


class AggregationEngine:

    def __init__(self, activation_threshold=3.0):
        self.threshold = activation_threshold

    def compute(self, buffer):

        if not buffer:
            return None

        window_size = len(buffer)
        anomaly_count = 0
        severe_drift_count = 0

        domain_activity = defaultdict(int)
        domain_time_series = defaultdict(list)

        for entry in buffer:

            if entry["prediction"] == -1:
                anomaly_count += 1

            if entry["drift_level"] == "severe_drift":
                severe_drift_count += 1

            for domain, score in entry["domain_scores"].items():
                domain_time_series[domain].append(score)

                if score >= self.threshold:
                    domain_activity[domain] += 1

        # -----------------------------
        # Domain persistence ratio
        # -----------------------------
        domain_persistence_ratio = {
            d: domain_activity[d] / window_size
            for d in domain_time_series
        }

        # -----------------------------
        # Cross-domain co-occurrence
        # -----------------------------
        co_occurrence = defaultdict(lambda: defaultdict(int))

        for entry in buffer:
            active_domains = [
                d for d, score in entry["domain_scores"].items()
                if score >= self.threshold
            ]

            for d1 in active_domains:
                for d2 in active_domains:
                    if d1 != d2:
                        co_occurrence[d1][d2] += 1

        # -----------------------------
        # Domain trend analysis
        # -----------------------------
        domain_trend = {}

        for domain, series in domain_time_series.items():

            if len(series) < 3:
                domain_trend[domain] = "stable"
                continue

            slope = np.polyfit(range(len(series)), series, 1)[0]

            if slope > 0.5:
                domain_trend[domain] = "increasing"
            elif slope < -0.5:
                domain_trend[domain] = "decreasing"
            else:
                domain_trend[domain] = "stable"

        return AggregationState(
            window_size=window_size,
            anomaly_count=anomaly_count,
            anomaly_ratio=anomaly_count / window_size,
            severe_drift_count=severe_drift_count,
            drift_ratio=severe_drift_count / window_size,
            domain_activity_count=dict(domain_activity),
            domain_persistence_ratio=domain_persistence_ratio,
            co_occurrence_matrix={
                d: dict(inner)
                for d, inner in co_occurrence.items()
            },
            domain_trend=domain_trend
        )