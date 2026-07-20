"""
External incident state store untuk DCIM Operations Agent.

Menutup gap `memory` dan `multiturn`: incident state disimpan di luar konteks
model (SQLite, stdlib only) dan di-inject ulang tiap turn. Model TIDAK mengandalkan
ingatan percakapan — ia hanya membaca snapshot terbaru. Ini menghilangkan sumber
fabrikasi (mis. nilai CPU lama dari turn sebelumnya dipakai sebagai kebenaran).

Field state mengikuti yang disebut di PRE_EXECUTION_CHECKLIST Fase 1:
  incident_id, device, metrics_snapshot, steps_done, pending_action.

Dipakai oleh context engine sebelum memanggil
``build_dcim_operations_messages`` — section ``incident_state`` diisi dari sini.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


DEFAULT_DB_PATH = Path(__file__).parent / "state" / "incident_state.db"


@dataclass
class IncidentState:
    incident_id: str
    device: str = ""
    status: str = "investigating"
    metrics_snapshot: Dict[str, Any] = field(default_factory=dict)
    steps_done: List[str] = field(default_factory=list)
    pending_action: Optional[Dict[str, Any]] = None
    updated_at: str = ""  # caller-supplied ISO timestamp (model must not invent time)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class IncidentStateStore:
    """SQLite-backed incident state. One row per incident_id, last-write-wins."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path))
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incident_state (
                incident_id   TEXT PRIMARY KEY,
                device        TEXT NOT NULL DEFAULT '',
                status        TEXT NOT NULL DEFAULT 'investigating',
                metrics_json  TEXT NOT NULL DEFAULT '{}',
                steps_json    TEXT NOT NULL DEFAULT '[]',
                pending_json  TEXT,
                updated_at    TEXT NOT NULL DEFAULT ''
            )
            """
        )
        self._conn.commit()

    # ---- write ----
    def upsert(self, state: IncidentState) -> None:
        self._conn.execute(
            """
            INSERT INTO incident_state
                (incident_id, device, status, metrics_json, steps_json, pending_json, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(incident_id) DO UPDATE SET
                device=excluded.device,
                status=excluded.status,
                metrics_json=excluded.metrics_json,
                steps_json=excluded.steps_json,
                pending_json=excluded.pending_json,
                updated_at=excluded.updated_at
            """,
            (
                state.incident_id,
                state.device,
                state.status,
                json.dumps(state.metrics_snapshot, ensure_ascii=False),
                json.dumps(state.steps_done, ensure_ascii=False),
                json.dumps(state.pending_action, ensure_ascii=False) if state.pending_action is not None else None,
                state.updated_at,
            ),
        )
        self._conn.commit()

    def record_step(self, incident_id: str, step: str, updated_at: str) -> None:
        st = self.get(incident_id) or IncidentState(incident_id=incident_id)
        st.steps_done.append(step)
        st.updated_at = updated_at
        self.upsert(st)

    def update_metrics(self, incident_id: str, snapshot: Dict[str, Any], updated_at: str) -> None:
        """Replace metrics snapshot (always latest-wins to avoid stale fabrication)."""
        st = self.get(incident_id) or IncidentState(incident_id=incident_id)
        st.metrics_snapshot = snapshot
        st.updated_at = updated_at
        self.upsert(st)

    # ---- read ----
    def get(self, incident_id: str) -> Optional[IncidentState]:
        cur = self._conn.execute(
            "SELECT incident_id, device, status, metrics_json, steps_json, pending_json, updated_at "
            "FROM incident_state WHERE incident_id = ?",
            (incident_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        return IncidentState(
            incident_id=row[0],
            device=row[1],
            status=row[2],
            metrics_snapshot=json.loads(row[3]),
            steps_done=json.loads(row[4]),
            pending_action=json.loads(row[5]) if row[5] is not None else None,
            updated_at=row[6],
        )

    def as_context_section(self, incident_id: str) -> Dict[str, Any]:
        """Return the `incident_state` section to inject into model context.

        Returns an empty-but-valid shell when the incident is unknown, so the
        model still sees explicit empty fields instead of hallucinating.
        """
        st = self.get(incident_id)
        if st is None:
            return {
                "incident_id": incident_id,
                "device": "",
                "status": "investigating",
                "metrics_snapshot": {},
                "steps_done": [],
                "pending_action": None,
                "updated_at": "",
            }
        return st.to_dict()

    def close(self) -> None:
        self._conn.close()


__all__ = ["IncidentState", "IncidentStateStore", "DEFAULT_DB_PATH"]
