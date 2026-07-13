# MT-023 — Fase 0–1: Re-validasi Capability & Arsitektur Dekomposisi

Dokumen ini mencatat hasil **Fase 0 (validasi hasil test)** dan **Fase 1 (quick
wins tanpa training)** dari `PRE_EXECUTION_CHECKLIST.md`, untuk model produksi
DCIM `unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL`.

- Tanggal: 2026-06-15
- Runtime: llama.cpp / llama-server, endpoint `http://localhost:8080/completion`
- Use case: DCIM Operations Agent (monitoring, alert triage, incident response, SOP)
- Artefak kode: `implementation/dcim_ai_v2_rag/llm/production_readiness/`

---

## 1. Ringkasan Eksekutif

| Item | Hasil |
|---|---|
| 3 "gap HIGH" hasil capability test awal (json_mode, memory, context_engine) | **Artefak harness/prompt — BUKAN defisit model** |
| Kebutuhan fine-tuning untuk gap tersebut | **Tidak perlu** |
| Masalah nyata yang ditemukan | Model Q4 **degenerate** saat mengisi skema response besar one-shot |
| Solusi | **Arsitektur dekomposisi** (tanpa training) |
| Schema pass response produksi | **0% → 100%** (55/55 bukti live) |
| Evidence fabrikasi | **0** dari 55 sampel |
| Test | **11/11 hijau** |

---

## 2. Fase 0 — Re-validasi Capability

### 2.1 Latar
Capability test awal (`model_specification_test/results/Hasil Output Capability
Test - Scoring.md`) menandai beberapa capability gagal di level rendah. Hipotesis:
sebagian adalah artefak metodologi (output ditempel ke Markdown → escape karakter;
prompt manual kurang imperatif), bukan kemampuan model.

### 2.2 Metode
Runner `model_specification_test/fase0_revalidation.py` memanggil model **langsung
via API** (raw output, tanpa paste markdown) untuk 4 capability target, dengan
validasi JSON strict setara `jq`.

### 2.3 Hasil

| Capability | Skor awal | Re-test | Kesimpulan |
|---|---|---|---|
| `json_mode` | Level 0 | **PASS 0.84** — strict JSON 5/5 valid | Artefak paste markdown |
| `memory` | Level 1 | **PASS 0.84** — tool store/recall 5/5 | Artefak compressed prompt |
| `context_engine` | Level 0 | default 0/4 → **direktif 4/4** | Gap **prompt**, bukan model |
| `multiturn` | Level 1 | **PASS 0.65** (lewat ambang) | Lolos tipis; tak ada fabrikasi di run raw |

`context_engine` 0/4 berubah jadi 4/4 hanya dengan menambah system prompt
direktif + `tool_choice` — bukti model **mampu**, prompt-nya yang kurang.

### 2.4 Implikasi
3 gap HIGH terbukti artefak → **Fase 2 (dataset besar) & Fase 4 (fine-tuning)
kemungkinan tidak diperlukan** untuk gap tersebut. Prioritas bergeser ke Fase 1
(prompt/schema/state) dan Fase 3 (eval gate).

Bukti: `model_specification_test/results/fase0/`.

---

## 3. Fase 1 — Quick Wins Tanpa Training

### 3.1 Masalah yang ditemukan (akar sebenarnya)
Saat membangun jalur output produksi (response penuh `dcim-agent-response/v1`),
ditemukan kegagalan **bukan pada validitas JSON** melainkan pada **kapasitas
generasi one-shot**:

- Diberi skema besar-bernested (`evidence[]`, `tool_calls[]`, `approval_request`),
  model Q4 **degenerate**: loop digit (`0.85000000…`, `1111…`), ID/timestamp
  ngawur (`ev-3487656565…`, `2026-05349788Z`), teks sampah → output truncated.
- Skema **kecil/datar** (status, summary, risk, action, confidence) → **100% valid**,
  output bagus.

Diagnostik kunci:

| Skema | Token | JSON valid | Catatan |
|---|---|---|---|
| FULL (nested) | 2048 (limit) | ❌ | konten degenerate |
| MINI (flat scalar) | ~174 (eos) | ✅ | ringkasan akurat |

Bagian yang memicu degenerasi adalah tempat model dipaksa **mengarang** evidence —
yang justru **dilarang** oleh prinsip anti-fabrikasi.

### 3.2 Solusi: Arsitektur Dekomposisi
Alih-alih satu panggilan besar, generasi dipecah dan perakitan data dipindah ke kode:

| Bagian response | Sumber | Mekanisme |
|---|---|---|
| `evidence[]` | **Kode** | `assemble_evidence()` dari konteks RAG/tool — source+timestamp nyata, 0 fabrikasi |
| `status, summary, risk, recommended_action, requires_human_approval, confidence` | **Model** | 1 panggilan, `triage.schema.json` (kecil & andal) |
| `tool_calls[]` (pilihan) | **Model** | `tool_selection.schema.json` — hanya enum `action_type` + `asset_id` + `reason` |
| `tool_calls[]` (argumen) | **Kode** | diisi dari `tool_catalog_template.yaml` + asset nyata |
| `approval_request` | **Kode** | diturunkan otomatis saat ada aksi destruktif |
| `missing_evidence` | **Kode** | `compute_missing_evidence()` |

Seluruh response dirakit lalu **wajib** lolos `validate_dcim_agent_response`
sebelum dikembalikan.

### 3.3 Komponen pendukung
- **JSON enforcement** (`constrained_client.py`): `json_schema` constrained
  decoding (llama.cpp meng-compile schema→grammar) + `repeat_penalty=1.3`
  (memutus loop digit khas Q4) + retry dengan temperature menurun.
- **External state store** (`incident_state_store.py`): SQLite, latest-wins.
  Incident state (`incident_id, device, metrics_snapshot, steps_done,
  pending_action`) di luar konteks model → menutup gap memory/multiturn dan
  mencegah fabrikasi nilai stale dari turn lama.
- **Anti-fabrikasi**: ditegakkan **struktural** (evidence dirakit kode) + tekstual
  (SYSTEM_PROMPT melarang mengarang hostname/metric/timestamp).
- **`confidence` clamp**: json_schema mengabaikan `minimum`/`maximum`, jadi skor
  dinormalisasi ke [0,1] di kode.

### 3.4 Keputusan teknis yang diambil
1. **GBNF tulis-tangan ditinggalkan** → llama.cpp gagal meng-compile grammar
   penuh (di-fallback diam-diam). `json_schema` lebih robust. File GBNF disimpan
   sebagai catatan (`grammars/dcim_agent_response.gbnf`, deprecated).
2. **Skema FULL one-shot ditinggalkan** untuk generasi → dipakai hanya sebagai
   acuan validator. Generasi memakai skema kecil + dekomposisi.

### 3.5 Hasil terukur

| Metrik | Target | Hasil |
|---|---|---|
| Schema pass (bukti live 55 sampel) | ≥ 99% | **100%** |
| Evidence fabrikasi | 0 | **0** |
| Unit test (contract + orchestrator) | hijau | **11/11** |

Bukti: `model_specification_test/results/fase1/`.

---

## 4. Inventaris Artefak

### Runtime
| File | Fungsi |
|---|---|
| `agent_orchestrator.py` | Entry point `run_incident(context)` — dekomposisi. |
| `constrained_client.py` | Panggilan model terjamin JSON (json_schema + repeat_penalty + retry). |
| `incident_state_store.py` | State eksternal SQLite (latest-wins). |
| `production_readiness_contract.py` | SYSTEM_PROMPT + validator strict. |

### Schema
| File | Fungsi |
|---|---|
| `schemas/triage.schema.json` | Triage scalar (panggilan model). |
| `schemas/tool_selection.schema.json` | Pemilihan tool (enum). |
| `schemas/incident_report.schema.json` | Response penuh (acuan validator). |
| `schemas/dcim_agent_response.combined.schema.json` | Versi self-contained. |
| `schemas/tool_call.schema.json`, `schemas/approval_request.schema.json` | Sub-schema. |

### Test & bukti
| File | Fungsi |
|---|---|
| `tests/test_production_readiness_contract.py` | 7 test validator. |
| `tests/test_agent_orchestrator.py` | 4 test perakitan deterministik. |
| `fase1_live_proof.py` | Harness bukti live. |
| `model_specification_test/fase0_revalidation.py` | Runner re-validasi Fase 0. |

### Cara menjalankan ulang
```bash
# Fase 0 — re-validasi capability
cd model_specification_test && ../ragavenv/bin/python fase0_revalidation.py

# Fase 1 — bukti live schema pass
cd implementation/dcim_ai_v2_rag/llm/production_readiness
../../../../ragavenv/bin/python fase1_live_proof.py

# Test (autoload plugin pytest dimatikan karena konflik langsmith di env ini)
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 ./ragavenv/bin/python -m pytest \
  implementation/dcim_ai_v2_rag/tests/test_agent_orchestrator.py \
  implementation/dcim_ai_v2_rag/tests/test_production_readiness_contract.py -q
```

---

## 5. Status & Langkah Berikutnya

- ✅ **Fase 0** — selesai (re-validasi; 3 gap HIGH terbukti artefak).
- ✅ **Fase 1** — selesai (dekomposisi; schema pass 100%, anti-fabrikasi struktural).
- ⏭️ **Fase 3** — golden eval set sebagai gate go/no-go (fondasi orchestrator +
  validator sudah siap).
- Sisa kecil (non-blocker): tool `processes` + 1 tool agregasi multi-domain
  (gap tool_calling L5).

Catatan: Fase 2 (dataset besar) dan Fase 4 (fine-tuning) **belum diperlukan**
berdasarkan temuan Fase 0–1; ditinjau ulang hanya jika golden eval (Fase 3)
menemukan gap perilaku yang tidak bisa ditutup prompt/arsitektur.
