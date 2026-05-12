# dcim_ai/correlation/aggregation_models.py

from dataclasses import dataclass
from typing import Dict


@dataclass
class AggregationState:
    window_size: int
    anomaly_count: int
    anomaly_ratio: float
    severe_drift_count: int
    drift_ratio: float
    domain_activity_count: Dict[str, int]
    domain_persistence_ratio: Dict[str, float]
    co_occurrence_matrix: Dict[str, Dict[str, int]]
    domain_trend: Dict[str, str]