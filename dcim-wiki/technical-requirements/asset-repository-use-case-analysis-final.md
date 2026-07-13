---
title: "Use Case Analysis — Asset Repository (Final)"
created: 2026-06-25
updated: 2026-06-25
type: use-case-analysis
block: 3
phase: 1
status: final
confidence: high
tags: [use-case, asset-repository, lifecycle, financial, warranty, location, reconciliation, enrichment, fit041, merged]
sources:
  - IF-Use_Case_Analysis_Asset_Repository-FIT041-20260121.md
  - asset-repository-use-case-analysis-final.md
  - asset-repository (entity)
  - asset-data-model (concept)
  - cmdb-reconciliation-runbook (concept)
  - fit041-asset-use-case-komparasi.md
purpose: >
  Final Use Case Analysis untuk Asset Repository — merged dari FIT041 (3 UCs) + DCIM-Wiki (15 UCs).
  Setiap UC dilengkapi: actors, pre-conditions, flow, source systems, data types,
  API endpoints, SLA, data quality, consumers, acceptance criteria.
  FIT041 actors/pre-conditions/flow diadopsi untuk UC6, UC4, UC7.
---

# Use Case Analysis — Asset Repository (Final)

> **Purpose:** Use Case Analysis final untuk Asset Repository — merged dari FIT041 Requirements + DCIM-Wiki Implementation.
> **Cara pakai:** Review per use case untuk memahami data apa yang harus dikelola Asset Repository, dari mana datangnya, dengan SLA berapa, dan ke mana data dikirim.
> **Depends on:** Block 1 (Infrastructure), PostgreSQL, Redis
> **Merge Source:** FIT041 Use Case Analysis Asset Repository (Jan 2026) + DCIM-Wiki Use Case Analysis (Jun 2026)
> **Traceability:** UC6, UC4, UC7 dilengkapi dari FIT041 actors/pre-conditions/flow
> **Related:** [[fit041-asset-use-case-komparasi]] — Komparasi FIT041 UC Analysis vs DCIM-Wiki

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Use Case Taxonomy](#2-use-case-taxonomy)
3. [Asset Data Management Use Cases (UC1–UC3)](#3-asset-data-management-use-cases-uc1uc3)
4. [Asset Lifecycle Use Cases (UC4–UC6)](#4-asset-lifecycle-use-cases-uc4uc6)
5. [Financial & Contract Use Cases (UC7–UC9)](#5-financial--contract-use-cases-uc7uc9)
6. [Integration Use Cases (UC10–UC12)](#6-integration-use-cases-uc10uc12)
7. [Operational Use Cases (UC13–UC15)](#7-operational-use-cases-uc13uc15)
8. [Source System → Use Case Matrix](#8-source-system--use-case-matrix)
9. [Data Type → Use Case Mapping](#9-data-type--use-case-mapping)
10. [API Requirements per Use Case](#10-api-requirements-per-use-case)
11. [SLA & Latency Requirements](#11-sla--latency-requirements)
12. [Data Quality Requirements per Use Case](#12-data-quality-requirements-per-use-case)
13. [Downstream Consumer Mapping](#13-downstream-consumer-mapping)
14. [FIT041 Requirements Checklist](#14-fit041-requirements-checklist)
15. [Acceptance Criteria](#15-acceptance-criteria)
16. [Traceability Matrix](#16-traceability-matrix)

---

## 1. Executive Summary

### Scope

DCIM Core Platform memiliki **5 kategori use case** yang membutuhkan Asset Repository:

| Kategori | Jumlah | Prioritas Rata-rata |
|----------|--------|---------------------|
| **Asset Data Management** | 3 use case (UC1–UC3) | P1–P2 |
| **Asset Lifecycle** | 3 use case (UC4–UC6) | P1–P2 |
| **Financial & Contract** | 3 use case (UC7–UC9) | P2–P3 |
| **Integration** | 3 use case (UC10–UC12) | P1–P2 |
| **Operational** | 3 use case (UC13–UC15) | P1–P3 |
| **Total** | **15 use case** | — |

### Merge Summary

| Aspek | FIT041 | DCIM-Wiki | Merged |
|-------|--------|-----------|--------|
| Use Cases | 3 (conceptual) | 15 (detailed) | **15** (FIT041 UCs absorbed) |
| Actors per UC | ✅ Listed | ⚠️ Implicit | **✅** (UC6, UC4, UC7 dari FIT041) |
| Pre-conditions | ✅ Listed | ⚠️ Implicit | **✅** (UC6, UC4, UC7 dari FIT041) |
| Flow Steps | ✅ 4-5 step | ✅ Architecture | **✅** (merged) |
| Lifecycle States | 1 (In Use) | 7 states | **7 states** |
| SLA Tiers | — | 4 tiers | **4 tiers** |
| Data Quality | 1 rule | 9 rules + scorecard | **9 rules** |
| API Endpoints | Concept | 57 endpoints | **57 endpoints** |
| Acceptance Criteria | Per UC success | 16 items | **16 items** |

### Key Findings

1. **15 use cases** harus didukung oleh Asset Repository
2. **7 lifecycle states** harus dikelola: On Order → Received → Deployed → In Storage → Maintenance → Retired → Disposed
3. **57 API endpoints** diperlukan untuk CRUD, Lifecycle, Financial, Contract, Location, Search, Bulk, Enrichment
4. **4 SLA tiers**: Tier 1 real-time (<50ms), Tier 2 near-RT (<200ms), Tier 3 near-RT (<500ms), Tier 4 batch (<1s)
5. **9 data quality rules** harus terpenuhi dengan scorecard SQL
6. **FIT041 actors/pre-conditions** diadopsi untuk UC6 (Physical Audit), UC4 (Reservation/Deployment), UC7 (Financial Reporting)
7. **FIT041 unique concepts** diadopsi: mobile scanning integration, U-space reservation, capacity planning tool, provisioning system
8. **CMDB reconciliation** menjadi kunci integrasi antara Asset Repository dan CMDB
9. **Enrichment API** menjadi konsumen utama untuk CMDB dan Analytics

### Quick Architecture View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     USE CASES REQUIRING ASSET REPOSITORY                │
│                                                                         │
│  UC1 Asset CRUD        UC2 Bulk Import       UC3 Search & Reporting    │
│  UC4 Lifecycle Mgmt    UC5 Status Transition  UC6 Audit Trail           │
│  UC7 Depreciation      UC8 Warranty Tracking   UC9 Contract Mgmt       │
│  UC10 CMDB Recon       UC11 Discovery Recon    UC12 Enrichment API     │
│  UC13 NOC Dashboard    UC14 Workflow Auto      UC15 Compliance          │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      ASSET REPOSITORY (Block 3)                         │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     API Layer                                     │  │
│  │  Asset CRUD (7) • Lifecycle (4) • Financial (3) • Contract (3)  │  │
│  │  Location (3) • Bulk (2) • Search (1) • Enrichment (1) • Audit │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  ┌────────────────────────┴─────────────────────────────────────────┐  │
│  │                  Service Layer                                    │  │
│  │  Lifecycle Engine • Depreciation Calc • Warranty Checker          │  │
│  │  Reconciliation • Data Quality • Audit Trail • Enrichment Cache  │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  ┌────────────────────────┴─────────────────────────────────────────┐  │
│  │                  Data Layer                                       │  │
│  │  PostgreSQL 16        Redis 7 (cache)                             │  │
│  │  asset,               enrichment cache (TTL 15m)                  │  │
│  │  asset_location,      lifecycle cache                             │  │
│  │  asset_financial,     warranty cache                              │  │
│  │  asset_contract,      search index                                │  │
│  │  asset_lifecycle, asset_audit_trail                               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
         │                 │                │
         ▼                 ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │   CMDB   │    │ Discovery│    │  DI&I        │
  │          │    │  (NMS)   │    │  Gateway     │
  └──────────┘    └──────────┘    └──────────────┘
```

---

## 2. Use Case Taxonomy

### 2.1 Classification

| ID | Use Case Name | Kategori | Prioritas | Latency Target | FIT041 Traceability |
|----|--------------|----------|-----------|----------------|---------------------|
| UC1 | Asset CRUD Operations | Data Management | **P1** | < 50ms p99 | DCIM-Wiki original |
| UC2 | Asset Bulk Import/Export | Data Management | **P3** | Batch (< 1s/record) | DCIM-Wiki original |
| UC3 | Asset Search & Reporting | Data Management | **P2** | < 200ms p99 | DCIM-Wiki original |
| UC4 | Asset Lifecycle Management | Lifecycle | **P1** | < 100ms | **FIT041 UC2** |
| UC5 | Status Transition Management | Lifecycle | **P1** | < 100ms | DCIM-Wiki original |
| UC6 | Asset Audit Trail | Lifecycle | **P3** | Async (real-time logging) | **FIT041 UC1** |
| UC7 | Depreciation Calculation | Financial | **P2** | Batch (daily) | **FIT041 UC3** |
| UC8 | Warranty Tracking | Financial | **P2** | < 500ms | DCIM-Wiki original |
| UC9 | Contract Management | Financial | **P2** | < 500ms | DCIM-Wiki original |
| UC10 | CMDB Reconciliation | Integration | **P1** | Daily + event-driven | DCIM-Wiki original |
| UC11 | Discovery Reconciliation | Integration | **P1** | Hourly | DCIM-Wiki original |
| UC12 | Enrichment API for CMDB | Integration | **P1** | < 200ms | DCIM-Wiki original |
| UC13 | NOC Dashboard Integration | Operational | **P1** | < 5s (near-RT) | DCIM-Wiki original |
| UC14 | Workflow Automation | Operational | **P2** | < 30s (near-RT) | DCIM-Wiki original |
| UC15 | Compliance Reporting | Operational | **P3** | Batch (daily) | DCIM-Wiki original |

### 2.2 Priority Distribution

| Prioritas | Jumlah | Use Cases |
|-----------|--------|-----------|
| **P1 Critical** | 7 | UC1, UC4, UC5, UC10, UC11, UC12, UC13 |
| **P2 High** | 5 | UC3, UC7, UC8, UC9, UC14 |
| **P3 Medium** | 3 | UC2, UC6, UC15 |
| **P4 Supporting** | 0 | — |

---

## 3. Asset Data Management Use Cases (UC1–UC3)

### 3.1 UC1 — Asset CRUD Operations

**Objective:** Create, Read, Update, Delete aset dengan data model yang terstruktur dan teraudit.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | p99 < 50ms (GET), < 100ms (POST/PUT) |
| **Throughput** | 1000 req/s (GET), 100 req/s (POST) |

#### Asset Fields (Mandatory)

| Field | Type | Constraint | Description |
|-------|------|------------|-------------|
| asset_id | VARCHAR(50) | PK, format `AST-{seq}` | Unique identifier |
| serial_number | VARCHAR(100) | UNIQUE, NOT NULL | Manufacturer serial |
| asset_tag | VARCHAR(100) | UNIQUE | Internal barcode/RFID |
| name | VARCHAR(255) | NOT NULL | Asset name |
| model | VARCHAR(100) | — | Model identifier |
| manufacturer | VARCHAR(100) | — | Manufacturer name |
| lifecycle_status | VARCHAR(50) | NOT NULL, ENUM | Current status |

#### Asset Fields (Optional)

| Field | Type | Description |
|-------|------|-------------|
| owner_dept | VARCHAR(100) | Department responsible |
| location_id | VARCHAR(50) | FK to asset_location |
| po_number | VARCHAR(100) | Purchase order reference |
| purchase_date | DATE | Purchase date |
| purchase_cost | DECIMAL(15,2) | Purchase cost |
| warranty_start | DATE | Warranty start |
| warranty_end | DATE | Warranty end |
| contract_id | VARCHAR(50) | FK to asset_contract |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/assets` | asset.write | Create asset |
| GET | `/api/v1/assets` | asset.read | List assets (paginated, filterable) |
| GET | `/api/v1/assets/{id}` | asset.read | Get asset by ID |
| PUT | `/api/v1/assets/{id}` | asset.write | Update asset |
| DELETE | `/api/v1/assets/{id}` | asset.admin | Soft delete asset |
| GET | `/api/v1/assets/search` | asset.read | Search assets |
| GET | `/api/v1/assets/{id}/audit-trail` | asset.read | Get audit trail |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99% (mandatory fields terisi) |
| Accuracy | Serial number unique, asset_tag unique |
| Timeliness | Real-time (API response) |
| Consistency | lifecycle_status in allowed values |
| Validity | Schema validation, CHECK constraints |

---

### 3.2 UC2 — Asset Bulk Import/Export

**Objective:** Bulk operations untuk migrasi data, backup, dan integrasi dengan external systems.

| Aspect | Detail |
|--------|--------|
| **Priority** | P3 Medium |
| **Latency** | Batch (< 1s per record) |
| **Throughput** | ≥ 500 records/batch |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/assets/bulk` | asset.write | Bulk import assets |
| GET | `/api/v1/assets/export` | asset.read | Export assets (CSV/JSON) |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% (tolerance untuk partial records) |
| Accuracy | Per-record validation |
| Timeliness | Batch processing acceptable |
| Consistency | Same validation rules as single CRUD |
| Validity | CSV/XLSX format validation |

---

### 3.3 UC3 — Asset Search & Reporting

**Objective:** Full-text search, filtering, dan reporting untuk asset data.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | p99 < 200ms |
| **Throughput** | 200 req/s |

#### Search Capabilities

| Search Type | Fields | Example |
|-------------|--------|---------|
| Exact Match | asset_id, serial_number, asset_tag | `AST-001` |
| Partial Match | name, model, manufacturer | `Dell*` |
| Range Query | purchase_date, purchase_cost | `2024-01-01 TO 2024-12-31` |
| Filter | lifecycle_status, owner_dept, location_id | `status=Deployed` |
| Aggregate | COUNT, SUM, AVG | `SUM(purchase_cost) GROUP BY owner_dept` |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/assets/search?q=...` | asset.read | Full-text search |
| GET | `/api/v1/assets/report/summary` | asset.read | Summary report |
| GET | `/api/v1/assets/report/depreciation` | asset.read | Depreciation report |
| GET | `/api/v1/assets/report/warranty` | asset.read | Warranty expiry report |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all assets searchable) |
| Accuracy | Search results match query |
| Timeliness | < 200ms response |
| Consistency | Search index consistent with DB |
| Validity | Query syntax valid |

---

## 4. Asset Lifecycle Use Cases (UC4–UC6)

### 4.1 UC4 — Asset Lifecycle Management

> **FIT041 Traceability:** Merged dari FIT041 UC2 (Reservation and Deployment of New Assets)

**Objective:** Track perubahan status aset dari On Order hingga Disposed dengan audit trail lengkap.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 100ms per transition |
| **Audit** | 7 years retention |

#### Actors (from FIT041 UC2)

Server Provisioning System, Capacity Planning Tool, DCIM Operator

#### Pre-conditions (from FIT041 UC2)

- Data kapasitas rak (daya, pendinginan, ruang) diperbarui secara berkala di Asset Repository
- Kebijakan reservasi kapasitas telah ditetapkan (misalnya, penggunaan daya maksimum 80% per rak)
- Rack capacity data updated regularly
- Capacity reservation policies configured

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Input**: Sistem Penyediaan Server mengirimkan spesifikasi aset baru (ukuran U, daya/pendinginan yang diperlukan)
2. **Capacity Check**: Alat Perencanaan Kapasitas mengakses Asset Repository untuk mencari rak dengan kapasitas tersedia yang cukup dan memenuhi spesifikasi
3. **Reservasi**: Asset Repository menandai ruang U yang diidentifikasi (misalnya, Rak A03, U15-U16) sebagai Dipesan dan menghubungkannya dengan catatan tempholder aset baru
4. **Lifecycle Transition**: Setelah instalasi fisik selesai, DCIM Operator memperbarui status aset dari Dipesan menjadi Digunakan
5. **Output**: Asset Repository menyimpan status terbaru dan audit trail

#### Success Criteria (merged)

- Repositori Aset menyediakan lokasi fisik optimal (Data Center, Baris, Rak, Ruang U) dan mengamankan kapasitas dalam waktu 60 detik setelah permintaan diajukan (FIT041)
- Status transition tercatat dengan audit trail lengkap (DCIM-Wiki)

#### Lifecycle States

```
┌───────────┐    ┌───────────┐    ┌───────────┐    ┌─────────────┐
│ On Order  │───→│ Received  │───→│ Deployed  │───→│ In Storage  │
└───────────┘    └───────────┘    └───────────┘    └──────┬──────┘
                                       │                  │
                                       ▼                  ▼
                                 ┌─────────────┐    ┌───────────┐
                                 │ Maintenance │───→│  Retired  │
                                 └─────────────┘    └─────┬─────┘
                                                          │
                                                          ▼
                                                    ┌───────────┐
                                                    │ Disposed  │
                                                    └───────────┘
```

#### State Transition Rules

```
Valid Transitions:
  On Order → Received
  Received → Deployed
  Received → In Storage
  Deployed → Maintenance
  Deployed → In Storage
  Deployed → Retired
  In Storage → Deployed
  In Storage → Maintenance
  In Storage → Retired
  Maintenance → Deployed
  Maintenance → In Storage
  Maintenance → Retired
  Retired → Disposed

Invalid Transitions:
  Disposed → * (terminal state)
  On Order → Deployed (skip receiving)
  On Order → Retired (skip lifecycle)
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/assets/{id}/lifecycle` | asset.write | Transition status |
| GET | `/api/v1/assets/{id}/lifecycle` | asset.read | Get lifecycle history |
| GET | `/api/v1/assets/lifecycle/transitions` | asset.read | Get valid transitions |
| GET | `/api/v1/assets/lifecycle/stats` | asset.read | Lifecycle statistics |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (setiap transition tercatat) |
| Accuracy | old_status = actual previous status |
| Timeliness | Real-time (on transition) |
| Consistency | source consistent (manual/discovery/reconciliation) |
| Validity | new_status in allowed values |

---

### 4.2 UC5 — Status Transition Management

**Objective:** Enforce state machine rules dan validasi transisi status.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 100ms |
| **Validation** | Real-time |

#### Transition Validation Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| Valid source state | Source must be current status | API validation |
| Valid target state | Target must be in allowed transitions | API validation |
| Required fields | Some transitions require additional fields | API validation |
| Approval | Some transitions require approval | Workflow engine |
| Notification | Stakeholders notified on transition | Event bus |

#### Required Fields per Transition

| Transition | Required Fields |
|------------|-----------------|
| On Order → Received | serial_number, received_date |
| Received → Deployed | location_id, owner_dept |
| Deployed → Maintenance | maintenance_type, expected_end_date |
| * → Retired | retirement_reason, disposal_method |
| * → Disposed | disposal_date, disposal_certificate |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/assets/{id}/transition` | asset.write | Execute transition |
| GET | `/api/v1/assets/{id}/transitions/valid` | asset.read | Get valid transitions |
| POST | `/api/v1/assets/{id}/transition/validate` | asset.write | Validate transition |

---

### 4.3 UC6 — Asset Audit Trail

> **FIT041 Traceability:** Merged dari FIT041 UC1 (Physical Asset Audit and Inventory Reconciliation)

**Objective:** Track semua perubahan pada aset untuk compliance dan forensik.

| Aspect | Detail |
|--------|--------|
| **Priority** | P3 Medium |
| **Latency** | Async (real-time logging) |
| **Retention** | 7 years |

#### Actors (from FIT041 UC1)

DCIM Operator, Mobile Scanning Device/Tool

#### Pre-conditions (from FIT041 UC1)

- Semua aset dilengkapi dengan identifikasi yang dapat dipindai (misalnya, kode QR, barcode, RFID)
- Data Asset Repository selalu diperbarui (diperbarui oleh Lapisan Pengambilan Data)
- All assets equipped with scannable identification (QR, barcode, RFID)
- Asset Repository data always up-to-date

#### Trigger (from FIT041 UC1)

Scheduled quarterly audit or an ad-hoc need to locate a specific asset.

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Input**: Operator DCIM memindai tag aset di pusat data (misalnya, Server-B05)
2. **Query**: Perangkat pemindai mengakses Asset Repository menggunakan identifikasi unik
3. **Validate**: Repository mengembalikan lokasi dan atribut yang diharapkan
4. **Reconcile**: Jika lokasi aktual dan status (misalnya, Dalam Penggunaan) sesuai dengan catatan Repository, entri tersebut ditandai sebagai Terverifikasi. Jika terdapat ketidaksesuaian, Peringatan Ketidaksesuaian Audit dicatat
5. **Log**: Semua perubahan tercatat di audit trail
6. **Output**: Operator DCIM menerima umpan balik langsung mengenai status dan lokasi aset melalui perangkat seluler

#### Success Criteria (merged)

- Repositori Aset dapat memverifikasi keberadaan dan lokasi 100% aset kritis serta mengidentifikasi ketidaksesuaian (aset yang hilang atau terselip) dalam waktu 5 menit setelah audit selesai (FIT041)
- Semua perubahan tercatat di audit trail dengan 7-year retention (DCIM-Wiki)

#### Audit Trail Schema

```sql
CREATE TABLE asset_audit_trail (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id VARCHAR(50) NOT NULL REFERENCES asset(asset_id),
    action VARCHAR(20) NOT NULL, -- CREATE, UPDATE, DELETE, TRANSITION, AUDIT
    field_changed VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(50) DEFAULT 'manual', -- manual, api, discovery, reconciliation, mobile_scan
    ip_address INET,
    user_agent TEXT
);
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/assets/{id}/audit-trail` | asset.read | Get audit trail |
| GET | `/api/v1/assets/audit-trail` | asset.read | Search audit trail |
| GET | `/api/v1/assets/audit-trail/stats` | asset.read | Audit statistics |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all changes logged) |
| Accuracy | old_value = actual previous value |
| Timeliness | Real-time (on change) |
| Consistency | source consistent |
| Validity | action in allowed values |

---

## 5. Financial & Contract Use Cases (UC7–UC9)

### 5.1 UC7 — Depreciation Calculation

> **FIT041 Traceability:** Merged dari FIT041 UC3 (Financial Reporting and Depreciation Calculation)

**Objective:** Hitung depresiasi aset berdasarkan metode yang dipilih (straight-line, declining balance, dll.) dan menyediakan laporan keuangan.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | Batch (daily) |
| **Methods** | Straight-line, Declining balance, Units of production |

#### Actors (from FIT041 UC3)

Financial System, Asset Manager

#### Pre-conditions (from FIT041 UC3)

- All assets have associated financial attributes (Purchase Date, Acquisition Cost, Warranty Expiry Date) stored in the Asset Repository
- Semua aset memiliki atribut keuangan yang terkait (Tanggal Pembelian, Biaya Akuisisi, Tanggal Kadaluarsa Garansi) yang tersimpan di Asset Repository

#### Trigger (from FIT041 UC3)

Monthly or quarterly financial closing process.

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Input**: Sistem Keuangan mengajukan permintaan laporan ke Asset Repository
2. **Query**: Repository mengambil semua aset dengan status "Dalam Penggunaan" dan menyaring berdasarkan atribut keuangan
3. **Fetch Data**: Set data mencakup Tanggal Pembelian, Biaya Akuisisi, Umur Pakai yang Diharapkan, dan status saat ini
4. **Calculate**: Hitung depresiasi berdasarkan metode yang dipilih
5. **Output**: Repository menyediakan data dalam format standar (misalnya CSV atau endpoint API) untuk diproses oleh Sistem Keuangan
6. **Maintenance**: Manajer Aset secara rutin memastikan data keuangan untuk aset baru dimasukkan atau diimpor ke dalam Repository

#### Success Criteria (merged)

- Sistem Keuangan dapat menghasilkan laporan inventarisasi lengkap dan terstruktur yang mencakup semua data keuangan yang diperlukan untuk semua aset yang saat ini berstatus "Dalam Penggunaan" di pusat data (FIT041)
- Depresiasi dihitung dengan benar untuk semua metode (DCIM-Wiki)

#### Depreciation Methods

| Method | Formula | Use Case |
|--------|---------|----------|
| Straight-line | (Cost - Salvage) / Useful Life | Standard assets |
| Declining balance | Book Value × Rate | High-tech assets |
| Units of production | (Cost - Salvage) × (Units / Total Units) | Equipment |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/assets/{id}/depreciation` | asset.read | Get depreciation schedule |
| POST | `/api/v1/assets/depreciation/calculate` | asset.write | Calculate depreciation |
| GET | `/api/v1/assets/depreciation/report` | asset.read | Depreciation report |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | 100% (all depreciable assets) |
| Accuracy | Calculation matches method |
| Timeliness | Daily batch acceptable |
| Consistency | Method consistent per asset |
| Validity | Useful life > 0, cost > 0 |

---

### 5.2 UC8 — Warranty Tracking

**Objective:** Track status warranty aset dan notifikasi expiry.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 500ms |
| **Notifications** | 90, 60, 30 days before expiry |

#### Warranty Status

| Status | Condition | Action |
|--------|-----------|--------|
| Active | today < warranty_end | Normal operation |
| Expiring Soon | 90 days >= (warranty_end - today) > 0 | Send notification |
| Expired | today >= warranty_end | Flag for renewal |
| Extended | warranty_end > original_end | Track extension |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/assets/{id}/warranty` | asset.read | Get warranty status |
| GET | `/api/v1/assets/warranty/expiring` | asset.read | List expiring warranties |
| PUT | `/api/v1/assets/{id}/warranty` | asset.write | Update warranty |
| GET | `/api/v1/assets/warranty/report` | asset.read | Warranty report |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 98% (warranty fields populated) |
| Accuracy | Dates match contract |
| Timeliness | Real-time status check |
| Consistency | Status matches date calculation |
| Validity | warranty_start < warranty_end |

---

### 5.3 UC9 — Contract Management

**Objective:** Manage kontrak vendor, SLA terms, dan renewal tracking.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 500ms |
| **Notifications** | 90, 60, 30 days before renewal |

#### Contract Fields

| Field | Type | Description |
|-------|------|-------------|
| contract_id | VARCHAR(50) | PK |
| vendor | VARCHAR(100) | Vendor name |
| contract_type | VARCHAR(50) | Type (maintenance, support, lease) |
| start_date | DATE | Contract start |
| end_date | DATE | Contract end |
| sla_terms | TEXT | SLA description |
| renewal_date | DATE | Auto-renewal date |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/assets/contracts` | asset.read | List contracts |
| GET | `/api/v1/assets/contracts/{id}` | asset.read | Get contract |
| POST | `/api/v1/assets/contracts` | asset.write | Create contract |
| PUT | `/api/v1/assets/contracts/{id}` | asset.write | Update contract |
| GET | `/api/v1/assets/contracts/renewals` | asset.read | List renewals due |
| GET | `/api/v1/assets/contracts/report` | asset.read | Contract report |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% (contract fields populated) |
| Accuracy | Dates, vendor match PO |
| Timeliness | Real-time status check |
| Consistency | Contract linked to assets |
| Validity | start_date < end_date |

---

## 6. Integration Use Cases (UC10–UC12)

### 6.1 UC10 — CMDB Reconciliation

**Objective:** Sinkronisasi data antara Asset Repository dan CMDB.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | Daily batch + event-driven |
| **Match Keys** | serial_number + asset_tag |

#### Reconciliation Flow

```
1. Asset Repository → Export asset data
2. CMDB → Export CI data
3. Match by serial_number + asset_tag
4. Detect conflicts (newer wins)
5. Update both systems
6. Log all changes
```

#### Conflict Resolution Rules

| Scenario | Resolution |
|----------|------------|
| Asset exists, CI missing | Create CI from asset |
| CI exists, asset missing | Flag for review |
| Both exist, same data | No action |
| Both exist, different data | Newer timestamp wins |
| Both exist, critical conflict | Flag for manual review |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/assets/reconciliation/cmdb` | asset.write | Trigger reconciliation |
| GET | `/api/v1/assets/reconciliation/cmdb/status` | asset.read | Get status |
| GET | `/api/v1/assets/reconciliation/cmdb/log` | asset.read | Get reconciliation log |
| GET | `/api/v1/assets/reconciliation/cmdb/conflicts` | asset.read | List conflicts |

---

### 6.2 UC11 — Discovery Reconciliation

**Objective:** Sinkronisasi data aset dengan discovery data dari NMS, scanning tools.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | Hourly |
| **Sources** | NMS, network scanners, cloud APIs |

#### Discovery Sources

| Source | Protocol | Data Type |
|--------|----------|-----------|
| NMS (SNMP) | SNMP | Network devices |
| Server discovery | SSH/WMI | Servers |
| Cloud API | REST | Cloud assets |
| Network scanner | SNMP/ICMP | Network inventory |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/assets/reconciliation/discovery` | asset.write | Trigger reconciliation |
| GET | `/api/v1/assets/reconciliation/discovery/status` | asset.read | Get status |
| GET | `/api/v1/assets/reconciliation/discovery/log` | asset.read | Get log |

---

### 6.3 UC12 — Enrichment API for CMDB

**Objective:** Provide read-optimized API untuk CMDB dan analytics consumers.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 200ms (cached) |
| **Cache** | Redis, TTL 15 minutes |

#### Enrichment Response Schema

```json
{
  "asset_id": "AST-001",
  "serial_number": "SN-12345",
  "asset_tag": "TAG-67890",
  "owner_dept": "IT Infrastructure",
  "warranty_status": "active",
  "warranty_end": "2027-12-31",
  "contract_status": "active",
  "contract_id": "CON-001",
  "location": {
    "building": "DC-JKT",
    "floor": "3",
    "room": "Server Room A",
    "rack": "Rack-A1",
    "position_u": "U10-U20"
  },
  "lifecycle_status": "Deployed",
  "last_updated": "2026-06-25T10:30:00Z"
}
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/assets/enrich/{ci_id}` | asset.read | Enrichment for CMDB |
| GET | `/api/v1/assets/enrich/batch` | asset.read | Batch enrichment |
| POST | `/api/v1/assets/enrich/cache/invalidate` | asset.admin | Invalidate cache |

#### Cache Strategy

```python
# Key: enrich:{asset_id}
# TTL: 15 minutes
# Invalidate on: asset update, lifecycle transition
# Hit rate target: ≥ 95%
```

---

## 7. Operational Use Cases (UC13–UC15)

### 7.1 UC13 — NOC Dashboard Integration

**Objective:** Provide real-time asset data untuk NOC dashboard.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5s (near-RT) |
| **Updates** | WebSocket/SSE |

#### Dashboard Views

| View | Data | Refresh |
|------|------|---------|
| Asset Summary | Total, by status, by location | 5 min |
| Warranty Expiry | Expiring in 30/60/90 days | 1 hour |
| Contract Renewal | Renewals due | 1 day |
| Asset Health | Status distribution | 5 min |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/assets/dashboard/summary` | asset.read | Dashboard summary |
| GET | `/api/v1/assets/dashboard/warranty` | asset.read | Warranty dashboard |
| GET | `/api/v1/assets/dashboard/contract` | asset.read | Contract dashboard |
| WS | `/ws/assets` | asset.read | Real-time updates |

---

### 7.2 UC14 — Workflow Automation

**Objective:** Trigger workflows berdasarkan asset events.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 30s (near-RT) |
| **Engine** | n8n / custom workflow |

#### Workflow Triggers

| Trigger | Action | Consumer |
|---------|--------|----------|
| Asset deployed | Create CMDB CI | CMDB |
| Warranty expiring | Create renewal ticket | ITSM |
| Contract expiring | Notify procurement | Email |
| Maintenance due | Create maintenance ticket | ITSM |
| Asset retired | Update CMDB status | CMDB |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/assets/{id}/workflow` | asset.write | Trigger workflow |
| GET | `/api/v1/assets/workflows` | asset.read | List workflows |
| GET | `/api/v1/assets/{id}/workflows` | asset.read | Asset workflows |

---

### 7.3 UC15 — Compliance Reporting

**Objective:** Generate compliance reports untuk audit dan regulatory.

| Aspect | Detail |
|--------|--------|
| **Priority** | P3 Medium |
| **Latency** | Batch (daily) |
| **Reports** | Asset inventory, depreciation, warranty |

#### Compliance Reports

| Report | Frequency | Consumers |
|--------|-----------|-----------|
| Asset Inventory | Daily | Management, Audit |
| Depreciation Schedule | Monthly | Finance |
| Warranty Status | Weekly | Operations |
| Contract Summary | Monthly | Procurement |
| Audit Trail | On-demand | Compliance |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/assets/compliance/inventory` | asset.read | Inventory report |
| GET | `/api/v1/assets/compliance/depreciation` | asset.read | Depreciation report |
| GET | `/api/v1/assets/compliance/warranty` | asset.read | Warranty report |
| GET | `/api/v1/assets/compliance/audit` | asset.read | Audit report |

---

## 8. Source System → Use Case Matrix

| Source System | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | UC10 | UC11 | UC12 | UC13 | UC14 | UC15 |
|---------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|------|------|------|------|------|
| Manual Entry | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | — | ✅ | ✅ | — | — | — | — | — | — |
| ITSM | — | — | — | ✅ | ✅ | ✅ | — | — | ✅ | — | — | — | — | ✅ | — |
| NMS | — | — | — | — | — | — | — | — | — | — | ✅ | — | — | — | — |
| Discovery | — | — | — | — | — | — | — | — | — | — | ✅ | — | — | — | — |
| CMDB | — | — | — | — | — | — | — | — | — | ✅ | — | — | — | — | — |
| Finance | — | — | — | — | — | — | ✅ | — | ✅ | — | — | — | — | — | ✅ |
| Workflow | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | — | ✅ | — |
| Provisioning System | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | — | — | — |
| Mobile Scanning | — | — | — | — | — | ✅ | — | — | — | — | — | — | — | — | — |
| Capacity Planning | — | — | — | ✅ | — | — | — | — | — | — | — | — | — | — | — |

---

## 9. Data Type → Use Case Mapping

| Data Type | Primary UC | Secondary UC | Consumer |
|-----------|------------|--------------|----------|
| Asset Master | UC1 | UC3, UC12 | CMDB, Analytics |
| Lifecycle Status | UC4 | UC5, UC6 | CMDB, Workflow |
| Financial Data | UC7 | UC15 | Finance, Compliance |
| Warranty Data | UC8 | UC14 | Operations, ITSM |
| Contract Data | UC9 | UC14, UC15 | Procurement, Compliance |
| Location Data | UC1 | UC3, UC13 | NOC, Facilities |
| Audit Trail | UC6 | UC15 | Compliance, Forensics |

---

## 10. API Requirements per Use Case

| UC | Endpoints | Auth | Cache | Rate Limit |
|----|-----------|------|-------|------------|
| UC1 | 7 | asset.read/write/admin | Redis 15m | 1000 req/s |
| UC2 | 2 | asset.write/read | — | 10 req/s |
| UC3 | 4 | asset.read | Redis 5m | 200 req/s |
| UC4 | 4 | asset.write/read | Redis 5m | 100 req/s |
| UC5 | 3 | asset.write/read | — | 100 req/s |
| UC6 | 3 | asset.read | — | 100 req/s |
| UC7 | 3 | asset.read/write | — | 10 req/s |
| UC8 | 4 | asset.read/write | Redis 15m | 100 req/s |
| UC9 | 6 | asset.read/write | Redis 15m | 100 req/s |
| UC10 | 4 | asset.write/read | — | 1 req/min |
| UC11 | 3 | asset.write/read | — | 1 req/min |
| UC12 | 3 | asset.read/admin | Redis 15m | 1000 req/s |
| UC13 | 4 | asset.read | Redis 5m | 100 req/s |
| UC14 | 3 | asset.write/read | — | 10 req/s |
| UC15 | 4 | asset.read | — | 10 req/s |
| **Total** | **57** | — | — | — |

---

## 11. SLA & Latency Requirements

| Tier | Latency | Use Cases | Throughput |
|------|---------|-----------|------------|
| **Tier 1** (Real-time) | < 50ms p99 | UC1 (GET), UC12 | 1000 req/s |
| **Tier 2** (Near-RT) | < 200ms p99 | UC3, UC4, UC8, UC9 | 200 req/s |
| **Tier 3** (Near-RT) | < 500ms p99 | UC5, UC6 | 100 req/s |
| **Tier 4** (Batch) | < 1s/record | UC2, UC7, UC10, UC11, UC15 | Batch |

---

## 12. Data Quality Requirements per Use Case

| UC | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----|--------------|----------|------------|-------------|----------|
| UC1 | ≥ 99% | Serial/Tag unique | Real-time | Status ENUM | Schema |
| UC2 | ≥ 95% | Per-record | Batch | Same as CRUD | Format |
| UC3 | 100% | Search match | < 200ms | Index sync | Query |
| UC4 | 100% | Old = actual | Real-time | Source一致 | Transition |
| UC5 | 100% | Transition valid | Real-time | State machine | Rules |
| UC6 | 100% | Old value correct | Real-time | Source一致 | Action |
| UC7 | 100% | Calc correct | Batch | Method一致 | Formula |
| UC8 | ≥ 98% | Dates match | Real-time | Status = dates | Date |
| UC9 | ≥ 95% | Vendor/PO match | Real-time | Linked | Date |
| UC10 | 100% | Match correct | Daily | Both systems | Match |
| UC11 | 100% | Discovery correct | Hourly | Both systems | Source |
| UC12 | 100% | Cache hit | < 200ms | Cache = DB | Schema |
| UC13 | 100% | Dashboard correct | < 5s | View一致 | Format |
| UC14 | 100% | Trigger correct | < 30s | Event一致 | Trigger |
| UC15 | 100% | Report correct | Batch | Report一致 | Format |

---

## 13. Downstream Consumer Mapping

| Consumer | Use Case | Data Consumed | SLA |
|----------|----------|---------------|-----|
| **CMDB** | UC10, UC12 | Asset master, location, warranty | < 200ms |
| **Analytics** | UC3, UC7 | Asset data, depreciation | Batch |
| **NOC Dashboard** | UC13 | Real-time asset status | < 5s |
| **Workflow Engine** | UC14 | Asset events | < 30s |
| **ITSM** | UC8, UC9 | Warranty, contract status | < 500ms |
| **Finance** | UC7, UC15 | Depreciation, compliance | Batch |
| **Compliance** | UC6, UC15 | Audit trail, reports | Batch |
| **SIEM** | UC12 | Asset enrichment | < 1s |
| **Provisioning System** | UC4, UC5 | Capacity, location | < 100ms |
| **Mobile Scanning** | UC6 | Audit data, verification | < 500ms |

---

## 14. FIT041 Requirements Checklist

| Requirement Type | Requirement | Status |
|-----------------|-------------|--------|
| **Technical** | Unique identification (serial number, asset tag) | ✅ UC1 |
| **Technical** | Geolocation fields (building, floor, room, rack, U-space) | ✅ UC1, asset_location |
| **Performance** | Asset search < 10ms (FIT041) / < 50ms (DCIM-Wiki) | ⚠️ Adopt < 50ms |
| **Scalability** | Store and access asset records efficiently | ✅ 1000 req/s |
| **Security** | RBAC for financial and status attributes | ✅ asset.read/write/admin |
| **Data Quality** | Type validation for critical fields (U-space integer) | ✅ 9 DQ rules |

---

## 15. Acceptance Criteria

### UC1 — Asset CRUD

- [ ] Asset created with all mandatory fields
- [ ] Asset retrieved by ID in < 50ms
- [ ] Asset updated with audit trail
- [ ] Asset soft-deleted (not hard-deleted)
- [ ] Duplicate serial_number rejected
- [ ] Duplicate asset_tag rejected

### UC4 — Lifecycle Management

- [ ] Status transition enforced (valid source → target)
- [ ] Invalid transition rejected with error
- [ ] Audit trail logged for every transition
- [ ] Required fields validated per transition
- [ ] 7-year retention enforced
- [ ] FIT041: Optimal location provided in < 60 seconds

### UC6 — Audit Trail

- [ ] All changes logged with actor and timestamp
- [ ] FIT041: Mobile scan verifies asset location
- [ ] FIT041: Discrepancy warning generated on mismatch
- [ ] FIT041: 100% critical assets verified in 5 minutes
- [ ] 7-year retention enforced
- [ ] Audit trail searchable

### UC7 — Depreciation

- [ ] Depreciation calculated for all 3 methods
- [ ] FIT041: Financial report generated for "In Use" assets
- [ ] FIT041: Output available as CSV or API endpoint
- [ ] Asset Manager can update financial data
- [ ] Monthly/quarterly closing supported

### UC10 — CMDB Reconciliation

- [ ] Match by serial_number + asset_tag
- [ ] Conflict resolution (newer wins)
- [ ] Reconciliation log generated
- [ ] Conflicts flagged for manual review
- [ ] Both systems updated atomically

### UC12 — Enrichment API

- [ ] Response < 200ms (cached)
- [ ] Cache hit rate ≥ 95%
- [ ] Cache invalidated on asset update
- [ ] All required fields present
- [ ] CMDB can consume without transformation

---

## 16. Traceability Matrix

| UC | Source | Block | Phase | Priority | FIT041 |
|----|--------|-------|-------|----------|--------|
| UC1 | DCIM-Wiki | 3 | 1 | P1 | — |
| UC2 | DCIM-Wiki | 3 | 1 | P3 | — |
| UC3 | DCIM-Wiki | 3 | 1 | P2 | — |
| UC4 | DCIM-Wiki + FIT041 | 3 | 1 | P1 | **FIT041 UC2** |
| UC5 | DCIM-Wiki | 3 | 1 | P1 | — |
| UC6 | DCIM-Wiki + FIT041 | 3 | 1 | P3 | **FIT041 UC1** |
| UC7 | DCIM-Wiki + FIT041 | 3 | 1 | P2 | **FIT041 UC3** |
| UC8 | DCIM-Wiki | 3 | 1 | P2 | — |
| UC9 | DCIM-Wiki | 3 | 1 | P2 | — |
| UC10 | DCIM-Wiki | 3 | 1 | P1 | — |
| UC11 | DCIM-Wiki | 3 | 1 | P1 | — |
| UC12 | DCIM-Wiki | 3 | 1 | P1 | — |
| UC13 | DCIM-Wiki | 3 | 1 | P1 | — |
| UC14 | DCIM-Wiki | 3 | 1 | P2 | — |
| UC15 | DCIM-Wiki | 3 | 1 | P3 | — |

---

## Document History

| Date | Version | Changes |
|------|---------|---------|
| 2026-06-25 | 1.0 | Initial creation — 15 use cases for Asset Repository |
| 2026-06-25 | 2.0 | Merged FIT041 UCs (3) + DCIM-Wiki (15). UC6 enriched with FIT041 UC1 actors/pre-conditions/flow. UC4 enriched with FIT041 UC2 actors/pre-conditions/flow. UC7 enriched with FIT041 UC3 actors/pre-conditions/flow. Added FIT041 Requirements Checklist. Added Provisioning System and Mobile Scanning to Source System matrix. Updated Acceptance Criteria with FIT041 success criteria. |

---

> **Next Steps:**
> 1. Review with stakeholders (NOC, Facilities, Finance, Procurement)
> 2. Validate API endpoints with backend team
> 3. Confirm SLA requirements with operations
> 4. Evaluate FIT041 unique concepts (Mobile Scanning, U-space Reservation, Capacity Planning) for Phase 2
> 5. Begin implementation — Block 3 (Asset Repository)