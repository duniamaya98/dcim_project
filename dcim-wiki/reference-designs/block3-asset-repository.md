---
title: "Block 3 — Asset Repository: Reference Design Spec"
created: 2026-06-23
updated: 2026-06-23
type: reference-design
block: 3
phase: 1
status: generated
confidence: high
tags: [asset-repository, crud, bulk-import, reconciliation, audit-trail, enrichment, redis-cache, nvr, camera, location-validation]
wiki_pages:
  - asset-repository
  - asset-data-model
  - postgresql
  - redis
  - cmdb
  - data-ingestion-integration
  - api-design-principles
purpose: >
  Reference design spec untuk Block 3 Asset Repository.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Block 3 — Asset Repository: Reference Design Spec

> **Purpose:** Dokumen referensi lengkap untuk Asset Repository — SSOT aset fisik, finansial, dan kontrak.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi aktual. Setiap gap dicatat sebagai connection point.
> **Architecture Diagram:** `diagrams/block3-asset-repository-architecture.html` — buka di browser untuk visualisasi interaktif.
> **Depends on:** Block 1 (Infrastructure)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Asset Data Model](#2-asset-data-model)
3. [PostgreSQL Schema](#3-postgresql-schema)
4. [CRUD API](#4-crud-api)
5. [Bulk Import API](#5-bulk-import-api)
6. [Reconciliation Engine](#6-reconciliation-engine)
7. [Audit Trail](#7-audit-trail)
8. [Enrichment API](#8-enrichment-api)
9. [Data Quality Framework](#9-data-quality-framework)
10. [Performance & Caching](#10-performance--caching)
11. [Security](#11-security)
12. [Monitoring & Alerting](#12-monitoring--alerting)
13. [Acceptance Criteria](#13-acceptance-criteria)
14. [NVR Integration Extensions](#15-nvr-integration-extensions)
15. [Gap Comparison Template](#16-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────┐
│                 Asset Repository                            │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    API Layer                          │  │
│  │  CRUD • Bulk Import • Enrichment • Search • Audit    │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                 │
│  ┌────────────────────────┴─────────────────────────────┐  │
│  │                 Service Layer                         │  │
│  │  Validation • Reconciliation • Audit Trail • Cache   │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                 │
│  ┌────────────────────────┴─────────────────────────────┐  │
│  │                 Data Layer                            │  │
│  │  PostgreSQL 16 (primary)    Redis 7 (cache)          │  │
│  └────────────────────────┬─────────────────────────────┘  │
│                           │                                 │
└───────────────────────────┼─────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          │                 │                 │
          ▼                 ▼                 ▼
    ┌──────────┐    ┌──────────┐    ┌──────────┐
    │   CMDB   │    │   DI&I   │    │Analytics │
    │ (SSOT CI)│    │ Gateway  │    │  Engine  │
    └──────────┘    └──────────┘    └──────────┘
```

### 1.2 Data Flow

```
Ingestion Sources:
  1. Bulk Import (CSV/JSON) → Validation → Upsert
  2. DI&I Gateway (asset.updates topic) → Consumer → Validate → Upsert
  3. CMDB Reconciliation → Match → Update
  4. Manual API (CRUD) → Validate → Write

Output Consumers:
  1. CMDB Reconciliation → Enrichment API (CI → Asset mapping)
  2. Analytics Engine → Enrichment API (asset metrics)
  3. DI&I Gateway → Audit Trail (change events)
```

### 1.3 Core Responsibilities

| Responsibility | Description | SLA |
|---------------|-------------|-----|
| Asset Master Data | CRUD for all asset attributes | 99.9% availability |
| Lifecycle Management | Track asset from procurement to disposal | Real-time status |
| Location Tracking | Physical location (building → rack → U) | Accurate to room level |
| Financial Tracking | Cost, depreciation, book value | Updated monthly |
| Contract Management | Warranty, SLA, renewal dates | Alerts 30d before expiry |
| Enrichment API | Read-optimized for CMDB/Analytics | p99 < 50ms |
| Audit Trail | Every change logged with full history | Immutable |

---

## 2. Asset Data Model

### 2.1 Entity Relationship Diagram

```
┌──────────────────┐       ┌──────────────────┐
│      asset       │       │  asset_location   │
│──────────────────│       │──────────────────│
│ asset_id (PK)    │──FK──→│ location_id (PK) │
│ serial_number    │       │ building         │
│ asset_tag        │       │ floor            │
│ name             │       │ room             │
│ model            │       │ rack             │
│ manufacturer     │       │ position_u       │
│ owner_dept       │       │ latitude         │
│ location_id (FK) │       │ longitude        │
│ po_number        │       └──────────────────┘
│ purchase_date    │
│ purchase_cost    │       ┌──────────────────┐
│ warranty_start   │       │ asset_financial  │
│ warranty_end     │       │──────────────────│
│ contract_id (FK) │──FK──→│ asset_id (PK)    │
│ lifecycle_status │       │ depreciation_method│
│ created_at       │       │ useful_life_years │
│ updated_at       │       │ book_value        │
└──────────────────┘       │ last_depreciation │
                           └──────────────────┘
                           ┌──────────────────┐
                           │ asset_contract   │
                           │──────────────────│
                           │ contract_id (PK) │
                           │ vendor           │
                           │ contract_type    │
                           │ start_date       │
                           │ end_date         │
                           │ sla_terms        │
                           │ renewal_date     │
                           └──────────────────┘
```

### 2.2 Asset Lifecycle States

```
┌─────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ On Order │───→│ Received │───→│ Deployed │───→│In Storage │
└─────────┘    └──────────┘    └──────────┘    └───────────┘
                                     │                │
                                     │                ▼
                                     │          ┌───────────┐
                                     └─────────→│Maintenance│
                                                └─────┬─────┘
                                                      │
                                          ┌───────────┴───────────┐
                                          ▼                       ▼
                                    ┌──────────┐           ┌──────────┐
                                    │ Retired  │──────────→│ Disposed │
                                    └──────────┘           └──────────┘
```

### 2.3 Field Specifications

#### Core Asset Fields

| Field | Type | Required | Unique | Validation | Description |
|-------|------|----------|--------|------------|-------------|
| `asset_id` | UUID | Yes | Yes | Auto-generated | Primary key, format `AST-{seq}` |
| `serial_number` | VARCHAR(100) | Yes | Per manufacturer | No special chars | Manufacturer serial |
| `asset_tag` | VARCHAR(50) | Yes | Yes | Alphanumeric + dash | Internal barcode/RFID |
| `name` | VARCHAR(255) | Yes | No | — | Human-readable name |
| `model` | VARCHAR(100) | Yes | No | — | Product model |
| `manufacturer` | VARCHAR(100) | Yes | No | — | Manufacturer/vendor |
| `description` | TEXT | No | No | Max 2000 chars | Free text description |
| `owner_dept` | VARCHAR(100) | Yes | No | Must exist in org | Department responsible |
| `location_id` | UUID | Yes | No | FK → asset_location | Physical location |
| `po_number` | VARCHAR(50) | No | No | — | Purchase order ref |
| `purchase_date` | DATE | No | No | ≤ today | Procurement date |
| `purchase_cost` | DECIMAL(12,2) | No | No | ≥ 0 | Purchase price |
| `warranty_start` | DATE | No | No | ≤ warranty_end | Warranty start |
| `warranty_end` | DATE | No | No | ≥ warranty_start | Warranty expiry |
| `contract_id` | UUID | No | No | FK → asset_contract | Linked contract |
| `lifecycle_status` | ENUM | Yes | No | See lifecycle states | Current status |
| `created_at` | TIMESTAMPTZ | Auto | No | — | Record creation |
| `updated_at` | TIMESTAMPTZ | Auto | No | — | Last modification |

#### Location Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `location_id` | UUID | Yes | Primary key |
| `site_name` | VARCHAR(100) | Yes | Data center site |
| `building` | VARCHAR(100) | Yes | Building identifier |
| `floor` | VARCHAR(20) | Yes | Floor number/label |
| `room` | VARCHAR(50) | Yes | Room identifier |
| `rack` | VARCHAR(50) | No | Rack identifier |
| `position_u` | VARCHAR(20) | No | U position in rack |
| `latitude` | DECIMAL(9,6) | No | GPS latitude |
| `longitude` | DECIMAL(9,6) | No | GPS longitude |

#### Financial Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `asset_id` | UUID | Yes | FK → asset |
| `depreciation_method` | ENUM | Yes | straight_line, declining_balance, units_of_production |
| `useful_life_years` | INTEGER | Yes | > 0, ≤ 30 |
| `book_value` | DECIMAL(12,2) | Yes | ≥ 0 |
| `last_depreciation_date` | DATE | No | Last depreciation run |

#### Contract Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `contract_id` | UUID | Yes | Primary key |
| `vendor` | VARCHAR(100) | Yes | Contract vendor |
| `contract_type` | ENUM | Yes | warranty, sla, support, lease, maintenance |
| `start_date` | DATE | Yes | Contract start |
| `end_date` | DATE | Yes | Contract end |
| `sla_terms` | TEXT | No | SLA description |
| `renewal_date` | DATE | No | Auto-renewal date |
| `total_value` | DECIMAL(12,2) | No | Contract total value |

---

## 3. PostgreSQL Schema

### 3.1 Tables

```sql
-- Migration 001: Create tables

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- asset_location
-- ============================================
CREATE TABLE asset_location (
    location_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    site_name VARCHAR(100) NOT NULL,
    building VARCHAR(100) NOT NULL,
    floor VARCHAR(20) NOT NULL,
    room VARCHAR(50) NOT NULL,
    rack VARCHAR(50),
    position_u VARCHAR(20),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Unique constraint: rack + position within room
    CONSTRAINT uq_location_rack UNIQUE (room, rack, position_u)
);

-- ============================================
-- asset_contract
-- ============================================
CREATE TABLE asset_contract (
    contract_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor VARCHAR(100) NOT NULL,
    contract_type VARCHAR(20) NOT NULL
        CHECK (contract_type IN ('warranty', 'sla', 'support', 'lease', 'maintenance')),
    contract_number VARCHAR(50),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    sla_terms TEXT,
    renewal_date DATE,
    total_value DECIMAL(12,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT chk_contract_dates CHECK (end_date >= start_date)
);

-- ============================================
-- asset
-- ============================================
CREATE TABLE asset (
    asset_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_tag VARCHAR(50) NOT NULL UNIQUE,
    serial_number VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    model VARCHAR(100) NOT NULL,
    manufacturer VARCHAR(100) NOT NULL,
    description TEXT,

    -- Ownership
    owner_dept VARCHAR(100) NOT NULL,

    -- Location
    location_id UUID NOT NULL REFERENCES asset_location(location_id),

    -- Procurement
    po_number VARCHAR(50),
    purchase_date DATE,
    purchase_cost DECIMAL(12,2) CHECK (purchase_cost >= 0),

    -- Warranty
    warranty_start DATE,
    warranty_end DATE,

    -- Contract
    contract_id UUID REFERENCES asset_contract(contract_id),

    -- Lifecycle
    lifecycle_status VARCHAR(20) NOT NULL DEFAULT 'received'
        CHECK (lifecycle_status IN (
            'on_order', 'received', 'deployed', 'in_storage',
            'maintenance', 'retired', 'disposed'
        )),

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),

    -- Constraints
    CONSTRAINT chk_warranty_dates CHECK (
        warranty_end IS NULL OR warranty_start IS NULL OR warranty_end >= warranty_start
    ),
    CONSTRAINT uq_serial_manufacturer UNIQUE (serial_number, manufacturer)
);

-- ============================================
-- asset_financial
-- ============================================
CREATE TABLE asset_financial (
    asset_id UUID PRIMARY KEY REFERENCES asset(asset_id) ON DELETE CASCADE,
    depreciation_method VARCHAR(20) NOT NULL DEFAULT 'straight_line'
        CHECK (depreciation_method IN ('straight_line', 'declining_balance', 'units_of_production')),
    useful_life_years INTEGER NOT NULL CHECK (useful_life_years > 0 AND useful_life_years <= 30),
    book_value DECIMAL(12,2) NOT NULL CHECK (book_value >= 0),
    last_depreciation_date DATE,
    salvage_value DECIMAL(12,2) DEFAULT 0 CHECK (salvage_value >= 0),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- asset_audit_log (immutable)
-- ============================================
CREATE TABLE asset_audit_log (
    audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    asset_id UUID NOT NULL,
    action VARCHAR(10) NOT NULL CHECK (action IN ('create', 'update', 'delete', 'import', 'reconcile')),
    field_name VARCHAR(100),
    old_value TEXT,
    new_value TEXT,
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(50) NOT NULL,  -- 'api', 'bulk_import', 'di_reconciliation', 'manual'
    ip_address INET
);

-- ============================================
-- asset_reconciliation_log
-- ============================================
CREATE TABLE asset_reconciliation_log (
    reconciliation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(50) NOT NULL,  -- 'cmdb', 'discovery', 'erp'
    total_records INTEGER,
    matched INTEGER,
    created INTEGER,
    updated INTEGER,
    conflicts INTEGER,
    errors INTEGER,
    duration_ms INTEGER,
    status VARCHAR(20) DEFAULT 'running'
        CHECK (status IN ('running', 'completed', 'failed'))
);
```

### 3.2 Indexes

```sql
-- Migration 002: Create indexes

-- Asset searches
CREATE INDEX idx_asset_serial ON asset(serial_number);
CREATE INDEX idx_asset_manufacturer ON asset(manufacturer);
CREATE INDEX idx_asset_tag ON asset(asset_tag);
CREATE INDEX idx_asset_owner ON asset(owner_dept);
CREATE INDEX idx_asset_location ON asset(location_id);
CREATE INDEX idx_asset_lifecycle ON asset(lifecycle_status);
CREATE INDEX idx_asset_contract ON asset(contract_id);
CREATE INDEX idx_asset_purchase_date ON asset(purchase_date);
CREATE INDEX idx_asset_warranty_end ON asset(warranty_end) WHERE warranty_end IS NOT NULL;

-- Composite indexes for common queries
CREATE INDEX idx_asset_serial_manufacturer ON asset(serial_number, manufacturer);
CREATE INDEX idx_asset_lifecycle_owner ON asset(lifecycle_status, owner_dept);
CREATE INDEX idx_asset_location_lifecycle ON asset(location_id, lifecycle_status);

-- Location searches
CREATE INDEX idx_location_building ON asset_location(building);
CREATE INDEX idx_location_room ON asset_location(room);
CREATE INDEX idx_location_rack ON asset_location(rack);

-- Contract searches
CREATE INDEX idx_contract_vendor ON asset_contract(vendor);
CREATE INDEX idx_contract_end_date ON asset_contract(end_date);
CREATE INDEX idx_contract_type ON asset_contract(contract_type);

-- Audit log (partitioned by month)
CREATE INDEX idx_audit_asset ON asset_audit_log(asset_id);
CREATE INDEX idx_audit_changed_at ON asset_audit_log(changed_at);
CREATE INDEX idx_audit_action ON asset_audit_log(action);

-- Financial
CREATE INDEX idx_financial_depreciation ON asset_financial(last_depreciation_date);

-- Reconciliation
CREATE INDEX idx_reconciliation_run_at ON asset_reconciliation_log(run_at);
CREATE INDEX idx_reconciliation_source ON asset_reconciliation_log(source);
```

### 3.3 Triggers

```sql
-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_asset_updated
    BEFORE UPDATE ON asset
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_location_updated
    BEFORE UPDATE ON asset_location
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_contract_updated
    BEFORE UPDATE ON asset_contract
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

CREATE TRIGGER trg_financial_updated
    BEFORE UPDATE ON asset_financial
    FOR EACH ROW EXECUTE FUNCTION update_timestamp();

-- Partition audit_log by month
CREATE TABLE asset_audit_log_2026_06 PARTITION OF asset_audit_log
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');
```

---

## 4. CRUD API

### 4.1 API Design

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|------------|-------------|
| POST | `/api/v1/assets` | RBAC: asset.write | 100/min | Create asset |
| GET | `/api/v1/assets` | RBAC: asset.read | 1000/min | List assets (paginated) |
| GET | `/api/v1/assets/{id}` | RBAC: asset.read | 1000/min | Get asset by ID |
| PUT | `/api/v1/assets/{id}` | RBAC: asset.write | 100/min | Update asset |
| DELETE | `/api/v1/assets/{id}` | RBAC: asset.admin | 50/min | Soft delete asset |
| GET | `/api/v1/assets/search` | RBAC: asset.read | 500/min | Search assets |

### 4.2 Request/Response Schemas

#### Create Asset

```json
// POST /api/v1/assets
// Request
{
  "asset_tag": "AST-RACK-A1-001",
  "serial_number": "SN-12345678",
  "name": "Dell PowerEdge R750",
  "model": "R750",
  "manufacturer": "Dell",
  "owner_dept": "IT Infrastructure",
  "location_id": "550e8400-e29b-41d4-a716-446655440000",
  "po_number": "PO-2026-001",
  "purchase_date": "2026-01-15",
  "purchase_cost": 15000.00,
  "warranty_start": "2026-01-15",
  "warranty_end": "2029-01-15",
  "lifecycle_status": "received"
}

// Response (201 Created)
{
  "asset_id": "660e8400-e29b-41d4-a716-446655440001",
  "asset_tag": "AST-RACK-A1-001",
  "serial_number": "SN-12345678",
  "name": "Dell PowerEdge R750",
  "lifecycle_status": "received",
  "created_at": "2026-06-23T14:30:00.000Z",
  "updated_at": "2026-06-23T14:30:00.000Z"
}
```

#### List Assets

```json
// GET /api/v1/assets?page=1&limit=20&status=deployed&owner_dept=IT
// Response (200 OK)
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1547,
    "total_pages": 78
  },
  "filters": {
    "lifecycle_status": "deployed",
    "owner_dept": "IT"
  }
}
```

#### Error Response

```json
// 422 Unprocessable Entity
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Asset validation failed",
    "details": [
      {
        "field": "serial_number",
        "message": "Serial number already exists for this manufacturer"
      }
    ]
  }
}
```

### 4.3 Validation Rules

| Rule | Field(s) | Error Code | HTTP Status |
|------|----------|------------|-------------|
| Required fields | asset_tag, serial_number, name, model, manufacturer, owner_dept, location_id, lifecycle_status | MISSING_FIELD | 400 |
| Unique asset_tag | asset_tag | DUPLICATE_TAG | 409 |
| Unique serial+manufacturer | serial_number, manufacturer | DUPLICATE_SERIAL | 409 |
| Valid location_id | location_id | INVALID_LOCATION | 422 |
| Valid lifecycle_status | lifecycle_status | INVALID_STATUS | 422 |
| Warranty dates | warranty_start, warranty_end | INVALID_WARRANTY | 422 |
| Cost non-negative | purchase_cost | INVALID_COST | 422 |

### 4.4 FastAPI Implementation

```python
# api/asset_router.py

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from uuid import UUID

router = APIRouter(prefix="/api/v1/assets", tags=["assets"])

@router.post("/", status_code=201)
async def create_asset(
    asset: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new asset."""
    # Check permissions
    if not current_user.has_permission("asset.write"):
        raise HTTPException(status_code=403, detail="Insufficient permissions")

    # Validate
    errors = validate_asset(asset)
    if errors:
        raise HTTPException(status_code=422, detail=errors)

    # Check uniqueness
    existing = await db.execute(
        select(Asset).where(
            Asset.serial_number == asset.serial_number,
            Asset.manufacturer == asset.manufacturer
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Duplicate serial number")

    # Create
    db_asset = Asset(**asset.model_dump(), created_by=current_user.username)
    db.add(db_asset)
    await db.commit()

    # Audit trail
    await audit_log(db_asset.asset_id, "create", None, asset.model_dump(), current_user.username, "api")

    # Invalidate cache
    await redis.delete(f"asset:enrich:{db_asset.asset_id}")

    return db_asset

@router.get("/")
async def list_assets(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    lifecycle_status: Optional[str] = None,
    owner_dept: Optional[str] = None,
    location_id: Optional[UUID] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List assets with pagination and filters."""
    query = select(Asset)

    if lifecycle_status:
        query = query.where(Asset.lifecycle_status == lifecycle_status)
    if owner_dept:
        query = query.where(Asset.owner_dept == owner_dept)
    if location_id:
        query = query.where(Asset.location_id == location_id)
    if search:
        query = query.where(
            Asset.name.ilike(f"%{search}%") |
            Asset.serial_number.ilike(f"%{search}%") |
            Asset.asset_tag.ilike(f"%{search}%")
        )

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * limit).limit(limit)
    result = await db.execute(query)
    assets = result.scalars().all()

    return {
        "data": assets,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }
```

---

## 5. Bulk Import API

### 5.1 API Design

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|------------|-------------|
| POST | `/api/v1/assets/bulk` | RBAC: asset.write | 10/min | Bulk import (CSV/JSON) |
| GET | `/api/v1/assets/bulk/{job_id}` | RBAC: asset.read | 100/min | Check import status |

### 5.2 Import Flow

```
Upload File → Parse (CSV/JSON) → Validate Each Record → Upsert → Report Results
                                    │
                                    ├── Valid → Insert/Update
                                    └── Invalid → Error Report
```

### 5.3 Request/Response

```json
// POST /api/v1/assets/bulk
// Content-Type: multipart/form-data
// Body: file (CSV or JSON)

// Response (202 Accepted)
{
  "job_id": "770e8400-e29b-41d4-a716-446655440002",
  "status": "processing",
  "total_records": 500,
  "estimated_duration_seconds": 30
}

// GET /api/v1/assets/bulk/770e8400-...
// Response (200 OK)
{
  "job_id": "770e8400-...",
  "status": "completed",
  "total_records": 500,
  "processed": 500,
  "created": 450,
  "updated": 45,
  "errors": 5,
  "error_details": [
    {
      "row": 12,
      "serial_number": "SN-999",
      "error": "Missing required field: name"
    }
  ],
  "started_at": "2026-06-23T14:30:00.000Z",
  "completed_at": "2026-06-23T14:30:25.000Z",
  "duration_ms": 25000
}
```

### 5.4 CSV Format

```csv
asset_tag,serial_number,name,model,manufacturer,owner_dept,location_id,lifecycle_status
AST-001,SN-123,Dell R750,R750,Dell,IT,550e8400-...,deployed
AST-002,SN-456,Cisco 9300,C9300,Cisco,Network,550e8401-...,deployed
```

### 5.5 Idempotency

- Upsert key: `(serial_number, manufacturer)`
- If exists: update all fields
- If not exists: create new
- `asset_tag` uniqueness enforced, reject duplicate tags

### 5.6 Implementation

```python
# api/asset_bulk.py

import csv
import json
from typing import List
from fastapi import UploadFile, File, Depends

@router.post("/bulk", status_code=202)
async def bulk_import(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Bulk import assets from CSV or JSON."""

    # Read file
    content = await file.read()

    # Parse based on content type
    if file.filename.endswith('.csv'):
        records = parse_csv(content)
    elif file.filename.endswith('.json'):
        records = parse_json(content)
    else:
        raise HTTPException(400, "Unsupported file format. Use CSV or JSON.")

    # Create job
    job_id = str(uuid.uuid4())
    job = ImportJob(
        job_id=job_id,
        total_records=len(records),
        status="processing",
        started_at=datetime.utcnow()
    )
    db.add(job)
    await db.commit()

    # Process async
    asyncio.create_task(process_import(job_id, records, current_user.username))

    return {
        "job_id": job_id,
        "status": "processing",
        "total_records": len(records)
    }

async def process_import(job_id: str, records: List[dict], username: str):
    """Process import records."""
    created = updated = errors = 0

    for i, record in enumerate(records):
        try:
            # Validate
            errors_list = validate_asset_record(record)
            if errors_list:
                log_error(job_id, i, record, errors_list)
                errors += 1
                continue

            # Upsert
            existing = await find_existing(record)
            if existing:
                await update_asset(existing, record, username, "bulk_import")
                updated += 1
            else:
                await create_asset(record, username, "bulk_import")
                created += 1
        except Exception as e:
            log_error(job_id, i, record, [str(e)])
            errors += 1

    # Update job status
    await update_job(job_id, created, updated, errors)
```

---

## 6. Reconciliation Engine

### 6.1 Reconciliation Sources

| Source | Method | Frequency | Match Key |
|--------|--------|-----------|-----------|
| CMDB | Kafka consumer (dcim.cmdb.updates) | Real-time | serial_number + asset_tag |
| Discovery (NMS) | Scheduled scan | Daily | serial_number + IP |
| ERP (SAP/Oracle) | REST API | Weekly | serial_number + PO number |

### 6.2 Matching Logic

```
For each record from source:
  1. Exact match: serial_number + manufacturer → UPDATE
  2. Partial match: serial_number only → REVIEW (possible duplicate)
  3. Partial match: asset_tag only → REVIEW
  4. No match → CREATE (if source is trusted)
  5. Conflict → Resolution strategy
```

### 6.3 Conflict Resolution

| Scenario | Resolution | Action |
|----------|-----------|--------|
| Both sources have same field, different values | Newer timestamp wins | Auto-update |
| CMDB says deployed, Asset says in_storage | CMDB wins (operational) | Auto-update |
| Financial data conflict | Asset Repository wins (authoritative) | Auto-update |
| Manual override needed | Flag for review | Create ticket |

### 6.4 Implementation

```python
# services/asset_reconciliation.py

class AssetReconciliationEngine:
    def __init__(self, db, redis, kafka_producer):
        self.db = db
        self.redis = redis
        self.kafka = kafka_producer

    async def reconcile_cmdb(self, cmdb_records: List[dict]) -> ReconciliationResult:
        """Reconcile CMDB data with Asset Repository."""
        result = ReconciliationResult(source="cmdb")

        for record in cmdb_records:
            # Match by serial + manufacturer
            existing = await self._find_asset(
                serial_number=record["serial_number"],
                manufacturer=record.get("manufacturer")
            )

            if existing:
                # Check for conflicts
                conflicts = self._detect_conflicts(existing, record)

                if conflicts:
                    # Resolve conflicts
                    resolved = self._resolve_conflicts(existing, record, conflicts)
                    await self._update_asset(existing, resolved, source="cmdb_reconciliation")
                    result.updated += 1
                    result.conflicts += len(conflicts)
                else:
                    result.matched += 1
            else:
                # Create new asset from CMDB
                new_asset = self._transform_cmdb_to_asset(record)
                await self._create_asset(new_asset, source="cmdb_reconciliation")
                result.created += 1

        # Log reconciliation run
        await self._log_reconciliation(result)

        return result

    def _detect_conflicts(self, asset: Asset, cmdb_record: dict) -> List[Conflict]:
        """Detect conflicts between asset and CMDB record."""
        conflicts = []

        field_map = {
            "name": "ci_name",
            "location_id": "location_id",
            "lifecycle_status": "status",
            "owner_dept": "owner"
        }

        for asset_field, cmdb_field in field_map.items():
            asset_val = getattr(asset, asset_field)
            cmdb_val = cmdb_record.get(cmdb_field)

            if cmdb_val and asset_val != cmdb_val:
                conflicts.append(Conflict(
                    field=asset_field,
                    asset_value=asset_val,
                    source_value=cmdb_val,
                    source_timestamp=cmdb_record.get("updated_at")
                ))

        return conflicts

    def _resolve_conflicts(self, asset: Asset, record: dict, conflicts: List[Conflict]) -> dict:
        """Resolve conflicts using resolution strategy."""
        updates = {}

        for conflict in conflicts:
            if conflict.field == "lifecycle_status":
                # CMDB wins for operational status
                updates[conflict.field] = conflict.source_value
            elif conflict.field in ("book_value", "purchase_cost"):
                # Asset Repository wins for financial
                pass
            else:
                # Newer timestamp wins
                if conflict.source_timestamp > asset.updated_at:
                    updates[conflict.field] = conflict.source_value

        return updates
```

### 6.5 Reconciliation Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `asset_reconciliation_total_runs` | Counter | Total reconciliation runs |
| `asset_reconciliation_matched` | Counter | Records matched |
| `asset_reconciliation_created` | Counter | New assets created |
| `asset_reconciliation_updated` | Counter | Assets updated |
| `asset_reconciliation_conflicts` | Counter | Conflicts detected |
| `asset_reconciliation_duration_seconds` | Histogram | Run duration |

---

## 7. Audit Trail

### 7.1 Audit Events

| Event | Trigger | Data Captured |
|-------|---------|---------------|
| create | POST /assets | Full asset snapshot |
| update | PUT /assets/{id} | Changed fields only (old → new) |
| delete | DELETE /assets/{id} | Full asset snapshot |
| import | POST /assets/bulk | Import batch ID + records |
| reconcile | Reconciliation engine | Source + changes |

### 7.2 Audit Log Structure

```json
{
  "audit_id": "880e8400-...",
  "asset_id": "660e8400-...",
  "action": "update",
  "changes": [
    {
      "field": "lifecycle_status",
      "old_value": "received",
      "new_value": "deployed"
    },
    {
      "field": "location_id",
      "old_value": "550e8400-...",
      "new_value": "550e8401-..."
    }
  ],
  "changed_by": "admin@dcim.local",
  "changed_at": "2026-06-23T14:35:00.000Z",
  "source": "api",
  "ip_address": "10.70.0.50"
}
```

### 7.3 API Endpoint

```
GET /api/v1/assets/{id}/audit-trail?page=1&limit=50
GET /api/v1/assets/{id}/audit-trail?from=2026-06-01&to=2026-06-30
```

### 7.4 Immutability

- Audit log is append-only (no UPDATE, no DELETE)
- Partitioned by month for performance
- Retention: 7 years (compliance)
- Stored in separate table with no foreign key cascade

---

## 8. Enrichment API

### 8.1 Purpose

Read-optimized endpoint untuk CMDB dan Analytics. Returns asset data optimized for CI enrichment and analytics queries.

### 8.2 API Design

| Method | Endpoint | Auth | Cache | Description |
|--------|----------|------|-------|-------------|
| GET | `/api/v1/assets/enrich/{ci_id}` | RBAC: asset.read | 15 min | Enrich CI with asset data |
| GET | `/api/v1/assets/enrich/batch` | RBAC: asset.read | 15 min | Batch enrichment (max 100) |

### 8.3 Response Schema

```json
// GET /api/v1/assets/enrich/{ci_id}
// Response (200 OK)
{
  "ci_id": "CI-SERVER-001",
  "asset_id": "660e8400-...",
  "asset_tag": "AST-RACK-A1-001",
  "serial_number": "SN-12345678",
  "name": "Dell PowerEdge R750",
  "model": "R750",
  "manufacturer": "Dell",
  "owner_dept": "IT Infrastructure",
  "location": {
    "site_name": "DC-Jakarta",
    "building": "Building A",
    "floor": "3",
    "room": "Server Room 1",
    "rack": "Rack-A1",
    "position_u": "12-16"
  },
  "warranty_status": {
    "active": true,
    "start_date": "2026-01-15",
    "end_date": "2029-01-15",
    "days_remaining": 1056
  },
  "contract_status": {
    "has_contract": true,
    "contract_id": "...",
    "vendor": "Dell Technologies",
    "contract_type": "sla",
    "end_date": "2029-01-15"
  },
  "financial": {
    "purchase_cost": 15000.00,
    "book_value": 12000.00,
    "depreciation_method": "straight_line"
  },
  "lifecycle_status": "deployed",
  "enriched_at": "2026-06-23T14:30:00.000Z"
}
```

### 8.4 Cache Strategy

```python
# api/asset_enrichment.py

@router.get("/enrich/{ci_id}")
async def enrich_ci(
    ci_id: str,
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Enrich CI with asset data. Cached for 15 minutes."""

    cache_key = f"asset:enrich:{ci_id}"

    # Check cache
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # Query database (with joins)
    result = await db.execute("""
        SELECT a.*, l.*, f.*, c.*
        FROM asset a
        LEFT JOIN asset_location l ON a.location_id = l.location_id
        LEFT JOIN asset_financial f ON a.asset_id = f.asset_id
        LEFT JOIN asset_contract c ON a.contract_id = c.contract_id
        WHERE a.asset_id = (
            SELECT asset_id FROM cmdb_ci WHERE ci_id = :ci_id
        )
    """, {"ci_id": ci_id})

    asset = result.first()
    if not asset:
        raise HTTPException(404, "Asset not found for this CI")

    # Build response
    response = build_enrichment_response(asset)

    # Cache
    await redis.setex(cache_key, 900, json.dumps(response))  # 15 min

    return response
```

### 8.5 Batch Enrichment

```python
@router.get("/enrich/batch")
async def enrich_batch(
    ci_ids: List[str] = Query(..., max_length=100),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis)
):
    """Batch enrich CIs with asset data."""
    results = []

    for ci_id in ci_ids:
        cache_key = f"asset:enrich:{ci_id}"
        cached = await redis.get(cache_key)

        if cached:
            results.append({"ci_id": ci_id, "data": json.loads(cached), "cached": True})
        else:
            # Query and cache
            asset = await query_asset_by_ci(ci_id, db)
            if asset:
                response = build_enrichment_response(asset)
                await redis.setex(cache_key, 900, json.dumps(response))
                results.append({"ci_id": ci_id, "data": response, "cached": False})
            else:
                results.append({"ci_id": ci_id, "data": None, "error": "not_found"})

    return {"results": results}
```

---

## 9. Data Quality Framework

### 9.1 Quality Rules

| Rule | Field(s) | Type | Severity |
|------|----------|------|----------|
| Asset_ID uniqueness | asset_id | Uniqueness | Critical |
| Serial+Manufacturer uniqueness | serial_number, manufacturer | Uniqueness | Critical |
| Asset tag uniqueness | asset_tag | Uniqueness | Critical |
| Mandatory fields | asset_tag, serial_number, name, model, manufacturer, owner_dept, location_id, lifecycle_status | Completeness | Critical |
| Location exists | location_id | Referential | Critical |
| Contract exists | contract_id | Referential | High |
| Lifecycle status valid | lifecycle_status | Format | High |
| Warranty dates valid | warranty_start, warranty_end | Logical | Medium |
| Cost non-negative | purchase_cost | Range | Medium |
| Useful life valid | useful_life_years | Range | Medium |

### 9.2 Quality Scorecard

```sql
-- Asset data quality scorecard
CREATE VIEW asset_quality_scorecard AS
SELECT
    DATE(NOW()) as check_date,
    COUNT(*) as total_assets,

    -- Completeness
    ROUND(100.0 * COUNT(*) FILTER (WHERE name IS NOT NULL AND name != '') / COUNT(*), 2) as name_complete,
    ROUND(100.0 * COUNT(*) FILTER (WHERE serial_number IS NOT NULL) / COUNT(*), 2) as serial_complete,
    ROUND(100.0 * COUNT(*) FILTER (WHERE location_id IS NOT NULL) / COUNT(*), 2) as location_complete,
    ROUND(100.0 * COUNT(*) FILTER (WHERE owner_dept IS NOT NULL AND owner_dept != '') / COUNT(*), 2) as owner_complete,

    -- Uniqueness
    COUNT(*) - COUNT(DISTINCT serial_number || manufacturer) as duplicate_serials,
    COUNT(*) - COUNT(DISTINCT asset_tag) as duplicate_tags,

    -- Validity
    COUNT(*) FILTER (WHERE lifecycle_status NOT IN (
        'on_order', 'received', 'deployed', 'in_storage', 'maintenance', 'retired', 'disposed'
    )) as invalid_status,

    -- Warranty
    COUNT(*) FILTER (WHERE warranty_end IS NOT NULL AND warranty_end < NOW()) as warranty_expired,
    COUNT(*) FILTER (WHERE warranty_end IS NOT NULL AND warranty_end BETWEEN NOW() AND NOW() + INTERVAL '30 days') as warranty_expiring_soon

FROM asset
WHERE lifecycle_status != 'disposed';
```

---

## 10. Performance & Caching

### 10.1 Performance Targets

| Operation | Target p99 | Target p50 | Throughput |
|-----------|-----------|-----------|------------|
| GET /assets/{id} | < 50ms | < 10ms | 1000 req/s |
| GET /assets (list) | < 200ms | < 50ms | 100 req/s |
| POST /assets | < 100ms | < 20ms | 100 req/s |
| PUT /assets/{id} | < 100ms | < 20ms | 100 req/s |
| POST /assets/bulk | < 30s | < 10s | 10 req/min |
| GET /assets/enrich/{id} | < 50ms | < 5ms | 500 req/s |

### 10.2 Redis Cache Schema

```
Key Pattern                          TTL     Purpose
asset:enrich:{ci_id}                15 min  CI enrichment cache
asset:detail:{asset_id}             5 min   Asset detail cache
asset:search:{hash}                 5 min   Search result cache
asset:count:{filter_hash}           5 min   Count cache
```

### 10.3 Connection Pool

```python
# Database connection pool
DATABASE_POOL_SIZE = 20
DATABASE_MAX_OVERFLOW = 10
DATABASE_POOL_TIMEOUT = 30
DATABASE_POOL_RECYCLE = 1800

# Redis connection pool
REDIS_POOL_SIZE = 10
REDIS_MAX_CONNECTIONS = 50
```

---

## 11. Security

### 11.1 RBAC Matrix

| Role | Read | Write | Delete | Bulk Import | Admin | Audit View |
|------|------|-------|--------|-------------|-------|------------|
| viewer | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| operator | ✅ | ✅ | ❌ | ✅ | ❌ | Own |
| manager | ✅ | ✅ | ❌ | ✅ | ❌ | All |
| admin | ✅ | ✅ | ✅ | ✅ | ✅ | All |
| auditor | ✅ | ❌ | ❌ | ❌ | ❌ | All |

### 11.2 API Security

| Control | Implementation |
|---------|---------------|
| Authentication | JWT token (from Vault/OIDC) |
| Authorization | RBAC per endpoint |
| Rate limiting | Per-user, per-endpoint |
| Input validation | Pydantic models + JSON Schema |
| SQL injection | Parameterized queries (asyncpg) |
| Audit logging | Every API call logged |
| TLS | Enforced for all API traffic |

---

## 12. Monitoring & Alerting

### 12.1 Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `asset_total_count` | Gauge | Total assets in repository |
| `asset_by_status` | Gauge | Assets by lifecycle status |
| `asset_api_requests_total` | Counter | API requests by endpoint |
| `asset_api_latency_seconds` | Histogram | API response time |
| `asset_bulk_import_total` | Counter | Bulk import jobs |
| `asset_bulk_import_duration_seconds` | Histogram | Import duration |
| `asset_enrichment_cache_hit_ratio` | Gauge | Cache hit rate |
| `asset_reconciliation_runs_total` | Counter | Reconciliation runs |
| `asset_reconciliation_conflicts_total` | Counter | Conflicts detected |
| `asset_warranty_expiring_total` | Gauge | Warranties expiring in 30d |
| `asset_quality_score` | Gauge | Data quality score |

### 12.2 Alert Rules

```yaml
groups:
  - name: asset-repository
    rules:
      - alert: AssetAPILatencyHigh
        expr: histogram_quantile(0.99, rate(asset_api_latency_seconds_bucket[5m])) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Asset API p99 latency > 200ms"

      - alert: AssetBulkImportErrorsHigh
        expr: rate(asset_bulk_import_errors_total[1h]) > 5
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Bulk import error rate elevated"

      - alert: AssetWarrantyExpiring
        expr: asset_warranty_expiring_total > 10
        for: 1d
        labels:
          severity: info
        annotations:
          summary: "{{ $value }} asset warranties expiring in 30 days"

      - alert: AssetReconciliationConflicts
        expr: rate(asset_reconciliation_conflicts_total[24h]) > 20
        for: 24h
        labels:
          severity: warning
        annotations:
          summary: "High reconciliation conflict rate"

      - alert: AssetEnrichmentCacheHitLow
        expr: asset_enrichment_cache_hit_ratio < 0.8
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Enrichment cache hit ratio below 80%"
```

---

## 13. Acceptance Criteria — Block 3 Complete

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | Asset data model defined | JSON Schema + field specs | ⬜ |
| 2 | PostgreSQL schema created | Tables, indexes, triggers | ⬜ |
| 3 | CRUD API working | All 5 endpoints tested | ⬜ |
| 4 | Bulk import API working | CSV + JSON import tested | ⬜ |
| 5 | Reconciliation engine working | CMDB + discovery reconciliation | ⬜ |
| 6 | Audit trail logging | Every change captured | ⬜ |
| 7 | Enrichment API working | CI → Asset mapping + cache | ⬜ |
| 8 | Redis cache working | Cache hit ratio > 80% | ⬜ |
| 9 | Data quality rules enforced | Validation tests pass | ⬜ |
| 10 | RBAC enforced | Unauthorized access blocked | ⬜ |
| 11 | Performance targets met | p99 < 50ms (enrichment) | ⬜ |
| 12 | Integration tests pass | All test suites green | ⬜ |
| 13 | Monitoring dashboards | Grafana shows asset metrics | ⬜ |
| 14 | Alert rules active | Test alert fires | ⬜ |

---

## 15. NVR Integration Extensions

> **Full spec:** `nvr-asset-repository-integration.md`
> **Architecture diagram:** `diagrams/nvr-asset-repository-integration.html`

### 15.1 New Tables

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `asset_nvr` | NVR device metadata | storage_capacity_gb, channel_count, management_ip, sync_status |
| `asset_camera` | Camera-to-NVR mapping | nvr_asset_id, channel_number, resolution, location_verified |
| `camera_location_map` | Camera ↔ Location N:M | camera_asset_id, location_id, coverage_type |

### 15.2 Extended Tables

| Table | New Column | Type | Purpose |
|-------|-----------|------|---------|
| `asset` | `connector_type` | VARCHAR(30) | Enum includes 'nvr' |
| `asset_location` | `camera_verified` | BOOLEAN | Camera-validated location |
| `asset_location` | `camera_verified_at` | TIMESTAMPTZ | Last validation timestamp |

### 15.3 New API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/assets/nvr` | Register NVR device |
| GET | `/api/v1/assets/nvr` | List NVR devices |
| GET | `/api/v1/assets/nvr/{id}` | Get NVR with cameras |
| PUT | `/api/v1/assets/nvr/{id}/sync` | Trigger ONVIF sync |
| GET | `/api/v1/assets/cameras` | List all cameras |
| POST | `/api/v1/assets/location/{id}/verify` | Trigger location verification |

### 15.4 Location Validation Rules

| Rule | Condition | Action |
|------|-----------|--------|
| R1 | Location has ≥1 covering camera | Mark `camera_verified=true` |
| R2 | Camera offline >5h | Skip validation, alert |
| R3 | Camera sees unregistered device | Create investigation ticket |
| R4 | Asset moved without work order | Alert + create incident |

---

## 16. Gap Comparison Template

### Gap: [Component Name]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Data model | [spec fields] | [aktual fields] | [match/mismatch] | P1-P4 |
| Schema | [spec DDL] | [aktual DDL] | [gap detail] | P1-P4 |
| CRUD API | [spec endpoints] | [aktual endpoints] | [gap detail] | P1-P4 |
| Bulk import | [spec format] | [aktual format] | [gap detail] | P1-P4 |
| Reconciliation | [spec logic] | [aktual logic] | [gap detail] | P1-P4 |
| Audit trail | [spec events] | [aktual events] | [gap detail] | P1-P4 |
| Enrichment | [spec cache TTL] | [aktual cache TTL] | [gap detail] | P1-P4 |
| Data quality | [spec rules] | [aktual rules] | [gap detail] | P1-P4 |
| Security | [spec RBAC] | [aktual RBAC] | [gap detail] | P1-P4 |
| Performance | [spec targets] | [aktual metrics] | [gap detail] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

- [[asset-repository]]
- [[asset-data-model]]
- [[postgresql]] — primary database
- [[redis]] — cache layer
- [[cmdb]] — CI/asset reconciliation
- [[data-ingestion-integration]] — asset update events
- [[api-design-principles]]
- [[dcim-core-platform]]

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-23
> **Purpose:** Reference for team comparison → gap identification → connection dots
> **Block 1 Reference:** `block1-infrastructure-provisioning.md`
> **Block 2 Reference:** `block2-data-ingestion-integration.md`
