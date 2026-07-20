# DCIM Production Readiness Artifacts

Artifact ini mengubah hasil capability-test Gemma GGUF
(`unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL`) menjadi kontrak + runtime praktis
untuk supervised **DCIM Operations Agent** (monitoring, alert triage, incident
response, SOP execution).

Status: **Fase 0 (re-validasi) ✅ dan Fase 1 (quick wins tanpa training) ✅.**
Lihat `../../../../PRE_EXECUTION_CHECKLIST.md` untuk roadmap penuh dan
`../../../../documentation/MT-023_Fase0-1_Revalidation_and_Decomposition.md`
untuk catatan teknis lengkap.

## Arsitektur: Dekomposisi

Temuan Fase 1: model 12B Q4 **degenerate** (loop digit, ID/timestamp ngawur)
saat dipaksa mengisi skema response besar-bernested **satu-shot**, terutama saat
harus *mengarang* `evidence[]`/`tool_calls[]`. Solusinya bukan fine-tuning, tapi
**memecah generasi** + memindahkan perakitan data ke kode:

```
                         ┌─────────────── context (RAG/tool/CMDB) ───────────────┐
                         │ incident_state, retrieved_sop, live_metrics, logs,    │
                         │ asset_context, operator_notes                         │
                         └───────────────────────┬───────────────────────────────┘
                                                 │
        ┌────────────────────────────────────────┼────────────────────────────────┐
        ▼ (KODE)                                  ▼ (MODEL, skema kecil)            ▼ (MODEL, enum kecil)
  assemble_evidence()                       triage.schema.json              tool_selection.schema.json
  evidence[] dari konteks                   {status, summary, risk,         {selections:[{action_type,
  (source+timestamp NYATA,                   recommended_action,             asset_id, reason}]}
  0 fabrikasi)                               requires_human_approval,                │
        │                                    confidence}                            ▼ (KODE)
        │                                          │                          isi argumen tool dari
        └──────────────────┬───────────────────────┴──────────────┬───────────  tool catalog + asset nyata
                           ▼                                        ▼
                  rakit dcim-agent-response/v1  ───►  validate_dcim_agent_response()  ───► VALID / FLAG
```

Hasil terukur (bukti live 55 sampel): **schema pass 0% → 100%**, **0 evidence fabrikasi**.

## Isi

### Runtime (Fase 1)
| File | Fungsi |
|---|---|
| `agent_orchestrator.py` | **Entry point.** `run_incident(context)` → response valid via dekomposisi. |
| `constrained_client.py` | Panggilan model: `json_schema` constrained decoding + `repeat_penalty=1.3` (memutus loop digit Q4) + retry. |
| `incident_state_store.py` | External incident state (SQLite, latest-wins) → anti-fabrikasi stale, ganti memori percakapan model. |
| `../production_readiness_contract.py` | `SYSTEM_PROMPT` + `validate_dcim_agent_response` (validator strict contract v1). |

### Kontrak & schema
| File | Fungsi |
|---|---|
| `system_prompt.md` | Production system prompt (anti-fabrikasi) — Unsloth / llama.cpp / Ollama. |
| `schemas/triage.schema.json` | Skema kecil untuk panggilan triage model (andal). |
| `schemas/tool_selection.schema.json` | Skema kecil pemilihan tool (enum); argumen diisi kode. |
| `schemas/incident_report.schema.json` | Skema response penuh `dcim-agent-response/v1` (acuan validator). |
| `schemas/dcim_agent_response.combined.schema.json` | Versi self-contained (inline `$ref`) — referensi / jalur one-shot lama. |
| `schemas/tool_call.schema.json`, `schemas/approval_request.schema.json` | Sub-schema. |
| `tool_catalog_template.yaml` | Allowlist tool production (prometheus/loki/asset/sop/ticketing/pager/runbook). |
| `hitl_policy.md` | Policy approval untuk aksi berisiko. |
| `rag_context_spec.md` | Spesifikasi context assembly (SOP, metrics, logs, asset, ticket). |
| `grammars/dcim_agent_response.gbnf` | *(deprecated)* GBNF tulis-tangan — gagal di-compile llama.cpp, digantikan `json_schema`. Disimpan sebagai catatan. |

### Eval & data
| File | Fungsi |
|---|---|
| `eval/production_readiness_eval.md` | Rubric + scenario regression untuk gap capability. |
| `datasets/*.jsonl` | Seed data (few-shot) untuk eval & fine-tuning opsional. |

### Test & bukti
| Lokasi | Fungsi |
|---|---|
| `../../tests/test_production_readiness_contract.py` | 7 test validator contract. |
| `../../tests/test_agent_orchestrator.py` | 4 test perakitan deterministik (evidence, missing, contract). |
| `fase1_live_proof.py` | Harness bukti live end-to-end (orchestrator × scenario). |
| `../../../../model_specification_test/results/fase1/` | Report + raw hasil bukti live. |
| `../../../../model_specification_test/results/fase0/` | Report re-validasi capability Fase 0. |

## Runtime Minimum (kontrak yang TIDAK boleh dilanggar)

- Output agent wajib lolos `validate_dcim_agent_response` sebelum eksekusi tool.
- `evidence[]` dirakit kode dari data nyata — **model tidak pernah mengarang evidence**.
- Setiap evidence menyertakan `source` dan `timestamp` dari data asli.
- Semua action destructive berhenti di `approval_request` (HITL).
- Incident state disimpan eksternal (`incident_state_store`), bukan memori model.
- `confidence` di-clamp ke [0,1] di kode (json_schema mengabaikan min/max).

## Quick Use

```python
from agent_orchestrator import run_incident

# context sudah dirakit oleh RAG/context engine
result = run_incident(context)   # context: dict (incident_state, retrieved_sop, ...)

if result.valid:
    response = result.response   # dcim-agent-response/v1, sudah tervalidasi
    # response["tool_calls"] -> eksekusi (read-only auto; destructive tunggu approval)
else:
    # tandai/flag untuk operator; JANGAN eksekusi
    log.error("invalid agent response: %s", result.errors)
```

Endpoint default: `http://localhost:8080/completion` (llama.cpp / llama-server).

## Owner

| Area | Engineering | User/Ops |
|---|---|---|
| Prompt, schema, eval, orchestrator | Membuat & menjaga artifact | Review bahasa & policy |
| RAG design | Struktur konteks & evidence assembly | Menyediakan SOP, CMDB, logs, metrics |
| Tool integration | Contract & guardrail | Endpoint, credential, permission |
| HITL | Checkpoint & payload | Approver & SLA approval |
| Production go/no-go | Checklist teknis | Keputusan operasional |
