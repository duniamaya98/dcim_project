# MT-023 — LLM Fine-Tuning Phase 2: Progress Report

> **Tanggal:** 20 Juli 2026
> **Status:** 🟢 IN PROGRESS — Training berjalan
> **Assignee:** Fakhri Aulia R (DCIM Block 7 Lead)
> **dcim-wiki Reference:** block7-analytics-ai-engine.md §8 (Model Training Pipeline), MT-021

---

## 1. Executive Summary

Fine-tuning ulang LLM DCIM dari POC → production-grade. POC sebelumnya hanya menghasilkan train_loss tanpa evaluation, split validation, atau grid search. Phase 2 membangun pipeline training proper dengan 70/15/15 split, early stopping, best checkpoint, dan comprehensive logging.

**Hasil saat ini:** Training 3 epoch sedang berjalan (step 130/501, loss 0.27, token accuracy 90.5%).

**Blockers resolved:**
- bitsandbytes 0.49.2 incompatible dengan torch 2.9.1 di Ampere GPU (RTX 3070 Ti)
- Workaround: fp16 direct load (tanpa 4-bit quantization), tetap muat di 8GB VRAM
- Unsloth gagal install karena dependency conflict → fallback ke HuggingFace PEFT
- llama-server/ollama systemd service auto-restart mengganggu GPU → dihentikan

---

## 2. Fase Progress

### Fase 1 — Dataset Preparation

| # | Task | Status | Keterangan |
|---|------|--------|------------|
| T1.1 | Re-generate dataset | ⏳ Pending | Menunggu data baru dari TimescaleDB (Syauqi) |
| T1.2 | Audit kualitas dataset | ⏳ Pending | Belum dilakukan — 3,816 sampel, 9 kategori |
| T1.3 | 70/15/15 split | ✅ Done | Train=2670, Val=573, Test=573, stratified per kategori |
| T1.4 | Data augmentation | ⏳ Pending | synthetic_generator.py ada, belum dijalankan |
| T1.5 | Held-out test set | ✅ Done | `dcim_test_set.jsonl` — 573 sampel, tidak tersentuh training |

**File:**
- `implementation/dcim_ai_v2_rag/llm/datasets/dcim_test_set.jsonl`
- `implementation/dcim_ai_v2_rag/llm/finetune_proper.py`

### Fase 2 — Training Pipeline

| # | Task | Status | Keterangan |
|---|------|--------|------------|
| T2.1 | Grid search | ❌ Gagal | bitsandbytes + torch 2.9.1 incompatible di Ampere |
| T2.2 | Per-epoch logging | ✅ Done | train_loss, eval_loss, perplexity, token_accuracy terekam |
| T2.3 | Early stopping | ✅ Done | patience=3, monitor eval_loss |
| T2.4 | Best checkpoint | ✅ Done | `load_best_model_at_end=True` |
| T2.5 | Unsloth optimization | ❌ Gagal | Dependency conflict di ragavenv |
| T2.6 | Full training 3 epoch | 🟢 Running | Step 130/501, loss 0.27, acc 90.5%, ETA ~35 menit |
| T2.7 | Baseline evaluation | ⏳ Pending | Setelah training selesai |

**Training metrics saat ini (step 130/501):**

| Metric | Value |
|--------|-------|
| Train Loss | 0.2706 |
| Token Accuracy | 90.45% |
| Epoch | 0.78 |
| Gradient Norm | 0.43 |
| Speed | 5.8s/step |
| Runtime | ~12 menit |
| ETA | ~35 menit |

**Config final:**

| Parameter | Value |
|-----------|-------|
| Base Model | Qwen/Qwen2.5-3B-Instruct |
| Method | LoRA (fp16, no quantization) |
| LoRA r | 16 |
| LoRA alpha | 32 |
| LoRA dropout | 0.05 |
| Learning rate | 2e-4 |
| Batch size | 1 × 16 grad accum = 16 effective |
| Epochs | 3 |
| Max seq len | 512 |
| Optimizer | adamw_torch |
| Precision | fp16 |
| Trainable params | ~15M / 3.1B (0.48%) |
| GPU | RTX 3070 Ti (8GB), GPU 1 |

### Fase 3 — Evaluation & Registry

| # | Task | Status | Keterangan |
|---|------|--------|------------|
| T3.1 | Per-category metrics | ⏳ Pending | Precision/recall/F1 per 9 kategori |
| T3.2 | Hallucination test | ⏳ Pending | 5 test case dari benchmark MT-023 §11 |
| T3.3 | Reasoning test | ⏳ Pending | 4 logic soal DCIM |
| T3.4 | RCA test | ⏳ Pending | 4 skenario infrastruktur |
| T3.5 | Baseline vs fine-tuned comparison | ⏳ Pending | Keyword overlap, latency |
| T3.6 | Model registry (DB) | ⏳ Pending | model_registry_standalone.py |
| T3.7 | Promotion gatekeeper | ⏳ Pending | Threshold: F1 ≥ 0.6, keyword ≥ 70% |
| T3.8 | Export GGUF | ⏳ Pending | Q4_K_M + F16 |

### Fase 4 — Inference Service & API

| # | Task | Status | Keterangan |
|---|------|--------|------------|
| T4.1 | Deploy fine-tuned model | ⏳ Pending | llama-server dengan model baru |
| T4.2 | Un-stub /llm/query | ⏳ Pending | api/routers/llm.py |
| T4.3 | Un-stub /llm/explain | ⏳ Pending | api/routers/llm.py |
| T4.4 | RCA prompt contract | ⏳ Pending | rca_prompt_contract.py |
| T4.5 | Production readiness | ⏳ Pending | HITL + agent orchestrator |
| T4.6 | Benchmark latency | ⏳ Pending | benchmark_all_v4.py |

### Fase 5 — RAG Pipeline (Opsional)

| # | Task | Status | Keterangan |
|---|------|--------|------------|
| T5.1 | Vector store | ⏳ Pending | Tergantung Syauqi (Kafka + TimescaleDB) |
| T5.2 | Embedding pipeline | ⏳ Pending | Tergantung pipeline data |
| T5.3 | Context retrieval | ⏳ Pending | Tergantung pipeline data |
| T5.4 | Citation mechanism | ⏳ Pending | Tergantung RAG pipeline |

---

## 3. Technical Issues & Resolutions

### Issue 1: bitsandbytes 0.49.2 + torch 2.9.1 = CUDA error

**Symptom:** `CUBLAS_STATUS_NOT_SUPPORTED` dan `illegal memory access` di RTX 3070 Ti (Ampere)
**Root cause:** Kombinasi bf16 + 4-bit quantization gagal di Ampere GPU
**Resolution:** Skip bitsandbytes entirely — load model di fp16 langsung (3B = ~6GB, muat di 8GB)
**Impact:** VRAM usage lebih tinggi tapi training stabil

### Issue 2: Unsloth dependency conflict

**Symptom:** `PackageNotFoundError: unsloth_zoo`, `Cannot uninstall transformers None`
**Root cause:** transformers package corrupted di ragavenv
**Resolution:** Fallback ke HuggingFace PEFT + TRL (sudah proven di POC)

### Issue 3: Systemd services conflict

**Symptom:** llama-server + ollama auto-restart, nyedot VRAM
**Resolution:** `systemctl stop llama-server ollama` + `sudo rmmod nvidia*` untuk GPU reset

### Issue 4: GPU state corruption after forced kill

**Symptom:** `illegal memory access` persist setelah kill process
**Resolution:** Full driver reset: `rmmod nvidia_uvm nvidia_drm nvidia_modeset nvidia && modprobe`

---

## 4. Files Created/Modified

### New Files
| File | Purpose |
|------|---------|
| `implementation/dcim_ai_v2_rag/llm/finetune_proper.py` | Training script proper (643 lines) |
| `implementation/dcim_ai_v2_rag/llm/datasets/dcim_test_set.jsonl` | Held-out test set (573 samples) |

### Training Outputs (in progress)
| File | Purpose |
|------|---------|
| `implementation/dcim_ai_v2_rag/llm/models/v2.0_proper/` | Output directory |
| `implementation/dcim_ai_v2_rag/llm/models/v2.0_proper/adapter/` | LoRA adapter weights |
| `implementation/dcim_ai_v2_rag/llm/models/v2.0_proper/metadata.json` | Training metadata |
| `implementation/dcim_ai_v2_rag/llm/models/v2.0_proper/checkpoints/` | Epoch checkpoints |

---

## 5. Next Steps (Setelah Training Selesai)

1. **Evaluasi model** — `evaluate_model.py` dengan test set 573 sampel
2. **Baseline comparison** — fine-tuned vs base Qwen 2.5-3B
3. **Per-category metrics** — precision/recall/F1 untuk 9 kategori
4. **Export GGUF** — Q4_K_M untuk deployment
5. **Deploy ke llama-server** — ganti Gemma dengan model DCIM
6. **Un-stub API endpoints** — `/llm/query` dan `/llm/explain`

---

## 6. Dependencies

| Dependency | Pemilik | Status | Impact |
|------------|---------|--------|--------|
| TimescaleDB data pipeline | Syauqi / Tim AI | ⏳ Menunggu | Fase 5 (RAG) terblokir |
| Kafka metrics stream | Syauqi / Tim AI | ⏳ Menunggu | Dataset regeneration |
| CMDB API (Block 4) | Tim Infra | ⏳ Menunggu | RCA prompt contract |
| GPU availability | Fakhri | ✅ Available | Training jalan |
| Dataset (3,816 samples) | Fakhri | ✅ Available | Sudah digunakan |

---

**Last Updated:** 20 Juli 2026, ~12:20 WIB — Training step 130/501
