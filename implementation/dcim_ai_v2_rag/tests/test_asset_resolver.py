"""
Unit tests untuk dcim_ai/domain/asset_resolver.py.

Test ini tidak butuh DB / NetBox — hanya menulis YAML temporer
dan memvalidasi resolver.
"""

from __future__ import annotations

import os
import tempfile
import textwrap
import unittest

from dcim_ai.contracts import CriticalityTier
from dcim_ai.domain.asset_resolver import (
    CompositeAssetResolver,
    NetBoxAssetResolver,
    StaticYamlAssetResolver,
)


SAMPLE_YAML = textwrap.dedent(
    """
    assets:
      - asset_id: srv-1
        site: jkt-1
        rack: R-12
        zone: cooling_zone_2
        criticality: tier1
        role: database
        upstream_pdu: PDU-05
        upstream_ups: UPS-A
        notes: "primary DB"
      - asset_id: srv-2
        site: jkt-1
        rack: R-13
        criticality: tier3
        role: dev
    """
).strip()


class StaticYamlAssetResolverTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(
            "w", suffix=".yaml", delete=False, encoding="utf-8"
        )
        self.tmp.write(SAMPLE_YAML)
        self.tmp.flush()
        self.tmp.close()
        self.resolver = StaticYamlAssetResolver(yaml_path=self.tmp.name)

    def tearDown(self):
        try:
            os.unlink(self.tmp.name)
        except OSError:
            pass

    def test_resolve_known(self):
        ctx = self.resolver.resolve("srv-1")
        self.assertEqual(ctx.asset_id, "srv-1")
        self.assertEqual(ctx.rack, "R-12")
        self.assertEqual(ctx.criticality, CriticalityTier.TIER1)
        self.assertEqual(ctx.upstream_pdu, "PDU-05")
        self.assertEqual(ctx.extra.get("notes"), "primary DB")
        self.assertTrue(ctx.is_resolved)

    def test_resolve_unknown(self):
        ctx = self.resolver.resolve("srv-does-not-exist")
        self.assertEqual(ctx.criticality, CriticalityTier.UNKNOWN)
        self.assertFalse(ctx.is_resolved)

    def test_resolve_many(self):
        results = self.resolver.resolve_many(["srv-1", "srv-2", "srv-x"])
        self.assertEqual(len(results), 3)
        self.assertTrue(results["srv-1"].is_resolved)
        self.assertTrue(results["srv-2"].is_resolved)
        self.assertFalse(results["srv-x"].is_resolved)


class CompositeAssetResolverTests(unittest.TestCase):
    def test_fallback_to_yaml_when_netbox_unconfigured(self):
        with tempfile.NamedTemporaryFile(
            "w", suffix=".yaml", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(SAMPLE_YAML)
            yaml_path = fh.name
        try:
            yaml_resolver = StaticYamlAssetResolver(yaml_path=yaml_path)
            netbox_stub = NetBoxAssetResolver(url=None, token=None)
            composite = CompositeAssetResolver(netbox_stub, yaml_resolver)

            ctx = composite.resolve("srv-1")
            # NetBox stub return UNKNOWN, harus fallback ke YAML
            self.assertEqual(ctx.criticality, CriticalityTier.TIER1)
            self.assertEqual(ctx.rack, "R-12")
        finally:
            os.unlink(yaml_path)

    def test_empty_resolvers_raises(self):
        with self.assertRaises(ValueError):
            CompositeAssetResolver()


if __name__ == "__main__":
    unittest.main()
