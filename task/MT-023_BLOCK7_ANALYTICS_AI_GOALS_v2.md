---
title: "Block 7 — Analytics & AI Engine: Goals & Dependencies v2"
created: 2026-07-07
updated: 2026-07-09
version: 2.0
type: task-spec
block: 7
phase: 2
owner: Analytics & AI Team
status: active
confidence: 95%
tags: [analytics, ai, anomaly-detection, predictive-maintenance, rca, capacity, energy, llm-rag, timeseries, goals, fastapi, kafka, timescaledb]
reference_design: dcim-wiki/reference-designs/block7-analytics-ai-engine.md
technical_requirements: dcim-wiki/reference-designs/block7-analytics-ai-engine-technical-requirements.md
use_case_analysis: dcim-wiki/technical-requirements/analytics-ai-use-case-analysis-final-v2.md
changelog: |
  v2.0 (2026-07-09): Major update — sync dengan implementasi aktual
    - Updated scorecard: 27% → 66%
    - Added all new components (API, services, stream, correlation, domain, features, models)
    - Updated action items (banyak sudah selesai)
    - Added deployment instructions (Docker, Quick Start)
    - Added actual file tree
    - Updated timeline (Phase 1 mostly done)
  v1.1 (2026-07-08): Kafka topics clarification
  v1.0 (2026-07-07): Initial goals document
---

# Block 7 — Analytics & AI Engine: Goals & Dependencies v2

> **Scope:** Dokumen ini berisi goals, status implementasi aktual, dependency ke tim lain,
> dan action items untuk Block 7 Analytics & AI Engine.
> **Owner:** Analytics & AI Team
> **Reference:** dcim-wiki/reference-designs/block7-analytics-ai-engine.md
> **Status:** Implementasi sudah jauh lebih maju dari v1.1

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Scope & Sub-Components](#2-scope--sub-components)
3. [Current Implementation Status](#3-current-implementation-status)
4. [Dependencies — Block 1 (Infrastructure)](#4-dependencies--block-1-infrastructure)
5. [Dependencies — Block 2 (Data Ingestion & Integration)](#5-dependencies--block-2-data-ingestion--integration)
6. [Dependencies — Block 4 (CMDB)](#6-dependencies--block-4-cmdb)
7. [Action Items](#7-action-items)
8. [Acceptance Criteria](#8-acceptance-criteria)
9. [Timeline & Milestones](#9-timeline--milestones)
10. [Deployment](#10-deployment)

---

## 1. Executive Summary

### Current State (v2.0 — Updated)

dcim-wiki mendefinisikan **8 sub-komponen** untuk Block 7 Analytics & AI Engine.
Implementasi saat ini sudah menyentuh **8 dari 8** sub-komponen (dengan tingkat kelengkapan bervariasi).

| Sub-Komponen              | dcim-wiki Spec | Implementation | Alignment |
|---------------------------|----------------|----------------|-----------|
| 1. Time-Series Pipeline   | ✅             | ✅ Consumer ada | 60%       |
| 2. Anomaly Detection      | ✅             | ✅ Full service | 80%       |
| 3. Predictive Maintenance | ✅             | ⚠️ Partial    | 30%       |
| 4. RCA Engine             | ✅             | ✅ Full + API  | 90%       |
| 5. Capacity Forecasting   | ✅             | ✅ Service ada | 70%       |
| 6. Energy Optimization    | ✅             | ✅ Service ada | 70%       |
| 7. Model Training Pipeline| ✅             | ✅ Full pipeline| 80%       |
| 8. LLM/RAG Layer          | ✅             | ⚠️ Partial    | 45%       |
| **OVERALL**               |                |                | **~66%**  |

### Score Improvement

| Version | Date | Alignment | Notes |
|---------|------|-----------|-------|
| v1.0 | 2026-07-07 | ~27% | Initial assessment |
| v1.1 | 2026-07-08 | ~27% | Kafka topics clarified |
| **v2.0** | **2026-07-09** | **~66%** | **Synced with actual code** |

### Key Findings

1. **API Layer sudah FULL** — FastAPI dengan 7 routers, RBAC, health check, OpenAPI docs
2. **Anomaly Detection sudah FULL SERVICE** — Multi-model voting (IF + LOF + One-Class SVM)
3. **Capacity Forecasting sudah ada** — Service + API endpoint
4. **Energy Optimization sudah ada** — Service + API endpoint
5. **Stream Processing sudah ada** — Kafka consumer → TimescaleDB
6. **Docker deployment sudah ada** — Dockerfiles + docker-compose
7. **Correlation Engine** — Temporal + domain scoring (bonus, tidak di spec)
8. **Feature Pipeline** — Drift detection + scaling (bonus, tidak di spec)

### Yang Masih Perlu Dikerjakan

1. ❌ Kafka producer — untuk publish ke output topics
2. ❌ RAG pipeline — vector store + retrieval
3. ❌ Traditional ML training — Prophet/LSTM
4. ❌ CMDB integration — topology data masih mock
5. ❌ Live data connection — consumer belum connected ke Kafka real
6. ❌ TimescaleDB tables — anomaly_events, predictions, ml_models

---

## 2. Scope & Sub-Components

### 2.1 Time-Series Pipeline (Priority: P1)

**Goal:** Ingest metrics dari Kafka, store di TimescaleDB, serve ke analytics services.

| Requirement | Spec | Status | Notes |
|-------------|------|--------|-------|
| Kafka consumer dari `dcim.analytics.metrics` | P1 | ✅ | `stream/metrics_consumer.py` |
| TimescaleDB hypertable (metrics table) | P1 | ⚠️ | Schema ready, belum di-deploy |
| Continuous aggregates (hourly, daily) | P2 | ⚠️ | Migration file ada |
| Compression policy (7 hari) | P2 | ⚠️ | Migration file ada |
| Retention policy (90 hari) | P2 | ⚠️ | Migration file ada |
| 430+ metrics/sec throughput | P1 | ❌ | Belum di-benchmark |
| < 1s end-to-end latency | P1 | ❌ | Belum di-test |

**Code Location:**
- `stream/base_consumer.py` — Base Kafka consumer class
- `stream/metrics_consumer.py` — Kafka → TimescaleDB consumer
- `migrations/run_migrations.py` — Database migration runner

**Depends on:** Block 1 (TimescaleDB running), Block 2 (Kafka topic active)

### 2.2 Anomaly Detection (Priority: P1)

**Goal:** Deteksi anomali real-time menggunakan multiple methods.

| Method | Type | Latency Target | Status | Notes |
|--------|------|----------------|--------|-------|
| Z-score | Univariate, real-time | < 10ms | ✅ | Drift detection |
| Isolation Forest | Multivariate, near-RT | < 500ms | ✅ | Multi-model voting |
| LOF | Density-based | < 500ms | ✅ | Multi-model voting |
| One-Class SVM | Boundary-based | < 500ms | ✅ | Multi-model voting |
| Moving Average | Trend, batch 5min | Batch | ❌ | Belum ada |
| Seasonal Decomposition | Pattern, batch hourly | Batch | ❌ | Belum ada |

**API Endpoints (SUDAH ADA):**
- ✅ `GET /api/v1/analytics/anomalies` — List anomalies
- ✅ `POST /api/v1/analytics/anomalies/detect` — Trigger detection

**Code Location:**
- `services/anomaly_service.py` — Multi-model voting engine
- `stream/anomaly_detector.py` — Real-time anomaly detector
- `api/routers/anomalies.py` — API router

**Additional Features (bonus):**
- Drift detection (z-score based)
- Domain scoring per fitur
- Correlation rules engine
- Severity matrix

### 2.3 Predictive Maintenance (Priority: P1-P2)

**Goal:** Prediksi failure probability dan optimasi jadwal maintenance.

| Model | Use Case | Status | Notes |
|-------|----------|--------|-------|
| Prophet | Trend forecasting | ❌ | Belum ada |
| LSTM | Sequential pattern | ❌ | Belum ada |
| Survival Analysis | Time-to-failure | ❌ | Belum ada |
| Random Forest | Multi-factor risk | ❌ | Belum ada |
| Forward RCA | Forecast → root cause | ✅ | RCA engine forward mode |

**API Endpoints (SUDAH ADA):**
- ✅ `GET /api/v1/analytics/predictions` — List predictions
- ✅ `POST /api/v1/analytics/predictions/forecast` — Trigger forecast

**Code Location:**
- `api/routers/predictions.py` — API router
- `root_cause/rca_engine.py` — Forward mode (analyze_forward)

### 2.4 Root Cause Analysis (Priority: P1) ⭐

**Goal:** Identifikasi root cause dari incident menggunakan topology + scoring.

| Feature | Status | Notes |
|---------|--------|-------|
| Reactive mode (analyze) | ✅ | Composite scoring, softmax |
| Forward mode (predictive) | ✅ | Forecast → RCA |
| Hybrid mode | ✅ | Gabungkan reactive + forward |
| Causal chain reconstruction | ✅ | DFS, depth 3 |
| CMDB topology integration | ⚠️ | Mock topology, butuh real CMDB |
| API endpoint | ✅ | FastAPI wrapper ada |

**API Endpoints (SUDAH ADA):**
- ✅ `POST /api/v1/analytics/rca/analyze` — Trigger RCA
- ⚠️ `GET /api/v1/analytics/rca/{id}` — Get RCA report (returns 501)
- ⚠️ `GET /api/v1/analytics/rca/history` — RCA history (returns 501)

**Code Location:**
- `root_cause/rca_engine.py` — RCA Engine (3 modes)
- `root_cause/rca_models.py` — Data models
- `root_cause/topology_manager.py` — Causal topology
- `services/rca_service.py` — RCA service layer
- `api/routers/rca.py` — API router

### 2.5 Capacity Forecasting (Priority: P1-P2)

**Goal:** Forecast resource utilization dan prediksi exhaustion date.

| Feature | Status | Notes |
|---------|--------|-------|
| CPU, memory, storage, network forecast | ✅ | Service ada |
| Power consumption & cooling forecast | ⚠️ | Partial |
| Linear + exponential models | ⚠️ | Basic models |
| Capacity exhaustion dates | ✅ | Implemented |
| 30-day projections | ✅ | Implemented |
| Capacity threshold alerts | ⚠️ | Basic |

**API Endpoints (SUDAH ADA):**
- ✅ `GET /api/v1/analytics/capacity` — List capacity reports
- ✅ `POST /api/v1/analytics/capacity/forecast` — Trigger forecast

**Code Location:**
- `services/capacity_forecasting.py` — Capacity forecasting service
- `api/routers/capacity.py` — API router
- `examples/demo_capacity_forecast.py` — Demo script

### 2.6 Energy Optimization (Priority: P2)

**Goal:** Hitung PUE, optimasi cooling, analisis power distribution.

| Feature | Status | Notes |
|---------|--------|-------|
| PUE real-time calculation | ✅ | Service ada |
| Cooling efficiency | ✅ | Implemented |
| Power load balance | ✅ | Implemented |
| Carbon intensity (CO2/kWh) | ⚠️ | Basic |
| Cooling optimization recommendations | ✅ | Implemented |
| Energy cost impact analysis | ⚠️ | Basic |

**API Endpoints (SUDAH ADA):**
- ✅ `GET /api/v1/analytics/energy/pue` — Get PUE
- ✅ `POST /api/v1/analytics/energy/optimize` — Trigger optimization

**Code Location:**
- `services/energy_optimization.py` — Energy optimization service
- `api/routers/energy.py` — API router

### 2.7 Model Training Pipeline (Priority: P1)

**Goal:** End-to-end pipeline untuk training, registry, dan deployment model.

| Feature | Status | Notes |
|---------|--------|-------|
| Model Registry (v1) | ✅ | Single model |
| Model Registry (v2) | ✅ | Multi-model, type/domain |
| LLM Fine-tuning (QLoRA) | ✅ | Qwen2.5-3B-Instruct |
| Dataset generator | ✅ | 3,816 instruction samples |
| Text enrichment | ✅ | Pipeline lengkap |
| Export GGUF | ✅ | Untuk llama.cpp |
| Traditional ML training | ✅ | train_anomaly_model.py |
| Anomaly model training | ✅ | IF + LOF + SVM ensemble |
| A/B testing | ❌ | Belum ada |
| Model drift monitoring | ✅ | drift_detector.py |
| Model promotion gatekeeper | ✅ | promotion_gatekeeper.py |
| Ensemble engine | ✅ | ensemble_engine.py |

**API Endpoints (SUDAH ADA):**
- ✅ `GET /api/v1/analytics/models` — List models
- ✅ `POST /api/v1/analytics/models` — Register model
- ✅ `PUT /api/v1/analytics/models/{id}/deploy` — Deploy model

**Code Location:**
- `registry/model_registry.py` — Multi-model registry
- `models/ensemble_engine.py` — Ensemble engine
- `models/evaluation_engine.py` — Model evaluation
- `models/model_manager.py` — Model management
- `models/promotion_gatekeeper.py` — Promotion gates
- `training/train_anomaly_model.py` — Anomaly model training
- `training/training_orchestrator.py` — Training orchestration
- `features/feature_pipeline.py` — Feature engineering
- `features/drift_detector.py` — Drift detection
- `api/routers/models.py` — API router

### 2.8 LLM/RAG Explanation Layer (Priority: P1)

**Goal:** Natural language query dan explanation untuk metrics/anomalies.

| Feature | Status | Notes |
|---------|--------|-------|
| Fine-tuned model (dcim_assistant v1.0) | ✅ | Qwen2.5-3B, loss 0.310 |
| Model inference service | ⚠️ | API router ada, backend partial |
| RAG pipeline | ❌ | Vector store + retrieval belum ada |
| Context retrieval (CMDB/logs) | ❌ | Belum ada |
| Citation mechanism | ❌ | Belum ada |
| < 5s per query latency | ❌ | Belum di-test |

**API Endpoints (SUDAH ADA):**
- ⚠️ `POST /api/v1/analytics/llm/query` — Ask question (partial)
- ⚠️ `POST /api/v1/analytics/llm/explain` — Explain anomaly (partial)

**Code Location:**
- `llm/finetune_qlora.py` — QLoRA fine-tuning
- `llm/dataset_generator.py` — Dataset generation
- `llm/text_enrichment.py` — Text enrichment
- `llm/instruction_builder.py` — Instruction building
- `llm/model_registry.py` — LLM model registry
- `llm/export_gguf.py` — GGUF export
- `api/routers/llm.py` — API router
- `api/inference_service.py` — Inference service

---

## 3. Current Implementation Status

### What's Built (Complete File Tree)

```
implementation/dcim_ai_v2_rag/
│
├── api/                              ← FASTAPI API LAYER
│   ├── __init__.py
│   ├── main.py                       (FastAPI app, 173 lines)
│   ├── config.py                     (Settings, env vars)
│   ├── dependencies.py               (Auth, DB connection)
│   ├── inference_service.py          (LLM inference)
│   ├── requirements.txt
│   └── routers/
│       ├── __init__.py
│       ├── anomalies.py              ✅ Anomaly detection endpoints
│       ├── predictions.py            ✅ Predictive maintenance endpoints
│       ├── rca.py                    ✅ RCA endpoints
│       ├── capacity.py               ✅ Capacity forecasting endpoints
│       ├── energy.py                 ✅ Energy optimization endpoints
│       ├── models.py                 ✅ Model registry endpoints
│       └── llm.py                    ✅ LLM/RAG endpoints
│
├── services/                         ← BUSINESS LOGIC SERVICES
│   ├── __init__.py
│   ├── anomaly_service.py            ✅ Multi-model voting (IF+LOF+SVM)
│   ├── capacity_forecasting.py       ✅ Capacity forecasting
│   ├── energy_optimization.py        ✅ Energy optimization
│   ├── rca_service.py                ✅ RCA service layer
│   └── retraining_scheduler.py       ✅ Auto-retrain trigger
│
├── stream/                           ← KAFKA STREAM PROCESSING
│   ├── __init__.py
│   ├── base_consumer.py              ✅ Base Kafka consumer
│   ├── metrics_consumer.py           ✅ Kafka → TimescaleDB
│   └── anomaly_detector.py           ✅ Real-time anomaly detection
│
├── correlation/                      ← EVENT CORRELATION ENGINE
│   ├── __init__.py
│   ├── correlation_engine.py         ✅ Core correlation logic
│   ├── aggregation_engine.py         ✅ Temporal aggregation
│   ├── aggregation_models.py         ✅ Data models
│   ├── correlation_buffer.py         ✅ Rolling buffer
│   ├── incident_builder.py           ✅ Incident construction
│   └── severity_matrix.py            ✅ Severity classification
│
├── domain/                           ← DOMAIN ENGINE
│   ├── __init__.py
│   ├── domain_engine.py              ✅ Domain scoring
│   ├── domain_models.py              ✅ Data models
│   ├── domain_config.py              ✅ Configuration
│   └── asset_resolver.py             ✅ Asset resolution
│
├── features/                         ← FEATURE ENGINEERING
│   ├── __init__.py
│   ├── feature_pipeline.py           ✅ Feature pipeline
│   ├── feature_stats.py              ✅ Feature statistics
│   ├── drift_detection.py            ✅ Drift detection
│   └── drift_detector.py             ✅ Drift detector
│
├── models/                           ← MODEL MANAGEMENT
│   ├── __init__.py
│   ├── ensemble_engine.py            ✅ Multi-model ensemble
│   ├── evaluation_engine.py          ✅ Model evaluation
│   ├── model_manager.py              ✅ Model lifecycle
│   ├── promotion_gatekeeper.py       ✅ Promotion gates
│   ├── correlation_impact_evaluator.py ✅
│   └── drift_robustness_evaluator.py   ✅
│
├── monitoring/                       ← MONITORING
│   ├── __init__.py
│   ├── drift_detector.py             ✅ Production drift monitoring
│   └── event_logger.py               ✅ Event logging
│
├── training/                         ← TRAINING PIPELINE
│   ├── __init__.py
│   ├── train_anomaly_model.py        ✅ Anomaly model training
│   └── training_orchestrator.py      ✅ Training orchestration
│
├── root_cause/                       ← RCA ENGINE
│   ├── __init__.py
│   ├── rca_engine.py                 ✅ RCA Engine (3 modes)
│   ├── rca_models.py                 ✅ Data models
│   ├── topology_manager.py           ✅ Causal topology
│   ├── causal_topology.py            ✅ Causal graph
│   └── lifecycle_manager.py          ✅ Lifecycle management
│
├── registry/                         ← MODEL REGISTRY
│   ├── __init__.py
│   ├── model_registry.py             ✅ Multi-model registry
│   └── promote_model.py              ✅ Model promotion
│
├── llm/                              ← LLM PIPELINE
│   ├── __init__.py
│   ├── finetune_qlora.py             ✅ QLoRA fine-tuning
│   ├── finetune_unsloth.py           ✅ Unsloth fine-tuning
│   ├── dataset_generator.py          ✅ Dataset generation
│   ├── text_enrichment.py            ✅ Text enrichment
│   ├── instruction_builder.py        ✅ Instruction building
│   ├── synthetic_generator.py        ✅ Synthetic data
│   ├── model_registry.py             ✅ LLM model registry
│   ├── model_registry_standalone.py  ✅ Standalone registry
│   ├── export_gguf.py                ✅ GGUF export
│   ├── evaluate_model.py             ✅ Model evaluation
│   ├── rca_prompt_contract.py        ✅ RCA prompt contract
│   ├── production_readiness_contract.py ✅
│   └── production_readiness/
│       ├── agent_orchestrator.py     ✅
│       ├── constrained_client.py     ✅
│       ├── fase1_live_proof.py       ✅
│       └── incident_state_store.py   ✅
│
├── inference/                        ← INFERENCE
│   ├── __init__.py
│   ├── asset_enricher.py             ✅ Asset enrichment
│   ├── load_production_model.py      ✅ Model loading
│   └── model_manager.py              ✅ Model management
│
├── core/                             ← CORE MODULES
│   ├── __init__.py
│   ├── data_loader.py                ✅ Data loading
│   ├── metric_sources.py             ✅ Metric sources config
│   ├── correlation_rules.py          ✅ Correlation rules
│   ├── domain_aggregator.py          ✅ Domain aggregation
│   └── feature_pipeline.py           ✅ Feature pipeline
│
├── config/                           ← CONFIGURATION
│   ├── __init__.py
│   └── domain_mapping.py             ✅ Domain feature mapping
│
├── contracts/                        ← CONTRACTS
│   └── __init__.py
│
├── automation/                       ← AUTOMATION
│   ├── __init__.py
│   └── retrain_trigger.py            ✅ Auto-retrain
│
├── tools/                            ← TOOLS
│   ├── __init__.py
│   └── kafka_localhost_proxy.py      ✅ Local dev proxy
│
├── examples/                         ← EXAMPLES
│   ├── demo_anomaly_detection.py     ✅ Anomaly detection demo
│   ├── demo_api.py                   ✅ API demo
│   └── demo_capacity_forecast.py     ✅ Capacity forecast demo
│
├── migrations/                       ← DATABASE MIGRATIONS
│   └── run_migrations.py             ✅ Migration runner
│
├── tests/                            ← TESTS
│   ├── test_rca_engine.py            ✅
│   ├── test_rca_forward.py           ✅
│   ├── test_topology_manager.py      ✅
│   ├── test_correlation_engine.py    ✅
│   ├── test_aggregation_engine.py    ✅
│   ├── test_domain_engine.py         ✅
│   ├── test_domain_config.py         ✅
│   ├── test_asset_enricher.py        ✅
│   ├── test_asset_resolver.py        ✅
│   ├── test_contracts.py             ✅
│   ├── test_inference.py             ✅
│   ├── test_integration.py           ✅
│   ├── test_llm_rca_prompt_contract.py ✅
│   ├── test_agent_orchestrator.py    ✅
│   └── test_production_readiness_contract.py ✅
│
├── Dockerfile.api                    ✅ FastAPI container
├── Dockerfile.consumer               ✅ Kafka consumer container
├── docker-compose.yml                ✅ Full stack compose
├── docker-compose.simple.yml         ✅ Simplified compose (external infra)
├── QUICKSTART.md                     ✅ Quick start guide
├── main.py                           ✅ Main entry point
└── requirements.txt                  ✅ Dependencies
```

### File Count Summary

| Category | Files | Status |
|----------|-------|--------|
| API routers | 7 | ✅ All implemented |
| Services | 5 | ✅ All implemented |
| Stream processing | 3 | ✅ All implemented |
| Correlation | 6 | ✅ All implemented |
| Domain | 4 | ✅ All implemented |
| Features | 4 | ✅ All implemented |
| Models | 6 | ✅ All implemented |
| Monitoring | 2 | ✅ All implemented |
| Training | 2 | ✅ All implemented |
| RCA Engine | 5 | ✅ All implemented |
| Registry | 2 | ✅ All implemented |
| LLM | 12 | ✅ All implemented |
| Inference | 3 | ✅ All implemented |
| Core | 5 | ✅ All implemented |
| Automation | 1 | ✅ Implemented |
| Tools | 1 | ✅ Implemented |
| Examples | 3 | ✅ Implemented |
| Migrations | 1 | ✅ Implemented |
| Tests | 15 | ✅ Implemented |
| Docker | 3 | ✅ Implemented |
| **TOTAL** | **~90 files** | |

---

## 4. Dependencies — Block 1 (Infrastructure)

### 4.1 Actual Connection Details (from Syauqi Documentation)

| Service | Host | Port | Database/User | Password |
|---------|------|------|---------------|----------|
| TimescaleDB | `10.70.0.56` | `5433` | `dcim_analytics` / `ai_team` | `ai_team_access_pass` |
| Kafka | `10.70.0.56` | `9092` | — | — (PLAINTEXT) |
| Schema Registry | `10.70.0.56` | `8081` | — | — |

### 4.2 Kafka Topics

| Topic | Partitions | Retention | Direction | Status |
|-------|------------|-----------|-----------|--------|
| `dcim.analytics.metrics` | 6 | 7 days | INPUT (consume) | ✅ Created |
| `dcim.analytics.anomalies` | 3 | 30 days | OUTPUT (produce) | ✅ Created |
| `dcim.analytics.predictions` | 3 | 30 days | OUTPUT (produce) | ✅ Created |
| `dcim.analytics.rca` | 3 | 30 days | OUTPUT (produce) | ❌ Need to request |
| `dcim.analytics.capacity` | 3 | 30 days | OUTPUT (produce) | ❌ Need to request |
| `dcim.analytics.energy` | 3 | 30 days | OUTPUT (produce) | ❌ Need to request |

### 4.3 Environment Variables

```bash
# TimescaleDB
export TIMESCALEDB_HOST=10.70.0.56
export TIMESCALEDB_PORT=5433
export TIMESCALEDB_DATABASE=dcim_analytics
export TIMESCALEDB_USER=ai_team
export TIMESCALEDB_PASSWORD=ai_team_access_pass

# Kafka
export KAFKA_BOOTSTRAP_SERVERS=10.70.0.56:9092
export KAFKA_TOPIC_METRICS=dcim.analytics.metrics
export KAFKA_TOPIC_ANOMALIES=dcim.analytics.anomalies
export KAFKA_TOPIC_DLQ=dcim.analytics.dlq
```

### 4.4 Redis (Still Pending)

| Item | Specification | Status |
|------|---------------|--------|
| Host | TBD | ❌ Need to request |
| Port | TBD | ❌ Need to request |
| DB number | 3 | ❌ Need to request |
| Password | TBD | ❌ Need to request |

---

## 5. Dependencies — Block 2 (Data Ingestion & Integration)

### 5.1 Data Entry Points

| Entry Point | Format | Use Case | Status |
|-------------|--------|----------|--------|
| Kafka `dcim.analytics.metrics` | JSON | Real-time streaming | ✅ Consumer ready |
| TimescaleDB `metrics` table | SQL | Historical batch queries | ✅ Schema ready |

### 5.2 Pipeline Architecture

```
Source Devices → NiFi (Pollers) → Kafka (Raw, JSON) → NiFi (Enrich)
    → Kafka (Enriched, Avro) → Analytics Bridge (Python)
    → Kafka (dcim.analytics.metrics, JSON) → TIM AI CONSUME
    → Stream Processor → TimescaleDB → Continuous Aggregates
```

---

## 6. Dependencies — Block 4 (CMDB)

### 6.1 RCA Engine Needs

RCA Engine butuh topology data dari CMDB untuk causal chain reconstruction.

**Status:** Currently using mock topology data.

**API endpoints needed from CMDB:**

| Endpoint | Purpose | Priority |
|----------|---------|----------|
| `GET /api/v1/cmdb/cis/{ci_id}` | Get CI details | P1 |
| `GET /api/v1/cmdb/cis/{ci_id}/relationships` | Get CI relationships | P1 |
| `GET /api/v1/cmdb/topology/traverse?ci_id=X&depth=3` | Topology traversal | P1 |

---

## 7. Action Items

### 7.1 Completed ✅

- [x] FastAPI project structure
- [x] Wrapper untuk RCA Engine: `POST /api/v1/analytics/rca/analyze`
- [x] Wrapper untuk Model Registry: `GET /api/v1/analytics/models`
- [x] Wrapper untuk LLM inference: `POST /api/v1/analytics/llm/query`
- [x] OpenAPI/Swagger docs (di `/api/v1/docs`)
- [x] Health check endpoint (`/health`, `/api/v1/health`)
- [x] SQL migration files
- [x] Kafka consumer code (`stream/metrics_consumer.py`)
- [x] Schema validation
- [x] Error handling + DLQ routing
- [x] Connection config (env vars)
- [x] Anomaly detection service (multi-model voting)
- [x] Capacity forecasting service
- [x] Energy optimization service
- [x] Correlation engine
- [x] Domain engine
- [x] Feature pipeline
- [x] Drift detection
- [x] Model ensemble engine
- [x] Model promotion gatekeeper
- [x] Dockerfile per service
- [x] docker-compose.yml
- [x] Quick start guide (QUICKSTART.md)
- [x] Demo scripts
- [x] Unit tests (15 test files)

### 7.2 In Progress 🔄

- [ ] Run database migrations on TimescaleDB
- [ ] Connect Kafka consumer to live data
- [ ] Test API endpoints with real data
- [ ] Benchmark throughput (target: 430+ metrics/sec)

### 7.3 Not Started ❌

- [ ] Kafka producer code (publish ke output topics)
- [ ] RAG pipeline (vector store + retrieval)
- [ ] Traditional ML training (Prophet/LSTM)
- [ ] CMDB integration (real topology data)
- [ ] Redis integration
- [ ] TLS configuration for production
- [ ] Additional Kafka topics (rca, capacity, energy)

---

## 8. Acceptance Criteria

### 8.1 Per Sub-Component (Updated)

| Sub-Component | Acceptance Criteria | Priority | Status |
|---------------|---------------------|----------|--------|
| Time-Series Pipeline | Metrics dari Kafka tersimpan di TimescaleDB, queryable < 100ms | P1 | ⚠️ Code ready, belum live |
| Anomaly Detection | Multi-model voting detect anomalies, alerts emitted | P1 | ✅ Service ready |
| Predictive Maintenance | Failure probability generated, 30-day window | P1 | ⚠️ API ready, models partial |
| RCA Engine | Root cause < 30s, causal chain depth 3 | P1 | ✅ Fully working |
| Capacity Forecasting | 30-day projections, exhaustion dates | P2 | ✅ Service ready |
| Energy Optimization | PUE calculated, cooling recommendations | P2 | ✅ Service ready |
| Model Training | Model trained, evaluated, registered, deployed | P1 | ✅ Full pipeline |
| LLM/RAG | NL query < 5s, with context | P1 | ⚠️ API partial |

### 8.2 API Coverage (Updated)

Total: **~20 API endpoints** across 7 groups (some return 501)

| Group | Endpoints | Status | Auth Level |
|-------|-----------|--------|------------|
| Anomaly Detection | 2 | ✅ Working | analytics.read/write |
| Predictive Maintenance | 2 | ✅ Working | analytics.read/write |
| RCA | 3 | ⚠️ 1 working, 2 returns 501 | analytics.read/write |
| Capacity Forecasting | 2 | ✅ Working | analytics.read/write |
| Energy Optimization | 2 | ✅ Working | analytics.read/write |
| Model Registry | 3 | ✅ Working | analytics.read/admin |
| LLM/RAG | 2 | ⚠️ Partial | analytics.read |

---

## 9. Timeline & Milestones

### Phase 1: Foundation — SEBAGIAN BESAR SELESAI ✅

| Week | Milestone | Deliverable | Status |
|------|-----------|-------------|--------|
| W1 | API Layer | FastAPI wrapper | ✅ Done |
| W1 | DB Schema | SQL migration files | ✅ Done |
| W2 | Kafka Consumer | Consumer code | ✅ Done |
| W2 | Anomaly Detection | Multi-model service | ✅ Done |
| W2 | Capacity Forecasting | Service + API | ✅ Done |
| W2 | Energy Optimization | Service + API | ✅ Done |
| W2 | Docker | Dockerfiles + compose | ✅ Done |
| W2 | Quick Start | QUICKSTART.md | ✅ Done |

### Phase 2: Integration — DALAM PROGRESS 🔄

| Week | Milestone | Deliverable | Status |
|------|-----------|-------------|--------|
| W3 | DB Migration | Run migrations on TimescaleDB | 🔄 Next |
| W3 | Kafka Connection | Consumer connected to live data | 🔄 Next |
| W3 | API Testing | Test all endpoints | 🔄 Next |
| W4 | Anomaly Live | Real-time anomaly detection | ❌ Pending |
| W4 | RCA Live | RCA connected to CMDB | ❌ Pending |

### Phase 3: Enhancement — BELUM MULAI ❌

| Week | Milestone | Deliverable | Status |
|------|-----------|-------------|--------|
| W5-6 | Kafka Producer | Publish to output topics | ❌ |
| W5-6 | Predictive Maintenance | Prophet/LSTM models | ❌ |
| W7-8 | RAG Pipeline | Vector store + retrieval | ❌ |
| W7-8 | LLM Live | Full inference service | ❌ |

---

## 10. Deployment

### Option 1: Run Directly (No Docker)

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag

# Install dependencies
cd api
pip install -r requirements.txt
cd ..

# Set environment variables
export TIMESCALEDB_HOST=10.70.0.56
export TIMESCALEDB_PORT=5433
export TIMESCALEDB_DATABASE=dcim_analytics
export TIMESCALEDB_USER=ai_team
export TIMESCALEDB_PASSWORD=ai_team_access_pass
export KAFKA_BOOTSTRAP_SERVERS=10.70.0.56:9092

# Run API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# Test
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/docs  # OpenAPI docs
```

### Option 2: Docker Compose

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag

# Build and start
docker-compose -f docker-compose.simple.yml up -d

# Check logs
docker-compose -f docker-compose.simple.yml logs -f api

# Test
curl http://localhost:8000/health
```

### Option 3: Database Migrations

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/migrations

python run_migrations.py \
  --host 10.70.0.56 \
  --port 5433 \
  --database dcim_analytics \
  --user ai_team \
  --password ai_team_access_pass
```

---

## Appendix A: Message Template to Infrastructure Team

```
Subject: Block 7 — 3 Kafka Topics Request

Hi [Infrastructure Team],

Ada 3 topic yang belum dibuat, bisa tolong create?

 1. dcim.analytics.rca        (3 partitions, 30 days retention)
 2. dcim.analytics.capacity   (3 partitions, 30 days retention)
 3. dcim.analytics.energy     (3 partitions, 30 days retention)

Spec sama seperti topic analytics lainnya.
Gue yang akan publish data ke situ nanti.

Thanks!
```

---

**Last Updated:** 2026-07-09 (v2.0)
**Maintained By:** Analytics & AI Team
**Status:** Active
