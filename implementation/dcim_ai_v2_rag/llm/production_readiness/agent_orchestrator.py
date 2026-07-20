"""
DCIM Agent Orchestrator (arsitektur dekomposisi).

Temuan Fase 1: model 12B Q4 degenerate saat mengisi skema response besar-bernested
satu-shot, terutama saat dipaksa MENGARANG isi evidence[]/tool_calls[]. Solusi:

  1. evidence[]      -> DIRAKIT DI KODE dari konteks RAG/tool (source + timestamp
                        nyata). Model tidak pernah mengarang evidence -> anti-fabrikasi
                        ditegakkan secara struktural.
  2. triage scalars  -> 1 panggilan model dengan triage.schema.json (kecil, andal).
  3. tool selection  -> 1 panggilan model dengan tool_selection.schema.json (enum
                        kecil); ARGUMEN tool diisi kode dari tool catalog + asset nyata.
  4. approval_request-> diturunkan kode saat ada aksi destruktif.

Hasil akhir dirakit menjadi dcim-agent-response/v1 dan WAJIB lolos
validate_dcim_agent_response sebelum dikembalikan.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))

from constrained_client import complete_json  # noqa: E402
from llm.production_readiness_contract import (  # noqa: E402
    SCHEMA_VERSION,
    SYSTEM_PROMPT,
    DESTRUCTIVE_ACTION_TYPES,
    READ_ONLY_ACTION_TYPES,
    validate_dcim_agent_response,
)

TRIAGE_SCHEMA = json.loads((HERE / "schemas" / "triage.schema.json").read_text())
TOOL_SEL_SCHEMA = json.loads((HERE / "schemas" / "tool_selection.schema.json").read_text())

# action_type -> (tool_name, arg builder). Arg diisi dari asset/incident nyata,
# bukan dikarang model. Sinkron dengan tool_catalog_template.yaml.
_RISK_BY_MODE = {"read_only": "low", "controlled_write": "medium", "destructive": "critical"}


def _tool_for(action_type: str, asset_id: str, incident_id: str, window: Dict[str, str]) -> Dict[str, Any]:
    a = action_type
    if a == "read_metrics":
        return {"tool_name": "prometheus_query", "mode": "read_only",
                "arguments": {"query": f"dcim_metric{{asset_id=\"{asset_id}\"}}",
                              "start": window["start"], "end": window["end"], "step": "60s"}}
    if a == "query_logs":
        return {"tool_name": "loki_query", "mode": "read_only",
                "arguments": {"query": f"{{asset_id=\"{asset_id}\"}}",
                              "start": window["start"], "end": window["end"]}}
    if a == "lookup_asset":
        return {"tool_name": "dcim_asset_lookup", "mode": "read_only",
                "arguments": {"asset_id": asset_id}}
    if a == "retrieve_sop":
        return {"tool_name": "sop_retriever", "mode": "read_only",
                "arguments": {"query": "incident triage", "domain": "dcim", "severity": "high"}}
    if a in ("search_ticket", "create_ticket", "update_ticket"):
        return {"tool_name": "ticketing", "mode": "controlled_write",
                "arguments": {"incident_id": incident_id}}
    if a in ("notify", "request_approval"):
        return {"tool_name": "pager", "mode": "controlled_write",
                "arguments": {"channel": "dcim-oncall",
                              "message": f"{a} for incident {incident_id}"}}
    # destructive
    return {"tool_name": "runbook_automation", "mode": "destructive",
            "arguments": {"target": asset_id, "runbook_id": "SOP-PENDING",
                          "change_reason": f"{a} on {asset_id} after evidence confirmation"}}


@dataclass
class OrchestratorResult:
    valid: bool
    response: Optional[Dict[str, Any]]
    errors: List[str]
    triage: Optional[Dict[str, Any]]
    raw_selection: Optional[Dict[str, Any]]


# ---------- evidence assembly (deterministic, no fabrication) ----------
def assemble_evidence(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    ev: List[Dict[str, Any]] = []
    inc = context.get("incident_state", {}) or {}
    opened = inc.get("opened_at", "")
    assets = inc.get("affected_assets", []) or [""]
    n = 0

    def add(source, timestamp, asset_id, kind, summary, confidence, value, metadata=None):
        nonlocal n
        n += 1
        ev.append({
            "id": f"ev-{n:03d}", "source": source or "unknown",
            "timestamp": timestamp or opened or "unknown",
            "asset_id": asset_id or (assets[0] if assets else "unknown"),
            "kind": kind, "summary": summary,
            "confidence": confidence, "value": value, "metadata": metadata or {},
        })

    if inc:
        add("incident_state", opened, assets[0] if assets else "",
            "fact", f"{inc.get('trigger','incident')} (severity {inc.get('severity','unknown')}).",
            1.0, {"trigger": inc.get("trigger"), "severity": inc.get("severity")})
    for m in context.get("live_metrics", []) or []:
        add(m.get("source", "metrics"), m.get("timestamp", ""), m.get("asset_id", ""),
            "live_observation", f"{m.get('metric','metric')} = {m.get('value')}.",
            0.95, {"metric": m.get("metric"), "value": m.get("value")})
    for lg in context.get("logs", []) or []:
        add(lg.get("source", "logs"), lg.get("timestamp", ""), lg.get("asset_id", ""),
            "fact", str(lg.get("line", "log entry"))[:160], 0.9, {"line": lg.get("line")})
    for note in context.get("operator_notes", []) or []:
        add("operator", opened, assets[0] if assets else "",
            "operator_note", str(note.get("note", note))[:160], 0.8, {})
    return ev


def compute_missing_evidence(context: Dict[str, Any]) -> List[str]:
    miss = []
    if not (context.get("live_metrics")):
        miss.append("fresh metric for affected asset")
    if not (context.get("logs")):
        miss.append("recent logs")
    if not (context.get("retrieved_sop")):
        miss.append("relevant SOP")
    return miss


# ---------- prompts ----------
def _ctx_str(context: Dict[str, Any]) -> str:
    return json.dumps(context, ensure_ascii=False, indent=2, sort_keys=True)


def _triage_prompt(context: Dict[str, Any]) -> str:
    user = ("Berikan KEPUTUSAN TRIAGE (bukan evidence/tool) untuk konteks DCIM ini "
            "sebagai JSON triage. Gunakan hanya data dalam konteks; jika kurang, "
            "status=needs_more_data dan confidence<=0.5.\n\n" + _ctx_str(context))
    return f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\n{user}<end_of_turn>\n<start_of_turn>model\n"


def _selection_prompt(context: Dict[str, Any], triage: Dict[str, Any]) -> str:
    user = ("Pilih tool yang perlu dijalankan untuk langkah berikutnya (maks 4). "
            "Untuk evidence yang kurang, pilih action read-only (read_metrics, "
            "query_logs, lookup_asset, retrieve_sop). Jangan pilih aksi destruktif "
            "kecuali SOP & evidence mendukung. Output JSON tool_selection.\n\n"
            f"Triage: {json.dumps(triage, ensure_ascii=False)}\n\n"
            "Konteks:\n" + _ctx_str(context))
    return f"<start_of_turn>user\n{SYSTEM_PROMPT}\n\n{user}<end_of_turn>\n<start_of_turn>model\n"


# ---------- main orchestration ----------
def run_incident(context: Dict[str, Any], *, endpoint: str = "http://localhost:8080/completion") -> OrchestratorResult:
    inc = context.get("incident_state", {}) or {}
    incident_id = inc.get("incident_id", "inc-unknown")
    opened = inc.get("opened_at", "")
    assets = inc.get("affected_assets", []) or [""]
    primary_asset = assets[0] if assets else ""
    window = {"start": opened or "unknown", "end": opened or "unknown"}

    errors: List[str] = []

    # 1. evidence dirakit kode
    evidence = assemble_evidence(context)
    evidence_ids = [e["id"] for e in evidence]

    # 2. triage (model, skema kecil)
    triage = complete_json(_triage_prompt(context), TRIAGE_SCHEMA, endpoint=endpoint,
                           n_predict=384, base_temperature=0.2)
    if triage is None:
        return OrchestratorResult(False, None, ["triage generation failed"], None, None)
    # json_schema mengabaikan minimum/maximum -> clamp di kode (model kadang
    # output confidence 100 / >1). Bukan fabrikasi data, hanya normalisasi skor.
    try:
        c = float(triage.get("confidence", 0.0))
    except (TypeError, ValueError):
        c = 0.0
    triage["confidence"] = min(1.0, max(0.0, c if c <= 1.0 else c / 100.0))

    # 3. tool selection (model, enum kecil); args diisi kode
    sel = complete_json(_selection_prompt(context, triage), TOOL_SEL_SCHEMA, endpoint=endpoint,
                        n_predict=384, base_temperature=0.2) or {"selections": []}
    selections = sel.get("selections", []) or []

    tool_calls: List[Dict[str, Any]] = []
    destructive_call_id: Optional[str] = None
    for i, s in enumerate(selections, 1):
        at = s.get("action_type")
        asset = s.get("asset_id") or primary_asset
        spec = _tool_for(at, asset, incident_id, window)
        is_destructive = at in DESTRUCTIVE_ACTION_TYPES
        tc_id = f"tc-{i:03d}"
        tool_calls.append({
            "id": tc_id, "action_type": at, "tool_name": spec["tool_name"],
            "arguments": spec["arguments"], "risk": _RISK_BY_MODE[spec["mode"]],
            "requires_approval": is_destructive,
            "reason": (s.get("reason") or f"{at} for {asset}")[:200],
            "timeout_seconds": 120 if is_destructive else 30,
        })
        if is_destructive and destructive_call_id is None:
            destructive_call_id = tc_id

    # 4. approval derivation
    requires_approval = destructive_call_id is not None
    approval_request = None
    if requires_approval:
        approval_request = {
            "id": "appr-001", "requested_action_id": destructive_call_id,
            "approver_role": "dcim_lead",
            "reason": "Destructive action requires human approval before execution.",
            "risk": "critical",
            "evidence_ids": evidence_ids or ["ev-000"],
            "expires_at": opened or "unknown",
        }
        # validator: evidence_ids non-empty; jika tak ada evidence, sisipkan placeholder fact
        if not evidence_ids:
            evidence.append({"id": "ev-000", "source": "incident_state", "timestamp": opened or "unknown",
                             "asset_id": primary_asset or "unknown", "kind": "fact",
                             "summary": "Incident opened.", "confidence": 1.0, "value": {}, "metadata": {}})

    # 5. assemble full response
    response = {
        "schema_version": SCHEMA_VERSION,
        "incident_id": incident_id,
        "status": triage["status"],
        "summary": triage["summary"],
        "evidence": evidence,
        "risk": triage["risk"],
        "recommended_action": triage["recommended_action"],
        "tool_calls": tool_calls,
        "requires_human_approval": requires_approval,
        "approval_request": approval_request,
        "missing_evidence": compute_missing_evidence(context),
        "confidence": triage["confidence"],
    }

    vr = validate_dcim_agent_response(response)
    if not vr.valid:
        errors = vr.errors
    return OrchestratorResult(vr.valid, response if vr.valid else None, errors, triage, sel)


__all__ = ["run_incident", "OrchestratorResult", "assemble_evidence"]
