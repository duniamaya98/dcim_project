# DCIM AI Platform Extensions

This platform extends the existing DCIM system with advanced AI capabilities.

## Components

### 🔵 MT-023 — Private LLM Platform
- **Model**: Llama-3-8B-Instruct (4-bit AWQ)
- **Engine**: vLLM
- **API**: `/llm/inference`
- **Integration**: All components use this unified endpoint for text generation tasks.

### 🔵 MT-024 — Prompt Engineering
- Centralized `PromptManager` in `prompting/manager.py`.
- Supports versioned templates using Jinja2.
- Maps system metrics (`anomaly_ratio`, `drift_ratio`) directly into LLM prompts.

### 🔵 MT-025 — RAG System
- **Store**: Qdrant Vector DB.
- **Data**: Historical incidents, infrastructure SOPs.
- **Workflow**: Context-aware retrieval for RCA and query answering.

### 🔵 MT-026 — Contextual Query Engine
- **Endpoint**: `/dcim/query`
- **Logic**: Combines real-time metrics, historical knowledge (RAG), and LLM reasoning to explain complex system states.

### 🔵 MT-027 — What-If Simulation Engine
- **Endpoint**: `/simulation/run`
- **Logic**: Generates synthetic failures, predicts pipeline results (anomaly/incident), and provides LLM-based risk assessments.

## Integration with Existing DCIM

1. **Anomaly pipeline**: After an anomaly is detected by the Isolation Forest, call `/llm/inference` with the `ANOMALY_EXPLANATION` template to get a human-readable reason.
2. **Incident Management**: Use `/rag/query` to find similar past incidents and provide recommended SOPs to technicians.
3. **Dashboards**: Integrate `/dcim/query` for a natural language search bar where operators can ask "Why did power usage spike last night?"
