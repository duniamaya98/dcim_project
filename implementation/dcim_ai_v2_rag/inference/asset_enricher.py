"""
DCIM AI — Asset Enricher (MT-022 §6.5, MT-019 §6.3)

Helper untuk melengkapi output AI dengan konteks fisik aset:
    - RootCauseResult.asset_context     (RCA engine)
    - InferenceResult.asset_context     (inference service)
    - CapacityRecommendation.asset_contexts (capacity reasoning)

Modul ini stateless terhadap data ML — hanya membungkus
AssetContextResolver agar penggunaan di banyak tempat konsisten dan
gampang di-swap (NetBox, YAML, atau composite).

Prinsip:
    - Best-effort: jika resolver gagal / belum dikonfigurasi,
      enricher mengembalikan object aslinya tanpa raise.
    - Idempotent: enrich object yang sudah punya asset_context tidak
      menimpa, kecuali force=True.
    - Singleton-friendly: factory get_default_enricher() agar service
      cukup memanggil sekali.
"""

from __future__ import annotations

import logging
import threading
from typing import Iterable, List, Optional

from dcim_ai.contracts import (
    AssetContext,
    CapacityRecommendation,
    InferenceResult,
    RootCauseResult,
)
from dcim_ai.domain.asset_resolver import (
    CompositeAssetResolver,
    StaticYamlAssetResolver,
    default_resolver,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Enricher
# ============================================================================


class AssetEnricher:
    """
    Wrapper di atas AssetContextResolver dengan policy enrichment yang
    konsisten lintas modul (RCA, Inference, Capacity).
    """

    def __init__(self, resolver=None):
        self._resolver = resolver or default_resolver()

    # ------------------------------------------------------------------
    # Resolver passthrough
    # ------------------------------------------------------------------

    def resolve(self, asset_id: str) -> AssetContext:
        if not asset_id:
            return AssetContext.unknown("")
        try:
            return self._resolver.resolve(asset_id)
        except Exception as exc:  # noqa: BLE001 — best-effort enrichment
            logger.warning("AssetEnricher resolve failed for %s: %s", asset_id, exc)
            return AssetContext.unknown(asset_id)

    # ------------------------------------------------------------------
    # InferenceResult — MT-019 §6.3
    # ------------------------------------------------------------------

    def enrich_inference(
        self,
        result: InferenceResult,
        *,
        force: bool = False,
    ) -> InferenceResult:
        """Set ``result.asset_context`` bila belum ada (atau force=True)."""
        if result.asset_context is not None and not force:
            return result
        result.asset_context = self.resolve(result.asset_id)
        return result

    def enrich_inferences(
        self,
        results: Iterable[InferenceResult],
        *,
        force: bool = False,
    ) -> List[InferenceResult]:
        return [self.enrich_inference(r, force=force) for r in results]

    # ------------------------------------------------------------------
    # RootCauseResult — MT-022 §6.5
    # ------------------------------------------------------------------

    def enrich_rca(
        self,
        result: RootCauseResult,
        asset_id: Optional[str] = None,
        *,
        force: bool = False,
    ) -> RootCauseResult:
        """
        Set ``result.asset_context`` (dict-form) berdasarkan asset_id.

        Sumber asset_id (urutan prioritas):
            1. argumen ``asset_id`` eksplisit,
            2. ``result.metadata['asset_id']`` (dipasang oleh
               ``RCAEngine.analyze_forward()``),
            3. tidak melakukan apa-apa.
        """
        if result.asset_context is not None and not force:
            return result

        target = asset_id or (result.metadata or {}).get("asset_id")
        if not target:
            return result

        ctx = self.resolve(target)
        # rca_models.RootCauseResult menyimpan asset_context sebagai dict
        # untuk loose coupling — sesuai keputusan v1.2.0.
        result.asset_context = ctx.to_dict()

        # MT-022 §6.7 governance flag bila asset belum diregistrasi.
        if not ctx.is_resolved:
            gov = dict(result.governance or {})
            gov["asset_context_missing"] = True
            gov["governance_flag"] = True
            result.governance = gov

        # MT-022 §6.7 governance flag tambahan: cross-domain power+cooling.
        active = set(result.impact_domains or [])
        if {"power", "cooling"} & active and result.root_domain in {"power", "cooling"}:
            if len(active) > 1:
                gov = dict(result.governance or {})
                gov["cross_domain_power_cooling"] = True
                gov["governance_flag"] = True
                result.governance = gov

        return result

    # ------------------------------------------------------------------
    # CapacityRecommendation — MT-022 §6.4
    # ------------------------------------------------------------------

    def enrich_capacity(
        self,
        recommendation: CapacityRecommendation,
        *,
        force: bool = False,
    ) -> CapacityRecommendation:
        """Resolve seluruh asset_ids → list AssetContext."""
        if recommendation.asset_contexts and not force:
            return recommendation
        recommendation.asset_contexts = [
            self.resolve(aid) for aid in (recommendation.asset_ids or [])
        ]
        return recommendation


# ============================================================================
# Default singleton
# ============================================================================


_default_enricher: Optional[AssetEnricher] = None
_lock = threading.Lock()


def get_default_enricher() -> AssetEnricher:
    """
    Singleton AssetEnricher untuk dipakai service runtime tanpa
    membuat resolver berulang-ulang.

    Override untuk testing:
        get_default_enricher.cache = AssetEnricher(my_resolver)
    """
    global _default_enricher
    with _lock:
        if _default_enricher is None:
            _default_enricher = AssetEnricher()
        return _default_enricher


def set_default_enricher(enricher: Optional[AssetEnricher]) -> None:
    """Untuk testing / dependency injection."""
    global _default_enricher
    with _lock:
        _default_enricher = enricher


__all__ = [
    "AssetEnricher",
    "get_default_enricher",
    "set_default_enricher",
]
