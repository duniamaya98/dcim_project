"""
DCIM AI — Model Registry (extended v1.2.0)

Existing functions (register_model, activate_model, get_active_model)
DIPERTAHANKAN apa adanya untuk backward compatibility dengan kode lama
yang masih memanggil API ini.

Tambahan v1.2.0 (MT-019 §6.2):
    - register_model_v2()       — multi-model dengan field type/domain/inference_mode
    - activate_model_v2()       — promote per (model_name, model_type)
    - get_active_model_v2()     — kembalikan dict lengkap, bukan hanya artifact_path
    - list_models_by_type()
    - list_models_by_domain()

Field tambahan disimpan via kolom baru pada tabel `model_registry`. Migration
idempotent dijalankan otomatis saat fungsi v2 dipakai pertama kali, sehingga
schema lama (yang sudah jalan di production) tidak perlu di-migrate paksa.
Migration penuh juga tersedia di:
    dcim_ai/registry/sql/migrations/2026_05_20_v1_2_0_multi_model.sql
"""

from sqlalchemy import text
import json
from typing import Any, Dict, List, Optional

from dcim_ai.core.data_loader import get_db_engine

engine = get_db_engine()


# ============================================================================
# Legacy API — DO NOT BREAK
# ============================================================================


def register_model(model_name, version, contamination, training_window, artifact_path, metrics):
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO model_registry 
            (model_name, version, contamination, training_window, artifact_path, metrics_json)
            VALUES (:model_name, :version, :contamination, :training_window, :artifact_path, :metrics)
        """), {
            "model_name": model_name,
            "version": version,
            "contamination": contamination,
            "training_window": training_window,
            "artifact_path": artifact_path,
            "metrics": json.dumps(metrics)
        })
        conn.commit()


def activate_model(model_name, version):
    with engine.connect() as conn:
        conn.execute(text("""
            UPDATE model_registry
            SET is_active = FALSE
            WHERE model_name = :model_name
        """), {"model_name": model_name})

        conn.execute(text("""
            UPDATE model_registry
            SET is_active = TRUE
            WHERE model_name = :model_name
              AND version = :version
        """), {"model_name": model_name, "version": version})

        conn.commit()


def get_active_model(model_name):
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT artifact_path
            FROM model_registry
            WHERE model_name = :model_name
            AND is_active = TRUE
            LIMIT 1
        """), {"model_name": model_name})

        row = result.fetchone()

        if row is None:
            return None

        # SQLAlchemy 2.x safe access
        return row._mapping["artifact_path"]


# ============================================================================
# v1.2.0 — Multi-model registry (MT-019 §6.2)
# ============================================================================


# Tipe model yang dikenali — sinkron dengan dcim_ai.contracts.ModelType
VALID_MODEL_TYPES = {
    "anomaly",
    "forecast",
    "clustering",
    "energy_anomaly",
    "capacity_optimizer",
}

VALID_INFERENCE_MODES = {"batch", "streaming", "scheduled"}

# Versi data contract default — naik bila ada breaking change pada
# kontrak InferenceResult / RootCauseResult / dst.
DEFAULT_DATA_CONTRACT_VERSION = "1.2.0"


def _ensure_v2_columns(conn) -> None:
    """
    Tambah kolom v1.2.0 secara idempotent bila migration belum dijalankan.
    Tujuan: register_model_v2() bisa dipakai langsung di lab tanpa
    perlu menjalankan SQL migration manual lebih dulu.
    """
    conn.execute(text("""
        ALTER TABLE model_registry
            ADD COLUMN IF NOT EXISTS model_type            TEXT,
            ADD COLUMN IF NOT EXISTS domain                TEXT,
            ADD COLUMN IF NOT EXISTS inference_mode        TEXT,
            ADD COLUMN IF NOT EXISTS data_contract_version TEXT
    """))


def register_model_v2(
    *,
    model_name: str,
    version: str,
    model_type: str,
    domain: str,
    artifact_path: str,
    inference_mode: str = "batch",
    contamination: Optional[float] = None,
    training_window: Optional[str] = None,
    metrics: Optional[Dict[str, Any]] = None,
    data_contract_version: str = DEFAULT_DATA_CONTRACT_VERSION,
) -> None:
    """
    Register model dengan metadata multi-model.

    Backward compat: untuk model_type='anomaly', record juga ditulis ke
    kolom legacy (contamination, training_window) agar tooling lama
    tetap berjalan.
    """
    if model_type not in VALID_MODEL_TYPES:
        raise ValueError(
            f"Invalid model_type={model_type!r}. "
            f"Allowed: {sorted(VALID_MODEL_TYPES)}"
        )
    if inference_mode not in VALID_INFERENCE_MODES:
        raise ValueError(
            f"Invalid inference_mode={inference_mode!r}. "
            f"Allowed: {sorted(VALID_INFERENCE_MODES)}"
        )

    metrics = metrics or {}
    metrics_with_meta = dict(metrics)
    metrics_with_meta["registry_meta"] = {
        "model_type": model_type,
        "domain": domain,
        "inference_mode": inference_mode,
        "data_contract_version": data_contract_version,
    }

    with engine.connect() as conn:
        _ensure_v2_columns(conn)
        conn.execute(text("""
            INSERT INTO model_registry
                (model_name, version, contamination, training_window,
                 artifact_path, metrics_json,
                 model_type, domain, inference_mode, data_contract_version)
            VALUES
                (:model_name, :version, :contamination, :training_window,
                 :artifact_path, :metrics,
                 :model_type, :domain, :inference_mode, :dcv)
        """), {
            "model_name": model_name,
            "version": version,
            "contamination": contamination,
            "training_window": training_window,
            "artifact_path": artifact_path,
            "metrics": json.dumps(metrics_with_meta),
            "model_type": model_type,
            "domain": domain,
            "inference_mode": inference_mode,
            "dcv": data_contract_version,
        })
        conn.commit()


def activate_model_v2(*, model_name: str, model_type: str, version: str) -> None:
    """
    Aktivasi model per (model_name, model_type).

    Berbeda dengan activate_model() lama yang men-deactivate seluruh
    record untuk model_name, varian v2 hanya men-deactivate record
    dengan model_type yang sama agar coexistence multi-type bekerja
    (mis. anomaly + forecast aktif bersamaan).
    """
    with engine.connect() as conn:
        _ensure_v2_columns(conn)
        conn.execute(text("""
            UPDATE model_registry
            SET is_active = FALSE
            WHERE model_name = :model_name
              AND COALESCE(model_type, 'anomaly') = :model_type
        """), {"model_name": model_name, "model_type": model_type})

        conn.execute(text("""
            UPDATE model_registry
            SET is_active = TRUE
            WHERE model_name = :model_name
              AND COALESCE(model_type, 'anomaly') = :model_type
              AND version = :version
        """), {
            "model_name": model_name,
            "model_type": model_type,
            "version": version,
        })

        conn.commit()


def get_active_model_v2(model_name: str, model_type: str = "anomaly") -> Optional[Dict[str, Any]]:
    """
    Ambil record aktif lengkap untuk (model_name, model_type).
    Return dict, atau None bila tidak ada.
    """
    with engine.connect() as conn:
        _ensure_v2_columns(conn)
        result = conn.execute(text("""
            SELECT model_name, version, artifact_path, metrics_json,
                   COALESCE(model_type, 'anomaly')           AS model_type,
                   domain,
                   COALESCE(inference_mode, 'batch')         AS inference_mode,
                   COALESCE(data_contract_version, '1.0.0')  AS data_contract_version
            FROM model_registry
            WHERE model_name = :model_name
              AND COALESCE(model_type, 'anomaly') = :model_type
              AND is_active = TRUE
            ORDER BY id DESC
            LIMIT 1
        """), {"model_name": model_name, "model_type": model_type})

        row = result.fetchone()
        if row is None:
            return None

        m = row._mapping
        metrics_json = m["metrics_json"]
        if isinstance(metrics_json, str):
            try:
                metrics_json = json.loads(metrics_json)
            except (TypeError, ValueError):
                metrics_json = {}

        return {
            "model_name": m["model_name"],
            "version": m["version"],
            "artifact_path": m["artifact_path"],
            "model_type": m["model_type"],
            "domain": m["domain"],
            "inference_mode": m["inference_mode"],
            "data_contract_version": m["data_contract_version"],
            "metrics": metrics_json or {},
        }


def list_models_by_type(model_type: str) -> List[Dict[str, Any]]:
    """List semua versi untuk model_type tertentu (semua model_name)."""
    with engine.connect() as conn:
        _ensure_v2_columns(conn)
        result = conn.execute(text("""
            SELECT model_name, version, is_active, domain,
                   COALESCE(inference_mode, 'batch') AS inference_mode,
                   artifact_path
            FROM model_registry
            WHERE COALESCE(model_type, 'anomaly') = :model_type
            ORDER BY model_name, id DESC
        """), {"model_type": model_type})
        return [dict(r._mapping) for r in result.fetchall()]


def list_models_by_domain(domain: str) -> List[Dict[str, Any]]:
    """List model untuk domain tertentu (mis. 'power' untuk UC3)."""
    with engine.connect() as conn:
        _ensure_v2_columns(conn)
        result = conn.execute(text("""
            SELECT model_name, version, is_active,
                   COALESCE(model_type, 'anomaly') AS model_type,
                   COALESCE(inference_mode, 'batch') AS inference_mode,
                   artifact_path
            FROM model_registry
            WHERE domain = :domain
            ORDER BY model_name, id DESC
        """), {"domain": domain})
        return [dict(r._mapping) for r in result.fetchall()]


__all__ = [
    # legacy
    "register_model",
    "activate_model",
    "get_active_model",
    # v1.2.0
    "register_model_v2",
    "activate_model_v2",
    "get_active_model_v2",
    "list_models_by_type",
    "list_models_by_domain",
    "VALID_MODEL_TYPES",
    "VALID_INFERENCE_MODES",
    "DEFAULT_DATA_CONTRACT_VERSION",
]