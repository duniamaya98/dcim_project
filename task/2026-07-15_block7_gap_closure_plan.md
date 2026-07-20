# Block 7 Analytics & AI — Gap Closure Plan

**Tanggal:** 15 Juli 2026
**Sumber analisis:** Cross-check `dcim-wiki` (pull 5512eab) vs implementasi `dcim_ai_v2_rag`
**Service status:** ✅ Running di port 8000 via `/home/infra/dcim_project/ragavenv`

---

## Ringkasan Alignment (Koreksi)

Alignment doc (`impl-repo-analytics-ai-alignment.md`, 13 Juli) klaim **~38%**.  
Setelah verifikasi langsung (API call + code review), angka sebenarnya:

| Area | Alignment Doc | Hasil Verifikasi Langsung | Koreksi |
|---|---|---|---|
| API Endpoints functional | 7/28 (25%) | **12/28 (43%)** | ⬆ +5 endpoint |
| LLM/RAG | 0/7 FR | **2/7 FR** (query + explain jalan, template fallback) | ⬆ |
| Capacity Forecasting | 3/7 FR | **4/7 FR** (forecast POST fully functional) | ⬆ |
| Energy Optimization | 4/7 FR | **4/7 FR** (tetap, tapi bukan stub) | ✅ |
| Anomaly Detection | 4/8 FR | **4/8 FR** (tetap — detect masih 501) | — |
| Predictive Maintenance | 0/7 FR | **0/7 FR** (belum ada) | ❌ |

---

## Gap Berdasarkan Prioritas

### P1 — Critical (Blocker)

| # | Gap | Lokasi | Estimasi |
|---|---|---|---|
| P1-01 | `POST /predictions/forecast` → 501 | `api/routers/predictions.py:46` | 2-3 jam |
| P1-02 | `POST /anomalies/detect` → 501 | `api/routers/anomalies.py:62` | 1-2 jam |
| P1-03 | `GET /anomalies/{id}` → 501 | `api/routers/anomalies.py:53` | 1 jam |
| P1-04 | Predictive maintenance: tidak ada LSTM/Prophet/RUL | `services/` — empty | 5-7 hari |

### P2 — High (Operational gap)

| # | Gap | Lokasi | Estimasi |
|---|---|---|---|
| P2-01 | LLM `/query` hanya template fallback — belum pakai model LLM sebenarnya | `api/routers/llm.py` | 1-2 jam |
| P2-02 | Belum ada RAG vector store production (Qdrant) | `rag/pipeline.py` | 3-5 jam |
| P2-03 | `GET /anomalies` return empty list | `api/routers/anomalies.py:44` | 1 jam |
| P2-04 | `GET /predictions` return empty list | `api/routers/predictions.py:37` | 1 jam |
| P2-05 | Belum ada Grafana dashboards & Prometheus alert rules | `monitoring/` | 3-4 jam |
| P2-06 | Anomaly seasonal decomposition (STL) belum ada | `stream/anomaly_detector.py` | 2-3 jam |
| P2-07 | Carbon intensity & energy cost di energy belum | `api/routers/energy.py` | 2 jam |
| P2-08 | Out-of-order event handling belum ada | `stream/metrics_consumer.py` | 2 jam |

### P3 — Enhancement

| # | Gap | Estimasi |
|---|---|---|
| P3-01 | Multi-backend LLM (GPT-4/Claude adapter) | 3-4 jam |
| P3-02 | Rack space forecasting | 2 jam |
| P3-03 | A/B testing framework | 3-4 jam |
| P3-04 | Query history di LLM | 1 jam |
| P3-05 | Survival analysis (Kaplan-Meier/Cox) | 4 jam |

---

## Tahapan Pekerjaan

### Fase 1 — API Wiring (H-1, ~5 jam)

**Goal:** 12/28 → 17/28 endpoint functional. Semua yang udah ada service-nya harus terhubung.

| Step | Action | Detail | Estimasi |
|---|---|---|---|
| 1.1 | Wire anomaly detection API | Hubungkan `POST /detect` + `GET /{id}` ke `anomaly_detector.py` + `anomaly_service.py` | 1.5 jam |
| 1.2 | Wire prediction forecast API | Hubungkan `POST /forecast` ke existing IF/LOF/OCSVM model ensemble | 2 jam |
| 1.3 | Enable real LLM inference | Ganti template fallback di `POST /query` + `POST /explain` dengan panggilan ke llama.cpp server | 1.5 jam |

### Fase 2 — RAG + Monitoring (H-2, ~6 jam)

**Goal:** Observability + LLM context retrieval jalan.

| Step | Action | Detail | Estimasi |
|---|---|---|---|
| 2.1 | Setup Qdrant vector store | Ganti in-memory `VectorStore` dengan Qdrant. Index CMDB + logs + runbooks | 3 jam |
| 2.2 | Wire anomaly list + prediction list | `GET /anomalies` + `GET /predictions` query TimescaleDB | 1 jam |
| 2.3 | Prometheus alert rules (5 rules) | Buat `PrometheusRules` CRD: anomaly rate, forecast drift, PUE spike, RCA latency, model drift | 2 jam |

### Fase 3 — Energy + Pipeline Hardening (H-3, ~5 jam)

**Goal:** P2 gap closure.

| Step | Action | Detail | Estimasi |
|---|---|---|---|
| 3.1 | Carbon intensity + energy cost | Tambah CO2 calculation ke `energy_optimization.py`. Integrasi dengan API | 2 jam |
| 3.2 | Out-of-order event handling | Buffer late events di `metrics_consumer.py`, reorder + deduplicate | 2 jam |
| 3.3 | Seasonal decomposition (STL) | Tambah STL decomposition ke anomaly detector | 1 jam |

### Fase 4 — Predictive Maintenance ML (H-4..H-8, ~5 hari)

**Goal:** 0/7 FR → 5/7 FR. Paling berat — butuh training.

| Step | Action | Detail | Estimasi |
|---|---|---|---|
| 4.1 | Prophet integration | Install `prophet`, train di `server_metrics`, wire ke API | 2 jam |
| 4.2 | LSTM failure prediction | PyTorch LSTM model, train di TimescaleDB historical data | 8 jam |
| 4.3 | Remaining Useful Life (RUL) | RUL calculation dari LSTM output | 4 jam |
| 4.4 | Confidence intervals | Add CI ke prediction responses | 2 jam |
| 4.5 | Maintenance scheduling | Optimize schedule dari RUL + asset criticality | 4 jam |

---

## Dependencies & Prerequisites

| Dependency | Status | Notes |
|---|---|---|
| Venv `ragavenv` aktif | ✅ | Sudah di `/home/infra/dcim_project/ragavenv` |
| Service port 8000 running | ✅ | Uvicorn dari venv yang benar |
| TimescaleDB (10.70.0.56:5433) | ✅ | Migration schema tersedia |
| Kafka (10.70.0.56:9092) | ✅ | Untuk anomaly stream |
| GPU (NVIDIA) | ⚠️ | Butuh untuk LSTM training + LLM inference |
| llama.cpp server | ❌ | Perlu di-setup untuk LLM sebenarnya (bukan template) |
| Qdrant | ❌ | Perlu install untuk RAG vector store |

---

## Target Alignment Setelah Semua Fase

| Area | Sebelum | Sesudah |
|---|---|---|
| API Endpoints functional | 12/28 (43%) | 22/28 (79%) |
| Anomaly Detection FR | 4/8 (50%) | 6/8 (75%) |
| Predictive Maintenance FR | 0/7 (0%) | 5/7 (71%) |
| Capacity Forecasting FR | 4/7 (57%) | 4/7 (57%) |
| Energy Optimization FR | 4/7 (57%) | 6/7 (86%) |
| LLM/RAG FR | 2/7 (29%) | 5/7 (71%) |
| Monitoring | ~20% | ~60% |
| **Overall** | **~45%** | **~75%** |

---

## Catatan

- Pekerjaan **TIDAK mengubah** komponen yang sudah solid: RCA Engine (4/7 FR, fully functional), Correlation Engine, Data Contracts v1.2.0, TimescaleDB schema, Model Registry, Training Orchestrator, LLM fine-tuning pipeline.
- `agent_orchestrator.py` + `production_readiness/` sudah align dengan Hermes Agentic AI Control Plane — dekomposisi arsitektur, evidence anti-fabrikasi, bounded tool selection.
- Deployment Plan v2 (hybrid Gemma 4 12B) masih proposed — belum perlu code-level action sekarang, cukup pastikan pipeline compatible.
