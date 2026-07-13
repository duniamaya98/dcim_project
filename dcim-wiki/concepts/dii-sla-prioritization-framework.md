---
title: DI&I SLA & Prioritization Framework
created: 2026-06-25
updated: 2026-06-25
type: framework
tags: [sla, prioritization, data-ingestion, dii, framework]
sources:
  - dcim-wiki/concepts/priority-severity-model.md
  - dcim-wiki/technical-requirements/dii-use-case-analysis-final.md
  - dcim-wiki/reference-designs/block2-data-ingestion-integration.md
confidence: high
---

# DI&I SLA & Prioritization Framework

Framework terpadu untuk SLA, prioritas, dan urgensi di Data Ingestion & Integration layer.

---

## 1. Priority Model (Data / Event / CI)

| Priority | Meaning | Operational Effect | Default Latency |
|----------|---------|-------------------|-----------------|
| **P1 Critical** | Outage, safety, real-time ops (NOC/SIEM) | Real-time atau near-real-time wajib | < 1 detik |
| **P2 High** | Significant service degradation | Fast sync + high accuracy | 1–30 detik |
| **P3 Medium** | Planning, audit, reporting | Batch acceptable | 1–5 menit |
| **P4 Supporting** | Historical, reference, background | Async / scheduled | > 1 jam |

---

## 2. SLA Tiers (End-to-End Latency)

| Tier | Latency | Processing Mode | Use Cases |
|------|---------|-----------------|-----------|
| **Tier 1 (Real-time)** | < 1s | Kafka → Stream Processor | UC4 NOC, UC5 SIEM |
| **Tier 2 (Near-RT)** | 1–30s | Kafka → Consumer | UC1 Predictive, UC6 Incident, UC8 CMDB |
| **Tier 3 (Near-RT)** | 1–5 min | Kafka → Batch Consumer | UC3 Energy, UC7 Asset, UC10 Energy Mgmt |
| **Tier 4 (Batch)** | 15–60 min | NiFi Scheduled | UC2 Capacity, UC9–13 |
| **Tier 5 (Async)** | > 1 hour | Background Jobs | UC14 Audit Trail |

---

## 3. Priority Mapping per Use Case

| Use Case | Priority | SLA Tier | Completeness | Timeliness |
|----------|----------|----------|-------------|------------|
| UC1 Predictive Failure | P2 | Tier 2 | ≥ 98% | < 60s |
| UC2 Capacity Optimization | P3 | Tier 4 | ≥ 95% | < 5 min |
| UC3 Energy / PUE Drift | P2 | Tier 3 | ≥ 99% | < 60s |
| UC4 NOC Monitoring | **P1** | **Tier 1** | ≥ 99% | < 5s |
| UC5 SIEM Correlation | **P1** | **Tier 1** | ≥ 99.9% | < 1s |
| UC6 Incident Response | P1 | Tier 2 | ≥ 98% | < 30s |
| UC7 Asset Lifecycle | P3 | Tier 3 | ≥ 95% | < 5 min |
| UC8 CMDB Sync | **P1** | Tier 2 | ≥ 99% | < 10s |
| UC9 Capacity Planning | P3 | Tier 4 | ≥ 95% | < 60 min |
| UC10 Energy Management | P3 | Tier 3 | ≥ 95% | < 5 min |
| UC11 Compliance | P4 | Tier 4 | ≥ 90% | < 60 min |
| UC12 Executive Dashboard | P3 | Tier 4 | ≥ 95% | < 60 min |
| UC13 Workforce Mgmt | P4 | Tier 4 | ≥ 90% | < 60 min |
| UC14 Audit Trail | P4 | Tier 5 | ≥ 90% | < 1 jam |

---

## 4. Priority Assignment Logic

### 4.1 Auto-Assignment Rules

Event priority diassign otomatis oleh enrichment processor:

```yaml
# enrichment-rules.yaml (excerpt)
rules:
  - name: critical_alarm_priority
    condition:
      event_type: "*.alarm"
      payload.severity: "critical"
    action:
      set_priority: "P1"
      set_impact_score: 9

  - name: warning_alarm_priority
    condition:
      event_type: "*.alarm"
      payload.severity: "warning"
    action:
      set_priority: "P2"
      set_impact_score: 6
```

### 4.2 Python Logic

```python
def _assign_priority(self, event: dict) -> str:
    """Assign priority based on event rules."""
    event_type = event.get("event_type", "")
    severity = event.get("payload", {}).get("severity", "")

    if severity == "critical" or "alarm" in event_type:
        return "P1"
    elif severity == "warning":
        return "P2"
    elif "metrics" in event_type:
        return "P3"
    else:
        return "P4"
```

### 4.3 Priority Override

Source system dapat override priority via field `metadata.priority`. Jika tidak di-set, default = `P3`.

---

## 5. Impact Scoring

Impact score (0–10) digunakan untuk triage dan eskalasi:

```python
def _calculate_impact(self, event: dict) -> float:
    base = 5.0

    # Priority adjustment
    priority = event.get("metadata", {}).get("priority", "P3")
    priority_adj = {"P1": 4, "P2": 2, "P3": 0, "P4": -2}
    base += priority_adj.get(priority, 0)

    # CI criticality adjustment
    ci_criticality = event.get("enrichment", {}).get("ci_criticality", "medium")
    criticality_adj = {"critical": 2, "high": 1, "medium": 0, "low": -1}
    base += criticality_adj.get(ci_criticality, 0)

    return max(0, min(10, base))
```

### Impact Score Thresholds

| Score | Action |
|-------|--------|
| 8–10 | Immediate escalation, P1 ticket |
| 5–7 | Fast track, P2 ticket |
| 2–4 | Normal queue, P3 ticket |
| 0–1 | Low priority, background processing |

---

## 6. Incident Severity (untuk Escalation)

| Severity | Meaning | Default Response | Trigger |
|----------|---------|-----------------|---------|
| **S1 Critical** | Total failure / P1 source down | Immediate triage & escalation | P1 event + source failure |
| **S2 High** | P2 failure / major degradation | Fast owner assignment | P2 event + degraded perf |
| **S3 Medium** | Latency, sync issue, minor DQ | Planned remediation | SLA breach 15+ min |
| **S4 Low** | Ad-hoc report, minor request | Normal queue | Non-urgent request |

---

## 7. Kafka Topic Priority

| Topic | Priority | Partition Key | Retention |
|-------|----------|---------------|-----------|
| `dcim.siem.alerts` | P1 | event_id | 30 hari |
| `dcim.noc.events` | P1 | device_id | 7 hari |
| `dcim.cmdb.updates` | P1 | ci_id | 90 hari |
| `dcim.analytics.anomalies` | P1 | device_id | 90 hari |
| `dcim.analytics.metrics` | P2 | device_id | 30 hari |
| `dcim.workflow.events` | P2 | entity_id | 90 hari |
| `dcim.asset.updates` | P2 | asset_id | 90 hari |
| `dcim.events.enriched` | P2 | event_id | 7 hari |
| `dcim.dlq` | P1 | event_id | 30 hari |
| `dcim.lineage` | P4 | event_id | 1 tahun |

---

## 8. Consumer Group Priority

Kafka consumer groups diprioritaskan via partition assignment:

| Consumer Group | Topic | Priority | Max Lag Before Alert |
|---------------|-------|----------|---------------------|
| `dii-siem-consumer` | `dcim.siem.alerts` | P1 | 100 msgs |
| `dii-noc-consumer` | `dcim.noc.events` | P1 | 100 msgs |
| `dii-cmdb-consumer` | `dcim.cmdb.updates` | P1 | 500 msgs |
| `dii-analytics-consumer` | `dcim.analytics.metrics` | P2 | 1,000 msgs |
| `dii-workflow-consumer` | `dcim.workflow.events` | P2 | 500 msgs |
| `dii-batch-consumer` | batch topics | P3–P4 | 5,000 msgs |

---

## 9. SLA Monitoring & Alerting

### 9.1 Per-Stage Latency SLA

| Stage | SLA | Alert Threshold |
|-------|-----|----------------|
| Validation | p99 < 100ms | > 100ms |
| Enrichment | p99 < 50ms | > 50ms |
| Kafka publish | p99 < 10ms | > 10ms |
| Consumer lag | < 1,000 msgs | > 1,000 msgs |

### 9.2 Availability SLA

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| DI&I Gateway | 99.9% | 5 min | 0 (Kafka replay) |
| Kafka Cluster | 99.95% | 30s | 0 (RF=3) |
| NiFi Cluster | 99.9% | 2 min | 1 min |
| Enrichment API | 99.9% | 1 min | N/A |

### 9.3 Prometheus Alert Rules

```yaml
groups:
  - name: dii_sla_alerts
    rules:
      - alert: ValidationLatencyHigh
        expr: histogram_quantile(0.99, rate(dii_validation_latency_seconds_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Validation p99 latency > 100ms"

      - alert: EnrichmentLatencyHigh
        expr: histogram_quantile(0.99, rate(dii_enrichment_latency_seconds_bucket[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Enrichment p99 latency > 50ms"

      - alert: KafkaConsumerLagHigh
        expr: kafka_consumer_group_lag > 1000
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Kafka consumer lag > 1000 msgs"
```

### 9.4 Cross-Cutting SLA Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total EPS | ≥ 5,000 | Events per second aggregate |
| Kafka Throughput | ≥ 100,000 msg/s | Per broker cluster |
| Batch Records | ≥ 5,000 rec/s | Per batch job |
| API Response | < 200ms p99 | Enrichment API |
| DLQ Rate | < 1% | Failed / total events |
| Enrichment Success Rate | ≥ 95% | Enriched / total events |
| Lineage Coverage | 100% | Every event tracked |

---

## 10. SLA Breach Handling

### 10.1 Breach Detection Flow

```
Metric Check → Threshold Breach → Alert Firing → Escalation
                                                      │
                                          ┌───────────┼───────────┐
                                          ▼           ▼           ▼
                                      S3: Auto    S2: Pager    S1: War
                                      Remediate   Alert        Room
```

### 10.2 Escalation Matrix

| SLA Tier | Breach → Auto Action | Breach → Escalation |
|----------|---------------------|---------------------|
| Tier 1 | Auto-retry + DLQ | PagerDuty P1, on-call < 5 min |
| Tier 2 | Auto-retry + DLQ | Slack alert, owner < 15 min |
| Tier 3 | Batch retry next cycle | Dashboard flag, owner < 1 hour |
| Tier 4 | Retry in next batch | Email report, next business day |
| Tier 5 | Log + archive | Monthly review |

### 10.3 SLA Breach → Ticket Routing

| Priority | Ticket Type | Assignment | Resolution SLA |
|----------|------------|------------|----------------|
| P1 | Incident | NOC Lead → On-Call | 1 jam |
| P2 | Problem | Data Engineer | 4 jam |
| P3 | Service Request | Data Engineer | 1 hari kerja |
| P4 | Task | Scheduled | Sprint berikutnya |

---

## 11. Data Quality per Priority

| Priority | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| P1 | ≥ 99% | Critical | < 5s–30s | Strict | Schema + Referential |
| P2 | ≥ 98% | ±0.5%–2% | < 1–60s | Cross-system | Schema + Business rules |
| P3 | ≥ 95% | ±2%–5% | < 5–60 min | Batch-valid | Schema |
| P4 | ≥ 90% | Best-effort | < 1–24 jam | Async-valid | Basic format |

---

## 12. Consumer SLA Matrix

| Consumer | Input Topics | Required SLA | Protocol |
|----------|-------------|-------------|----------|
| **CMDB** | `dcim.cmdb.updates` | Tier 2 (< 10s) | REST API |
| **Asset Repository** | `dcim.asset.updates` | Tier 3 (< 5 min) | REST API |
| **Time-Series DB** | `dcim.analytics.metrics` | Tier 2 (< 30s) | Direct write |
| **SIEM (ES)** | `dcim.siem.alerts` | Tier 1 (< 1s) | Bulk API |
| **Workflow Engine** | `dcim.workflow.events` | Tier 2 (< 30s) | REST API |
| **Dashboard** | `dcim.events.enriched` | Tier 1 (< 5s) | WebSocket |
| **BI Tools** | Batch exports | Tier 4 (< 60 min) | Export API |
| **AI Training** | `dcim.analytics.metrics` | Tier 5 (> 1 jam) | File export |

---

## Related

- [[priority-severity-model]] — Global priority & severity model
- [[data-quality-framework]] — Data quality dimensions
- [[block2-data-ingestion-integration]] — DI&I reference design
- [[dii-use-case-analysis-final]] — DI&I use case analysis
- [[data-ingestion-integration]] — DI&I component page
- [[workflow-automation]] — Escalation & ticket routing
