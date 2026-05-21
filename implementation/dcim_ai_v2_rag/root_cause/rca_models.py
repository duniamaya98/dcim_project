"""
RCA data contract.

Versi v1.2.0 (MT-022 §6.3, §6.5):
    - Tambah field opsional: mode, forecast_horizon_h, forecast_confidence,
      asset_context, governance.
    - Semua field baru bersifat Optional dengan default sensible — kode
      lama yang membuat RootCauseResult tanpa argumen baru tetap berjalan.
    - Sinkron dengan dcim_ai.contracts.RootCauseResult (kontrak lintas-MT).
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import math


# Mode RCA (MT-022 §6.3). String konstanta untuk loose coupling.
RCA_MODE_REACTIVE = "reactive"
RCA_MODE_FORWARD = "forward"
RCA_MODE_HYBRID = "hybrid"

VALID_RCA_MODES = (RCA_MODE_REACTIVE, RCA_MODE_FORWARD, RCA_MODE_HYBRID)


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

    # Chain reconstruction
    causal_chain: List[str]

    # All impacted domains
    impact_domains: List[str]

    # Global confidence score
    confidence: float

    # Explanation text
    explanation: str

    # Evaluation-ready metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    # ------------------------------------------------------------
    # v1.2.0 additions — semua Optional untuk backward compatibility
    # ------------------------------------------------------------

    # MT-022 §6.3 — RCA mode
    mode: str = RCA_MODE_REACTIVE

    # MT-022 §6.3 — context untuk FORWARD mode
    forecast_horizon_h: Optional[int] = None
    forecast_confidence: Optional[float] = None

    # MT-022 §6.5 — asset enrichment (dict-form to avoid hard dep)
    asset_context: Optional[Dict[str, Any]] = None

    # MT-022 §6.7 — governance flags
    governance: Dict[str, Any] = field(default_factory=dict)

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
