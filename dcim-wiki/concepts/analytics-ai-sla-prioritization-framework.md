---
title: Analytics & AI Engine SLA & Prioritization Framework
created: 2026-06-25
updated: 2026-06-25
type: framework
tags: [sla, prioritization, analytics, ai, framework, timeseries, anomaly, predictive, rca, llm]
sources:
  - dcim-wiki/concepts/priority-severity-model.md
  - dcim-wiki/concepts/dii-sla-prioritization-framework.md
  - dcim-wiki/concepts/cmdb-sla-prioritization-framework.md
  - dcim-wiki/concepts/asset-repository-sla-prioritization-framework.md
  - dcim-wiki/technical-requirements/analytics-ai-use-case-analysis-final-v2.md
  - dcim-wiki/reference-designs/block7-analytics-ai-engine.md
  - dcim-wiki/technical-requirements/fit041-analytics-ai-komparasi.md
confidence: high
---

# Analytics & AI Engine SLA & Prioritization Framework

Framework terpadu untuk SLA, prioritas, dan kualitas data di Analytics & AI Engine layer (Block 7).

---

## 1. Priority Model (Analytics Component)

| Priority | Meaning | Operational Effect | Default Latency |
|----------|---------|-------------------|-----------------|
| **P1 Critical** | Real-time stream ingestion, anomaly detection, failure prediction, RCA — downtime menghambat NOC/SIEM alerting dan predictive maintenance | Real-time processing, in-memory scoring, immediate alert propagation | < 1 detik |
| **P2 High** | Threshold alerting, pattern recognition, FP handling, automated RCA, model deployment — dampak ke quality of insight | Fast processing, high accuracy, batch within SLA | < 500ms (scoring), < 30s (API) |
| **P3 Medium** | Capacity forecasting, energy optimization, LLM/RAG — planning, optimization, NL query | Scheduled batch, API response acceptable | < 5 detik (API), < 2 jam (batch) |
| **P4 Supporting** | Model training, knowledge base indexing, historical analysis — development, background processing | Offline, async, non-urgent | < 4 jam (batch) |

---

## 2. Component Criticality Mapping

| Component | Default Criticality | P1 Example | P2 Example |
|-----------|--------------------:|------------|------------|
| Time-Series Ingestion | Critical | Metrics pipeline down → blind NOC | Degraded throughput |
| Anomaly Detection (Z-score) | Critical | Real-time anomaly scoring | — |
| Anomaly Detection (Isolation Forest) | High | Multi-metric pattern detection | False positive tuning |
| Predictive Maintenance (LSTM) | Critical | Failure probability scoring | Model accuracy monitoring |
| Predictive Maintenance (Prophet) | High | Trend forecasting | Capacity optimization |
| RCA Engine | Critical | Incident root cause analysis | Dependency mapping |
| Capacity Forecasting | High | Trend analysis, projection | Threshold alerting |
| Energy Optimization | High | PUE calculation, cooling | Power distribution |
| Model Registry | High | Model versioning, deployment | — |
| Scoring Service | Critical | Real-time inference serving | A/B testing |
| LLM/RAG Service | Medium | NL query, explanation | Knowledge base indexing |
| Model Training | Medium | Offline training pipeline | — |

### Component Criticality → Priority Assignment

```
Critical → P1 (real-time processing, in-memory scoring, immediate propagation)
High     → P2 (fast processing, high accuracy, batch within SLA)
Medium   → P3 (scheduled batch, API within target)
Low      → P4 (offline, async, background)
```

---

## 3. SLA Tiers (End-to-End Latency)

| Tier | Latency | Use Cases | Processing Mode | Model/Engine |
|------|---------|-----------|-----------------|--------------|
| **Tier 1 (Real-time)** | < 1s | UC1 Ingestion, UC4 Anomaly Detection | Stream processing | Kafka → Flink/Python |
| **Tier 2 (Inference)** | < 500ms | UC5 Threshold, UC6 Isolation Forest, UC23 Scoring | In-memory scoring | Z-score, Isolation Forest |
| **Tier 3 (Interactive)** | < 5s | UC12 RCA, UC13 Topology, UC14 Hypothesis, UC24 LLM Query, UC25 Explanation | API + computation | RCA engine, LLM/RAG |
| **Tier 4 (Batch-Hourly)** | < 1 jam | UC7 FP Handling, UC18 PUE, UC19 Cooling, UC20 Power | Scheduled batch | Hourly cron jobs |
| **Tier 5 (Batch-Daily)** | < 4 jam | UC8 Prediction, UC9 Scheduling, UC10 Accuracy, UC11 Drift, UC15 Trend, UC16 Projection, UC17 Capacity Alert, UC21 Training, UC22 Registry | Nightly batch | Daily cron (02:00 UTC) |

### Tier Definitions

- **Tier 1**: Kafka consumer → Flink/Python stream processor → TimescaleDB write. Real-time, sub-second, stateless.
- **Tier 2**: In-memory model scoring. Model loaded from registry, predictions computed per-event. Stateless, failover-ready.
- **Tier 3**: API call → computation → response. RCA engine multi-step analysis, LLM/RAG retrieval + generation. Stateful within request.
- **Tier 4**: Scheduled batch (hourly). Idempotent, retry-enabled, DLQ for failures.
- **Tier 5**: Scheduled batch (daily). Long-running, resource-intensive, offline. Model training uses GPU.

---

## 4. Priority Mapping per Use Case

| Use Case | Priority | SLA Tier | Completeness | Timeliness | Data Quality |
|----------|----------|----------|-------------|------------|--------------|
| UC1 Metric Ingestion | **P1** | Tier 1 (< 1s) | ≥ 99% | < 1s | Schema + numeric + ISO 8601 |
| UC2 Storage & Compression | P1 | Tier 1 (< 1 min) | 100% | < 1 min | Compression intact |
| UC3 Query & Aggregation | P1 | Tier 3 (< 5s) | 100% | < 5s | Aggregate match |
| UC4 Real-Time Anomaly | **P1** | Tier 1 (< 500ms) | ≥ 98% | < 500ms | Z-score correct + severity valid |
| UC5 Threshold Alerting | P1 | Tier 2 (< 100ms) | 100% | < 100ms | Threshold comparison correct |
| UC6 Pattern Recognition | P2 | Tier 2 (< 500ms) | 100% | < 500ms | Model accuracy > 90% |
| UC7 FP Handling | P3 | Tier 4 (< 5 min/batch) | 100% | Batch hourly | FP rate < 10% |
| UC8 Failure Prediction | **P1** | Tier 5 (daily batch) | ≥ 95% | Daily 02:00 UTC | F1 > 0.80, probability 0.0–1.0 |
| UC9 Schedule Optimization | P2 | Tier 5 (daily batch) | ≥ 95% | Daily | Constraint valid |
| UC10 Accuracy Monitoring | P2 | Tier 5 (weekly) | 100% | Weekly | F1 tracked |
| UC11 Drift Detection | P2 | Tier 5 (weekly) | 100% | Weekly | PSI 0.0–1.0 |
| UC12 Event Correlation | **P1** | Tier 3 (< 30s) | ≥ 95% | < 30s | Correlation accuracy > 90% |
| UC13 Dependency Mapping | P2 | Tier 3 (< 5s) | 100% | < 5s | Topology from CMDB consistent |
| UC14 Automated RCA | P2 | Tier 3 (< 30s total) | 100% | < 30s | ≥ 3 hypotheses ranked |
| UC15 Trend Analysis | P1 | Tier 5 (daily batch) | ≥ 95% | Daily 02:30 UTC | MAPE < 10% |
| UC16 Resource Projection | P2 | Tier 5 (daily batch) | 100% | Daily | Exhaustion date accurate |
| UC17 Capacity Alerting | P2 | Tier 4 (< 5s alert) | 100% | < 5s | Threshold configurable |
| UC18 PUE Calculation | **P1** | Tier 4 (< 1 jam) | 100% | Hourly | PUE = total/IT exact |
| UC19 Cooling Optimization | P2 | Tier 4 (hourly) | 100% | Hourly | Zone-specific correct |
| UC20 Power Distribution | P2 | Tier 4 (hourly) | 100% | Hourly | Load balance ratio valid |
| UC21 Model Training | P4 | Tier 5 (weekly batch) | 100% | Weekly | Time-based split, no leakage |
| UC22 Model Registry | P1 | Tier 5 (< 5s reg) | 100% | < 5s | Semver + artifact integrity |
| UC23 Model Deployment | **P1** | Tier 2 (< 500ms inference) | 100% | Real-time | Model loaded, health check |
| UC24 NL Query | P1 | Tier 3 (< 5s) | ≥ 90% | < 5s | Citations present |
| UC25 Explanation | P3 | Tier 3 (< 5s) | ≥ 90% | < 5s | Facts verifiable |
| UC26 Knowledge Base | P4 | Tier 5 (on-change) | ≥ 95% | On-change | ≥ 100 docs indexed |

### Priority Distribution

| Priority | Count | Use Cases |
|----------|-------|-----------|
| **P1 Critical** | 12 | UC1, UC2, UC3, UC4, UC5, UC8, UC12, UC15, UC18, UC22, UC23, UC24 |
| **P2 High** | 10 | UC6, UC9, UC10, UC11, UC13, UC14, UC16, UC17, UC19, UC20 |
| **P3 Medium** | 3 | UC7, UC25, UC3 |
| **P4 Supporting** | 2 | UC21, UC26 |

---

## 5. Auto-Assignment Logic

### 5.1 Metric Priority Assignment

```yaml
# analytics-priority-rules.yaml
rules:
  - name: critical_metric_ingestion
    condition:
      metric_category: ["power", "cooling", "environment"]
      ci_criticality: ["critical", "high"]
    action:
      set_priority: "P1"
      set_tier: "Tier 1"
      set_processing: "stream"

  - name: anomaly_scoring
    condition:
      event_type: "anomaly.*"
    action:
      set_priority: "P1"
      set_tier: "Tier 2"
      set_processing: "in-memory"

  - name: capacity_forecast
    condition:
      event_type: "capacity.*"
      schedule: "daily"
    action:
      set_priority: "P2"
      set_tier: "Tier 5"
      set_processing: "batch"

  - name: llm_query
    condition:
      event_type: "llm.*"
    action:
      set_priority: "P3"
      set_tier: "Tier 3"
      set_processing: "interactive"
```

### 5.2 Event Priority Assignment (Python)

```python
def _assign_analytics_priority(self, event: dict) -> str:
    """Assign priority based on analytics event rules."""
    event_type = event.get("event_type", "")
    severity = event.get("severity", "")
    model_type = event.get("model_type", "")

    # P1: Real-time critical
    if event_type in ("anomaly.realtime", "ingestion"):
        return "P1"
    if model_type == "lstm" and severity == "critical":
        return "P1"
    if event_type == "rca.correlation":
        return "P1"

    # P2: High-value inference
    if event_type in ("anomaly.threshold", "anomaly.pattern"):
        return "P2"
    if event_type in ("rca.hypothesis", "capacity.alert"):
        return "P2"
    if model_type in ("isolation_forest", "prophet"):
        return "P2"

    # P3: Interactive / batch
    if event_type in ("llm.query", "llm.explain"):
        return "P3"
    if event_type in ("energy.pue", "energy.cooling"):
        return "P3"

    # P4: Background
    if event_type in ("model.training", "knowledgebase.indexing"):
        return "P4"

    return "P3"  # default
```

### 5.3 Priority Override

- Source system dapat override via field `metadata.priority`
- DI&I Gateway mengirim priority dari enrichment layer
- Manual override oleh admin (role: `analytics.admin`) dengan audit trail
- Model training jobs selalu P4 meskipun model type kritis

---

## 6. Impact Scoring

Impact score (0–10) digunakan untuk triage dan eskalasi:

```python
def _calculate_analytics_impact(self, event: dict) -> float:
    """Calculate analytics impact score for prioritization."""
    base = 5.0

    # Priority adjustment
    priority = event.get("metadata", {}).get("priority", "P3")
    priority_adj = {"P1": 4, "P2": 2, "P3": 0, "P4": -2}
    base += priority_adj.get(priority, 0)

    # Model accuracy adjustment
    model_accuracy = event.get("model_accuracy", 0.0)
    if model_accuracy < 0.7:
        base += 2  # Low accuracy = high impact
    elif model_accuracy < 0.8:
        base += 1

    # CI criticality adjustment
    ci_criticality = event.get("ci_criticality", "medium")
    criticality_adj = {"critical": 2, "high": 1, "medium": 0, "low": -1}
    base += criticality_adj.get(ci_criticality, 0)

    # Anomaly severity adjustment
    anomaly_score = event.get("anomaly_score", 0.0)
    if anomaly_score > 0.9:
        base += 1  # Very high anomaly

    return max(0, min(10, base))
```

### Impact Score Thresholds

| Score | Action |
|-------|--------|
| 8–10 | Immediate escalation, P1 ticket, real-time alert |
| 5–7 | Fast track, P2 ticket, priority processing |
| 2–4 | Normal queue, P3 ticket, standard processing |
| 0–1 | Low priority, background, batch queue |

---

## 7. Incident Severity (untuk Escalation)

| Severity | Meaning | Default Response | Trigger |
|----------|---------|-----------------|---------|
| **S1 Critical** | Analytics pipeline total failure / time-series ingestion down | Immediate triage & escalation | Kafka consumer down / TimescaleDB failure / scoring service crash |
| **S2 High** | Model accuracy degraded / prediction delay / RCA failure | Fast owner assignment | F1 < 0.80 / batch delay > 2 jam / RCA timeout |
| **S3 Medium** | Cache miss rate high / LLM latency spike / drift detected | Planned remediation | Cache hit < 80% / LLM p99 > 10s / PSI > 0.15 |
| **S4 Low** | Ad-hoc query / minor model tuning / knowledge base update | Normal queue | Non-urgent request |

---

## 8. Kafka Topic Priority

| Topic | Priority | Partitions | Retention | Use Case |
|-------|----------|------------|-----------|----------|
| `dcim.analytics.metrics` | **P1** | 6 | 7 hari | Raw metrics from DI&I |
| `dcim.analytics.anomalies` | **P1** | 3 | 30 hari | Anomaly alerts |
| `dcim.analytics.predictions` | **P1** | 3 | 30 hari | Prediction results |
| `dcim.analytics.rca` | **P1** | 3 | 30 hari | RCA results |
| `dcim.analytics.capacity` | P2 | 3 | 30 hari | Capacity forecasts |
| `dcim.analytics.energy` | P2 | 3 | 30 hari | Energy optimization results |
| `dcim.analytics.model.events` | P3 | 3 | 90 hari | Model lifecycle events |
| `dcim.analytics.dlq` | **P1** | 3 | 30 hari | Failed events |

### Topic Configuration

| Setting | Tier 1 Topics | Tier 2 Topics | Tier 3–5 Topics |
|---------|---------------|---------------|-----------------|
| Replication Factor | 3 | 3 | 3 |
| min.insync.replicas | 2 | 2 | 2 |
| acks | all | all | all |
| retention.ms | 7 hari | 30 hari | 30–90 hari |
| cleanup.policy | delete | delete | delete |
| compression | lz4 | lz4 | snappy |

---

## 9. Consumer Group Priority

| Consumer Group | Topic | Priority | Max Lag Before Alert |
|---------------|-------|----------|---------------------|
| `analytics-anomaly-consumer` | `dcim.analytics.metrics` | P1 | 100 msgs |
| `analytics-timeseries-consumer` | `dcim.analytics.metrics` | P1 | 500 msgs |
| `analytics-predictive-consumer` | `dcim.analytics.predictions` | P1 | 500 msgs |
| `analytics-rca-consumer` | `dcim.analytics.rca` | P1 | 200 msgs |
| `analytics-capacity-consumer` | `dcim.analytics.capacity` | P2 | 1,000 msgs |
| `analytics-energy-consumer` | `dcim.analytics.energy` | P2 | 1,000 msgs |
| `analytics-batch-consumer` | batch topics | P3–P4 | 5,000 msgs |
| `workflow-analytics-consumer` | `dcim.analytics.anomalies` | P1 | 500 msgs |

---

## 10. Consumer SLA Matrix

| Consumer | Input Topics / UCs | Required SLA | Protocol | Latency |
|----------|-------------------|-------------|----------|---------|
| **NOC Dashboard** | UC4, UC5, UC8, UC12, UC18 | Tier 1 (< 5s) | WebSocket / SSE | < 5 detik |
| **Workflow Automation** | UC4, UC8, UC17 | Tier 3 (< 5s) | REST API / Kafka | < 5 detik |
| **DC Managers** | UC8, UC15, UC16, UC18 | Tier 3 (< 5s) | REST API | < 5 detik |
| **IT Operations** | UC8, UC9, UC12, UC14 | Tier 3 (< 30s) | REST API | < 30 detik |
| **Facilities Team** | UC18, UC19, UC20 | Tier 4 (< 1 jam) | REST API / Export | Hourly |
| **SIEM/SOC** | UC4, UC12 | Tier 1 (< 5s) | Kafka / REST API | < 5 detik |
| **ITSM** | UC8, UC12, UC14 | Tier 3 (< 30s) | REST API | < 30 detik |
| **Grafana** | UC1, UC3, UC4, UC18 | Tier 1 (< 5s) | Direct query | < 5 detik |
| **LLM/RAG Service** | UC4, UC8, UC12, UC15, UC18 | Tier 3 (< 5s) | REST API | < 5 detik |
| **Model Training Pipeline** | UC10, UC11 | Tier 5 (weekly) | Kafka / Batch | Weekly |
| **BI Tools** | UC3, UC8, UC15, UC18 | Tier 5 (daily) | Export API | Batch |
| **Compliance** | UC1, UC4, UC8 | Tier 5 (daily) | REST API / Export | Batch |

---

## 11. SLA Monitoring & Alerting

### 11.1 Per-Component Latency SLA

| Component | SLA Target | Alert Threshold |
|-----------|-----------|----------------|
| Time-series ingestion | p99 < 100ms | > 100ms |
| Z-score anomaly scoring | p99 < 10ms | > 10ms |
| Isolation Forest scoring | p99 < 500ms | > 500ms |
| Prophet forecast | p99 < 10s | > 10s |
| RCA analysis (full) | p99 < 30s | > 30s |
| LLM/RAG query | p99 < 5s | > 10s |
| Model registration | p99 < 5s | > 5s |
| Model deployment | p99 < 10s | > 10s |

### 11.2 Availability SLA

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| Time-series Ingestion | 99.9% | < 5 min | ≤ 5 min (WAL) |
| Anomaly Detection | 99.9% | < 30s (failover) | 0 (stateless) |
| TimescaleDB | 99.95% | < 30 min | ≤ 5 min |
| LLM/RAG Service | 99.5% | < 5 min | N/A |
| Model Training | 99.0% | < 1 hour | N/A (batch) |
| Model Registry (MinIO) | 99.9% | < 15 min | 0 (replicated) |
| Scoring Service | 99.9% | < 30s (failover) | 0 (stateless) |

### 11.3 Prometheus Alert Rules

```yaml
groups:
  - name: analytics_ai_sla_alerts
    rules:
      - alert: AnalyticsIngestionLatencyHigh
        expr: histogram_quantile(0.99, rate(analytics_ingestion_latency_seconds_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Analytics ingestion p99 latency > 100ms"

      - alert: AnalyticsZScoreLatencyHigh
        expr: histogram_quantile(0.99, rate(analytics_zscore_latency_seconds_bucket[5m])) > 0.01
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Z-score anomaly scoring p99 latency > 10ms"

      - alert: AnalyticsIsolationForestLatencyHigh
        expr: histogram_quantile(0.99, rate(analytics_isolation_forest_latency_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Isolation Forest p99 latency > 500ms"

      - alert: AnalyticsModelAccuracyLow
        expr: analytics_model_accuracy < 0.8
        for: 7d
        labels:
          severity: warning
        annotations:
          summary: "Model accuracy dropped below 80%: {{ $value }}"

      - alert: AnalyticsModelDrift
        expr: analytics_model_drift_score > 0.15
        for: 7d
        labels:
          severity: warning
        annotations:
          summary: "Model drift detected (PSI={{ $value }}), retraining recommended"

      - alert: AnalyticsLLMLatencyHigh
        expr: histogram_quantile(0.99, rate(analytics_llm_query_latency_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "LLM query p99 latency > 10s"

      - alert: AnalyticsRCATimeout
        expr: histogram_quantile(0.99, rate(analytics_rca_latency_seconds_bucket[5m])) > 30
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "RCA analysis p99 latency > 30s"

      - alert: AnalyticsTimescaleDBDown
        expr: pg_up{datname="dcim_analytics"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "TimescaleDB analytics instance is down"

      - alert: AnalyticsKafkaConsumerLagHigh
        expr: kafka_consumer_group_lag{group=~"analytics-.*"} > 1000
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Analytics Kafka consumer lag > 1000 msgs: {{ $labels.group }}"

      - alert: AnalyticsAnomalyRateHigh
        expr: rate(analytics_anomalies_detected_total[1h]) > 50
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "High anomaly detection rate: {{ $value }}/hour"

      - alert: AnalyticsModelRegistryUnavailable
        expr: minio_bucket_objects_total{bucket="analytics-models"} == 0
        for: 30m
        labels:
          severity: critical
        annotations:
          summary: "Model Registry (MinIO) unreachable or empty"
```

### 11.4 Cross-Cutting Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Ingestion throughput | ≥ 1,000 metrics/sec | Events processed per second |
| Z-score check rate | 5,000 checks/sec | In-memory scoring throughput |
| Anomaly detection latency | < 500ms p99 | Per event (Isolation Forest) |
| Prediction throughput | ≥ 5,000 predictions/day | Daily batch |
| RCA analysis latency | < 30s p99 | Per incident (full pipeline) |
| LLM query throughput | 20 queries/min | Concurrent |
| Model accuracy (F1) | > 0.80 | Weekly evaluation |
| False positive rate | < 10% | After tuning |
| Knowledge base coverage | ≥ 100 documents | Indexed runbooks + docs |
| API availability | 99.9% | Aggregate endpoints |
| Data completeness (P1) | ≥ 95% | Per priority level |
| DLQ rate | < 1% | Failed / total events |

---

## 12. SLA Breach Handling

### 12.1 Breach Detection Flow

```
Metric Check → Threshold Breach → Alert Firing → Escalation
                                                    │
                                        ┌───────────┼───────────┐
                                        ▼           ▼           ▼
                                    S4: Log     S3: Auto    S2: Alert
                                    + Monitor   Retry       Owner
                                                        │
                                                        ▼
                                                    S1: War Room
                                                    + Incident
```

### 12.2 Escalation Matrix

| SLA Tier | Breach → Auto Action | Breach → Escalation |
|----------|---------------------|---------------------|
| Tier 1 | Auto-retry + DLQ + fallback (cached data) | PagerDuty P1, on-call < 5 min |
| Tier 2 | Score fallback (previous model version) | Slack alert, owner < 15 min |
| Tier 3 | Cache serve stale + retry | Dashboard flag, owner < 1 hour |
| Tier 4 | Retry next batch cycle | Email report, next business day |
| Tier 5 | Log + archive for review | Weekly review |

### 12.3 SLA Breach → Ticket Routing

| Priority | Ticket Type | Assignment | Resolution SLA |
|----------|------------|------------|----------------|
| P1 | Incident | Analytics Engineer → On-Call | 1 jam |
| P2 | Problem | Data Engineer | 4 jam |
| P3 | Service Request | Data Engineer | 1 hari kerja |
| P4 | Task | Scheduled | Sprint berikutnya |

---

## 13. Data Quality per Priority

| Priority | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| P1 | ≥ 99% | Metric numeric, Z-score correct, PUE exact | < 1s–5s | Schema + referential | ISO 8601 + ENUM valid |
| P2 | ≥ 98% | Model F1 > 0.80, Correlation > 90% | < 500ms–30s | Cross-model consistent | Schema + business rules |
| P3 | ≥ 95% | MAPE < 10%, FP rate < 10% | < 5s–1 jam | Batch-consistent | Schema |
| P4 | ≥ 90% | Best-effort | < 1–4 jam | Async-valid | Basic format |

### 15 Data Quality Rules

| Rule | Dimension | Check | Action | Severity |
|------|-----------|-------|--------|----------|
| DQ-TS-01 | Completeness | metric_value must be numeric | Reject + DLQ | Critical |
| DQ-TS-02 | Validity | timestamp must be ISO 8601 | Reject + DLQ | Critical |
| DQ-TS-03 | Mandatory | metric_name must be non-empty | Reject + DLQ | Critical |
| DQ-TS-04 | Referential | source must be valid system identifier | Reject + DLQ | Critical |
| DQ-AD-01 | Validity | anomaly_score must be 0.0–1.0 | Clamp to range | High |
| DQ-AD-02 | Validity | severity must be valid ENUM | Default to 'medium' | High |
| DQ-PM-01 | Validity | failure_probability must be 0.0–1.0 | Clamp to range | High |
| DQ-PM-02 | Validity | confidence must be 0.0–1.0 | Clamp to range | High |
| DQ-PM-03 | Validity | prediction_window must be valid | Reject + alert | High |
| DQ-RCA-01 | Referential | incident_id must be valid UUID | Reject + alert | Critical |
| DQ-RCA-02 | Range | timeframe must be 1–1440 minutes | Clamp to range | Medium |
| DQ-LLM-01 | Range | query length 10–5000 chars | Reject with message | Medium |
| DQ-LLM-02 | Completeness | response must include source count | Append warning | Low |
| DQ-MOD-01 | Validity | model version must follow semver | Reject + alert | Critical |
| DQ-MOD-02 | Range | training_data_size must be > 1000 | Reject + alert | High |

---

## 14. Cache Strategy by Priority

| Priority | Cache Mode | TTL | Invalidation |
|----------|-----------|-----|-------------|
| P1 | Write-through (TimescaleDB) | Real-time | On every write |
| P2 | In-memory model cache | Session (model reload) | On deployment / hot-reload |
| P3 | Redis query cache | 5 min | TTL + event-driven |
| P4 | Lazy-load | 1 hour | TTL only |

### Cache Key Patterns

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `analytics:anomaly:{ci_id}:{window}` | 5 min | Anomaly detection cache |
| `analytics:topology:{ci_id}:{depth}` | 5 min | CMDB topology cache for RCA |
| `analytics:rca:{incident_id}` | 30 min | RCA result cache |
| `analytics:capacity:{resource}` | 1 hour | Capacity forecast cache |
| `analytics:llm:context:{ci_id}` | 15 min | LLM/RAG context cache |
| `analytics:model:version:{model_name}` | Session | Active model version pointer |

### Cache Invalidation Events

```yaml
invalidation_rules:
  - trigger: "anomaly.detected"
    action: "invalidate_anomaly_cache"
    scope: "ci_id"
    propagation: "event-driven"

  - trigger: "model.deployed"
    action: "invalidate_model_cache + reload_scoring_service"
    scope: "model_name"
    propagation: "hot-reload"

  - trigger: "rca.completed"
    action: "invalidate_rca_cache"
    scope: "incident_id"
    propagation: "write-through"

  - trigger: "capacity.batch.complete"
    action: "invalidate_capacity_cache"
    scope: "global"
    propagation: "batch invalidation"
```

---

## 15. Resource Allocation & Sizing

| Component | vCPU | RAM | Storage | Instances | Priority |
|-----------|------|-----|---------|-----------|----------|
| Time-series processor | 2 | 4 GB | — | 2 | P1 |
| Anomaly detection (Z-score) | 1 | 2 GB | — | 2 | P1 |
| Anomaly detection (Isolation Forest) | 2 | 4 GB | — | 2 | P2 |
| Predictive maintenance | 2 | 4 GB | 10 GB (models) | 1 | P1 |
| RCA engine | 2 | 4 GB | — | 1 | P1 |
| Capacity forecasting | 1 | 2 GB | — | 1 | P3 |
| Energy optimization | 1 | 2 GB | — | 1 | P3 |
| Model training (offline) | 4 | 16 GB | 50 GB | 1 | P4 |
| LLM/RAG service | 4 | 8 GB | 20 GB (embeddings) | 1 | P3 |
| Scoring service (inference) | 2 | 4 GB | — | 2 | P1 |
| **Total** | **~21** | **~50 GB** | **~80 GB** | **~15** | — |

---

## 16. Monitoring Dashboard

### Analytics & AI Health Metrics

| Metric | Source | Refresh |
|--------|--------|---------|
| Ingestion throughput (metrics/sec) | Prometheus | Real-time |
| Ingestion latency (p50, p95, p99) | Prometheus | Real-time |
| Anomaly detection rate (per hour) | Prometheus | Real-time |
| Anomaly severity distribution | PostgreSQL | Real-time |
| Prediction accuracy (F1, by model) | PostgreSQL | Daily |
| Model drift score (PSI) | PostgreSQL | Weekly |
| RCA analysis count & latency | Prometheus | Real-time |
| LLM query count & latency | Prometheus | Real-time |
| Capacity forecast MAPE | PostgreSQL | Daily |
| PUE trend (daily) | PostgreSQL | Hourly |
| Model registry status | MinIO + PostgreSQL | Real-time |
| Kafka consumer lag | Prometheus | Real-time |
| DLQ count | Kafka | Real-time |
| Cache hit rate | Redis | Real-time |

---

## 17. Model Lifecycle SLA

| Stage | SLA | Alert Threshold |
|-------|-----|----------------|
| Training completion | < 4 hours | > 4 hours |
| Model registration | < 5 seconds | > 5 seconds |
| Validation on staging | < 30 minutes | > 30 minutes |
| Deployment to production | < 10 seconds | > 10 seconds |
| Hot-reload (new version) | < 30 seconds | > 30 seconds |
| Rollback | < 60 seconds | > 60 seconds |
| Model artifact availability | 99.9% | < 99.9% |

### Model Accuracy SLA

| Metric | Minimum | Warning | Critical |
|--------|---------|---------|----------|
| F1 Score | > 0.80 | < 0.80 (7 days) | < 0.70 (7 days) |
| Precision | > 0.85 | < 0.85 (7 days) | < 0.75 (7 days) |
| Recall | > 0.80 | < 0.80 (7 days) | < 0.70 (7 days) |
| False Positive Rate | < 10% | > 10% (7 days) | > 20% (7 days) |
| PSI (Drift) | < 0.10 | > 0.15 (7 days) | > 0.25 (7 days) |

---

## Related

- [[priority-severity-model]] — Global priority & severity model
- [[dii-sla-prioritization-framework]] — DI&I SLA framework
- [[cmdb-sla-prioritization-framework]] — CMDB SLA framework
- [[asset-repository-sla-prioritization-framework]] — Asset Repository SLA framework
- [[analytics-ai-use-case-analysis-final-v2]] — Analytics & AI use case analysis (26 UCs)
- [[block7-analytics-ai-engine]] — Analytics & AI reference design spec
- [[fit041-analytics-ai-komparasi]] — FIT041 vs DCIM-Wiki comparison
- [[data-quality-framework]] — Data quality dimensions
- [[workflow-automation]] — Escalation & ticket routing
