# DCIM Project - File Migration Guide

**Migration Date**: May 12, 2026  
**Purpose**: Consolidate all DCIM-related files into organized structure

---

## 📋 Migration Summary

All DCIM project files have been consolidated from scattered locations in `/home/infra/` into a single organized folder: `/home/infra/dcim_project/`

---

## 🗂️ File Mapping

### Documentation Files

| Original Location | New Location | Status |
|-------------------|--------------|--------|
| `/home/infra/DCIM_AI_ANALYSIS.md` | `dcim_project/documentation/DCIM_AI_ANALYSIS.md` | ✅ Moved |
| `/home/infra/DCIM_AI_IMPLEMENTATION_ANALYSIS.md` | `dcim_project/documentation/DCIM_AI_IMPLEMENTATION_ANALYSIS.md` | ✅ Moved |
| `/home/infra/DCIM_AI_PATH_REFERENCE.md` | `dcim_project/documentation/DCIM_AI_PATH_REFERENCE.md` | ✅ Moved |
| `/home/infra/DCIM_AI_RECONCILIATION.md` | `dcim_project/documentation/DCIM_AI_RECONCILIATION.md` | ✅ Moved |
| `/home/infra/DCIM_AI_SUMMARY.md` | `dcim_project/documentation/DCIM_AI_SUMMARY.md` | ✅ Moved |
| `/home/infra/dcim_ai_plan.md` | `dcim_project/documentation/dcim_ai_plan.md` | ✅ Moved |
| `/home/infra/MT-023_COMPLETION_CERTIFICATE.md` | `dcim_project/documentation/MT-023_COMPLETION_CERTIFICATE.md` | ✅ Moved |
| `/home/infra/MT-023_IMPLEMENTATION_SUMMARY.md` | `dcim_project/documentation/MT-023_IMPLEMENTATION_SUMMARY.md` | ✅ Moved |
| `/home/infra/MT-023_LLM_Inference_Service_API_Layer.md` | `dcim_project/documentation/MT-023_LLM_Inference_Service_API_Layer.md` | ✅ Moved |
| `/home/infra/MT-023_Model_Preparation_Detail.md` | `dcim_project/documentation/MT-023_Model_Preparation_Detail.md` | ✅ Moved |
| `/home/infra/MT-023_UNSLOTH_INTEGRATION_ANALYSIS.md` | `dcim_project/documentation/MT-023_UNSLOTH_INTEGRATION_ANALYSIS.md` | ✅ Moved |

### Implementation Folders

| Original Location | New Location | Status |
|-------------------|--------------|--------|
| `/home/infra/dcim_ai/` | `dcim_project/implementation/dcim_ai_v1/` | ✅ Moved |
| `/home/infra/rnd_rag-anything/dcim_ai/` | `dcim_project/implementation/dcim_ai_v2_rag/` | ✅ Moved |
| `/home/infra/rnd_llm/` | `dcim_project/implementation/dcim_rnd_llm/` | ✅ Moved |
| `/home/infra/benchmark_model/` | `dcim_project/implementation/dcim_benchmark/` | ✅ Moved |

### Reference Documentation

| Original Location | New Location | Status |
|-------------------|--------------|--------|
| `/home/infra/affine_document/MT-004_Analytics & AI Foundation/` | `dcim_project/reference_docs/MT-004_Analytics & AI Foundation/` | ✅ Copied |

### Analysis Files

| Original Location | New Location | Status |
|-------------------|--------------|--------|
| `/home/infra/ANALYSIS_INDEX.md` | `dcim_project/analysis/ANALYSIS_INDEX.md` | ✅ Moved |

---

## 🔧 Required Updates

### 1. Update Import Paths in Python Scripts

**Old paths**:
```python
from dcim_ai.llm import dataset_generator
from dcim_ai.rag import query_engine
```

**New paths** (if running from project root):
```python
from implementation.dcim_ai_v2_rag.llm import dataset_generator
from implementation.dcim_ai_v2_rag.rag import query_engine
```

**Recommended**: Run scripts from their respective directories:
```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
python -m llm.dataset_generator
```

### 2. Update Database Connection Strings

No changes needed - database connection remains:
```
postgresql://infra:StrongPassword123@127.0.0.1/dcim_ai
```

### 3. Update Model Paths

**Old path**:
```
/home/infra/rnd_rag-anything/dcim_ai/llm/models/v1.0/adapter/
```

**New path**:
```
/home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/models/v1.0/adapter/
```

**Update in**:
- Model registry database records
- Configuration files
- Deployment scripts

### 4. Update Virtual Environment Activation

Virtual environment location remains unchanged:
```bash
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
```

---

## ✅ Verification Steps

### 1. Check File Structure
```bash
cd /home/infra/dcim_project
tree -L 2
```

Expected output:
```
dcim_project/
├── README.md
├── MIGRATION_GUIDE.md
├── documentation/
│   ├── DCIM_AI_*.md (5 files)
│   ├── MT-023_*.md (6 files)
│   └── dcim_ai_plan.md
├── implementation/
│   ├── dcim_ai_v1/
│   ├── dcim_ai_v2_rag/
│   └── dcim_rnd_llm/
├── reference_docs/
│   └── MT-004_Analytics & AI Foundation/
└── analysis/
    └── ANALYSIS_INDEX.md
```

### 2. Verify Model Files
```bash
ls -lh /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/models/v1.0/adapter/
```

Expected: `adapter_model.safetensors` (~58 MB) and config files

### 3. Test Model Registry
```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
source /home/infra/rnd_rag-anything/ragavenv/bin/activate
python -m llm.model_registry active --name dcim_assistant
```

Expected: Shows dcim_assistant v1.0 as active production model

### 4. Test Dataset Access
```bash
wc -l /home/infra/dcim_project/implementation/dcim_ai_v2_rag/llm/datasets/*.jsonl
```

Expected: 2088, 2088, 3816 lines

---

## 🔄 Rollback Instructions

If you need to revert the migration:

```bash
# Move documentation back
cd /home/infra/dcim_project/documentation
mv DCIM_AI_*.md MT-023_*.md dcim_ai_plan.md /home/infra/

# Move implementations back
cd /home/infra/dcim_project/implementation
mv dcim_ai_v1 /home/infra/dcim_ai
mv dcim_ai_v2_rag /home/infra/rnd_rag-anything/dcim_ai
mv dcim_rnd_llm /home/infra/rnd_llm

# Move analysis back
mv /home/infra/dcim_project/analysis/ANALYSIS_INDEX.md /home/infra/

# Remove project folder
cd /home/infra
rm -rf dcim_project
```

---

## 📝 Post-Migration Tasks

### Immediate (Priority 1)
- [x] Create organized folder structure
- [x] Move all documentation files
- [x] Move all implementation folders
- [x] Create README.md and MIGRATION_GUIDE.md
- [ ] Update model registry database with new paths
- [ ] Test all scripts with new paths
- [ ] Update any hardcoded paths in configuration files

### Short-term (Priority 2)
- [ ] Update deployment scripts
- [ ] Update CI/CD pipelines (if any)
- [ ] Update team documentation
- [ ] Notify team members of new structure

### Long-term (Priority 3)
- [ ] Archive old backup folders
- [ ] Clean up unused files
- [ ] Optimize folder structure based on usage patterns

---

## 🚨 Important Notes

1. **Virtual Environment**: The virtual environment at `/home/infra/rnd_rag-anything/ragavenv` was NOT moved to avoid breaking dependencies. Continue using it as before.

2. **Database Records**: The model registry database still references old paths. Update these manually:
   ```sql
   UPDATE llm_model_registry 
   SET adapter_path = REPLACE(adapter_path, 
       '/home/infra/rnd_rag-anything/dcim_ai/', 
       '/home/infra/dcim_project/implementation/dcim_ai_v2_rag/')
   WHERE model_name = 'dcim_assistant';
   ```

3. **Symbolic Links**: Consider creating symbolic links for backward compatibility:
   ```bash
   ln -s /home/infra/dcim_project/implementation/dcim_ai_v2_rag /home/infra/rnd_rag-anything/dcim_ai
   ```

4. **Backup**: Original folder structure is preserved in `/home/infra/rnd_rag-anything/` (except dcim_ai which was moved). The `affine_document` folder was copied, not moved.

---

## 📞 Support

If you encounter issues after migration:

1. Check this guide for path updates
2. Verify file permissions: `chmod -R u+rwX /home/infra/dcim_project`
3. Check symbolic links: `ls -la /home/infra/dcim_project/implementation/`
4. Review error messages for old path references

---

**Migration Completed**: May 12, 2026  
**Status**: ✅ Successful  
**Next Step**: Update database paths and test all scripts
