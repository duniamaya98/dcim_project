---
title: SIEM SOAR SLA & Prioritization Framework
created: 2026-06-25
updated: 2026-06-25
type: framework
tags: [sla, prioritization, siem, soar, security, incident, playbook, correlation, detection]
sources:
  - dcim-wiki/concepts/priority-severity-model.md
  - dcim-wiki/concepts/cmdb-sla-prioritization-framework.md
  - dcim-wiki/concepts/dii-sla-prioritization-framework.md
  - dcim-wiki/technical-requirements/siem-use-case-analysis-final.md
  - dcim-wiki/reference-designs/siem-soar.md
  - dcim-wiki/reference-designs/siem-soar-actual-architecture.md
confidence: high
---

# SIEM SOAR SLA & Prioritization Framework

Framework terpadu untuk SLA, prioritas, dan urgensi di Security Information & Event Management / Security Orchestration, Automation & Response layer.

---

## 1. Priority Model (Alert / Event / Incident)

| Priority | Meaning | Operational Effect | Default Latency |
|----------|---------|-------------------|-----------------|
| **P1 Critical** | Active breach, compromised critical asset, safety event | Real-time detection + auto-response, immediate SOC escalation, playbook execution < 60s | < 1 detik |
| **P2 High** | Suspicious activity, enrichment pending, policy violation | Fast triage, enrichment < 30s, alert assigned to L1 analyst | 1–30 detik |
| **P3 Medium** | Compliance event, periodic scan, audit log | Batch processing, daily review acceptable | 1–5 menit |
| **P4 Supporting** | Historical analytics, threat hunting data, dashboard refresh | Async, background, scheduled | > 1 jam |

---

## 2. Incident Severity Mapping

| Severity | Source Priority | SOC Response | Auto-Response | Escalation | Example |
|----------|----------------|--------------|---------------|------------|---------|
| **S1 Critical** | P1 + Critical Asset | Immediate triage (L2/L3) | Auto-contain (with OT-safe guard) | CISO within 15 min | Active ransomware, P1 DC asset compromised |
| **S2 High** | P1 + Non-Critical or P2 + Critical Asset | Fast assign (L1/L2) | Enrich + notify | SOC Manager within 30 min | Brute force on admin account, malware detected |
| **S3 Medium** | P2 + Non-Critical Asset | Normal queue (L1) | Enrich only | Within 4 hours | Suspicious DNS, policy violation |
| **S4 Low** | P3/P4 | Batch review | None | Next shift | Compliance scan, informational log |

---

## 3. SLA Tiers (End-to-End Latency)

| Tier | Latency | Use Cases | Processing Mode | Pipeline |
|------|---------|-----------|-----------------|----------|
| **Tier 1 (Real-time)** | < 1s | UC1-6, UC14, UC19 | Kafka → Stream Processor | Wazuh → Kafka → ES + Correlation |
| **Tier 2 (Near-RT)** | 1–30s | UC7-13, UC16, UC20 | Kafka → Consumer | ElastAlert → Tracecat → IRIS |
| **Tier 3 (Batch)** | 1–5 min | UC17-18 | NiFi Scheduled | Scheduled scan + report generation |
| **Tier 4 (Batch)** | 15–60 min | UC6 (MITRE mapping) | Background Jobs | Rule-to-ATT&CK mapper |
| **Tier 5 (On-demand)** | Variable | UC15 (Threat Hunting) | Ad-hoc Query | Analyst → ES/Kibana query |

### Tier Definitions

- **Tier 1**: Event masuk Kafka, langsung diproses stream processor, alert tergenerate < 1 detik. Zero tolerance untuk data loss.
- **Tier 2**: Alert masuk enrichment pipeline, AI triage < 30s, playbook execution < 60s. Near-real-time untuk SOC response.
- **Tier 3**: Scheduled compliance scans dan report generation. Batch processing acceptable, idempotent.
- **Tier 4**: Background MITRE ATT&CK mapping, historical correlation. Non-urgent.
- **Tier 5**: Analyst-initiated threat hunting. Variable latency, depends on query complexity.

---

## 4. Priority Mapping per Use Case

| UC | Name | Priority | SLA Tier | Latency Target | DQ Completeness | DQ Timeliness |
|----|------|----------|----------|----------------|-----------------|---------------|
| UC1 | Security Event Collection & Normalization | **P1** | Tier 1 (< 1s) | < 1s | ≥ 99.9% | < 1s |
| UC2 | Log Decoding & Field Extraction | **P1** | Tier 1 (< 1s) | < 500ms | ≥ 99.9% | < 500ms |
| UC3 | Security Event Schema & Storage | **P1** | Tier 1 (< 1s) | < 1s | ≥ 99.9% | < 1s |
| UC4 | Correlation Engine | **P1** | Tier 1 (< 1s) | < 30s | ≥ 99% | < 30s |
| UC5 | Detection Engineering (Detection-as-Code) | **P1** | Tier 1 (< 1s) | < 30s | ≥ 99% | Real-time |
| UC6 | MITRE ATT&CK Mapping | **P1** | Tier 4 (15–60m) | < 60 min | ≥ 95% | Batch |
| UC7 | ML Alert Triage | **P2** | Tier 2 (1–30s) | < 30s | ≥ 98% | < 30s |
| UC8 | Alert Enrichment Pipeline | **P1** | Tier 2 (1–30s) | < 30s | ≥ 95% | < 60s |
| UC9 | Incident Response Workflow | **P1** | Tier 2 (1–30s) | < 30s | ≥ 98% | < 30s |
| UC10 | SOAR Automated Response | **P1** | Tier 2 (1–30s) | < 60s | ≥ 98% | < 60s |
| UC11 | Case Management (DFIR-IRIS) | **P1** | Tier 2 (1–30s) | < 120s | ≥ 100% | < 120s |
| UC12 | Escalation Workflow | **P1** | Tier 2 (1–30s) | < 5 min | ≥ 99% | < 5 min |
| UC13 | Physical-Cyber Correlation | **P1** | Tier 2 (1–30s) | < 30s | ≥ 99% | < 30s |
| UC14 | Deception Technology (Honeypots) | **P3** | Tier 1 (< 1s) | < 1s | ≥ 99% | < 1s |
| UC15 | Threat Hunting | **P2** | Tier 5 (on-demand) | Variable | ≥ 95% | On-demand |
| UC16 | XDR Integration | **P2** | Tier 2 (1–30s) | < 30s | ≥ 98% | < 30s |
| UC17 | Compliance & Audit Reporting | **P2** | Tier 3 (1–5m) | < 5 min | ≥ 100% | < 5 min |
| UC18 | CIS Benchmark Compliance | **P2** | Tier 3 (1–5m) | < 5 min | ≥ 100% | < 5 min |
| UC19 | SOC Dashboard & Visualization | **P2** | Tier 1 (< 1s) | < 3s | ≥ 99% | Real-time |
| UC20 | User & Entity Behavior Analytics (UEBA) | **P2** | Tier 2 (1–30s) | < 30s | ≥ 98% | < 30s |

### Priority Distribution

```
P1 Critical: 13 UCs (UC1-6, UC8-13) — security core + incident response
P2 High:      5 UCs (UC7, UC15-20)  — analytics, advanced detection, operations
P3 Medium:    1 UC  (UC14)           — deception (honeypots)
P4 Supporting: 0 UCs
```

---

## 5. SOC Operational SLAs

### 5.1 Incident Metrics (MTTA / MTTC / MTTR)

| Metric | Target | Measurement | Escalation Trigger |
|--------|--------|-------------|-------------------|
| **MTTA** (Mean Time to Acknowledge) | < 15 min | Alert created → Analyst acknowledges | > 15 min → SOC Manager |
| **MTTC** (Mean Time to Contain) | < 30 min | Alert confirmed → Containment action | > 30 min → SOC Manager + CISO |
| **MTTR** (Mean Time to Resolve) | < 4 hours | Incident created → Incident closed | > 4 hours → Escalation review |
| **Auto-closure Rate** | > 60% | SOAR playbook auto-resolved / total | < 60% → Playbook tuning |
| **Escalation Rate** | < 25% | Escalated incidents / total | > 25% → Process review |
| **False Positive Rate** | < 10% | FP alerts / total alerts | > 10% → Rule tuning |

### 5.2 SOC Shift SLAs

| Shift | Coverage | Response Target | Escalation Path |
|-------|----------|----------------|-----------------|
| Day (08:00–16:00) | Full SOC team (L1+L2+L3) | Standard SLAs | L1 → L2 → L3 → CISO |
| Evening (16:00–00:00) | Skeleton crew (L1+L2) | Standard SLAs | L1 → L2 → On-call L3 |
| Night (00:00–08:00) | On-call (L1) | S1/S2 only, S3/S4 deferred | L1 → On-call L2 → CISO |

### 5.3 Response SLA by Severity

| Severity | First Response | Containment | Resolution | Notification |
|----------|---------------|-------------|------------|--------------|
| S1 Critical | Immediate (< 5 min) | < 30 min | < 4 hours | CISO within 15 min |
| S2 High | < 15 min | < 1 hour | < 8 hours | SOC Manager within 30 min |
| S3 Medium | < 1 hour | < 4 hours | < 24 hours | Next shift handover |
| S4 Low | < 4 hours | < 24 hours | < 72 hours | Weekly review |

---

## 6. Kafka Topic Priority & Consumer Group

### 6.1 Topic Priority Mapping

| Kafka Topic | Partitions | Replication | Retention | Priority | Consumer |
|-------------|------------|-------------|-----------|----------|----------|
| `dcim.siem.events` | 12 | RF=3 | 7 days | **P1** | ES Indexer, Correlation Engine |
| `dcim.siem.alerts` | 6 | RF=3 | 30 days | **P1** | ML Triage, SOAR (ElastAlert) |
| `dcim.siem.triaged` | 6 | RF=3 | 30 days | **P1** | Enrichment Pipeline |
| `dcim.siem.enriched` | 6 | RF=3 | 30 days | **P1** | SOAR (Tracecat Webhook) |
| `dcim.siem.incidents` | 6 | RF=3 | 90 days | **P1** | DFIR-IRIS |
| `dcim.siem.correlated` | 6 | RF=3 | 30 days | **P2** | Physical-Cyber Correlation |
| `dcim.siem.deception` | 3 | RF=2 | 30 days | **P3** | SOAR (Honeypot alert) |
| `dcim.siem.ueba` | 6 | RF=3 | 30 days | **P2** | UEBA Alert Engine |

### 6.2 Consumer Group Priority

| Consumer Group | Topic(s) | Priority | Max Latency | Concurrency |
|----------------|----------|----------|-------------|-------------|
| `siem-es-indexer` | `dcim.siem.events` | **P1** | < 1s | 6 consumers |
| `siem-correlation` | `dcim.siem.events` | **P1** | < 30s | 3 consumers |
| `siem-triage` | `dcim.siem.alerts` | **P1** | < 30s | 3 consumers |
| `siem-enrichment` | `dcim.siem.triaged` | **P1** | < 30s | 3 consumers |
| `soar-playbook` | `dcim.siem.enriched` | **P1** | < 60s | 3 consumers |
| `iris-incident` | `dcim.siem.incidents` | **P1** | < 120s | 2 consumers |
| `siem-xdr` | `dcim.xdr.events` | **P2** | < 30s | 2 consumers |
| `siem-ueba` | `dcim.siem.ueba` | **P2** | < 30s | 2 consumers |

---

## 7. SLA Breach Handling

### 7.1 Breach Detection & Escalation

| SLA Breach Type | Detection Method | Escalation Path | Max Recovery |
|----------------|-----------------|-----------------|--------------|
| MTTA > 15 min | Alert aging monitor (Kibana) | Auto-escalate to SOC Manager | < 30 min |
| MTTC > 30 min | DFIR-IRIS timer | SOC Manager → CISO | < 1 hour |
| MTTR > 4 hours | DFIR-IRIS SLA tracker | CISO + Management report | < 8 hours |
| Ingestion > 1s | Kafka consumer lag monitor | Auto-alert NOC + SOC | < 5 min |
| Playbook > 60s | Temporal workflow timeout | Auto-retry + alert SOC | < 5 min |

### 7.2 Breach Response Actions

```
Breach Detected
├── Severity S1/S2 → Immediate notification (PagerDuty/Slack/SMS)
├── Severity S3/S4 → Email notification + ticket
├── Auto-escalation if no ACK within threshold
├── Post-breach: root cause analysis within 24h
└── Post-breach: remediation plan within 48h
```

---

## 8. Data Quality Rules per Priority

| Priority | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| **P1** | ≥ 99.9% | Field validation + cross-source | < 1s | ECS schema enforced | Schema check on ingest |
| **P2** | ≥ 98% | API response validation | < 30s | Cross-source correlation | Model drift monitor |
| **P3** | ≥ 95% | Report accuracy | < 5 min | Audit format | Template match |
| **P4** | ≥ 90% | Historical consistency | < 1 hour | Archive format | Format check |

### DQ Enforcement Points

| Pipeline Stage | DQ Check | Action on Failure |
|---------------|----------|-------------------|
| Ingestion (UC1) | Schema validation, source allowlist | Quarantine + error alert |
| Decoding (UC2) | Field extraction accuracy > 99% | Fallback decoder + log error |
| Correlation (UC4) | Rule match confidence > 80% | Manual review queue |
| Triage (UC7) | Model accuracy > 90% | Flag for analyst review |
| Enrichment (UC8) | API response validation | Retry + fallback source |
| Case (UC11) | Required field completeness | Block case creation |

---

## 9. Performance Targets

### 9.1 Pipeline Performance

| Metric | Target | Current (v4.2) | Gap |
|--------|--------|----------------|-----|
| Event Ingestion Rate | ≥ 1,000 EPS | ~500 EPS | ⚠️ 50% of target |
| Detection Latency (alert generation) | < 5s | ~10s (ElastAlert polling) | ❌ 2x target |
| Playbook Execution | < 30s | Not deployed | ❌ Missing |
| Data Retention (Hot) | 7 days (SSD) | 7 days | ✅ Match |
| Data Retention (Cold) | 90 days | 90 days | ✅ Match |
| ES Cluster Size | 3-node minimum | Single node | ❌ Not HA |
| Kafka Brokers | 3 brokers, RF=3 | 1 broker, RF=1 | ❌ Not HA |

### 9.2 SOC Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| Alert Volume (daily) | < 500 actionable | Post-triage count |
| Alert-to-Incident Ratio | < 10:1 | Alerts / confirmed incidents |
| SOC Analyst Utilization | 70–85% | Active investigation time / shift |
| Playbook Success Rate | > 95% | Completed / started |
| CMDB Enrichment Hit Rate | > 80% | CI found / alert enriched |

---

## 10. Consumer SLA Matrix

| Consumer | Source Topic(s) | Priority | Max Latency | Fallback |
|----------|----------------|----------|-------------|----------|
| Elasticsearch | `dcim.siem.events` | **P1** | < 1s | DLQ + retry |
| Kibana Dashboard | ES query | **P2** | < 3s | Cached view |
| ElastAlert → Tracecat | `dcim.siem.alerts` | **P1** | < 30s | Email fallback |
| Tracecat SOAR | `dcim.siem.enriched` | **P1** | < 60s | Manual trigger |
| DFIR-IRIS | `dcim.siem.incidents` | **P1** | < 120s | Manual creation |
| SOC Analyst (L1/L2) | DFIR-IRIS + Email | **P1** | < 15 min (MTTA) | PagerDuty |
| SOC Manager | Escalation queue | **P2** | < 30 min | SMS alert |
| CISO | Executive report | **P3** | < 1 hour | Email summary |
| Auditor | Compliance report | **P3** | < 24 hours | Manual export |
| CMDB | Enrichment query | **P1** | < 500ms | Cached CI |
| ITSM (ServiceNow) | Incident sync | **P2** | < 5 min | Manual ticket |
| MISP | IOC enrichment | **P2** | < 30s | Cached intel |

---

## 11. OT-Safe Enforcement Rules

| Rule | Scope | Enforcement | Override |
|------|-------|-------------|----------|
| No auto-reboot | DCIM critical assets (P1 priority) | Playbook blocks reboot action | Requires CISO approval |
| No auto-patch | Production servers | Playbook blocks patch action | Requires change ticket |
| Read-only forensics | All DCIM systems | Memory dump, PCAP = read-only | None |
| Approval gate | P1 asset containment | Manual approval before IP block | CISO override |
| Rollback required | Any config change | Playbook must include rollback | None |

---

## 12. Monitoring & Alerting Rules

### 12.1 Prometheus Metrics

| Metric | Type | Labels | Alert Threshold |
|--------|------|--------|-----------------|
| `siem_events_ingested_total` | counter | source, priority | — |
| `siem_events_ingestion_latency_seconds` | histogram | source | p99 > 2s |
| `siem_alerts_generated_total` | counter | severity, rule_id | — |
| `siem_alert_triage_latency_seconds` | histogram | model | p99 > 30s |
| `siem_playbook_execution_seconds` | histogram | playbook, status | p99 > 60s |
| `siem_incidents_created_total` | counter | severity | — |
| `siem_incidents_mtta_seconds` | histogram | severity | p95 > 15min |
| `siem_incidents_mttr_seconds` | histogram | severity | p95 > 4h |
| `siem_kafka_consumer_lag` | gauge | topic, consumer_group | > 1000 |
| `siem_es_cluster_health` | gauge | cluster | < 1 (yellow/red) |
| `siem_enrichment_hit_rate` | gauge | source | < 0.80 |
| `siem_false_positive_rate` | gauge | rule_id | > 0.10 |

### 12.2 Alert Rules (Prometheus)

```yaml
groups:
  - name: siem-slo-breach
    rules:
      - alert: SIEMIngestionLatencyHigh
        expr: histogram_quantile(0.99, siem_events_ingestion_latency_seconds) > 2
        for: 5m
        labels:
          severity: S2
        annotations:
          summary: "SIEM ingestion latency p99 > 2s"

      - alert: SIEMPlaybookTimeout
        expr: histogram_quantile(0.99, siem_playbook_execution_seconds) > 60
        for: 2m
        labels:
          severity: S2
        annotations:
          summary: "SOAR playbook execution p99 > 60s"

      - alert: SIEMMTTABreach
        expr: histogram_quantile(0.95, siem_incidents_mtta_seconds) > 900
        for: 10m
        labels:
          severity: S2
        annotations:
          summary: "SOC MTTA p95 > 15 minutes"

      - alert: SIEMKafkaConsumerLagHigh
        expr: siem_kafka_consumer_lag > 1000
        for: 5m
        labels:
          severity: S2
        annotations:
          summary: "Kafka consumer lag > 1000 messages"

      - alert: SIEMESClusterRed
        expr: siem_es_cluster_health < 1
        for: 2m
        labels:
          severity: S1
        annotations:
          summary: "Elasticsearch cluster health RED"

      - alert: SIEMFalsePositiveRateHigh
        expr: siem_false_positive_rate > 0.10
        for: 1h
        labels:
          severity: S3
        annotations:
          summary: "SIEM false positive rate > 10% — rule tuning needed"
```

---

## 13. SLA Dashboard Views

| View | Key Metrics | Refresh | Audience |
|------|------------|---------|----------|
| **SOC Real-time** | Alert volume, severity distribution, MTTA/MTTC/MTTR | Real-time | SOC Analyst |
| **SOC Operations** | Analyst utilization, queue depth, escalation rate | 5 min | SOC Manager |
| **SOAR Health** | Playbook success rate, execution time, error rate | 1 min | SOC Engineer |
| **Pipeline Health** | Ingestion EPS, consumer lag, ES cluster health | Real-time | NOC |
| **Executive Summary** | Incident trend, SLA compliance, threat landscape | Daily | CISO / Management |

---

## 14. Acceptance Criteria

| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | P1 alerts terdeteksi < 1 detik dari event masuk | Kafka consumer lag < 1000, ES write latency p99 < 1s |
| 2 | MTTA < 15 menit untuk semua S1/S2 incidents | DFIR-IRIS dashboard metrics |
| 3 | MTTC < 30 menit untuk S1 incidents | DFIR-IRIS containment timestamp |
| 4 | MTTR < 4 jam untuk S1 incidents | DFIR-IRIS resolution timestamp |
| 5 | Auto-closure rate > 60% | SOAR playbook completion stats |
| 6 | False positive rate < 10% | Alert triage statistics |
| 7 | Kafka HA: 3 brokers, RF=3 untuk semua P1 topics | Kafka cluster status |
| 8 | ES cluster: 3-node minimum | ES cluster health GREEN |
| 9 | Playbook execution < 60s p99 | Temporal workflow metrics |
| 10 | OT-safe enforcement aktif untuk semua DCIM P1 assets | Playbook audit log |
| 11 | Escalation rate < 25% | DFIR-IRIS escalation stats |
| 12 | CMDB enrichment hit rate > 80% | Enrichment pipeline metrics |
| 13 | Prometheus metrics aktif untuk 12 metric di §12.1 | Grafana dashboard live |
| 14 | SLA breach auto-escalation aktif | PagerDuty/notification test |
| 15 | Consumer SLA matrix terpenuhi untuk 12 consumers | Consumer lag + latency metrics |

---

## 15. Gap Comparison Template

### Gap: SIEM SOAR SLA & Prioritization

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Priority Model | P1-P4 with SOC severity mapping | — | ❌ Not created | P1 |
| SLA Tiers | 5 tiers (Real-time → On-demand) | — | ❌ Not created | P1 |
| MTTA/MTTC/MTTR | < 15m / < 30m / < 4h | — | ❌ Not measured | P1 |
| Kafka HA | 3 brokers, RF=3 | 1 broker, RF=1 | ❌ Not HA | P1 |
| ES Cluster | 3-node cluster | Single node | ❌ Not HA | P1 |
| Playbook SLA | < 60s execution | Not deployed | ❌ Missing | P1 |
| OT-Safe Rules | Active enforcement | Not implemented | ❌ Missing | P1 |
| Consumer SLA Matrix | 12 consumers mapped | — | ❌ Not tracked | P2 |
| Prometheus Metrics | 12 metrics | — | ❌ Not deployed | P2 |
| SLA Dashboard | 5 views | — | ❌ Not built | P2 |
| DQ Rules per Priority | 4-tier enforcement | — | ❌ Not enforced | P2 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]
