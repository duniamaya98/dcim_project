"""
Unit tests untuk RCAEngine FORWARD & HYBRID mode (MT-022 §6.3).

Test ini tidak butuh DB / GPU — hanya memvalidasi logika RCA.
"""

from __future__ import annotations

import unittest
from datetime import datetime

from dcim_ai.root_cause.rca_engine import RCAEngine
from dcim_ai.root_cause.rca_models import (
    RCA_MODE_FORWARD,
    RCA_MODE_HYBRID,
    RCA_MODE_REACTIVE,
    RootCauseResult,
)


class _Base(unittest.TestCase):
    """Helper base class dengan factory incident & forecast."""

    def make_incident(self):
        return {
            "incident_id": "inc-001",
            "timestamp": datetime(2026, 5, 20, 9, 0, 0),
            "active_domains": ["compute", "memory"],
            "domain_scores": {"compute": 5.0, "memory": 3.0},
            "domain_strength_index": 8.0,
            "anomaly_ratio": 0.6,
            "drift_ratio": 0.2,
            "domain_persistence_ratio": {"compute": 0.8, "memory": 0.5},
            "domain_trend": {"compute": "increasing", "memory": "stable"},
        }

    def make_forecast(self, **overrides):
        payload = {
            "incident_id": "fwd-001",
            "timestamp": datetime(2026, 5, 21, 9, 0, 0),
            "forecast_horizon_h": 24,
            "forecast_confidence": 0.7,
            "asset_id": "srv-db-01",
            "forecasted_domains": {
                "storage": 0.9,
                "compute": 0.6,
                "memory": 0.2,
            },
        }
        payload.update(overrides)
        return payload


# =============================================================================
# REACTIVE backward compatibility
# =============================================================================


class ReactiveBackwardCompatTests(_Base):
    def test_reactive_mode_default(self):
        result = RCAEngine.analyze(self.make_incident())
        self.assertIsInstance(result, RootCauseResult)
        self.assertEqual(result.mode, RCA_MODE_REACTIVE)
        self.assertIsNone(result.forecast_horizon_h)
        self.assertIsNone(result.forecast_confidence)
        # Existing behavior tetap menghasilkan domain dari active_domains.
        self.assertIn(result.root_domain, {"compute", "memory"})


# =============================================================================
# FORWARD mode
# =============================================================================


class ForwardModeTests(_Base):
    def test_forward_basic_payload(self):
        result = RCAEngine.analyze_forward(self.make_forecast())
        self.assertEqual(result.mode, RCA_MODE_FORWARD)
        self.assertEqual(result.forecast_horizon_h, 24)
        self.assertAlmostEqual(result.forecast_confidence, 0.7)
        self.assertEqual(result.metadata.get("mode_origin"), "forward")
        self.assertEqual(result.metadata.get("asset_id"), "srv-db-01")
        # Domain probabilities harus berasal dari forecasted_domains.
        self.assertSetEqual(
            set(result.domain_probabilities.keys()),
            {"storage", "compute", "memory"},
        )

    def test_forward_empty_payload(self):
        result = RCAEngine.analyze_forward({"incident_id": "fwd-empty"})
        self.assertEqual(result.mode, RCA_MODE_FORWARD)
        self.assertEqual(result.root_domain, "unknown")
        self.assertEqual(result.causal_chain, [])

    def test_forward_low_confidence_triggers_governance(self):
        result = RCAEngine.analyze_forward(
            self.make_forecast(forecast_confidence=0.3)
        )
        self.assertTrue(result.governance.get("forward_low_confidence"))
        self.assertTrue(result.governance.get("governance_flag"))

    def test_forward_high_confidence_no_governance_flag(self):
        result = RCAEngine.analyze_forward(
            self.make_forecast(forecast_confidence=0.9)
        )
        self.assertFalse(result.governance.get("forward_low_confidence", False))


# =============================================================================
# HYBRID mode
# =============================================================================


class HybridModeTests(_Base):
    def test_hybrid_basic(self):
        result = RCAEngine.analyze_hybrid(
            self.make_incident(),
            self.make_forecast(),
            forecast_weight=0.4,
        )
        self.assertEqual(result.mode, RCA_MODE_HYBRID)
        self.assertEqual(result.forecast_horizon_h, 24)
        self.assertEqual(result.metadata.get("forecast_weight"), 0.4)
        self.assertIn("reactive_root", result.metadata)
        self.assertIn("forward_root", result.metadata)

    def test_hybrid_probabilities_normalized(self):
        result = RCAEngine.analyze_hybrid(
            self.make_incident(),
            self.make_forecast(),
        )
        total = sum(result.domain_probabilities.values())
        self.assertAlmostEqual(total, 1.0, places=4)

    def test_hybrid_invalid_weight(self):
        with self.assertRaises(ValueError):
            RCAEngine.analyze_hybrid(
                self.make_incident(),
                self.make_forecast(),
                forecast_weight=1.5,
            )
        with self.assertRaises(ValueError):
            RCAEngine.analyze_hybrid(
                self.make_incident(),
                self.make_forecast(),
                forecast_weight=-0.1,
            )

    def test_hybrid_weight_zero_equals_reactive(self):
        # forecast_weight=0 → seluruh bobot ke reactive
        hybrid = RCAEngine.analyze_hybrid(
            self.make_incident(),
            self.make_forecast(),
            forecast_weight=0.0,
        )
        reactive = RCAEngine.analyze(self.make_incident())
        self.assertEqual(hybrid.root_domain, reactive.root_domain)

    def test_hybrid_weight_one_equals_forward(self):
        # forecast_weight=1 → seluruh bobot ke forward
        hybrid = RCAEngine.analyze_hybrid(
            self.make_incident(),
            self.make_forecast(),
            forecast_weight=1.0,
        )
        forward = RCAEngine.analyze_forward(self.make_forecast())
        self.assertEqual(hybrid.root_domain, forward.root_domain)


# =============================================================================
# Serialization
# =============================================================================


class RCASerializationTests(_Base):
    def test_forward_to_dict_includes_new_fields(self):
        result = RCAEngine.analyze_forward(self.make_forecast())
        d = result.to_dict()
        self.assertEqual(d["mode"], "forward")
        self.assertEqual(d["forecast_horizon_h"], 24)
        self.assertIn("entropy", d)
        self.assertIn("governance", d)


if __name__ == "__main__":
    unittest.main()
