---
title: "Use Case Analysis — Configuration Management Database (CMDB)"
created: 2026-06-25
updated: 2026-06-25
type: use-case-analysis
block: 4
phase: 1
status: final
confidence: high
tags: [use-case, cmdb, ci, relationships, topology, impact-analysis, reconciliation, service-mapping, merged]
sources:
  - IF-Technical_Requirements_CMDB-FIT041-20260119.md
  - block4-cmdb.md
  - fit041-cmdb-komparasi.md
  - cmdb (entity)
  - cmdb-data-model (concept)
  - cmdb-reconciliation-runbook (concept)
purpose: >
  Use Case Analysis komprehensif untuk CMDB (Block 4).
  Merged dari FIT041 CMDB Requirements + DCIM-Wiki Block 4 Reference Design.
  Setiap UC dilengkapi: actors, pre-conditions, flow, source systems, data types,
  API endpoints, SLA, data quality, consumers, acceptance criteria.
---

# Use Case Analysis — Configuration Management Database (CMDB)

> **Purpose:** Use Case Analysis komprehensif untuk CMDB — merged dari FIT041 Requirements + DCIM-Wiki Implementation.
> **Cara pakai:** Review per use case untuk memahami data apa yang harus dikelola CMDB, dari mana datangnya, dengan SLA berapa, dan ke mana data dikirim.
> **Depends on:** Block 4 Reference Design, FIT041 CMDB Requirements, Block 1 (Infrastructure), Block 3 (Asset Repository)
> **Merge Source:** FIT041 Technical Requirements CMDB (Jan 2026) + DCIM-Wiki Block 4 Reference Design (Jun 2026)
> **Traceability:** UC1, UC2, UC3, UC4 dilengkapi dari FIT041 actors/pre-conditions/flow
> **Related:** [[fit041-cmdb-komparasi]] — Komparasi FIT041 vs Block 4

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Use Case Taxonomy](#2-use-case-taxonomy)
3. [CI Data Management Use Cases (UC1–UC3)](#3-ci-data-management-use-cases-uc1uc3)
4. [Relationship & Topology Use Cases (UC4–UC6)](#4-relationship--topology-use-cases-uc4uc6)
5. [Data Integration & Reconciliation Use Cases (UC7–UC9)](#5-data-integration--reconciliation-use-cases-uc7uc9)
6. [Service & Health Use Cases (UC10–UC12)](#6-service--health-use-cases-uc10uc12)
7. [Operational Consumer Use Cases (UC13–UC16)](#7-operational-consumer-use-cases-uc13uc16)
8. [Source System → Use Case Matrix](#8-source-system--use-case-matrix)
9. [Data Type → Use Case Mapping](#9-data-type--use-case-mapping)
10. [API Requirements per Use Case](#10-api-requirements-per-use-case)
11. [SLA & Latency Requirements](#11-sla--latency-requirements)
12. [Data Quality Requirements per Use Case](#12-data-quality-requirements-per-use-case)
13. [Downstream Consumer Mapping](#13-downstream-consumer-mapping)
14. [FIT041 Requirements Checklist](#14-fit041-requirements-checklist)
15. [Gaps & Recommendations](#15-gaps--recommendations)
16. [Acceptance Criteria](#16-acceptance-criteria)
17. [Traceability Matrix](#17-traceability-matrix)

---

## 1. Executive Summary

### Scope

DCIM Core Platform memiliki **4 kategori use case** yang membutuhkan CMDB:

| Kategori | Jumlah | Prioritas Rata-rata |
|----------|--------|---------------------|
| **CI Data Management** | 3 use case (UC1–UC3) | P1–P2 |
| **Relationship & Topology** | 3 use case (UC4–UC6) | P1–P2 |
| **Data Integration & Reconciliation** | 3 use case (UC7–UC9) | P1–P2 |
| **Service & Health** | 3 use case (UC10–UC12) | P2–P3 |
| **Operational Consumers** | 4 use case (UC13–UC16) | P1–P3 |
| **Total** | **16 use case** | — |

### Merge Summary

| Aspek | FIT041 | DCIM-Wiki | Merged |
|-------|--------|-----------|--------|
| Use Cases | 4 (conceptual) | 16 (detailed) | **16** (FIT041 UCs absorbed) |
| Actors per UC | ✅ Listed | ⚠️ Implicit | **✅** (UC1–UC4 dari FIT041) |
| Pre-conditions | ✅ Listed | ⚠️ Implicit | **✅** (UC1–UC4 dari FIT041) |
| Flow Steps | ✅ 5-step | ✅ Architecture | **✅** (merged) |
| CI Types | 4 groups | 10 specific types | **10 types** |
| Relationship Types | 4 types | 7 types | **7 types** |
| SLA Tiers | 1 (<500ms) | 4 tiers | **4 tiers** |
| Data Quality | — | 9 rules + scorecard | **9 rules** |
| API Endpoints | Concept | 14 endpoints | **14 endpoints** |
| Acceptance Criteria | — | 18 items | **18 items** |

### Key Findings

1. **10 CI types** harus dikelola: Server, NetworkDevice, Storage, VM, Application, Service, Rack, PatchPanel, UPS, PDU
2. **7 relationship types** dibutuhkan: contains, depends_on, connected_to, runs_on, part_of, managed_by, impacts
3. **14 API endpoints** diperlukan untuk CI CRUD, Relationship, Topology, Impact, Health
4. **4 SLA tiers**: Tier 1 real-time (<50ms), Tier 2 near-RT (<200ms), Tier 3 near-RT (<500ms), Tier 4 batch (<1s)
5. **9 data quality rules** harus terpenuhi dengan scorecard SQL
6. **FIT041 actors/pre-conditions** diadopsi untuk UC1–UC4 sebagai traceability baseline
7. **Neo4j vs PostgreSQL** — pertahankan PostgreSQL untuk Phase 1 (sufficient untuk 150K CIs)

### Quick Architecture View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     USE CASES REQUIRING CMDB                            │
│                                                                         │
│  UC1 CI CRUD        UC2 Lifecycle       UC3 Bulk Import/Export          │
│  UC4 Relationships  UC5 Topology        UC6 Impact Analysis             │
│  UC7 Asset Recon    UC8 Discovery Recon  UC9 DI&I Gateway Sync         │
│  UC10 Service Map   UC11 Health Dash    UC12 Data Quality               │
│  UC13 NOC Dashboard UC14 SIEM Enrich    UC15 Workflow Auto  UC16 Audit  │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CMDB (Block 4)                                   │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     API Layer                                     │  │
│  │  CI CRUD (7) • Relationship (4) • Topology (4) • Impact (3)     │  │
│  │  Health (3) • Service Mapping (1)                                │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  ┌────────────────────────┴─────────────────────────────────────────┐  │
│  │                  Service Layer                                    │  │
│  │  Topology Engine • Impact Analysis • Reconciliation              │  │
│  │  Service Mapping • Data Quality • Audit Trail                    │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  ┌────────────────────────┴─────────────────────────────────────────┐  │
│  │                  Data Layer                                       │  │
│  │  PostgreSQL 16        Redis 7 (cache)                             │  │
│  │  ci, ci_attribute,    topology cache                              │  │
│  │  ci_relationship,     impact cache                                │  │
│  │  ci_lifecycle, ci_service, ci_reconciliation_log                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
         │                 │                │
         ▼                 ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │  Asset   │    │ Discovery│    │  DI&I        │
  │  Repository│  │  (NMS)   │    │  Gateway     │
  └──────────┘    └──────────┘    └──────────────┘
```

---

## 2. Use Case Taxonomy

### 2.1 Classification

| ID | Use Case Name | Kategori | Prioritas | Latency Target | FIT041 Traceability |
|----|--------------|----------|-----------|----------------|---------------------|
| UC1 | CI CRUD Operations | CI Data Mgmt | **P1** | < 50ms p99 | **FIT041 §2.1** |
| UC2 | CI Lifecycle Management | CI Data Mgmt | **P1** | < 100ms | **FIT041 §2.1.2** |
| UC3 | CI Bulk Import/Export | CI Data Mgmt | **P3** | Batch (< 1s/record) | DCIM-Wiki original |
| UC4 | Relationship Management | Relationship & Topology | **P1** | < 50ms p99 | **FIT041 §2.2.1** |
| UC5 | Topology Visualization | Relationship & Topology | **P2** | < 200ms p99 | **FIT041 §2.2.1.2** |
| UC6 | Impact Analysis | Relationship & Topology | **P1** | < 500ms p99 | **FIT041 §2.2.2** |
| UC7 | Asset Reconciliation | Data Integration | **P1** | Daily + event-driven | DCIM-Wiki original |
| UC8 | Discovery Reconciliation | Data Integration | **P1** | Hourly | DCIM-Wiki original |
| UC9 | DI&I Gateway Sync | Data Integration | **P1** | < 10s (near-RT) | DCIM-Wiki original |
| UC10 | Service Mapping | Service & Health | **P2** | < 1s p99 | DCIM-Wiki original |
| UC11 | Health Dashboard | Service & Health | **P2** | < 1s p99 | DCIM-Wiki original |
| UC12 | Data Quality Management | Service & Health | **P3** | Batch (daily) | DCIM-Wiki original |
| UC13 | NOC Dashboard Integration | Operational | **P1** | < 5s (near-RT) | DCIM-Wiki original |
| UC14 | SIEM Enrichment | Operational | **P1** | < 1s (real-time) | DCIM-Wiki original |
| UC15 | Workflow Automation | Operational | **P2** | < 30s (near-RT) | DCIM-Wiki original |
| UC16 | Audit Trail & Compliance | Operational | **P3** | Async (real-time logging) | DCIM-Wiki original |

### 2.2 Priority Distribution

| Prioritas | Jumlah | Use Cases |
|-----------|--------|-----------|
| **P1 Critical** | 8 | UC1, UC2, UC4, UC6, UC7, UC8, UC9, UC13, UC14 |
| **P2 High** | 4 | UC5, UC10, UC11, UC15 |
| **P3 Medium** | 3 | UC3, UC12, UC16 |
| **P4 Supporting** | 0 | — |

### 2.3 Category Breakdown

| Kategori | UCs | Description |
|----------|-----|-------------|
| CI Data Management | UC1–UC3 | CRUD, lifecycle, bulk operations |
| Relationship & Topology | UC4–UC6 | Relationships, graph traversal, impact |
| Data Integration & Reconciliation | UC7–UC9 | Asset sync, discovery sync, DI&I gateway |
| Service & Health | UC10–UC12 | Service mapping, health dashboard, data quality |
| Operational Consumers | UC13–UC16 | NOC, SIEM, workflow, audit |

---

## 3. CI Data Management Use Cases (UC1–UC3)

### 3.1 UC1 — CI CRUD Operations

> **FIT041 Traceability:** Merged dari FIT041 §2.1 (CI Data Model) + §4.2 (API Requirements)

**Objective:** Create, Read, Update, Delete Configuration Items dengan data model yang fleksibel dan terstruktur.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | p99 < 50ms (GET), < 100ms (POST/PUT) |
| **Throughput** | 1000 req/s (GET), 100 req/s (POST) |

#### Actors (from FIT041)

Server Provisioning System, Virtualization Management Platform, Network Discovery Tools, CMDB Administrator, API Consumers

#### Pre-conditions (from FIT041)

- PostgreSQL 16 deployed with CMDB schema
- Redis 7 cache operational
- RBAC configured (5 roles: viewer, operator, manager, admin, auditor)
- API authentication (TLS 1.2+, token-based)

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Authentication:** Client authenticates via token/API key
2. **Authorization:** RBAC check — verify role permissions for operation
3. **Validation:** Schema validation (mandatory fields, data types, constraints)
4. **Execution:** CRUD operation on PostgreSQL
5. **Cache Invalidation:** Redis cache updated (key patterns: `ci:detail:{ci_id}`, `ci:search:{hash}`)
6. **Audit Trail:** ci_lifecycle table updated for status changes
7. **Response:** Return result with proper HTTP status

#### CI Types (10 types)

| CI Type | Description | Key Attributes | Example |
|---------|-------------|----------------|---------|
| Server | Physical/virtual server | serial_number, cpu, ram, os | Dell R750 |
| NetworkDevice | Switch, router, firewall | ip_address, vendor, model | Cisco 9300 |
| Storage | SAN, NAS, disk array | capacity, protocol, iops | NetApp AFF |
| VM | Virtual machine | hypervisor, vcpu, vram | VMware VM |
| Application | Software application | version, license, tier | SAP ERP |
| Service | Business service | owner, sla, criticality | Email Service |
| Rack | Physical rack | u_height, power_capacity | Rack-A1 |
| PatchPanel | Network patch panel | ports, type | PP-Floor3 |
| UPS | Uninterruptible Power Supply | capacity, runtime | APC SRT |
| PDU | Power Distribution Unit | outlets, amperage | PDU-RackA1 |

#### Lifecycle States

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ Planned │───→│ Active   │───→│Maintenance│───→│ Retired   │
└─────────┘    └──────────┘    └──────────┘    └─────┬─────┘
                                     │                │
                                     ▼                ▼
                               ┌──────────┐    ┌──────────┐
                               │  In Use  │    │ Disposed │
                               └──────────┘    └──────────┘
```

#### Mandatory Fields per CI Type

| Field | Server | NetworkDevice | Storage | VM | Application | Service |
|-------|--------|---------------|---------|-----|-------------|---------|
| ci_id | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| name | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ci_type | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| status | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| owner | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| location_id | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| serial_number | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ |
| ip_address | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ |
| os | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ |
| vendor | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| model | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/cmdb/ci` | ci.write | Create CI |
| GET | `/api/v1/cmdb/ci` | ci.read | List CIs (paginated, filterable) |
| GET | `/api/v1/cmdb/ci/{id}` | ci.read | Get CI by ID |
| PUT | `/api/v1/cmdb/ci/{id}` | ci.write | Update CI |
| DELETE | `/api/v1/cmdb/ci/{id}` | ci.admin | Soft delete CI |
| POST | `/api/v1/cmdb/ci/bulk` | ci.write | Bulk import CIs |
| GET | `/api/v1/cmdb/ci/search` | ci.read | Search CIs |

#### Success Criteria (from FIT041)

- Semua CI types dapat di-CRUD melalui API
- Mandatory fields terisi untuk setiap CI type
- CI_ID unique constraint terjaga
- Audit trail tercatat untuk setiap perubahan
- Response time < 50ms untuk GET, < 100ms untuk POST/PUT

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99% (mandatory fields terisi) |
| Accuracy | Serial number unique, IP format valid |
| Timeliness | Real-time (API response) |
| Consistency | CI type enum valid, status transition valid |
| Validity | Schema validation, CHECK constraints |

---

### 3.2 UC2 — CI Lifecycle Management

> **FIT041 Traceability:** Merged dari FIT041 §2.1.2 (CI Lifecycle Management)

**Objective:** Track perubahan status CI dari Planned hingga Disposed dengan audit trail lengkap.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 100ms per transition |
| **Audit** | 7 years retention |

#### Actors (from FIT041)

CMDB Administrator, Automated Systems (Discovery, Reconciliation), Change Management (ITSM)

#### Pre-conditions (from FIT041)

- CI exists in CMDB
- ci_lifecycle table created
- State transition rules defined (DAG)

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Trigger:** Status change request (manual or automated)
2. **Validation:** Verify transition is valid (DAG check)
3. **Execution:** Update CI status
4. **Audit:** Insert into ci_lifecycle table (old_status, new_status, changed_by, changed_at, reason, source)
5. **Cache Invalidation:** Redis cache updated
6. **Event:** Publish lifecycle event for downstream consumers

#### State Transition Rules

```
Valid Transitions:
  Planned → Active
  Planned → Maintenance
  Active → Maintenance
  Active → In Use
  Active → Retired
  Maintenance → Active
  Maintenance → Retired
  In Use → Retired
  Retired → Disposed

Invalid Transitions:
  Disposed → * (terminal state)
  Planned → Retired (skip lifecycle)
  Active → Planned (no backward)
```

#### Audit Trail Schema

```sql
CREATE TABLE ci_lifecycle (
    lifecycle_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ci_id UUID NOT NULL REFERENCES ci(ci_id) ON DELETE CASCADE,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    reason TEXT,
    source VARCHAR(50) DEFAULT 'manual'
);
```

#### Success Criteria (from FIT041)

- Semua perubahan status tercatat di audit trail
- Siapa (changed_by), Kapan (changed_at), Perubahan Lama (old_status), Perubahan Baru (new_status), Alasan (reason)
- State transition rules enforced (tidak ada invalid transition)
- Audit trail queryable untuk compliance

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (setiap transition tercatat) |
| Accuracy | old_status = actual previous status |
| Timeliness | Real-time (on transition) |
| Consistency | source consistent (manual/discovery/reconciliation) |
| Validity | new_status in allowed values |

---

### 3.3 UC3 — CI Bulk Import/Export

**Objective:** Bulk operations untuk migrasi data, backup, dan integrasi dengan external systems.

| Aspect | Detail |
|--------|--------|
| **Priority** | P3 Medium |
| **Latency** | Batch (< 1s per record) |
| **Throughput** | ≥ 500 records/batch |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| Manual Entry (CSV/XLSX) | REST API | CI records | Ad-hoc |
| ITSM (iTop) | REST API | CI records | Daily |
| Asset Repository | REST API | CI-asset mappings | Daily |
| Discovery Tools | REST API | Discovered CIs | Hourly |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/cmdb/ci/bulk` | ci.write | Bulk import CIs |
| GET | `/api/v1/cmdb/ci/export` | ci.read | Export CIs (CSV/JSON) |

#### Success Criteria

- Bulk import handles ≥ 500 records per batch
- Idempotent import (upsert behavior)
- Error handling per record (don't fail entire batch)
- Import progress tracking
- Export includes all CI types with filters

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% (tolerance untuk partial records) |
| Accuracy | Per-record validation |
| Timeliness | Batch processing acceptable |
| Consistency | Same validation rules as single CRUD |
| Validity | CSV/XLSX format validation |

---

## 4. Relationship & Topology Use Cases (UC4–UC6)

### 4.1 UC4 — Relationship Management

> **FIT041 Traceability:** Merged dari FIT041 §2.2.1 (Relationship Management)

**Objective:** Create, query, dan delete relationships antara Configuration Items.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | p99 < 50ms |
| **Throughput** | 100 req/s |

#### Actors (from FIT041)

CMDB Administrator, Discovery Tools, Reconciliation Engine, Automated Systems

#### Pre-conditions (from FIT041)

- Source and target CIs exist
- Relationship type valid
- No self-relationship
- No containment cycles

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Validation:** Verify source/target CIs exist, type valid, no self-relationship
2. **Cycle Check:** For 'contains' type, verify no cycle created (DAG check)
3. **Execution:** Insert into ci_relationship table
4. **Reverse Relationship:** Auto-create reverse for 'impacts' type
5. **Cache Invalidation:** Redis topology cache invalidated
6. **Response:** Return relationship with metadata

#### Relationship Types (7 types)

| Type | Direction | Description | Example |
|------|-----------|-------------|---------|
| **contains** | parent → child | Physical containment | Rack contains Server |
| **depends_on** | source → target | Functional dependency | Service depends_on Application |
| **connected_to** | source → target | Network connectivity | Server connected_to Switch |
| **runs_on** | source → target | Execution dependency | Application runs_on Server |
| **part_of** | child → parent | Logical grouping | VM part_of Cluster |
| **managed_by** | ci → team | Ownership | Server managed_by Team |
| **impacts** | source → target | Impact relationship | Change on Server impacts Service |

#### Relationship Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| No self-relationship | A CI cannot relate to itself | API validation |
| No cycles in containment | Containment must be DAG | Graph check |
| Max depth | Max 10 levels of containment | API validation |
| Bidirectional impact | impacts(A→B) implies B affected by A | Auto-create reverse |
| Orphan detection | CI without any relationship = warning | Health check |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/cmdb/ci/{id}/relationships` | ci.write | Create relationship |
| GET | `/api/v1/cmdb/ci/{id}/relationships` | ci.read | List CI relationships |
| GET | `/api/v1/cmdb/ci/{id}/relationships/{type}` | ci.read | List by type |
| DELETE | `/api/v1/cmdb/ci/{id}/relationships/{rel_id}` | ci.write | Delete relationship |

#### Success Criteria (from FIT041)

- Two-way relationships supported (bidirectional)
- Topology map interface available
- Relationship visualization per CI
- Reverse relationships auto-created for impacts

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 98% (orphan CIs flagged) |
| Accuracy | source/target CIs exist (referential integrity) |
| Timeliness | Real-time (API response) |
| Consistency | Relationship type in allowed values |
| Validity | No self-relationship, no cycles |

---

### 4.2 UC5 — Topology Visualization

> **FIT041 Traceability:** Merged dari FIT041 §2.2.1.2 (Topology Visualization)

**Objective:** Graph-based visualization of CI relationships dan dependencies.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | p99 < 200ms |
| **Throughput** | 200 req/s |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| CMDB (PostgreSQL) | SQL | CI + relationships | Real-time |
| Redis Cache | Redis | Topology cache | 5 min TTL |

#### Traversal Algorithms

| Algorithm | Use Case | Complexity |
|-----------|----------|------------|
| BFS | Direct dependencies (1-2 levels) | O(V + E) |
| DFS | Full dependency chain | O(V + E) |
| Dijkstra | Shortest dependency path | O((V + E) log V) |
| PageRank | CI criticality scoring | O(V * iterations) |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/cmdb/topology/{ci_id}?depth=3&type=depends_on` | ci.read | Get topology |
| GET | `/api/v1/cmdb/topology/{ci_id}/upstream?depth=5` | ci.read | Upstream dependencies |
| GET | `/api/v1/cmdb/topology/{ci_id}/downstream?depth=5` | ci.read | Downstream impacts |
| GET | `/api/v1/cmdb/topology/service/{service_ci_id}` | ci.read | Service topology |

#### Response Schema

```json
{
  "root": {
    "ci_id": "CI-SERVER-001",
    "ci_type": "server",
    "name": "web-server-01",
    "status": "active"
  },
  "nodes": [
    { "ci_id": "CI-APP-001", "ci_type": "application", "name": "web-app", "status": "active", "depth": 1 },
    { "ci_id": "CI-SERVICE-001", "ci_type": "service", "name": "email-service", "status": "active", "depth": 2 }
  ],
  "edges": [
    { "source": "CI-APP-001", "target": "CI-SERVER-001", "type": "runs_on" },
    { "source": "CI-SERVICE-001", "target": "CI-APP-001", "type": "depends_on" }
  ],
  "depth": 3,
  "total_nodes": 4,
  "total_edges": 3
}
```

#### Cache Strategy

```python
# Key: topology:{ci_id}:{depth}:{relationship_type}
# TTL: 5 minutes
# Invalidate on: relationship create/delete
```

#### Success Criteria (from FIT041)

- Topology map interface available
- Graph traversal returns correct results
- Upstream/downstream visualization
- Configurable depth (1-10 levels)
- Cache hit rate > 80%

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all relationships included) |
| Accuracy | Graph traversal correct (no missing edges) |
| Timeliness | < 200ms response |
| Consistency | Cache consistent with DB |
| Validity | Depth within limits |

---

### 4.3 UC6 — Impact Analysis

> **FIT041 Traceability:** Merged dari FIT041 §2.2.2 (Impact Analysis)

**Objective:** "What breaks if this CI fails?" — Real-time impact calculation dengan scoring model.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | p99 < 500ms |
| **Scenarios** | failure, change, maintenance |

#### Actors (from FIT041)

Change Manager, NOC Operator, Incident Manager, Automated Systems

#### Pre-conditions (from FIT041)

- CI exists with relationships
- Topology data populated
- Impact scoring model configured

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Select CI:** Choose CI to analyze
2. **Traverse Upstream:** Find CIs that depend on selected CI (depends_on, runs_on)
3. **Traverse Downstream:** Find CIs impacted by selected CI (impacts)
4. **Calculate Score:** Apply weighted scoring model
5. **Group by Severity:** critical, high, medium, low
6. **Return Report:** Impact report with affected CIs and estimated downtime

#### Impact Scoring Model

| Factor | Weight | Calculation |
|--------|--------|-------------|
| CI Criticality | 40% | critical=10, high=7, medium=4, low=1 |
| Dependency Depth | 30% | Direct=10, 2-hop=7, 3-hop=4, 4+=1 |
| CI Type | 20% | service=10, application=8, server=6, other=4 |
| Relationship Type | 10% | depends_on=10, runs_on=8, connected_to=6, contains=4 |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/cmdb/impact/{ci_id}?scenario=failure` | ci.read | Impact analysis (failure) |
| GET | `/api/v1/cmdb/impact/{ci_id}?scenario=change` | ci.read | Impact analysis (change) |
| GET | `/api/v1/cmdb/impact/{ci_id}?scenario=maintenance` | ci.read | Impact analysis (maintenance) |

#### Response Schema

```json
{
  "ci_id": "CI-SERVER-001",
  "scenario": "failure",
  "overall_impact_score": 8.5,
  "impact_level": "critical",
  "affected_cis": [
    {
      "ci_id": "CI-APP-001",
      "ci_type": "application",
      "name": "web-app",
      "impact_score": 9.0,
      "impact_level": "critical",
      "reason": "runs_on failed CI",
      "depth": 1,
      "affected_services": ["CI-SERVICE-001"]
    }
  ],
  "summary": {
    "total_affected": 2,
    "by_level": { "critical": 1, "high": 1, "medium": 0, "low": 0 },
    "affected_services": ["email-service"],
    "estimated_downtime_minutes": 30
  }
}
```

#### Success Criteria (from FIT041)

- Real-time impact calculation
- Identifikasi layanan & CI terpengaruh
- Semua jalur koneksi dari layanan ke infrastruktur teridentifikasi
- Impact scoring akurat
- Estimated downtime tersedia

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all affected CIs identified) |
| Accuracy | Scoring model correct |
| Timeliness | < 500ms response |
| Consistency | Same CI, same scenario = same score |
| Validity | Scenario in allowed values |

---

## 5. Data Integration & Reconciliation Use Cases (UC7–UC9)

### 5.1 UC7 — Asset Reconciliation

**Objective:** Reconcile CI data dengan Asset Repository untuk memastikan konsistensi data.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | Daily batch + event-driven |
| **Match Key** | serial_number + asset_tag |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| Asset Repository | Kafka (asset.updates) | Asset records | Daily |
| CMDB | PostgreSQL | CI records | Real-time |

#### Matching Logic

```
For each asset record:
  1. Exact match: serial_number → UPDATE CI
  2. IP match: ip_address → VERIFY (IP might be reassigned)
  3. Name match: name → REVIEW (possible rename)
  4. No match → CREATE (if trusted source)
  5. Conflict → Resolution strategy
```

#### Conflict Resolution

| Scenario | Resolution |
|----------|-----------|
| Asset says active, CMDB says maintenance | CMDB wins (operational truth) |
| Asset found, CMDB not | Auto-create CI with status=active |
| CMDB found, Asset not | Flag for review (don't auto-delete) |
| Asset and CMDB disagree on location | Newer timestamp wins |

#### Success Criteria

- CI ↔ Asset sync tested
- Match rate > 95%
- Conflicts flagged for review
- Audit trail updated

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% match rate |
| Accuracy | Serial number matching accurate |
| Timeliness | Daily batch acceptable |
| Consistency | Asset ↔ CI data consistent |
| Validity | Referential integrity (asset_id exists) |

---

### 5.2 UC8 — Discovery Reconciliation

**Objective:** Auto-discover CIs dari network dan reconcile dengan CMDB.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | Hourly |
| **Match Key** | serial_number + IP |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| NMS (Zabbix/Nagios) | SNMP/REST | Discovered devices | Hourly |
| Network Discovery (Nmap) | REST | Network scan results | Hourly |
| CMDB | PostgreSQL | CI records | Real-time |

#### Matching Logic

```
For each discovered device:
  1. Match by serial_number → UPDATE CI (update last_discovered_at)
  2. Match by IP → VERIFY (IP might be reassigned)
  3. No match → Auto-create CI (source='discovery')
  4. CI not discovered for 7 days → Flag for review
```

#### Success Criteria

- CI ↔ Discovery sync tested
- Auto-create new CIs from discovery
- Stale CIs flagged (not discovered for 7 days)
- Match rate > 88%

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 88% match rate |
| Accuracy | IP/serial matching accurate |
| Timeliness | Hourly updates |
| Consistency | Discovery data consistent with CMDB |
| Validity | IP format valid |

---

### 5.3 UC9 — DI&I Gateway Sync

**Objective:** Real-time CI updates dari DI&I Gateway (Kafka consumer).

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 10s (near-RT) |
| **Topic** | `dcim.cmdb.updates` |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| DI&I Gateway | Kafka | CI update events | Real-time |
| CMDB Automation | Python scripts | CI status updates | Daily |

#### Data Flow

```
Discovery/Asset Changes → DI&I Gateway → dcim.cmdb.updates → CMDB Consumer
                                                                ↓
                                                          CI Upsert/Reconcile
```

#### Success Criteria

- CMDB records terupdate dalam 10s
- ≥ 99% data completeness
- CI_ID unique constraint valid
- Delta detection akurat
- CMDB terupdate dalam 1 jam setelah perubahan (FIT041)

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99% |
| Accuracy | Delta detection accurate |
| Timeliness | < 10s end-to-end |
| Consistency | CI_ID unique |
| Validity | Schema validation |

---

## 6. Service & Health Use Cases (UC10–UC12)

### 6.1 UC10 — Service Mapping

**Objective:** End-to-end service dependency view — dari business service hingga physical infrastructure.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | p99 < 1s |
| **Tiers** | 5 levels (critical → low) |

#### Service Model

```
Service CI
  └── depends_on
      ├── Application CI
      │   └── runs_on
      │       ├── Server CI
      │       │   └── contains
      │       │       └── Disk CI
      │       └── Server CI
      │           └── contains
      │               └── Disk CI
      └── Application CI
          └── runs_on
              └── Server CI
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/cmdb/services/{id}/mapping` | ci.read | Service mapping |
| GET | `/api/v1/cmdb/services` | ci.read | List all services |

#### Response Schema

```json
{
  "service": {
    "ci_id": "CI-SERVICE-001",
    "name": "email-service",
    "status": "active",
    "criticality": "critical",
    "owner": "IT Operations"
  },
  "dependency_graph": {
    "total_cis": 8,
    "by_type": { "application": 2, "server": 3, "storage": 2, "network_device": 1 },
    "critical_path": ["CI-SERVICE-001", "CI-APP-EMAIL", "CI-SERVER-EMAIL-01", "CI-SAN-01"]
  },
  "health_summary": {
    "total": 8, "healthy": 6, "degraded": 1, "critical": 1,
    "health_score": 75.0
  },
  "dependency_tiers": [
    { "tier": 1, "cis": ["CI-APP-EMAIL"], "criticality": "critical" },
    { "tier": 2, "cis": ["CI-SERVER-EMAIL-01", "CI-SERVER-EMAIL-02"], "criticality": "high" }
  ]
}
```

#### Success Criteria

- End-to-end service view available
- Critical path identified
- Health score calculated (0-100)
- Dependency tiers defined

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all service dependencies mapped) |
| Accuracy | Critical path correct |
| Timeliness | < 1s response |
| Consistency | Health score consistent |
| Validity | Tier values valid |

---

### 6.2 UC11 — Health Dashboard

**Objective:** Real-time CI health overview — counts, quality metrics, reconciliation status.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | p99 < 1s |
| **Refresh** | 5 min cache |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/cmdb/health` | ci.read | Health overview |
| GET | `/api/v1/cmdb/health/summary` | ci.read | CI counts by type/status |
| GET | `/api/v1/cmdb/health/quality` | ci.read | Data quality metrics |

#### Response Schema

```json
{
  "timestamp": "2026-06-23T14:30:00.000Z",
  "summary": {
    "total_cis": 1247,
    "by_type": { "server": 342, "network_device": 156, "storage": 89, "vm": 445 },
    "by_status": { "active": 980, "planned": 45, "maintenance": 120, "retired": 32 }
  },
  "data_quality": {
    "completeness_score": 92.5,
    "mandatory_fields_complete": 95.0,
    "serial_number_coverage": 88.0,
    "orphan_cis": 15,
    "duplicate_suspects": 3
  },
  "reconciliation": {
    "last_asset_run": "2026-06-23T02:00:00Z",
    "last_discovery_run": "2026-06-23T14:00:00Z",
    "asset_match_rate": 95.0,
    "discovery_match_rate": 88.0,
    "pending_conflicts": 2
  }
}
```

#### Success Criteria

- CI counts accurate
- Data quality metrics available
- Reconciliation status visible
- Cache hit rate > 80%

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all metrics included) |
| Accuracy | Counts match actual data |
| Timeliness | < 1s response (cached) |
| Consistency | Quality score consistent |
| Validity | All metrics numeric |

---

### 6.3 UC12 — Data Quality Management

**Objective:** Enforce data quality rules dan generate scorecard untuk CMDB.

| Aspect | Detail |
|--------|--------|
| **Priority** | P3 Medium |
| **Latency** | Batch (daily) |
| **Rules** | 9 quality rules |

#### Quality Rules

| Rule | Category | Severity | Description |
|------|----------|----------|-------------|
| CI_ID uniqueness | Uniqueness | Critical | Every CI has unique ID |
| Mandatory fields | Completeness | Critical | name, ci_type, status, owner present |
| Status valid | Format | High | Status in allowed values |
| Relationship integrity | Referential | Critical | source/target CIs exist |
| No self-relationship | Logic | Critical | source != target |
| No containment cycles | Logic | Critical | Containment is DAG |
| Serial number unique | Uniqueness | High | Serial unique where present |
| Location exists | Referential | High | location_id valid |
| Asset linked | Completeness | Medium | asset_id populated where possible |

#### Quality Scorecard (SQL)

```sql
CREATE VIEW cmdb_quality_scorecard AS
SELECT
    DATE(NOW()) as check_date,
    COUNT(*) as total_cis,
    ROUND(100.0 * COUNT(*) FILTER (WHERE name IS NOT NULL AND name != '') / COUNT(*), 2) as name_complete,
    ROUND(100.0 * COUNT(*) FILTER (WHERE owner IS NOT NULL AND owner != '') / COUNT(*), 2) as owner_complete,
    ROUND(100.0 * COUNT(*) FILTER (WHERE location_id IS NOT NULL) / COUNT(*), 2) as location_complete,
    (SELECT COUNT(*) FROM ci WHERE ci_id NOT IN (SELECT source_ci_id FROM ci_relationship)
        AND ci_id NOT IN (SELECT target_ci_id FROM ci_relationship)) as orphan_cis
FROM ci;
```

#### Success Criteria

- Quality rules enforced
- Scorecard generated daily
- Quality score > 80%
- Orphan CIs flagged

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all rules checked) |
| Accuracy | Scorecard accurate |
| Timeliness | Daily batch |
| Consistency | Rules consistent |
| Validity | Score valid (0-100) |

---

## 7. Operational Consumer Use Cases (UC13–UC16)

### 7.1 UC13 — NOC Dashboard Integration

**Objective:** Real-time CI status untuk NOC operator — topology, health, alerts.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5s (near-RT) |
| **Refresh** | 5–15s interval |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| CMDB (PostgreSQL) | SQL | CI status, relationships | Real-time |
| Redis Cache | Redis | Topology, health | 5 min TTL |

#### Success Criteria

- NOC dashboard refresh < 15s
- Real-time CI status visible
- Topology visualization available
- Alert integration working

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99% |
| Accuracy | Status real-time |
| Timeliness | < 5s |
| Consistency | Consistent with CMDB |
| Validity | Status values valid |

---

### 7.2 UC14 — SIEM Enrichment

**Objective:** Add CI context ke security events — enrichment untuk SIEM correlation.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 1s (real-time) |
| **Target** | SIEM (Wazuh + Elasticsearch) |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| CMDB (PostgreSQL) | SQL | CI details, relationships | Real-time |
| SIEM Events | Kafka | Security events | Event-driven |

#### Enrichment Data

| Field | Source | Purpose |
|-------|--------|---------|
| ci_id | CMDB | CI identifier |
| ci_type | CMDB | Device type |
| owner | CMDB | Responsible team |
| location | CMDB | Physical location |
| criticality | CMDB | Business impact |
| dependencies | CMDB | Related CIs |

#### Success Criteria

- Security events enriched with CI context
- Enrichment latency < 1s
- CI lookup < 50ms
- Cache hit rate > 90%

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99.9% |
| Accuracy | CI context accurate |
| Timeliness | < 1s |
| Consistency | Consistent with CMDB |
| Validity | All fields valid |

---

### 7.3 UC15 — Workflow Automation

**Objective:** CI-aware ticket creation — auto-create tickets berdasarkan CI relationships dan impact.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 30s (near-RT) |
| **Target** | Workflow Engine (n8n/Temporal) |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| CMDB (PostgreSQL) | SQL | CI relationships, impact | Real-time |
| Impact Analysis | API | Impact report | Event-driven |
| Workflow Engine | REST API | Ticket requests | Event-driven |

#### Success Criteria

- CI-aware ticket creation working
- Impact analysis integrated
- Ticket includes affected CIs
- Escalation based on CI criticality

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 98% |
| Accuracy | CI context in ticket |
| Timeliness | < 30s |
| Consistency | Consistent with CMDB |
| Validity | Ticket data valid |

---

### 7.4 UC16 — Audit Trail & Compliance

**Objective:** Track semua perubahan CI untuk audit compliance — 7 years retention.

| Aspect | Detail |
|--------|--------|
| **Priority** | P3 Medium |
| **Retention** | 7 years |
| **Source** | ci_lifecycle table |

#### Audit Data

| Data | Source | Retention |
|------|--------|-----------|
| CI Changes | CMDB (ci_lifecycle) | 7 years |
| Access Logs | Access Control | 1 year |
| Config Changes | Git/Vault | 7 years |
| Data Lineage | DI&I Layer | 1 year |

#### Success Criteria

- All CI changes tracked
- Audit trail queryable
- 7 year retention enforced
- Compliance reports generated

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all changes tracked) |
| Accuracy | Change details accurate |
| Timeliness | Real-time logging |
| Consistency | Consistent format |
| Validity | All fields valid |

---

## 8. Source System → Use Case Matrix

| Source System | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | UC10 | UC11 | UC12 | UC13 | UC14 | UC15 | UC16 |
|--------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|------|------|------|------|------|------|
| **Asset Repository** | — | — | ✅ | — | — | — | ✅ | — | — | — | — | ✅ | — | — | — | — |
| **NMS (Zabbix/Nagios)** | — | — | — | — | — | — | — | ✅ | — | — | — | — | — | — | — | — |
| **Network Discovery (Nmap)** | — | — | — | — | — | — | — | ✅ | — | — | — | — | — | — | — | — |
| **DI&I Gateway (Kafka)** | — | — | — | — | — | — | — | — | ✅ | — | — | — | — | — | — | — |
| **ITSM (iTop)** | — | — | ✅ | — | — | — | — | — | — | — | — | — | — | — | ✅ | ✅ |
| **Manual Entry** | ✅ | ✅ | ✅ | ✅ | — | — | — | — | — | — | — | — | — | — | — | — |
| **PostgreSQL (CMDB)** | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Redis Cache** | — | — | — | — | ✅ | ✅ | — | — | — | ✅ | ✅ | — | ✅ | ✅ | — | — |
| **SIEM (Wazuh/ES)** | — | — | — | — | — | — | — | — | — | — | — | — | — | ✅ | — | — |
| **Workflow Engine (n8n)** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | ✅ | — |
| **Access Control** | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | ✅ |

**Legend:** ✅ = source digunakan, — = tidak digunakan

---

## 9. Data Type → Use Case Mapping

### 9.1 CI Master Data

| Data Field | UC1 | UC2 | UC3 | UC7 | UC8 | UC9 | UC13 | UC14 |
|-----------|-----|-----|-----|-----|-----|-----|------|------|
| ci_id | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| name | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| ci_type | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| status | ✅ | ✅ | — | ✅ | ✅ | ✅ | ✅ | — |
| owner | ✅ | — | — | ✅ | — | — | ✅ | ✅ |
| serial_number | ✅ | — | ✅ | ✅ | ✅ | ✅ | — | — |
| ip_address | ✅ | — | — | ✅ | ✅ | ✅ | — | — |
| location_id | ✅ | — | — | ✅ | — | — | ✅ | ✅ |
| asset_id | ✅ | — | — | ✅ | — | — | — | — |

### 9.2 Relationship Data

| Data Field | UC4 | UC5 | UC6 | UC10 | UC13 | UC15 |
|-----------|-----|-----|-----|------|------|------|
| source_ci_id | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| target_ci_id | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| relationship_type | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| metadata | ✅ | — | — | — | — | — |

### 9.3 Health & Quality Data

| Data Field | UC11 | UC12 | UC13 |
|-----------|------|------|------|
| total_cis | ✅ | ✅ | ✅ |
| by_type | ✅ | ✅ | ✅ |
| by_status | ✅ | ✅ | ✅ |
| completeness_score | ✅ | ✅ | — |
| orphan_cis | ✅ | ✅ | — |
| reconciliation_status | ✅ | ✅ | — |

---

## 10. API Requirements per Use Case

### 10.1 API Endpoint Summary

| Use Case | Endpoints | Method | Auth |
|----------|-----------|--------|------|
| UC1 (CI CRUD) | 7 | POST, GET, PUT, DELETE | ci.read, ci.write, ci.admin |
| UC2 (Lifecycle) | 1 (implicit) | PUT (status change) | ci.write |
| UC3 (Bulk) | 2 | POST, GET | ci.write, ci.read |
| UC4 (Relationships) | 4 | POST, GET, DELETE | ci.read, ci.write |
| UC5 (Topology) | 4 | GET | ci.read |
| UC6 (Impact) | 3 | GET | ci.read |
| UC10 (Service Map) | 2 | GET | ci.read |
| UC11 (Health) | 3 | GET | ci.read |
| **Total** | **26** | — | — |

### 10.2 Performance Targets

| Operation | Target p99 | Target p50 | Throughput |
|-----------|-----------|-----------|------------|
| GET /cmdb/ci/{id} | < 50ms | < 10ms | 1000 req/s |
| GET /cmdb/ci (list) | < 200ms | < 50ms | 100 req/s |
| POST /cmdb/ci | < 100ms | < 20ms | 100 req/s |
| GET /cmdb/topology/{id} | < 200ms | < 50ms | 200 req/s |
| GET /cmdb/impact/{id} | < 500ms | < 100ms | 50 req/s |
| GET /cmdb/health | < 1s | < 200ms | 10 req/s |
| GET /cmdb/services/{id}/mapping | < 1s | < 200ms | 20 req/s |

### 10.3 Cache Strategy

| Key Pattern | TTL | Purpose |
|-------------|-----|---------|
| ci:detail:{ci_id} | 5 min | CI detail cache |
| ci:relationships:{ci_id} | 5 min | Relationship cache |
| ci:topology:{ci_id}:{depth} | 5 min | Topology cache |
| ci:impact:{ci_id}:{scenario} | 5 min | Impact analysis cache |
| ci:health:summary | 5 min | Health summary cache |
| ci:search:{hash} | 5 min | Search result cache |

---

## 11. SLA & Latency Requirements

### 11.1 End-to-End Latency SLA

| Tier | Latency | Use Cases | Processing Mode |
|------|---------|-----------|-----------------|
| **Tier 1 (Real-time)** | < 50ms | UC1 (CRUD), UC4 (Relationships) | PostgreSQL direct query |
| **Tier 2 (Near-RT)** | < 200ms | UC5 (Topology), UC13 (NOC) | Redis cache + PostgreSQL |
| **Tier 3 (Near-RT)** | < 500ms | UC6 (Impact), UC9 (DI&I Sync) | PostgreSQL + graph traversal |
| **Tier 4 (Batch)** | < 1s | UC3 (Bulk), UC7 (Asset Recon), UC8 (Discovery Recon), UC12 (DQ) | Batch processing |

### 11.2 Availability Targets

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| CMDB API | 99.9% | < 15 min | 0 (PostgreSQL WAL) |
| PostgreSQL | 99.95% | < 5 min | 0 (streaming replication) |
| Redis Cache | 99.9% | < 1 min | N/A (rebuildable) |
| Topology Engine | 99.9% | < 5 min | 0 (from PostgreSQL) |

### 11.3 Capacity Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Total CIs | 150,000 | FIT041 requirement |
| Total Relationships | 500,000 | FIT041 requirement |
| API Throughput | 1,000 req/s | Aggregate |
| Topology Depth | 10 levels | Max traversal |
| Cache Hit Rate | > 80% | Redis |

---

## 12. Data Quality Requirements per Use Case

### 12.1 Quality Dimensions by Priority

| Use Case | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| UC1 (P1) | ≥ 99% | Serial unique, IP valid | Real-time | CI type enum valid | CHECK constraints |
| UC2 (P1) | 100% | old_status = actual | Real-time | Source consistent | Transition valid |
| UC4 (P1) | ≥ 98% | source/target exist | Real-time | Type in allowed values | No self, no cycles |
| UC6 (P1) | 100% | Scoring model correct | < 500ms | Same CI = same score | Scenario valid |
| UC7 (P1) | ≥ 95% | Serial matching | Daily batch | Asset ↔ CI consistent | asset_id exists |
| UC8 (P1) | ≥ 88% | IP/serial matching | Hourly | Discovery ↔ CI consistent | IP format valid |
| UC9 (P1) | ≥ 99% | Delta detection | < 10s | CI_ID unique | Schema valid |
| UC14 (P1) | ≥ 99.9% | CI context accurate | < 1s | Consistent with CMDB | All fields valid |

### 12.2 Validation Rules per Data Type

| Data Type | Mandatory Fields | Range Check | Format Check |
|-----------|-----------------|-------------|--------------|
| CI Record | ci_id, name, ci_type, status, owner | status in allowed values | UUID format, enum valid |
| Relationship | source_ci_id, target_ci_id, relationship_type | source != target | UUID format, enum valid |
| Lifecycle | ci_id, new_status, changed_by | new_status in allowed values | UUID format, timestamp |
| Service Mapping | service_ci_id, ci_id, tier | tier BETWEEN 1 AND 5 | UUID format |

---

## 13. Downstream Consumer Mapping

### 13.1 Consumer → Data Requirements

| Consumer | Input | Required Fields | Output | Latency |
|----------|-------|-----------------|--------|---------|
| **NOC Dashboard** | CI status, topology | ci_id, status, relationships | Real-time view | < 5s |
| **SIEM** | CI context | ci_id, ci_type, owner, location | Enriched events | < 1s |
| **Workflow Engine** | CI impact, relationships | ci_id, impact_score, affected_cis | Ticket context | < 30s |
| **Analytics & AI** | CI data, relationships | ci_id, metrics, dependencies | Capacity predictions | Batch |
| **ITSM (iTop)** | CI sync | ci_id, status, location | CI record | Daily |
| **Dashboard** | Health, quality | ci counts, quality scores | Executive view | < 1s |
| **BI Tools** | Aggregated CI data | CI counts, trends, quality | Reports | Batch |
| **Compliance** | Audit trail | ci_lifecycle records | Audit report | Batch |

### 13.2 Integration Patterns

| Pattern | Consumer | Mechanism |
|---------|----------|-----------|
| **Sync API** | NOC Dashboard, SIEM | REST API (real-time) |
| **Async Events** | Workflow Engine | Kafka (near-RT) |
| **Batch Export** | BI Tools, Compliance | Scheduled job |
| **Cache Read** | Dashboard | Redis cache |
| **Kafka Consumer** | Analytics & AI | dcim.cmdb.updates topic |

---

## 14. FIT041 Requirements Checklist

> Source: IF-Technical_Requirements_CMDB-FIT041-20260119.md

| Requirement Type | Requirement | Aligned UCs | Status |
|-----------------|-------------|-------------|--------|
| **Data Model** | CI data model fleksibel dan terstruktur | UC1 | ✅ Covered (EAV pattern) |
| **Data Model** | Hierarki dan pewarisan (inheritance) | UC1 | ⚠️ Partial (CI types independent) |
| **Lifecycle** | Lifecycle management dengan audit trail | UC2 | ✅ Covered (ci_lifecycle table) |
| **Lifecycle** | Status: Planned, Operational, Maintenance, Retired, Decommissioned | UC2 | ✅ Covered (6 states) |
| **Relationships** | 4 types: Connects to, Runs on, Contained in, Powers | UC4 | ✅ Covered (7 types, extended) |
| **Relationships** | Two-way relationships | UC4 | ✅ Covered (bidirectional) |
| **Topology** | Topology map interface | UC5 | ✅ Covered (Topology API) |
| **Impact** | Real-time impact calculation | UC6 | ✅ Covered (scoring model) |
| **Reconciliation** | Reconciliation engine, merge dari berbagai sumber | UC7, UC8 | ✅ Covered (Asset + Discovery) |
| **API** | REST API CRUD | UC1 | ✅ Covered (7 endpoints) |
| **API** | Query dengan filter kompleks | UC1 | ✅ Covered (paginated, filterable) |
| **Security** | RBAC granular (per CI type, location, role) | All | ✅ Covered (5 roles + matrix) |
| **Security** | TLS 1.2+, OAuth 2.0 atau API Key | All | ✅ Covered (token-based) |
| **Performance** | 150,000 CIs + 500,000 Relationships | UC1, UC4 | ✅ Covered (capacity targets) |
| **Performance** | <500ms for 5+ filter/join | UC1 | ✅ Covered (per-operation targets) |
| **HA** | 99.9% availability | All | ✅ Covered (availability targets) |
| **HA** | Cluster HA dengan auto-failover | All | ✅ Covered (PostgreSQL cluster) |
| **HA** | Daily full backup | All | ✅ Covered (WAL + PITR) |
| **HA** | RTO < 4 hours | All | ✅ Covered (< 15 min) |
| **Platform** | 3+ App Server (Active-Active) | All | ⚠️ Implicit (Block 1) |
| **Platform** | 3 DB Server (Cluster) | All | ⚠️ Implicit (Block 1) |

---

## 15. Gaps & Recommendations

### 15.1 Identified Gaps

| # | Gap | Impact | Priority | Recommendation |
|---|-----|--------|----------|----------------|
| 1 | CI Hierarchy/Inheritance tidak explicit di Block 4 | Cleaner data model | **P2** | Pertimbangkan tambah concept hierarchy |
| 2 | "Powers" relationship type tidak ada di Block 4 | Facilities integration | **P3** | Tambah ke relationship types |
| 3 | Data Classification (Public, Internal, Confidential) belum ada | Security compliance | **P2** | Tambah data classification levels |
| 4 | Query Language (GraphQL/SQL-like) belum ada | Flexible querying | **P3** | Pertimbangkan GraphQL |
| 5 | Encryption at Rest belum terdefinisi | Data security | **P2** | Tambah encryption config |
| 6 | Platform sizing matrix belum ada untuk CMDB | Infrastructure planning | **P2** | Tambah CMDB-specific sizing |
| 7 | Monitoring System integration belum ada | Event correlation | **P2** | Tambah monitoring integration |
| 8 | Workflow integration belum ada | Automation | **P2** | Tambah workflow integration |

### 15.2 Recommendations

| # | Recommendation | Rationale | Effort |
|---|---------------|-----------|--------|
| 1 | Pertahankan PostgreSQL untuk Phase 1 | Sufficient untuk 150K CIs | — |
| 2 | Neo4j menjadi future consideration | Jika scale > 500K CIs | — |
| 3 | Add data classification | Security compliance | 2 days |
| 4 | Add CI hierarchy concept | Cleaner data model | 3 days |
| 5 | Add "Powers" relationship type | Facilities integration | 1 day |
| 6 | Add monitoring integration | Event correlation | 1 sprint |
| 7 | Add workflow integration | Automation | 1 sprint |

### 15.3 Tidak Perlu Diubah

| Item | Reason |
|------|--------|
| PostgreSQL Schema | Sudah detailed dengan 6 tables + indexes |
| Topology Engine | Sudah lengkap dengan 4 algorithms |
| Impact Analysis | Sudah ada scoring model |
| Reconciliation Engine | Sudah ada matching logic |
| Data Quality Framework | Sudah ada 9 rules + scorecard |
| Monitoring & Alerts | Sudah ada 12 metrics + 5 alerts |
| RBAC Matrix | Sudah ada 5 roles |

---

## 16. Acceptance Criteria

### 16.1 Per Use Case

| Use Case | Acceptance Criteria |
|----------|-------------------|
| **UC1** | ✅ Semua 10 CI types dapat di-CRUD<br>✅ Mandatory fields enforced<br>✅ Response time < 50ms (GET), < 100ms (POST)<br>✅ CI_ID unique constraint valid<br>✅ Audit trail tercatat |
| **UC2** | ✅ Semua 6 lifecycle states available<br>✅ State transition rules enforced<br>✅ Audit trail lengkap (who, when, old, new, reason)<br>✅ 7 year retention |
| **UC3** | ✅ Bulk import ≥ 500 records/batch<br>✅ Idempotent import<br>✅ Error handling per record<br>✅ Export dengan filters |
| **UC4** | ✅ Semua 7 relationship types available<br>✅ No self-relationship enforced<br>✅ No containment cycles<br>✅ Bidirectional impact auto-created<br>✅ Response time < 50ms |
| **UC5** | ✅ 4 traversal algorithms working<br>✅ Configurable depth (1-10)<br>✅ Upstream/downstream separate<br>✅ Cache hit rate > 80%<br>✅ Response time < 200ms |
| **UC6** | ✅ 3 scenarios (failure, change, maintenance)<br>✅ Impact scoring model accurate<br>✅ Response time < 500ms<br>✅ Estimated downtime included |
| **UC7** | ✅ CI ↔ Asset sync tested<br>✅ Match rate > 95%<br>✅ Conflicts flagged for review<br>✅ Audit trail updated |
| **UC8** | ✅ CI ↔ Discovery sync tested<br>✅ Auto-create new CIs<br>✅ Stale CIs flagged<br>✅ Match rate > 88% |
| **UC9** | ✅ CMDB records terupdate dalam 10s<br>✅ ≥ 99% data completeness<br>✅ CI_ID unique constraint valid<br>✅ Delta detection akurat |
| **UC10** | ✅ End-to-end service view<br>✅ Critical path identified<br>✅ Health score calculated (0-100)<br>✅ Dependency tiers defined |
| **UC11** | ✅ CI counts accurate<br>✅ Data quality metrics available<br>✅ Reconciliation status visible<br>✅ Cache hit rate > 80% |
| **UC12** | ✅ 9 quality rules enforced<br>✅ Scorecard generated daily<br>✅ Quality score > 80%<br>✅ Orphan CIs flagged |
| **UC13** | ✅ NOC dashboard refresh < 15s<br>✅ Real-time CI status visible<br>✅ Topology visualization available<br>✅ Alert integration working |
| **UC14** | ✅ Security events enriched with CI context<br>✅ Enrichment latency < 1s<br>✅ CI lookup < 50ms<br>✅ Cache hit rate > 90% |
| **UC15** | ✅ CI-aware ticket creation working<br>✅ Impact analysis integrated<br>✅ Ticket includes affected CIs<br>✅ Escalation based on CI criticality |
| **UC16** | ✅ All CI changes tracked<br>✅ Audit trail queryable<br>✅ 7 year retention enforced<br>✅ Compliance reports generated |

### 16.2 Cross-Cutting

| Criteria | Target |
|----------|--------|
| Total CIs | ≥ 150,000 |
| Total Relationships | ≥ 500,000 |
| API p99 latency | < 500ms |
| Data completeness (P1) | ≥ 98% |
| Cache hit rate | > 80% |
| Reconciliation match rate | > 88% |
| Quality score | > 80% |
| Availability | 99.9% |

---

## 17. Traceability Matrix

| DCIM-Wiki UC | FIT041 Equivalent | Merge Type | Enhanced With |
|-------------|-------------------|------------|---------------|
| UC1 CI CRUD | FIT041 §2.1 CI Data Model | **Merged** | Actors, pre-conditions, flow, CI types, mandatory fields |
| UC2 Lifecycle | FIT041 §2.1.2 CI Lifecycle Management | **Merged** | Actors, pre-conditions, flow, audit trail |
| UC3 Bulk Import | — | DCIM-Wiki original | — |
| UC4 Relationships | FIT041 §2.2.1 Relationship Management | **Merged** | Actors, pre-conditions, flow, 7 types, rules |
| UC5 Topology | FIT041 §2.2.1.2 Topology Visualization | **Merged** | Actors, pre-conditions, flow, algorithms |
| UC6 Impact | FIT041 §2.2.2 Impact Analysis | **Merged** | Actors, pre-conditions, flow, scoring model |
| UC7 Asset Recon | — | DCIM-Wiki original | — |
| UC8 Discovery Recon | — | DCIM-Wiki original | — |
| UC9 DI&I Sync | — | DCIM-Wiki original | — |
| UC10 Service Map | — | DCIM-Wiki original | — |
| UC11 Health Dash | — | DCIM-Wiki original | — |
| UC12 Data Quality | — | DCIM-Wiki original | — |
| UC13 NOC Dashboard | — | DCIM-Wiki original | — |
| UC14 SIEM Enrich | — | DCIM-Wiki original | — |
| UC15 Workflow | — | DCIM-Wiki original | — |
| UC16 Audit Trail | — | DCIM-Wiki original | — |

---

## References

- [[IF-Technical_Requirements_CMDB-FIT041-20260119]] — FIT041 CMDB Requirements (source)
- [[block4-cmdb]] — Block 4 Reference Design Spec
- [[fit041-cmdb-komparasi]] — Comparison document
- [[cmdb]] — Entity page
- [[cmdb-data-model]] — Data model concept
- [[cmdb-reconciliation-runbook]] — Reconciliation procedures
- [[asset-repository]] — CI/asset reconciliation target
- [[data-ingestion-integration]] — CI update events source
- [[postgresql]] — Primary database
- [[redis]] — Cache layer

---

> **Status:** Final — Merged dari FIT041 + DCIM-Wiki
> **Date:** 2026-06-25
> **Purpose:** Use Case Analysis final untuk CMDB — 16 use cases, merged actors/pre-conditions/flow dari FIT041
> **Method:** dcim-comparison skill + document alignment + MCP Sequential Thinking
