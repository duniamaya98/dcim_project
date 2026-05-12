from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any
from datetime import datetime
import math


@dataclass
class RootCauseResult:
    incident_id: str
    timestamp: datetime

    # Softmax distribution
    domain_probabilities: Dict[str, float]

    # Final selected root
    root_domain: str

    # Ranked domains by probability
    ranked_domains: List[str]

    # Chain reconstruction (to be filled later)
    causal_chain: List[str]

    # All impacted domains
    impact_domains: List[str]

    # Global confidence score
    confidence: float

    # Explanation text
    explanation: str

    # Evaluation-ready metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def entropy(self) -> float:
        """
        Shannon entropy of domain probability distribution.
        Lower entropy → clearer root cause.
        """
        probs = self.domain_probabilities.values()
        return -sum(p * math.log(p + 1e-12) for p in probs)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        data["entropy"] = self.entropy()
        return data