---
title: Asset Repository SLA & Prioritization Framework FINAL
created: 2026-06-25
updated: 2026-06-25
type: framework
status: final
tags: [sla, prioritization, asset-repository, framework, quality, enrichment, governance, compliance]
sources:
  - dcim-wiki/concepts/asset-repository-sla-prioritization-framework.md
  - dcim-wiki/concepts/priority-severity-model.md
  - dcim-wiki/concepts/dii-sla-prioritization-framework.md
  - dcim-wiki/concepts/cmdb-sla-prioritization-framework.md
  - dcim-wiki/technical-requirements/asset-repository-use-case-analysis-final.md
  - dcim-wiki/reference-designs/block3-asset-repository.md
  - dcim-wiki/technical-requirements/fit041-asset-repository-komparasi.md
  - dcim-wiki/technical-requirements/fit041-asset-sla-prioritization-komparasi.md
  - IF-SLA__Prioritization_Asset_Repository-FIT041-20260126.md
confidence: high
purpose: >
  Final version SLA & Prioritization Framework untuk Asset Repository.
  Merged dari DCIM-Wiki (technical/operational layer) + FIT041 (business/compliance layer).
  17 sections, 15 use cases, 10 DQ rules, 5 business KPIs, RACI governance.
---

# Asset Repository SLA & Prioritization Framework FINAL

> **Purpose:** Framework terpadu SLA, prioritas, kualitas data, dan governance untuk Asset Repository layer.
> **Merged from:** DCIM-Wiki (technical/operational) + FIT041 (business/compliance).
> **Cara pakai:** Review per section untuk memahami SLA targets, priority assignment, monitoring, dan governance.
> **Depends on:** Block 1 (Infrastructure), Block 3 (Asset Repository Reference Design), PostgreSQL, Redis, Kafka

---

## Merge Summary

| Aspek | DCIM-Wiki | FIT041 | Merged |
|-------|-----------|--------|--------|
| Sections | 15 (§1-§15) | 6 | **17** (§1-§17) |
| Use Cases | 15 (UC1-UC15) | Implied | **15** (UC1-UC15) |
| SLA Tiers | 4 (Tier 1-4) | Business targets | **4** + business layer |
| DQ Rules | 10 | Attribute priority | **10** + hierarchy |
| Business KPIs | 0 | 5 | **5** (adopted) |
| RACI Roles | 0 | 5 roles | **5** (adopted) |
| Reporting | 0 | Daily/Quarterly/Annual | **3 cadences** (adopted) |
| Conflicts | — | — | **0** |

---

## Table of Contents

1. [Priority Model](#1-priority-model-asset--change--consumer)
2. [Asset Criticality Mapping](#2-asset-criticality-mapping)
3. [SLA Tiers](#3-sla-tiers-end-to-end-latency)
4. [Priority Mapping per Use Case](#4-priority-mapping-per-use-case)
5. [Auto-Assignment Logic](#5-auto-assignment-logic)
6. [Impact Scoring](#6-impact-scoring)
7. [Incident Severity](#7-incident-severity-untuk-escalation)
8. [Kafka Topic Priority](#8-kafka-topic-priority-asset-repository-events)
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

## 1. Priority Model (Asset / Change / Consumer)

| Priority | Meaning | Operational Effect | Default Latency |
|----------|---------|-------------------|-----------------|
| **P1 Critical** | Asset mendukung service kritis (production servers, core network, UPS) — CRUD langsung, NOC dashboard, CMDB enrichment | Real-time sync, write-through cache, immediate propagation | < 50ms |
| **P2 High** | Asset penting (staging, monitoring, warranty tracking, contract management) — lifecycle transitions, warranty checks | Fast sync, high accuracy | < 200ms |
| **P3 Medium** | Planning, audit, reporting — bulk import, depreciation, compliance reports | Batch acceptable | < 500ms |
| **P4 Supporting** | Historical, reference, background — legacy data, archived records | Async / scheduled | > 1 jam |

> **FIT041 Traceability:** Prioritas also considers lifecycle phase (FIT041 §3.1):
> - P1: Aset aktif di Production Rack, mendukung layanan Tier 1
> - P2: Aset di bawah Garansi/Kontrak, Aset Cadangan
> - P3: Aset Decommissioned/Archival
> - P4: Aset Retired, nilai rendah

---

## 2. Asset Criticality Mapping

| Asset Category | Default Criticality | P1 Example | P2 Example |
|---------------|--------------------:|------------|------------|
| Server | High | Prod DB server, App server | Dev/test server |
| NetworkDevice | Critical | Core switch, firewall, router | Access switch |
| Storage | High | SAN primary, NAS production | NAS archive |
| UPS | Critical | Main UPS | Sub-UPS |
| PDU | High | Main PDU | Branch PDU |
| Rack | Medium | Active rack (contains P1 assets) | Spare rack |
| Camera/NVR | Medium | Security-critical camera | Monitoring camera |
| PatchPanel | Low | — | — |

### Asset Criticality → Priority Assignment

```
Critical → P1 (real-time propagation, cache write-through)
High     → P2 (fast sync, cache TTL 30s)
Medium   → P3 (batch sync, cache TTL 5 min)
Low      → P4 (async, cache TTL 1 hour)
```

---

## 3. SLA Tiers (End-to-End Latency)

| Tier | Latency | Throughput | Use Cases | Processing Mode |
|------|---------|-----------|-----------|-----------------|
| **Tier 1 (Real-time)** | < 50ms p99 | 1000 req/s | UC1 GET, UC12 Enrichment | PostgreSQL direct query + Redis write-through |
| **Tier 2 (Near-RT)** | < 200ms p99 | 200 req/s | UC3 Search, UC4 Lifecycle, UC8 Warranty, UC9 Contract | Redis cache + PostgreSQL fallback |
| **Tier 3 (Near-RT)** | < 500ms p99 | 100 req/s | UC5 Status Transition, UC6 Audit Trail, UC13 NOC Dashboard | PostgreSQL + indexed queries |
| **Tier 4 (Batch)** | < 1s/record | Batch | UC2 Bulk Import, UC7 Depreciation, UC10 Recon, UC11 Discovery, UC15 Compliance | Batch processing / scheduled jobs |

### Tier Definitions

- **Tier 1**: API call langsung ke PostgreSQL/Redis, response synchronous, write-through cache. Untuk CRUD read dan enrichment API.
- **Tier 2**: Read dari Redis cache, fallback ke PostgreSQL, cache warming async. Untuk search, lifecycle, warranty, contract queries.
- **Tier 3**: Query dengan index, audit trail write, dashboard aggregation. Timeout 500ms, fallback ke cached result.
- **Tier 4**: Batch job berjadwal, idempotent, retry enabled, DLQ untuk failures.

> **FIT041 Dual Definition — Update Latency:**
> - **System Response Latency** (DCIM-Wiki): < 50ms (Tier 1) — waktu API call → response
> - **Business Process Latency** (FIT041 §2.2): ≤ 4 jam kerja — waktu perubahan fisik aset → data di repository diperbarui
> - Keduanya valid, mengukur aspek berbeda. Target compliance menggunakan business process latency (§16).

---

## 4. Priority Mapping per Use Case

| Use Case | Priority | SLA Tier | Completeness | Timeliness | Data Quality |
|----------|----------|----------|-------------|------------|--------------|
| UC1 Asset CRUD | **P1** | Tier 1 (< 50ms) | ≥ 99% | Real-time | Schema + referential + uniqueness |
| UC2 Bulk Import/Export | P3 | Tier 4 (< 1s/rec) | ≥ 95% | Batch | Schema + row-level validation |
| UC3 Search & Reporting | P2 | Tier 2 (< 200ms) | 100% | < 200ms | Index sync + query match |
| UC4 Lifecycle Management | **P1** | Tier 2 (< 200ms) | 100% | Real-time | Source-consistent + transition rules |
| UC5 Status Transition | **P1** | Tier 3 (< 500ms) | 100% | Real-time | State machine valid |
| UC6 Audit Trail | **P1** | Tier 3 (< 500ms) | 100% | Real-time | Immutable + field-level |
| UC7 Depreciation Calc | P3 | Tier 4 (daily) | 100% | Batch | Formula correct + method-consistent |
| UC8 Warranty Tracking | P2 | Tier 2 (< 200ms) | ≥ 98% | Real-time | Dates match + status accurate |
| UC9 Contract Management | P2 | Tier 2 (< 200ms) | ≥ 95% | Real-time | Vendor/PO linked |
| UC10 CMDB Reconciliation | **P1** | Tier 4 (daily) | 100% | Daily batch | Match rate > 95% |
| UC11 Discovery Reconciliation | **P1** | Tier 4 (hourly) | 100% | Hourly | Discovery source correct |
| UC12 Enrichment API | **P1** | Tier 1 (< 50ms) | 100% | < 200ms | Cache hit > 95% |
| UC13 NOC Dashboard | **P1** | Tier 3 (< 5s) | 100% | < 5s | Dashboard-consistent |
| UC14 Workflow Automation | P2 | Tier 3 (< 30s) | 100% | < 30s | Trigger correct + event-consistent |
| UC15 Compliance Reporting | P3 | Tier 4 (daily) | 100% | Batch | Report-consistent + format-valid |

### Priority Distribution

| Priority | Count | Use Cases |
|----------|-------|-----------|
| **P1 Critical** | 8 | UC1, UC4, UC5, UC6, UC10, UC11, UC12, UC13 |
| **P2 High** | 4 | UC3, UC8, UC9, UC14 |
| **P3 Medium** | 3 | UC2, UC7, UC15 |
| **P4 Supporting** | 0 | — |

---

## 5. Auto-Assignment Logic

### 5.1 Asset Priority Assignment

Priority diassign otomatis berdasarkan asset criticality dan category:

```yaml
# asset-priority-rules.yaml
rules:
  - name: critical_infrastructure
    condition:
      asset_category: ["NetworkDevice", "UPS", "PDU"]
      criticality: "critical"
    action:
      set_priority: "P1"
      set_cache_mode: "write-through"
      set_sync_mode: "real-time"

  - name: production_servers
    condition:
      asset_category: ["Server", "Storage"]
      criticality: ["critical", "high"]
    action:
      set_priority: "P1"
      set_cache_mode: "write-through"
      set_sync_mode: "real-time"

  - name: standard_infrastructure
    condition:
      asset_category: ["Server", "Storage"]
      criticality: "medium"
    action:
      set_priority: "P2"
      set_cache_mode: "TTL-30s"
      set_sync_mode: "fast-sync"

  - name: supporting_assets
    condition:
      asset_category: ["Rack", "PatchPanel"]
    action:
      set_priority: "P3"
      set_cache_mode: "TTL-5min"
      set_sync_mode: "batch"
```

### 5.2 Change Priority Assignment

```python
def _assign_change_priority(self, change: dict) -> str:
    """Assign priority based on change impact."""
    asset_priority = change.get("asset_priority", "P3")
    change_type = change.get("change_type", "")

    if change_type == "lifecycle" and asset_priority == "P1":
        return "P1"  # Status change on critical asset
    elif change_type == "lifecycle" and asset_priority == "P2":
        return "P2"  # Status change on important asset
    elif change_type == "location":
        return "P2"  # Physical move — needs tracking
    elif change_type == "financial":
        return "P3"  # Financial attribute update
    elif change_type == "attribute":
        return "P3"  # Generic attribute update
    else:
        return "P4"  # Bulk/import changes
```

### 5.3 Priority Override

- Source system dapat override via field `metadata.priority`
- DI&I Gateway mengirim priority dari enrichment layer
- Manual override oleh admin (role: `asset.admin`) dengan audit trail

---

## 6. Impact Scoring

Impact score (0–10) digunakan untuk triage dan eskalasi:

```python
def _calculate_asset_impact(self, asset: dict) -> float:
    """Calculate asset impact score for prioritization."""
    base = 5.0

    # Asset category adjustment
    category_adj = {
        "NetworkDevice": 3, "UPS": 3, "PDU": 2,
        "Server": 2, "Storage": 2,
        "Camera": 1, "NVR": 1,
        "Rack": 0, "PatchPanel": -1
    }
    base += category_adj.get(asset.get("asset_category", ""), 0)

    # Dependency count adjustment (CIs depending on this asset)
    dep_count = asset.get("dependency_count", 0)
    if dep_count > 10:
        base += 2
    elif dep_count > 5:
        base += 1

    # Lifecycle status adjustment
    status = asset.get("lifecycle_status", "")
    if status == "deployed":
        base += 1
    elif status == "maintenance":
        base -= 1
    elif status == "retired":
        base -= 2

    # Warranty status adjustment
    if asset.get("warranty_active"):
        base += 0.5  # Under warranty — faster resolution expected

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
| **S1 Critical** | Asset Repository total failure / P1 asset data loss | Immediate triage & escalation (< 5 min) | API down / data corruption / PostgreSQL failure |
| **S2 High** | Asset Repository degraded / P1 sync failure | Fast owner assignment (< 15 min) | API latency > 200ms / cache hit < 80% / sync lag |
| **S3 Medium** | Reconciliation drift / cache inconsistency / enrichment miss | Planned remediation (< 1 hour) | Quality score < 80% / reconciliation conflicts > 20/day |
| **S4 Low** | Ad-hoc query / minor data issue / non-urgent request | Normal queue | Non-urgent request |

> **FIT041 Traceability:** FIT041 §2.3 defines slightly different resolution targets:
> - S1: FIT041 = 2 jam; DCIM-Wiki = 1 jam (stricter) → **Gunakan DCIM-Wiki 1 jam**
> - S2: FIT041 = 4 jam; DCIM-Wiki = 4 jam → **Aligned**
> - S3: FIT041 = 1 hari kerja; DCIM-Wiki = 1 hari kerja → **Aligned**
> - S4: FIT041 = 3 hari kerja; DCIM-Wiki = tidak spesifik → **Gunakan FIT041 3 hari kerja**

---

## 8. Kafka Topic Priority (Asset Repository Events)

| Topic | Priority | Partition Key | Retention | Use Case |
|-------|----------|---------------|-----------|----------|
| `dcim.asset.updates` | **P1** | asset_id | 90 hari | Real-time asset CRUD events |
| `dcim.asset.lifecycle` | **P1** | asset_id | 90 hari | Lifecycle state transitions |
| `dcim.asset.location` | **P2** | asset_id | 30 hari | Location changes |
| `dcim.asset.reconciliation` | P2 | reconciliation_id | 30 hari | Reconciliation results |
| `dcim.asset.audit` | P3 | asset_id | 1 tahun | Audit trail events |
| `dcim.asset.bulk` | P3 | batch_id | 7 hari | Bulk import results |
| `dcim.asset.warranty.alerts` | **P1** | asset_id | 30 hari | Warranty expiry alerts |
| `dcim.asset.contract.alerts` | P2 | contract_id | 30 hari | Contract renewal alerts |
| `dcim.asset.dlq` | **P1** | event_id | 30 hari | Failed events |

---

## 9. Consumer SLA Matrix

| Consumer | Input Topics | Required SLA | Protocol | Cache Mode |
|----------|-------------|-------------|----------|------------|
| **CMDB** | `dcim.asset.updates` | Tier 2 (< 200ms) | REST API (Enrichment) | TTL 15 min |
| **NOC Dashboard** | `dcim.asset.updates`, `dcim.asset.lifecycle` | Tier 3 (< 5s) | WebSocket / SSE | Real-time push |
| **Analytics & AI** | `dcim.asset.updates` | Tier 4 (batch) | Direct read / Export | TTL 5 min |
| **Workflow Engine** | `dcim.asset.lifecycle`, `dcim.asset.warranty.alerts` | Tier 3 (< 30s) | REST API / Kafka | TTL 30s |
| **ITSM (iTop)** | `dcim.asset.warranty.alerts`, `dcim.asset.contract.alerts` | Tier 3 (< 500ms) | REST API | TTL 1 hour |
| **Compliance** | `dcim.asset.audit` | Tier 4 (async) | REST API | N/A |
| **DI&I Gateway** | `dcim.asset.updates` | Tier 3 (< 5 min) | Kafka consumer | N/A |
| **BI Tools** | Batch exports | Tier 4 (< 60 min) | Export API | N/A |

---

## 10. SLA Monitoring & Alerting

### 10.1 Per-Operation Latency SLA

| Operation | SLA Target | Alert Threshold |
|-----------|-----------|----------------|
| GET /api/v1/assets/{id} | p99 < 50ms | > 50ms |
| GET /api/v1/assets (list) | p99 < 200ms | > 200ms |
| POST /api/v1/assets | p99 < 100ms | > 100ms |
| PUT /api/v1/assets/{id} | p99 < 100ms | > 100ms |
| GET /api/v1/assets/search | p99 < 200ms | > 200ms |
| GET /api/v1/assets/enrich/{id} | p99 < 50ms | > 50ms |
| POST /api/v1/assets/bulk | < 30s total | > 30s |
| Reconciliation (full) | < 1 hour | > 1 hour |
| Enrichment cache hit rate | > 95% | < 80% |

### 10.2 Availability SLA

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| Asset API | 99.9% | < 15 min | 0 (PostgreSQL WAL) |
| PostgreSQL | 99.95% | < 5 min | 0 (streaming replication) |
| Redis Cache | 99.9% | < 10 sec | N/A (rebuildable) |
| Enrichment API | 99.9% | < 5 min | 0 (from PostgreSQL) |

### 10.3 Prometheus Alert Rules

```yaml
groups:
  - name: asset_repository_sla_alerts
    rules:
      - alert: AssetAPILatencyHigh
        expr: histogram_quantile(0.99, rate(asset_api_latency_seconds_bucket[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Asset API p99 latency > 50ms"

      - alert: AssetEnrichmentLatencyHigh
        expr: histogram_quantile(0.99, rate(asset_enrichment_latency_seconds_bucket[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Asset Enrichment API p99 latency > 50ms"

      - alert: AssetEnrichmentCacheHitLow
        expr: asset_enrichment_cache_hit_ratio < 0.80
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Asset enrichment cache hit ratio < 80%"

      - alert: AssetBulkImportErrorsHigh
        expr: rate(asset_bulk_import_errors_total[1h]) > 5
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Bulk import error rate elevated"

      - alert: AssetReconciliationConflictsHigh
        expr: rate(asset_reconciliation_conflicts_total[24h]) > 20
        for: 24h
        labels:
          severity: warning
        annotations:
          summary: "High reconciliation conflict rate (> 20/day)"

      - alert: AssetWarrantyExpiring
        expr: asset_warranty_expiring_total > 10
        for: 1d
        labels:
          severity: info
        annotations:
          summary: "{{ $value }} asset warranties expiring in 30 days"

      - alert: AssetApiAvailabilityLow
        expr: (1 - rate(asset_api_errors_total[5m]) / rate(asset_api_requests_total[5m])) < 0.999
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Asset API availability < 99.9%"

      - alert: AssetPostgresFailover
        expr: pg_stat_replication_lag_seconds > 30
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL replication lag > 30s"
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
| Tier 1 | Retry + DLQ + cache fallback (serve stale) | PagerDuty P1, on-call < 5 min |
| Tier 2 | Cache serve stale + alert | Slack alert, owner < 15 min |
| Tier 3 | Retry next cycle + DLQ | Dashboard flag, owner < 1 hour |
| Tier 4 | Retry in next batch | Email report, next business day |

### 11.3 SLA Breach → Ticket Routing

| Priority | Ticket Type | Assignment | Resolution SLA |
|----------|------------|------------|----------------|
| P1 | Incident | Asset Admin → On-Call | 1 jam |
| P2 | Problem | Data Engineer | 4 jam |
| P3 | Service Request | Data Engineer | 1 hari kerja |
| P4 | Task | Scheduled | Sprint berikutnya |

---

## 12. Data Quality per Priority

| Priority | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| P1 | ≥ 99% | Serial unique, Tag unique, Location valid | Real-time | Lifecycle ENUM valid | CHECK + referential + uniqueness |
| P2 | ≥ 98% | Dates match, Source/target exist | < 200ms | Type in allowed values | Schema + business rules |
| P3 | ≥ 95% | Batch-valid, Formula correct | < 5 min | Consistent format | Schema |
| P4 | ≥ 90% | Best-effort | < 1 hour | Async-valid | Basic format |

### 10 Data Quality Rules

| Rule | Dimension | Check | Target |
|------|-----------|-------|--------|
| DQ-01 | Uniqueness | asset_id UNIQUE constraint | 100% |
| DQ-02 | Uniqueness | asset_tag UNIQUE constraint | 100% |
| DQ-03 | Uniqueness | (serial_number, manufacturer) UNIQUE | 100% |
| DQ-04 | Referential Integrity | location_id → asset_location exists | 100% |
| DQ-05 | Referential Integrity | contract_id → asset_contract exists (if set) | 100% |
| DQ-06 | Mandatory Fields | asset_tag, serial_number, name, model, manufacturer, owner_dept, location_id, lifecycle_status not null | 100% |
| DQ-07 | Lifecycle Validity | lifecycle_status IN (on_order, received, deployed, in_storage, maintenance, retired, disposed) | 100% |
| DQ-08 | Lifecycle Transition | Valid state machine transitions only | 100% |
| DQ-09 | Financial Validity | purchase_cost ≥ 0, useful_life_years > 0 AND ≤ 30 | 100% |
| DQ-10 | Reconciliation Match | Asset ↔ CI match rate > 95% | > 95% |

> **FIT041 Attribute Priority Hierarchy** (adopted from FIT041 §3.2):
> Digunakan sebagai weight factor dalam DQ scoring — field P1 lebih kritis dari P4:
>
> | Priority | Atribut Data | Weight |
> |----------|-------------|--------|
> | P1 | Serial Number, Lokasi Fisik (Rack ID/Slot), Status Operasional | 1.0 (critical) |
> | P2 | Owner, Garansi/Kontrak End Date, Purchase Date | 0.8 (high) |
> | P3 | Depreciation Value, Asset Tag Internal | 0.6 (medium) |
> | P4 | Konfigurasi Software/OS, IP Address | 0.4 (low) |

---

## 13. Cache Strategy by Priority

| Priority | Cache Mode | TTL | Invalidation |
|----------|-----------|-----|-------------|
| P1 | Write-through | Instant | On every write (CRUD, lifecycle) |
| P2 | Read-through | 30s | TTL + event-driven |
| P3 | Lazy-load | 5 min | TTL only |
| P4 | Lazy-load | 1 hour | TTL only |

### Cache Key Patterns

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| `asset:enrich:{ci_id}` | 15 min | CI enrichment cache (Enrichment API) |
| `asset:detail:{asset_id}` | 5 min | Asset detail cache (CRUD read) |
| `asset:search:{hash}` | 5 min | Search result cache |
| `asset:count:{filter_hash}` | 5 min | Count cache |
| `asset:warranty:expiring` | 1 hour | Warranty expiry dashboard |
| `asset:contract:renewals` | 1 hour | Contract renewal dashboard |

### Cache Invalidation Events

```yaml
invalidation_rules:
  - trigger: "asset.update"
    action: "invalidate_asset_cache"
    scope: "asset_id"
    propagation: "write-through for P1, event-driven for P2"

  - trigger: "asset.lifecycle.transition"
    action: "invalidate_lifecycle_cache + invalidate_enrichment_cache"
    scope: "asset_id + related ci_ids"
    propagation: "write-through for all"

  - trigger: "asset.location.update"
    action: "invalidate_location_cache + invalidate_search_cache"
    scope: "location_id + asset_id"
    propagation: "event-driven"

  - trigger: "reconciliation.complete"
    action: "invalidate_all_enrichment_cache"
    scope: "global"
    propagation: "batch invalidation"
```

---

## 14. Performance Targets

### 14.1 Technical Metrics (DCIM-Wiki)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total Assets | ≥ 50,000 → 500,000 | Asset count in PostgreSQL |
| API Throughput | 1,000 req/s | Aggregate (GET endpoints) |
| Enrichment Throughput | 500 req/s | Enrichment API |
| Bulk Import | 1,000 records/sec | Per batch job |
| Reconciliation | 5,000 records/min | Per reconciliation run |
| Enrichment Cache Hit | > 95% | Redis |
| Search Cache Hit | > 80% | Redis |
| API p99 Latency | < 50ms (enrichment), < 200ms (list) | All endpoints |
| DLQ Rate | < 1% | Failed / total events |
| Concurrent Users | 100+ | Simultaneous connections |
| Reconciliation Match | > 95% | Asset ↔ CI match rate |
| Data Quality Score | > 90% | 10 rules scorecard |

### 14.2 Business Metrics (FIT041 — adopted)

> **FIT041 Traceability:** Business metrics adopted from FIT041 §2.1, §2.2, §5.1.

| Metric | Target | Frequency | Source |
|--------|--------|-----------|--------|
| **Inventory Accuracy** (Physical vs Logical) | **≥ 98.0%** | Quarterly | Physical audit |
| **Barcode/RFID Reliability** | **≥ 99.5%** Read Success Rate | Continuous | Scanner logs |
| **Warranty Data Completeness** (P1/P2) | **100%** | Continuous | Asset Repository |
| **Update Latency** (Business Process) | **≤ 4 jam kerja** | Per change | Audit trail |
| **Data Integrity Check** (P1) | **Harian** | Daily | Automated check |
| **Report Response Time** | **≤ 1 menit** | Per request | API metrics |

---

## 15. Monitoring Dashboard

### Asset Repository Health Metrics

| Metric | Source | Refresh |
|--------|--------|---------|
| Asset Count by Status | PostgreSQL | Real-time |
| Asset Count by Category | PostgreSQL | Real-time |
| Asset Count by Location | PostgreSQL | Real-time |
| API Latency (p50, p95, p99) | Prometheus | Real-time |
| API Error Rate | Prometheus | Real-time |
| Enrichment Cache Hit Rate | Redis | Real-time |
| Search Cache Hit Rate | Redis | Real-time |
| Reconciliation Match Rate | Reconciliation engine | Daily |
| Reconciliation Conflicts | Reconciliation engine | Daily |
| Bulk Import Success Rate | Import engine | Per job |
| Warranty Expiring (30d) | PostgreSQL | Daily |
| Contract Renewal Due (30d) | PostgreSQL | Daily |
| Data Quality Score | DQ engine | Daily |
| DLQ Count | Kafka | Real-time |

---

## 16. FIT041 Alignment & Traceability

### 16.1 Merge Summary

| FIT041 Section | FIT041 Content | DCIM-Wiki Section | Adoption Status |
|---------------|----------------|-------------------|-----------------|
| §2.1 Akurasi Inventaris | Inventory Accuracy ≥98%, Barcode ≥99.5%, Warranty 100% | §14.2 (Business Metrics) | ✅ Adopted |
| §2.2 Kinerja & Latensi | Update Latency ≤4 jam, Data Integrity Harian, Report ≤1 min | §3 (footnote), §14.2 | ✅ Adopted |
| §2.3 Waktu Respons | S1: 2 jam, S2: 4 jam, S3: 1 hari, S4: 3 hari | §7 (Incident Severity) | ✅ Adopted (S1: DCIM-Wiki 1 jam stricter) |
| §3.1 Matriks Prioritas | P1-P4 lifecycle + financial lens | §1 (Priority Model) | ✅ Aligned |
| §3.2 Prioritas Atribut | Attribute priority hierarchy P1-P4 | §12 (DQ Rules) | ✅ Adopted |
| §4 Peran & Tanggung Jawab | 5 RACI roles | §17 (Governance) | ✅ Adopted |
| §5.1 Metrik Kepatuhan | 5 business KPIs | §16.2 (Business KPIs) | ✅ Adopted |
| §5.2 Frekuensi Pelaporan | Daily/Quarterly/Annual | §17.3 (Reporting) | ✅ Adopted |
| §6 Tinjauan & Revisi | Annual review cycle | §17.4 (Review) | ✅ Adopted |

### 16.2 Business KPIs (FIT041 — adopted)

> **FIT041 Traceability:** Adopted from FIT041 §5.1.

| KPI | Target | Type | Owner |
|-----|--------|------|-------|
| **Financial Accuracy Variance** | **< 1.0%** | Business Compliance | Finance/Accounting |
| **Audit Variance Rate** | **< 2.0%** | Audit Compliance | Asset Manager |
| **Cost Avoidance from Reuse** | **Peningkatan Bersih Triwulanan** | Financial Benefit | Asset Manager |
| **Warranty Coverage Rate (P1/P2)** | **≥ 99.5%** | Compliance | Asset Manager |
| **Update Latency Compliance** | **≥ 95.0%** | Operational Compliance | DC Technicians |

### 16.3 Dual-Definition Reconciliation

| Concept | FIT041 Definition | DCIM-Wiki Definition | Resolution |
|---------|-------------------|---------------------|------------|
| Update Latency | ≤ 4 jam kerja (business process) | < 50ms (system response) | **Both valid** — different layers |
| Inventory Accuracy | ≥ 98% (quarterly physical audit) | > 95% (daily automated reconciliation) | **Both valid** — different methods |
| S1 Resolution | 2 jam | 1 jam | **DCIM-Wiki 1 jam** (stricter) |
| S4 Resolution | 3 hari kerja | Not specified | **FIT041 3 hari kerja** |

---

## 17. Governance Framework

### 17.1 RACI Roles (FIT041 — adopted)

> **FIT041 Traceability:** Adopted from FIT041 §4.

| Peran | Tanggung Jawab Utama | RACI Level |
|-------|---------------------|------------|
| **Asset Manager (DCIM)** | Pemilik Proses SLA, pastikan Inventory Accuracy (≥98%), pimpin audit triwulanan, approve perubahan P1/P2 | **R** (Responsible) + **A** (Accountable) |
| **Data Center Technicians** | Check-in/check-out fisik, pastikan Barcode/RFID akurat (≥99.5%), jamin Update Latency (≤4 jam) | **R** (Responsible) |
| **Tim Procurement** | Input Purchase Date & Warranty/Contract Start Date ke sistem | **R** (Responsible) |
| **Tim Finance/Accounting** | Input Depreciation Value, gunakan Asset Repository sebagai basis pelaporan finansial | **C** (Consulted) |
| **Automation Developers** | Pemeliharaan integrasi (ERP, Ticketing System) | **R** (Responsible) |

> **Note:** DCIM-Wiki RBAC (viewer, operator, manager, admin, auditor) tetap berlaku untuk access control. RACI di atas adalah untuk accountability/responsibility.

### 17.2 Quarterly Physical Audit Process

> **FIT041 Traceability:** Adopted from FIT041 §2.1.

| Aspect | Detail |
|--------|--------|
| **Frequency** | 4x/tahun (triwulanan) |
| **Scope** | Seluruh aset P1 di Production Rack |
| **Method** | Physical scan (Barcode/RFID) → compare with repository |
| **Target** | Inventory Accuracy ≥ 98.0% |
| **Owner** | Asset Manager |
| **Participants** | Asset Manager + DC Technicians |
| **Output** | Audit Variance Rate report (≤ 2.0%) |
| **Escalation** | Jika Accuracy < 98% → S2 incident, investigation required |

### 17.3 Reporting Cadence

> **FIT041 Traceability:** Adopted from FIT041 §5.2.

| Jenis Laporan | Frekuensi | Penerima | Fokus Konten |
|--------------|-----------|----------|-------------|
| **Laporan Harian** | Harian (awal hari kerja) | DC Technicians, Asset Manager | Check-in/out hari sebelumnya; validasi integritas data P1 |
| **Laporan Triwulanan** | Setelah audit fisik | Asset Manager, Tim Finance, Project Owner | Ringkasan Inventory Accuracy & Audit Variance Rate |
| **Laporan Tahunan** | Tahunan | Tim Finance, Project Owner, Auditor Eksternal | Kepatuhan SLA menyeluruh, Financial Accuracy Variance, Cost Avoidance |

### 17.4 Annual Review Cycle

> **FIT041 Traceability:** Adopted from FIT041 §6.

| Aspect | Detail |
|--------|--------|
| **Frequency** | Tahunan |
| **Scope** | Seluruh SLA targets, priority model, governance procedures |
| **Trigger** | Siklus audit finansial + perencanaan anggaran modal (CAPEX) |
| **Approver** | Project Owner (DCIM) + Tim Finance/Accounting |
| **Output** | Revised SLA framework (if needed) |
| **Change Control** | Perubahan Inventory Accuracy atau Financial Accuracy Variance memerlukan approval ganda |

---

## Related

- [[priority-severity-model]] — Global priority & severity model
- [[dii-sla-prioritization-framework]] — DI&I SLA framework
- [[cmdb-sla-prioritization-framework]] — CMDB SLA framework
- [[asset-repository-use-case-analysis-final]] — Asset Repository use case analysis (15 UCs)
- [[block3-asset-repository]] — Asset Repository reference design spec
- [[asset-data-model]] — Asset data model
- [[fit041-asset-repository-komparasi]] — FIT041 vs DCIM-Wiki comparison
- [[fit041-asset-sla-prioritization-komparasi]] — FIT041 SLA comparison
- [[data-quality-framework]] — Data quality dimensions
- [[workflow-automation]] — Escalation & ticket routing

---

> **Status:** FINAL — Merged dari DCIM-Wiki (15 sections) + FIT041 (14 items adopted)
> **Date:** 2026-06-25
> **Conflicts:** 0
> **FIT041 Absorption:** 100% (all 9 FIT041 sections mapped)
