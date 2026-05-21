"""
DCIM AI — Cross-MT Data Contracts (v1.2.0)

Modul ini berisi kontrak data lintas modul yang dirujuk oleh:
  - MT-018 §11.3 : MetricSource
  - MT-019 §6.3  : InferenceResult
  - MT-020 §6.3  : CapacityState
  - MT-020 §6.4  : AssetContext
  - MT-022 §6.3  : RootCauseResult (extended)
  - MT-022 §6.4  : CapacityRecommendation

Prinsip:
  - Backward compatible: field baru bersifat Optional dengan default sensible.
  - Serializable: semua dataclass mendukung as_dict() / from_dict() untuk
    persistensi (Postgres JSONB, Kafka payload, REST API).
  - Tidak meng-import model ML / framework — hanya stdlib + typing.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Protocol


# ============================================================================
# 1. TIME WINDOW
# ============================================================================


@dataclass(frozen=True)
class TimeWindow:
    """Rentang waktu absolut untuk loader & training window strategy."""

    start: datetime
    end: datetime

    @classmethod
    def last(cls, **kwargs) -> "TimeWindow":
        """Helper: TimeWindow.last(minutes=30), TimeWindow.last(days=7)."""
        end = datetime.utcnow()
        return cls(start=end - timedelta(**kwargs), end=end)

    @property
    def duration_seconds(self) -> float:
        return (self.end - self.start).total_seconds()

    def to_dict(self) -> Dict[str, str]:
        return {"start": self.start.isoformat(), "end": self.end.isoformat()}


# ============================================================================
# 2. METRIC SOURCE — MT-018 §11.3
# ============================================================================


class MetricSource(ABC):
    """
    Kontrak abstrak untuk semua sumber data telemetry.

    Dipakai oleh:
      - dcim_ai/training/training_orchestrator.py (loader training)
      - dcim_ai/inference/streaming_adapter.py    (loader inference)

    Implementasi konkret yang direncanakan:
      - ServerMetricsSource     (UC1/UC2, sumber: server_metrics)
      - PowerMetricsSource      (UC3,     sumber: power_metrics)
      - EnvironmentMetricsSource(UC3,     sumber: environment_metrics)
      - NetBoxAssetSource       (UC2,     sumber: NetBox API)

    Catatan: tipe DataFrame di-import lokal di subclass agar contracts/
    tetap zero-dependency.
    """

    domain: str = "server"          # 'server' | 'power' | 'cooling' | 'compute'
    table: str = ""
    feature_columns: List[str] = []
    timestamp_column: str = "time"
    asset_id_column: str = "hostname"

    @abstractmethod
    def load(self, window: TimeWindow):  # -> pd.DataFrame
        """Load data untuk window tertentu. Return DataFrame."""
        ...

    def describe(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "table": self.table,
            "feature_columns": list(self.feature_columns),
            "timestamp_column": self.timestamp_column,
            "asset_id_column": self.asset_id_column,
        }


# ============================================================================
# 3. ASSET CONTEXT — MT-020 §6.4
# ============================================================================


class CriticalityTier(str, Enum):
    TIER1 = "tier1"
    TIER2 = "tier2"
    TIER3 = "tier3"
    UNKNOWN = "unknown"


@dataclass
class AssetContext:
    """
    Konteks fisik aset — di-resolve oleh AssetContextResolver.

    Dipakai untuk enrichment di:
      - InferenceResult.asset_context
      - RootCauseResult.asset_context
      - CapacityRecommendation.asset_ids → resolve per item
    """

    asset_id: str
    site: Optional[str] = None
    rack: Optional[str] = None
    zone: Optional[str] = None                  # 'cooling_zone_2', dll.
    criticality: CriticalityTier = CriticalityTier.UNKNOWN
    role: Optional[str] = None                  # 'database', 'compute', 'storage'
    upstream_pdu: Optional[str] = None
    upstream_ups: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["criticality"] = self.criticality.value
        return d

    @classmethod
    def unknown(cls, asset_id: str) -> "AssetContext":
        return cls(asset_id=asset_id, criticality=CriticalityTier.UNKNOWN)

    @property
    def is_resolved(self) -> bool:
        return self.criticality is not CriticalityTier.UNKNOWN


class AssetContextResolver(Protocol):
    """Protocol untuk resolver — implementasi konkret di domain/asset_resolver.py."""

    def resolve(self, asset_id: str) -> AssetContext: ...


# ============================================================================
# 4. INFERENCE RESULT — MT-019 §6.3
# ============================================================================


class Severity(str, Enum):
    NORMAL = "normal"
    WEAK_SIGNAL = "weak_signal"
    WARNING = "warning"
    CRITICAL = "critical"


class ModelType(str, Enum):
    ANOMALY = "anomaly"
    FORECAST = "forecast"
    CLUSTERING = "clustering"
    ENERGY_ANOMALY = "energy_anomaly"
    CAPACITY_OPTIMIZER = "capacity_optimizer"


@dataclass
class InferenceResult:
    """
    Output standar lintas modul (MT-019 §6.3).

    Field eksisting MT-018/MT-019 (`prediction`, `severity`, `ensemble_score`,
    `model_votes`) dipertahankan via `legacy` untuk backward compatibility.
    """

    model_id: str
    model_type: ModelType
    asset_id: str
    timestamp: datetime
    score: float
    severity: Severity
    confidence: float                                   # [0, 1]
    domain: str
    evidence: Dict[str, Any] = field(default_factory=dict)

    # Optional — hanya untuk forecast (MT-018 §11.4 / MT-019 §6.3)
    forecast_horizon_h: Optional[int] = None
    forecast_value: Optional[float] = None
    forecast_ci_low: Optional[float] = None
    forecast_ci_high: Optional[float] = None

    # Optional — enrichment
    asset_context: Optional[AssetContext] = None

    # Backward compatibility — field lama yang masih dipakai eksisting code
    legacy: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "model_id": self.model_id,
            "model_type": self.model_type.value,
            "asset_id": self.asset_id,
            "timestamp": self.timestamp.isoformat(),
            "score": self.score,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "domain": self.domain,
            "evidence": self.evidence,
            "forecast_horizon_h": self.forecast_horizon_h,
            "forecast_value": self.forecast_value,
            "forecast_ci_low": self.forecast_ci_low,
            "forecast_ci_high": self.forecast_ci_high,
            "asset_context": self.asset_context.to_dict() if self.asset_context else None,
            "legacy": self.legacy,
        }


# ============================================================================
# 5. CAPACITY STATE — MT-020 §6.3
# ============================================================================


class CapacityTrend(str, Enum):
    INCREASING = "increasing"
    STABLE = "stable"
    DECREASING = "decreasing"


@dataclass
class CapacityState:
    """
    Indikator kapasitas struktural (bukan anomaly).
    Dihasilkan oleh aggregation engine MT-020 §6.3, dikonsumsi
    oleh CapacityRecommendation (MT-022 §6.4).
    """

    domain: str
    asset_id: str
    utilization_p50: float
    utilization_p95: float
    headroom_pct: float
    occupancy_pct: Optional[float] = None    # dari NetBox (rack U usage)
    trend_30d: CapacityTrend = CapacityTrend.STABLE
    underutilized: bool = False              # p95 < threshold (default 30%)
    saturating: bool = False                 # p95 > threshold (default 85%)
    window: Optional[str] = None             # 'rolling_30d' | 'rolling_90d'

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["trend_30d"] = self.trend_30d.value
        return d


# ============================================================================
# 6. ROOT CAUSE RESULT — MT-022 §6.3, §6.5 (extended)
# ============================================================================


class RCAMode(str, Enum):
    REACTIVE = "reactive"   # default — incident yang sudah terjadi
    FORWARD = "forward"     # baru   — projected dari forecast
    HYBRID = "hybrid"       # gabungkan keduanya


@dataclass
class RootCauseResult:
    """
    Kontrak output RCA. Field baru bersifat Optional untuk backward compat.
    Field lama tetap dipertahankan persis seperti MT-022 §1.
    """

    incident_id: str
    timestamp: datetime
    domain_probabilities: Dict[str, float]
    root_domain: str
    ranked_domains: List[str]
    causal_chain: List[str]
    impact_domains: List[str]
    confidence: float
    entropy: float
    metadata: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""

    # --- Field baru v1.2.0 ---
    mode: RCAMode = RCAMode.REACTIVE
    forecast_horizon_h: Optional[int] = None
    forecast_confidence: Optional[float] = None
    asset_context: Optional[AssetContext] = None
    governance: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "incident_id": self.incident_id,
            "timestamp": self.timestamp.isoformat(),
            "domain_probabilities": self.domain_probabilities,
            "root_domain": self.root_domain,
            "ranked_domains": self.ranked_domains,
            "causal_chain": self.causal_chain,
            "impact_domains": self.impact_domains,
            "confidence": self.confidence,
            "entropy": self.entropy,
            "metadata": self.metadata,
            "explanation": self.explanation,
            "mode": self.mode.value,
            "forecast_horizon_h": self.forecast_horizon_h,
            "forecast_confidence": self.forecast_confidence,
            "asset_context": self.asset_context.to_dict() if self.asset_context else None,
            "governance": self.governance,
        }


# ============================================================================
# 7. CAPACITY RECOMMENDATION — MT-022 §6.4
# ============================================================================


class CapacityFinding(str, Enum):
    UNDERUTILIZED = "underutilized"
    SATURATING = "saturating"
    IMBALANCED = "imbalanced"


class CapacityAction(str, Enum):
    CONSOLIDATE = "consolidate"
    REDISTRIBUTE = "redistribute"
    SCALE_OUT = "scale_out"
    NO_ACTION = "no_action"


@dataclass
class CapacityRecommendation:
    """Kontrak output untuk modul capacity reasoning UC2 (MT-022 §6.4)."""

    recommendation_id: str
    timestamp: datetime
    scope: str                                 # 'rack' | 'zone' | 'site'
    asset_ids: List[str]
    finding: CapacityFinding
    metrics: Dict[str, Any]                    # utilization_p50/p95, headroom_pct
    suggested_action: CapacityAction
    estimated_savings: Dict[str, float] = field(default_factory=dict)
    confidence: float = 0.0
    narrative: str = ""                        # diisi oleh LLM dcim_assistant
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    asset_contexts: List[AssetContext] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "recommendation_id": self.recommendation_id,
            "timestamp": self.timestamp.isoformat(),
            "scope": self.scope,
            "asset_ids": self.asset_ids,
            "finding": self.finding.value,
            "metrics": self.metrics,
            "suggested_action": self.suggested_action.value,
            "estimated_savings": self.estimated_savings,
            "confidence": self.confidence,
            "narrative": self.narrative,
            "evidence": self.evidence,
            "asset_contexts": [a.to_dict() for a in self.asset_contexts],
        }


# ============================================================================
# 8. CONTRACT VERSIONING
# ============================================================================

CONTRACTS_VERSION = "1.2.0"

__all__ = [
    "CONTRACTS_VERSION",
    "TimeWindow",
    "MetricSource",
    "AssetContext",
    "AssetContextResolver",
    "CriticalityTier",
    "InferenceResult",
    "Severity",
    "ModelType",
    "CapacityState",
    "CapacityTrend",
    "RootCauseResult",
    "RCAMode",
    "CapacityRecommendation",
    "CapacityFinding",
    "CapacityAction",
]
