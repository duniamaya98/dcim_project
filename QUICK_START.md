# 🚀 DCIM Project - Quick Start Guide

**Project Location**: `/home/infra/dcim_project/`  
**Last Updated**: May 12, 2026

---

## ⚡ Quick Access

### Load Shortcuts (Recommended)
```bash
source /home/infra/dcim_project/dcim_shortcuts.sh
```

This loads helpful aliases like:
- `dcim` - Go to project root
- `dcim-v2` - Go to DCIM AI v2 (main implementation)
- `dcim-llm` - Go to LLM folder
- `dcim-activate` - Activate Python environment
- `dcim-registry-active` - Show active model
- `dcim-help` - Show all shortcuts

---

## 📁 Project Structure

```
dcim_project/
├── 📚 documentation/          # All project docs (11 files)
├── 💻 implementation/         # All code
│   ├── dcim_ai_v1/           # Original version
│   ├── dcim_ai_v2_rag/       # ⭐ Main version (MT-023)
│   ├── dcim_rnd_llm/         # Research
│   └── dcim_benchmark/       # Benchmarking & performance tests
├── 📖 reference_docs/         # MT-004 references
└── 📊 analysis/               # Analysis docs
```

---

## 🎯 Common Tasks

### 1. Check Active Model
```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
python model_registry_standalone.py active --name dcim_assistant
```

**Or with shortcuts**:
```bash
dcim-registry-active
```

### 2. Run Dataset Generation
```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
python -m llm.dataset_generator
```

### 3. Fine-Tune Model
```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
python -m llm.finetune_qlora
```

### 4. List All Models
```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
python model_registry_standalone.py list --name dcim_assistant
```

**Or with shortcuts**:
```bash
dcim-registry-list
```

---

## 📚 Documentation

### Main Docs
- **Project Overview**: `README.md`
- **Migration Guide**: `MIGRATION_GUIDE.md`
- **Consolidation Summary**: `CONSOLIDATION_SUMMARY.md`
- **This Guide**: `QUICK_START.md`

### MT-023 Docs (in `implementation/dcim_ai_v2_rag/llm/`)
- **Complete Guide**: `MT-023_COMPLETE_DOCUMENTATION.md`
- **Quick Reference**: `QUICK_REFERENCE.md`
- **Status**: `STATUS.txt`
- **Final Report**: `FINAL_REPORT.txt`

### Project Docs (in `documentation/`)
- All DCIM analysis docs
- All MT-023 specification docs

---

## 🔧 Environment Setup

### Virtual Environment
```bash
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
```

### Database
```
Host: 127.0.0.1
Port: 5432
Database: dcim_ai
User: infra
Password: StrongPassword123
```

### GPU
```bash
nvidia-smi  # Check GPU status
```

---

## 🎓 Current Status

### Production Model
- **Name**: dcim_assistant
- **Version**: v1.0
- **Status**: ✅ PRODUCTION (Active)
- **Base Model**: Qwen/Qwen2.5-3B-Instruct
- **Training Loss**: 0.310
- **Dataset**: 3,816 samples
- **Location**: `implementation/dcim_ai_v2_rag/llm/models/v1.0/adapter/`

### Completed Tasks
- ✅ Task 1: Dataset Generation (2,088 + 2,088 + 3,816 samples)
- ✅ Task 2: Instruction Dataset (9 categories)
- ✅ Task 3: Fine-Tuning (LoRA, loss: 0.310)
- ✅ Task 4: Model Registry (v1.0 in production)

---

## 🆘 Troubleshooting

### Can't find files?
All DCIM files are now in `/home/infra/dcim_project/`

### Module not found errors?
Use `model_registry_standalone.py` instead of `model_registry.py`

### Old paths not working?
Symbolic link created at `/home/infra/rnd_rag-anything/dcim_ai` for backward compatibility

### Need help?
```bash
dcim-help  # Show all shortcuts
cat /home/infra/dcim_project/README.md  # Read full documentation
```

---

## 📞 Quick Links

- **Project Root**: `/home/infra/dcim_project/`
- **Main Implementation**: `implementation/dcim_ai_v2_rag/`
- **LLM Code**: `implementation/dcim_ai_v2_rag/llm/`
- **Models**: `implementation/dcim_ai_v2_rag/llm/models/`
- **Documentation**: `documentation/`
- **Virtual Env**: `/home/infra/rnd_rag-anything/ragavenv`

---

**Status**: ✅ Ready for Development  
**Version**: 2.0 (Consolidated)  
**Date**: May 12, 2026
