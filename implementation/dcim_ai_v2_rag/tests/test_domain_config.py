"""
Unit tests untuk dcim_ai/domain/domain_config.py addendum v1.2.0.
"""

from __future__ import annotations

import unittest

from dcim_ai.domain.domain_config import (
    CAUSAL_TOPOLOGY_DEFAULT,
    DOMAIN_ACTIVATION_THRESHOLD,
    DOMAIN_CRITICALITY_WEIGHTS,
    DOMAIN_FEATURE_MAP,
    DOMAIN_SEVERITY_WEIGHT,
    active_domains_for,
)


class DomainConfigTests(unittest.TestCase):
    def test_existing_domains_preserved(self):
        # Backward compat: 4 domain awal harus tetap ada dengan fitur sama.
        self.assertIn("compute", DOMAIN_FEATURE_MAP)
        self.assertIn("memory", DOMAIN_FEATURE_MAP)
        self.assertIn("storage", DOMAIN_FEATURE_MAP)
        self.assertIn("network", DOMAIN_FEATURE_MAP)
        self.assertEqual(DOMAIN_FEATURE_MAP["compute"], ["cpu_usage"])
        self.assertEqual(DOMAIN_FEATURE_MAP["network"], ["net_rx", "net_tx"])

    def test_new_domains_present(self):
        self.assertIn("power", DOMAIN_FEATURE_MAP)
        self.assertIn("cooling", DOMAIN_FEATURE_MAP)
        self.assertIn("hardware", DOMAIN_FEATURE_MAP)
        self.assertIn("pue", DOMAIN_FEATURE_MAP["power"])
        self.assertIn("temp_inlet", DOMAIN_FEATURE_MAP["cooling"])
        self.assertIn("smart_temp", DOMAIN_FEATURE_MAP["hardware"])

    def test_criticality_weights(self):
        self.assertGreater(
            DOMAIN_CRITICALITY_WEIGHTS["power"],
            DOMAIN_CRITICALITY_WEIGHTS["compute"],
        )
        self.assertGreater(
            DOMAIN_CRITICALITY_WEIGHTS["cooling"],
            DOMAIN_CRITICALITY_WEIGHTS["network"],
        )

    def test_severity_weight_has_new_domains(self):
        self.assertIn("power", DOMAIN_SEVERITY_WEIGHT)
        self.assertIn("cooling", DOMAIN_SEVERITY_WEIGHT)
        self.assertIn("hardware", DOMAIN_SEVERITY_WEIGHT)

    def test_activation_threshold_unchanged(self):
        self.assertEqual(DOMAIN_ACTIVATION_THRESHOLD, 3.0)

    def test_active_domains_for_legacy_features(self):
        # Hanya feature lama tersedia → hanya domain lama yang aktif.
        active = set(
            active_domains_for(
                ["cpu_usage", "memory_usage", "disk_io", "net_rx", "net_tx"]
            )
        )
        self.assertSetEqual(active, {"compute", "memory", "storage", "network"})

    def test_active_domains_for_power_features(self):
        active = set(active_domains_for(["power_w", "voltage", "pue"]))
        self.assertEqual(active, {"power"})

    def test_active_domains_for_environment(self):
        active = set(active_domains_for(["temp_inlet", "humidity"]))
        self.assertEqual(active, {"cooling"})

    def test_active_domains_empty(self):
        self.assertEqual(active_domains_for([]), [])
        self.assertEqual(active_domains_for(None), [])

    def test_causal_topology_includes_new_edges(self):
        edges = set(CAUSAL_TOPOLOGY_DEFAULT)
        self.assertIn(("power", "compute"), edges)
        self.assertIn(("power", "cooling"), edges)
        self.assertIn(("cooling", "compute"), edges)
        self.assertIn(("hardware", "storage"), edges)


if __name__ == "__main__":
    unittest.main()
