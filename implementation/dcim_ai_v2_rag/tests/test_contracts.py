"""
Unit tests untuk dcim_ai/contracts/__init__.py (v1.2.0).

Tujuan:
    - Memastikan semua dataclass kontrak bisa di-instantiate, di-serialize,
      dan field default-nya stabil.
    - Mendeteksi breaking change pada kontrak lintas-MT lebih awal.
    - Tidak butuh DB / GPU — bisa dijalankan di CI cepat.

Cara jalankan:
    cd /home/infra/dcim_project/implementation
    python -m pytest dcim_ai_v2_rag/tests/test_contracts.py -v

    # atau via stdlib unittest:
    python -m unittest dcim_ai_v2_rag.tests.test_contracts -v
"""

from __future__ import annotations

import json
import unittest
from datetime import datetime, timedelta

from dcim_ai.contracts import (
    AssetContext,
    CapacityAction,
    CapacityFinding,
    CapacityRecommendation,
    CapacityState,
    CapacityTrend,
    CONTRACTS_VERSION,
    CriticalityTier,
    InferenceResult,
    ModelType,
    RCAMode,
    RootCauseResult,
    Severity,
    TimeWindow,
)


class TimeWindowTests(unittest.TestCase):
    def test_last_minutes(self):
        w = TimeWindow.last(minutes=30)
        self.assertEqual(w.duration_seconds, 30 * 60)
        self.assertLess(w.start, w.end)

    def test_last_days(self):
        w = TimeWindow.last(days=7)
        self.assertAlmostEqual(w.duration_seconds, 7 * 86400, delta=1)

    def test_to_dict_iso(self):
        end = datetime(2026, 5, 20, 9, 0, 0)
        start = end - timedelta(minutes=15)
        w = TimeWindow(start=start, end=end)
        d = w.to_dict()
        self.assertEqual(d["start"], start.isoformat())
        self.assertEqual(d["end"], end.isoformat())


class AssetContextTests(unittest.TestCase):
    def test_unknown_factory(self):
        ctx = AssetContext.unknown("srv-x")
        self.assertEqual(ctx.asset_id, "srv-x")
        self.assertEqual(ctx.criticality, CriticalityTier.UNKNOWN)
        self.assertFalse(ctx.is_resolved)

    def test_resolved_flag(self):
        ctx = AssetContext(
            asset_id="srv-1",
            criticality=CriticalityTier.TIER1,
            rack="R-12",
        )
        self.assertTrue(ctx.is_resolved)

    def test_to_dict_roundtrip_json(self):
        ctx = AssetContext(
            asset_id="srv-1",
            site="jkt-1",
            rack="R-12",
            criticality=CriticalityTier.TIER1,
            role="database",
            extra={"power_kw": 4.2},
        )
        s = json.dumps(ctx.to_dict())
        d = json.loads(s)
        self.assertEqual(d["asset_id"], "srv-1")
        self.assertEqual(d["criticality"], "tier1")
        self.assertEqual(d["extra"]["power_kw"], 4.2)


class InferenceResultTests(unittest.TestCase):
    def _base(self) -> InferenceResult:
        return InferenceResult(
            model_id="energy_anomaly_v1.0",
            model_type=ModelType.ENERGY_ANOMALY,
            asset_id="PDU-05",
            timestamp=datetime(2026, 5, 20, 9, 0, 0),
            score=0.87,
            severity=Severity.WARNING,
            confidence=0.71,
            domain="power",
            evidence={"z_score": 4.2, "baseline_pue": 1.5},
        )

    def test_minimal_serialize(self):
        r = self._base()
        d = r.to_dict()
        self.assertEqual(d["model_type"], "energy_anomaly")
        self.assertEqual(d["severity"], "warning")
        self.assertIsNone(d["forecast_horizon_h"])
        self.assertIsNone(d["asset_context"])

    def test_with_forecast_fields(self):
        r = self._base()
        r.model_type = ModelType.FORECAST
        r.forecast_horizon_h = 24
        r.forecast_value = 78.0
        r.forecast_ci_low = 70.0
        r.forecast_ci_high = 86.0
        d = r.to_dict()
        self.assertEqual(d["forecast_horizon_h"], 24)
        self.assertEqual(d["forecast_value"], 78.0)

    def test_with_asset_context(self):
        r = self._base()
        r.asset_context = AssetContext(
            asset_id="PDU-05",
            zone="cooling_zone_2",
            criticality=CriticalityTier.TIER1,
        )
        d = r.to_dict()
        self.assertEqual(d["asset_context"]["zone"], "cooling_zone_2")
        self.assertEqual(d["asset_context"]["criticality"], "tier1")


class CapacityStateTests(unittest.TestCase):
    def test_defaults(self):
        s = CapacityState(
            domain="compute",
            asset_id="srv-app-01",
            utilization_p50=22.0,
            utilization_p95=29.0,
            headroom_pct=71.0,
        )
        self.assertEqual(s.trend_30d, CapacityTrend.STABLE)
        self.assertFalse(s.underutilized)
        self.assertFalse(s.saturating)

    def test_serialization(self):
        s = CapacityState(
            domain="compute",
            asset_id="srv-app-01",
            utilization_p50=22.0,
            utilization_p95=29.0,
            headroom_pct=71.0,
            trend_30d=CapacityTrend.DECREASING,
            underutilized=True,
        )
        d = s.to_dict()
        self.assertEqual(d["trend_30d"], "decreasing")
        self.assertTrue(d["underutilized"])


class RootCauseResultTests(unittest.TestCase):
    def _base(self) -> RootCauseResult:
        return RootCauseResult(
            incident_id="ed41740a-2141-431e-91b2-f2c4293f8161",
            timestamp=datetime(2026, 5, 20, 9, 0, 0),
            domain_probabilities={"power": 0.55, "cooling": 0.30, "compute": 0.15},
            root_domain="power",
            ranked_domains=["power", "cooling", "compute"],
            causal_chain=["power", "cooling", "compute"],
            impact_domains=["compute", "memory"],
            confidence=0.55,
            entropy=0.92,
            metadata={"num_domains": 3, "max_probability": 0.55},
            explanation="Root cause chain reconstructed: power -> cooling -> compute.",
        )

    def test_default_mode_reactive(self):
        rca = self._base()
        self.assertEqual(rca.mode, RCAMode.REACTIVE)
        self.assertIsNone(rca.forecast_horizon_h)
        self.assertIsNone(rca.asset_context)

    def test_forward_mode_payload(self):
        rca = self._base()
        rca.mode = RCAMode.FORWARD
        rca.forecast_horizon_h = 24
        rca.forecast_confidence = 0.7
        d = rca.to_dict()
        self.assertEqual(d["mode"], "forward")
        self.assertEqual(d["forecast_horizon_h"], 24)
        self.assertAlmostEqual(d["forecast_confidence"], 0.7)

    def test_with_asset_context_and_governance(self):
        rca = self._base()
        rca.asset_context = AssetContext(
            asset_id="srv-db-01",
            rack="R-12",
            zone="cooling_zone_2",
            criticality=CriticalityTier.TIER1,
            upstream_pdu="PDU-05",
        )
        rca.governance = {
            "rca_unstable": False,
            "low_confidence": True,
            "high_entropy": True,
            "governance_flag": True,
            "stability_score": 0.42,
            "severity_level": "unstable",
            "cross_domain_power_cooling": True,
        }
        d = rca.to_dict()
        self.assertEqual(d["asset_context"]["upstream_pdu"], "PDU-05")
        self.assertTrue(d["governance"]["cross_domain_power_cooling"])


class CapacityRecommendationTests(unittest.TestCase):
    def test_minimal(self):
        rec = CapacityRecommendation(
            recommendation_id="rec-001",
            timestamp=datetime(2026, 5, 20, 9, 0, 0),
            scope="rack",
            asset_ids=["srv-app-01", "srv-app-02"],
            finding=CapacityFinding.UNDERUTILIZED,
            metrics={"utilization_p95": 24.0, "headroom_pct": 76.0},
            suggested_action=CapacityAction.CONSOLIDATE,
            estimated_savings={"capacity_pct": 12.5, "power_kw": 4.2},
            confidence=0.78,
        )
        d = rec.to_dict()
        self.assertEqual(d["finding"], "underutilized")
        self.assertEqual(d["suggested_action"], "consolidate")
        self.assertEqual(d["estimated_savings"]["power_kw"], 4.2)


class ContractVersionTests(unittest.TestCase):
    def test_version_string(self):
        self.assertEqual(CONTRACTS_VERSION, "1.2.0")


if __name__ == "__main__":
    unittest.main()
