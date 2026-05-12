# MT-023 — Model Preparation & Fine-Tuning (Detailed Task Description)

## 1. Overview

Tahap ini merupakan lanjutan dari MT-023 (Infrastructure Setup) yang berfokus pada:
- Transformasi data DCIM menjadi dataset LLM
- Pembuatan instruction dataset
- Fine-tuning model agar domain-aware
- Manajemen model secara versioned (artifact registry)

Tujuan utama:
> Mengubah sistem DCIM dari "data-driven engine" menjadi "AI yang bisa menjelaskan dan membantu decision"

---

## 2. Task 1 — Kumpulkan Dataset DCIM Incident & Telemetry Explanation

### Objective
Mengumpulkan data dari pipeline DCIM (MT-018 s.d MT-022) untuk dijadikan knowledge dasar LLM.

### Data Source (WAJIB)
- MT-018 → Output prediction
- MT-019 → Anomaly + drift
- MT-020 → Correlation & incident
- MT-022 → Root Cause Analysis (RCA)

### Data Structure (Contoh)
```json
{
  "severity": "critical",
  "domain_state": {
    "active_domains": ["compute", "memory"]
  },
  "aggregation_state": {
    "anomaly_ratio": 0.85,
    "drift_ratio": 0.7
  },
  "rca": {
    "root_cause": "compute overload",
    "confidence": 0.88
  }
}
```

### Enrichment (WAJIB)
Data harus dikonversi menjadi natural language:

```text
Sistem mengalami kondisi kritis akibat overload pada domain compute.
Terdapat indikasi drift tinggi yang menunjukkan perubahan pola penggunaan.
```

### Output Dataset
- Input: structured JSON
- Output: natural language explanation

---

## 3. Task 2 — Buat Dataset Instruction Tuning

### Objective
Mengubah dataset menjadi format training LLM.

### Format Standar
```json
{
  "instruction": "Jelaskan kondisi sistem",
  "input": {...},
  "output": "..."
}
```

### Variasi Instruction (WAJIB)
- Jelaskan anomaly
- Apa root cause?
- Apa dampaknya?
- Apa rekomendasi tindakan?
- Ringkas kondisi

### Requirement
- Dataset minimal 500–1000 sample
- Variasi prompt harus banyak
- Output harus konsisten

### Tujuan
- Model menjadi fleksibel
- Bisa menjawab berbagai jenis pertanyaan

---

## 4. Task 3 — Fine-Tune Model (LoRA / QLoRA)

### Objective
Menyesuaikan model agar memahami domain DCIM.

---

### Metode

#### LoRA
- Training ringan
- Tidak melatih seluruh model
- Cepat dan hemat resource

#### QLoRA (Recommended)
- LoRA + quantization
- Hemat VRAM
- Cocok untuk GPU terbatas (RTX/A5000)

---

### Workflow
```text
Load Base Model
    ↓
Load Dataset
    ↓
Train LoRA Adapter
    ↓
Evaluate Model
```

---

### Tools
- HuggingFace Transformers
- PEFT (Parameter Efficient Fine-Tuning)
- Axolotl (simplified training)

---

### Evaluation
- Relevansi output
- Konsistensi
- Kesesuaian RCA
- Minim hallucination

---

### Output
- Model adapter (LoRA)
- Ready untuk inference

---

## 5. Task 4 — Simpan Model Versioned (Artifact Registry)

### Objective
Mengelola model secara production-grade.

---

### Struktur
```text
models/
 ├── v1.0/
 ├── v1.1/
 ├── v1.2/
```

---

### Isi Artifact
- Model adapter
- Tokenizer
- Config
- Metadata

---

### Metadata Example
```json
{
  "version": "v1.2",
  "base_model": "qwen2.5",
  "dataset": "dcim_v1",
  "created_at": "2026-05-01"
}
```

---

### Feature
- Version control
- Rollback
- A/B testing
- Production vs candidate

---

## 6. Dependencies (Keterkaitan dengan MT-018 s.d MT-022)

| Module | Peran |
|--------|------|
| MT-018 | Prediction data |
| MT-019 | Anomaly + drift |
| MT-020 | Correlation & incident |
| MT-022 | Root cause |
| MT-021 | Lifecycle governance |

---

## 7. End-to-End Flow

```text
DCIM Output
    ↓
Dataset Generator
    ↓
Instruction Dataset
    ↓
Fine-Tuning
    ↓
Model Registry
    ↓
Production LLM
```

---

## 8. Requirement Sebelum Memulai

### Data
- Minimal 100–1000 sample JSON
- Output RCA tersedia

### Infra
- GPU (RTX 3070 / A5000)
- Model base (Qwen / Phi)

### Tools
- Python environment
- transformers / peft
- llama.cpp / Ollama

---

## 9. Expected Output

- Model yang memahami DCIM
- Bisa menjelaskan anomaly
- Bisa memberikan rekomendasi
- Siap digunakan untuk:
  - Chat AI
  - Dashboard explanation
  - Decision support system

---

## 10. Conclusion

Tahap ini merupakan inti dari:
> Transformasi AI system → AI intelligence

Tanpa tahap ini:
- LLM hanya generic

Dengan tahap ini:
- LLM menjadi domain expert (DCIM AI Assistant)
