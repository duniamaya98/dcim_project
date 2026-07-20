"""
Fase 1 - Bukti live: schema pass dengan arsitektur DEKOMPOSISI.

Menjalankan model produksi nyata (llama.cpp /completion) lewat agent_orchestrator:
  - evidence[]      dirakit kode dari konteks (anti-fabrikasi)
  - triage scalars  dari model (triage.schema.json, kecil & andal)
  - tool_calls[]    enum dari model + argumen diisi kode (tool_selection.schema.json)
  - hasil dirakit -> dcim-agent-response/v1 -> validate_dcim_agent_response()

Menutup item Fase 1 checklist:
  "[ ] Uji: schema pass tinggi pada 50+ sampel" (tanpa degenerate skema FULL).

Output: report markdown + raw json di results/fase1/.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent.parent))  # dcim_ai_v2_rag/ on path

from agent_orchestrator import run_incident  # noqa: E402

ENDPOINT = "http://localhost:8080/completion"

# Skenario incident kontekstual. Tiap item adalah konteks DCIM yang sudah
# di-assemble (seperti output context engine). Diulang untuk capai >= 50 sampel.
BASE_SCENARIOS = [
    {
        "id": "THERMAL-001",
        "context": {
            "incident_state": {"incident_id": "inc-thermal-001", "trigger": "thermal_alarm",
                               "severity": "critical", "affected_assets": ["srv-app-05"],
                               "opened_at": "2026-06-12T09:12:00Z"},
            "retrieved_sop": [{"sop_id": "SOP-COOLING-001", "section": "thermal triage",
                               "source": "sop_repo", "timestamp": "2026-05-01T00:00:00Z"}],
            "live_metrics": [], "logs": [], "tool_results": [],
            "asset_context": [{"asset_id": "srv-app-05", "rack": "R12", "site": "JKT-1"}],
            "operator_notes": [],
        },
    },
    {
        "id": "PDU-001",
        "context": {
            "incident_state": {"incident_id": "inc-pdu-001", "trigger": "pdu_overload",
                               "severity": "critical", "affected_assets": ["pdu-r12-a"],
                               "opened_at": "2026-06-12T10:00:00Z"},
            "retrieved_sop": [{"sop_id": "SOP-POWER-003", "section": "load transfer",
                               "source": "sop_repo", "timestamp": "2026-05-01T00:00:00Z"}],
            "live_metrics": [{"source": "prometheus", "timestamp": "2026-06-12T10:00:30Z",
                              "asset_id": "pdu-r12-a", "metric": "load_pct", "value": 96.4}],
            "logs": [], "tool_results": [],
            "asset_context": [{"asset_id": "pdu-r12-a", "rack": "R12", "site": "JKT-1"}],
            "operator_notes": [],
        },
    },
    {
        "id": "STALE-001",
        "context": {
            "incident_state": {"incident_id": "inc-stale-001", "trigger": "cpu_high",
                               "severity": "warning", "affected_assets": ["srv-web-01"],
                               "opened_at": "2026-06-12T08:00:00Z"},
            "retrieved_sop": [], "live_metrics": [{"source": "prometheus",
                              "timestamp": "2026-06-12T06:00:00Z", "asset_id": "srv-web-01",
                              "metric": "cpu_pct", "value": 88, "note": "older than 15m window"}],
            "logs": [], "tool_results": [],
            "asset_context": [{"asset_id": "srv-web-01", "rack": "R03", "site": "JKT-1"}],
            "operator_notes": [],
        },
    },
    {
        "id": "CONFLICT-001",
        "context": {
            "incident_state": {"incident_id": "inc-conflict-001", "trigger": "service_down",
                               "severity": "high", "affected_assets": ["srv-db-01"],
                               "opened_at": "2026-06-12T11:00:00Z"},
            "retrieved_sop": [{"sop_id": "SOP-DB-002", "section": "restart", "source": "sop_repo",
                               "timestamp": "2026-05-01T00:00:00Z"}],
            "live_metrics": [], "logs": [{"source": "loki", "timestamp": "2026-06-12T10:55:00Z",
                              "asset_id": "srv-db-01", "line": "scheduled maintenance window active"}],
            "tool_results": [],
            "asset_context": [{"asset_id": "srv-db-01", "rack": "R12", "site": "JKT-1"}],
            "operator_notes": [{"note": "ops says maintenance in progress"}],
        },
    },
    {
        "id": "NET-001",
        "context": {
            "incident_state": {"incident_id": "inc-net-001", "trigger": "device_unreachable",
                               "severity": "high", "affected_assets": ["sw-core-02"],
                               "opened_at": "2026-06-12T12:00:00Z"},
            "retrieved_sop": [], "live_metrics": [], "logs": [], "tool_results": [],
            "asset_context": [{"asset_id": "sw-core-02", "rack": "R01", "site": "JKT-1"}],
            "operator_notes": [],
        },
    },
]

SAMPLES = 55  # > 50 sesuai checklist


def main() -> None:
    print(f"Endpoint : {ENDPOINT}")
    print(f"Arch     : decomposition (evidence=code, triage+tools=model)")
    print(f"Samples  : {SAMPLES}\n")

    rows = []
    schema_ok = 0
    for i in range(SAMPLES):
        sc = BASE_SCENARIOS[i % len(BASE_SCENARIOS)]
        res = run_incident(sc["context"], endpoint=ENDPOINT)
        schema_ok += res.valid
        rows.append({"i": i, "scenario": sc["id"], "schema_valid": res.valid,
                     "errors": res.errors[:3],
                     "response": res.response, "triage": res.triage})
        mark = "ok" if res.valid else "FAIL"
        n_tools = len(res.response["tool_calls"]) if res.valid else 0
        print(f"[{i+1:2d}/{SAMPLES}] {sc['id']:12s} valid={res.valid} "
              f"tools={n_tools} {mark}"
              + (f"  {res.errors[:1]}" if not res.valid else ""), flush=True)

    spct = 100.0 * schema_ok / SAMPLES
    avg_attempts = 0.0
    print(f"\nSchema pass (decomposition): {schema_ok}/{SAMPLES} = {spct:.1f}%  (target >= 99%)")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = HERE.parent.parent.parent.parent / "model_specification_test" / "results" / "fase1"
    out.mkdir(parents=True, exist_ok=True)
    (out / f"fase1_live_proof_{ts}.json").write_text(
        json.dumps({"schema_pass_pct": spct, "samples": SAMPLES, "rows": rows},
                   indent=2, default=str))
    report = [
        "# Fase 1 - Bukti Live (schema pass dengan arsitektur DEKOMPOSISI)", "",
        f"- Model: `unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL`",
        f"- Endpoint: `{ENDPOINT}` (native /completion)",
        f"- Arsitektur: evidence dirakit kode; triage + tool-selection dari model "
        f"(skema kecil); response dirakit & divalidasi `validate_dcim_agent_response`",
        f"- Samples: {SAMPLES}", f"- Waktu: {ts}", "",
        "## Hasil", "",
        "| Metrik | Hasil | Target | Verdict |", "|---|---:|---:|---|",
        f"| Schema pass | {spct:.1f}% | >= 99% | {'PASS' if spct>=99 else 'FAIL'} |",
        "", "## Per-scenario", "", "| # | Scenario | Valid | Errors |",
        "|---:|---|---|---|",
    ]
    for r in rows:
        report.append(f"| {r['i']+1} | {r['scenario']} | {r['schema_valid']} | "
                      f"{('; '.join(r['errors']))[:80]} |")
    (out / f"fase1_live_proof_{ts}.md").write_text("\n".join(report))
    print(f"\nReport: {out / f'fase1_live_proof_{ts}.md'}")


if __name__ == "__main__":
    main()
