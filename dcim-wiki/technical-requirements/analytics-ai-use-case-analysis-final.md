---
title: "Use Case Analysis — Analytics & AI Engine (Block 7) (Final)"
created: 2026-06-25
updated: 2026-06-25
type: use-case-analysis
block: 7
phase: 1
status: final
confidence: high
tags: [use-case, analytics, ai, anomaly, predictive, rca, capacity, energy, llm-rag, timeseries, model-training, merged]
sources:
  - IF-Technical_Requirements_Analytics_AI_Engine-FIT041-20260119.md
  - block7-analytics-ai-engine.md
  - block7-analytics-ai-engine-technical-requirements.md
  - fit041-analytics-ai-komparasi.md
  - analytics-ai-engine (entity)
  - analytics-ai-engine-data-model (concept)
purpose: > Use Case Analysis final untuk Analytics & AI Engine (Block 7) — 26 use cases across 8 kategori.
  Setiap UC dilengkapi: actors, pre-conditions, flow, source systems, data types,
  API endpoints, SLA, data quality, consumers, acceptance criteria.
  Dipetakan dari FIT041 Requirements (20 requirements) + DCIM-Wiki Reference Design + Technical Requirements.
---

# Use Case Analysis — Analytics & AI Engine (Block 7) (Final)

> **Purpose:** Use Case Analysis final untuk Analytics & AI Engine (Block 7) — merged dari FIT041 Requirements + DCIM-Wiki Reference Design & Technical Requirements.
> **Cara pakai:** Review per use case untuk memahami data apa yang harus diproses Analytics & AI Engine, dari mana datangnya, dengan SLA berapa, dan ke mana data dikirim.
> **Depends on:** Block 7 Reference Design, FIT041 Analytics & AI Technical Requirements, Block 2 (DI&I Gateway), Block 4 (CMDB), Block 5 (Web Dashboard)
> **Merge Source:** FIT041 Technical Requirements (Jan 2026) + DCIM-Wiki Block 7 Reference Design (Jun 2026) + DCIM-Wiki Block 7 Technical Requirements (Jun 2026)
> **Traceability:** 20 FIT041 requirements mapped ke 26 use cases DCIM-Wiki
> **Related:** [[fit041-analytics-ai-komparasi]] — Komparasi FIT041 vs DCIM-Wiki

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Use Case Taxonomy](#2-use-case-taxonomy)
3. [Time-Series Data Processing Use Cases (UC1–UC3)](#3-time-series-data-processing-use-cases-uc1uc3)
4. [Anomaly Detection Use Cases (UC4–UC7)](#4-anomaly-detection-use-cases-uc4uc7)
5. [Predictive Maintenance Use Cases (UC8–UC11)](#5-predictive-maintenance-use-cases-uc8uc11)
6. [Root Cause Analysis Use Cases (UC12–UC14)](#6-root-cause-analysis-use-cases-uc12uc14)
7. [Capacity Forecasting Use Cases (UC15–UC17)](#7-capacity-forecasting-use-cases-uc15uc17)
8. [Energy Optimization Use Cases (UC18–UC20)](#8-energy-optimization-use-cases-uc18uc20)
9. [Model Training & Management Use Cases (UC21–UC23)](#9-model-training--management-use-cases-uc21uc23)
10. [LLM/RAG Explanation Layer Use Cases (UC24–UC26)](#10-llmrag-explanation-layer-use-cases-uc24uc26)
11. [Source System → Use Case Matrix](#11-source-system--use-case-matrix)
12. [Data Type → Use Case Mapping](#12-data-type--use-case-mapping)
13. [API Requirements per Use Case](#13-api-requirements-per-use-case)
14. [SLA & Latency Requirements](#14-sla--latency-requirements)
15. [Data Quality Requirements per Use Case](#15-data-quality-requirements-per-use-case)
16. [Downstream Consumer Mapping](#16-downstream-consumer-mapping)
17. [FIT041 Requirements Checklist](#17-fit041-requirements-checklist)
18. [Gaps & Recommendations](#18-gaps--recommendations)
19. [Acceptance Criteria](#19-acceptance-criteria)
20. [Traceability Matrix](#20-traceability-matrix)

---

## 1. Executive Summary

### Scope

DCIM Core Platform memiliki **8 kategori use case** yang membutuhkan Analytics & AI Engine:

| Kategori | Jumlah | Prioritas Rata-rata |
|----------|--------|---------------------|
| **Time-Series Data Processing** | 3 use case (UC1–UC3) | P1 |
| **Anomaly Detection** | 4 use case (UC4–UC7) | P1–P2 |
| **Predictive Maintenance** | 4 use case (UC8–UC11) | P1–P2 |
| **Root Cause Analysis** | 3 use case (UC12–UC14) | P1–P2 |
| **Capacity Forecasting** | 3 use case (UC15–UC17) | P1–P2 |
| **Energy Optimization** | 3 use case (UC18–UC20) | P1–P2 |
| **Model Training & Management** | 3 use case (UC21–UC23) | P1–P2 |
| **LLM/RAG Explanation Layer** | 3 use case (UC24–UC26) | P1–P2 |
| **Total** | **26 use case** | — |

### Merge Summary

| Aspek | FIT041 | DCIM-Wiki Ref Design | DCIM-Wiki Tech Req | Merged |
|-------|--------|----------------------|---------------------|--------|
| Use Cases | 20 requirements (conceptual) | 8 functional areas | 32 FRs | **26 UCs** (detailed) |
| Architecture | 6 layers | 6-layer architecture | Specific stack | **6 layers** |
| Anomaly Detection | 2 req (generic) | 4 methods | 8 FRs | **4 UCs** (UC4–UC7) |
| Predictive Maint. | 1 req (generic) | 4 models | 7 FRs | **4 UCs** (UC8–UC11) |
| RCA | 1 req (correlation) | 6-step pipeline | 7 FRs | **3 UCs** (UC12–UC14) |
| Capacity | 1 req (generic) | 7 metrics, 4 models | 7 FRs | **3 UCs** (UC15–UC17) |
| Energy | — (missing) | PUE, cooling, carbon | 7 FRs | **3 UCs** (UC18–UC20) |
| Model Training | 1 req (generic) | 9-stage pipeline | 9 FRs | **3 UCs** (UC21–UC23) |
| LLM/RAG | — (missing) | Architecture + API | 7 FRs | **3 UCs** (UC24–UC26) |
| SLA Tiers | 1 (<500ms) | 8 components | 8 NFR tiers | **5 tiers** |
| Data Quality | — | 8 rules | 8 DQ rules | **8 rules** |
| API Endpoints | Generic REST | 24 endpoints | 24 endpoints | **24 endpoints** |
| Acceptance Criteria | — | 16 items | 32 items | **26 items** |

### Key Findings

1. **430+ metrics/sec** ingestion throughput dari DI&I Gateway melalui Kafka topic `dcim.analytics.metrics`
2. **< 1s latency** untuk time-series ingestion ke TimescaleDB hypertable
3. **< 500ms per event** untuk anomaly detection (Z-score real-time, Isolation Forest near-RT)
4. **< 30s per incident** untuk RCA analysis (timeline + topology + hypothesis)
5. **Daily batch** untuk capacity forecasting (Prophet, ARIMA)
6. **Hourly** untuk energy optimization (PUE calculation, cooling recommendations)
7. **< 5s per query** untuk LLM/RAG natural language explanation
8. **6 Kafka topics** dengan replication factor 3: metrics, anomalies, predictions, rca, capacity, energy
9. **4 ML models** di production: Z-score (real-time), Isolation Forest (multivariate), Prophet (trend), LSTM (sequential)
10. **24 API endpoints** across 7 groups dengan RBAC (analytics.read, analytics.write, analytics.admin)

### Quick Architecture View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     USE CASES — ANALYTICS & AI ENGINE                    │
│                                                                         │
│  UC1 Ingestion     UC2 Storage         UC3 Query/Aggregate             │
│  UC4 Real-time Det UC5 Threshold       UC6 Pattern Recog  UC7 FP Handle│
│  UC8 Failure Pred  UC9 Sched Optim     UC10 Model Accuracy UC11 Drift  │
│  UC12 Correlation  UC13 Dependency     UC14 Automated RCA               │
│  UC15 Trend Anal   UC16 Projection     UC17 Threshold Alert             │
│  UC18 PUE Calc     UC19 Cooling Opt    UC20 Power Distribution          │
│  UC21 Dev Pipeline UC22 Versioning     UC23 Deployment                  │
│  UC24 NL Query     UC25 Explanation    UC26 Knowledge Base              │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              ANALYTICS & AI ENGINE (Block 7)                            │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              Time-Series Pipeline                                 │  │
│  │  Kafka (dcim.analytics.metrics) → Flink/Python Stream Processor  │  │
│  │  → TimescaleDB hypertable → Grafana                              │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  ┌────────────────────────┴─────────────────────────────────────────┐  │
│  │              Intelligence Layer                                  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │  │
│  │  │ Anomaly  │ │Predictive│ │   RCA    │ │ Capacity │           │  │
│  │  │Detection │ │Maintenan.│ │  Engine  │ │Forecast. │           │  │
│  │  │Z-score   │ │Prophet   │ │Timeline  │ │Prophet   │           │  │
│  │  │Isol.Fors.│ │LSTM      │ │Topology  │ │ARIMA     │           │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                         │  │
│  │  │ Energy   │ │ LLM/RAG  │ │  Model   │                         │  │
│  │  │Optimiz.  │ │ Layer    │ │ Training │                         │  │
│  │  │PUE/Cool  │ │GPT-4/Cla │ │Pipeline  │                         │  │
│  │  └──────────┘ └──────────┘ └──────────┘                         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
         │                 │                │              │
         ▼                 ▼                ▼              ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐  ┌──────────┐
  │   CMDB   │    │Workflow  │    │  Dashboard   │  │   SIEM   │
  │(topology)│    │Automation│    │  (Grafana)   │  │  (Wazuh) │
  └──────────┘    └──────────┘    └──────────────┘  └──────────┘
```

---

## 2. Use Case Taxonomy

### 2.1 Classification

| ID | Use Case Name | Kategori | Prioritas | Latency Target | FIT041 Traceability |
|----|--------------|----------|-----------|----------------|---------------------|
| UC1 | Metric Ingestion Pipeline | Time-Series | **P1** | < 1s end-to-end | FIT041 §2.1.1 |
| UC2 | Time-Series Storage & Compression | Time-Series | **P1** | < 100ms write | FIT041 §2.1.3 |
| UC3 | Time-Series Query & Aggregation | Time-Series | **P1** | < 100ms p99 | FIT041 §2.1.2 |
| UC4 | Real-Time Anomaly Detection | Anomaly Detection | **P1** | < 500ms per event | FIT041 §2.3.1 |
| UC5 | Threshold-Based Alerting | Anomaly Detection | **P1** | < 100ms per check | FIT041 §2.3.1 |
| UC6 | Multi-Metric Pattern Recognition | Anomaly Detection | **P2** | < 500ms per prediction | FIT041 §2.3.1 |
| UC7 | False Positive Handling & Tuning | Anomaly Detection | **P2** | Batch (hourly) | FIT041 §3.2.2 |
| UC8 | Failure Probability Prediction | Predictive Maint. | **P1** | Daily batch | FIT041 §2.2.2 |
| UC9 | Maintenance Schedule Optimization | Predictive Maint. | **P2** | Daily batch | FIT041 §2.2.3 |
| UC10 | Model Accuracy Monitoring | Predictive Maint. | **P2** | Weekly evaluation | FIT041 §3.2.2 |
| UC11 | Model Drift Detection | Predictive Maint. | **P2** | Weekly computation | FIT041 §3.2.2 |
| UC12 | Incident Event Correlation | RCA | **P1** | < 30s per incident | FIT041 §2.3.2 |
| UC13 | Dependency Mapping & Traversal | RCA | **P1** | < 5s per traversal | FIT041 §2.3.2 |
| UC14 | Automated Root Cause Hypothesis | RCA | **P2** | < 30s per incident | FIT041 §2.3.2 |
| UC15 | Trend Analysis | Capacity Forecasting | **P1** | Daily batch | FIT041 §2.2.1 |
| UC16 | Resource Projection | Capacity Forecasting | **P2** | Daily batch | FIT041 §2.2.1 |
| UC17 | Capacity Threshold Alerting | Capacity Forecasting | **P1** | < 5min after batch | FIT041 §2.2.1 |
| UC18 | PUE Calculation | Energy Optimization | **P1** | Hourly | — (DCIM-Wiki unique) |
| UC19 | Cooling Optimization | Energy Optimization | **P2** | Hourly | — (DCIM-Wiki unique) |
| UC20 | Power Distribution Analysis | Energy Optimization | **P2** | Hourly | — (DCIM-Wiki unique) |
| UC21 | Model Development Pipeline | Model Training | **P1** | Weekly batch | FIT041 §3.1.2 |
| UC22 | Model Versioning & Registry | Model Training | **P1** | < 5s per operation | FIT041 §3.1.2 |
| UC23 | Model Deployment & Scoring | Model Training | **P1** | < 10s per deployment | FIT041 §3.1.2 |
| UC24 | Natural Language Query | LLM/RAG | **P1** | < 5s per query | — (DCIM-Wiki unique) |
| UC25 | Explanation Generation | LLM/RAG | **P1** | < 5s per query | — (DCIM-Wiki unique) |
| UC26 | Knowledge Base Management | LLM/RAG | **P2** | On-change | — (DCIM-Wiki unique) |

### 2.2 Priority Distribution

| Prioritas | Jumlah | Use Cases |
|-----------|--------|-----------|
| **P1 Critical** | 13 | UC1, UC2, UC3, UC4, UC5, UC8, UC12, UC13, UC15, UC17, UC18, UC21, UC22, UC23, UC24, UC25 |
| **P2 High** | 13 | UC6, UC7, UC9, UC10, UC11, UC14, UC16, UC19, UC20, UC26 |

---

## 3. Time-Series Data Processing Use Cases (UC1–UC3)

### 3.1 UC1 — Metric Ingestion Pipeline

**Objective:** Ingest 430+ metrics/sec dari DI&I Gateway melalui Kafka topic ke TimescaleDB dengan latency < 1s end-to-end.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 1s end-to-end (Kafka → TimescaleDB) |
| **Throughput** | ≥ 1000 metrics/sec (target: 430+ baseline) |
| **Kafka Topic** | `dcim.analytics.metrics` (6 partitions, RF=3, 7 days retention) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| DI&I Gateway (Block 2) | Metric producer | Publishes metric events to Kafka |
| Stream Processor (Flink/Python) | Consumer | Reads from Kafka, transforms, writes to TimescaleDB |
| NOC Operators | Consumer | Views ingested metrics on dashboard |
| SOC Analysts | Consumer | Correlates metrics with security events |

#### Pre-conditions

- Kafka broker cluster (3+ brokers) operational
- Topic `dcim.analytics.metrics` created with 6 partitions
- TimescaleDB hypertable `metrics` created
- Flink/Python stream processor deployed (2+ instances)
- DI&I Gateway configured to publish to Kafka topic

#### Main Flow

1. **Publish:** DI&I Gateway publishes metric event ke Kafka topic `dcim.analytics.metrics`
2. **Consume:** Stream Processor reads batch dari Kafka (max.poll.records = 500)
3. **Validate:** Validate schema — metric_name non-empty, value numeric, timestamp valid ISO 8601
4. **Transform:** Map event ke TimescaleDB schema (time, metric_name, ci_id, asset_id, source, value, unit, tags)
5. **Enrich:** Lookup CI metadata dari CMDB jika ci_id tersedia (cache Redis, TTL 5 min)
6. **Write:** Batch INSERT ke TimescaleDB hypertable (batch size 1000, async)
7. **Ack:** Commit Kafka offset setelah successful write
8. **Late Data:** Handle out-of-order events (up to 5 min late) via `time_bucket` gap-fill

#### Alternative Flows

- **A1:** Schema validation gagal → route message ke Dead Letter Queue (DLQ) topic `dcim.analytics.metrics.dlq`, log error, skip
- **A2:** TimescaleDB write gagal → retry 3x dengan exponential backoff (1s, 2s, 4s), lalu route ke DLQ
- **A3:** Kafka consumer lag > 1000 messages → trigger alert `AnalyticsKafkaConsumerLagHigh`, auto-scale consumer instances
- **A4:** CI metadata tidak ditemukan di CMDB → store dengan ci_id=null, tag `enrichment_status=missed`

#### Source Systems

| Source | Protocol | Data |
|--------|----------|------|
| DI&I Gateway (Block 2) | Kafka | Raw metric events |
| Prometheus / NMS | Pull/Push | Infrastructure metrics |
| BMS/EPMS | Kafka/MQTT | Power, cooling metrics |
| Cloud APIs | REST | Cloud resource metrics |

#### Data Types

| Data Type | Format | Example |
|-----------|--------|---------|
| Metric event | JSON | `{"timestamp":"...","metric_name":"cpu_usage","ci_id":"...","value":85.3,"unit":"%","tags":{}}` |
| Enrichment metadata | JSONB | CI name, type, owner, location |
| Ingestion metadata | JSONB | `{"ingestion_id":"uuid","batch_id":"...", "quality":"good"}` |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/metrics` | analytics.read | Query raw metrics (paginated, filterable) |
| GET | `/api/v1/analytics/metrics/{metric_name}/timeseries` | analytics.read | Get time-series data for metric |

#### SLA

| Dimension | Target |
|-----------|--------|
| End-to-end latency | < 1s (p99) |
| Availability | 99.9% |
| RTO | < 5 min |
| RPO | ≤ 5 min (WAL-based) |
| Consumer lag | < 1000 messages |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99% (events terproses / events diterima) |
| Accuracy | Value numeric, timestamp valid |
| Timeliness | < 1s end-to-end |
| Consistency | Schema valid sesuai contract |
| Validity | metric_name non-empty, source in allowed values |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| TimescaleDB | Time-series storage | Real-time |
| Anomaly Detection Service | Real-time scoring | < 500ms |
| Continuous Aggregates | Hourly/daily rollup | < 1 min lag |
| Grafana Dashboard | Visualization | < 5s |

#### Acceptance Criteria

- ✅ Kafka topic `dcim.analytics.metrics` menerima events dari DI&I Gateway
- ✅ Stream Processor memproses ≥ 1000 metrics/sec tanpa lag
- ✅ Metrics queryable di TimescaleDB dalam < 1s setelah publish ke Kafka
- ✅ Late events (up to 5 min) terproses dengan benar
- ✅ Failed messages route ke DLQ tanpa data loss
- ✅ Consumer lag < 1000 messages dalam kondisi normal

---

### 3.2 UC2 — Time-Series Storage & Compression

**Objective:** Store metrics di TimescaleDB hypertable dengan automatic compression (>7 hari) dan retention policy (90 hari configurable).

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Storage** | TimescaleDB hypertable |
| **Compression** | Auto-compress after 7 days (segmentby: metric_name, source) |
| **Retention** | Auto-drop after 90 days (configurable per metric) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Stream Processor | Writer | Writes metrics ke TimescaleDB |
| Analytics Services | Reader | Query metrics for analysis |
| Database Admin | Manager | Configures compression/retention policies |

#### Pre-conditions

- TimescaleDB v2.15+ installed and configured
- Hypertable `metrics` created with `create_hypertable('metrics', 'time')`
- Compression policy configured: `add_compression_policy('metrics', INTERVAL '7 days')`
- Retention policy configured: `add_retention_policy('metrics', INTERVAL '90 days')`
- Continuous aggregates created (metrics_hourly, metrics_daily)

#### Main Flow

1. **Write:** Stream Processor batch INSERT metrics ke hypertable (async, batch 1000)
2. **Index:** TimescaleDB auto-create indexes on time column
3. **Compress:** Background job compress chunks older than 7 days (segmentby: metric_name, source)
4. **Aggregate:** Continuous aggregates auto-refresh `metrics_hourly` dan `metrics_daily`
5. **Retain:** Background job drop chunks older than 90 days
6. **Backup:** Full backup daily, WAL archiving every 5 min

#### Alternative Flows

- **A1:** Compression job delay → alert DBA, chunks uncompressed > 7 days
- **A2:** Retention policy conflict → configurable per-metric override via `retention_config` table
- **A3:** Disk space < 20% → trigger alert, reduce retention window temporarily

#### TimescaleDB Schema

```sql
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    ci_id UUID,
    asset_id UUID,
    source VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    tags JSONB DEFAULT '{}'
);
SELECT create_hypertable('metrics', 'time');

ALTER TABLE metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'metric_name, source',
    timescaledb.compress_orderby = 'time DESC'
);
SELECT add_compression_policy('metrics', INTERVAL '7 days');
SELECT add_retention_policy('metrics', INTERVAL '90 days');

CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    metric_name, source,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS sample_count
FROM metrics
GROUP BY bucket, metric_name, source;

CREATE MATERIALIZED VIEW metrics_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    metric_name, source,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value
FROM metrics
GROUP BY bucket, metric_name, source;
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/metrics/storage/stats` | analytics.admin | Storage usage, compression ratio |
| PUT | `/api/v1/analytics/metrics/storage/compression` | analytics.admin | Update compression policy |

#### SLA

| Dimension | Target |
|-----------|--------|
| Write latency (batch) | < 100ms p99 |
| Compression ratio | > 50% reduction after compression |
| Aggregate refresh lag | < 1 minute |
| Backup RPO | ≤ 5 min |
| Backup RTO | ≤ 30 min |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (semua metric yang ditulis ter-compress) |
| Accuracy | Data tidak berubah setelah compression |
| Timeliness | Aggregate lag < 1 minute |
| Consistency | Compression segmentby konsisten |
| Validity | Retention config valid |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| Analytics Services | Historical data query | < 100ms |
| Continuous Aggregates | Rollup views | < 1 min lag |
| Model Training Pipeline | Historical feature extraction | Batch |

#### Acceptance Criteria

- ✅ Hypertable `metrics` terbentuk dengan partisi otomatis oleh waktu
- ✅ Data > 7 hari ter-compress secara otomatis (storage reduced > 50%)
- ✅ Data > 90 hari ter-drop secara otomatis
- ✅ Continuous aggregates (hourly, daily) ter-refresh < 1 minute lag
- ✅ Backup full daily + WAL archiving every 5 min aktif
- ✅ PITR (Point-in-Time Recovery) enabled

---

### 3.3 UC3 — Time-Series Query & Aggregation

**Objective:** Provide fast query access ke time-series data untuk analytics services, dashboards, dan LLM/RAG context retrieval.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 100ms p99 for 1-hour range query |
| **Throughput** | 100 req/s aggregate |
| **Data Sources** | Raw metrics, hourly aggregates, daily aggregates |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Anomaly Detection Service | Consumer | Queries recent metrics for Z-score |
| Predictive Maintenance | Consumer | Queries historical features for LSTM |
| Capacity Forecasting | Consumer | Queries daily aggregates for Prophet |
| Energy Optimization | Consumer | Queries power/cooling metrics hourly |
| LLM/RAG Service | Consumer | Queries metrics for context assembly |
| Grafana Dashboard | Consumer | Queries for visualization |

#### Pre-conditions

- TimescaleDB hypertable populated with metrics
- Continuous aggregates (hourly, daily) refreshed
- Connection pool (PgBouncer) configured, max 100 connections
- Query result cache (Redis) configured for frequently accessed ranges

#### Main Flow

1. **Query:** Consumer sends query with time range, metric_name, filters
2. **Route:** Query router determines if raw, hourly, or daily data needed
3. **Execute:** TimescaleDB executes query against appropriate table/view
4. **Cache:** Cache result in Redis (TTL: 30s for raw, 5 min for aggregates)
5. **Return:** Return JSON result with metadata

#### Alternative Flows

- **A1:** Cache hit → return cached result (< 5ms)
- **A2:** Query range > 7 days → route to compressed data, slightly higher latency
- **A3:** Connection pool exhausted → queue request, retry with backoff

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/metrics` | analytics.read | Query raw metrics (paginated) |
| GET | `/api/v1/analytics/metrics/{metric_name}/timeseries` | analytics.read | Time-series data for metric |
| GET | `/api/v1/analytics/metrics/aggregate` | analytics.read | Aggregated metrics (hourly/daily) |
| GET | `/api/v1/analytics/metrics/health` | analytics.read | Ingestion health check |

#### SLA

| Dimension | Target |
|-----------|--------|
| Query latency (1-hour range) | < 100ms p99 |
| Query latency (1-day range) | < 200ms p99 |
| Query latency (1-month range) | < 1s p99 |
| Throughput | 100 req/s |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% data returned sesuai query |
| Accuracy | Aggregate values konsisten dengan raw |
| Timeliness | Freshness < 1 min (aggregates) |
| Consistency | Same query = same result (deterministic) |
| Validity | Time range in allowed bounds |

#### Acceptance Criteria

- ✅ 1-hour range query < 100ms p99
- ✅ 1-day range query < 200ms p99
- ✅ Aggregates (hourly, daily) queryable dan refreshed < 1 min
- ✅ Cache hit rate > 60% untuk frequently queried metrics
- ✅ Connection pool handles 100 concurrent connections
- ✅ Query results konsisten antara raw dan aggregate tables

---

## 4. Anomaly Detection Use Cases (UC4–UC7)

### 4.1 UC4 — Real-Time Anomaly Detection

**Objective:** Detect anomalies real-time menggunakan Z-score method dengan latency < 500ms per event dan emit alerts ke Kafka topic `dcim.analytics.anomalies`.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 500ms per event (end-to-end) |
| **Method** | Z-score (threshold: 3.0, configurable) |
| **Kafka Topic** | `dcim.analytics.anomalies` (3 partitions, RF=3, 30 days retention) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Stream Processor | Trigger | Calls anomaly detection on each metric |
| Anomaly Detection Service | Processor | Scores metric against historical baseline |
| NOC Operators | Consumer | Receives anomaly alerts on dashboard |
| Workflow Automation (Block 8) | Consumer | Triggers remediation workflows |
| LLM/RAG Service | Consumer | Retrieves anomalies for explanation |

#### Pre-conditions

- Anomaly Detection Service deployed (2+ instances)
- TimescaleDB has ≥ 20 historical data points per metric for Z-score baseline
- Kafka topic `dcim.analytics.anomalies` created
- Alert thresholds configured per metric (default: Z-score > 3.0)

#### Main Flow

1. **Receive:** Stream Processor passes metric event ke Anomaly Detection Service
2. **Query History:** Fetch last 100 values dari TimescaleDB untuk metric_name + source (1-hour window)
3. **Compute Z-score:** Calculate mean, stdev dari historical values; compute Z-score untuk current value
4. **Evaluate:** If Z-score > 3.0 → anomaly detected
5. **Score:** Compute anomaly_score (0.0–1.0) berdasarkan Z-score magnitude
6. **Classify:** Assign severity: low (3.0–3.5), medium (3.5–4.5), high (4.5–5.5), critical (>5.5)
7. **Enrich:** Attach possible_causes dan recommended_actions based on metric_name patterns
8. **Emit:** Publish anomaly event ke Kafka topic `dcim.analytics.anomalies`
9. **Store:** Write anomaly record ke `anomaly_events` table di TimescaleDB

#### Alternative Flows

- **A1:** Historical data < 20 points → skip detection, log warning, tag metric as `baseline_insufficient`
- **A2:** Anomaly score > 0.9 + severity = critical → immediate alert ke Workflow Automation (Kafka)
- **A3:** Detection service instance down → failover ke second instance (HA, < 30s)
- **A4:** Anomaly matches recent known anomaly (same metric, < 30 min window) → deduplicate, update count

#### Anomaly Alert Schema

```json
{
  "anomaly_id": "uuid",
  "timestamp": "ISO-8601",
  "metric_name": "string",
  "ci_id": "uuid",
  "asset_id": "uuid",
  "detection_method": "z_score",
  "current_value": "number",
  "expected_range": ["number", "number"],
  "z_score": "number",
  "anomaly_score": "number (0.0-1.0)",
  "severity": "low|medium|high|critical",
  "description": "string",
  "possible_causes": ["string"],
  "recommended_actions": ["string"]
}
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/anomalies` | analytics.read | List anomalies (filterable) |
| GET | `/api/v1/analytics/anomalies/{id}` | analytics.read | Get anomaly details |
| POST | `/api/v1/analytics/anomalies/detect` | analytics.write | Trigger detection for metric |
| PUT | `/api/v1/analytics/anomalies/{id}/threshold` | analytics.admin | Update threshold config |

#### SLA

| Dimension | Target |
|-----------|--------|
| Detection latency | < 500ms per event (p99) |
| Alert emit latency | < 1s end-to-end |
| Availability | 99.9% |
| False positive rate | < 10% |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 98% anomalies classified dengan severity |
| Accuracy | Z-score computation correct |
| Timeliness | < 500ms per detection |
| Consistency | Same metric + value = same anomaly score |
| Validity | Severity in allowed enum, score in 0.0–1.0 |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| Kafka (dcim.analytics.anomalies) | Alert stream | Real-time |
| Workflow Automation | Remediation trigger | < 5s |
| NOC Dashboard | Alert display | < 5s |
| LLM/RAG Service | Explanation context | < 5s |
| Anomaly Events Table | Historical analysis | Real-time |

#### Acceptance Criteria

- ✅ Z-score detection menangkap threshold violations (Z > 3.0) dalam < 500ms
- ✅ Anomaly alerts terpublish ke Kafka topic `dcim.analytics.anomalies`
- ✅ Severity classification: low, medium, high, critical — correct mapping
- ✅ Anomaly score dalam range 0.0–1.0
- ✅ Deduplication aktif: same anomaly dalam 30 min window → update, bukan duplicate
- ✅ HA failover < 30s saat primary instance down

---

### 4.2 UC5 — Threshold-Based Alerting

**Objective:** Provide configurable threshold-based alerting untuk metrics dengan static bounds (min/max) dan rate-of-change detection.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 100ms per check |
| **Thresholds** | Static (min/max), Dynamic (percentage change), Rate-of-change |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| DC Managers | Configurer | Configures thresholds via API |
| Stream Processor | Trigger | Checks thresholds on each metric |
| Alert Service | Processor | Evaluates and emits threshold alerts |

#### Pre-conditions

- Threshold configuration table populated (`threshold_config`)
- Default thresholds for standard metrics configured
- Alert service deployed and operational

#### Main Flow

1. **Receive:** Metric event received
2. **Load Config:** Fetch threshold configuration for metric_name + ci_id (from Redis cache, TTL 5 min)
3. **Evaluate Static:** Check if value > max_threshold or value < min_threshold
4. **Evaluate Rate:** Check if percentage change from last value > rate_threshold (e.g., > 50% in 1 min)
5. **Evaluate Sustained:** Check if value has been above threshold for > sustained_minutes (default: 5 min)
6. **Alert:** If any check triggers → emit threshold alert ke `dcim.analytics.anomalies` with detection_method = "threshold"
7. **Notify:** Send notification ke configured channels (email, Slack, webhook)

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/anomalies/thresholds` | analytics.read | List threshold configs |
| PUT | `/api/v1/analytics/anomalies/thresholds/{metric_name}` | analytics.admin | Update threshold |
| POST | `/api/v1/analytics/anomalies/thresholds/test` | analytics.write | Test threshold against value |

#### SLA

| Dimension | Target |
|-----------|--------|
| Check latency | < 100ms per check |
| Alert latency | < 200ms end-to-end |
| Config refresh | < 5 min (cache TTL) |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% thresholds evaluated |
| Accuracy | Threshold comparison correct |
| Timeliness | < 100ms per check |
| Consistency | Same value + config = same alert |
| Validity | Threshold values numeric, min < max |

#### Acceptance Criteria

- ✅ Static threshold checks complete dalam < 100ms
- ✅ Rate-of-change detection (> 50%/min) aktif
- ✅ Sustained threshold alerts (5 min window) working
- ✅ Threshold configs updateable via API dengan cache refresh < 5 min
- ✅ Configurable per-metric dan per-CI

---

### 4.3 UC6 — Multi-Metric Pattern Recognition

**Objective:** Detect anomalous patterns across multiple metrics simultaneously menggunakan Isolation Forest untuk multi-variate anomaly detection.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 500ms per prediction |
| **Method** | Isolation Forest (scikit-learn) |
| **Model** | Trained offline, loaded to scoring service |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Model Training Pipeline | Producer | Trains and deploys Isolation Forest model |
| Scoring Service | Processor | Scores multi-metric feature vectors |
| NOC Operators | Consumer | Views multi-metric anomalies |

#### Pre-conditions

- Isolation Forest model trained and registered in Model Registry
- Model deployed to scoring service (loaded in memory)
- Feature engineering pipeline active (metrics → feature vector)
- Training data size ≥ 10,000 samples

#### Main Flow

1. **Aggregate:** Collect recent metrics (last 1 hour) for same CI into feature vector
2. **Transform:** Feature engineering — normalize, handle missing values, create derived features
3. **Score:** Isolation Forest model predicts anomaly label (-1 = anomaly, 1 = normal) + anomaly score
4. **Interpret:** If label = -1 → anomaly detected, compute feature importance for explanation
5. **Correlate:** Cross-reference with Z-score anomalies for same time window
6. **Emit:** Publish combined anomaly event ke `dcim.analytics.anomalies`

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/analytics/anomalies/detect/multivariate` | analytics.write | Trigger multi-metric detection |
| GET | `/api/v1/analytics/anomalies/patterns` | analytics.read | List detected patterns |

#### SLA

| Dimension | Target |
|-----------|--------|
| Prediction latency | < 500ms per prediction (p99) |
| Model accuracy | > 90% (precision > 0.85) |
| Availability | 99.9% |

#### Acceptance Criteria

- ✅ Isolation Forest model loaded dan scoring < 500ms
- ✅ Multi-metric anomalies terdeteksi dengan benar
- ✅ Feature importance disertakan untuk explainability
- ✅ Cross-reference dengan Z-score anomalies aktif
- ✅ Model retrained setidaknya bulanan

---

### 4.4 UC7 — False Positive Handling & Tuning

**Objective:** Reduce false positive rate melalui feedback loop, threshold tuning, dan seasonal adjustment.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | Batch (hourly evaluation) |
| **Target** | False positive rate < 10% |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| NOC Operators | Feedback provider | Marks anomalies as true/false positive |
| Tuning Service | Processor | Analyzes feedback, adjusts thresholds |
| Data Engineer | Reviewer | Reviews tuning recommendations |

#### Pre-conditions

- Anomaly feedback API available (mark as true/false positive)
- Historical anomaly labels available (≥ 30 days)
- Seasonal patterns identified for key metrics

#### Main Flow

1. **Collect:** Gather anomaly feedback dari operators (via API or dashboard)
2. **Analyze:** Calculate false positive rate per metric, per detection method, per time window
3. **Identify:** Find patterns — e.g., high FP rate pada weekend morning untuk specific metric
4. **Tune:** Recommend threshold adjustments based on analysis
5. **Seasonal:** Apply seasonal decomposition to baseline calculation (daily/weekly patterns)
6. **Apply:** Auto-apply tuned thresholds (if confidence > 0.9) or recommend for review
7. **Report:** Generate tuning report (accuracy improvement, FP reduction)

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/analytics/anomalies/{id}/feedback` | analytics.write | Submit FP/TP feedback |
| GET | `/api/v1/analytics/anomalies/false-positive-stats` | analytics.read | FP rate statistics |
| POST | `/api/v1/analytics/anomalies/tune` | analytics.admin | Trigger tuning analysis |

#### SLA

| Dimension | Target |
|-----------|--------|
| Analysis latency | < 5 min per batch |
| FP rate target | < 10% |
| Threshold update propagation | < 5 min |

#### Acceptance Criteria

- ✅ FP feedback mechanism available via API
- ✅ False positive rate < 10% setelah tuning
- ✅ Seasonal decomposition mengurangi FP pada predictable patterns
- ✅ Tuning recommendations auto-generated
- ✅ Accuracy improvement tracked dan terukur

---

## 5. Predictive Maintenance Use Cases (UC8–UC11)

### 5.1 UC8 — Failure Probability Prediction

**Objective:** Predict failure probability untuk setiap CI dalam 30-day window menggunakan LSTM dan Prophet models.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Models** | LSTM (primary), Prophet (secondary), Survival Analysis (quarterly) |
| **Prediction Window** | 30 days |
| **Kafka Topic** | `dcim.analytics.predictions` (3 partitions, RF=3, 30 days retention) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Predictive Maintenance Service | Processor | Generates predictions batch |
| IT Operations | Consumer | Reviews predictions, schedules maintenance |
| DC Managers | Consumer | Executive view of risk |
| Workflow Automation | Consumer | Triggers proactive maintenance |

#### Pre-conditions

- LSTM model trained, registered, and deployed
- Prophet model configured with trend + seasonality parameters
- Historical metrics available (≥ 90 days for training data)
- CI-to-metric mapping configured in CMDB

#### Main Flow

1. **Schedule:** Daily batch job triggered (cron: 02:00 UTC)
2. **Collect:** Extract feature vectors untuk semua active CIs dari TimescaleDB
3. **Predict (LSTM):** Run LSTM inference — output: failure_probability, confidence
4. **Predict (Prophet):** Run Prophet forecast — output: trend projection, seasonality
5. **Combine:** Ensemble prediction (weighted average: LSTM 0.7, Prophet 0.3)
6. **Classify:** Assign risk_level: low (<0.2), medium (0.2-0.4), high (0.4-0.7), critical (>0.7)
7. **Enrich:** Attach contributing_factors dengan weights
8. **Schedule Maintenance:** Calculate optimal maintenance_window based on risk level
9. **Emit:** Publish prediction ke Kafka topic `dcim.analytics.predictions`
10. **Store:** Write prediction record ke `predictions` table

#### Prediction Schema

```json
{
  "prediction_id": "uuid",
  "ci_id": "uuid",
  "asset_id": "uuid",
  "prediction_type": "failure_probability",
  "model": "lstm_v2.1",
  "predicted_at": "ISO-8601",
  "prediction_window": "30_days",
  "failure_probability": 0.72,
  "confidence": 0.85,
  "risk_level": "high",
  "contributing_factors": [
    {"factor": "disk_health_declining", "weight": 0.35},
    {"factor": "age_above_threshold", "weight": 0.25}
  ],
  "recommended_actions": ["Schedule disk replacement within 2 weeks"],
  "maintenance_window": {
    "earliest": "2026-06-30",
    "latest": "2026-07-07",
    "estimated_duration_hours": 4
  }
}
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/predictions` | analytics.read | List predictions (filterable) |
| GET | `/api/v1/analytics/predictions/{id}` | analytics.read | Get prediction details |
| POST | `/api/v1/analytics/predictions/forecast` | analytics.write | Trigger forecast for CI |
| GET | `/api/v1/analytics/predictions/schedule` | analytics.read | Get maintenance schedule |

#### SLA

| Dimension | Target |
|-----------|--------|
| Batch completion | < 4 hours (full CI fleet) |
| Single CI forecast | < 10s |
| Model accuracy | > 80% (F1 score) |
| Prediction freshness | Daily |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% CIs covered by predictions |
| Accuracy | F1 score > 0.80 |
| Timeliness | Daily freshness |
| Consistency | Same CI + same date = same prediction (deterministic) |
| Validity | failure_probability in 0.0–1.0, confidence in 0.0–1.0 |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| Kafka (dcim.analytics.predictions) | Prediction stream | Daily |
| IT Operations | Maintenance planning | < 1 day |
| Workflow Automation | Proactive ticket creation | < 5 min |
| LLM/RAG Service | Prediction explanation | < 5s |

#### Acceptance Criteria

- ✅ Daily batch menghasilkan predictions untuk ≥ 95% active CIs
- ✅ Failure probability dalam range 0.0–1.0 dengan confidence score
- ✅ Contributing factors dengan weights disertakan
- ✅ Maintenance window dihitung berdasarkan risk level
- ✅ Predictions terpublish ke Kafka topic
- ✅ Model ensemble (LSTM 0.7 + Prophet 0.3) working

---

### 5.2 UC9 — Maintenance Schedule Optimization

**Objective:** Generate optimal maintenance schedule berdasarkan predictions, constraints (maintenance window, resource availability), dan risk prioritization.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Optimization** | Priority-based scheduling |
| **Constraints** | Time window, technician availability, CI criticality |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| IT Operations | Schedule manager | Reviews and approves schedules |
| Workflow Automation | Executor | Creates maintenance tickets |
| Maintenance Team | Consumer | Receives scheduled work orders |

#### Pre-conditions

- Failure predictions available (from UC8)
- Maintenance constraints defined (max concurrent, time windows, resource pools)
- CI criticality levels configured in CMDB

#### Main Flow

1. **Collect:** Fetch all predictions with risk_level >= medium
2. **Prioritize:** Sort by failure_probability / time_to_failure (urgency score)
3. **Schedule:** Assign maintenance dates based on urgency + constraints
4. **De-conflict:** Ensure no scheduling conflicts (same CI, overlapping windows)
5. **Optimize:** Minimize total downtime by grouping maintenance per rack/location
6. **Output:** Generate schedule JSON with dates, CIs, priorities, estimated duration
7. **Notify:** Publish schedule to Workflow Automation for ticket creation

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/predictions/schedule` | analytics.read | Get current schedule |
| POST | `/api/v1/analytics/predictions/schedule/optimize` | analytics.write | Trigger schedule optimization |
| PUT | `/api/v1/analytics/predictions/schedule/{ci_id}` | analytics.write | Manual schedule override |

#### SLA

| Dimension | Target |
|-----------|--------|
| Schedule generation | < 30s for full fleet |
| Optimization | < 60s |

#### Acceptance Criteria

- ✅ Schedule generated untuk semua CIs dengan risk_level >= medium
- ✅ Constraints respected (max concurrent, time windows)
- ✅ De-confliction aktif (no overlapping maintenance)
- ✅ Grouping per location mengurangi total downtime
- ✅ Manual override available via API

---

### 5.10 UC10 — Model Accuracy Monitoring

**Objective:** Monitor prediction model accuracy over time dan trigger retraining when accuracy degrades below threshold.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Evaluation** | Weekly (batch) |
| **Metrics** | Precision, Recall, F1, AUC-ROC |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Model Monitoring Service | Processor | Evaluates model performance |
| Data Engineer | Reviewer | Reviews accuracy reports |
| Model Training Pipeline | Executor | Triggers retraining if needed |

#### Pre-conditions

- Ground truth data available (actual failures vs predicted)
- Model evaluation pipeline configured
- Model Registry with performance history

#### Main Flow

1. **Collect:** Fetch predictions from last 7 days
2. **Match:** Match predictions with actual outcomes (from CMDB, ITSM)
3. **Evaluate:** Calculate precision, recall, F1, AUC-ROC
4. **Compare:** Compare with previous evaluation and baseline
5. **Alert:** If F1 < 0.80 for 7 consecutive days → alert Data Engineer
6. **Retrain:** If accuracy drop confirmed → trigger retraining pipeline (UC21)
7. **Report:** Generate weekly accuracy report

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/models/{id}/metrics` | analytics.read | Model performance metrics |
| GET | `/api/v1/analytics/models/{id}/accuracy/history` | analytics.read | Accuracy trend |

#### SLA

| Dimension | Target |
|-----------|--------|
| Evaluation latency | < 30 min (weekly batch) |
| Accuracy alert | < 1 hour after degradation detected |

#### Acceptance Criteria

- ✅ Weekly evaluation menghasilkan precision, recall, F1, AUC-ROC
- ✅ Accuracy alert fires jika F1 < 0.80 selama 7 hari
- ✅ Retraining pipeline triggered secara otomatis
- ✅ Accuracy history available via API
- ✅ Baseline accuracy tercatat di Model Registry

---

### 5.11 UC11 — Model Drift Detection

**Objective:** Detect model drift — perubahan distribusi data input atau output yang menyebabkan degradasi prediksi.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Computation** | Weekly (batch) |
| **Drift Score** | 0.0 (no drift) to 1.0 (severe drift) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Drift Monitor Service | Processor | Computes drift scores |
| Data Engineer | Reviewer | Reviews drift reports |
| Model Training Pipeline | Executor | Triggers retraining |

#### Pre-conditions

- Reference distribution (training data statistics) stored in Model Registry
- Recent prediction distribution available
- Drift detection algorithm configured (PSI or KL-divergence)

#### Main Flow

1. **Reference:** Load reference distribution from training data statistics
2. **Current:** Compute current distribution from last 7 days of predictions/features
3. **Compute PSI:** Calculate Population Stability Index (PSI) for each key feature
4. **Aggregate:** Compute overall drift score (weighted average of feature PSI scores)
5. **Alert:** If drift_score > 0.15 for 7 consecutive days → alert
6. **Action:** Trigger model retraining (UC21) if drift confirmed
7. **Report:** Generate drift report with feature-level breakdown

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/models/{id}/drift` | analytics.read | Current drift score |
| GET | `/api/v1/analytics/models/{id}/drift/history` | analytics.read | Drift score history |

#### SLA

| Dimension | Target |
|-----------|--------|
| Drift computation | < 10 min (weekly batch) |
| Alert latency | < 1 hour after threshold exceeded |

#### Acceptance Criteria

- ✅ PSI computed untuk setiap key feature
- ✅ Overall drift score dalam range 0.0–1.0
- ✅ Alert fires jika drift_score > 0.15 selama 7 hari
- ✅ Feature-level drift breakdown available
- ✅ Retraining triggered jika drift confirmed

---

## 6. Root Cause Analysis Use Cases (UC12–UC14)

### 6.1 UC12 — Incident Event Correlation

**Objective:** Correlate events dari multiple sources (metrics, logs, alerts, CMDB changes) untuk reconstruct timeline insiden.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 30s per incident |
| **Sources** | Metrics, Elasticsearch logs, CMDB events, alerts |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Incident Management (ITSM) | Trigger | Sends incident details for RCA |
| RCA Engine | Processor | Correlates events and generates analysis |
| NOC Operators | Consumer | Reviews correlated timeline |
| LLM/RAG Service | Consumer | Generates natural language explanation |

#### Pre-conditions

- Elasticsearch index `dcim-siem-*,dcim-events-*` populated
- TimescaleDB has historical metrics for affected CI
- CMDB topology data available via API
- RCA engine deployed and operational

#### Main Flow

1. **Receive:** RCA Engine receives incident_id + ci_id + timeframe (default: 60 min)
2. **Timeline:** Query Elasticsearch for all events related to CI in timeframe (sorted by timestamp)
3. **Metrics:** Query TimescaleDB for metric anomalies around incident time
4. **CMDB Changes:** Query CMDB for recent config changes on CI
5. **Correlate:** Match events by timestamp proximity (±5 min window) and CI relationship
6. **Cluster:** Group correlated events into event clusters
7. **Score:** Rank event clusters by relevance to incident (time proximity, causality indicators)
8. **Output:** Return correlated event timeline dengan cluster labels

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/analytics/rca/analyze` | analytics.write | Trigger RCA for incident |
| GET | `/api/v1/analytics/rca/{id}` | analytics.read | Get RCA report |
| GET | `/api/v1/analytics/rca/history` | analytics.read | RCA history |

#### SLA

| Dimension | Target |
|-----------|--------|
| Analysis latency | < 30s per incident (p99) |
| Availability | 99.9% |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% correlated events included |
| Accuracy | Timestamp correlation correct (±5 min) |
| Timeliness | < 30s end-to-end |
| Consistency | Same incident = same correlation |
| Validity | Event timestamps valid |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| ITSM | Incident enrichment | < 30s |
| NOC Operators | Investigation support | < 30s |
| LLM/RAG Service | Natural language explanation | < 5s |
| Knowledge Base | Pattern storage | On-demand |

#### Acceptance Criteria

- ✅ Timeline reconstructed dengan events dari ≥ 3 sources
- ✅ Event correlation complete dalam < 30s
- ✅ Correlated events dikluster dengan benar
- ✅ Timeline visualizable (text + API)
- ✅ Correlation accuracy > 90% (verified against manual analysis)

---

### 6.2 UC13 — Dependency Mapping & Traversal

**Objective:** Traverse CMDB topology untuk identify upstream dependencies dan downstream impacts dari CI yang terkena insiden.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5s per traversal |
| **Depth** | Max 3 levels (configurable) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| RCA Engine | Trigger | Requests topology traversal |
| CMDB (Block 4) | Provider | Returns topology data |
| NOC Operators | Consumer | Views dependency chain |

#### Pre-conditions

- CMDB topology data accessible via API
- CI relationships populated (contains, depends_on, runs_on, connected_to)
- Topology cache (Redis) warm

#### Main Flow

1. **Receive:** RCA Engine requests topology for ci_id, depth=3
2. **Cache Check:** Check Redis cache for topology (key: `topology:{ci_id}:3`)
3. **Traverse:** If cache miss → BFS traversal from CMDB API
4. **Upstream:** Identify CIs that depend on target CI (depends_on, runs_on)
5. **Downstream:** Identify CIs impacted by target CI (impacts)
6. **Score:** Assign dependency weight based on relationship type and CI criticality
7. **Cache:** Store result in Redis (TTL: 5 min)
8. **Output:** Return dependency tree with scores

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/rca/{id}/dependencies` | analytics.read | Get CI dependencies for RCA |
| GET | `/api/v1/analytics/rca/dependencies/{ci_id}` | analytics.read | Direct dependency query |

#### SLA

| Dimension | Target |
|-----------|--------|
| Traversal latency | < 5s (with cache) |
| Cache hit rate | > 80% |

#### Acceptance Criteria

- ✅ Upstream dependencies identified (depends_on, runs_on)
- ✅ Downstream impacts identified (impacts)
- ✅ Traversal depth configurable (1–3 levels)
- ✅ Dependency scores assigned (weight by relationship + criticality)
- ✅ Cache hit rate > 80% untuk repeated queries
- ✅ Topology data consistent dengan CMDB

---

### 6.3 UC14 — Automated Root Cause Hypothesis

**Objective:** Generate ranked root cause hypotheses berdasarkan timeline, correlations, dependencies, dan historical patterns.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 30s per incident (included in UC12 total) |
| **Output** | Ranked hypotheses with confidence scores |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| RCA Engine | Processor | Generates and ranks hypotheses |
| NOC Operators | Consumer | Reviews hypotheses, selects root cause |
| Knowledge Base | Provider | Historical incident patterns |

#### Pre-conditions

- Timeline from UC12 available
- Dependency map from UC13 available
- Historical incident database with resolutions
- Hypothesis generation rules configured

#### Main Flow

1. **Collect:** Gather timeline (UC12) + dependencies (UC13) + historical patterns
2. **Hypothesize:** Generate hypotheses based on:
   - **Upstream failure:** If upstream CI has anomaly/failure → confidence 0.7
   - **Metric anomaly:** If metric deviated before incident → confidence 0.6
   - **Security event:** If security event correlated → confidence 0.5
   - **Config change:** If config change before incident → confidence 0.65
   - **Known pattern:** If matches historical incident → confidence 0.8
3. **Score:** Apply Bayesian scoring using historical resolution data
4. **Rank:** Sort hypotheses by confidence score (descending)
5. **Remediate:** Attach recommended actions per hypothesis
6. **Output:** Return ranked hypotheses with evidence

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/rca/{id}/hypotheses` | analytics.read | Get ranked hypotheses |
| POST | `/api/v1/analytics/rca/{id}/hypotheses/confirm` | analytics.write | Confirm root cause (feedback) |

#### SLA

| Dimension | Target |
|-----------|--------|
| Total analysis (UC12+13+14) | < 30s per incident (p99) |
| Hypothesis ranking | Included in total |

#### Acceptance Criteria

- ✅ ≥ 3 hypotheses generated per incident
- ✅ Hypotheses ranked by confidence (descending)
- ✅ Each hypothesis has: cause, confidence, evidence, type
- ✅ Recommended actions attached per hypothesis
- ✅ Historical pattern matching aktif
- ✅ Feedback mechanism (confirm/reject) available via API

---

## 7. Capacity Forecasting Use Cases (UC15–UC17)

### 7.1 UC15 — Trend Analysis

**Objective:** Analyze historical trends untuk CPU, memory, storage, network, power, cooling dengan Prophet dan ARIMA models.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Models** | Prophet (trend + seasonality), ARIMA (stationary), Linear Regression (simple) |
| **Schedule** | Daily batch (02:30 UTC) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Capacity Forecasting Service | Processor | Runs trend analysis |
| DC Managers | Consumer | Reviews trends for planning |
| IT Operations | Consumer | Identifies trending issues |

#### Pre-conditions

- Historical metrics available (≥ 30 days) for target resources
- TimescaleDB daily aggregates populated
- Forecasting models configured (Prophet, ARIMA)
- Resource-to-metric mapping defined

#### Main Flow

1. **Schedule:** Daily batch job triggered (02:30 UTC)
2. **Collect:** Extract daily aggregates untuk target resources (CPU, memory, storage, network, power, cooling, rack space)
3. **Model Selection:** Choose model per resource:
   - **Prophet:** Strong seasonality (daily/weekly patterns)
   - **ARIMA:** Stationary time-series
   - **Linear:** Simple linear trend
4. **Fit:** Train model on historical data (last 90 days)
5. **Project:** Generate 30-day forecast (CPU, memory, network, power, cooling) and 365-day (rack space)
6. **Confidence:** Calculate confidence intervals (95%)
7. **Store:** Write forecast results to `capacity_forecasts` table
8. **Emit:** Publish to Kafka topic `dcim.analytics.capacity`

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/capacity` | analytics.read | List capacity reports |
| GET | `/api/v1/analytics/capacity/{resource}` | analytics.read | Get forecast for resource |
| POST | `/api/v1/analytics/capacity/forecast` | analytics.write | Trigger capacity forecast |

#### SLA

| Dimension | Target |
|-----------|--------|
| Batch completion | < 2 hours (full datacenter) |
| Single resource forecast | < 10s |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% resources covered |
| Accuracy | Forecast within 10% of actual (30-day MAPE) |
| Timeliness | Daily freshness |
| Consistency | Same resource + same date = same forecast |
| Validity | Projection values > 0, confidence intervals valid |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| Capacity Dashboard | Trend visualization | < 5s |
| DC Managers | Planning decisions | Daily |
| LLM/RAG Service | Trend explanation | < 5s |

#### Acceptance Criteria

- ✅ Trend analysis complete untuk 7 resource types (CPU, memory, storage, network, power, cooling, rack)
- ✅ Model selection otomatis (Prophet/ARIMA/Linear) per resource
- ✅ 30-day forecast dengan 95% confidence interval
- ✅ 365-day forecast untuk rack space
- ✅ Forecast MAPE < 10% (30-day accuracy)
- ✅ Results terpublish ke Kafka dan dashboard

---

### 7.2 UC16 — Resource Projection

**Objective:** Project resource exhaustion dates berdasarkan trends dan generate capacity recommendations.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Projections** | Exhaustion date, days until 90% utilization |
| **Recommendations** | Resource additions, optimization actions |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Capacity Forecasting Service | Processor | Generates projections |
| DC Managers | Consumer | Reviews projections for CAPEX planning |
| Procurement | Consumer | Uses for purchase planning |

#### Pre-conditions

- Trend analysis from UC15 available
- Total capacity for each resource defined
- Recommendation rules configured

#### Main Flow

1. **Collect:** Load forecasts from UC15
2. **Project:** Calculate date when utilization > 90% (exhaustion date)
3. **Days:** Calculate days_until_90pct for each resource
4. **Recommend:** Generate recommendations:
   - If exhaustion < 30 days → "Urgent: add capacity immediately"
   - If exhaustion < 90 days → "Plan: add capacity within quarter"
   - If exhaustion < 180 days → "Monitor: capacity adequate for 6 months"
5. **Cost:** Calculate estimated cost impact (if cost data available)
6. **Store:** Write projection to `capacity_projections` table

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/capacity/projections` | analytics.read | List projections |
| GET | `/api/v1/analytics/capacity/projections/{resource}` | analytics.read | Projection for resource |

#### SLA

| Dimension | Target |
|-----------|--------|
| Projection generation | < 30s per resource |

#### Acceptance Criteria

- ✅ Exhaustion dates calculated untuk semua resources
- ✅ Days until 90% utilization accurate
- ✅ Recommendations generated berdasarkan urgency
- ✅ Cost impact included (if data available)
- ✅ Projections available via API

---

### 7.3 UC17 — Capacity Threshold Alerting

**Objective:** Alert when projected utilization exceeds thresholds — proactive capacity warning sebelum exhaustion terjadi.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Alert Thresholds** | 70% (info), 80% (warning), 90% (critical) |
| **Check Frequency** | After each daily forecast |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Capacity Alert Service | Processor | Evaluates projections against thresholds |
| DC Managers | Consumer | Receives capacity alerts |
| Workflow Automation | Consumer | Triggers capacity planning workflow |

#### Pre-conditions

- Forecasts from UC15 available
- Alert thresholds configured per resource type
- Notification channels configured (email, Slack)

#### Main Flow

1. **Evaluate:** For each resource, check if projected utilization > threshold within forecast horizon
2. **Alert:** If threshold exceeded:
   - 70% within 180 days → info notification
   - 80% within 90 days → warning alert
   - 90% within 30 days → critical alert
3. **Deduplicate:** Don't re-alert if same resource + same threshold already alerted within 7 days
4. **Notify:** Send alert via configured channels
5. **Workflow:** If critical → trigger capacity planning workflow

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/capacity/alerts` | analytics.read | List active capacity alerts |
| PUT | `/api/v1/analytics/capacity/alerts/thresholds` | analytics.admin | Update alert thresholds |

#### SLA

| Dimension | Target |
|-----------|--------|
| Alert generation | < 5 min after forecast completion |
| Deduplication window | 7 days |

#### Acceptance Criteria

- ✅ Capacity alerts fire saat projected > threshold
- ✅ 3 severity levels: info, warning, critical
- ✅ Deduplication aktif (7-day window)
- ✅ Critical alerts trigger workflow
- ✅ Thresholds configurable via API

---

## 8. Energy Optimization Use Cases (UC18–UC20)

### 8.1 UC18 — PUE Calculation

**Objective:** Calculate Power Usage Effectiveness (PUE) secara real-time dan historical untuk datacenter.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Calculation** | Hourly batch + real-time |
| **Formula** | PUE = Total Facility Power / IT Equipment Power |
| **Target PUE** | < 1.4 |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Energy Optimization Service | Processor | Calculates PUE |
| Facilities Team | Consumer | Monitors PUE for optimization |
| DC Managers | Consumer | Executive PUE reporting |

#### Pre-conditions

- BMS/EPMS data available (total facility power, IT power)
- Power metrics ingested via Kafka topic `dcim.analytics.metrics`
- PUE target configured (default: 1.4)
- Historical PUE data available (≥ 30 days)

#### Main Flow

1. **Collect:** Fetch total facility power and IT equipment power dari metrics (hourly)
2. **Calculate:** PUE = total_power / it_power
3. **Rate:** Assign PUE rating:
   - < 1.2 → exceptional
   - 1.2–1.4 → good
   - 1.4–1.6 → average
   - 1.6–2.0 → poor
   - > 2.0 → critical
4. **Overhead:** Calculate overhead_power = total - IT, overhead_pct = overhead / total
5. **Cost:** Calculate annual_cost_impact (if electricity rate available)
6. **Store:** Write PUE record ke `energy_pue` table
7. **Alert:** If PUE > 1.6 → alert Facilities Team
8. **Emit:** Publish to Kafka topic `dcim.analytics.energy`

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/energy/pue` | analytics.read | Get current PUE calculation |
| GET | `/api/v1/analytics/energy/pue/history` | analytics.read | Historical PUE trend |
| GET | `/api/v1/analytics/energy/overview` | analytics.read | Energy overview (PUE + cooling + power) |

#### SLA

| Dimension | Target |
|-----------|--------|
| Calculation latency | < 30s per calculation |
| Availability | 99.9% |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (both power values present) |
| Accuracy | PUE = total/it (exact division) |
| Timeliness | Hourly freshness |
| Consistency | Same time range = same PUE |
| Validity | PUE > 1.0 (physical constraint) |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| Energy Dashboard | PUE visualization | < 5s |
| Facilities Team | Optimization decisions | Hourly |
| LLM/RAG Service | PUE explanation | < 5s |

#### Acceptance Criteria

- ✅ PUE calculated hourly dengan formula total/IT
- ✅ PUE rating assigned (exceptional, good, average, poor, critical)
- ✅ Overhead percentage calculated
- ✅ Historical PUE trend available
- ✅ Alert fires jika PUE > 1.6
- ✅ Annual cost impact calculated (if rate available)

---

### 8.2 UC19 — Cooling Optimization

**Objective:** Analyze cooling efficiency per zone dan generate optimization recommendations untuk mengurangi energy consumption.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Calculation** | Hourly |
| **Target** | Cooling Efficiency < 0.4 |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Energy Optimization Service | Processor | Analyzes cooling per zone |
| Facilities Team | Consumer | Implements recommendations |
| BMS/EPMS | Source | Temperature, humidity data |

#### Pre-conditions

- BMS zone temperature data available
- Cooling power metrics available
- Target temperature configured (22°C default)

#### Main Flow

1. **Collect:** Fetch zone temperatures and cooling power dari BMS metrics
2. **Calculate:** Cooling efficiency = cooling_power / IT_power per zone
3. **Analyze:** Identify zones with:
   - Temperature > 27°C → increase cooling needed
   - Temperature < 18°C → reduce cooling (wasted energy)
   - Imbalance > 15% between zones → rebalancing recommended
4. **Recommend:** Generate zone-specific recommendations:
   - "Zone A: increase cooling (current 29°C, target 22°C, estimated savings: 2.5 kW)"
   - "Zone B: reduce cooling (current 16°C, target 22°C, estimated savings: 1.5 kW)"
5. **Aggregate:** Calculate total estimated savings across all zones
6. **Store:** Write recommendations ke `energy_recommendations` table

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/energy/cooling` | analytics.read | Get cooling recommendations |
| GET | `/api/v1/analytics/energy/cooling/zones` | analytics.read | Zone-specific cooling data |
| POST | `/api/v1/analytics/energy/optimize` | analytics.write | Trigger optimization analysis |

#### SLA

| Dimension | Target |
|-----------|--------|
| Analysis latency | < 60s per calculation |

#### Acceptance Criteria

- ✅ Cooling efficiency calculated per zone
- ✅ Zone-specific recommendations generated
- ✅ Temperature imbalances detected
- ✅ Estimated savings calculated per recommendation
- ✅ Total estimated savings aggregated

---

### 8.3 UC20 — Power Distribution Analysis

**Objective:** Analyze power distribution across PDUs, racks, dan zones untuk identify load imbalances dan optimize power allocation.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Calculation** | Hourly |
| **Target** | Power Load Balance < 1.2 (max/avg ratio) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Energy Optimization Service | Processor | Analyzes power distribution |
| Facilities Team | Consumer | Reviews distribution reports |

#### Pre-conditions

- PDU power metrics available
- Rack-level power data available
- Zone-level aggregation available

#### Main Flow

1. **Collect:** Fetch PDU, rack, and zone power metrics
2. **Balance:** Calculate load balance ratio = max(pdu) / avg(pdu)
3. **Identify:** Find overloaded PDUs (> 80% capacity) and underutilized PDUs (< 20%)
4. **Carbon:** Calculate carbon intensity = CO2(kg) / IT_power(kWh)
5. **Recommend:** Generate rebalancing recommendations
6. **Report:** Store power distribution report

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/energy/power` | analytics.read | Power distribution report |
| GET | `/api/v1/analytics/energy/carbon` | analytics.read | Carbon intensity metrics |

#### SLA

| Dimension | Target |
|-----------|--------|
| Analysis latency | < 60s per calculation |

#### Acceptance Criteria

- ✅ Load balance ratio calculated (< 1.2 target)
- ✅ Overloaded PDUs identified (> 80% capacity)
- ✅ Underutilized PDUs identified (< 20%)
- ✅ Carbon intensity calculated
- ✅ Rebalancing recommendations generated

---

## 9. Model Training & Management Use Cases (UC21–UC23)

### 9.1 UC21 — Model Development Pipeline

**Objective:** End-to-end model training pipeline — data collection, feature engineering, training, evaluation, untuk ML models.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Pipeline Stages** | 9 stages (collection → monitoring) |
| **Schedule** | Weekly batch (configurable per model) |
| **Models** | Isolation Forest, LSTM, Prophet, Random Forest |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Data Engineer | Operator | Initiates and monitors training |
| Model Training Service | Processor | Executes training pipeline |
| Model Registry | Store | Receives trained models |
| Scoring Service | Consumer | Receives deployed models |

#### Pre-conditions

- Historical data available in TimescaleDB (≥ 90 days)
- Feature engineering code tested
- Training infrastructure available (4 vCPU, 16GB RAM, GPU optional)
- Model Registry (MinIO/S3) operational

#### Main Flow

1. **Collect:** Extract training data dari TimescaleDB (historical metrics, labels if supervised)
2. **Feature Engineering:** Transform raw metrics to features (normalization, aggregation, time features)
3. **Split:** Train/Validation/Test (70/15/15) — time-based split (no future leakage)
4. **Train:** Train model offline (CPU or GPU):
   - Isolation Forest: 100 estimators, contamination=0.01
   - LSTM: input_dim=features, hidden=64, output=1, epochs=50
   - Prophet: default params + seasonality=auto
   - Random Forest: n_estimators=100, max_depth=10
5. **Evaluate:** Calculate metrics — accuracy, precision, recall, F1, AUC-ROC
6. **Threshold:** If F1 > 0.80 → proceed to registry; else → alert, retry with different params
7. **Register:** Upload model artifact to Model Registry with metadata
8. **Version:** Semantic versioning (v1.2.3 increment)
9. **Notify:** Notify Data Engineer of training completion + results

#### Alternative Flows

- **A1:** F1 < 0.80 → try hyperparameter tuning (grid search, 5 iterations)
- **A2:** Training fails → log error, alert Data Engineer, skip deployment
- **A3:** GPU unavailable → fall back to CPU training (longer time)

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/analytics/models/train` | analytics.admin | Trigger model training |
| GET | `/api/v1/analytics/models/train/{job_id}` | analytics.read | Check training job status |
| GET | `/api/v1/analytics/models/train/history` | analytics.read | Training history |

#### SLA

| Dimension | Target |
|-----------|--------|
| Training completion | < 4 hours (full pipeline) |
| Model evaluation | < 30 min |
| Code coverage | ≥ 80% |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% features non-null |
| Accuracy | No data leakage (time-based split) |
| Timeliness | Training data ≤ 30 days old |
| Consistency | Same data + same params = same model |
| Validity | Feature ranges within expected bounds |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| Model Registry | Model storage | Real-time |
| Scoring Service | Model deployment | On-demand |
| Data Engineer | Training reports | On-demand |

#### Acceptance Criteria

- ✅ 9-stage pipeline end-to-end working
- ✅ Feature engineering produces valid features
- ✅ Time-based data split (no leakage)
- ✅ Model evaluation metrics (accuracy, precision, recall, F1, AUC-ROC) calculated
- ✅ Model registered dengan metadata dan artifact
- ✅ Training completion notification sent

---

### 9.2 UC22 — Model Versioning & Registry

**Objective:** Version control ML models dengan metadata, performance metrics, dan deployment status.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Storage** | Model Registry (MinIO/S3) + PostgreSQL metadata |
| **Versioning** | Semantic versioning (v1.2.3) |
| **Statuses** | registered → staging → production → archived |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Model Training Pipeline | Writer | Registers new models |
| Data Engineer | Manager | Manages model lifecycle |
| Scoring Service | Reader | Loads production models |

#### Pre-conditions

- Model Registry deployed (MinIO/S3 + PostgreSQL table `ml_models`)
- Model artifact storage configured
- Deployment pipeline tested

#### Main Flow

1. **Register:** Training pipeline creates model entry in `ml_models` table with status = "registered"
2. **Upload:** Model artifact uploaded to MinIO/S3 at `models/{model_name}/{version}/model.pkl`
3. **Metadata:** Record hyperparameters, features_used, training metrics
4. **Review:** Data Engineer reviews model performance
5. **Stage:** If approved → status = "staging" (deployed to staging scoring service)
6. **Validate:** Run validation tests on staging model
7. **Promote:** If validation passes → status = "production" (deployed to production scoring service)
8. **Archive:** If superseded by newer model → status = "archived"

#### Model Registry Schema

```sql
CREATE TABLE ml_models (
    model_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    trained_at TIMESTAMPTZ,
    training_data_size INTEGER,
    training_duration_seconds INTEGER,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc_roc DECIMAL(5,4),
    status VARCHAR(20) DEFAULT 'registered'
        CHECK (status IN ('registered', 'staging', 'production', 'archived')),
    deployed_at TIMESTAMPTZ,
    artifact_path VARCHAR(500),
    artifact_size_bytes BIGINT,
    hyperparameters JSONB,
    features_used JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/analytics/models` | analytics.read | List registered models |
| GET | `/api/v1/analytics/models/{id}` | analytics.read | Get model details |
| POST | `/api/v1/analytics/models` | analytics.admin | Register new model |
| PUT | `/api/v1/analytics/models/{id}/deploy` | analytics.admin | Deploy model |
| GET | `/api/v1/analytics/models/{id}/metrics` | analytics.read | Model performance |

#### SLA

| Dimension | Target |
|-----------|--------|
| Registration latency | < 5s |
| Deployment latency | < 10s |
| Artifact availability | 99.9% |

#### Acceptance Criteria

- ✅ Model versioned dengan semantic versioning
- ✅ Model artifact stored di MinIO/S3
- ✅ Metadata (hyperparameters, features, metrics) recorded
- ✅ Status lifecycle working (registered → staging → production → archived)
- ✅ Rollback capability available (deploy previous version)

---

### 9.3 UC23 — Model Deployment & Scoring

**Objective:** Deploy production models ke scoring service dan handle real-time/batch inference requests.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 500ms per prediction (Isolation Forest), < 10s (Prophet) |
| **A/B Testing** | Supported (traffic split between model versions) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Model Registry | Source | Provides model artifacts |
| Scoring Service | Processor | Loads and serves models |
| Anomaly Detection | Consumer | Calls scoring for Isolation Forest |
| Predictive Maintenance | Consumer | Calls scoring for LSTM, Prophet |
| Data Engineer | Operator | Manages deployments |

#### Pre-conditions

- Model Registry operational
- Scoring service deployed (2+ instances for HA)
- Model artifacts accessible from scoring service
- Health check endpoints configured

#### Main Flow

1. **Load:** Scoring service loads model artifact from Registry (in-memory)
2. **Warm-up:** Run 10 test predictions to warm cache
3. **Serve:** Handle inference requests:
   - Isolation Forest: < 500ms per prediction
   - LSTM: < 100ms per sequence
   - Prophet: < 10s per forecast
4. **A/B Test:** If A/B configured → split traffic between model versions
5. **Health Check:** Periodic health check (every 30s)
6. **Reload:** If new version deployed → hot-reload model artifact

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/analytics/models/{id}/predict` | analytics.write | Run prediction |
| GET | `/api/v1/analytics/models/score/status` | analytics.read | Scoring service health |
| PUT | `/api/v1/analytics/models/{id}/reload` | analytics.admin | Hot-reload model |

#### SLA

| Dimension | Target |
|-----------|--------|
| Isolation Forest latency | < 500ms per prediction |
| LSTM latency | < 100ms per sequence |
| Prophet latency | < 10s per forecast |
| Scoring availability | 99.9% |

#### Acceptance Criteria

- ✅ Model loaded in-memory, serving predictions
- ✅ Hot-reload on new version deployment
- ✅ A/B testing supported (configurable traffic split)
- ✅ Health check endpoint active
- ✅ Prediction latency within SLA per model type
- ✅ Model artifact integrity verified (checksum)

---

## 10. LLM/RAG Explanation Layer Use Cases (UC24–UC26)

### 10.1 UC24 — Natural Language Query

**Objective:** Answer natural language questions tentang metrics, anomalies, predictions, dan capacity using LLM + RAG retrieval.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5s per query (p99) |
| **LLM Backends** | GPT-4, Claude, Local LLM (configurable) |
| **RAG Sources** | CMDB, Logs, Runbooks, Historical, Metrics |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| NOC Operators | Query submitter | Asks questions via chat interface |
| DC Managers | Query submitter | Asks executive-level questions |
| LLM/RAG Service | Processor | Retrieves context, generates answer |

#### Pre-conditions

- LLM backend configured and accessible (API key or local model)
- RAG knowledge sources indexed:
  - CMDB: CI data, relationships, topology
  - Elasticsearch: Logs (dcim-logs-*)
  - Wiki: Runbooks, documentation (markdown files)
  - TimescaleDB: Recent metrics and trends
- Embedding model configured (for vector similarity search)
- Query history storage configured

#### Main Flow

1. **Receive:** User submits natural language query
2. **Classify:** Intent classification — what type of question?
   - Metric query → retrieve from TimescaleDB
   - Anomaly inquiry → retrieve from anomaly_events
   - Prediction inquiry → retrieve from predictions
   - Capacity question → retrieve from capacity forecasts
   - General question → retrieve from runbooks/docs
3. **Retrieve:** RAG retrieval from relevant sources:
   - CMDB context: CI info, relationships
   - Metric context: Recent values, trends
   - Log context: Related log entries
   - Runbook context: Relevant procedures
4. **Assemble:** Combine retrieved context into prompt
5. **Generate:** Call LLM with assembled context + user query
6. **Validate:** Check response for hallucination (verify facts against source)
7. **Cite:** Attach source citations to response
8. **Store:** Save query + response to history
9. **Return:** Return response with citations

#### Query Examples

```
User: "Why is web-server-01 showing high CPU?"

RAG Process:
1. Retrieve CI info: web-server-01 (CI-SERVER-001), owner: Platform Team
2. Retrieve metrics: cpu_usage = 95.5% (normal: 20-60%), rising since 14:00
3. Retrieve anomalies: 3 OOM kills in last hour
4. Retrieve runbooks: "Java Memory Troubleshooting" (Section 3.2)

Response: "web-server-01 (CI-SERVER-001) experiencing high CPU (95.5% vs normal 40%).
Timeline: CPU rising since 14:00. Correlated: 3 OOM kills in last hour.
Root cause hypothesis: Java application memory leak causing GC storms.
Action: Restart application service and review memory allocation.
Reference: Runbook 'Java Memory Troubleshooting' (Section 3.2)."
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/analytics/llm/query` | analytics.read | Ask natural language question |
| GET | `/api/v1/analytics/llm/context/{ci_id}` | analytics.read | Get context for CI |
| GET | `/api/v1/analytics/llm/history` | analytics.read | Query history |

#### SLA

| Dimension | Target |
|-----------|--------|
| Query latency | < 5s per query (p99) |
| Availability | 99.5% (degradation acceptable) |
| Throughput | 20 queries/min |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 90% queries answered |
| Accuracy | Facts verifiable against sources |
| Timeliness | < 5s response |
| Consistency | Same query = similar response |
| Validity | Citations present, no fabricated facts |

#### Downstream Consumers

| Consumer | Usage | Latency |
|----------|-------|---------|
| NOC Operators | Investigation support | < 5s |
| DC Managers | Executive insights | < 5s |
| Dashboard | Chat interface | < 5s |

#### Acceptance Criteria

- ✅ Natural language queries answered dengan contextual response
- ✅ RAG retrieval aktif (CMDB, logs, runbooks, metrics)
- ✅ Citations included dalam response
- ✅ Response latency < 5s p99
- ✅ Query history available
- ✅ Multiple LLM backends supported

---

### 10.2 UC25 — Explanation Generation

**Objective:** Generate natural language explanations untuk anomalies, predictions, dan capacity forecasts — menjelaskan "mengapa" dalam bahasa manusia.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5s per explanation |
| **Targets** | Anomalies, Predictions, Capacity Reports |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| NOC Operators | Consumer | Views explanations for alerts |
| LLM/RAG Service | Processor | Generates explanations |

#### Pre-conditions

- LLM backend operational
- Anomaly/Prediction/Capacity data available
- CMDB context accessible

#### Main Flow

1. **Receive:** Explanation request with entity type (anomaly/prediction/capacity) + entity_id
2. **Retrieve Data:** Fetch entity details (anomaly record, prediction record, etc.)
3. **Retrieve Context:** Fetch related CMDB data, metrics history, runbooks
4. **Template:** Select explanation template based on entity type:
   - **Anomaly:** "Metric X detected anomaly (score Y). Normal range: A-B. Current: C. Possible causes: [list]. Recommended: [list]."
   - **Prediction:** "CI X has Y% failure probability in Z days. Contributing factors: [list]. Recommended: [list]."
   - **Capacity:** "Resource X projected to reach 90% in Y days. Current: Z%. Recommendation: [list]."
5. **Enhance:** Pass template + context to LLM for natural language enhancement
6. **Cite:** Attach data sources as citations
7. **Return:** Return explanation with citations

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/analytics/llm/explain` | analytics.read | Explain anomaly/prediction |
| POST | `/api/v1/analytics/llm/explain/batch` | analytics.read | Batch explain (multiple entities) |

#### SLA

| Dimension | Target |
|-----------|--------|
| Explanation latency | < 5s per explanation |
| Batch latency | < 30s for 10 entities |

#### Acceptance Criteria

- ✅ Anomaly explanations generated (cause, impact, action)
- ✅ Prediction explanations generated (probability, factors, schedule)
- ✅ Capacity explanations generated (trend, projection, recommendation)
- ✅ Citations attached per explanation
- ✅ Batch explanation supported

---

### 10.3 UC26 — Knowledge Base Management

**Objective:** Manage RAG knowledge sources — indexing, updating, dan retrieval optimization untuk runbooks, documentation, dan historical incidents.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Sources** | Runbooks, Documentation, Historical Incidents |
| **Update** | On-change (wiki), Daily (incidents), Weekly (docs) |

#### Actors

| Actor | Role | Interaction |
|-------|------|-------------|
| Data Engineer | Manager | Manages knowledge sources |
| Wiki System | Source | Provides runbooks and docs |
| ITSM | Source | Provides historical incidents |

#### Pre-conditions

- Wiki pages accessible (markdown files)
- Elasticsearch indices populated
- Embedding model configured
- Knowledge base indexed

#### Main Flow

1. **Index Runbooks:** Parse markdown files → extract sections → generate embeddings → store in vector index
2. **Index Docs:** Parse documentation → extract sections → generate embeddings → store in vector index
3. **Index Incidents:** Daily batch — extract resolved incidents → generate embeddings → store
4. **Update:** On-change triggers re-indexing for modified files
5. **Optimize:** Periodic re-ranking of knowledge sources based on query relevance
6. **Cleanup:** Remove stale entries (deleted docs, archived incidents)

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/analytics/llm/knowledge/reindex` | analytics.admin | Trigger reindex |
| GET | `/api/v1/analytics/llm/knowledge/stats` | analytics.read | Knowledge base statistics |
| POST | `/api/v1/analytics/llm/knowledge/upload` | analytics.admin | Upload knowledge source |

#### SLA

| Dimension | Target |
|-----------|--------|
| Reindex latency | < 30 min (full reindex) |
| Incremental update | < 5 min |

#### Acceptance Criteria

- ✅ Runbooks indexed dan searchable
- ✅ Documentation indexed dan searchable
- ✅ Historical incidents indexed (daily batch)
- ✅ On-change re-indexing active
- ✅ Knowledge base statistics available (source count, embedding count)
- ✅ Stale entries cleaned up

---

## 11. Source System → Use Case Matrix

| Source System | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | UC10 | UC11 | UC12 | UC13 | UC14 | UC15 | UC16 | UC17 | UC18 | UC19 | UC20 | UC21 | UC22 | UC23 | UC24 | UC25 | UC26 |
|--------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|------|
| **DI&I Gateway (Kafka)** | ✅ | — | — | ✅ | ✅ | ✅ | — | — | — | — | — | — | — | — | — | — | — | ✅ | ✅ | ✅ | — | — | — | — | — | — |
| **Prometheus/NMS** | ✅ | — | ✅ | ✅ | ✅ | ✅ | — | ✅ | — | — | — | — | — | — | ✅ | ✅ | ✅ | — | — | — | — | — | — | ✅ | ✅ | — |
| **BMS/EPMS** | ✅ | — | ✅ | — | — | — | — | — | — | — | — | — | — | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — | ✅ | ✅ | — |
| **CMDB (Block 4)** | — | — | ✅ | — | — | — | — | ✅ | ✅ | — | — | ✅ | ✅ | ✅ | — | — | — | — | — | — | — | — | — | ✅ | ✅ | — |
| **Elasticsearch (Logs)** | — | — | ✅ | — | — | — | — | — | — | — | — | ✅ | — | — | — | — | — | — | — | — | — | — | — | ✅ | ✅ | — |
| **ITSM** | — | — | — | — | — | — | — | — | — | ✅ | ✅ | ✅ | — | — | — | — | — | — | — | — | — | — | — | — | — | ✅ |
| **Wiki (Runbooks)** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | ✅ | ✅ | ✅ |
| **Cloud APIs** | ✅ | — | ✅ | ✅ | — | — | — | ✅ | — | — | — | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | — | ✅ | — |
| **Manual Entry** | — | — | — | — | ✅ | — | ✅ | — | ✅ | — | — | — | — | — | — | — | — | — | — | — | ✅ | ✅ | ✅ | — | — | — |
| **TimescaleDB** | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | ✅ | ✅ | — |
| **MinIO/S3** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | ✅ | ✅ | ✅ | — | — | — |

**Legend:** ✅ = source digunakan, — = tidak digunakan

---

## 12. Data Type → Use Case Mapping

### 12.1 Metric Data

| Data Type | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC8 | UC15 | UC18 | UC19 | UC20 |
|-----------|-----|-----|-----|-----|-----|-----|-----|------|------|------|------|
| CPU usage % | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Memory usage % | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Disk usage % | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Network bandwidth | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | — |
| Power (kW) | ✅ | ✅ | ✅ | — | — | — | — | ✅ | ✅ | — | ✅ |
| Temperature (°C) | ✅ | ✅ | ✅ | — | ✅ | — | — | — | — | ✅ | — |
| Cooling power (kW) | ✅ | ✅ | ✅ | — | — | — | — | ✅ | ✅ | ✅ | — |
| PDU load (A) | ✅ | ✅ | ✅ | — | ✅ | — | — | — | — | — | ✅ |
| Disk health (S.M.A.R.T.) | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | — | — | — | — |

### 12.2 Event Data

| Data Type | UC4 | UC7 | UC12 | UC24 | UC25 |
|-----------|-----|-----|------|------|------|
| Anomaly events | ✅ | ✅ | ✅ | ✅ | ✅ |
| Prediction results | — | — | — | ✅ | ✅ |
| CMDB changes | — | — | ✅ | ✅ | ✅ |
| Log entries | — | — | ✅ | ✅ | — |
| Security events | — | — | ✅ | ✅ | — |
| Incident records | — | — | ✅ | ✅ | ✅ |

### 12.3 Model Data

| Data Type | UC21 | UC22 | UC23 | UC10 | UC11 |
|-----------|------|------|------|------|------|
| Training data | ✅ | — | — | — | — |
| Model artifacts | ✅ | ✅ | ✅ | — | — |
| Model metrics | ✅ | ✅ | — | ✅ | ✅ |
| Feature vectors | ✅ | — | ✅ | — | ✅ |
| Prediction outputs | — | — | ✅ | ✅ | ✅ |

---

## 13. API Requirements per Use Case

### 13.1 API Endpoint Summary

| Use Case | Endpoints | Method | Auth |
|----------|-----------|--------|------|
| UC1 (Metric Ingestion) | 2 | GET | analytics.read |
| UC2 (Storage & Compression) | 2 | GET, PUT | analytics.read, analytics.admin |
| UC3 (Query & Aggregation) | 4 | GET | analytics.read |
| UC4 (Real-Time Anomaly) | 4 | GET, POST, PUT | analytics.read, analytics.write, analytics.admin |
| UC5 (Threshold Alerting) | 3 | GET, PUT, POST | analytics.read, analytics.admin, analytics.write |
| UC6 (Pattern Recognition) | 2 | GET, POST | analytics.read, analytics.write |
| UC7 (FP Handling) | 3 | GET, POST | analytics.read, analytics.write, analytics.admin |
| UC8 (Failure Prediction) | 4 | GET, POST | analytics.read, analytics.write |
| UC9 (Schedule Optimization) | 3 | GET, POST, PUT | analytics.read, analytics.write |
| UC10 (Accuracy Monitoring) | 2 | GET | analytics.read |
| UC11 (Drift Detection) | 2 | GET | analytics.read |
| UC12 (Event Correlation) | 3 | GET, POST | analytics.read, analytics.write |
| UC13 (Dependency Mapping) | 2 | GET | analytics.read |
| UC14 (Hypothesis) | 2 | GET, POST | analytics.read, analytics.write |
| UC15 (Trend Analysis) | 3 | GET, POST | analytics.read, analytics.write |
| UC16 (Resource Projection) | 2 | GET | analytics.read |
| UC17 (Capacity Alerting) | 2 | GET, PUT | analytics.read, analytics.admin |
| UC18 (PUE) | 3 | GET | analytics.read |
| UC19 (Cooling) | 3 | GET, POST | analytics.read, analytics.write |
| UC20 (Power Dist.) | 2 | GET | analytics.read |
| UC21 (Model Training) | 3 | GET, POST | analytics.read, analytics.admin |
| UC22 (Model Registry) | 5 | GET, POST, PUT | analytics.read, analytics.admin |
| UC23 (Model Deployment) | 3 | GET, POST, PUT | analytics.read, analytics.write, analytics.admin |
| UC24 (NL Query) | 3 | GET, POST | analytics.read |
| UC25 (Explanation) | 2 | POST | analytics.read |
| UC26 (Knowledge Base) | 3 | GET, POST | analytics.read, analytics.admin |
| **Total** | **71** | — | — |

### 13.2 Performance Targets

| Operation | Target p99 | Target p50 | Throughput |
|-----------|-----------|-----------|------------|
| GET /analytics/metrics | < 100ms | < 20ms | 100 req/s |
| GET /analytics/anomalies | < 200ms | < 50ms | 50 req/s |
| POST /analytics/anomalies/detect | < 500ms | < 100ms | 100 req/s |
| GET /analytics/predictions | < 200ms | < 50ms | 50 req/s |
| POST /analytics/rca/analyze | < 30s | < 10s | 10 req/s |
| GET /analytics/capacity | < 200ms | < 50ms | 20 req/s |
| GET /analytics/energy/pue | < 100ms | < 20ms | 50 req/s |
| POST /analytics/llm/query | < 5s | < 2s | 20 req/s |
| POST /analytics/llm/explain | < 5s | < 2s | 20 req/s |
| POST /analytics/models/train | < 4 hours | — | 1 req/batch |

---

## 14. SLA & Latency Requirements

### 14.1 End-to-End Latency SLA

| Tier | Latency | Use Cases | Processing Mode |
|------|---------|-----------|-----------------|
| **Tier 1 (Real-time)** | < 1s | UC1 (Ingestion), UC4 (Anomaly Detection) | Stream processing |
| **Tier 2 (Near-RT)** | < 500ms | UC4 (Z-score), UC5 (Threshold), UC6 (Isolation Forest) | In-memory scoring |
| **Tier 3 (Interactive)** | < 5s | UC12 (RCA), UC13 (Topology), UC24 (LLM Query), UC25 (Explanation) | API + computation |
| **Tier 4 (Batch-Hourly)** | < 1 hour | UC18 (PUE), UC19 (Cooling), UC20 (Power) | Scheduled batch |
| **Tier 5 (Batch-Daily)** | < 4 hours | UC8 (Prediction), UC15 (Trend), UC16 (Projection), UC21 (Training) | Nightly batch |

### 14.2 Availability Targets

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| Time-series Ingestion | 99.9% | < 5 min | ≤ 5 min (WAL) |
| Anomaly Detection | 99.9% | < 30s (failover) | 0 (stateless) |
| TimescaleDB | 99.95% | < 30 min | ≤ 5 min |
| LLM/RAG Service | 99.5% | < 5 min | N/A |
| Model Training | 99.0% | < 1 hour | N/A (batch) |
| Model Registry (MinIO) | 99.9% | < 15 min | 0 (replicated) |

### 14.3 Capacity Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Ingestion throughput | ≥ 1000 metrics/sec | Baseline 430+, headroom for growth |
| Anomaly detection rate | 5000 checks/sec | Z-score (in-memory) |
| Active CIs covered | ≥ 5000 | All monitored CIs |
| Daily predictions | ≥ 5000 | All active CIs |
| Knowledge base docs | ≥ 100 | Runbooks + docs |
| API total throughput | ≥ 200 req/s | Aggregate across endpoints |

---

## 15. Data Quality Requirements per Use Case

### 15.1 Quality Dimensions by Priority

| Use Case | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| UC1 (P1) | ≥ 99% | Value numeric, timestamp valid | < 1s | Schema valid | metric_name non-empty |
| UC2 (P1) | 100% | Data unchanged after compression | < 1 min | Segmentby consistent | Config valid |
| UC3 (P1) | 100% | Aggregates match raw | < 1 min | Deterministic | Time range valid |
| UC4 (P1) | ≥ 98% | Z-score computation correct | < 500ms | Same metric = same score | Severity valid |
| UC5 (P1) | 100% | Threshold comparison correct | < 100ms | Same value = same alert | Threshold numeric |
| UC8 (P1) | ≥ 95% | F1 > 0.80 | Daily | Same CI = same pred | Probability 0.0–1.0 |
| UC12 (P1) | ≥ 95% | Timestamp correlation correct | < 30s | Same incident = same result | Timestamps valid |
| UC18 (P1) | 100% | PUE = total/IT exact | Hourly | Same range = same PUE | PUE > 1.0 |
| UC24 (P1) | ≥ 90% | Facts verifiable | < 5s | Similar response | Citations present |
| UC22 (P1) | 100% | Artifact integrity | < 5s | Version unique | Version format valid |

### 15.2 Data Quality Rules

| Rule | Description | Action | Severity |
|------|-------------|--------|----------|
| DQ-TS-01 | Metric value must be numeric | Reject + DLQ | Critical |
| DQ-TS-02 | Timestamp must be valid ISO 8601 | Reject + DLQ | Critical |
| DQ-TS-03 | Metric name must be non-empty | Reject + DLQ | Critical |
| DQ-TS-04 | Source must be valid system identifier | Reject + DLQ | Critical |
| DQ-AD-01 | Anomaly score must be 0.0–1.0 | Clamp to range | High |
| DQ-AD-02 | Severity must be valid enum | Default to 'medium' | High |
| DQ-PM-01 | Failure probability must be 0.0–1.0 | Clamp to range | High |
| DQ-PM-02 | Confidence must be 0.0–1.0 | Clamp to range | High |
| DQ-PM-03 | Prediction window must be valid | Reject + alert | High |
| DQ-RCA-01 | Incident ID must be valid UUID | Reject + alert | Critical |
| DQ-RCA-02 | Timeframe must be 1–1440 minutes | Clamp to range | Medium |
| DQ-LLM-01 | Query length must be 10–5000 chars | Reject with message | Medium |
| DQ-LLM-02 | Response must include source count | Append warning | Low |
| DQ-MOD-01 | Model version must follow semver | Reject + alert | Critical |
| DQ-MOD-02 | Training data size must be > 1000 | Reject + alert | High |

---

## 16. Downstream Consumer Mapping

| Consumer | Input UCs | Required Fields | Output | Latency |
|----------|-----------|-----------------|--------|---------|
| **NOC Dashboard** | UC4, UC5, UC8, UC12, UC18 | anomaly_id, severity, metric_name, ci_id | Real-time alerts, PUE | < 5s |
| **Workflow Automation (Block 8)** | UC4, UC8, UC17 | anomaly_id, prediction_id, ci_id, severity | Remediation triggers | < 5s |
| **DC Managers** | UC8, UC15, UC16, UC18 | risk_level, exhaustion_date, PUE, cost | Executive reports | < 5s |
| **IT Operations** | UC8, UC9, UC12, UC14 | prediction_id, schedule, hypotheses | Maintenance plans | < 30s |
| **Facilities Team** | UC18, UC19, UC20 | PUE, cooling_efficiency, power_balance | Energy reports | Hourly |
| **SIEM/SOC (Block 6)** | UC4, UC12 | anomaly_id, ci_id, correlated_events | Security correlation | < 5s |
| **ITSM** | UC8, UC12, UC14 | prediction, incident_rca, hypotheses | Ticket enrichment | < 30s |
| **Grafana Dashboard** | UC1, UC3, UC4, UC18 | metrics, anomalies, PUE | Visualizations | < 5s |
| **LLM/RAG Service** | UC4, UC8, UC12, UC15, UC18 | entity data, context | Natural language | < 5s |
| **Model Training Pipeline** | UC10, UC11 | accuracy metrics, drift scores | Retraining triggers | Weekly |
| **BI Tools** | UC3, UC8, UC15, UC18 | aggregated metrics, forecasts | Reports | Batch |
| **Compliance** | UC1, UC4, UC8 | audit trail, anomaly log | Compliance reports | Batch |

---

## 17. FIT041 Requirements Checklist

> Source: IF-Technical_Requirements_Analytics_AI_Engine-FIT041-20260119.md

| # | Requirement Type | FIT041 Requirement | Aligned UCs | Status |
|---|-----------------|---------------------|-------------|--------|
| 1 | Data Processing | Data ingestion (structured, semi, unstructured) | UC1 (Time-Series Pipeline) | ⚠️ Partial — DCIM-Wiki focuses on time-series, FIT041 also expects unstructured |
| 2 | Data Processing | Data Lake architecture (raw, processed, feature/embedding) | UC2 (Storage), UC21 (Training) | ⚠️ Partial — DCIM-Wiki uses TimescaleDB only, no explicit Data Lake |
| 3 | Data Processing | Data retention by type and importance | UC2 (Compression & Retention) | ✅ Covered — 90 days configurable retention |
| 4 | Predictive Analytics | Capacity forecasting (CPU, GPU, Memory, Storage, Network) | UC15 (Trend), UC16 (Projection), UC17 (Alerting) | ✅ Covered — 7 resources, 4 models |
| 5 | Predictive Analytics | Failure prediction (early warning, risk downtime) | UC8 (Failure Prediction), UC9 (Schedule) | ✅ Covered — LSTM, Prophet, 4 models |
| 6 | Predictive Analytics | Optimization recommendations | UC9 (Schedule), UC19 (Cooling), UC20 (Power) | ✅ Covered — Maintenance + Energy optimization |
| 7 | Anomaly & RCA | Anomaly detection (rule-based, statistical, ML) | UC4 (Z-score), UC5 (Threshold), UC6 (Isolation Forest) | ✅ Covered — 4 detection methods |
| 8 | Anomaly & RCA | Event correlation for RCA | UC12 (Correlation), UC13 (Topology), UC14 (Hypothesis) | ✅ Covered — 6-step RCA pipeline |
| 9 | Performance | Low-latency queries | UC3 (Query, <100ms), UC24 (LLM, <5s) | ✅ Covered — 5 SLA tiers |
| 10 | Performance | Model training (GPU, batch, parallel) | UC21 (Training Pipeline) | ✅ Covered — 9-stage pipeline, GPU optional |
| 11 | Performance | Scalability (vertical + horizontal) | UC1 (2-6 instances), UC4 (2-8 instances) | ✅ Covered — Auto-scaling per component |
| 12 | Reliability | High availability (redundancy, failover) | All UCs (HA requirements) | ✅ Covered — 99.9% for critical services |
| 13 | Reliability | Data quality (validation, detection, logging) | UC7 (FP Handling), DQ Rules | ✅ Covered — 15 DQ rules |
| 14 | Security | Data segmentation (tenant isolation) | All UCs | ⚠️ Partial — DCIM-Wiki assumes single-tenant |
| 15 | Security | API security (auth, rate limiting, audit) | All UCs (RBAC) | ✅ Covered — 3 RBAC roles |
| 16 | Architecture | 6-layer architecture | Architecture overview | ✅ Covered — 6 layers match |
| 17 | Tech Stack | Technology selection | System Requirements | ✅ Covered — Specific stack chosen (Kafka/Flink/TS) |
| 18 | Integration | DI&I, CMDB, Monitoring, Workflow, ITSM, Dashboard | UC1, UC4, UC12, UC15, UC18 | ✅ Covered — 10 integration points |
| 19 | Dashboard | Operational + Executive dashboard | UC1, UC3, UC18 | ✅ Covered — 5 dashboards |
| 20 | API | REST API with documentation | All UCs (24 endpoints) | ✅ Covered — 24 endpoints, OpenAPI 3.0 |

**Kesimpulan:** Dari 20 FIT041 requirements:
- **17 fully covered** (85%)
- **3 partially covered** (15%): unstructured data (P3), Data Lake (P3), tenant isolation (P3)
- **0 not covered** (0%)

---

## 18. Gaps & Recommendations

### 18.1 Identified Gaps

| # | Gap | Impact | Priority | Recommendation |
|---|-----|--------|----------|----------------|
| 1 | Unstructured data ingestion (PDF, DOCX) tidak ada | LLM/RAG knowledge base terbatas | **P3** | Pertimbangkan unstructured parser untuk runbooks dalam format non-markdown |
| 2 | Data Lake architecture tidak ada (Raw/Processed/Feature separation) | ML pipeline data management | **P3** | Pertimbangkan data lake untuk advanced feature engineering |
| 3 | Vector database (FAISS/Qdrant) tidak ada | LLM/RAG semantic search performance | **P3** | Evaluasi apakah TimescaleDB full-text search cukup atau perlu vector DB |
| 4 | Tenant isolation tidak ada | Multi-organization support | **P3** | Konfirmasi single-tenant assumption; jika multi-tenant, tambah isolation |
| 5 | Spark/Dask tidak ada (hanya Flink/Python) | Distributed batch processing | **P4** | Python sufficient untuk Phase 1; Spark menjadi future consideration |
| 6 | Proxmox tidak ada (Docker/K8s) | On-prem VM management | **P4** | Docker/K8s sufficient; Proxmox menjadi infrastructure choice di luar scope |
| 7 | A/B testing framework belum ada | Model comparison capability | **P3** | Pertimbangkan A/B testing untuk model version comparison |

### 18.2 Recommendations

| # | Recommendation | Rationale | Effort |
|---|---------------|-----------|--------|
| 1 | Pertahankan DCIM-Wiki sebagai implementation spec | Lebih komprehensif dari FIT041 | — |
| 2 | Gunakan FIT041 sebagai validasi requirements | Cross-check coverage | 1 day |
| 3 | Evaluasi Vector DB untuk LLM/RAG (Phase 2) | Jika TimescaleDB full-text insufficient | 5 days |
| 4 | Tambah unstructured parser untuk runbooks (Phase 2) | Enhance knowledge base | 3 days |
| 5 | Evaluasi Spark untuk large-scale ETL (Phase 3) | Jika data volume exceeds Python capacity | 10 days |
| 6 | Konfirmasi tenant isolation requirement | Architecture decision | 0.5 day |
| 7 | Pertahankan Kafka sebagai primary messaging | Proven, scalable, integrated | — |

### 18.3 Tidak Perlu Diubah

| Item | Reason |
|------|--------|
| Block 7 Reference Design | Sudah komprehensif dengan 14 sections |
| Block 7 Technical Requirements | Sudah memiliki 32 FR, 24 API, 32 acceptance criteria |
| TimescaleDB sebagai time-series store | Proven, integrated, compression support |
| Kafka sebagai messaging layer | Proven, HA, exactly-once semantics |
| LLM/RAG architecture | Sudah ada dengan multi-backend support |
| Energy Optimization module | Sudah ada sebagai dedicated module (unique ke DCIM-Wiki) |
| RCA Engine | Sudah ada dengan 6-step pipeline (FIT041 missing) |

---

## 19. Acceptance Criteria

### 19.1 Per Use Case

| Use Case | Acceptance Criteria |
|----------|-------------------|
| **UC1** | ✅ Kafka topic `dcim.analytics.metrics` menerima ≥ 1000 metrics/sec<br>✅ Stream Processor memproses tanpa consumer lag > 1000<br>✅ Metrics queryable di TimescaleDB dalam < 1s<br>✅ Late events (5 min) terproses dengan benar<br>✅ Failed messages route ke DLQ |
| **UC2** | ✅ Hypertable terbentuk dengan auto-partitioning<br>✅ Data > 7 hari ter-compress (> 50% reduction)<br>✅ Data > 90 hari ter-drop otomatis<br>✅ Continuous aggregates refreshed < 1 min lag<br>✅ Backup full daily + WAL archiving aktif |
| **UC3** | ✅ 1-hour range query < 100ms p99<br>✅ 1-day range query < 200ms p99<br>✅ Aggregates queryable (hourly, daily)<br>✅ Cache hit rate > 60%<br>✅ 100 concurrent connections handled |
| **UC4** | ✅ Z-score detection menangkap threshold violations (Z > 3.0)<br>✅ Detection latency < 500ms per event<br>✅ Severity classification: low, medium, high, critical<br>✅ Anomaly score dalam 0.0–1.0<br>✅ Deduplication aktif (30-min window) |
| **UC5** | ✅ Static threshold checks < 100ms<br>✅ Rate-of-change detection aktif<br>✅ Sustained threshold alerts (5 min) working<br>✅ Thresholds updateable via API<br>✅ Configurable per-metric dan per-CI |
| **UC6** | ✅ Isolation Forest scoring < 500ms<br>✅ Multi-metric anomalies terdeteksi<br>✅ Feature importance untuk explainability<br>✅ Cross-reference dengan Z-score aktif |
| **UC7** | ✅ FP feedback mechanism available<br>✅ FP rate < 10% setelah tuning<br>✅ Seasonal decomposition aktif<br>✅ Tuning recommendations auto-generated |
| **UC8** | ✅ Daily batch ≥ 95% CIs covered<br>✅ Failure probability dalam 0.0–1.0<br>✅ Contributing factors dengan weights<br>✅ Maintenance window calculated<br>✅ Predictions terpublish ke Kafka |
| **UC9** | ✅ Schedule generated untuk risk >= medium<br>✅ Constraints respected<br>✅ De-confliction aktif<br>✅ Grouping per location |
| **UC10** | ✅ Weekly evaluation menghasilkan P, R, F1, AUC-ROC<br>✅ Accuracy alert fires jika F1 < 0.80<br>✅ Retraining triggered otomatis |
| **UC11** | ✅ PSI computed per feature<br>✅ Drift score dalam 0.0–1.0<br>✅ Alert fires jika drift > 0.15 (7 hari) |
| **UC12** | ✅ Timeline reconstructed dari ≥ 3 sources<br>✅ Correlation complete < 30s<br>✅ Events dikluster dengan benar<br>✅ Correlation accuracy > 90% |
| **UC13** | ✅ Upstream dependencies identified<br>✅ Downstream impacts identified<br>✅ Traversal depth configurable<br>✅ Cache hit rate > 80% |
| **UC14** | ✅ ≥ 3 hypotheses generated<br>✅ Ranked by confidence<br>✅ Each has cause, confidence, evidence<br>✅ Recommended actions attached |
| **UC15** | ✅ 7 resource types analyzed<br>✅ Model selection otomatis<br>✅ 30-day forecast dengan CI 95%<br>✅ MAPE < 10%<br>✅ Results ke Kafka + dashboard |
| **UC16** | ✅ Exhaustion dates calculated<br>✅ Days until 90% accurate<br>✅ Recommendations generated<br>✅ Cost impact included |
| **UC17** | ✅ Capacity alerts fire saat projected > threshold<br>✅ 3 severity levels<br>✅ Deduplication aktif (7 hari)<br>✅ Thresholds configurable |
| **UC18** | ✅ PUE calculated hourly<br>✅ PUE rating assigned<br>✅ Overhead percentage calculated<br>✅ Historical trend available<br>✅ Alert fires jika PUE > 1.6 |
| **UC19** | ✅ Cooling efficiency per zone<br>✅ Zone-specific recommendations<br>✅ Temperature imbalances detected<br>✅ Estimated savings calculated |
| **UC20** | ✅ Load balance ratio calculated<br>✅ Overloaded PDUs identified<br>✅ Carbon intensity calculated<br>✅ Rebalancing recommendations |
| **UC21** | ✅ 9-stage pipeline end-to-end<br>✅ Feature engineering produces valid features<br>✅ Time-based split (no leakage)<br>✅ Evaluation metrics calculated<br>✅ Model registered dengan metadata |
| **UC22** | ✅ Semantic versioning working<br>✅ Artifact stored di MinIO/S3<br>✅ Metadata recorded<br>✅ Status lifecycle working<br>✅ Rollback available |
| **UC23** | ✅ Model loaded in-memory<br>✅ Hot-reload on deployment<br>✅ A/B testing supported<br>✅ Health check active<br>✅ Latency within SLA |
| **UC24** | ✅ NL queries answered dengan contextual response<br>✅ RAG retrieval aktif (4 sources)<br>✅ Citations included<br>✅ Response < 5s p99<br>✅ History available |
| **UC25** | ✅ Anomaly explanations generated<br>✅ Prediction explanations generated<br>✅ Capacity explanations generated<br>✅ Citations attached<br>✅ Batch explanation supported |
| **UC26** | ✅ Runbooks indexed<br>✅ Docs indexed<br>✅ Incidents indexed (daily)<br>✅ On-change re-indexing active<br>✅ Stats available |

### 19.2 Cross-Cutting

| Criteria | Target |
|----------|--------|
| Total ingestion throughput | ≥ 1000 metrics/sec |
| Anomaly detection latency | < 500ms (p99) |
| RCA analysis latency | < 30s (p99) |
| LLM query latency | < 5s (p99) |
| Model accuracy (F1) | > 0.80 |
| Model drift alert | > 0.15 for 7 days |
| PUE target | < 1.4 |
| False positive rate | < 10% |
| Knowledge base coverage | ≥ 100 documents |
| API availability | 99.9% |
| Data completeness (P1 UCs) | ≥ 95% |
| DQ rule compliance | 100% (all rules enforced) |

---

## 20. Traceability Matrix

| DCIM-Wiki UC | FIT041 Equivalent | Merge Type | Enhanced With |
|-------------|-------------------|------------|---------------|
| UC1 Metric Ingestion | FIT041 §2.1.1 (Data Ingestion) | **Mapped** | Kafka topics, TimescaleDB hypertable, DLQ strategy |
| UC2 Storage & Compression | FIT041 §2.1.3 (Data Retention) | **Mapped** | Compression policy, retention policy, continuous aggregates |
| UC3 Query & Aggregation | FIT041 §2.1.2 (Data Lake/Warehouse) | **Mapped** | Cache strategy, query optimization, aggregate views |
| UC4 Real-Time Anomaly | FIT041 §2.3.1 (Anomaly Detection) | **Mapped** | Z-score implementation, severity classification, deduplication |
| UC5 Threshold Alerting | FIT041 §2.3.1 (Rule-based) | **Mapped** | Static/dynamic/rate thresholds, per-metric config |
| UC6 Pattern Recognition | FIT041 §2.3.1 (ML-based) | **Mapped** | Isolation Forest, multi-variate, feature importance |
| UC7 FP Handling | FIT041 §3.2.2 (Data Quality) | **Mapped** | Feedback loop, seasonal decomposition, auto-tuning |
| UC8 Failure Prediction | FIT041 §2.2.2 (Failure Prediction) | **Mapped** | LSTM, Prophet, ensemble, contributing factors |
| UC9 Schedule Optimization | FIT041 §2.2.3 (Optimization) | **Mapped** | Constraint-based scheduling, de-confliction, grouping |
| UC10 Accuracy Monitoring | FIT041 §3.2.2 (Data Quality) | **Mapped** | Weekly evaluation, accuracy alert, auto-retrain trigger |
| UC11 Drift Detection | FIT041 §3.2.2 (Data Quality) | **Mapped** | PSI-based drift, feature-level breakdown, retrain trigger |
| UC12 Event Correlation | FIT041 §2.3.2 (Event Correlation) | **Mapped** | Multi-source correlation, timeline reconstruction, clustering |
| UC13 Dependency Mapping | FIT041 §2.3.2 (Topology) | **Mapped** | CMDB traversal, upstream/downstream, dependency scoring |
| UC14 Automated RCA | FIT041 §2.3.2 (RCA) | **Mapped** | Hypothesis generation, Bayesian scoring, recommended actions |
| UC15 Trend Analysis | FIT041 §2.2.1 (Capacity Forecasting) | **Mapped** | Prophet, ARIMA, 7 resources, 30/365-day horizons |
| UC16 Resource Projection | FIT041 §2.2.1 (Capacity Planning) | **Mapped** | Exhaustion dates, recommendations, cost impact |
| UC17 Capacity Alerting | FIT041 §2.2.1 (Threshold) | **Mapped** | 3 severity levels, deduplication, workflow trigger |
| UC18 PUE Calculation | — (FIT041 missing) | **DCIM-Wiki unique** | PUE formula, rating, cost impact, alerting |
| UC19 Cooling Optimization | — (FIT041 missing) | **DCIM-Wiki unique** | Zone-specific, temperature analysis, savings |
| UC20 Power Distribution | — (FIT041 missing) | **DCIM-Wiki unique** | Load balance, carbon intensity, PDU analysis |
| UC21 Model Training | FIT041 §3.1.2 (Model Training) | **Mapped** | 9-stage pipeline, feature engineering, evaluation |
| UC22 Model Registry | FIT041 §3.1.2 (Model Management) | **Mapped** | Semantic versioning, artifact storage, lifecycle |
| UC23 Model Deployment | FIT041 §3.1.2 (Model Deployment) | **Mapped** | Hot-reload, A/B testing, health check |
| UC24 NL Query | — (FIT041 missing) | **DCIM-Wiki unique** | RAG retrieval, multi-source, citations |
| UC25 Explanation Generation | — (FIT041 missing) | **DCIM-Wiki unique** | Template + LLM, batch support |
| UC26 Knowledge Base | — (FIT041 missing) | **DCIM-Wiki unique** | Runbooks, docs, incidents indexing |

### Coverage Summary

| Category | FIT041 Items | Covered | Partial | Missing |
|----------|-------------|---------|---------|---------|
| Data Processing | 3 | 1 | 2 | 0 |
| Predictive Analytics | 3 | 3 | 0 | 0 |
| Anomaly & RCA | 2 | 2 | 0 | 0 |
| Performance | 3 | 3 | 0 | 0 |
| Reliability | 2 | 2 | 0 | 0 |
| Security | 2 | 1 | 1 | 0 |
| Architecture | 1 | 1 | 0 | 0 |
| Tech Stack | 1 | 1 | 0 | 0 |
| Integration | 1 | 1 | 0 | 0 |
| Dashboard/API | 2 | 2 | 0 | 0 |
| **Total** | **20** | **17 (85%)** | **3 (15%)** | **0 (0%)** |

---

## References

- [[IF-Technical_Requirements_Analytics_AI_Engine-FIT041-20260119]] — FIT041 Technical Requirements (source)
- [[block7-analytics-ai-engine]] — Reference Design Spec
- [[block7-analytics-ai-engine-technical-requirements]] — Technical Requirements
- [[fit041-analytics-ai-komparasi]] — FIT041 vs DCIM-Wiki comparison
- [[analytics-ai-engine]] — Entity page
- [[cmdb]] — CI topology for RCA
- [[data-ingestion-integration]] — Metric streams (DI&I)
- [[web-dashboard]] — Visualization (Grafana)
- [[workflow-automation]] — Alert workflows (Block 8)
- [[time-series-db-comparison]] — TimescaleDB selection
- [[ml-framework-comparison]] — ML framework selection
- [[llm-rag-explanation-layer]] — LLM/RAG architecture
- [[capacity-planning-runbook]] — Capacity procedures
- [[energy-optimization-strategy]] — Energy strategy
- [[dcim-core-platform]] — Platform overview

---

> **Status:** Final — Merged dari FIT041 + DCIM-Wiki Reference Design + Technical Requirements
> **Date:** 2026-06-25
> **Purpose:** Use Case Analysis final untuk Analytics & AI Engine (Block 7) — 26 use cases across 8 kategori
> **Method:** MCP Sequential Thinking + dcim-comparison skill + document alignment
> **FIT041 Requirements:** 20 requirements → 26 use cases (85% fully covered, 15% partial)
> **Phase 2 Progress:** B5 ✅ → B6 ✅ → B7 ✅ → B8 ⬜ → B9 ⬜
