# MT-023 Quick Reference Guide

## 🚀 Quick Commands

### Complete Pipeline (All Tasks)
```bash
cd /home/infra/rnd_rag-anything
source ragavenv/bin/activate
./dcim_ai/llm/quickstart.sh
```

### Individual Tasks

#### Task 1: Dataset Generation
```bash
# Generate raw dataset
python -m dcim_ai.llm.dataset_generator

# Enrich with natural language
python -m dcim_ai.llm.text_enrichment

# Output: dcim_ai/llm/datasets/raw_incidents.jsonl (2,088 records)
#         dcim_ai/llm/datasets/enriched_incidents.jsonl (2,088 records)
```

#### Task 2: Instruction Dataset
```bash
# Build instruction tuning dataset
python -m dcim_ai.llm.instruction_builder --target 1500

# Output: dcim_ai/llm/datasets/dcim_instructions.jsonl (3,816 samples)
```

#### Task 3: Fine-Tuning
```bash
# Fine-tune with LoRA (default settings)
python -m dcim_ai.llm.finetune_qlora

# Custom settings
python -m dcim_ai.llm.finetune_qlora \
    --epochs 3 \
    --batch-size 1 \
    --grad-accum 16 \
    --gpu 0 \
    --version v1.1

# Output: dcim_ai/llm/models/v1.0/adapter/ (~50 MB)
# Duration: ~1.6 hours on RTX 3070 Ti
```

#### Task 4: Model Registry
```bash
# Create registry table
psql -U infra -d dcim_ai -f dcim_ai/llm/sql/create_llm_registry.sql

# Register model
python -m dcim_ai.llm.model_registry register \
    --name dcim_assistant \
    --version v1.0 \
    --adapter-path /home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/adapter

# Promote to production
python -m dcim_ai.llm.model_registry promote \
    --name dcim_assistant \
    --version v1.0

# List versions
python -m dcim_ai.llm.model_registry list --name dcim_assistant

# Show active model
python -m dcim_ai.llm.model_registry active --name dcim_assistant
```

---

## 📊 Verification Commands

### Check Dataset Files
```bash
# Line counts
wc -l dcim_ai/llm/datasets/*.jsonl

# File sizes
du -sh dcim_ai/llm/datasets/*.jsonl

# Expected output:
# 2088 raw_incidents.jsonl
# 2088 enriched_incidents.jsonl
# 3816 dcim_instructions.jsonl
```

### Check Model Artifacts
```bash
# List model versions
ls -lh dcim_ai/llm/models/

# Check adapter files
ls -lh dcim_ai/llm/models/v1.0/adapter/

# View metadata
cat dcim_ai/llm/models/v1.0/metadata.json | jq
```

### Check System Status
```bash
# GPU status
nvidia-smi

# PostgreSQL status
sudo systemctl status postgresql

# Test DB connection
psql -U infra -d dcim_ai -c "SELECT COUNT(*) FROM server_metrics;"

# Python environment
source ragavenv/bin/activate
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

---

## 🧪 Testing & Evaluation

### Evaluate Model
```bash
# Via llama-server (recommended)
python -m dcim_ai.llm.evaluate_model --endpoint http://localhost:8080

# Direct adapter loading
python -m dcim_ai.llm.evaluate_model \
    --adapter dcim_ai/llm/models/v1.0/adapter \
    --base-model Qwen/Qwen2.5-3B-Instruct
```

### Quick Test
```bash
# Test single prompt
python3 << 'EOF'
import requests
import json

prompt = """Apakah ada anomali yang terdeteksi? Jelaskan.

Data: {"metrics": {"cpu_usage": 92.5, "memory_usage": 88.3}, "prediction": "anomaly", "severity": "critical"}"""

response = requests.post("http://localhost:8080/v1/completions", json={
    "prompt": prompt,
    "max_tokens": 256,
    "temperature": 0.7
})

print(response.json()["choices"][0]["text"])
EOF
```

---

## 🚢 Production Deployment

### Start Inference Server

#### Option 1: llama.cpp
```bash
cd /home/infra/llama.cpp
./llama-server \
    -m /home/infra/models/dcim_assistant_v1.0_q8_0.gguf \
    --port 8080 \
    --ctx-size 4096 \
    --n-gpu-layers 35 \
    --threads 8
```

#### Option 2: vLLM
```bash
vllm serve Qwen/Qwen2.5-3B-Instruct \
    --enable-lora \
    --lora-modules dcim_assistant=/home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/adapter \
    --port 8080 \
    --gpu-memory-utilization 0.8
```

### Export to GGUF
```bash
# Merge adapter with base model
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

---

## 🔧 Troubleshooting

### CUDA Out of Memory
```bash
# Reduce batch size
python -m dcim_ai.llm.finetune_qlora --batch-size 1 --grad-accum 32

# Use single GPU
CUDA_VISIBLE_DEVICES=0 python -m dcim_ai.llm.finetune_qlora
```

### Database Connection Error
```bash
# Start PostgreSQL
sudo systemctl start postgresql

# Test connection
psql -U infra -d dcim_ai -c "SELECT 1;"

# Check credentials in dcim_ai/core/data_loader.py
```

### Model Artifacts Not Found
```bash
# Check registry
cat dcim_ai/registry/registry.json

# Verify artifacts
ls -lh dcim_ai/artifacts/models/v1.4/
```

### Import Errors
```bash
# Reinstall dependencies
source ragavenv/bin/activate
pip install -r requirements.txt

# Check torch installation
python -c "import torch; print(torch.__version__)"
```

---

## 📁 File Locations

### Scripts
```
dcim_ai/llm/
├── dataset_generator.py      # Task 1: Generate raw dataset
├── text_enrichment.py         # Task 1: Add natural language
├── instruction_builder.py     # Task 2: Build instruction dataset
├── finetune_qlora.py          # Task 3: Fine-tune with LoRA
├── model_registry.py          # Task 4: Registry management
├── evaluate_model.py          # Evaluation
├── export_gguf.py             # Export to GGUF
└── quickstart.sh              # Complete pipeline
```

### Datasets
```
dcim_ai/llm/datasets/
├── raw_incidents.jsonl        # 2,088 structured JSON records
├── enriched_incidents.jsonl   # 2,088 with natural language
└── dcim_instructions.jsonl    # 3,816 instruction samples
```

### Models
```
dcim_ai/llm/models/
└── v1.0/
    ├── adapter/               # LoRA adapter (~50 MB)
    ├── checkpoints/           # Training checkpoints
    └── metadata.json          # Training metadata
```

### SQL
```
dcim_ai/llm/sql/
└── create_llm_registry.sql    # Registry table schema
```

---

## 📚 Documentation

- **Complete Guide**: `dcim_ai/llm/MT-023_COMPLETE_DOCUMENTATION.md`
- **Quick Reference**: `dcim_ai/llm/QUICK_REFERENCE.md` (this file)
- **Original Spec**: `/home/infra/MT-023_Model_Preparation_Detail.md`

---

## 🎯 Current Status

- ✅ Task 1: Dataset Generation (100%)
- ✅ Task 2: Instruction Dataset (100%)
- ✅ Task 3: Fine-Tuning (100%)
- ⚠️ Task 4: Model Registry (60% - DB integration pending)

**Overall Progress**: 85% Complete

---

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review complete documentation
3. Check logs in `dcim_ai/llm/models/v1.0/checkpoints/`
4. Verify system prerequisites (GPU, PostgreSQL, Python env)
