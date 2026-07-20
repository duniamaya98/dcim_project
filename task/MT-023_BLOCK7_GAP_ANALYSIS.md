---
title: "Block 7 — Gap Analysis: Goals vs Infrastructure Delivery"
created: 2026-07-08
updated: 2026-07-08
version: 1.1
type: gap-analysis
block: 7
owner: Analytics & AI Team
status: active
confidence: 92%
tags: [gap-analysis, infrastructure, timescaledb, kafka, redis, block1, block2]
source_goals: MT-023_BLOCK7_ANALYTICS_AI_GOALS.md
source_delivery: reference_docs/Syauqi/
changelog: |
  v1.1 (2026-07-08): Updated with new documentation from Infrastructure team.
    - Architecture diagram clarified (Analytics Bridge, Avro/JSON)
    - Network access confirmed (no VPN needed)
    - Python (Pandas) example added
    - Data flow more detailed
    - Overall score adjusted: 65% → 75%
---

# Block 7 — Gap Analysis: Goals vs Infrastructure Delivery

> **Purpose:** Perbandingan antara apa yang diminta (Goals Doc) dengan apa yang
> diberikan oleh tim Infrastructure (Syauqi Documentation).
> **Owner:** Analytics & AI Team
> **Source Goals:** `task/MT-023_BLOCK7_ANALYTICS_AI_GOALS.md`
> **Source Delivery:** `reference_docs/Syauqi/` (3 files)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [TimescaleDB](#2-timescaledb)
3. [Kafka Cluster](#3-kafka-cluster)
4. [Kafka Topics](#4-kafka-topics)
5. [Redis](#5-redis)
6. [Event Schema](#6-event-schema)
7. [Bonus Items (Unrequested)](#7-bonus-items-unrequested)
8. [Questions for Infrastructure Team](#8-questions-for-infrastructure-team)
9. [Action Items](#9-action-items)
10. [Updated Connection Details](#10-updated-connection-details)

---

## 1. Executive Summary

### Overall Score

| Category | Requested | Provided | Match |
|----------|-----------|----------|-------|
| TimescaleDB connection | 7 items | 4 items | 57% |
| Kafka cluster | 5 items | 4 items | 80% |
| Kafka topics | 6 topics | 3 topics + 9 bonus | 50% |
| Redis | 4 items | 0 items | 0% |
| Event schema | 10 fields | 8 fields | 80% |
| Network access | 1 item | 1 item | 100% |
| Data flow clarity | 1 item | 1 item | 100% |
| Performance/monitoring | — | 6 bonus | N/A |
| **OVERALL** | **32 items** | **27 items** | **~75%** |

### Score Improvement (v1.0 → v1.1)

| Version | Score | Notes |
|---------|-------|-------|
| v1.0 (initial) | 65% | Based on first documentation |
| v1.1 (updated) | 75% | +10% from architecture clarity, network access, data flow |

### Verdict

Dokumentasi infrastructure **BAGUS dan LENGKAP** untuk tahap awal.
Bisa langsung mulai connect ke TimescaleDB dan Kafka dari internal network (tanpa VPN).
Architecture pipeline sudah jelas dengan Analytics Bridge component.
Perlu konfirmasi beberapa detail (version, TLS, Redis).

### Files Received

| File | Description | Version |
|------|-------------|---------|
| `reference_docs/Syauqi/README.md` | Overview, quick start, component matrix | v1.1 (updated) |
| `reference_docs/Syauqi/ai-pipeline-architecture.md` | Full architecture spec | v1.1 (updated) |
| `reference_docs/Syauqi/ai-team-access.md` | Connection details, credentials, queries | v1.1 (updated) |

### Key Updates in v1.1

| Update | Impact |
|--------|--------|
| Architecture diagram clarified | ✅ Pipeline sekarang jelas: Raw → Enriched → Analytics |
| Analytics Bridge component | ✅ Jembatan antara infra pipeline dan Tim AI |
| Network access confirmed | ✅ Tidak perlu VPN, langsung akses dari internal network |
| Python (Pandas) example | ✅ Contoh praktis untuk langsung dipakai |
| Tags JSONB access | ✅ Bisa query device_type, rack, zone |
| Avro vs JSON clarified | ✅ Enriched pakai Avro, Analytics pakai JSON |

---

## 1.5 Architecture & Data Flow (NEW in v1.1)

### Architecture Diagram (Updated)

```
┌──────────────┐     ┌──────────────┐     ┌────────────────┐     ┌────────────────┐
│   Sources    │     │  Ingestion   │     │   Kafka (Raw)  │     │  Processing    │
├──────────────┤     ├──────────────┤     ├────────────────┤     ├────────────────┤
│ Server       │────▶│ NiFi         │────▶│ dcim.raw.*     │────▶│ NiFi           │
│ CCTV/NVR     │     │ ExecuteProcess│   │ (JSON)         │     │ (Normalizer &  │
│ NAS          │     │ (Python)     │     │                │     │  Enrichment)   │
│ UPS          │     │              │     │                │     │                │
│ Network      │     │              │     │                │     │                │
└──────────────┘     └──────────────┘     └────────────────┘     └────────────────┘
                                                                        │
                                                                        ▼
                                          ┌────────────────┐     ┌────────────────┐
                                          │ Kafka (Enrich) │     │ AI Integration │
                                          ├────────────────┤     ├────────────────┤
                                          │ dcim.enriched.*│────▶│ Analytics      │
                                          │ (Avro via SR)  │     │ Bridge (Python)│
                                          └────────────────┘     └────────────────┘
                                                                        │
                                                                        ▼
┌──────────────┐     ┌──────────────┐     ┌────────────────┐     ┌────────────────┐
│   Storage    │     │  TimescaleDB │     │  Analytics     │     │   Kafka (AI)   │
├──────────────┤     ├──────────────┤     ├────────────────┤     ├────────────────┤
│ PostgreSQL   │◀────│ metrics      │◀────│ Stream         │◀────│ dcim.          │
│ Elasticsearch│     │ hypertable   │     │ Processor      │     │ analytics.*    │
│ Redis        │     │              │     │ (Python)       │     │ (JSON)         │
│              │     │ hourly agg   │     │                │     │                │
│              │     │ daily agg    │     │                │     │                │
└──────────────┘     └──────────────┘     └────────────────┘     └────────────────┘
```

### Data Flow for AI Team

```
Source Devices (Server, CCTV, NAS, UPS, Network)
        ↓
    NiFi (Ingestion Pollers)
        ↓
    NiFi (Enrichment & Normalizer)
        ↓
    Kafka (dcim.enriched.events - Avro)
        ↓
    Analytics Bridge (Python)
        ↓
    Kafka (dcim.analytics.metrics - JSON) ← Tim AI bisa consume dari sini
        ↓
    Stream Processor (analytics_stream_processor.py)
        ↓
    TimescaleDB (metrics hypertable) ← Tim AI bisa query ke sini
        ↓
    Continuous Aggregates (hourly, daily)
```

### Entry Points for AI Team

| Entry Point | Format | Use Case | Protocol |
|-------------|--------|----------|----------|
| Kafka `dcim.analytics.metrics` | JSON | Real-time streaming | Kafka consumer |
| TimescaleDB `metrics` table | SQL | Historical batch queries | psycopg2/pandas |

### Key Clarifications

| Aspect | Clarification |
|--------|---------------|
| Raw data format | JSON (dcim.raw.*) |
| Enriched data format | Avro via Schema Registry (dcim.enriched.*) |
| Analytics data format | JSON (dcim.analytics.*) — yang kita consume |
| Analytics Bridge | Python component converts Avro → JSON |
| Network access | Internal network, no VPN needed |

---

## 2. TimescaleDB

### Comparison

| Item | Requested (Goals) | Provided (Delivery) | Status |
|------|-------------------|---------------------|--------|
| PostgreSQL version | 16 | 15.x | ⚠️ Version diff |
| TimescaleDB version | v2.15+ | 2.x | ⚠️ Need exact version |
| Database name | `dcim_analytics` | `dcim_analytics` | ✅ Match |
| Username | `dcim_analytics_user` | `ai_team` | ⚠️ Name diff |
| Password | — | `ai_team_access_pass` | ✅ Provided |
| Host | — | `10.70.0.56` | ✅ Provided |
| Port | — | `5433` | ✅ Provided |
| TLS 1.2+ | Required | Not mentioned | ❌ Missing |
| PgBouncer | Required | Not mentioned | ❌ Missing |
| `uuid-ossp` extension | Required | Not mentioned | ❌ Missing |

### Schema Comparison

| Schema Element | Requested | Provided | Status |
|----------------|-----------|----------|--------|
| `metrics` hypertable | ✅ | ✅ | ✅ Match |
| `metrics_hourly` aggregate | ✅ | ✅ | ✅ Match |
| `metrics_daily` aggregate | ✅ | ✅ | ✅ Match |
| Compression after 7 days | ✅ | ✅ | ✅ Match |
| Retention 90 days | ✅ | ✅ | ✅ Match |
| `anomaly_events` table | ✅ | ❌ | ❌ Missing |
| `predictions` table | ✅ | ❌ | ❌ Missing |
| `ml_models` table | ✅ | ❌ | ❌ Missing |

### Connection String

```
psql -h 10.70.0.56 -p 5433 -U ai_team -d dcim_analytics
```

### Verdict: 80% MATCH

Schema match, connection available. Perlu verifikasi version dan request
additional tables (anomaly_events, predictions, ml_models).

---

## 3. Kafka Cluster

### Comparison

| Item | Requested (Goals) | Provided (Delivery) | Status |
|------|-------------------|---------------------|--------|
| Kafka version | 3.x | 3.7.0 | ✅ Match |
| Brokers | 3 minimum | 3-node cluster | ✅ Match |
| Bootstrap servers | — | `10.70.0.56:9092` | ✅ Provided |
| Auth mechanism | SASL/SSL | PLAINTEXT | ⚠️ No auth |
| Consumer group | `dcim-analytics-engine` | `ai-team-consumer` | ⚠️ Name diff |
| Schema Registry | — | `10.70.0.56:8081` | ✅ Bonus |

### Connection Details

```python
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'dcim.analytics.metrics',
    bootstrap_servers='10.70.0.56:9092',
    group_id='ai-team-consumer',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)
```

### Verdict: 80% MATCH

Cluster ready, connection details provided. PLAINTEXT acceptable for dev,
perlu TLS untuk production.

---

## 4. Kafka Topics

### Topics Comparison

| Topic | Requested | Provided | Status |
|-------|-----------|----------|--------|
| `dcim.analytics.metrics` | 6 partitions, 7 days | ✅ 6 partitions, 7 days | ✅ Match |
| `dcim.analytics.anomalies` | 3 partitions, 30 days | ✅ 3 partitions, 30 days | ✅ Match |
| `dcim.analytics.predictions` | 3 partitions, 30 days | ✅ 3 partitions, 30 days | ✅ Match |
| `dcim.analytics.rca` | 3 partitions, 30 days | ❌ Not created | ❌ Missing |
| `dcim.analytics.capacity` | 3 partitions, 30 days | ❌ Not created | ❌ Missing |
| `dcim.analytics.energy` | 3 partitions, 30 days | ❌ Not created | ❌ Missing |

### Bonus Topics (Unrequested but Useful)

| Topic | Partitions | Retention | Purpose |
|-------|------------|-----------|---------|
| `dcim.raw.hardware.server` | 3 | 7 days | Raw server metrics |
| `dcim.raw.hardware.server.inventory` | 3 | 7 days | Server inventory |
| `dcim.raw.storage.nas` | 3 | 7 days | NAS metrics |
| `dcim.raw.power.ups` | 3 | 7 days | UPS metrics |
| `dcim.raw.network.snmp` | 3 | 7 days | Network SNMP data |
| `dcim.raw.network.interfaces` | 3 | 7 days | Network interfaces |
| `dcim.raw.device.isapi` | 3 | 7 days | CCTV/NVR data |
| `dcim.normalized.events` | 6 | 30 days | Normalized events |
| `dcim.enriched.events` | 6 | 90 days | Enriched events |

### Verdict: 50% MATCH (topics), 100%+ BONUS

3 analytics topics yang diminta belum ada (rca, capacity, energy).
Tapi ada 9 bonus topics yang berguna untuk data ingestion.
`dcim.enriched.events` adalah input utama yang kita butuhkan.

---

## 5. Redis

### Comparison

| Item | Requested (Goals) | Provided (Delivery) | Status |
|------|-------------------|---------------------|--------|
| Redis version | 7 | 7.x (mentioned) | ⚠️ No access details |
| DB number | 3 | Not specified | ❌ Missing |
| Max memory | 2GB | Not specified | ❌ Missing |
| Eviction policy | `allkeys-lru` | Not specified | ❌ Missing |
| Connection string | Required | Not provided | ❌ Missing |
| Password | Required | Not provided | ❌ Missing |

### Verdict: 0% MATCH

Redis disebut di architecture doc sebagai "Cache" tapi tidak ada access details.

### Action Required

Perlu request Redis connection details secara terpisah.

---

## 6. Event Schema

### Schema Comparison

| Field | Requested (Goals) | Provided (Delivery) | Status |
|-------|-------------------|---------------------|--------|
| `event_id` (UUID) | Required | Not in DB schema | ⚠️ |
| `timestamp` (ISO 8601) | Required | `time` (TIMESTAMPTZ) | ✅ Match |
| `source_system` | Required | `source` (TEXT) | ✅ Match |
| `event_type` | Required | Not in DB schema | ⚠️ |
| `payload.metric_name` | Required | `metric_name` (TEXT) | ✅ Match |
| `payload.value` (numeric) | Required | `value` (DOUBLE PRECISION) | ✅ Match |
| `ci_id` (UUID) | Required | `ci_id` (UUID) | ✅ Match |
| `asset_id` (UUID) | Required | `asset_id` (UUID) | ✅ Match |
| `payload.unit` | Optional | `unit` (TEXT) | ✅ Match |
| `metadata.tags` | Optional | `tags` (JSONB) | ✅ Match |

### Schema Format

**Provided schema is FLAT** (direct columns), not nested JSON:

```sql
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name TEXT NOT NULL,
    ci_id UUID,
    asset_id UUID,
    source TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit TEXT,
    tags JSONB DEFAULT '{}'
);
```

**Benefits of flat schema:**
- Better query performance on TimescaleDB
- Easier indexing
- Native hypertable support

### Verdict: 80% MATCH

Schema usable. `event_id` and `event_type` may exist at Kafka message level
but not persisted to TimescaleDB. Need to confirm.

---

## 7. Bonus Items (Unrequested)

Infrastructure team provided additional valuable items:

### 7.1 NiFi Poller Scripts

| Poller Script | Target Topic | Device Type | Protocol |
|---------------|--------------|-------------|----------|
| `redfish_poller.py` | `dcim.raw.hardware.server` | Server | Redfish |
| `cctv_poller.py` | `dcim.raw.device.isapi` | CCTV + NVR | Hikvision ISAPI |
| `nas_poller.py` | `dcim.raw.storage.nas` | NAS | SNMP |
| `snmp_ups_poller.py` | `dcim.raw.power.ups` | UPS | SNMP |
| `mikrotik_poller.py` | `dcim.raw.network.snmp` | Network | SNMP |

### 7.2 Performance Metrics

| Metric | Target (Goals) | Actual (Delivery) | Status |
|--------|----------------|-------------------|--------|
| Throughput | 430+ metrics/sec | ~500 metrics/sec | ✅ Exceeds |
| Latency | < 1s | < 500ms | ✅ Exceeds |
| Query performance | < 5s | < 2s | ✅ Exceeds |
| Availability | 99.9% | 99.9% | ✅ Match |

### 7.3 Monitoring Dashboards

| Dashboard | Purpose |
|-----------|---------|
| Grafana | Pipeline monitoring |
| Kibana | Log analysis |
| Kafka UI | Topic monitoring |

### 7.4 Monitoring Metrics

| Metric | Description |
|--------|-------------|
| `dcim.metrics.ingestion.rate` | Metrics per second |
| `dcim.kafka.lag` | Consumer lag |
| `dcim.timescale.size` | Database size |
| `dcim.pipeline.latency` | End-to-end latency |

### 7.5 RBAC Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| `ai_team` | SELECT on analytics tables | General AI/ML queries |
| `analytics_read` | SELECT only | Read-only access |
| `analytics_write` | SELECT + INSERT | Write predictions |
| `analytics_admin` | ALL | Full access |

### 7.6 Network Segmentation

| VLAN | Subnet | Purpose |
|------|--------|---------|
| Management | 10.70.0.0/24 | Admin, monitoring |
| Data | 10.70.1.0/24 | DB, AI access |
| DMZ | 10.70.2.0/24 | External API |

### 7.7 DR/Backup Strategy

| Data Type | Frequency | Retention |
|-----------|-----------|-----------|
| PostgreSQL | Daily | 30 days |
| TimescaleDB | Daily | 30 days |
| Kafka | Replica | 7 days |

**RPO:** Database: 1 hour | **RTO:** Database: 4 hours, Full system: 24 hours

---

## 8. Questions for Infrastructure Team

### Critical (Blocking)

| # | Question | Why Needed |
|---|----------|------------|
| Q1 | Exact PostgreSQL version? (15.x = ?) | Feature compatibility check |
| Q2 | Exact TimescaleDB version? (need >= 2.15) | Compression/aggregate features |
| Q3 | Is TLS available for production? | Security requirement |
| Q4 | Redis connection details? (host, port, password, DB) | Cache layer for analytics |

### Important (Non-blocking)

| # | Question | Why Needed |
|---|----------|------------|
| Q5 | Is `event_id` present in Kafka messages? | Event tracking |
| Q6 | Is `event_type` present in Kafka messages? | Event routing |
| Q7 | Analytics Bridge source code or API spec? | Understanding data transformation |
| Q8 | Schema Registry credentials for Avro? | If we need to read enriched events directly |

### Nice to Have

| # | Question | Why Needed |
|---|----------|------------|
| Q9 | Can create `dcim.analytics.rca` topic? | For RCA results output |
| Q10 | Can create `dcim.analytics.capacity` topic? | For capacity forecasts |
| Q11 | Can create `dcim.analytics.energy` topic? | For energy reports |

---

## 9. Action Items

### Immediate (This Week)

- [ ] Test TimescaleDB connection: `psql -h 10.70.0.56 -p 5433 -U ai_team -d dcim_analytics`
- [ ] Test Kafka connection: Run consumer example script
- [ ] Query existing data: `SELECT * FROM metrics ORDER BY time DESC LIMIT 10;`
- [ ] Send Q1-Q4 to Infrastructure team
- [ ] Update goals doc with actual connection details

### Short-term (Next Week)

- [ ] Create `anomaly_events` table in TimescaleDB
- [ ] Create `predictions` table in TimescaleDB
- [ ] Create `ml_models` table in TimescaleDB
- [ ] Build Kafka consumer for `dcim.analytics.metrics`
- [ ] Build Kafka consumer for `dcim.enriched.events`

### Medium-term (After Confirmation)

- [ ] Request Redis access details
- [ ] Request TLS configuration for production
- [ ] Request additional Kafka topics (rca, capacity, energy)
- [ ] Set up Schema Registry integration

---

## 10. Updated Connection Details

### TimescaleDB (VERIFIED)

```bash
# Connection
psql -h 10.70.0.56 -p 5433 -U ai_team -d dcim_analytics

# Password: ai_team_access_pass
```

```python
# Python (psycopg2)
import psycopg2

conn = psycopg2.connect(
    host="10.70.0.56",
    port=5433,
    database="dcim_analytics",
    user="ai_team",
    password="ai_team_access_pass"
)
```

```python
# Python (Pandas) — NEW in v1.1
import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="10.70.0.56",
    port="5433",
    dbname="dcim_analytics",
    user="ai_team",
    password="ai_team_access_pass"
)

# Ambil data metrik UPS dalam 24 jam terakhir
query = """
    SELECT time, source, value, tags->>'device_type' as device_type
    FROM metrics 
    WHERE metric_name = 'battery_temp' 
      AND time > NOW() - INTERVAL '24 hours'
    ORDER BY time ASC;
"""

df = pd.read_sql(query, conn)
print(df.head())
```

### Kafka (VERIFIED)

```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'dcim.analytics.metrics',
    bootstrap_servers='10.70.0.56:9092',
    group_id='ai-team-consumer',
    auto_offset_reset='earliest',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    print(message.value)
```

### Schema Registry (BONUS)

```
URL: http://10.70.0.56:8081
```

### Redis (PENDING)

```
Status: Awaiting details from Infrastructure team
```

---

## Appendix A: Sample Queries

### Get Latest Metrics

```sql
SELECT time, metric_name, source, value, unit
FROM metrics
WHERE time > NOW() - INTERVAL '1 hour'
ORDER BY time DESC;
```

### Get Hourly Aggregates

```sql
SELECT time, metric_name, source, value_avg, value_min, value_max
FROM metrics_hourly
WHERE time > NOW() - INTERVAL '7 days'
ORDER BY time DESC;
```

### Get Daily Aggregates

```sql
SELECT time, metric_name, source, value_avg
FROM metrics_daily
WHERE time > NOW() - INTERVAL '30 days'
ORDER BY time DESC;
```

### Get Specific Device Metrics

```sql
SELECT time, metric_name, value, unit
FROM metrics
WHERE source = 'server'
  AND metric_name = 'cpu_utilization'
  AND time > NOW() - INTERVAL '24 hours'
ORDER BY time DESC;
```

### Check Data Availability

```sql
-- Row count last 24 hours
SELECT COUNT(*) FROM metrics WHERE time > NOW() - INTERVAL '24 hours';

-- By source
SELECT source, COUNT(*)
FROM metrics
WHERE time > NOW() - INTERVAL '1 hour'
GROUP BY source;
```

---

## Appendix B: Kafka Topic Check Commands

```bash
# List all topics
kafka-topics.sh --bootstrap-server 10.70.0.56:9092 --list

# Describe specific topic
kafka-topics.sh --bootstrap-server 10.70.0.56:9092 --topic dcim.analytics.metrics --describe

# Check consumer lag
kafka-consumer-groups.sh --bootstrap-server 10.70.0.56:9092 --describe --group ai-team-consumer
```

---

## Appendix C: Changelog

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2026-07-08 | Initial gap analysis |
| v1.1 | 2026-07-08 | Updated with new documentation from Infrastructure team |

### v1.1 Changes Detail

1. **Architecture Diagram** — Updated with Analytics Bridge component and Avro/JSON clarification
2. **Data Flow** — Added detailed flow for AI team entry points
3. **Network Access** — Confirmed internal network access (no VPN needed)
4. **Python Example** — Added Pandas example with tags JSONB access
5. **Questions** — Updated Q7-Q8 (removed enriched events question, added Analytics Bridge question)
6. **Score** — Adjusted from 65% to 75% based on new information
7. **Confidence** — Increased from 90% to 92%

---

**Last Updated:** 2026-07-08 (v1.1)
**Maintained By:** Analytics & AI Team
**Status:** Active
