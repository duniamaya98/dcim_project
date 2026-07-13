---
title: "Use Case Analysis — Configuration Management Database (CMDB) (Final)"
created: 2026-06-25
updated: 2026-06-25
type: use-case-analysis
block: 4
phase: 1
status: final
confidence: high
tags: [use-case, cmdb, ci, relationships, topology, impact-analysis, reconciliation, service-mapping, merged]
sources:
  - IF-Use_Case_Analysis_CMDB-FIT041-20260121.md
  - cmdb-use-case-analysis.md
  - fit041-cmdb-use-case-komparasi.md
  - fit041-cmdb-komparasi.md
  - block4-cmdb.md
  - cmdb (entity)
  - cmdb-data-model (concept)
  - cmdb-reconciliation-runbook (concept)
purpose: >
  Final Use Case Analysis untuk CMDB — merged dari FIT041 (3 UCs) + DCIM-Wiki (16 UCs).
  Setiap UC dilengkapi: actors, pre-conditions, flow, source systems, data types,
  API endpoints, SLA, data quality, consumers, acceptance criteria.
  FIT041 actors/pre-conditions/flow diadopsi untuk UC6, UC16, UC7.
---

# Use Case Analysis — Configuration Management Database (CMDB) (Final)

> **Purpose:** Use Case Analysis final untuk CMDB — merged dari FIT041 Requirements + DCIM-Wiki Implementation.
> **Cara pakai:** Review per use case untuk memahami data apa yang harus dikelola CMDB, dari mana datangnya, dengan SLA berapa, dan ke mana data dikirim.
> **Depends on:** Block 4 Reference Design, FIT041 CMDB Use Case Analysis, FIT041 CMDB Technical Requirements, Block 1 (Infrastructure), Block 3 (Asset Repository)
> **Merge Source:** FIT041 Use Case Analysis CMDB (Jan 2026) + DCIM-Wiki CMDB Use Case Analysis (Jun 2026)
> **Traceability:** UC6, UC16, UC7 dilengkapi dari FIT041 actors/pre-conditions/flow
> **Related:** [[fit041-cmdb-use-case-komparasi]] — Komparasi FIT041 UC Analysis vs DCIM-Wiki

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
| Use Cases | 3 (conceptual) | 16 (detailed) | **16** (FIT041 UCs absorbed) |
| Actors per UC | ✅ Listed | ⚠️ Implicit | **✅** (UC6, UC16, UC7 dari FIT041) |
| Pre-conditions | ✅ Listed | ⚠️ Implicit | **✅** (UC6, UC16, UC7 dari FIT041) |
| Flow Steps | ✅ 4-5 step | ✅ Architecture | **✅** (merged) |
| CI Types | 4 groups | 10 specific types | **10 types** |
| Relationship Types | 4 types | 7 types | **7 types** |
| SLA Tiers | 1 (<500ms) | 4 tiers | **4 tiers** |
| Data Quality | — | 9 rules + scorecard | **9 rules** |
| API Endpoints | Concept | 26 endpoints | **26 endpoints** |
| Acceptance Criteria | — | 18 items | **18 items** |

### Key Findings

1. **10 CI types** harus dikelola: Server, NetworkDevice, Storage, VM, Application, Service, Rack, PatchPanel, UPS, PDU
2. **7 relationship types** dibutuhkan: contains, depends_on, connected_to, runs_on, part_of, managed_by, impacts
3. **26 API endpoints** diperlukan untuk CI CRUD, Relationship, Topology, Impact, Health, Service Map
4. **4 SLA tiers**: Tier 1 real-time (<50ms), Tier 2 near-RT (<200ms), Tier 3 near-RT (<500ms), Tier 4 batch (<1s)
5. **9 data quality rules** harus terpenuhi dengan scorecard SQL
6. **FIT041 actors/pre-conditions** diadopsi untuk UC6, UC16, UC7 sebagai traceability baseline
7. **FIT041 unique concepts** diadopsi: drift detection (UC16), financial integration (UC7), capacity planning tool (UC7)
8. **Neo4j vs PostgreSQL** — pertahankan PostgreSQL untuk Phase 1 (sufficient untuk 150K CIs)

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
│  │  Health (3) • Service Mapping (1) • Bulk (2) • Search (1)       │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  ┌────────────────────────┴─────────────────────────────────────────┐  │
│  │                  Service Layer                                    │  │
│  │  Topology Engine • Impact Analysis • Reconciliation              │  │
│  │  Service Mapping • Data Quality • Audit Trail • Drift Detection  │  │
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
| UC1 | CI CRUD Operations | CI Data Mgmt | **P1** | < 50ms p99 | DCIM-Wiki original |
| UC2 | CI Lifecycle Management | CI Data Mgmt | **P1** | < 100ms | DCIM-Wiki original |
| UC3 | CI Bulk Import/Export | CI Data Mgmt | **P3** | Batch (< 1s/record) | DCIM-Wiki original |
| UC4 | Relationship Management | Relationship & Topology | **P1** | < 50ms p99 | DCIM-Wiki original |
| UC5 | Topology Visualization | Relationship & Topology | **P2** | < 200ms p99 | DCIM-Wiki original |
| UC6 | Impact Analysis | Relationship & Topology | **P1** | < 500ms p99 | **FIT041 UC1** |
| UC7 | Asset Reconciliation | Data Integration | **P1** | Daily + event-driven | **FIT041 UC3** |
| UC8 | Discovery Reconciliation | Data Integration | **P1** | Hourly | DCIM-Wiki original |
| UC9 | DI&I Gateway Sync | Data Integration | **P1** | < 10s (near-RT) | DCIM-Wiki original |
| UC10 | Service Mapping | Service & Health | **P2** | < 1s p99 | DCIM-Wiki original |
| UC11 | Health Dashboard | Service & Health | **P2** | < 1s p99 | DCIM-Wiki original |
| UC12 | Data Quality Management | Service & Health | **P3** | Batch (daily) | DCIM-Wiki original |
| UC13 | NOC Dashboard Integration | Operational | **P1** | < 5s (near-RT) | DCIM-Wiki original |
| UC14 | SIEM Enrichment | Operational | **P1** | < 1s (real-time) | DCIM-Wiki original |
| UC15 | Workflow Automation | Operational | **P2** | < 30s (near-RT) | DCIM-Wiki original |
| UC16 | Audit Trail & Compliance | Operational | **P3** | Async (real-time logging) | **FIT041 UC2** |

### 2.2 Priority Distribution

| Prioritas | Jumlah | Use Cases |
|-----------|--------|-----------|
| **P1 Critical** | 8 | UC1, UC2, UC4, UC6, UC7, UC8, UC9, UC13, UC14 |
| **P2 High** | 4 | UC5, UC10, UC11, UC15 |
| **P3 Medium** | 3 | UC3, UC12, UC16 |
| **P4 Supporting** | 0 | — |

---

## 3. CI Data Management Use Cases (UC1–UC3)

### 3.1 UC1 — CI CRUD Operations

**Objective:** Create, Read, Update, Delete Configuration Items dengan data model yang fleksibel dan terstruktur.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | p99 < 50ms (GET), < 100ms (POST/PUT) |
| **Throughput** | 1000 req/s (GET), 100 req/s (POST) |

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

**Objective:** Track perubahan status CI dari Planned hingga Disposed dengan audit trail lengkap.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 100ms per transition |
| **Audit** | 7 years retention |

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

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/cmdb/ci/bulk` | ci.write | Bulk import CIs |
| GET | `/api/v1/cmdb/ci/export` | ci.read | Export CIs (CSV/JSON) |

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

**Objective:** Create, query, dan delete relationships antara Configuration Items.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | p99 < 50ms |
| **Throughput** | 100 req/s |

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

**Objective:** Graph-based visualization of CI relationships dan dependencies.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | p99 < 200ms |
| **Throughput** | 200 req/s |

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

#### Cache Strategy

```python
# Key: topology:{ci_id}:{depth}:{relationship_type}
# TTL: 5 minutes
# Invalidate on: relationship create/delete
```

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

> **FIT041 Traceability:** Merged dari FIT041 UC1 (Incident Impact Analysis and Root Cause Identification)

**Objective:** "What breaks if this CI fails?" — Real-time impact calculation dengan scoring model.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | p99 < 500ms |
| **Scenarios** | failure, change, maintenance |

#### Actors (from FIT041 UC1)

DCIM Operator, Incident Management System, CMDB

#### Pre-conditions (from FIT041 UC1)

- CMDB diisi dengan hubungan CI-ke-CI dan CI-ke-Layanan yang akurat dan terkini
- CI exists with relationships
- Topology data populated
- Impact scoring model configured

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Input:** Sistem Manajemen Insiden meminta data dari CMDB menggunakan pengidentifikasi CI yang gagal (misalnya, PDU-A01)
2. **Select CI:** Choose CI to analyze
3. **Traverse Upstream:** Find CIs that depend on selected CI (depends_on, runs_on)
4. **Traverse Downstream:** Find CIs impacted by selected CI (impacts)
5. **Calculate Score:** Apply weighted scoring model
6. **Pemetaan Dampak:** Daftar CI yang bergantung dipetakan ke layanan bisnis
7. **Output:** Sistem DCIM menampilkan peta dampak visual dan daftar layanan yang terpengaruh dan CI yang bergantung yang diprioritaskan kepada Operator DCIM

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

#### Success Criteria (merged)

- Operator DCIM dapat menghasilkan daftar semua CI dan layanan yang terpengaruh dalam waktu 30 detik setelah insiden tercatat (FIT041)
- Real-time impact calculation (DCIM-Wiki)
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

> **FIT041 Traceability:** Merged dari FIT041 UC3 (Asset Lifecycle Management and Capacity Planning)

**Objective:** Reconcile CI data dengan Asset Repository untuk memastikan konsistensi data.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | Daily batch + event-driven |
| **Match Key** | serial_number + asset_tag |

#### Actors (from FIT041 UC3)

Asset Manager, Financial System, Capacity Planning Tool, DCIM Operator

#### Pre-conditions (from FIT041 UC3)

- CMDB berisi atribut siklus hidup (misalnya, Tanggal Pembelian, Tanggal Berakhirnya Garansi, Status)
- Asset Repository connected
- DI&I layer ready

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Query:** Alat Perencanaan Kapasitas meminta daftar semua CI komputasi fisik yang saat ini 'Dalam Penggunaan'
2. **Matching Logic:** For each asset record:
   - Exact match: serial_number → UPDATE CI
   - IP match: ip_address → VERIFY (IP might be reassigned)
   - Name match: name → REVIEW (possible rename)
   - No match → CREATE (if trusted source)
   - Conflict → Resolution strategy
3. **Integrasi:** CMDB mengekspor inventaris ke Sistem Keuangan untuk perhitungan depresiasi
4. **Pembaruan:** Ketika aset secara fisik dinonaktifkan, Operator DCIM memperbarui status CI di CMDB menjadi 'Dinonaktifkan'

#### Conflict Resolution

| Scenario | Resolution |
|----------|-----------|
| Asset says active, CMDB says maintenance | CMDB wins (operational truth) |
| Asset found, CMDB not | Auto-create CI with status=active |
| CMDB found, Asset not | Flag for review (don't auto-delete) |
| Asset and CMDB disagree on location | Newer timestamp wins |

#### Financial Integration (from FIT041 UC3)

| Integration | Description | Frequency |
|-------------|-------------|-----------|
| Depreciation Calculation | Export CI data ke financial system | Quarterly |
| Warranty Tracking | Track end-of-warranty dates | Daily |
| Capacity Planning | Support quarterly capacity review | Quarterly |
| Asset Decommission | Update status saat aset dinonaktifkan | Event-driven |

#### Success Criteria (merged)

- Manajer Aset dapat menghasilkan laporan yang merinci semua aset yang dijadwalkan untuk dinonaktifkan dalam 90 hari ke depan dengan akurasi data 100% (FIT041)
- CI ↔ Asset sync tested (DCIM-Wiki)
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

#### Matching Logic

```
For each discovered device:
  1. Match by serial_number → UPDATE CI (update last_discovered_at)
  2. Match by IP → VERIFY (IP might be reassigned)
  3. No match → Auto-create CI (source='discovery')
  4. CI not discovered for 7 days → Flag for review
```

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

#### Data Flow

```
Discovery/Asset Changes → DI&I Gateway → dcim.cmdb.updates → CMDB Consumer
                                                                ↓
                                                          CI Upsert/Reconcile
```

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

---

## 7. Operational Consumer Use Cases (UC13–UC16)

### 7.1 UC13 — NOC Dashboard Integration

**Objective:** Real-time CI status untuk NOC operator — topology, health, alerts.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5s (near-RT) |
| **Refresh** | 5–15s interval |

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

#### Enrichment Data

| Field | Source | Purpose |
|-------|--------|---------|
| ci_id | CMDB | CI identifier |
| ci_type | CMDB | Device type |
| owner | CMDB | Responsible team |
| location | CMDB | Physical location |
| criticality | CMDB | Business impact |
| dependencies | CMDB | Related CIs |

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

> **FIT041 Traceability:** Merged dari FIT041 UC2 (Change Verification and Audit Compliance)

**Objective:** Track semua perubahan CI untuk audit compliance — 7 years retention.

| Aspect | Detail |
|--------|--------|
| **Priority** | P3 Medium |
| **Retention** | 7 years |
| **Source** | ci_lifecycle table |

#### Actors (from FIT041 UC2)

Change Management System, Auditor, DCIM Operator

#### Pre-conditions (from FIT041 UC2)

- Sebuah Konfigurasi Dasar telah ditetapkan untuk CI target
- Lapisan Pengambilan dan Integrasi Data telah menyediakan detail konfigurasi terbaru

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Perubahan Masukan:** Sistem Manajemen Perubahan mencatat perubahan yang disetujui
2. **Pengambilan Data:** Lapisan Pengambilan dan Integrasi Data mengambil status konfigurasi aktual dari CI
3. **Perbandingan:** CMDB membandingkan keadaan aktual dengan keadaan baseline yang diotorisasi
4. **Verifikasi:** Jika keadaan aktual sesuai dengan perubahan yang disetujui, CMDB memperbarui baseline
5. **Audit/Drift:** Jika keadaan aktual menyimpang dari keadaan yang disetujui (perubahan yang tidak diotorisasi), CMDB mengirimkan peringatan Pergeseran Konfigurasi kepada Pihak Terkait
6. **Logging:** Semua perubahan tercatat di ci_lifecycle table dengan retention 7 tahun

#### Drift Detection (from FIT041 UC2)

| Aspect | Detail |
|--------|--------|
| **Mechanism** | CMDB membandingkan keadaan aktual dengan baseline |
| **Detection Time** | Drift terdeteksi dalam 15 menit setelah terdeteksi |
| **Alert** | Peringatan Pergeseran Konfigurasi dikirim ke pihak terkait |
| **Resolution** | Perubahan tidak diotorisasi ditandai untuk review |

#### Audit Data

| Data | Source | Retention |
|------|--------|-----------|
| CI Changes | CMDB (ci_lifecycle) | 7 years |
| Access Logs | Access Control | 1 year |
| Config Changes | Git/Vault | 7 years |
| Data Lineage | DI&I Layer | 1 year |

#### Success Criteria (merged)

- CMDB secara otomatis menandai setiap penyimpangan konfigurasi yang tidak sah (drift) dalam waktu 15 menit setelah terdeteksi (FIT041)
- Semua CI changes tracked (DCIM-Wiki)
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
| **Financial System** | — | — | — | — | — | — | ✅ | — | — | — | — | — | — | — | — | — |
| **Capacity Planning Tool** | — | — | — | — | — | — | ✅ | — | — | — | — | — | — | — | — | — |

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

---

## 13. Downstream Consumer Mapping

| Consumer | Input | Required Fields | Output | Latency |
|----------|-------|-----------------|--------|---------|
| **NOC Dashboard** | CI status, topology | ci_id, status, relationships | Real-time view | < 5s |
| **SIEM** | CI context | ci_id, ci_type, owner, location | Enriched events | < 1s |
| **Workflow Engine** | CI impact, relationships | ci_id, impact_score, affected_cis | Ticket context | < 30s |
| **Analytics & AI** | CI data, relationships | ci_id, metrics, dependencies | Capacity predictions | Batch |
| **ITSM (iTop)** | CI sync | ci_id, status, location | CI record | Daily |
| **Financial System** | CI lifecycle data | ci_id, purchase_date, warranty, status | Depreciation report | Quarterly |
| **Capacity Planning Tool** | CI capacity data | ci_id, cpu, ram, storage, utilization | Capacity report | Quarterly |
| **Dashboard** | Health, quality | ci counts, quality scores | Executive view | < 1s |
| **BI Tools** | Aggregated CI data | CI counts, trends, quality | Reports | Batch |
| **Compliance** | Audit trail | ci_lifecycle records | Audit report | Batch |

---

## 14. FIT041 Requirements Checklist

> Source: IF-Use_Case_Analysis_CMDB-FIT041-20260121.md

| # | Requirement Type | Requirement | Aligned UCs | Status |
|---|-----------------|-------------|-------------|--------|
| 1 | Technical | Dukungan model data CI (fisik, virtual, logis) | UC1 (CI CRUD), 10 CI types | ✅ Covered |
| 2 | Technical | Database grafis / mesin pemetaan hubungan | UC5 (Topology Engine, 4 algorithms) | ✅ Covered |
| 3 | Performance | Penelusuran hubungan CI <500ms | UC6 (Impact Analysis, p99 < 500ms) | ✅ Covered |
| 4 | Scalability | Minimal 150,000 CIs + 500,000 relationships | UC1, UC4 (capacity targets) | ✅ Covered |
| 5 | Security | RBAC to restrict update permissions | All UCs (5 roles matrix) | ✅ Covered |
| 6 | Availability | HA cluster RTO < 15 minutes | All UCs (PostgreSQL cluster) | ✅ Covered |

**Kesimpulan:** Semua 6 requirements dari FIT041 **100% covered** di DCIM-Wiki.

---

## 15. Gaps & Recommendations

### 15.1 Identified Gaps

| # | Gap | Impact | Priority | Recommendation |
|---|-----|--------|----------|----------------|
| 1 | Drift Detection mechanism belum explicit di DCIM-Wiki | Change management gap | **P2** | Tambah UC eksplisit atau extend UC16 |
| 2 | Financial System integration belum ada | Asset management gap | **P3** | Pertimbangkan integrasi financial system |
| 3 | Capacity Planning Tool integration belum ada | Planning gap | **P3** | Pertimbangkan integrasi capacity planning |
| 4 | CI Hierarchy/Inheritance tidak explicit | Cleaner data model | **P2** | Pertimbangkan tambah concept hierarchy |
| 5 | "Powers" relationship type tidak ada | Facilities integration | **P3** | Tambah ke relationship types |
| 6 | Data Classification belum ada | Security compliance | **P2** | Tambah data classification levels |
| 7 | Query Language belum ada | Flexible querying | **P3** | Pertimbangkan GraphQL |
| 8 | Encryption at Rest belum terdefinisi | Data security | **P2** | Tambah encryption config |

### 15.2 Recommendations

| # | Recommendation | Rationale | Effort |
|---|---------------|-----------|--------|
| 1 | Adopsi FIT041 actors/pre-conditions ke DCIM-Wiki UCs | Business context | 1 day |
| 2 | Tambah drift detection ke UC16 | Change management | 2 days |
| 3 | Tambah financial integration ke UC7 | Asset management | 3 days |
| 4 | Tambah capacity planning tool integration | Planning | 3 days |
| 5 | Pertahankan PostgreSQL untuk Phase 1 | Sufficient untuk 150K CIs | — |
| 6 | Neo4j menjadi future consideration | Jika scale > 500K CIs | — |

### 15.3 Tidak Perlu Diubah

| Item | Reason |
|------|--------|
| FIT041 Use Case Analysis | Sudah valid untuk requirements layer |
| DCIM-Wiki UC Analysis | Sudah comprehensive dengan 16 UCs |
| Block 4 Reference Design | Sudah detailed dengan 17 sections |
| PostgreSQL Schema | Sudah detailed dengan 6 tables + indexes |
| Topology Engine | Sudah lengkap dengan 4 algorithms |
| Impact Analysis | Sudah ada scoring model |
| Data Quality Framework | Sudah ada 9 rules + scorecard |

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
| **UC6** | ✅ 3 scenarios (failure, change, maintenance)<br>✅ Impact scoring model accurate<br>✅ Response time < 500ms<br>✅ Estimated downtime included<br>✅ Daftar CI + layanan terpengaruh dalam 30 detik (FIT041) |
| **UC7** | ✅ CI ↔ Asset sync tested<br>✅ Match rate > 95%<br>✅ Conflicts flagged for review<br>✅ Audit trail updated<br>✅ Financial system integration (FIT041) |
| **UC8** | ✅ CI ↔ Discovery sync tested<br>✅ Auto-create new CIs<br>✅ Stale CIs flagged<br>✅ Match rate > 88% |
| **UC9** | ✅ CMDB records terupdate dalam 10s<br>✅ ≥ 99% data completeness<br>✅ CI_ID unique constraint valid<br>✅ Delta detection akurat |
| **UC10** | ✅ End-to-end service view<br>✅ Critical path identified<br>✅ Health score calculated (0-100)<br>✅ Dependency tiers defined |
| **UC11** | ✅ CI counts accurate<br>✅ Data quality metrics available<br>✅ Reconciliation status visible<br>✅ Cache hit rate > 80% |
| **UC12** | ✅ 9 quality rules enforced<br>✅ Scorecard generated daily<br>✅ Quality score > 80%<br>✅ Orphan CIs flagged |
| **UC13** | ✅ NOC dashboard refresh < 15s<br>✅ Real-time CI status visible<br>✅ Topology visualization available<br>✅ Alert integration working |
| **UC14** | ✅ Security events enriched with CI context<br>✅ Enrichment latency < 1s<br>✅ CI lookup < 50ms<br>✅ Cache hit rate > 90% |
| **UC15** | ✅ CI-aware ticket creation working<br>✅ Impact analysis integrated<br>✅ Ticket includes affected CIs<br>✅ Escalation based on CI criticality |
| **UC16** | ✅ All CI changes tracked<br>✅ Audit trail queryable<br>✅ 7 year retention enforced<br>✅ Compliance reports generated<br>✅ Drift terdeteksi dalam 15 menit (FIT041) |

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
| UC1 CI CRUD | — | DCIM-Wiki original | — |
| UC2 Lifecycle | — | DCIM-Wiki original | — |
| UC3 Bulk Import | — | DCIM-Wiki original | — |
| UC4 Relationships | — | DCIM-Wiki original | — |
| UC5 Topology | — | DCIM-Wiki original | — |
| UC6 Impact Analysis | FIT041 UC1: Incident Impact Analysis | **Merged** | Actors, pre-conditions, flow, 30s success criteria |
| UC7 Asset Reconciliation | FIT041 UC3: Asset Lifecycle Management | **Merged** | Actors, pre-conditions, flow, financial integration |
| UC8 Discovery Recon | — | DCIM-Wiki original | — |
| UC9 DI&I Sync | — | DCIM-Wiki original | — |
| UC10 Service Mapping | — | DCIM-Wiki original | — |
| UC11 Health Dashboard | — | DCIM-Wiki original | — |
| UC12 Data Quality | — | DCIM-Wiki original | — |
| UC13 NOC Dashboard | — | DCIM-Wiki original | — |
| UC14 SIEM Enrichment | — | DCIM-Wiki original | — |
| UC15 Workflow | — | DCIM-Wiki original | — |
| UC16 Audit Trail | FIT041 UC2: Change Verification/Audit | **Merged** | Actors, pre-conditions, flow, drift detection |

---

## References

- [[IF-Use_Case_Analysis_CMDB-FIT041-20260121]] — FIT041 Use Case Analysis (source)
- [[cmdb-use-case-analysis]] — DCIM-Wiki Use Case Analysis (source)
- [[fit041-cmdb-use-case-komparasi]] — Comparison document
- [[block4-cmdb]] — Reference design spec
- [[fit041-cmdb-komparasi]] — FIT041 Technical Requirements comparison
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
> **Purpose:** Use Case Analysis final untuk CMDB — 16 use cases, merged actors/pre-conditions/flow dari FIT041 UCs
> **Method:** MCP Sequential Thinking (3 steps) + dcim-comparison skill + document alignment
> **FIT041 UCs Absorbed:** UC1→UC6, UC2→UC16, UC3→UC7
