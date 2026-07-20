# TASK BREAKDOWN: LLM Fine-Tuning Proper + Integration

> Seluruh fase di bawah ini dapat dikerjakan tanpa menunggu Syauqi karena dataset dan model artifacts sudah tersedia.

---

# Fase 1 — Dataset Preparation & Quality Check
**Estimasi:** 1–2 jam

| ID | Task | Skrip Terkait | Status |
|----|------|---------------|--------|
| T1.1 | Re-generate dataset dari source terbaru (jika ada data baru di TimescaleDB) | `dataset_generator.py` | ✅ Ada |
| T1.2 | Audit kualitas dataset (imbalance per category & duplicate detection) | Baru | ❌ |
| T1.3 | Implementasi dataset split 70/15/15 (train/validation/test). Saat ini masih train/eval saja. | `finetune_qlora.py` | ❌ |
| T1.4 | Data augmentation (variasi prompt & synthetic samples) | `synthetic_generator.py` | ⚠️ Ada (200/3816 enhanced) |
| T1.5 | Membuat held-out test set yang tidak pernah digunakan saat training | Baru | ❌ |

---

# Fase 2 — Proper Fine-Tuning Pipeline
**Estimasi:** 3–5 jam

| ID | Task | Skrip Terkait | Status |
|----|------|---------------|--------|
| T2.1 | Grid Search Hyperparameter:<br>- Learning Rate: `1e-4`, `2e-4`, `5e-4`<br>- LoRA Rank: `8`, `16`, `32`<br>- Epoch: `2`, `3`, `5` | `finetune_unsloth.py` | ⚠️ Single Config |
| T2.2 | Logging training metrics (loss, eval loss, perplexity) | Baru | ❌ |
| T2.3 | Early stopping jika eval loss tidak membaik selama 3 epoch | Baru | ❌ |
| T2.4 | Checkpoint management (simpan model terbaik, bukan last epoch) | Baru | ❌ |
| T2.5 | Optimasi menggunakan Unsloth (2–3× lebih cepat) | `finetune_unsloth.py` | ⚠️ Masih POC |
| T2.6 | Training menggunakan dataset split 70/15/15 | Modifikasi existing | ❌ |
| T2.7 | Baseline evaluation (pre fine-tuning) sebagai pembanding | `evaluate_model.py` | ⚠️ Basic |

---

# Fase 3 — Evaluation & Model Registry
**Estimasi:** 2–3 jam

| ID | Task | Skrip Terkait | Status |
|----|------|---------------|--------|
| T3.1 | Per-category metrics (Precision, Recall, F1 untuk 9 kategori instruction) | `evaluate_model.py` | ⚠️ Baru keyword score |
| T3.2 | Hallucination test (5 test case sesuai benchmark MT-023 §11) | Baru | ❌ |
| T3.3 | Reasoning test (4 soal logika DCIM sesuai benchmark) | Baru | ❌ |
| T3.4 | RCA test (4 skenario infrastruktur) | `test_dcim_ai.py` | ⚠️ Masih sederhana |
| T3.5 | Perbandingan baseline vs fine-tuned (precision delta & drift tolerance) | Baru | ❌ |
| T3.6 | Registrasi model ke database `model_registry` | `model_registry_standalone.py` | ⚠️ Masih file-based |
| T3.7 | Promotion Gatekeeper (threshold: **F1 ≥ 0.6** dan **keyword ≥ 70%**) | Adaptasi `promotion_gatekeeper.py` | ❌ |
| T3.8 | Export GGUF (`Q4_K_M` & `F16`) dengan version tag yang benar | `export_gguf.py` | ✅ Ada |

---

# Fase 4 — Inference Service & API Integration
**Estimasi:** 2–4 jam

| ID | Task | Skrip Terkait | Status |
|----|------|---------------|--------|
| T4.1 | Deploy model fine-tuned ke `llama-server` (stop Gemma → start DCIM-AI) | Manual | ❌ |
| T4.2 | Mengaktifkan endpoint `/llm/query` agar meneruskan request ke llama-server | `api/routers/llm.py` | ⚠️ Masih template fallback |
| T4.3 | Mengaktifkan endpoint `/llm/explain` untuk anomaly explanation | `api/routers/llm.py` | ⚠️ Masih template fallback |
| T4.4 | Integrasi RCA Prompt Contract (structured output) | `rca_prompt_contract.py` | ⚠️ Sudah dibuat tetapi belum di-wire |
| T4.5 | Production Readiness (Agent Orchestrator + HITL) | `production_readiness/` | ⚠️ Sudah ada tetapi offline |
| T4.6 | Benchmark latency & throughput (mengacu MT-023 §2) | `benchmark_all_v4.py` | ✅ Reusable |

---

# Fase 5 — RAG Pipeline *(Opsional)*
Dikerjakan setelah Fase 1–4 selesai.

| ID | Task | Deskripsi |
|----|------|-----------|
| T5.1 | Vector Store Setup | ChromaDB atau pgvector |
| T5.2 | Embedding Pipeline | Metrics → Vector |
| T5.3 | Context Retrieval | Query metrics + anomaly history |
| T5.4 | Citation Mechanism | Menampilkan sumber jawaban |

> **Catatan**
>
> Sebagian besar pekerjaan pada Fase 5 masih bergantung pada pipeline milik Syauqi (Kafka Metrics & TimescaleDB).

---

# Rekomendasi Urutan Pengerjaan

Karena dataset dan GPU sudah tersedia, urutan yang paling efisien adalah:

1. 🚀 **Fase 2** — Proper Fine-Tuning
   - Jalankan grid search.
   - Gunakan GPU yang sedang idle.
   - Port `8080` dapat dihentikan sementara jika diperlukan.

2. 📊 **Fase 3** — Evaluation & Model Registry
   - Mendapatkan metrik objektif mengenai kualitas model.
   - Menentukan apakah model layak dipromosikan.

3. 🔌 **Fase 4** — Deployment & API Integration
   - Deploy model hasil fine-tuning.
   - Mengaktifkan endpoint LLM sehingga tidak lagi mengembalikan HTTP **501 Not Implemented**.

4. 🧹 **Fase 1** — Dataset Quality
   - Dapat dikerjakan secara paralel selama proses training berlangsung.

---

# Estimasi Total Pekerjaan

**Durasi:** sekitar **2–3 hari kerja penuh**

> Sebelumnya hanya Proof of Concept (±1 hari). Tahapan di atas akan menghasilkan pipeline fine-tuning yang jauh lebih siap digunakan di lingkungan produksi.