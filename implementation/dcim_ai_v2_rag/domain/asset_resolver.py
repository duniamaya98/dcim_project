"""
DCIM AI — Asset Context Resolver (MT-020 §6.4)

Implementasi konkret dari `AssetContextResolver` Protocol di contracts/.
Menyediakan dua backend:

1. StaticYamlAssetResolver
   - Sumber: file YAML lokal.
   - Cocok untuk dev, testing, atau lingkungan tanpa NetBox.
   - Path default: dcim_ai/config/asset_inventory.yaml

2. NetBoxAssetResolver (stub)
   - Sumber: NetBox API via pynetbox.
   - Implementasi minimal — fokus integrasi nanti saat UC2 kick-off.

3. CompositeAssetResolver
   - Mencoba resolver utama, fallback ke resolver berikutnya.
   - Cocok untuk production: NetBox primer, YAML fallback.

Caching:
   - In-memory dict + TTL sederhana (default 5 menit).
   - Cukup untuk kebutuhan inference. Bila perlu Redis/DB, refactor di sini.
"""

from __future__ import annotations

import logging
import os
import threading
import time
from typing import Dict, Iterable, List, Optional

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    yaml = None

from dcim_ai.contracts import AssetContext, CriticalityTier

logger = logging.getLogger(__name__)


# ============================================================================
# Cache helper
# ============================================================================


class _TTLCache:
    """Cache sangat sederhana — cukup untuk skala asset registry kecil."""

    def __init__(self, ttl_seconds: int = 300):
        self._ttl = ttl_seconds
        self._data: Dict[str, tuple[float, AssetContext]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[AssetContext]:
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            ts, ctx = entry
            if time.time() - ts > self._ttl:
                self._data.pop(key, None)
                return None
            return ctx

    def set(self, key: str, value: AssetContext) -> None:
        with self._lock:
            self._data[key] = (time.time(), value)

    def clear(self) -> None:
        with self._lock:
            self._data.clear()


# ============================================================================
# Static YAML resolver
# ============================================================================


class StaticYamlAssetResolver:
    """
    Resolver berbasis file YAML.

    Format YAML yang diharapkan:

        assets:
          - asset_id: srv-01
            site: jkt-1
            rack: R-12
            zone: cooling_zone_2
            criticality: tier1
            role: database
            upstream_pdu: PDU-05
            upstream_ups: UPS-A
          - asset_id: srv-02
            ...
    """

    def __init__(
        self,
        yaml_path: Optional[str] = None,
        ttl_seconds: int = 300,
    ):
        self.yaml_path = yaml_path or os.getenv(
            "DCIM_ASSET_INVENTORY",
            "dcim_ai/config/asset_inventory.yaml",
        )
        self._cache = _TTLCache(ttl_seconds=ttl_seconds)
        self._index: Dict[str, dict] = {}
        self._mtime: Optional[float] = None
        self._load()

    # --- internal ---

    def _load(self) -> None:
        if yaml is None:
            logger.warning(
                "PyYAML tidak terinstall; StaticYamlAssetResolver tidak dapat memuat %s",
                self.yaml_path,
            )
            return
        if not os.path.exists(self.yaml_path):
            logger.info("asset_inventory.yaml belum ada di %s — akan return UNKNOWN", self.yaml_path)
            return

        try:
            mtime = os.path.getmtime(self.yaml_path)
            if self._mtime == mtime:
                return  # file tidak berubah
            with open(self.yaml_path, "r", encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
            assets = data.get("assets", [])
            self._index = {item["asset_id"]: item for item in assets if "asset_id" in item}
            self._mtime = mtime
            self._cache.clear()
            logger.info("Loaded %d assets from %s", len(self._index), self.yaml_path)
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to load asset inventory: %s", exc)

    @staticmethod
    def _to_context(asset_id: str, raw: dict) -> AssetContext:
        criticality_raw = (raw.get("criticality") or "unknown").lower()
        try:
            criticality = CriticalityTier(criticality_raw)
        except ValueError:
            criticality = CriticalityTier.UNKNOWN

        # Field eksplisit
        known = {
            "asset_id",
            "site",
            "rack",
            "zone",
            "criticality",
            "role",
            "upstream_pdu",
            "upstream_ups",
        }
        extra = {k: v for k, v in raw.items() if k not in known}

        return AssetContext(
            asset_id=asset_id,
            site=raw.get("site"),
            rack=raw.get("rack"),
            zone=raw.get("zone"),
            criticality=criticality,
            role=raw.get("role"),
            upstream_pdu=raw.get("upstream_pdu"),
            upstream_ups=raw.get("upstream_ups"),
            extra=extra,
        )

    # --- public ---

    def resolve(self, asset_id: str) -> AssetContext:
        if not asset_id:
            return AssetContext.unknown(asset_id or "")

        cached = self._cache.get(asset_id)
        if cached is not None:
            return cached

        # Hot reload bila file berubah
        self._load()

        raw = self._index.get(asset_id)
        if raw is None:
            ctx = AssetContext.unknown(asset_id)
        else:
            ctx = self._to_context(asset_id, raw)
        self._cache.set(asset_id, ctx)
        return ctx

    def resolve_many(self, asset_ids: Iterable[str]) -> Dict[str, AssetContext]:
        return {aid: self.resolve(aid) for aid in asset_ids}


# ============================================================================
# NetBox resolver (stub — diselesaikan saat UC2)
# ============================================================================


class NetBoxAssetResolver:
    """
    Stub resolver berbasis NetBox API.

    Implementasi penuh ditunda ke fase UC2 (lihat MT-020 §6.4).
    Untuk sekarang, instance ini akan selalu mengembalikan UNKNOWN
    sehingga sistem tetap aman dipakai sebelum NetBox terkonfigurasi.

    Konstruktor menerima parameter koneksi agar interface sudah final
    saat implementasi dilanjutkan.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        ttl_seconds: int = 300,
        verify_ssl: bool = True,
    ):
        self.url = url or os.getenv("NETBOX_URL")
        self.token = token or os.getenv("NETBOX_TOKEN")
        self.verify_ssl = verify_ssl
        self._cache = _TTLCache(ttl_seconds=ttl_seconds)
        self._client = None  # akan diisi pynetbox saat implementasi penuh
        if self.url and self.token:
            logger.info("NetBoxAssetResolver dikonfigurasi (stub) untuk %s", self.url)
        else:
            logger.info("NetBoxAssetResolver belum dikonfigurasi — return UNKNOWN")

    def resolve(self, asset_id: str) -> AssetContext:
        cached = self._cache.get(asset_id)
        if cached is not None:
            return cached
        # TODO(UC2): panggil pynetbox dan map ke AssetContext
        ctx = AssetContext.unknown(asset_id)
        self._cache.set(asset_id, ctx)
        return ctx


# ============================================================================
# Composite resolver
# ============================================================================


class CompositeAssetResolver:
    """
    Coba resolver pertama; bila hasilnya UNKNOWN, lanjut ke resolver berikutnya.
    Production setup yang direkomendasikan:

        CompositeAssetResolver(
            NetBoxAssetResolver(),
            StaticYamlAssetResolver(),
        )
    """

    def __init__(self, *resolvers):
        if not resolvers:
            raise ValueError("CompositeAssetResolver butuh minimal 1 resolver")
        self.resolvers = list(resolvers)

    def resolve(self, asset_id: str) -> AssetContext:
        last: Optional[AssetContext] = None
        for resolver in self.resolvers:
            ctx = resolver.resolve(asset_id)
            if ctx.is_resolved:
                return ctx
            last = ctx
        return last or AssetContext.unknown(asset_id)


# ============================================================================
# Factory
# ============================================================================


def default_resolver() -> CompositeAssetResolver:
    """
    Factory default berdasarkan environment variables:
      - NETBOX_URL & NETBOX_TOKEN  → NetBoxAssetResolver primer
      - DCIM_ASSET_INVENTORY        → StaticYamlAssetResolver fallback

    Selalu menyertakan StaticYamlAssetResolver di akhir agar dev tetap punya
    resolver yang berfungsi tanpa NetBox.
    """
    resolvers: List = []
    if os.getenv("NETBOX_URL") and os.getenv("NETBOX_TOKEN"):
        resolvers.append(NetBoxAssetResolver())
    resolvers.append(StaticYamlAssetResolver())
    return CompositeAssetResolver(*resolvers)


__all__ = [
    "StaticYamlAssetResolver",
    "NetBoxAssetResolver",
    "CompositeAssetResolver",
    "default_resolver",
]
