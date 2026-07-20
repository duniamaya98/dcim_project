"""
Tests untuk agent_orchestrator (arsitektur dekomposisi Fase 1).

Fokus pada bagian DETERMINISTIK (perakitan kode) yang tidak butuh model:
  - assemble_evidence: tidak mengarang, source/timestamp dari konteks
  - compute_missing_evidence
  - validitas response yang dirakit dari triage + selection palsu

Bagian yang butuh model (run_incident end-to-end) diuji oleh fase1_live_proof.py.
"""

import sys
from pathlib import Path

PR = Path(__file__).resolve().parents[1] / "llm" / "production_readiness"
sys.path.insert(0, str(PR))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_orchestrator import assemble_evidence, compute_missing_evidence  # noqa: E402
from llm.production_readiness_contract import validate_dcim_agent_response  # noqa: E402


CTX = {
    "incident_state": {"incident_id": "inc-1", "trigger": "pdu_overload",
                       "severity": "critical", "affected_assets": ["pdu-r12-a"],
                       "opened_at": "2026-06-12T10:00:00Z"},
    "retrieved_sop": [{"sop_id": "SOP-POWER-003", "timestamp": "2026-05-01T00:00:00Z"}],
    "live_metrics": [{"source": "prometheus", "timestamp": "2026-06-12T10:00:30Z",
                      "asset_id": "pdu-r12-a", "metric": "load_pct", "value": 96.4}],
    "logs": [], "tool_results": [],
    "asset_context": [{"asset_id": "pdu-r12-a", "rack": "R12"}], "operator_notes": [],
}


def test_evidence_not_fabricated():
    ev = assemble_evidence(CTX)
    assert ev, "harus ada evidence dari incident_state + metrics"
    # setiap evidence harus punya source & timestamp dari konteks (bukan dikarang)
    sources = {e["source"] for e in ev}
    assert "incident_state" in sources
    assert "prometheus" in sources
    for e in ev:
        assert e["timestamp"] and e["timestamp"] != "unknown"
        assert 0.0 <= e["confidence"] <= 1.0


def test_missing_evidence_flags_gaps():
    miss = compute_missing_evidence(CTX)
    assert "recent logs" in miss  # logs kosong di CTX


def test_assembled_response_passes_contract():
    # rakit response minimal dengan evidence nyata + triage palsu -> harus valid
    ev = assemble_evidence(CTX)
    response = {
        "schema_version": "dcim-agent-response/v1",
        "incident_id": "inc-1",
        "status": "needs_more_data",
        "summary": "PDU overload pada pdu-r12-a.",
        "evidence": ev,
        "risk": "high",
        "recommended_action": "Query fresh metrics sebelum aksi.",
        "tool_calls": [],
        "requires_human_approval": False,
        "approval_request": None,
        "missing_evidence": compute_missing_evidence(CTX),
        "confidence": 0.5,
    }
    vr = validate_dcim_agent_response(response)
    assert vr.valid, vr.errors


def test_empty_context_safe():
    ev = assemble_evidence({"incident_state": {}})
    # tidak error, mengembalikan list (mungkin kosong)
    assert isinstance(ev, list)
