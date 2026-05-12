# MT-023 — Model Preparation & Fine-Tuning

## LLM Dataset Generation Pipeline

Dokumentasi lengkap untuk proses transformasi data DCIM menjadi dataset instruction tuning LLM.

---

## 1. Overview

Pipeline ini mengubah output dari sistem DCIM AI (MT-018 s.d MT-022) menjadi dataset training untuk fine-tuning LLM agar menjadi domain-aware DCIM AI Assistant.

### Arsitektur Pipeline

```
PostgreSQL (server_metrics: 19.347 rows)
        ↓
[1] Dataset Generator (simulasi full pipeline)
        ↓
    raw_incidents.jsonl (2.088 records)
        ↓
[2] Text Enrichment (JSON → Natural Language)
        ↓
    enriched_incidents.jsonl (2.088 records)
        ↓
[3] Instruction Builder (→ instruction tuning format)
        ↓
    dcim_instructions.jsonl (3.816 samples)
        ↓
[4] Fine-Tuning (QLoRA) ← NEXT STEP
        ↓
    DCIM AI Assistant Model
```

---

## 2. Konfigurasi Sistem

### Environment

| Komponen | Detail |
|----------|--------|
| Server | srv-rnd-llm (VM QEMU/KVM) |
| OS | Ubuntu 24.04 LTS |
| Python | 3.12.3 |
| Virtual Environment | `/home/infra/rnd_rag-anything/ragavenv` |
| Working Directory | `/home/infra/rnd_rag-anything/` |

### Hardware

| Komponen | Spesifikasi |
|----------|-------------|
| CPU | Intel i7-11700KF @ 3.60GHz (8 cores) |
| RAM | 28 GB |
| GPU 0 | NVIDIA RTX 3070 Ti (8 GB VRAM) |
| GPU 1 | NVIDIA RTX 3070 Ti (8 GB VRAM) |
| Storage | 1 TB SSD (424 GB free) |
| CUDA | 12.0, Driver 575.51.03 |

### Database

| Parameter | Nilai |
|-----------|-------|
| Engine | PostgreSQL 16 |
| Connection | `postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai` |
| Tabel utama | `server_metrics` (19.442 rows, 12-19 Feb 2026) |
| Tabel audit | `anomaly_events` (47 rows) |
| Tabel registry | `model_registry` (5 rows) |

### Model ML (Production)

| Parameter | Nilai |
|-----------|-------|
| Version | v1.4 |
| Algoritma | Ensemble (IsolationForest + LOF + OCSVM) |
| Features | `cpu_usage`, `memory_usage`, `disk_io`, `net_rx`, `net_tx` |
| Artifacts | `dcim_ai/artifacts/models/v1.4/` |
| Registry | `dcim_ai/registry/registry.json` |

### Python Dependencies (sudah terinstall di ragavenv)

```
torch==2.9.1
transformers==4.57.5
huggingface-hub==0.36.0
numpy
pandas
scikit-learn
sqlalchemy
psycopg2-binary
joblib
```

---

## 3. File yang Dibuat

### Scripts

| File | Fungsi | Lines |
|------|--------|-------|
| `dcim_ai/llm/__init__.py` | Module init | 1 |
| `dcim_ai/llm/dataset_generator.py` | Simulasi full DCIM pipeline → raw JSON | ~380 |
| `dcim_ai/llm/text_enrichment.py` | Konversi JSON → natural language | ~280 |
| `dcim_ai/llm/instruction_builder.py` | Build instruction tuning dataset | ~300 |

### Output Datasets

| File | Records | Size | Deskripsi |
|------|---------|------|-----------|
| `dcim_ai/llm/datasets/raw_incidents.jsonl` | 2.088 | 2.9 MB | Structured JSON per incident |
| `dcim_ai/llm/datasets/enriched_incidents.jsonl` | 2.088 | 6.5 MB | + Natural language fields |
| `dcim_ai/llm/datasets/dcim_instructions.jsonl` | 3.816 | 2.8 MB | Format instruction tuning |

---

## 4. Detail Setiap Komponen

### 4.1 Dataset Generator (`dataset_generator.py`)

**Fungsi:** Mensimulasikan seluruh pipeline DCIM AI terhadap data `server_metrics` untuk menghasilkan dataset structured JSON.

**Pipeline yang disimulasikan:**
1. **Ensemble Prediction** — 3 model (IForest, LOF, OCSVM), majority vote ≥2/3
2. **Drift Detection** — Z-score terhadap baseline mean/std
3. **Domain Scoring** — Map feature z-scores ke domain (compute, memory, storage, network)
4. **Temporal Correlation** — Sliding window 20 snapshots
5. **Aggregation** — anomaly_ratio, domain_persistence, co-occurrence, trend
6. **Severity Matrix** — Escalation rules
7. **Root Cause Analysis** — Softmax + composite scoring + causal chain (DFS)

**Konfigurasi:**

```python
DB_URL = "postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai"
WINDOW_SIZE = 20  # sliding window untuk temporal correlation
FEATURE_COLUMNS = ["cpu_usage", "memory_usage", "disk_io", "net_rx", "net_tx"]
DOMAIN_ACTIVATION_THRESHOLD = 3.0  # z-score threshold
```

**Output record structure:**
```json
{
  "id": 1,
  "timestamp": "2026-02-12 ...",
  "hostname": "srv-rnd-llm",
  "model_version": "v1.4",
  "metrics": {"cpu_usage": 85.2, "memory_usage": 72.1, ...},
  "prediction": {"result": "anomaly", "anomaly_votes": 3, "severity": "critical", ...},
  "drift": {"score": 2.5, "status": "moderate_drift", "feature_z_scores": {...}},
  "domain_state": {"domain_scores": {...}, "active_domains": [...], ...},
  "aggregation": {"anomaly_ratio": 0.8, "domain_trend": {...}, ...},
  "incident": {"severity": "critical", "confidence": 0.95},
  "rca": {"root_domain": "memory", "confidence": 0.88, "causal_chain": [...], ...}
}
```

**Filter:** Hanya menyimpan record yang memiliki "signal" (anomaly, drift non-stable, atau active domains).

---

### 4.2 Text Enrichment (`text_enrichment.py`)

**Fungsi:** Mengkonversi setiap field structured JSON menjadi natural language explanation.

**7 jenis enrichment yang dihasilkan:**

| Field | Deskripsi | Contoh |
|-------|-----------|--------|
| `nl_summary` | Ringkasan kondisi | "Sistem mendeteksi anomali dengan kondisi KRITIS pada domain memori (RAM)..." |
| `nl_metrics` | Deskripsi metrik | "CPU usage tinggi (85.2%); memory usage kritis (92.1%)..." |
| `nl_drift` | Analisis drift | "Drift score: 2.50 (moderate_drift). Fitur dengan drift tertinggi: memory_usage (z=4.2)..." |
| `nl_domain` | Analisis domain | "Domain aktif: memori (RAM) (skor: 4.2). Domain strength index: 3.8..." |
| `nl_temporal` | Analisis temporal | "Dalam window 20 snapshot terakhir: rasio anomali 80%, tren meningkat pada memori..." |
| `nl_rca` | Analisis root cause | "Root cause: domain memori (RAM) sebagai penyebab utama dengan confidence 88%..." |
| `nl_recommendation` | Rekomendasi | "Eskalasi segera. Periksa memory leak, pertimbangkan restart service..." |
| `nl_full_explanation` | Gabungan semua | Semua field di atas digabung |

**Konfigurasi mapping:**
- Domain names: compute→"komputasi (CPU)", memory→"memori (RAM)", dll
- Severity descriptions: critical→"kondisi KRITIS yang memerlukan tindakan segera"
- Drift descriptions: severe_drift→"pergeseran berat dari baseline"
- Threshold interpretasi: CPU >90% = "sangat tinggi", >70% = "tinggi", dll

---

### 4.3 Instruction Builder (`instruction_builder.py`)

**Fungsi:** Mengkonversi enriched records menjadi format instruction tuning `{instruction, input, output}`.

**9 kategori instruction:**

| Kategori | Variasi Prompt | Contoh |
|----------|---------------|--------|
| `summary` | 6 | "Jelaskan kondisi sistem berdasarkan data berikut." |
| `anomaly` | 5 | "Apakah ada anomali yang terdeteksi? Jelaskan." |
| `root_cause` | 6 | "Apa root cause dari masalah ini?" |
| `impact` | 5 | "Apa dampak dari kondisi ini terhadap infrastruktur?" |
| `recommendation` | 6 | "Apa rekomendasi tindakan untuk kondisi ini?" |
| `drift` | 4 | "Analisis drift dari data monitoring berikut." |
| `domain` | 4 | "Domain infrastruktur mana yang terpengaruh?" |
| `temporal` | 4 | "Bagaimana tren temporal dari kondisi ini?" |
| `full_analysis` | 4 | "Lakukan analisis lengkap terhadap data monitoring berikut." |

**Strategi distribusi:**
- **High-interest records** (anomaly/active domains/drift): 5 instruction types per record
- **Low-interest records** (normal): 1 instruction type per record
- Input format divariasikan: compact JSON, natural text, mixed

**Konfigurasi:**
```python
--target 1500  # target jumlah samples (actual: 3816 karena high-interest × 5)
```

**Output format:**
```json
{
  "id": 1,
  "instruction": "Apa root cause dari masalah ini?",
  "input": "Server metrics — cpu_usage: 0.6, memory_usage: 29.7...",
  "output": "Root cause analysis menunjukkan domain memori (RAM) sebagai penyebab utama...",
  "metadata": {
    "source_id": 1263,
    "instruction_type": "root_cause",
    "severity": "critical",
    "prediction": "anomaly",
    "root_domain": "memory",
    "timestamp": "2026-02-12 09:02:44..."
  }
}
```

---

## 5. Statistik Dataset Final

### Distribusi Instruction Type

| Type | Count | % |
|------|-------|---|
| drift | 757 | 19.8% |
| summary | 713 | 18.7% |
| temporal | 643 | 16.9% |
| recommendation | 324 | 8.5% |
| anomaly | 323 | 8.5% |
| root_cause | 321 | 8.4% |
| full_analysis | 320 | 8.4% |
| domain | 295 | 7.7% |
| impact | 120 | 3.1% |

### Distribusi Severity

| Severity | Count | % |
|----------|-------|---|
| normal | 2.093 | 54.8% |
| warning | 870 | 22.8% |
| weak_signal | 542 | 14.2% |
| critical | 306 | 8.0% |
| high | 5 | 0.1% |

### Distribusi Prediction

| Prediction | Instructions |
|------------|-------------|
| anomaly | 1.120 (29.4%) |
| normal | 2.696 (70.6%) |

### Distribusi Root Domain

| Root Domain | Count |
|-------------|-------|
| unknown | 1.728 (82.8% of raw) |
| memory | 245 (11.7%) |
| compute | 115 (5.5%) |

---

## 6. Cara Menjalankan

### Prerequisites

```bash
# Aktivasi virtual environment
source /home/infra/rnd_rag-anything/ragavenv/bin/activate

# Pastikan working directory
cd /home/infra/rnd_rag-anything
```

### Step 1: Generate Raw Dataset

```bash
python -m dcim_ai.llm.dataset_generator
```

**Output:** `dcim_ai/llm/datasets/raw_incidents.jsonl`
**Durasi:** ~2-3 menit (19.347 samples)
**Requirement:** PostgreSQL running, model artifacts di `dcim_ai/artifacts/models/v1.4/`

### Step 2: Text Enrichment

```bash
python -m dcim_ai.llm.text_enrichment
```

**Output:** `dcim_ai/llm/datasets/enriched_incidents.jsonl`
**Durasi:** ~10 detik
**Requirement:** `raw_incidents.jsonl` harus sudah ada

### Step 3: Build Instruction Dataset

```bash
python -m dcim_ai.llm.instruction_builder --target 1500
```

**Output:** `dcim_ai/llm/datasets/dcim_instructions.jsonl`
**Durasi:** ~5 detik
**Requirement:** `enriched_incidents.jsonl` harus sudah ada
**Parameter:** `--target` = target jumlah samples (default: 1000)

### Run All (Sequential)

```bash
cd /home/infra/rnd_rag-anything
source ragavenv/bin/activate

python -m dcim_ai.llm.dataset_generator && \
python -m dcim_ai.llm.text_enrichment && \
python -m dcim_ai.llm.instruction_builder --target 1500
```

---

## 7. Testing & Verifikasi

### Verifikasi File Output

```bash
# Cek file sizes dan line counts
du -sh dcim_ai/llm/datasets/*.jsonl
wc -l dcim_ai/llm/datasets/*.jsonl
```

Expected:
```
2.9M    raw_incidents.jsonl
6.5M    enriched_incidents.jsonl
2.8M    dcim_instructions.jsonl

2088 raw_incidents.jsonl
2088 enriched_incidents.jsonl
3816 dcim_instructions.jsonl
```

### Verifikasi Kualitas Dataset

```bash
python3 -c "
import json
from collections import Counter

with open('dcim_ai/llm/datasets/dcim_instructions.jsonl') as f:
    records = [json.loads(l) for l in f]

print(f'Total samples: {len(records)}')

# Instruction type distribution
types = Counter(r['metadata']['instruction_type'] for r in records)
print(f'Instruction types: {dict(types)}')

# Severity distribution
sevs = Counter(r['metadata']['severity'] for r in records)
print(f'Severity: {dict(sevs)}')

# Prediction distribution
preds = Counter(r['metadata']['prediction'] for r in records)
print(f'Prediction: {dict(preds)}')

# Root domain distribution
roots = Counter(r['metadata']['root_domain'] for r in records)
print(f'Root domain: {dict(roots)}')
"
```

### Lihat Sample Record

```bash
# Sample instruction (critical anomaly)
python3 -c "
import json
with open('dcim_ai/llm/datasets/dcim_instructions.jsonl') as f:
    for line in f:
        r = json.loads(line)
        if r['metadata']['severity'] == 'critical' and r['metadata']['prediction'] == 'anomaly':
            print('INSTRUCTION:', r['instruction'])
            print('INPUT:', r['input'][:200])
            print('OUTPUT:', r['output'])
            break
"
```

### Validasi Format untuk Fine-Tuning

```bash
# Pastikan semua record punya field yang diperlukan
python3 -c "
import json

errors = 0
with open('dcim_ai/llm/datasets/dcim_instructions.jsonl') as f:
    for i, line in enumerate(f):
        r = json.loads(line)
        if not all(k in r for k in ['instruction', 'input', 'output']):
            errors += 1
            print(f'Missing field at line {i}')
        if len(r['output']) < 10:
            errors += 1
            print(f'Short output at line {i}: {r[\"output\"]}')

print(f'Validation: {errors} errors found')
"
```

---

## 8. Troubleshooting

### Database Connection Error

```
Failed postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai
```

**Solusi:** Pastikan PostgreSQL running:
```bash
sudo systemctl status postgresql
```

### Model Artifacts Not Found

```
FileNotFoundError: dcim_ai/artifacts/models/v1.4/models.pkl
```

**Solusi:** Cek registry dan artifacts:
```bash
cat dcim_ai/registry/registry.json | python3 -m json.tool
ls dcim_ai/artifacts/models/v1.4/
```

### Empty Dataset (0 records)

**Kemungkinan:** Semua data `server_metrics` sudah di-drop karena NULL.
**Solusi:** Cek data:
```bash
python3 -c "
from sqlalchemy import create_engine, text
engine = create_engine('postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai')
with engine.connect() as conn:
    r = conn.execute(text('SELECT COUNT(*) FROM server_metrics WHERE cpu_usage IS NOT NULL'))
    print(f'Valid rows: {r.scalar()}')
"
```

---

## 9. Keterkaitan dengan Dokumen Referensi

| Dokumen | Relevansi |
|---------|-----------|
| MT-018 (Traditional ML Model) | Source: model artifacts, feature columns, baseline stats |
| MT-019 (Anomaly Detection Framework) | Source: ensemble voting, drift detection, model registry |
| MT-020 (Cross-Domain Correlation Engine) | Source: domain mapping, correlation buffer, aggregation |
| MT-021 (Model Training Lifecycle) | Source: training orchestrator, artifact structure |
| MT-022 (Root Cause Analysis Engine) | Source: RCA engine, causal topology, lifecycle manager |
| MT-023 (Private LLM Platform) | Context: benchmark results, model selection (Qwen3.5:4B) |

---

## 10. Task 3 — Fine-Tuning & Model Preparation

### Status Dependencies (sudah terinstall di ragavenv)

```
peft==0.19.1
bitsandbytes==0.49.2
trl==1.3.0
datasets==4.8.5
accelerate==1.13.0
torch==2.9.1
transformers==4.57.5
```

### Base Model (Fine-Tuning)

| Parameter | Nilai |
|-----------|-------|
| Model | `Qwen/Qwen2.5-3B-Instruct` |
| Method | QLoRA (BitsAndBytes 4-bit NF4) |
| Size | 6.2 GB full-weight (lokal di HF cache) |
| Architecture | Qwen2, 36 layers, hidden=2048, vocab=152064 |
| Location | `~/.cache/huggingface/hub/models--Qwen--Qwen2.5-3B-Instruct/` |
| VRAM saat training | ~5.5 GB (muat di 1× RTX 3070 Ti 8GB) |

#### Kenapa Qwen2.5-3B-Instruct?

| Pertimbangan | Detail |
|-------------|--------|
| **VRAM constraint** | 1× RTX 3070 Ti = 8GB. Model 7B QLoRA butuh ~10-12GB → OOM. Model 3B QLoRA = ~5.5GB → muat. |
| **AWQ deprecated** | `Qwen2.5-7B-AWQ` (5.2GB, lokal) tidak bisa dipakai — `autoawq` incompatible dengan `transformers 4.57.5` (`PytorchGELUTanh` removed). |
| **GGUF tidak bisa di-fine-tune** | Model Qwen3 yang ada di cache hanya format GGUF (untuk llama.cpp/Ollama) — tidak bisa di-load dengan PEFT/LoRA. |
| **Narrow domain** | Task DCIM (anomaly, drift, RCA) terstruktur dan repetitif — 3B parameter + LoRA sudah cukup. |
| **Alternatif** | Multi-GPU split (2× 8GB = 16GB) bisa untuk 7B, tapi menambah kompleksitas. |

### Inference Server (Baseline Evaluation)

| Parameter | Nilai |
|-----------|-------|
| Server | llama-server (llama.cpp) |
| Model | Qwen3-VL-4B-Instruct (GGUF Q4_K_M) |
| Endpoint | `http://localhost:8080` |
| GPU | GPU0 (RTX 3070 Ti, ~7.2GB VRAM used) |
| Catatan | Harus di-stop saat fine-tuning untuk free GPU |

### Baseline Evaluation (Pre-Fine-Tune)

Model base (Qwen3-VL-4B) sudah dievaluasi terhadap 6 test DCIM:

| Metric | Score |
|--------|-------|
| Overall Relevance | **0.83 / 1.0** (🟢 GOOD) |
| Keyword Score | 0.69 / 1.0 |
| Average Latency | 4.8s |
| Tests Passed | **6/6** |

Per-category:
- ✅ anomaly_detection: 100% keywords
- ✅ root_cause: 75% keywords
- ✅ recommendation: 80% keywords
- ✅ drift_analysis: 50% keywords
- ✅ normal_condition: 67% keywords
- ✅ multi_domain: 40% keywords

Report: `dcim_ai/llm/datasets/eval_baseline.json`

### Synthetic Dataset Enhancement

Menggunakan model running (Qwen3-VL-4B) sebagai "teacher" untuk memperkaya dataset:

| Metric | Nilai |
|--------|-------|
| Samples enhanced | 200 / 200 (0 failed) |
| Avg output length (LLM) | **1.259 chars** |
| Avg output length (template) | 194 chars |
| Enhancement ratio | 6.5x lebih kaya |
| Output file | `dcim_instructions_enhanced.jsonl` |

### Scripts Task 3

| File | Fungsi |
|------|--------|
| `dcim_ai/llm/finetune_qlora.py` | QLoRA fine-tuning (BitsAndBytes 4-bit) |
| `dcim_ai/llm/evaluate_model.py` | Evaluasi model via endpoint atau adapter |
| `dcim_ai/llm/export_gguf.py` | Merge adapter + convert ke GGUF |
| `dcim_ai/llm/synthetic_generator.py` | Enhance dataset via running LLM |

### Fine-Tuning Configuration

```python
BASE_MODEL = "Qwen/Qwen2.5-3B-Instruct"
LORA_R = 16
LORA_ALPHA = 32
LORA_DROPOUT = 0.05
LORA_TARGET_MODULES = ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"]
BATCH_SIZE = 1
GRAD_ACCUM = 16          # effective batch = 16
MAX_SEQ_LEN = 512
EPOCHS = 3
LR = 2e-4
QUANTIZATION = "BitsAndBytes NF4 (load_in_4bit)"
OPTIMIZER = "paged_adamw_8bit"
TRAINABLE_PARAMS = "29.9M / 3.1B (0.96%)"
```

### Cara Menjalankan Fine-Tuning

```bash
# 1. Stop llama-server (free GPU VRAM)
# 2. Jalankan fine-tuning
cd /home/infra/rnd_rag-anything
source ragavenv/bin/activate
PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
python -m dcim_ai.llm.finetune_qlora \
    --epochs 3 --batch-size 1 --grad-accum 16 \
    --max-seq-len 512 --gpu 0 --version v1.0

# 3. Evaluate
python -m dcim_ai.llm.evaluate_model --adapter dcim_ai/llm/models/v1.0/adapter

# 4. Export ke GGUF
python -m dcim_ai.llm.export_gguf --adapter dcim_ai/llm/models/v1.0/adapter --step all

# 5. Deploy via Ollama
ollama create dcim-ai -f dcim_ai/llm/models/v1.0/Modelfile
```

### Error yang Ditemui & Solusi

| Error | Penyebab | Solusi |
|-------|----------|--------|
| `ImportError: autoawq` | AWQ library belum terinstall | `pip install autoawq` |
| `cannot import 'PytorchGELUTanh'` | AutoAWQ deprecated, incompatible dengan transformers 4.57 | Switch ke BitsAndBytes QLoRA + model full-weight |
| `TypeError: max_seq_length` | trl 1.3.0 menggunakan `SFTConfig.max_length` bukan `SFTTrainer.max_seq_length` | Gunakan `SFTConfig(max_length=512)` |
| `NotImplementedError: BFloat16` | fp16 grad scaler tidak support BFloat16 dari model 4-bit | Set `bf16=True, fp16=False` |
| `CUDA out of memory` | batch_size=2 + seq_len=1024 + 3B model = >8GB | Turunkan ke batch_size=1, seq_len=512 (~5.5GB) |

### Cara Evaluate Model Running (Tanpa Fine-Tune)

```bash
# Evaluate model yang sedang running di llama-server
python -m dcim_ai.llm.evaluate_model --endpoint http://localhost:8080
```

### Cara Generate Synthetic Data (Menggunakan Model Running)

```bash
# Enhance 200 high-interest samples
python -m dcim_ai.llm.synthetic_generator --endpoint http://localhost:8080 --samples 200
```

---

## 11. Task 4 — Model Versioning & Deployment

### Struktur Artifact (Setelah Fine-Tune)

```
dcim_ai/llm/models/
└── v1.0/
    ├── adapter/           # LoRA adapter weights
    │   ├── adapter_config.json
    │   ├── adapter_model.safetensors
    │   └── tokenizer files
    ├── merged/            # Full merged model (HF format)
    ├── dcim-ai-f16.gguf  # GGUF F16
    ├── dcim-ai-Q4_K_M.gguf  # GGUF quantized
    ├── Modelfile          # Ollama deployment file
    ├── metadata.json      # Training metadata
    └── train_metrics.json # Training loss/metrics
```

### Deployment Options

| Method | Command | Use Case |
|--------|---------|----------|
| llama-server | `llama-server -m dcim-ai-Q4_K_M.gguf -ngl 99 --port 8080` | Production API |
| Ollama | `ollama create dcim-ai -f Modelfile && ollama run dcim-ai` | Easy deployment |
| Python (PEFT) | `evaluate_model.py --adapter path/to/adapter` | Development/testing |

---

## 12. Dataset Files Summary

| File | Records | Size | Deskripsi |
|------|---------|------|-----------|
| `raw_incidents.jsonl` | 2.088 | 2.9 MB | Structured JSON per incident |
| `enriched_incidents.jsonl` | 2.088 | 6.5 MB | + Natural language fields |
| `dcim_instructions.jsonl` | 3.816 | 2.8 MB | Instruction tuning (template) |
| `dcim_instructions_enhanced.jsonl` | 3.816 | 3.0 MB | Instruction tuning (200 LLM-enhanced) |
| `eval_baseline.json` | 6 tests | - | Baseline evaluation report |

---

## 13. Kesimpulan & Rekomendasi

### Temuan Utama

1. **Model base sudah cukup bagus** (0.83 relevance) untuk DCIM domain tanpa fine-tuning
2. **Synthetic enhancement** berhasil menghasilkan output 6.5x lebih kaya
3. **Dataset siap** untuk fine-tuning (3.816 samples, 200 LLM-enhanced)
4. **Infrastructure siap** — semua dependencies terinstall, model AWQ lokal

### Rekomendasi Deployment

| Skenario | Rekomendasi |
|----------|-------------|
| Quick deployment | Gunakan model base + system prompt (sudah 0.83) |
| Better quality | Fine-tune LoRA + deploy GGUF |
| Best quality | Fine-tune + synthetic data augmentation + iterasi |

### Catatan VRAM & Hardware

| Operasi | VRAM Dibutuhkan | GPU |
|---------|----------------|-----|
| Fine-tuning QLoRA (3B, batch=1, seq=512) | ~5.5 GB | 1× RTX 3070 Ti |
| llama-server (Qwen3-VL-4B GGUF) | ~7.2 GB | 1× RTX 3070 Ti |
| Fine-tuning + inference | **Tidak bisa bersamaan** | Harus pilih salah satu |

- llama-server harus di-stop dulu saat fine-tuning
- Setelah fine-tune, export ke GGUF dan jalankan kembali llama-server
- Untuk model 7B: butuh multi-GPU split (2× 8GB) atau GPU lebih besar

---

*Dokumentasi ini dibuat: 4 Mei 2026*
*Terakhir diupdate: 4 Mei 2026 (fine-tuning config & troubleshooting)*
*Pipeline dijalankan terhadap data: 12-19 Februari 2026 (19.442 rows server_metrics)*
*Synthetic enhancement: 200 samples via Qwen3-VL-4B (llama-server)*
*Fine-tuning: Qwen2.5-3B-Instruct + QLoRA 4-bit (BitsAndBytes NF4)*
