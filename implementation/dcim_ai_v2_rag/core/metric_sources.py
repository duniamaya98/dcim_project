"""
DCIM AI — MetricSource implementations (MT-018 §11.3)

Generalisasi pipa data telemetry. Implementasi konkret dari kontrak
`MetricSource` (lihat dcim_ai/contracts/__init__.py).

Backward compatibility:
    Loader lama `dcim_ai.core.data_loader.load_training_data()` tetap
    bekerja tanpa perubahan. Modul baru ini bersifat additive.

Sumber yang didukung saat ini:

    ServerMetricsSource         — server_metrics (existing, UC1/UC2)
    PowerMetricsSource          — power_metrics (UC3)
    EnvironmentMetricsSource    — environment_metrics (UC3)
    NetBoxAssetSource           — read-only NetBox API (UC2, stub)

Catatan:
    - Semua loader memakai engine SQLAlchemy yang sama dengan
      `dcim_ai.core.data_loader.get_db_engine()` agar konfigurasi DB
      terpusat di .env / environment.
    - Query memakai parameterized statements (parameterized via SQLAlchemy
      `text()` + bindparams) untuk mencegah injection.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import List, Optional

import pandas as pd
from sqlalchemy import text

from dcim_ai.contracts import MetricSource, TimeWindow
from dcim_ai.core.data_loader import get_db_engine

logger = logging.getLogger(__name__)


# ============================================================================
# Base class with shared SQL behavior
# ============================================================================


class _SqlMetricSource(MetricSource):
    """
    Implementasi dasar MetricSource yang membaca dari TimescaleDB/Postgres.

    Subclass cukup men-set: domain, table, feature_columns, timestamp_column,
    asset_id_column.
    """

    def __init__(
        self,
        engine=None,
        feature_columns: Optional[List[str]] = None,
    ):
        self._engine = engine or get_db_engine()
        if feature_columns is not None:
            # Override per-instance (immutable di class-level karena annotation).
            self.feature_columns = list(feature_columns)

    def load(self, window: TimeWindow) -> pd.DataFrame:
        if not self.table:
            raise ValueError(f"{type(self).__name__}: 'table' tidak diset")

        cols: List[str] = [self.timestamp_column, self.asset_id_column]
        cols += [c for c in (self.feature_columns or []) if c not in cols]
        cols_sql = ", ".join(cols) if cols else "*"

        query = text(
            f"""
            SELECT {cols_sql}
            FROM {self.table}
            WHERE {self.timestamp_column} >= :start
              AND {self.timestamp_column} <  :end
            ORDER BY {self.timestamp_column} ASC
            """
        )

        with self._engine.connect() as conn:
            df = pd.read_sql(
                query, conn, params={"start": window.start, "end": window.end}
            )

        logger.debug(
            "%s loaded %d rows from %s [%s..%s]",
            type(self).__name__,
            len(df),
            self.table,
            window.start.isoformat(),
            window.end.isoformat(),
        )
        return df


# ============================================================================
# Concrete sources
# ============================================================================


class ServerMetricsSource(_SqlMetricSource):
    """Sumber existing untuk UC1 (anomaly + forecast) dan UC2 (capacity)."""

    domain = "server"
    table = "server_metrics"
    timestamp_column = "time"
    asset_id_column = "hostname"
    feature_columns = [
        "cpu_usage",
        "memory_usage",
        "disk_io",
        "net_rx",
        "net_tx",
        "temperature",
        "gpu_util",
        "gpu_mem_used",
    ]


class ServerHealthSource(_SqlMetricSource):
    """
    Sumber baru untuk UC1 — metrik hardware health (SMART, fan, hwmon).
    Tabel target: server_health (akan dibuat saat ingestion SNMP/IPMI/Redfish).
    """

    domain = "server"
    table = "server_health"
    timestamp_column = "time"
    asset_id_column = "hostname"
    feature_columns = [
        "smart_reallocated_sectors",
        "smart_pending_sectors",
        "smart_temp",
        "fan_speed",
        "hwmon_temp",
    ]


class PowerMetricsSource(_SqlMetricSource):
    """Sumber UC3 — telemetry PDU/UPS."""

    domain = "power"
    table = "power_metrics"
    timestamp_column = "time"
    asset_id_column = "device_id"
    feature_columns = [
        "power_w",
        "voltage",
        "current",
        "energy_kwh",
        "pue",
    ]


class EnvironmentMetricsSource(_SqlMetricSource):
    """Sumber UC3 — sensor lingkungan (suhu, kelembaban)."""

    domain = "cooling"
    table = "environment_metrics"
    timestamp_column = "time"
    asset_id_column = "device_id"
    feature_columns = [
        "temp_inlet",
        "temp_outlet",
        "humidity",
        "dewpoint",
    ]


class NetBoxAssetSource(MetricSource):
    """
    Stub sumber data dari NetBox API untuk UC2 (rack occupancy, asset metadata).
    Implementasi penuh ditunda ke fase UC2 (lihat MT-020 §6.4).

    Saat ini `load()` mengembalikan DataFrame kosong agar pipeline yang
    optional-nya memakai sumber ini tidak gagal.
    """

    domain = "asset"
    table = "netbox.devices"
    timestamp_column = "snapshot_time"
    asset_id_column = "name"
    feature_columns = ["rack_occupancy_u", "primary_ip", "site"]

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.url = url or os.getenv("NETBOX_URL")
        self.token = token or os.getenv("NETBOX_TOKEN")
        if not (self.url and self.token):
            logger.info("NetBoxAssetSource belum dikonfigurasi — load() return empty DataFrame")

    def load(self, window: TimeWindow) -> pd.DataFrame:  # noqa: ARG002
        if not (self.url and self.token):
            return pd.DataFrame(columns=[self.timestamp_column, self.asset_id_column] + list(self.feature_columns))
        # TODO(UC2): implement pynetbox query → DataFrame
        return pd.DataFrame(columns=[self.timestamp_column, self.asset_id_column] + list(self.feature_columns))


# ============================================================================
# Registry of sources
# ============================================================================


_SOURCES = {
    "server":      ServerMetricsSource,
    "server_health": ServerHealthSource,
    "power":       PowerMetricsSource,
    "environment": EnvironmentMetricsSource,
    "cooling":     EnvironmentMetricsSource,  # alias domain
    "netbox":      NetBoxAssetSource,
}


def get_source(name: str, **kwargs) -> MetricSource:
    """Factory sederhana untuk membuat MetricSource by name."""
    key = name.lower()
    if key not in _SOURCES:
        raise KeyError(f"Unknown metric source: {name}. Available: {sorted(_SOURCES)}")
    return _SOURCES[key](**kwargs)


def list_sources() -> List[str]:
    return sorted(_SOURCES.keys())


__all__ = [
    "ServerMetricsSource",
    "ServerHealthSource",
    "PowerMetricsSource",
    "EnvironmentMetricsSource",
    "NetBoxAssetSource",
    "get_source",
    "list_sources",
]
