# dcim_ai/domain/domain_engine.py

from .domain_config import (
    DOMAIN_FEATURE_MAP,
    DOMAIN_SEVERITY_WEIGHT,
    DOMAIN_ACTIVATION_THRESHOLD
)
from .domain_models import DomainState


class DomainEngine:

    def __init__(self):
        self.feature_map = DOMAIN_FEATURE_MAP
        self.weights = DOMAIN_SEVERITY_WEIGHT
        self.threshold = DOMAIN_ACTIVATION_THRESHOLD

    def compute(self, feature_z_map: dict) -> DomainState:

        domain_scores = {}

        for domain, features in self.feature_map.items():
            scores = [
                abs(feature_z_map[f])
                for f in features
                if f in feature_z_map
            ]

            if scores:
                domain_scores[domain] = max(scores)
            else:
                domain_scores[domain] = 0.0

        active_domains = [
            d for d, score in domain_scores.items()
            if score >= self.threshold
        ]

        # Weighted domain strength index
        weighted_sum = sum(
            domain_scores[d] * self.weights.get(d, 1.0)
            for d in domain_scores
        )

        domain_strength_index = weighted_sum / len(domain_scores)

        return DomainState(
            domain_scores=domain_scores,
            active_domains=active_domains,
            domain_strength_index=domain_strength_index
        )