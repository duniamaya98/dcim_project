"""
Unit tests untuk dcim_ai/inference/asset_enricher.py.

Tidak butuh DB / NetBox — pakai StaticYamlAssetResolver dengan
inventory in-memory.
"""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest
from datetime import datetime

from dcim_ai.contracts import (
    AssetContext,
    CapacityAction,
    CapacityFinding,
    CapacityRecommendation,
    CriticalityTier,
    InferenceResult,
    ModelType,
    Severity,
)
from dcim_ai.domain.asset_resolver import StaticYamlAssetResolver
from dcim_ai.inference.asset_enricher import AssetEnricher
from dcim_ai.root_cause.rca_models import RootCauseResult


SAMPLE_YAML = textwrap.dedent(
    """
    assets:
      - asset_id: srv-db-01
        site: jkt-1
        rack: R-12
        zone: cooling_zone_2
        criticality: tier1
        role: database
        upstream_pdu: PDU-05
        upstream_ups: UPS-A
      - asset_id: PDU-05
        site: jkt-1
        rack: R-12
        zone: cooling_zone_2
        criticality: tier1
        role: pdu
    """
).strip()


def _make_yaml() -> str:
    fh = tempfile.NamedTemporaryFile(
        "w", suffix=".yaml", delete=False, encoding="utf-8"
    )
    fh.write(SAMPLE_YAML)
    fh.flush()
    fh.close()
    return fh.name


class _Base(unittest.TestCase):
    def setUp(self):
        self.yaml_path = _make_yaml()
        self.enricher = AssetEnricher(
            resolver=StaticYamlAssetResolver(yaml_path=self.yaml_path)
        )

    def tearDown(self):
        try:
            os.unlink(self.yaml_path)
        except OSError:
            pass


class ResolveTests(_Base):
    def test_resolve_known(self):
        ctx = self.enricher.resolve("srv-db-01")
        self.assertEqual(ctx.criticality, CriticalityTier.TIER1)
        self.assertEqual(ctx.upstream_pdu, "PDU-05")

    def test_resolve_empty(self):
        ctx = self.enricher.resolve("")
        self.assertFalse(ctx.is_resolved)

    def test_resolve_unknown(self):
        ctx = self.enricher.resolve("ghost-server")
        self.assertFalse(ctx.is_resolved)


class InferenceResultTests(_Base):
    def _make_result(self) -> InferenceResult:
        return InferenceResult(
            model_id="anomaly_v1.4",
            model_type=ModelType.ANOMALY,
            asset_id="srv-db-01",
            timestamp=datetime(2026, 5, 20, 9, 0, 0),
            score=0.9,
            severity=Severity.WARNING,
            confidence=0.7,
            domain="storage",
        )

    def test_enrich_inference_attaches_context(self):
        r = self.enricher.enrich_inference(self._make_result())
        self.assertIsNotNone(r.asset_context)
        self.assertEqual(r.asset_context.rack, "R-12")
        self.assertEqual(r.asset_context.criticality, CriticalityTier.TIER1)

    def test_enrich_inference_idempotent(self):
        r = self._make_result()
        r.asset_context = AssetContext.unknown("srv-db-01")
        out = self.enricher.enrich_inference(r)
        # tidak ditimpa karena sudah ada (meskipun UNKNOWN)
        self.assertFalse(out.asset_context.is_resolved)

    def test_enrich_inference_force(self):
        r = self._make_result()
        r.asset_context = AssetContext.unknown("srv-db-01")
        out = self.enricher.enrich_inference(r, force=True)
        self.assertTrue(out.asset_context.is_resolved)

    def test_enrich_inferences_batch(self):
        rs = [self._make_result(), self._make_result()]
        out = self.enricher.enrich_inferences(rs)
        self.assertEqual(len(out), 2)
        self.assertTrue(all(r.asset_context is not None for r in out))


class RCAEnrichTests(_Base):
    def _make_rca(self, asset_id_in_metadata=None) -> RootCauseResult:
        return RootCauseResult(
            incident_id="inc-1",
            timestamp=datetime(2026, 5, 20, 9, 0, 0),
            domain_probabilities={"power": 0.7, "cooling": 0.3},
            root_domain="power",
            ranked_domains=["power", "cooling"],
            causal_chain=["power", "cooling"],
            impact_domains=["power", "cooling", "compute"],
            confidence=0.7,
            explanation="test",
            metadata={"asset_id": asset_id_in_metadata} if asset_id_in_metadata else {},
        )

    def test_enrich_rca_uses_explicit_asset_id(self):
        rca = self._make_rca()
        out = self.enricher.enrich_rca(rca, asset_id="srv-db-01")
        self.assertIsNotNone(out.asset_context)
        self.assertEqual(out.asset_context["rack"], "R-12")

    def test_enrich_rca_uses_metadata_asset_id(self):
        rca = self._make_rca(asset_id_in_metadata="PDU-05")
        out = self.enricher.enrich_rca(rca)
        self.assertIsNotNone(out.asset_context)
        self.assertEqual(out.asset_context["role"], "pdu")

    def test_enrich_rca_no_asset_id_skips(self):
        rca = self._make_rca()
        out = self.enricher.enrich_rca(rca)
        self.assertIsNone(out.asset_context)

    def test_enrich_rca_unknown_sets_governance(self):
        rca = self._make_rca()
        out = self.enricher.enrich_rca(rca, asset_id="ghost-server")
        self.assertTrue(out.governance.get("asset_context_missing"))
        self.assertTrue(out.governance.get("governance_flag"))

    def test_enrich_rca_cross_domain_power_cooling(self):
        rca = self._make_rca()
        rca.impact_domains = ["power", "cooling", "compute"]
        rca.root_domain = "power"
        out = self.enricher.enrich_rca(rca, asset_id="PDU-05")
        self.assertTrue(out.governance.get("cross_domain_power_cooling"))

    def test_enrich_rca_single_domain_no_cross_flag(self):
        rca = self._make_rca()
        rca.impact_domains = ["power"]
        rca.root_domain = "power"
        out = self.enricher.enrich_rca(rca, asset_id="PDU-05")
        self.assertFalse(out.governance.get("cross_domain_power_cooling", False))


class CapacityEnrichTests(_Base):
    def test_enrich_capacity(self):
        rec = CapacityRecommendation(
            recommendation_id="rec-1",
            timestamp=datetime(2026, 5, 20, 9, 0, 0),
            scope="rack",
            asset_ids=["srv-db-01", "PDU-05", "ghost"],
            finding=CapacityFinding.UNDERUTILIZED,
            metrics={},
            suggested_action=CapacityAction.CONSOLIDATE,
        )
        out = self.enricher.enrich_capacity(rec)
        self.assertEqual(len(out.asset_contexts), 3)
        self.assertTrue(out.asset_contexts[0].is_resolved)
        self.assertTrue(out.asset_contexts[1].is_resolved)
        self.assertFalse(out.asset_contexts[2].is_resolved)


if __name__ == "__main__":
    unittest.main()
