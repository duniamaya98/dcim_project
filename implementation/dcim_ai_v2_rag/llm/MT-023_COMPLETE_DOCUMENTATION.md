# MT-023 — Model Preparation & Fine-Tuning
## Complete Implementation Documentation

**Project**: DCIM AI Platform Extension  
**Module**: MT-023 (LLM Fine-Tuning)  
**Status**: ✅ 85% Complete (Task 1-3 Done, Task 4 Partial)  
**Date**: May 11, 2026  
**Location**: `/home/infra/rnd_rag-anything/dcim_ai/llm/`

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [System Configuration](#2-system-configuration)
3. [Task 1: Dataset Generation](#3-task-1-dataset-generation)
4. [Task 2: Instruction Dataset](#4-task-2-instruction-dataset)
5. [Task 3: Fine-Tuning (LoRA)](#5-task-3-fine-tuning-lora)
6. [Task 4: Model Registry](#6-task-4-model-registry)
7. [Evaluation & Testing](#7-evaluation--testing)
8. [Production Deployment](#8-production-deployment)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. Overview

### Objective
Transform DCIM AI system from "data-driven engine" to "AI that can explain and assist decision-making" by fine-tuning LLM with domain-specific knowledge.

### Pipeline Architecture
```
DCIM Output (MT-018 to MT-022)
        ↓
Dataset Generator (Task 1)
        ↓
Text Enrichment
        ↓
Instruction Builder (Task 2)
        ↓
Fine-Tuning LoRA (Task 3)
        ↓
Model Registry (Task 4)
        ↓
Production LLM
```

### Key Results
- ✅ **3,816 instruction samples** generated
- ✅ **Model v1.0** fine-tuned (Qwen2.5-3B + LoRA)
- ✅ **Training loss: 0.310** (converged)
- ⚠️ **Registry integration** pending

---

## 2. System Configuration

### Hardware
```
Server: srv-rnd-llm (QEMU/KVM VM)
CPU: Intel i7-11700KF @ 3.60GHz (8 cores)
RAM: 28 GB
GPU 0: NVIDIA RTX 3070 Ti (8 GB VRAM)
GPU 1: NVIDIA RTX 3070 Ti (8 GB VRAM)
Storage: 1 TB SSD (424 GB free)
CUDA: 12.0, Driver 575.51.03
```

### Software Environment
```bash
OS: Ubuntu 24.04 LTS
Python: 3.12.3
Virtual Environment: /home/infra/rnd_rag-anything/ragavenv
Working Directory: /home/infra/rnd_rag-anything/
```

### Database
```
Engine: PostgreSQL 16
Connection: postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai
Tables:
  - server_metrics (19,442 rows)
  - anomaly_events (47 rows)
  - model_registry (5 rows)
```

### Python Dependencies
```
torch==2.9.1
transformers==4.57.5
peft==0.14.0
trl==0.13.0
bitsandbytes==0.45.0
accelerate==1.2.1
datasets==3.2.0
huggingface-hub==0.36.0
numpy, pandas, scikit-learn
sqlalchemy, psycopg2-binary
joblib
```

---

## 3. Task 1: Dataset Generation

### 3.1 Overview
Generate structured JSON dataset by simulating full DCIM pipeline (MT-018 to MT-022) against `server_metrics` data.

### 3.2 Script: `dataset_generator.py`

**Location**: `dcim_ai/llm/dataset_generator.py`

**Pipeline Simulation**:
1. **Ensemble Prediction** (IForest + LOF + OCSVM)
2. **Drift Detection** (Z-score vs baseline)
3. **Domain Scoring** (compute, memory, storage, network)
4. **Temporal Correlation** (sliding window 20 snapshots)
5. **Aggregation** (anomaly_ratio, domain_persistence, co-occurrence)
6. **Severity Matrix** (escalation rules)
7. **Root Cause Analysis** (softmax + causal chain DFS)

**Configuration**:
```python
DB_URL = "postgresql+psycopg2://infra:StrongPassword123@127.0.0.1/dcim_ai"
WINDOW_SIZE = 20
FEATURE_COLUMNS = ["cpu_usage", "memory_usage", "disk_io", "net_rx", "net_tx"]
DOMAIN_ACTIVATION_THRESHOLD = 3.0
```

### 3.3 How to Run

```bash
# Activate environment
cd /home/infra/rnd_rag-anything
source ragavenv/bin/activate

# Run generator
python -m dcim_ai.llm.dataset_generator
```

**Output**: `dcim_ai/llm/datasets/raw_incidents.jsonl` (2,088 records)  
**Duration**: ~2-3 minutes  
**Requirements**: PostgreSQL running, model artifacts at `dcim_ai/artifacts/models/v1.4/`

### 3.4 Output Structure
```json
{
  "id": 1,
  "timestamp": "2026-02-12 09:02:44",
  "hostname": "srv-rnd-llm",
  "model_version": "v1.4",
  "metrics": {
    "cpu_usage": 85.2,
    "memory_usage": 72.1,
    "disk_io": 45.0,
    "net_rx": 120.5,
    "net_tx": 80.3
  },
  "prediction": {
    "result": "anomaly",
    "anomaly_votes": 3,
    "severity": "critical"
  },
  "drift": {
    "score": 2.5,
    "status": "moderate_drift",
    "feature_z_scores": {...}
  },
  "domain_state": {
    "domain_scores": {...},
    "active_domains": ["compute", "memory"]
  },
  "aggregation": {
    "anomaly_ratio": 0.8,
    "domain_trend": {...}
  },
  "rca": {
    "root_domain": "memory",
    "confidence": 0.88,
    "causal_chain": [...]
  }
}
```

### 3.5 Text Enrichment

**Script**: `text_enrichment.py`

```bash
python -m dcim_ai.llm.text_enrichment
```

**Output**: `enriched_incidents.jsonl` (2,088 records with natural language fields)

**Enrichment Fields**:
- `nl_summary`: Overall condition summary
- `nl_metrics`: Metrics description
- `nl_drift`: Drift analysis
- `nl_domain`: Domain analysis
- `nl_temporal`: Temporal trend
- `nl_rca`: Root cause explanation
- `nl_recommendation`: Action recommendations
- `nl_full_explanation`: Combined explanation

---

## 4. Task 2: Instruction Dataset

### 4.1 Overview
Convert enriched records into instruction tuning format `{instruction, input, output}`.

### 4.2 Script: `instruction_builder.py`

**Location**: `dcim_ai/llm/instruction_builder.py`

**Instruction Categories** (9 types):
1. **summary** — "Jelaskan kondisi sistem berdasarkan data berikut."
2. **anomaly** — "Apakah ada anomali yang terdeteksi?"
3. **root_cause** — "Apa root cause dari masalah ini?"
4. **impact** — "Apa dampak dari kondisi ini?"
5. **recommendation** — "Apa rekomendasi tindakan?"
6. **drift** — "Analisis drift dari data monitoring."
7. **domain** — "Domain infrastruktur mana yang terpengaruh?"
8. **temporal** — "Bagaimana tren temporal dari kondisi ini?"
9. **full_analysis** — "Lakukan analisis lengkap."

### 4.3 How to Run

```bash
python -m dcim_ai.llm.instruction_builder --target 1500
```

**Output**: `dcim_instructions.jsonl` (3,816 samples)  
**Duration**: ~5 seconds  
**Parameter**: `--target` = target samples (default: 1000)

### 4.4 Output Format
```json
{
  "id": 1,
  "instruction": "Apa root cause dari masalah ini?",
  "input": "Server metrics — cpu_usage: 0.6, memory_usage: 29.7...",
  "output": "Root cause analysis menunjukkan domain memori (RAM)...",
  "metadata": {
    "source_id": 1263,
    "instruction_type": "root_cause",
    "severity": "critical",
    "prediction": "anomaly",
    "root_domain": "memory",
    "timestamp": "2026-02-12 09:02:44"
  }
}
```

### 4.5 Dataset Statistics

**Instruction Type Distribution**:
```
drift:          757 (19.8%)
summary:        713 (18.7%)
temporal:       643 (16.9%)
recommendation: 324 (8.5%)
anomaly:        323 (8.5%)
root_cause:     321 (8.4%)
full_analysis:  320 (8.4%)
domain:         295 (7.7%)
impact:         120 (3.1%)
```

**Severity Distribution**:
```
normal:       2,093 (54.8%)
warning:        870 (22.8%)
weak_signal:    542 (14.2%)
critical:       306 (8.0%)
high:             5 (0.1%)
```

---

## 5. Task 3: Fine-Tuning (LoRA)

### 5.1 Overview
Fine-tune Qwen2.5-3B-Instruct with LoRA adapters on DCIM instruction dataset.

### 5.2 Script: `finetune_qlora.py`

**Location**: `dcim_ai/llm/finetune_qlora.py`

**Model Configuration**:
```
Base Model: Qwen/Qwen2.5-3B-Instruct
Method: LoRA (4-bit quantization via BitsAndBytes)
LoRA r: 16
LoRA alpha: 32
LoRA dropout: 0.05
Target Modules: q_proj, k_proj, v_proj, o_proj, 
                gate_proj, up_proj, down_proj
```

**Training Configuration**:
```
Epochs: 3
Batch Size: 1
Gradient Accumulation: 16 (effective batch = 16)
Learning Rate: 2e-4
Max Sequence Length: 512
Warmup Ratio: 0.05
Optimizer: AdamW (paged_adamw_8bit)
```

### 5.3 How to Run

```bash
# Activate environment
cd /home/infra/rnd_rag-anything
source ragavenv/bin/activate

# Basic run (default settings)
python -m dcim_ai.llm.finetune_qlora

# Custom settings
python -m dcim_ai.llm.finetune_qlora \
    --epochs 3 \
    --batch-size 2 \
    --gpu 0 \
    --version v1.1
```

**Parameters**:
```
--epochs: Number of training epochs (default: 3)
--batch-size: Per-device batch size (default: 1)
--grad-accum: Gradient accumulation steps (default: 16)
--lr: Learning rate (default: 2e-4)
--max-seq-len: Max sequence length (default: 512)
--gpu: GPU device ID (default: 0)
--version: Model version name (default: auto-generated)
```

**Duration**: ~1.6 hours (5,838 seconds) on RTX 3070 Ti  
**VRAM Usage**: ~6.5 GB

### 5.4 Training Results (v1.0)

```
Dataset: 3,816 samples
Train/Eval Split: 3,434 / 382 (90/10)
Final Train Loss: 0.310
Training Steps: 645
Checkpoints: checkpoint-600, checkpoint-645
GPU: RTX 3070 Ti (GPU 0)
Created: 2026-05-05 11:53:58
```

### 5.5 Output Artifacts

**Directory Structure**:
```
dcim_ai/llm/models/v1.0/
├── adapter/
│   ├── adapter_model.safetensors  (~50 MB)
│   ├── adapter_config.json
│   ├── tokenizer.json
│   ├── tokenizer_config.json
│   ├── vocab.json
│   ├── merges.txt
│   ├── special_tokens_map.json
│   ├── added_tokens.json
│   ├── chat_template.jinja
│   └── README.md
├── checkpoints/
│   ├── checkpoint-600/
│   │   ├── adapter_model.safetensors
│   │   ├── adapter_config.json
│   │   └── training_args.bin
│   └── checkpoint-645/
│       └── (same structure)
└── metadata.json
```

**Metadata** (`metadata.json`):
```json
{
  "version": "v1.0",
  "base_model": "Qwen/Qwen2.5-3B-Instruct",
  "method": "LoRA on AWQ",
  "lora_r": 16,
  "lora_alpha": 32,
  "lora_target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
  "epochs": 3,
  "batch_size": 1,
  "grad_accum": 16,
  "effective_batch_size": 16,
  "learning_rate": 0.0002,
  "max_seq_len": 512,
  "dataset": "/home/infra/rnd_rag-anything/dcim_ai/llm/datasets/dcim_instructions.jsonl",
  "dataset_size": 3816,
  "train_size": 3434,
  "eval_size": 382,
  "train_loss": 0.31006272827932074,
  "train_runtime_seconds": 5838.7567,
  "created_at": "2026-05-05T11:53:58.320659",
  "gpu": "RTX 3070 Ti (GPU 0)"
}
```

---

## 6. Task 4: Model Registry

### 6.1 Overview
Manage fine-tuned models with version control, production/candidate status, and rollback capability.

### 6.2 Current Status

**✅ Completed**:
- Versioned folder structure (`models/v1.0/`)
- Metadata JSON with training details
- Adapter artifacts saved

**⚠️ Pending**:
- Database registration (extend `model_registry` table)
- Production/candidate status management
- A/B testing mechanism
- Rollback workflow

### 6.3 Database Schema (To Implement)

```sql
CREATE TABLE llm_model_registry (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(50) NOT NULL,
    base_model VARCHAR(200),
    adapter_path VARCHAR(500),
    status VARCHAR(20) DEFAULT 'candidate',  -- candidate/production/archived
    metrics_json JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    activated_at TIMESTAMP,
    is_active BOOLEAN DEFAULT FALSE,
    UNIQUE(model_name, version)
);

CREATE INDEX idx_llm_active ON llm_model_registry(model_name, is_active);
```

### 6.4 Registry Script (To Create)

**File**: `dcim_ai/llm/model_registry.py`

```python
from sqlalchemy import text
import json
from dcim_ai.core.data_loader import get_db_engine

engine = get_db_engine()

def register_llm_model(model_name, version, base_model, adapter_path, metrics):
    """Register new LLM model version"""
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO llm_model_registry 
            (model_name, version, base_model, adapter_path, metrics_json, status)
            VALUES (:model_name, :version, :base_model, :adapter_path, :metrics, 'candidate')
        """), {
            "model_name": model_name,
            "version": version,
            "base_model": base_model,
            "adapter_path": adapter_path,
            "metrics": json.dumps(metrics)
        })
        conn.commit()

def promote_to_production(model_name, version):
    """Promote candidate to production"""
    with engine.connect() as conn:
        # Deactivate current production
        conn.execute(text("""
            UPDATE llm_model_registry
            SET is_active = FALSE, status = 'archived'
            WHERE model_name = :model_name AND is_active = TRUE
        """), {"model_name": model_name})
        
        # Activate new version
        conn.execute(text("""
            UPDATE llm_model_registry
            SET is_active = TRUE, status = 'production', activated_at = NOW()
            WHERE model_name = :model_name AND version = :version
        """), {"model_name": model_name, "version": version})
        
        conn.commit()

def get_active_model(model_name):
    """Get current production model"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT version, adapter_path, metrics_json
            FROM llm_model_registry
            WHERE model_name = :model_name AND is_active = TRUE
            LIMIT 1
        """), {"model_name": model_name})
        
        row = result.fetchone()
        if row:
            return {
                "version": row._mapping["version"],
                "adapter_path": row._mapping["adapter_path"],
                "metrics": json.loads(row._mapping["metrics_json"])
            }
        return None

def list_versions(model_name):
    """List all versions"""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT version, status, created_at, is_active
            FROM llm_model_registry
            WHERE model_name = :model_name
            ORDER BY created_at DESC
        """), {"model_name": model_name})
        
        return [dict(row._mapping) for row in result]
```

### 6.5 How to Register Model v1.0

```bash
# Create registry table
psql -U infra -d dcim_ai -f dcim_ai/llm/sql/create_llm_registry.sql

# Register model
python3 << EOF
from dcim_ai.llm.model_registry import register_llm_model
import json

with open('dcim_ai/llm/models/v1.0/metadata.json') as f:
    metadata = json.load(f)

register_llm_model(
    model_name="dcim_assistant",
    version="v1.0",
    base_model=metadata["base_model"],
    adapter_path="/home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/adapter",
    metrics={
        "train_loss": metadata["train_loss"],
        "dataset_size": metadata["dataset_size"],
        "epochs": metadata["epochs"]
    }
)
print("✅ Model v1.0 registered as candidate")
EOF
```

---

## 7. Evaluation & Testing

### 7.1 Evaluation Script

**File**: `dcim_ai/llm/evaluate_model.py`

**Test Prompts** (6 categories):
1. Anomaly detection
2. Root cause analysis
3. Recommendation
4. Drift analysis
5. Normal condition
6. Multi-domain analysis

### 7.2 How to Run Evaluation

**Option 1: Via llama-server** (recommended)

```bash
# Start llama-server with fine-tuned model
cd /home/infra/llama.cpp
./llama-server \
    -m /home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/adapter/model.gguf \
    --port 8080 \
    --ctx-size 4096 \
    --n-gpu-layers 35

# Run evaluation
cd /home/infra/rnd_rag-anything
source ragavenv/bin/activate
python -m dcim_ai.llm.evaluate_model --endpoint http://localhost:8080
```

**Option 2: Direct adapter loading**

```bash
python -m dcim_ai.llm.evaluate_model \
    --adapter dcim_ai/llm/models/v1.0/adapter \
    --base-model Qwen/Qwen2.5-3B-Instruct
```

### 7.3 Evaluation Metrics

**Qualitative**:
- Response relevance
- Domain terminology accuracy
- Hallucination check
- Consistency with RCA logic

**Quantitative** (to implement):
- Perplexity
- BLEU/ROUGE scores
- Domain keyword coverage
- Response length distribution

### 7.4 Sample Test

```bash
python3 << 'EOF'
import requests
import json

prompt = """Apakah ada anomali yang terdeteksi? Jelaskan.

Data: {"metrics": {"cpu_usage": 92.5, "memory_usage": 88.3}, "prediction": "anomaly", "severity": "critical", "active_domains": ["compute", "memory"], "drift_score": 3.8}"""

response = requests.post("http://localhost:8080/v1/completions", json={
    "prompt": prompt,
    "max_tokens": 256,
    "temperature": 0.7
})

print(response.json()["choices"][0]["text"])
EOF
```

---

## 8. Production Deployment

### 8.1 Export to GGUF (for llama.cpp)

**Script**: `export_gguf.py`

```bash
# Merge LoRA adapter with base model
python -m dcim_ai.llm.export_gguf \
    --adapter dcim_ai/llm/models/v1.0/adapter \
    --base-model Qwen/Qwen2.5-3B-Instruct \
    --output dcim_ai/llm/models/v1.0/merged

# Convert to GGUF
cd /home/infra/llama.cpp
python convert_hf_to_gguf.py \
    /home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/merged \
    --outfile /home/infra/models/dcim_assistant_v1.0_q8_0.gguf \
    --outtype q8_0
```

### 8.2 Start Inference Server

**llama.cpp server**:
```bash
cd /home/infra/llama.cpp
./llama-server \
    -m /home/infra/models/dcim_assistant_v1.0_q8_0.gguf \
    --port 8080 \
    --ctx-size 4096 \
    --n-gpu-layers 35 \
    --threads 8
```

**vLLM server** (alternative):
```bash
vllm serve Qwen/Qwen2.5-3B-Instruct \
    --enable-lora \
    --lora-modules dcim_assistant=/home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/adapter \
    --port 8080 \
    --gpu-memory-utilization 0.8
```

### 8.3 API Integration

**Endpoint**: `/llm/dcim-assistant`

```python
# dcim_ai/api/llm_service.py
import requests

LLM_ENDPOINT = "http://localhost:8080/v1/completions"

def query_dcim_assistant(instruction, input_data, max_tokens=256):
    """Query fine-tuned DCIM assistant"""
    prompt = f"{instruction}\n\n{input_data}"
    
    response = requests.post(LLM_ENDPOINT, json={
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stop": ["\n\n", "###"]
    })
    
    return response.json()["choices"][0]["text"]
```

---

## 9. Troubleshooting

### 9.1 Common Issues

**Issue**: CUDA Out of Memory during training
```bash
# Solution: Reduce batch size or use gradient checkpointing
python -m dcim_ai.llm.finetune_qlora --batch-size 1 --grad-accum 32
```

**Issue**: Database connection error
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test connection
psql -U infra -d dcim_ai -c "SELECT 1;"
```

**Issue**: Model artifacts not found
```bash
# Verify model registry
cat dcim_ai/registry/registry.json

# Check artifacts directory
ls -lh dcim_ai/artifacts/models/v1.4/
```

### 9.2 Verification Commands

```bash
# Check dataset files
wc -l dcim_ai/llm/datasets/*.jsonl

# Check model artifacts
ls -lh dcim_ai/llm/models/v1.0/adapter/

# Check GPU availability
nvidia-smi

# Check Python environment
source ragavenv/bin/activate
python -c "import torch; print(torch.cuda.is_available())"
```

### 9.3 Logs Location

```
Training logs: dcim_ai/llm/models/v1.0/checkpoints/
Dataset generation: stdout (redirect to file if needed)
Inference logs: llama-server stdout
```

---

## 10. Next Steps

### Priority 1: Complete Registry Integration
1. Create `llm_model_registry` table
2. Register model v1.0
3. Implement promotion workflow

### Priority 2: Production Readiness
4. Export to GGUF format
5. Deploy inference server
6. Integrate with API layer

### Priority 3: Evaluation & Monitoring
7. Implement quantitative metrics
8. Set up A/B testing
9. Monitor response quality

---

## 11. References

- **MT-018**: Traditional ML Model
- **MT-019**: Anomaly Detection Framework
- **MT-020**: Cross-Domain Correlation Engine
- **MT-021**: Model Training & Evaluation Lifecycle
- **MT-022**: Root Cause Analysis Engine
- **MT-024**: Prompt Engineering (next phase)
- **MT-025**: RAG System (next phase)

---

**Document Version**: 1.0  
**Last Updated**: May 11, 2026  
**Author**: DCIM AI Team
