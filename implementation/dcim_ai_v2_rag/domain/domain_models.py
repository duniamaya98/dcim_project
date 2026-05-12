# dcim_ai/domain/domain_models.py

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class DomainState:
    domain_scores: Dict[str, float]
    active_domains: List[str]
    domain_strength_index: float