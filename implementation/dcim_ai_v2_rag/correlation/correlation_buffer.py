import time
from collections import deque


class CorrelationBuffer:

    def __init__(self, window_seconds=300):
        """
        window_seconds: default 5 menit
        """
        self.window_seconds = window_seconds
        self.buffer = deque()

    def add_snapshot(self, domain_scores, prediction, drift_level):
        """
        Store snapshot data into buffer
        """
        timestamp = time.time()

        self.buffer.append({
            "timestamp": timestamp,
            "domain_scores": domain_scores,
            "prediction": prediction,
            "drift_level": drift_level
        })

        self._cleanup()

    def _cleanup(self):
        """
        Remove old entries outside rolling window
        """
        now = time.time()
        while self.buffer and (now - self.buffer[0]["timestamp"] > self.window_seconds):
            self.buffer.popleft()

    def aggregate(self):
        """
        Generate correlation features over window
        """

        if not self.buffer:
            return {}

        domain_activity = {}
        anomaly_count = 0
        severe_drift_count = 0

        for entry in self.buffer:
            if entry["prediction"] == -1:
                anomaly_count += 1

            if entry["drift_level"] == "severe_drift":
                severe_drift_count += 1

            for domain, score in entry["domain_scores"].items():
                if score > 3.0:  # domain active threshold
                    domain_activity[domain] = domain_activity.get(domain, 0) + 1
    
        return {
            "window_size": len(self.buffer),
            "anomaly_count": anomaly_count,
            "severe_drift_count": severe_drift_count,
            "domain_activity": domain_activity
        }
    
    def get_buffer(self):
        return list(self.buffer)