# DCIM AI Platform - Testing Guide

This guide describes how to verify each component of the new DCIM AI extension.

## 1. Environment Preparation
Ensure you have the required Python packages installed:
```bash
pip install fastapi uvicorn httpx qdrant-client sentence-transformers jinja2 numpy
```

## 2. Component Testing (Step-by-Step)

### A. Test MT-023 (LLM Inference API)
To test the API logic without needing the full 15GB Llama model immediately, you can run a mock test.

1. **Start the API Wrapper**:
   ```bash
   export VLLM_API_URL="http://mock-url" # Or your actual vLLM URL
   python3 /home/infra/dcim_ai/llm/inference_api.py
   ```
2. **Send a Test Request**:
   ```bash
   curl -X POST http://localhost:8080/llm/inference \
   -H "Content-Type: application/json" \
   -d '{"prompt": "Explain a cooling failure in a data center."}'
   ```

### B. Test MT-025 (RAG System)
Verify that knowledge can be indexed and retrieved.
```python
from dcim_ai.rag.engine import RAGSystem

rag = RAGSystem()
# Index mock SOP
rag.index_document("SOP-001", "If temperature > 30C, check Chiller-01.", {"domain": "cooling"})

# Search
results = rag.search("What to do if it gets too hot?")
print(f"RAG Result: {results[0]['text']}")
```

### C. Test MT-026 (Contextual Query Engine)
This is the "main" interface for operators.
```bash
curl -X POST http://localhost:8090/dcim/query \
-H "Content-Type: application/json" \
-d '{"user_query": "Why is the anomaly ratio so high in the Power domain?"}'
```

### D. Test MT-027 (What-If Simulation)
Simulate a failure and get an AI analysis.
```bash
curl -X POST http://localhost:8090/simulation/run \
-H "Content-Type: application/json" \
-d '{"scenario": "cooling_failure", "severity": 0.8}'
```

---

## 3. Automated Test Suite
I have provided a comprehensive test script at `/home/infra/dcim_ai/scripts/test_all.py`. 
You can run it to verify the integration logic across all modules.

```bash
python3 /home/infra/dcim_ai/scripts/test_all.py
```
