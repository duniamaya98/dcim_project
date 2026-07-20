# Pre-Execution Checklist — DCIM LLM (Gemma 4 12B Q4_K_XL)

Model: `unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL`
Use case: DCIM Operations Agent (monitoring, alerting, incident response, SOP execution)
Sumber gap: `model_specification_test/results/Hasil Output Capability Test - Scoring.md`

Checklist ini berurutan sebagai **gate**. Jangan lanjut ke fase berikutnya sebelum fase sebelumnya tuntas.

---

## Fase 0 — Validasi Hasil Test (WAJIB dulu, murah) — ✅ SELESAI 2026-06-12
Tujuan: pastikan gap nyata, bukan artefak harness. Bisa membatalkan kebutuhan training.

Runner: `model_specification_test/fase0_revalidation.py` (raw API, model live `:8080`).
Report: `model_specification_test/results/fase0/`.

- [x] Re-test `json_mode` dengan **raw output** model → **PASS 0.84, strict JSON 5/5 valid** (`jq`-equivalent). Gap L0 sebelumnya = artefak paste markdown, BUKAN model.
- [x] Re-test `context_engine` → harness default **0/4**, tapi dengan **system prompt direktif → 4/4**. Gap = **prompt**, bukan model (model bisa tool-call, lihat memory).
- [x] Re-test `memory` (tool memory_store/recall) → **PASS 0.84, 5/5**. Gap L1 sebelumnya = artefak compressed prompt, BUKAN model.
- [x] Re-test `multiturn` → **PASS 0.65, 4/4 lewat ambang**. Tidak terobservasi fabrikasi `srv-db-01` di run raw; skor tipis di atas ambang (perhatikan).
- [ ] Verifikasi runtime nyata (bukan content-only): `streaming`, `web_search`, `file_ops`, `session_search` — *butuh tool/runtime aktual, ditunda ke Fase 5*.
- [x] **Keputusan:** 3 gap HIGH (json_mode, memory, context_engine) **TERBUKTI artefak harness/prompt — bukan defisit model**. Tidak perlu fine-tune untuk ketiganya. Yang nyata & perlu dijaga: (a) `multiturn` margin tipis → state store + anti-fabrikasi (Fase 1); (b) tool-calling perlu system prompt direktif + `tool_choice`.

**Implikasi ke scope:** Fase 2 & Fase 4 (dataset besar + fine-tuning) kemungkinan besar TIDAK diperlukan untuk gap HIGH. Prioritas geser ke Fase 1 (prompt/grammar/state) + Fase 3 (eval gate).

## Fase 1 — Quick Wins Tanpa Training — ✅ SELESAI 2026-06-15
Artefak di `implementation/dcim_ai_v2_rag/llm/production_readiness/`.

- [x] **Arsitektur DEKOMPOSISI** (`agent_orchestrator.py`) — menggantikan one-shot skema FULL yang bikin model degenerate:
  - `evidence[]` → dirakit kode dari konteks RAG/tool (source+timestamp nyata) → **anti-fabrikasi struktural** (0 evidence fabrikasi pada 55 sampel).
  - triage scalar → 1 panggilan model (`triage.schema.json`, kecil & andal).
  - `tool_calls[]` → enum dari model (`tool_selection.schema.json`); argumen diisi kode dari tool catalog + asset nyata.
  - `approval_request` → diturunkan kode saat ada aksi destruktif.
- [x] JSON enforcement: `json_schema` constrained decoding + `repeat_penalty=1.3` (memutus loop digit khas Q4) + retry (`constrained_client.py`). **GBNF tulis-tangan ditinggalkan** (gagal di-compile server).
- [x] **External State Store** (SQLite): `incident_state_store.py` — `incident_id, device, metrics_snapshot, steps_done, pending_action`, latest-wins.
- [x] **System prompt** + anti-fabrikasi: `system_prompt.md` + `SYSTEM_PROMPT`.
- [x] **Bukti live: schema pass 55/55 = 100%** (target ≥99%) via orchestrator. Bukti: `model_specification_test/results/fase1/fase1_live_proof_*`.
- [x] Validator strict + test: **11/11 pytest hijau** (`test_production_readiness_contract.py` 7 + `test_agent_orchestrator.py` 4).
- [x] Few-shot + tool catalog: `datasets/*.jsonl`, `tool_catalog_template.yaml`.
- [ ] *(minor, susul)* tool `processes` + 1 tool agregasi multi-domain (gap tool_calling L5) — loki_query/prometheus/asset/sop/ticketing/pager/runbook sudah ada.

**Temuan kunci Fase 1:** masalah bukan "JSON tidak valid" (model OK untuk skema kecil), tapi **skema response produksi terlalu besar untuk one-shot model Q4** → degenerate saat dipaksa mengarang evidence. **Dekomposisi menyelesaikannya tanpa fine-tuning** (0% → 100% valid) sekaligus menegakkan anti-fabrikasi.

## Fase 2 — Dataset Prep (hanya untuk gap yang masih persist)

- [ ] Kumpulkan & **anonymize** sumber: `Baseline Query Database.md`, NetBox (`ingest_netbox.py`), log historis
- [ ] Bangun **tool-call traces** (500–1k): prompt → JSON call valid → result → answer (termasuk logs/processes)
- [ ] Bangun **grounded QA** + contoh negatif (model dihukum saat mengarang angka)
- [ ] Bangun **multi-turn incident dialogs** (5–10 turn, state persisten)
- [ ] Bangun **SOP execution** + checkpoint HITL
- [ ] Bangun **structured output** sesuai schema ticketing/alerting riil
- [ ] Split train/val/test, cek tidak ada leakage

## Fase 3 — Golden Eval Set (gate go/no-go)
Bangun **sebelum** fine-tune supaya ada baseline.

- [ ] Susun **100–200 skenario DCIM** dengan expected output
- [ ] Implement metrik otomatis + threshold:
  - [ ] Hallucination rate < 1%
  - [ ] JSON valid rate = 100%
  - [ ] Tool-call accuracy ≥ 95%
  - [ ] Multi-turn fact retention ≥ 95%
  - [ ] SOP step adherence ≥ 90%
  - [ ] Numeric grounding ≥ 99%
- [ ] Jalankan eval pada **base + prompt/grammar** (baseline sebelum training)

## Fase 4 — Fine-Tuning (jika Fase 1 belum cukup)

- [ ] Konfirmasi base **fp16/bf16** Gemma 4 12B-it tersedia (BUKAN train di atas GGUF Q4)
- [ ] Setup **QLoRA via Unsloth** (env `.unsloth/` sudah ada)
- [ ] Train hanya gap perilaku tersisa (jangan latih capability yang sudah Level 5)
- [ ] Merge adapter → convert ke GGUF (`convert_hf_to_gguf.py`) → quantize **Q4_K_XL (UD)**
- [ ] **Re-run golden eval pada GGUF Q4 final** (bukan hanya base fp16) — cek quant drift
- [ ] Gate: semua metrik Fase 3 lolos threshold → boleh lanjut

## Fase 5 — Integrasi & Safety

- [ ] Integrasi RAG 3-lapis: SOP→vector, NetBox→exact lookup, metrics/logs→live API (jangan di-embed)
- [ ] Setup reranker + top-k kecil (3–5), jaga konteks aktif < 8–12k token
- [ ] Hubungkan tools: monitoring (read auto), ticketing/alerting/remediation (write→HITL)
- [ ] Implement **klasifikasi aksi L0–L3** + gating HITL (L2+ = approval di fase awal)
- [ ] Implement **audit log** semua tool call & keputusan
- [ ] Test **rollback** & failover path

## Fase 6 — Pra-Go-Live

- [ ] **Shadow/canary mode**: model jalan paralel tanpa eksekusi, bandingkan vs operator
- [ ] Drift monitor live (hallucination rate, JSON valid rate) + **auto-rollback threshold**
- [ ] Runbook operator + prosedur eskalasi
- [ ] Sign-off: semua aksi L2+ terkunci HITL → baru promote
- [ ] Definisikan kriteria pelonggaran HITL (hallucination rate < 1% terbukti di lapangan)

---

**Critical path minimum sebelum eksekusi apa pun:** Fase 0 → Fase 1 → Fase 3 (baseline).
Jika gap HIGH sudah tertutup di sini, Fase 4 (training) mungkin tidak perlu.

---

## Ringkasan Gap & Risiko (referensi)

| Gap | Risiko | Fase penanganan |
|---|---|---|
| Fabrikasi data metrik (`multiturn` L2) | HIGH | 0, 1, 2 |
| Memory tidak menyimpan fakta (`memory` L1) | HIGH | 0, 1 |
| JSON strict invalid (`json_mode` L0) | HIGH | 0, 1 |
| `context_engine` gagal/salah capability | MEDIUM | 0 |
| `tool_calling` belum lengkap di L5 | MEDIUM | 1, 2 |
| Capability simulated/content-only | MEDIUM | 0 |
| Quantization drift (Q4_K_XL) | LOW–MEDIUM | 3, 4 |
