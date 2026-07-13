---
title: "CMDB SLA & Prioritization Framework (Final)"
created: 2026-06-25
updated: 2026-06-25
type: framework
status: final
tags: [sla, prioritization, cmdb, framework, ci, quality, fit041, merged]
sources:
  - dcim-wiki/concepts/priority-severity-model.md
  - dcim-wiki/concepts/dii-sla-prioritization-framework.md
  - dcim-wiki/technical-requirements/cmdb-use-case-analysis-final.md
  - dcim-wiki/reference-designs/block4-cmdb.md
  - IF-Use_Case_Analysis_CMDB-FIT041-20260121.md
  - fit041-cmdb-sla-prioritization-komparasi.md
  - cmdb-sla-prioritization-framework.md
confidence: high
purpose: >
  Framework SLA & Prioritization FINAL untuk CMDB — merged dari FIT041 (requirements layer)
  + DCIM-Wiki (implementation layer). 17 sections, 16 UCs, 4 SLA tiers, 9 DQ rules,
  governance framework, dan FIT041 traceability.
---

# CMDB SLA & Prioritization Framework (Final)

> **Purpose:** Framework terpadu FINAL untuk SLA, prioritas, dan kualitas data di Configuration Management Database layer. Merged dari FIT041 (Jan 2026) + DCIM-Wiki (Jun 2026).
> **Cara pakai:** Referensi utama untuk CMDB SLA, prioritasi, auto-assignment, monitoring, escalation, dan governance.
> **Merge Source:** FIT041 Use Case Analysis CMDB (Jan 2026) + DCIM-Wiki CMDB SLA Framework (Jun 2026)
> **Traceability:** FIT041 UC1 → UC6, FIT041 UC2 → UC16, FIT041 UC3 → UC7
> **Status:** Final — 0 conflicts, COMPLEMENTARY, 100% FIT041 absorbed
> **Related:** [[cmdb-use-case-analysis-final]], [[fit041-cmdb-sla-prioritization-komparasi]], [[block4-cmdb]]

---

## Table of Contents

1. [Priority Model (CI / Change / Consumer)](#1-priority-model-ci--change--consumer)
2. [CI Criticality Mapping](#2-ci-criticality-mapping)
3. [SLA Tiers (End-to-End Latency)](#3-sla-tiers-end-to-end-latency)
4. [Priority Mapping per Use Case](#4-priority-mapping-per-use-case)
5. [Auto-Assignment Logic](#5-auto-assignment-logic)
6. [Impact Scoring](#6-impact-scoring)
7. [Incident Severity (untuk Escalation)](#7-incident-severity-untuk-escalation)
8. [Kafka Topic Priority (CMDB Events)](#8-kafka-topic-priority-cmdb-events)
9. [Consumer SLA Matrix](#9-consumer-sla-matrix)
10. [SLA Monitoring & Alerting](#10-sla-monitoring--alerting)
11. [SLA Breach Handling](#11-sla-breach-handling)
12. [Data Quality per Priority](#12-data-quality-per-priority)
13. [Cache Strategy by Priority](#13-cache-strategy-by-priority)
14. [Performance Targets](#14-performance-targets)
15. [Monitoring Dashboard](#15-monitoring-dashboard)
16. [FIT041 Alignment & Traceability](#16-fit041-alignment--traceability)
17. [Governance Framework](#17-governance-framework)

---

## 1. Priority Model (CI / Change / Consumer)

| Priority | Meaning | Operational Effect | Default Latency |
|----------|---------|-------------------|-----------------|
| **P1 Critical** | CI mendukung service kritis (production DB, core switch, firewall) | Real-time sync, write-through cache, immediate propagation | < 100ms |
| **P2 High** | CI mendukung service penting (staging, monitoring, backup) | Fast sync, high accuracy | < 500ms |
| **P3 Medium** | CI untuk planning, audit, reporting | Batch acceptable | < 5 menit |
| **P4 Supporting** | CI historical, reference, documentation | Async / scheduled | > 1 jam |

---

## 2. CI Criticality Mapping

| CI Type | Default Criticality | P1 Example | P2 Example |
|---------|--------------------:|------------|------------|
| Server | High | Prod DB server | Dev/test server |
| NetworkDevice | Critical | Core switch, firewall | Access switch |
| Storage | High | SAN primary | NAS archive |
| VM | Medium | Prod VM | Dev VM |
| Application | High | ERP, CRM | Internal tool |
| Service | Critical | DNS, AD, email | Monitoring |
| Rack | Medium | Active rack | Spare rack |
| PatchPanel | Low | — | — |
| UPS | Critical | Main UPS | Sub-UPS |
| PDU | High | Main PDU | Branch PDU |

### CI Criticality → Priority Assignment

```
Critical → P1 (real-time propagation, cache write-through)
High     → P2 (fast sync, cache TTL 30s)
Medium   → P3 (batch sync, cache TTL 5 min)
Low      → P4 (async, cache TTL 1 hour)
```

---

## 3. SLA Tiers (End-to-End Latency)

| Tier | Latency | Use Cases | Processing Mode |
|------|---------|-----------|-----------------|
| **Tier 1 (Real-time)** | < 50ms | UC1 CI CRUD, UC4 Relationships | PostgreSQL direct query + Redis write-through |
| **Tier 2 (Near-RT)** | < 200ms | UC5 Topology, UC13 NOC Dashboard | Redis cache + PostgreSQL fallback |
| **Tier 3 (Near-RT)** | < 500ms | UC6 Impact Analysis, UC9 DI&I Sync, UC14 SIEM | PostgreSQL + graph traversal |
| **Tier 4 (Batch)** | < 1s | UC3 Bulk, UC7 Asset Recon, UC8 Discovery Recon, UC12 DQ | Batch processing |

### Tier Definitions

- **Tier 1**: API call langsung ke PostgreSQL/Redis, response synchronous, write-through cache
- **Tier 2**: Read dari Redis cache, fallback ke PostgreSQL, cache warming async
- **Tier 3**: Query kompleks (graph traversal, reconciliation), timeout 500ms, fallback ke cached result
- **Tier 4**: Batch job berjadwal, idempotent, retry enabled, DLQ untuk failures

---

## 4. Priority Mapping per Use Case

| Use Case | Priority | SLA Tier | Completeness | Timeliness | Data Quality |
|----------|----------|----------|-------------|------------|--------------|
| UC1 CI CRUD | **P1** | Tier 1 (< 50ms) | ≥ 99% | Real-time | Schema + referential |
| UC2 CI Lifecycle | **P1** | Tier 1 (< 100ms) | 100% | Real-time | Schema + business rules |
| UC3 Bulk Import/Export | P3 | Tier 4 (< 1s/rec) | ≥ 95% | Batch | Schema validation |
| UC4 Relationship Mgmt | **P1** | Tier 1 (< 50ms) | ≥ 98% | Real-time | Schema + no cycles |
| UC5 Topology Viz | P2 | Tier 2 (< 200ms) | ≥ 95% | Near-RT | Cached + consistent |
| UC6 Impact Analysis | **P1** | Tier 3 (< 500ms) | 100% | Near-RT | Scoring model accurate |
| UC7 Asset Reconciliation | **P1** | Tier 4 (daily) | ≥ 95% | Daily batch | Serial matching |
| UC8 Discovery Recon | **P1** | Tier 4 (hourly) | ≥ 88% | Hourly | IP/serial matching |
| UC9 DI&I Gateway Sync | **P1** | Tier 3 (< 10s) | ≥ 99% | Near-RT | Schema + delta detect |
| UC10 Service Mapping | P2 | Tier 3 (< 1s) | ≥ 95% | Near-RT | Dependency accuracy |
| UC11 Health Dashboard | P2 | Tier 2 (< 1s) | ≥ 95% | Near-RT | Cache hit > 80% |
| UC12 Data Quality Mgmt | P3 | Tier 4 (daily) | ≥ 90% | Daily batch | 9 quality rules |
| UC13 NOC Dashboard | **P1** | Tier 2 (< 5s) | ≥ 99% | Near-RT | Real-time CI status |
| UC14 SIEM Enrichment | **P1** | Tier 3 (< 1s) | ≥ 99.9% | Real-time | CI context accurate |
| UC15 Workflow Automation | P2 | Tier 3 (< 30s) | ≥ 95% | Near-RT | Impact score accurate |
| UC16 Audit & Compliance | P3 | Tier 4 (async) | 100% | Real-time logging | All changes tracked |

### Priority Distribution

| Priority | Count | Use Cases |
|----------|-------|-----------|
| **P1 Critical** | 9 | UC1, UC2, UC4, UC6, UC7, UC8, UC9, UC13, UC14 |
| **P2 High** | 4 | UC5, UC10, UC11, UC15 |
| **P3 Medium** | 3 | UC3, UC12, UC16 |
| **P4 Supporting** | 0 | — |

---

## 5. Auto-Assignment Logic

### 5.1 CI Priority Assignment

Priority diassign otomatis berdasarkan CI criticality dan type:

```yaml
# cmdb-priority-rules.yaml
rules:
  - name: critical_infrastructure
    condition:
      ci_type: ["NetworkDevice", "UPS", "PDU"]
      criticality: "critical"
    action:
      set_priority: "P1"
      set_cache_mode: "write-through"
      set_sync_mode: "real-time"

  - name: production_servers
    condition:
      ci_type: ["Server", "Storage"]
      criticality: ["critical", "high"]
    action:
      set_priority: "P1"
      set_cache_mode: "write-through"
      set_sync_mode: "real-time"

  - name: application_services
    condition:
      ci_type: ["Application", "Service"]
      criticality: ["critical", "high"]
    action:
      set_priority: "P1"
      set_cache_mode: "write-through"
      set_sync_mode: "real-time"

  - name: standard_infrastructure
    condition:
      ci_type: ["Server", "Storage", "VM"]
      criticality: "medium"
    action:
      set_priority: "P2"
      set_cache_mode: "TTL-30s"
      set_sync_mode: "fast-sync"

  - name: supporting_assets
    condition:
      ci_type: ["Rack", "PatchPanel"]
    action:
      set_priority: "P3"
      set_cache_mode: "TTL-5min"
      set_sync_mode: "batch"
```

### 5.2 Change Priority Assignment

```python
def _assign_change_priority(self, change: dict) -> str:
    """Assign priority based on change impact."""
    ci_priority = change.get("ci_priority", "P3")
    change_type = change.get("change_type", "")

    if change_type == "lifecycle" and ci_priority == "P1":
        return "P1"  # Status change on critical CI
    elif change_type == "relationship" and ci_priority in ["P1", "P2"]:
        return "P2"  # Relationship change on important CI
    elif change_type == "attribute":
        return "P3"  # Attribute update
    else:
        return "P4"  # Bulk/import changes
```

### 5.3 Priority Override

- Source system dapat override via field `metadata.priority`
- DI&I Gateway mengirim priority dari enrichment layer
- Manual override oleh admin (role: `ci.admin`) dengan audit trail

---

## 6. Impact Scoring

Impact score (0–10) digunakan untuk triage dan eskalasi:

```python
def _calculate_ci_impact(self, ci: dict) -> float:
    """Calculate CI impact score for prioritization."""
    base = 5.0

    # CI type adjustment
    type_adj = {
        "NetworkDevice": 3, "UPS": 3, "PDU": 2,
        "Server": 2, "Storage": 2, "Service": 2,
        "Application": 1, "VM": 1,
        "Rack": 0, "PatchPanel": -1
    }
    base += type_adj.get(ci.get("ci_type", ""), 0)

    # Dependency count adjustment
    dep_count = ci.get("dependency_count", 0)
    if dep_count > 10:
        base += 2
    elif dep_count > 5:
        base += 1

    # Lifecycle status adjustment
    status = ci.get("status", "")
    if status == "Active":
        base += 1
    elif status == "Maintenance":
        base -= 1

    return max(0, min(10, base))
```

### Impact Score Thresholds

| Score | Action |
|-------|--------|
| 8–10 | Immediate sync, P1 ticket, real-time propagation |
| 5–7 | Fast sync, P2 ticket, cache write-through |
| 2–4 | Normal queue, P3 ticket, batch processing |
| 0–1 | Low priority, background, cache TTL 1 hour |

---

## 7. Incident Severity (untuk Escalation)

| Severity | Meaning | Default Response | Trigger |
|----------|---------|-----------------|---------|
| **S1 Critical** | CMDB total failure / P1 CI data loss | Immediate triage & escalation | CMDB API down / data corruption |
| **S2 High** | CMDB degraded / P1 sync failure | Fast owner assignment | API latency > 500ms / sync lag > 100 |
| **S3 Medium** | Reconciliation drift / cache inconsistency | Planned remediation | Quality score < 80% / cache hit < 70% |
| **S4 Low** | Ad-hoc query / minor data issue | Normal queue | Non-urgent request |

---

## 8. Kafka Topic Priority (CMDB Events)

| Topic | Priority | Partition Key | Retention | Use Case |
|-------|----------|---------------|-----------|----------|
| `dcim.cmdb.updates` | **P1** | ci_id | 90 hari | Real-time CI sync |
| `dcim.cmdb.changes` | **P1** | ci_id | 90 hari | Change tracking |
| `dcim.cmdb.relationships` | **P1** | source_ci_id | 90 hari | Relationship updates |
| `dcim.cmdb.reconciliation` | P2 | ci_id | 30 hari | Reconciliation results |
| `dcim.cmdb.health` | P2 | ci_id | 30 hari | Health scores |
| `dcim.cmdb.bulk` | P3 | batch_id | 7 hari | Bulk operations |
| `dcim.cmdb.audit` | P3 | ci_id | 1 tahun | Audit trail |
| `dcim.cmdb.dlq` | **P1** | event_id | 30 hari | Failed events |

---

## 9. Consumer SLA Matrix

| Consumer | Input Topics | Required SLA | Protocol | Cache Mode |
|----------|-------------|-------------|----------|------------|
| **NOC Dashboard** | `dcim.cmdb.updates` | Tier 2 (< 5s) | WebSocket | Real-time push |
| **SIEM (Wazuh/ES)** | `dcim.cmdb.updates` | Tier 3 (< 1s) | REST API | Write-through |
| **Workflow Engine** | `dcim.cmdb.changes` | Tier 3 (< 30s) | REST API | TTL 30s |
| **Analytics & AI** | `dcim.cmdb.reconciliation` | Tier 4 (batch) | Direct read | TTL 5 min |
| **Asset Repository** | `dcim.cmdb.relationships` | Tier 3 (daily + event) | REST API | TTL 1 hour |
| **ITSM (iTop)** | `dcim.cmdb.updates` | Tier 4 (daily) | Bulk API | TTL 1 hour |
| **Dashboard** | `dcim.cmdb.health` | Tier 2 (< 1s) | WebSocket | Real-time push |
| **BI Tools** | Batch exports | Tier 4 (< 60 min) | Export API | N/A |
| **Compliance** | `dcim.cmdb.audit` | Tier 4 (async) | REST API | N/A |

---

## 10. SLA Monitoring & Alerting

### 10.1 Per-Operation Latency SLA

| Operation | SLA Target | Alert Threshold |
|-----------|-----------|----------------|
| GET /cmdb/ci/{id} | p99 < 50ms | > 50ms |
| GET /cmdb/ci (list) | p99 < 200ms | > 200ms |
| POST /cmdb/ci | p99 < 100ms | > 100ms |
| GET /cmdb/topology/{id} | p99 < 200ms | > 200ms |
| GET /cmdb/impact/{id} | p99 < 500ms | > 500ms |
| GET /cmdb/health | p99 < 1s | > 1s |
| Reconciliation (full) | < 1 hour | > 1 hour |
| Cache hit rate | > 80% | < 70% |

### 10.2 Availability SLA

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| CMDB API | 99.9% | < 15 min | 0 (PostgreSQL WAL) |
| PostgreSQL | 99.95% | < 5 min | 0 (streaming replication) |
| Redis Cache | 99.9% | < 1 min | N/A (rebuildable) |
| Topology Engine | 99.9% | < 5 min | 0 (from PostgreSQL) |

### 10.3 Prometheus Alert Rules

```yaml
groups:
  - name: cmdb_sla_alerts
    rules:
      - alert: CMDBApiLatencyHigh
        expr: histogram_quantile(0.99, rate(cmdb_api_latency_seconds_bucket[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CMDB API p99 latency > 50ms"

      - alert: CMDBTopologyLatencyHigh
        expr: histogram_quantile(0.99, rate(cmdb_topology_latency_seconds_bucket[5m])) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CMDB Topology p99 latency > 200ms"

      - alert: CMDBImpactLatencyHigh
        expr: histogram_quantile(0.99, rate(cmdb_impact_latency_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "CMDB Impact Analysis p99 latency > 500ms"

      - alert: CMDBCacheHitRateLow
        expr: cmdb_cache_hit_rate < 0.70
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "CMDB cache hit rate < 70%"

      - alert: CMDBReconciliationDriftHigh
        expr: cmdb_reconciliation_drift_ratio > 0.12
        for: 30m
        labels:
          severity: critical
        annotations:
          summary: "CMDB reconciliation drift > 12%"

      - alert: CMDBApiAvailabilityLow
        expr: (1 - rate(cmdb_api_errors_total[5m]) / rate(cmdb_api_requests_total[5m])) < 0.999
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "CMDB API availability < 99.9%"
```

---

## 11. SLA Breach Handling

### 11.1 Breach Detection Flow

```
Metric Check → Threshold Breach → Alert Firing → Escalation
                                                    │
                                        ┌───────────┼───────────┐
                                        ▼           ▼           ▼
                                    S4: Log     S3: Auto    S2: Alert
                                    + Monitor   Remediate   Owner
                                                        │
                                                        ▼
                                                    S1: War Room
                                                    + Incident
```

### 11.2 Escalation Matrix

| SLA Tier | Breach → Auto Action | Breach → Escalation |
|----------|---------------------|---------------------|
| Tier 1 | Retry + DLQ + cache fallback | PagerDuty P1, on-call < 5 min |
| Tier 2 | Cache serve stale + alert | Slack alert, owner < 15 min |
| Tier 3 | Retry next cycle + DLQ | Dashboard flag, owner < 1 hour |
| Tier 4 | Retry in next batch | Email report, next business day |

### 11.3 SLA Breach → Ticket Routing

| Priority | Ticket Type | Assignment | Resolution SLA |
|----------|------------|------------|----------------|
| P1 | Incident | CMDB Admin → On-Call | 1 jam |
| P2 | Problem | Data Engineer | 4 jam |
| P3 | Service Request | Data Engineer | 1 hari kerja |
| P4 | Task | Scheduled | Sprint berikutnya |

---

## 12. Data Quality per Priority

| Priority | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| P1 | ≥ 99% | Serial unique, IP valid | Real-time | CI type enum valid | CHECK + referential |
| P2 | ≥ 98% | Source/target exist | < 500ms | Type in allowed values | Schema + business rules |
| P3 | ≥ 95% | Batch-valid | < 5 min | Consistent format | Schema |
| P4 | ≥ 90% | Best-effort | < 1 hour | Async-valid | Basic format |

### 9 Data Quality Rules

| Rule | Dimension | Check | Target |
|------|-----------|-------|--------|
| DQ-01 | Uniqueness | ci_id UNIQUE constraint | 100% |
| DQ-02 | Referential Integrity | source_ci_id, target_ci_id exist | 100% |
| DQ-03 | No Self-Relationship | source ≠ target | 100% |
| DQ-04 | No Containment Cycles | BFS cycle detection | 100% |
| DQ-05 | Mandatory Fields | ci_id, name, ci_type, status not null | 100% |
| DQ-06 | Lifecycle Transition | Planned→Active→Maintenance→Retired→Disposed | 100% |
| DQ-07 | IP Format | IPv4/IPv6 validation | 100% |
| DQ-08 | Serial Uniqueness | serial_number unique per CI type | 100% |
| DQ-09 | Reconciliation Match | CI ↔ Asset match rate > 95% | > 95% |

---

## 13. Cache Strategy by Priority

| Priority | Cache Mode | TTL | Invalidation |
|----------|-----------|-----|-------------|
| P1 | Write-through | Instant | On every write |
| P2 | Read-through | 30s | TTL + event-driven |
| P3 | Lazy-load | 5 min | TTL only |
| P4 | Lazy-load | 1 hour | TTL only |

### Cache Invalidation Events

```yaml
invalidation_rules:
  - trigger: "ci.update"
    action: "invalidate_ci_cache"
    scope: "ci_id"
    propagation: "write-through for P1, event-driven for P2"

  - trigger: "relationship.update"
    action: "invalidate_topology_cache"
    scope: "source_ci_id + target_ci_id"
    propagation: "write-through for P1, event-driven for P2"

  - trigger: "reconciliation.complete"
    action: "invalidate_all_reconciliation_cache"
    scope: "global"
    propagation: "batch invalidation"
```

---

## 14. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total CIs | ≥ 150,000 | CI count in PostgreSQL |
| Total Relationships | ≥ 500,000 | Relationship count |
| API Throughput | 1,000 req/s | Aggregate |
| Topology Depth | 10 levels | Max traversal |
| Cache Hit Rate | > 80% | Redis |
| Reconciliation Match | > 95% | CI ↔ Asset |
| Quality Score | > 80% | 9 rules scorecard |
| API p99 Latency | < 500ms | All endpoints |
| DLQ Rate | < 1% | Failed / total events |

---

## 15. Monitoring Dashboard

### CMDB Health Metrics

| Metric | Source | Refresh |
|--------|--------|---------|
| CI Count by Type | PostgreSQL | Real-time |
| CI Count by Status | PostgreSQL | Real-time |
| Relationship Count | PostgreSQL | Real-time |
| Reconciliation Match Rate | Reconciliation engine | Daily |
| Cache Hit Rate | Redis | Real-time |
| API Latency (p50, p95, p99) | Prometheus | Real-time |
| API Error Rate | Prometheus | Real-time |
| DLQ Count | Kafka | Real-time |
| Data Quality Score | DQ engine | Daily |

---

## 16. FIT041 Alignment & Traceability

### 16.1 Merge Summary

| Aspek | FIT041 | DCIM-Wiki | Merged |
|-------|--------|-----------|--------|
| Use Cases | 3 (operational) | 16 (technical) | **16** (FIT041 UCs absorbed) |
| Priority Model | High/Medium (2 levels) | P1-P4 (4 levels) | **P1-P4** (more granular) |
| SLA Tiers | Not defined | 4 tiers | **4 tiers** |
| Latency Targets | 1 (< 500ms) | 7 endpoints | **7 endpoints** |
| Data Quality | Not defined | 9 rules | **9 rules** |
| Acceptance Criteria | Not defined | 18 items | **18 items** |
| API Endpoints | Concept | 26 endpoints | **26 endpoints** |
| Consumer SLA | Not defined | 9 consumers | **9 consumers** |
| Monitoring | Not defined | 6 Prometheus rules | **6 rules** |
| Escalation | Not defined | S1-S4 + ticket routing | **Full matrix** |

### 16.2 FIT041 UCs Absorbed

| FIT041 UC | FIT041 Priority | DCIM-Wiki UC | DCIM-Wiki Priority | Enrichment |
|-----------|----------------|--------------|-------------------|------------|
| **UC1:** Incident Impact Analysis | High | **UC6:** Impact Analysis | P1 Critical | Actors (DCIM Operator, Incident Mgmt System, CMDB), pre-conditions (CI relationships akurat), flow (traverse → map → output), success criteria (30 detik) |
| **UC2:** Change Verification/Audit | Medium | **UC16:** Audit Trail & Compliance | P3 Medium | Actors (Change Mgmt System, Auditor, DCIM Operator), pre-conditions (configuration baseline), flow (input → fetch → compare → verify → audit), drift detection (15 menit) |
| **UC3:** Asset Lifecycle/Capacity Planning | High | **UC7:** Asset Reconciliation | P1 Critical | Actors (Asset Manager, Financial System, Capacity Planning Tool), pre-conditions (lifecycle attributes), flow (query → match → integrate → update), financial integration (quarterly export) |

### 16.3 FIT041 Unique Concepts Adopted

| Concept | Source | Adopted In | Status |
|---------|--------|-----------|--------|
| Drift detection (15 min) | FIT041 UC2 | UC16 acceptance criteria | ✅ Adopted |
| Financial System integration | FIT041 UC3 actors | UC7 financial integration | ✅ Adopted |
| Capacity Planning Tool | FIT041 UC3 actors | UC13 downstream consumer | ✅ Adopted |
| Configuration Baseline | FIT041 UC2 | UC16 lifecycle tracking | ✅ Adopted |
| 30-second impact list | FIT041 UC1 success | UC6 acceptance criteria | ✅ Adopted |

### 16.4 FIT041 Requirements Coverage

| # | FIT041 Requirement | Status | DCIM-Wiki Coverage |
|---|-------------------|--------|-------------------|
| 1 | Dukungan model data CI (fisik, virtual, logis) | ✅ Covered | 10 CI types |
| 2 | Database grafis / mesin pemetaan hubungan | ✅ Covered | Topology Engine, 4 algorithms |
| 3 | Penelusuran hubungan CI < 500ms | ✅ Covered | UC6 p99 < 500ms |
| 4 | Minimal 150,000 CIs + 500,000 relationships | ✅ Covered | Capacity targets |
| 5 | RBAC to restrict update permissions | ✅ Covered | 5 roles matrix |
| 6 | HA cluster RTO < 15 minutes | ✅ Covered | PG RTO < 5 min, API RTO < 15 min |

**Kesimpulan:** 6/6 FIT041 requirements = **100% covered**.

---

## 17. Governance Framework

### 17.1 Roles & Responsibilities (RACI)

| Activity | CMDB Admin | Data Engineer | DCIM Operator | Auditor | Capacity Planner |
|----------|:----------:|:------------:|:-------------:|:-------:|:----------------:|
| CI CRUD Operations | **R** | C | I | I | I |
| CI Lifecycle Management | **R** | C | **A** | I | I |
| Impact Analysis | C | **R** | **A** | I | I |
| Asset Reconciliation | C | **R** | **A** | I | C |
| Discovery Reconciliation | C | **R** | **A** | I | I |
| Data Quality Management | **R** | **R** | I | I | I |
| Audit & Compliance | C | C | I | **R/A** | I |
| Capacity Planning | C | C | I | I | **R** |
| SLA Monitoring | **R** | C | **A** | I | I |
| Incident Response (S1-S2) | **R** | C | **A** | I | I |

**Legend:** R = Responsible, A = Accountable, C = Consulted, I = Informed

### 17.2 Incident Response Times

| Severity | Response Time | Update Frequency | Resolution Target |
|----------|:------------:|:----------------:|:-----------------:|
| S1 Critical | < 5 min | Every 15 min | < 1 hour |
| S2 High | < 15 min | Every 30 min | < 4 hours |
| S3 Medium | < 1 hour | Daily | < 1 business day |
| S4 Low | < 4 hours | Weekly | < 1 sprint |

### 17.3 Reporting Framework

| Report | Frequency | Audience | Content |
|--------|:---------:|----------|---------|
| CMDB Health Dashboard | Real-time | NOC, DCIM Operator | CI counts, quality score, cache hit rate |
| SLA Compliance Report | Daily | CMDB Admin, Data Engineer | Latency p99, availability, DLQ rate |
| Reconciliation Status | Daily | Data Engineer | Match rate, drift ratio, conflicts |
| Data Quality Scorecard | Weekly | CMDB Admin, Auditor | 9 DQ rules score, orphan CIs, trends |
| Capacity Planning Report | Quarterly | Capacity Planner, Management | CI growth, utilization, deprecation forecast |
| Audit Compliance Report | Quarterly | Auditor, Management | Drift incidents, lifecycle compliance, RBAC audit |

### 17.4 Review Process

| Review | Frequency | Participants | Agenda |
|--------|:---------:|-------------|--------|
| CMDB Health Review | Weekly | CMDB Admin, Data Engineer | Quality score, DQ issues, cache performance |
| SLA Performance Review | Monthly | CMDB Admin, DCIM Operator, Data Engineer | SLA compliance, breach incidents, alert tuning |
| Reconciliation Review | Monthly | Data Engineer, Asset Manager | Match rate trends, conflict resolution, DQ rules |
| Strategic CMDB Review | Quarterly | All stakeholders | Capacity, roadmap, governance, FIT041 alignment |

### 17.5 Glossary

| Term | Definition |
|------|-----------|
| **CI (Configuration Item)** | Any component that needs to be managed to deliver an IT service |
| **CMDB** | Configuration Management Database — SSOT untuk CIs dan relationships |
| **Configuration Baseline** | Authorized version of a CI's configuration (FIT041) |
| **Drift** | Unauthorized deviation from configuration baseline (FIT041) |
| **Impact Analysis** | Process to determine which services/CIs are affected by a change or failure |
| **Reconciliation** | Process to match CI data with Asset Repository or Discovery data |
| **Topology** | Graph representation of CI relationships and dependencies |
| **SLA Tier** | Classification of latency requirements (Tier 1 real-time → Tier 4 batch) |
| **Priority** | Classification of CI criticality (P1 critical → P4 supporting) |
| **DLQ** | Dead Letter Queue — storage untuk events yang gagal diproses |
| **Write-through Cache** | Cache update同步 pada setiap write operation |
| **Impact Score** | Numerical score (0-10) untuk triage dan eskalasi CI impact |

---

## Related

- [[priority-severity-model]] — Global priority & severity model
- [[dii-sla-prioritization-framework]] — DI&I SLA framework
- [[cmdb-use-case-analysis-final]] — CMDB use case analysis (16 UCs)
- [[block4-cmdb]] — CMDB reference design spec
- [[cmdb-data-model]] — CI data model
- [[cmdb-reconciliation-runbook]] — Reconciliation procedures
- [[data-quality-framework]] — Data quality dimensions
- [[workflow-automation]] — Escalation & ticket routing
- [[fit041-cmdb-sla-prioritization-komparasi]] — FIT041 comparison document
- [[fit041-cmdb-use-case-komparasi]] — FIT041 UC analysis comparison
- [[IF-Use_Case_Analysis_CMDB-FIT041-20260121]] — FIT041 source document

---

> **Status:** Final — CMDB SLA & Prioritization Framework (merged FIT041 + DCIM-Wiki)
> **Date:** 2026-06-25
> **Method:** MCP Sequential Thinking (3 steps) + dcim-comparison skill + Context7 docs
> **Result:** 17 sections, 16 UCs, 4 SLA tiers, 9 DQ rules, governance framework, 0 conflicts
> **FIT041 Coverage:** 100% (6/6 requirements, 3/3 UCs absorbed)
> **DCIM-Wiki Supersession:** 100% (all FIT041 content covered + 13 additional UCs)
