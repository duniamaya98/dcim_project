# dcim_ai/root_cause/lifecycle_manager.py

from collections import deque
import numpy as np


class RootCauseLifecycleManager:

    def __init__(self, window_size=20):
        self.window_size = window_size
        self.root_history = deque(maxlen=window_size)
        self.confidence_history = deque(maxlen=window_size)
        self.entropy_history = deque(maxlen=window_size)

    # -----------------------------------
    # Update Lifecycle State
    # -----------------------------------
    def update(self, rca_result):

        self.root_history.append(rca_result.root_domain)
        self.confidence_history.append(rca_result.confidence)
        self.entropy_history.append(rca_result.entropy())

    # -----------------------------------
    # Root Stability
    # -----------------------------------
    def root_stability(self):

        if not self.root_history:
            return 1.0

        most_common = max(set(self.root_history),
                          key=self.root_history.count)

        stability = self.root_history.count(most_common) / len(self.root_history)

        return round(stability, 3)

    # -----------------------------------
    # Root Shift Detection
    # -----------------------------------
    def root_shift_frequency(self):

        if len(self.root_history) < 2:
            return 0

        shifts = 0
        prev = self.root_history[0]

        for root in list(self.root_history)[1:]:
            if root != prev:
                shifts += 1
            prev = root

        return shifts

    # -----------------------------------
    # Average Confidence
    # -----------------------------------
    def avg_confidence(self):

        if not self.confidence_history:
            return 0

        return round(np.mean(self.confidence_history), 3)

    # -----------------------------------
    # Average Entropy
    # -----------------------------------
    def avg_entropy(self):

        if not self.entropy_history:
            return 0

        return round(np.mean(self.entropy_history), 3)
    
    # -----------------------------------
    # Governance Evaluation
    # -----------------------------------
    def governance_status(self,
                          shift_threshold=3,
                          confidence_threshold=0.4,
                          entropy_threshold=1.2):

        status = {
            "rca_unstable": False,
            "low_confidence": False,
            "high_entropy": False,
            "governance_flag": False
        }
        status["stability_score"] = self.stability_score()
        status["severity_level"] = self.governance_severity()

        if self.root_shift_frequency() >= shift_threshold:
            status["rca_unstable"] = True

        if self.avg_confidence() < confidence_threshold:
            status["low_confidence"] = True

        if self.avg_entropy() > entropy_threshold:
            status["high_entropy"] = True

        # Master flag
        if any([
            status["rca_unstable"],
            status["low_confidence"],
            status["high_entropy"]
        ]):
            status["governance_flag"] = True

        return status

    # -----------------------------------
    # Lifecycle Summary
    # -----------------------------------
    def summary(self):

        return {
            "root_stability": self.root_stability(),
            "root_shift_frequency": self.root_shift_frequency(),
            "avg_confidence": self.avg_confidence(),
            "avg_entropy": self.avg_entropy()
        }

    # -----------------------------------
    def stability_score(self):

        if not self.root_history:
            return 1.0

        root_stability = self.root_stability()
        avg_conf = self.avg_confidence()
        avg_entropy = self.avg_entropy()

        # Number of unique roots observed
        unique_roots = len(set(self.root_history))
        domain_count = max(unique_roots, 2)

        # Entropy normalization
        max_entropy = np.log(domain_count)
        normalized_entropy = avg_entropy / (max_entropy + 1e-6)

        normalized_entropy = min(max(normalized_entropy, 0), 1)

        # Non-linear entropy penalty
        entropy_penalty = 1 - (normalized_entropy ** 1.5)

        # Weighted blend (enterprise calibration)
        stability = (
            0.5 * root_stability +
            0.3 * avg_conf +
            0.2 * entropy_penalty
        )

        return round(stability, 3)

    def governance_severity(self):

        score = self.stability_score()

        if score >= 0.75:
            return "stable"
        elif score >= 0.5:
            return "moderate"
        else:
            return "unstable"