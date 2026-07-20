# MT-023 Private LLM Platform — Alignment Analysis

> **Dokumen:** Analisis keselarasan MT-023 dengan kebutuhan DCIM Core Platform
> **Tanggal:** 2026-07-03 | **Status:** ANALYSIS COMPLETE
> **Sumber MT-023:** AFFiNE — 10 versi dokumen (FINAL, MERGED, AI_Model_Specs, dll)
> **Sumber Referensi:** Block 7 Reference Design (Section 9: LLM/RAG), FIT041 UC24-25
> **Analyst:** Hermes DCIM Orchestrator

---

## Daftar Isi

1. [Ringkasan Eksekutif](#1-ringkasan-eksekutif)
2. [Coverage MT-023 vs Block 7 Reference Design](#2-coverage-mt-023-vs-block-7-reference-design)
3. [Coverage MT-023 vs FIT041 Requirements](#3-coverage-mt-023-vs-fit041-requirements)
4. [Gap Analysis Detail](#4-gap-analysis-detail)
5. [Strength: What MT-023 Already Deliver](#5-strength-what-mt-023-already-deliver)
6. [Risk Analysis](#6-risk-analysis)
7. [Rekomendasi Alignment](#7-rekomendasi-alignment)
8. [Action Items](#8-action-items)

---

## 1. Ringkasan Eksekutif

### Status Alignment

| Aspek | Status | Persentase |
|-------|--------|-----------|
| **Inference Platform** | ✅ COMPLETE | 100% |
| **Model Selection & Benchmark** | ✅ COMPLETE | 100% |
| **Quantization Strategy** | ✅ COMPLETE | 100% |
| **RAG Pipeline** | ❌ NOT COVERED | 0% |
| **API Layer (DCIM Endpoints)** | ❌ NOT COVERED | 0% |
| **CMDB/ES/Runbook Integration** | ❌ NOT COVERED | 0% |
| **Security (RBAC, Vault, Audit)** | ❌ NOT COVERED | 0% |
| **Deployment Architecture** | ❌ NOT COVERED | 0% |
| **Monitoring & SLA** | ❌ NOT COVERED | 0% |

### Kesimpulan Utama

**MT-023 adalah fondasi yang solid tapi BELUM lengkap.**

MT-023 berhasil menyelesaikan **layer inferensi** (model selection, benchmark, quantization) — ini adalah **prasyarat kritis** sebelum membangun LLM/RAG service untuk DCIM.

Namun, Block 7 Reference Design membutuhkan **full LLM/RAG Explanation Layer** yang mencakup:

1. **RAG Pipeline** — Vector DB + embedding + context assembly
2. **DCIM Integration** — CMDB topology, Elasticsearch logs, Runbooks, TimescaleDB metrics
3. **API Layer** — 4 endpoint (`/query`, `/explain`, `/context/{ci_id}`, `/history`)
4. **Security** — RBAC, Vault, audit logging
5. **Monitoring** — Prometheus metrics, latency tracking
6. **Deployment** — Production-ready container spec

**Gap utama:** MT-023 = "What model to use and how fast it runs"
Block 7 = "How to build a complete LLM/RAG service with DCIM integration"

---

## 2. Coverage MT-023 vs Block 7 Reference Design

### 2.1 Block 7 — Section 9 (LLM/RAG Explanation Layer)

| Requirement (Block 7) | MT-023 Coverage | Status | Gap Detail |
|------------------------|-----------------|--------|------------|
| **9.1 Architecture** | | | |
| Intent Classification | ❌ | Not covered | No intent classifier implemented |
| RAG Retrieval Pipeline | ❌ | Not covered | No vector DB, no embedding pipeline |
| Context Assembly | ❌ | Not covered | No multi-source context assembly |
| LLM Generation | ✅ | Covered | Ollama/llama.cpp inference working |
| Response + Citations | ❌ | Not covered | No citation mechanism |
| **9.2 Knowledge Sources** | | | |
| CMDB (CI data, topology) | ❌ | Not covered | No CMDB integration |
| Logs (Elasticsearch) | ❌ | Not covered | No ES connector |
| Runbooks (Markdown) | ❌ | Not covered | No document ingestion |
| Historical Incidents | ❌ | Not covered | No incident store integration |
| Metrics (TimescaleDB) | ❌ | Not covered | No TS query integration |
| Documentation (Wiki) | ❌ | Not covered | No wiki ingestion |
| **9.3 Query Flow** | | | |
| CI info from CMDB | ❌ | Not covered | — |
| Recent metrics from TSDB | ❌ | Not covered | — |
| Recent incidents from ES | ❌ | Not covered | — |
| Relevant runbooks | ❌ | Not covered | — |
| Context assembly | ❌ | Not covered | — |
| NL explanation generation | ⚠️ Partial | Model capable but no pipeline | — |
| **9.4 API Design** | | | |
| `POST /analytics/llm/query` | ❌ | Not covered | No API server |
| `POST /analytics/llm/explain` | ❌ | Not covered | — |
| `GET /analytics/llm/context/{ci_id}` | ❌ | Not covered | — |
| `GET /analytics/llm/history` | ❌ | Not covered | — |

**Skor: 1/17 requirements terpenuhi (5.9%)**

### 2.2 Block 7 — Section 10 (Performance & Sizing)

| Requirement (Block 7) | MT-023 Coverage | Status | Detail |
|------------------------|-----------------|--------|--------|
| LLM throughput: 20 queries/min | ✅ | Benchmark shows 83-178 tok/s | Sufficient |
| LLM latency: < 5s p99 | ✅ | Latency 0.28-1.37s avg | Exceeds target |
| Resource: 4 vCPU, 8GB RAM | ⚠️ Partial | Server has i7-11700 + 30GB RAM | Resource available |
| Resource: 20GB embeddings storage | ❌ | No embeddings pipeline | — |

**Skor: 2.5/4 requirements (62.5%)**

### 2.3 Block 7 — Section 11 (Security)

| Requirement (Block 7) | MT-023 Coverage | Status |
|------------------------|-----------------|--------|
| Model artifacts encrypted at rest | ❌ | Not addressed |
| Training data anonymized | N/A | No training pipeline |
| LLM queries audit logged | ❌ | Not implemented |
| RBAC (analytics.read/write/admin) | ❌ | Not implemented |
| Vault for API keys | ❌ | Not implemented |

**Skor: 0/5 (0%)**

### 2.4 Block 7 — Section 12 (Monitoring)

| Requirement (Block 7) | MT-023 Coverage | Status |
|------------------------|-----------------|--------|
| `analytics_llm_query_latency_seconds` | ❌ | No Prometheus metrics |
| `analytics_model_accuracy` | ⚠️ Partial | Benchmark scores available |
| `analytics_model_drift_score` | ❌ | No drift monitoring |
| Alert: LLM latency > 10s | ❌ | No alerting |

**Skor: 0.5/4 (12.5%)**

### 2.5 Block 7 — Acceptance Criteria (LLM-specific)

| Criterion | MT-023 | Status |
|-----------|--------|--------|
| #14: LLM/RAG working — NL query returns contextual answer | ❌ | No RAG pipeline |

---

## 3. Coverage MT-023 vs FIT041 Requirements

### 3.1 FIT041 — UC24-25 (LLM/RAG Layer)

| Requirement (FIT041) | MT-023 Coverage | Status |
|----------------------|-----------------|--------|
| UC24: NL query untuk anomaly explanation | ⚠️ Partial | Model mampu, pipeline belum ada |
| UC25: Context-aware response dengan CMDB data | ❌ | No CMDB integration |
| Vector Database support (FAISS, Qdrant) | ❌ | No vector DB configured |
| Unstructured Data Ingestion (PDF, DOCX) | ❌ | No document pipeline |
| Data Lake Architecture | ❌ | No data lake for LLM context |
| Tenant Isolation | ❌ | Not addressed |

**Skor: 0.5/6 (8.3%)**

### 3.2 FIT041 — Strengths yang Dimanfaatkan MT-023

| FIT041 Strength | MT-023 Relevance | Utilization |
|-----------------|-------------------|-------------|
| Unstructured Data Ingestion | Future: document ingestion for RAG | ⬜ Not yet |
| Vector Database (FAISS, Qdrant) | Future: embedding store | ⬜ Not yet |
| Data Lake Architecture | Future: context source | ⬜ Not yet |
| Tenant Isolation | Future: multi-tenant LLM | ⬜ Not yet |

---

## 4. Gap Analysis Detail

### GAP-01: RAG Pipeline (P1 — Critical)

**Block 7 Reference:**
```
User Query → Intent Classification → RAG Retrieval → Context Assembly → LLM Generation
```

**MT-023 Current:**
```
User Query → Ollama/llama.cpp → Raw Response (no context)
```

**Gap Detail:**
- ❌ No vector database (Qdrant/FAISS/Milvus) configured
- ❌ No embedding model selected or deployed (e.g., sentence-transformers)
- ❌ No document ingestion pipeline (CMDB, logs, runbooks → embeddings)
- ❌ No context assembly logic
- ❌ No intent classification

**Impact:** LLM tanpa RAG hanya bisa menjawab dari training data, tidak bisa mengakses data DCIM aktual. **Ini kritis untuk production.**

**Required Components:**
1. Embedding Model: `sentence-transformers/all-MiniLM-L6-v2` atau `BAAI/bge-small-en-v1.5`
2. Vector DB: Qdrant (recommended) atau FAISS
3. Document Pipeline: CMDB + ES + Runbooks → chunking → embedding → vector store
4. Retrieval Logic: query → embed → similarity search → context assembly
5. Prompt Template: system prompt DCIM + retrieved context + user query

### GAP-02: API Layer (P2 — High)

**Block 7 Reference:** 4 API endpoints

| Endpoint | Purpose | MT-023 Status |
|----------|---------|---------------|
| `POST /analytics/llm/query` | NL query | ❌ Missing |
| `POST /analytics/llm/explain` | Anomaly explanation | ❌ Missing |
| `GET /analytics/llm/context/{ci_id}` | CI context | ❌ Missing |
| `GET /analytics/llm/history` | Query history | ❌ Missing |

**Gap:** No API server wrapping the LLM inference. Ollama provides `/api/generate` but not DCIM-specific endpoints.

**Required:** FastAPI/Flask server with:
- OpenAI-compatible chat completions
- RAG pipeline integration
- CMDB/topology context injection
- Query logging & history

### GAP-03: DCIM Integration (P2 — High)

| Integration Source | Data Type | MT-023 Status |
|-------------------|-----------|---------------|
| CMDB | CI data, relationships, topology | ❌ No connector |
| Elasticsearch | Logs (dcim-logs-*) | ❌ No connector |
| Runbooks | Markdown files | ❌ No parser |
| TimescaleDB | Metrics & trends | ❌ No query logic |
| Historical Incidents | Past resolutions | ❌ No store |

**Impact:** Tanpa integrasi ini, LLM tidak bisa memberikan "contextual answer" yang diminta acceptance criteria Block 7 #14.

### GAP-04: Security (P2 — High)

| Security Control | Block 7 Requirement | MT-023 Status |
|-----------------|---------------------|---------------|
| RBAC | analytics.read, analytics.write, analytics.admin | ❌ |
| Vault integration | API keys, model credentials | ❌ |
| Audit logging | LLM queries logged | ❌ |
| Data classification | No PII in prompts | ❌ Not enforced |

### GAP-05: Deployment Architecture (P3 — Medium)

**MT-023 Current:** Manual deployment on srv-rnd-llm (VM)

**Block 7 Required:**
- Resource: 4 vCPU, 8GB RAM, 20GB storage
- Container: Docker/K8s deployment
- HA: At least 2 instances for production
- Backup: Model artifacts + embeddings backup

**Gap:** No containerized deployment spec, no HA design, no backup strategy for LLM artifacts.

### GAP-06: Monitoring & SLA (P3 — Medium)

| Monitoring | Block 7 | MT-023 |
|-----------|---------|--------|
| Prometheus metrics | `analytics_llm_query_latency_seconds` | ❌ |
| Latency alerting | p99 > 10s triggers warning | ❌ |
| Model accuracy tracking | Gauge metric | ⚠️ Benchmark only |
| Drift detection | Weekly drift score | ❌ |

---

## 5. Strength: What MT-023 Already Delivers

MT-023 memberikan **fondasi yang sangat kuat** yang mempercepat implementasi Block 7:

### 5.1 Model Selection — ✅ COMPLETE

| Model | Use Case | Platform | Score |
|-------|----------|----------|-------|
| **Qwen3-VL-4B** | Best overall (RAG + reasoning) | llama.cpp | 92.34 |
| **Qwen2.5.1-Coder-7B** | Coding & technical analysis | llama.cpp | 91.47 |
| **phi-4** | Deep reasoning & RCA | llama.cpp | 90.69 |
| **qwen2.5-coder:1.5b** | Fast inference, low resource | Ollama | 88.76 |
| **phi4:14b** | High accuracy via Ollama | Ollama | 86.77 |

**Impact untuk Block 7:** Tidak perlu lagi melakukan model selection. Langsung pakai Qwen3-VL-4B untuk RAG service.

### 5.2 Performance Benchmarking — ✅ COMPLETE

| Metric | Target (Block 7) | Achieved (MT-023) | Status |
|--------|------------------|--------------------| ------|
| Latency avg | < 5s | 0.28–1.37s | ✅ Exceeds |
| Tokens/sec | > 15 | 48–178 | ✅ Exceeds |
| TTFT | < 1.5s | 0.02–0.06s | ✅ Exceeds |
| Hallucination | > 0.8 | 1.0 (Qwen) | ✅ Perfect |
| RCA | > 0.75 | 1.0 (Qwen) | ✅ Perfect |
| Tool Use | > 0.75 | 1.0 (Qwen) | ✅ Perfect |
| Domain Knowledge | > 0.8 | 1.0 (Qwen) | ✅ Perfect |

**Impact untuk Block 7:** Model Qwen sudah memenuhi semua SLA threshold Block 7 untuk LLM inference.

### 5.3 Quantization Strategy — ✅ COMPLETE

| Quant | Use Case | MT-023 Recommendation |
|-------|----------|----------------------|
| Q4_K_M | Production (default) | ✅ Recommended |
| Q8_0 | Research/quality-critical | ✅ Available |
| Q2_K | Edge device | ⚠️ Not suitable for reasoning |

**Impact untuk Block 7:** Q4_K_M adalah sweet spot untuk DCIM production deployment.

### 5.4 Platform Strategy — ✅ COMPLETE

| Layer | Platform | Use Case |
|-------|----------|----------|
| Fast API / Real-time | Ollama | Production inference |
| Heavy reasoning / Optimization | llama.cpp | Advanced RAG |
| Multi-GPU | llama.cpp | Throughput scaling |

**Impact untuk Block 7:** Dual-platform strategy memungkinkan deployment fleksibel.

### 5.5 DCIM-Specific Validation — ✅ COMPLETE

| DCIM Capability | MT-023 Benchmark | Score |
|-----------------|-------------------|-------|
| Root Cause Analysis | RCA test cases (4 scenarios) | 1.0 (Qwen) |
| Dependency Chain | Reasoning test (service dependency) | 1.0 (Qwen) |
| Tool Calling | Function calling accuracy | 1.0 (Qwen) |
| Domain Knowledge | PUE, SNMP, UPS, IPMI, Cooling | 1.0 (Qwen) |
| Hallucination Resistance | 5 test cases (fictitious + real) | 1.0 (Qwen) |
| Log Analysis | Long Context (200 lines) | 1.0 (Qwen via llama.cpp) |

---

## 6. Risk Analysis

### 6.1 Risks if Gaps Not Addressed

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM tanpa RAG memberikan jawaban tidak akurat | **P1 Critical** — false alarm, missed incident | High | Implementasi RAG pipeline |
| No audit trail untuk LLM queries | **P2 High** — compliance failure, no forensics | Medium | Add query logging |
| No RBAC on LLM API | **P2 High** — unauthorized access | Medium | Implement FastAPI RBAC |
| No drift monitoring | **P3 Medium** — model accuracy degrades undetected | Low | Add Prometheus metrics |
| Manual deployment only | **P3 Medium** — no HA, no scaling | Medium | Containerize deployment |

### 6.2 Risks from Current MT-023 Implementation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ollama single-GPU only | Throughput limited to 1 GPU | Use llama.cpp for production |
| Benchmark results hardware-dependent | Results may not transfer to prod server | Document hardware requirements |
| No model versioning in Ollama | Difficult to rollback | Implement model registry |
| No authentication on Ollama endpoint | Anyone can query | Add reverse proxy with auth |

---

## 7. Rekomendasi Alignment

### 7.1 Alignment Model

```
┌──────────────────────────────────────────────────────────┐
│                  BLOCK 7 — LLM/RAG Layer                 │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Layer 3: DCIM API + Security                      │  │
│  │  FastAPI endpoints, RBAC, audit logging, Vault     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Layer 2: RAG Pipeline                             │  │
│  │  Vector DB, Embedding, Context Assembly, Retrieval │  │
│  │  Sources: CMDB, ES, Runbooks, TSDB, Incidents      │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Layer 1: Inference Platform                       │  │
│  │  ✅ MT-023 — Model Selection, Benchmark, Quant     │  │
│  │  ✅ Qwen3-VL-4B via llama.cpp (Q4_K_M)            │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

**MT-023 = Layer 1 ✅ (COMPLETE)**
**Block 7 needs = Layer 1 + 2 + 3 (MT-023 covers ~33%)**

### 7.2 Recommended Next Steps

| Priority | Task | Estimated Effort | Depends On |
|----------|------|-------------------|------------|
| P1 | Implement RAG Pipeline (vector DB + embedding + retrieval) | 2-3 hari | MT-023 ✅ |
| P1 | Build DCIM API Layer (FastAPI + 4 endpoints) | 1-2 hari | RAG Pipeline |
| P1 | CMDB Integration (connector + context injection) | 1 hari | CMDB Block 4 |
| P2 | Elasticsearch Log Connector | 0.5 hari | ES available |
| P2 | Runbook Parser & Ingestion | 0.5 hari | Wiki markdown |
| P2 | Security (RBAC + Vault + audit logging) | 1 hari | Auth service |
| P3 | Monitoring (Prometheus metrics + Grafana) | 0.5 hari | Prometheus |
| P3 | Deployment (Docker Compose + HA spec) | 1 hari | Container setup |
| P3 | Model Drift Detection | 0.5 hari | Prometheus |
| P4 | Model Fine-tuning Pipeline | 2-3 hari | Training data |

---

## 8. Action Items

### Immediate (P1)

- [ ] **Select Embedding Model**: `sentence-transformers/all-MiniLM-L6-v2` or `BAAI/bge-small-en-v1.5`
- [ ] **Deploy Vector DB**: Qdrant (port 6333) atau FAISS local
- [ ] **Build Document Pipeline**: CMDB → chunking → embedding → vector store
- [ ] **Build Context Assembly**: retrieved context + system prompt DCIM
- [ ] **Build FastAPI Server**: 4 endpoints dari Block 7 Section 9.4
- [ ] **Connect to CMDB**: Use existing PostgreSQL connection

### Short-term (P2)

- [ ] **ES Log Connector**: Query `dcim-logs-*` for recent events
- [ ] **Runbook Parser**: Ingest markdown runbooks into vector DB
- [ ] **RBAC Implementation**: FastAPI middleware + role checking
- [ ] **Vault Integration**: Store API keys, model credentials
- [ ] **Audit Logging**: Log all LLM queries with timestamp, user, response

### Medium-term (P3)

- [ ] **Docker Compose**: LLM service + Qdrant + embedding model
- [ ] **Prometheus Metrics**: Latency, throughput, accuracy gauge
- [ ] **Grafana Dashboard**: LLM service health view
- [ ] **Model Drift Detection**: Weekly accuracy comparison
- [ ] **HA Design**: 2x LLM instances behind load balancer

### Long-term (P4)

- [ ] **Fine-tuning Pipeline**: LoRA/QLoRA on DCIM-specific data
- [ ] **Multi-tenant Support**: Per-team model/context isolation
- [ ] **A/B Testing**: Model comparison framework
- [ ] **Cost Optimization**: Token usage tracking, model downsizing

---

## Referensi

- Block 7 Reference Design: `~/dcim-wiki/reference-designs/block7-analytics-ai-engine.md` (Section 9: LLM/RAG)
- MT-023 FINAL: AFFiNE doc `LvM1h6BU02`
- MT-023 MERGED: AFFiNE doc `YAElpqZQg_`
- MT-023 AI Model Specs: AFFiNE doc `WKQx2rBIor`
- FIT041 UC24-25: LLM/RAG Layer Use Cases

---

> **Status:** Analysis Complete
> **Date:** 2026-07-03
> **Analyst:** Hermes DCIM Orchestrator
> **Next Step:** Implement Layer 2 (RAG Pipeline) → Start P1 Action Items
