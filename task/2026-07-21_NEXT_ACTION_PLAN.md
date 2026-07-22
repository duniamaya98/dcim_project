# Block 7 — Master Action Plan (Update: 21 Juli 2026)

> **Konteks:** Dokumen ini menggabungkan sisa pekerjaan *API Gap Closure* dengan rencana *LLM Fine-Tuning Proper* untuk Block 7 Analytics & AI Engine. Pekerjaan Fase 1 (API Wiring), Fase 3 (Energy), dan setup Grafana/Prometheus (Monitoring) sudah **SELESAI**.

---

## 🎯 TRACK A: LLM Fine-Tuning & Evaluation (Prioritas Utama)
> *Goal: Melatih model AI Qwen/Gemma menjadi spesialis DCIM dengan akurasi F1 > 0.6.*

### Fase 1 — Dataset Preparation & Quality Check (Estimasi: 1-2 Jam)
| ID | Task | Skrip Terkait | Status |
|----|------|---------------|--------|
| T1.1 | Re-generate dataset dari source terbaru | `dataset_generator.py` | ✅ Ada |
| T1.2 | Audit kualitas dataset (imbalance & duplicate) | `dataset_audit.py` | ✅ Done |
| T1.3 | Implementasi dataset split 70/15/15 | `clean_and_split.py` | ✅ Done |
| T1.4 | Data augmentation (variasi prompt & synthetic) | `synthetic_generator.py` | ⚠️ Partial |
| T1.5 | Membuat held-out test set | `clean_and_split.py` | ✅ Done |

### Fase 2 — Proper Fine-Tuning Pipeline (Estimasi: 3-5 Jam)
| ID | Task | Skrip Terkait | Status |
|----|------|---------------|--------|
| T2.1 | Grid Search Hyperparameter (LR, Rank, Epoch) | `finetune_proper.py` | ✅ Done |
| T2.2 | Logging training metrics | `finetune_proper.py` | ✅ Done |
| T2.3 | Early stopping (3 epoch no improve) | `finetune_proper.py` | ✅ Done |
| T2.4 | Checkpoint management (best model) | `finetune_proper.py` | ✅ Done |
| T2.5 | Optimasi menggunakan QLoRA/Unsloth | `finetune_unsloth.py` | ⚠️ Masih POC |

### Fase 3 — Evaluation & Model Registry (Estimasi: 2-3 Jam)
| ID | Task | Skrip Terkait | Status |
|----|------|---------------|--------|
| T3.1 | Per-category metrics (Precision, Recall, F1) | `evaluate_and_promote.py` | ✅ Done |
| T3.2 | Hallucination & Reasoning test | `evaluate_and_promote.py` | ✅ Done |
| T3.3 | RCA test (4 skenario infrastruktur) | `test_dcim_ai.py` | ⚠️ Partial |
| T3.4 | Promotion Gatekeeper (Threshold F1 ≥ 0.6) | `evaluate_and_promote.py`| ✅ Done |
| T3.5 | Export GGUF dengan version tag | `export_gguf.py` | ✅ Done |

---

## 🏗️ TRACK B: API Infrastructure & Predictive ML
> *Goal: Menyelesaikan sisa arsitektur backend Block 7.*

### Fase 4 — RAG (Retrieval-Augmented Generation) Pipeline (Estimasi: 3-5 Jam)
| ID | Task | Skrip Terkait | Status |
|----|------|---------------|--------|
| T4.1 | Vector Store Setup (Qdrant) | `rag/pipeline.py` | ✅ Done |
| T4.2 | Embedding Pipeline (CMDB, Logs, Runbooks) | `rag/index_knowledge.py` | ✅ Done |
| T4.3 | Context Retrieval saat API `/query` & `/explain` dipanggil | `api/routers/llm.py` | ✅ Done |

### Fase 5 — Predictive Maintenance ML (Estimasi: 3-5 Hari)
| ID | Task | Detail | Status |
|----|------|--------|--------|
| T5.1 | Prophet integration | Integrasi library Prophet untuk forecasting | ❌ |
| T5.2 | LSTM failure prediction | PyTorch LSTM model dari TimescaleDB historical data | ❌ |
| T5.3 | Remaining Useful Life (RUL) | RUL calculation dari LSTM output | ❌ |

---

## 💡 Rekomendasi Eksekusi Selanjutnya
Karena *infrastructure* API kita sekarang sudah terhubung (*wired*) dengan baik, langkah yang paling memberikan *impact* saat ini adalah **Mulai TRACK A: LLM Fine-Tuning (Fase 1 & Fase 2)**. 

GPU (RTX 3070 Ti) kita bisa langsung dipakai untuk proses ini. Sementara model ditraining (butuh waktu beberapa jam), kita bisa pindah mengerjakan kode untuk **RAG Qdrant (Fase 4)**.