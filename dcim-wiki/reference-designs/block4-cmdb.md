---
title: "Block 4 — CMDB: Reference Design Spec"
created: 2026-06-23
updated: 2026-06-23
type: reference-design
block: 4
phase: 1
status: generated
confidence: high
tags: [cmdb, ci, relationships, topology, impact-analysis, reconciliation, service-mapping]
wiki_pages:
  - cmdb
  - asset-repository
  - data-ingestion-integration
  - postgresql
  - redis
  - cmdb-reconciliation-runbook
purpose: >
  Reference design spec untuk Block 4 CMDB.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Block 4 — CMDB: Reference Design Spec

> **Purpose:** Dokumen referensi lengkap untuk CMDB — SSOT Configuration Items dan relationships.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi aktual. Setiap gap dicatat sebagai connection point.
> **Architecture Diagram:** `diagrams/block4-cmdb-architecture.html` — buka di browser untuk visualisasi interaktif.
> **Depends on:** Block 1 (Infrastructure), Block 3 (Asset Repository)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [CI Data Model](#2-ci-data-model)
3. [Relationship Model](#3-relationship-model)
4. [PostgreSQL Schema](#4-postgresql-schema)
5. [CI CRUD API](#5-ci-crud-api)
6. [Relationship API](#6-relationship-api)
7. [Topology Engine](#7-topology-engine)
8. [Impact Analysis](#8-impact-analysis)
9. [Reconciliation Engine](#9-reconciliation-engine)
10. [Service Mapping](#10-service-mapping)
11. [Health Dashboard](#11-health-dashboard)
12. [Data Quality Framework](#12-data-quality-framework)
13. [Performance & Caching](#13-performance--caching)
14. [Security](#14-security)
15. [Monitoring & Alerting](#15-monitoring--alerting)
16. [Acceptance Criteria](#16-acceptance-criteria)
17. [Gap Comparison Template](#17-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                         CMDB                                    │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                     API Layer                             │  │
│  │  CI CRUD • Relationship • Topology • Impact • Health     │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐  │
│  │                  Service Layer                            │  │
│  │  Topology Engine • Impact Analysis • Reconciliation      │  │
│  │  Service Mapping • Data Quality • Audit Trail            │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐  │
│  │                  Data Layer                               │  │
│  │  PostgreSQL 16        Redis 7 (cache)                     │  │
│  │  ci, ci_attribute,    topology cache                      │  │
│  │  ci_relationship,     impact cache                        │  │
│  │  ci_lifecycle, ci_service                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                 │                │
         ▼                 ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │  Asset   │    │ Discovery│    │  DI&I        │
  │  Repository│  │  (NMS)   │    │  Gateway     │
  └──────────┘    └──────────┘    └──────────────┘
```

### 1.2 Data Flow

```
Data Sources → CMDB:
  1. DI&I Gateway (cmdb.updates topic) → Consumer → CI Create/Update
  2. Asset Reconciliation → Match CI ↔ Asset
  3. Discovery Reconciliation → Match CI ↔ Discovered
  4. Manual API → CRUD operations

Data Consumers → CMDB:
  1. Impact Analysis → "what breaks if this CI fails?"
  2. Topology Engine → Service dependency graphs
  3. Service Mapping → End-to-end service views
  4. Dashboard → CI health overview
```

### 1.3 Core Responsibilities

| Responsibility | Description | SLA |
|---------------|-------------|-----|
| CI Master Data | CRUD for all Configuration Items | 99.9% availability |
| Relationship Modeling | Containment, dependency, connectivity, impact | Real-time |
| Topology Engine | Graph-based relationship traversal | p99 < 200ms |
| Impact Analysis | "What breaks if this CI fails?" | p99 < 500ms |
| Reconciliation | CI ↔ Asset ↔ Discovery sync | Daily + hourly |
| Service Mapping | End-to-end service dependency view | p99 < 1s |
| Health Dashboard | CI health overview + data quality | Real-time |

---

## 2. CI Data Model

### 2.1 CI Types

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

### 2.2 Lifecycle States

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

### 2.3 Mandatory Fields per CI Type

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

---

## 3. Relationship Model

### 3.1 Relationship Types

| Type | Direction | Description | Example |
|------|-----------|-------------|---------|
| **contains** | parent → child | Physical containment | Rack contains Server |
| **depends_on** | source → target | Functional dependency | Service depends_on Application |
| **connected_to** | source → target | Network connectivity | Server connected_to Switch |
| **runs_on** | source → target | Execution dependency | Application runs_on Server |
| **part_of** | child → parent | Logical grouping | VM part_of Cluster |
| **managed_by** | ci → team | Ownership | Server managed_by Team |
| **impacts** | source → target | Impact relationship | Change on Server impacts Service |

### 3.2 Relationship Rules

| Rule | Description | Enforcement |
|------|-------------|-------------|
| No self-relationship | A CI cannot relate to itself | API validation |
| No cycles in containment | Containment must be DAG | Graph check |
| Max depth | Max 10 levels of containment | API validation |
| Bidirectional impact | impacts(A→B) implies B affected by A | Auto-create reverse |
| Orphan detection | CI without any relationship = warning | Health check |

### 3.3 Relationship Schema

```json
{
  "source_ci_id": "CI-SERVER-001",
  "target_ci_id": "CI-RACK-A1-01",
  "relationship_type": "contains",
  "metadata": {
    "created_at": "2026-06-23T14:30:00Z",
    "created_by": "admin",
    "confidence": "high",
    "source": "manual"
  }
}
```

---

## 4. PostgreSQL Schema

### 4.1 Tables

```sql
-- Migration 001: Create CMDB tables

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================
-- ci (Configuration Items)
-- ============================================
CREATE TABLE ci (
    ci_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ci_type VARCHAR(50) NOT NULL
        CHECK (ci_type IN (
            'server', 'network_device', 'storage', 'vm',
            'application', 'service', 'rack', 'patch_panel',
            'ups', 'pdu', 'other'
        )),
    name VARCHAR(255) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'planned'
        CHECK (status IN ('planned', 'active', 'maintenance', 'in_use', 'retired', 'disposed')),
    owner VARCHAR(100) NOT NULL,
    location_id UUID REFERENCES asset_location(location_id),
    serial_number VARCHAR(100),
    ip_address INET,
    os VARCHAR(100),
    vendor VARCHAR(100),
    model VARCHAR(100),
    description TEXT,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),
    updated_by VARCHAR(100),

    -- Data source
    data_source VARCHAR(50) DEFAULT 'manual'
        CHECK (data_source IN ('manual', 'discovery', 'api', 'reconciliation')),
    last_discovered_at TIMESTAMPTZ,

    -- Asset link
    asset_id UUID REFERENCES asset(asset_id),

    CONSTRAINT uq_ci_serial UNIQUE (serial_number) -- only if serial_number IS NOT NULL
);

-- Partial unique index for serial_number
CREATE UNIQUE INDEX uq_ci_serial_partial ON ci(serial_number) WHERE serial_number IS NOT NULL;

-- ============================================
-- ci_attribute (EAV pattern for custom attributes)
-- ============================================
CREATE TABLE ci_attribute (
    attribute_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ci_id UUID NOT NULL REFERENCES ci(ci_id) ON DELETE CASCADE,
    attr_name VARCHAR(100) NOT NULL,
    attr_value TEXT,
    attr_type VARCHAR(20) NOT NULL DEFAULT 'string'
        CHECK (attr_type IN ('string', 'integer', 'float', 'boolean', 'date', 'json')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_ci_attribute UNIQUE (ci_id, attr_name)
);

-- ============================================
-- ci_relationship
-- ============================================
CREATE TABLE ci_relationship (
    relationship_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_ci_id UUID NOT NULL REFERENCES ci(ci_id) ON DELETE CASCADE,
    target_ci_id UUID NOT NULL REFERENCES ci(ci_id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL
        CHECK (relationship_type IN (
            'contains', 'depends_on', 'connected_to',
            'runs_on', 'part_of', 'managed_by', 'impacts'
        )),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100),

    -- No self-relationship
    CONSTRAINT chk_no_self_rel CHECK (source_ci_id != target_ci_id),
    -- Unique relationship
    CONSTRAINT uq_relationship UNIQUE (source_ci_id, target_ci_id, relationship_type)
);

-- ============================================
-- ci_lifecycle (audit trail)
-- ============================================
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

-- ============================================
-- ci_service_mapping
-- ============================================
CREATE TABLE ci_service_mapping (
    mapping_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_ci_id UUID NOT NULL REFERENCES ci(ci_id) ON DELETE CASCADE,
    ci_id UUID NOT NULL REFERENCES ci(ci_id) ON DELETE CASCADE,
    tier INTEGER DEFAULT 1 CHECK (tier BETWEEN 1 AND 5),
    criticality VARCHAR(20) DEFAULT 'medium'
        CHECK (criticality IN ('critical', 'high', 'medium', 'low')),
    created_at TIMESTAMPTZ DEFAULT NOW(),

    CONSTRAINT uq_service_mapping UNIQUE (service_ci_id, ci_id)
);

-- ============================================
-- ci_reconciliation_log
-- ============================================
CREATE TABLE ci_reconciliation_log (
    reconciliation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_at TIMESTAMPTZ DEFAULT NOW(),
    source VARCHAR(50) NOT NULL,
    total_records INTEGER,
    matched INTEGER DEFAULT 0,
    created INTEGER DEFAULT 0,
    updated INTEGER DEFAULT 0,
    conflicts INTEGER DEFAULT 0,
    errors INTEGER DEFAULT 0,
    duration_ms INTEGER,
    status VARCHAR(20) DEFAULT 'running'
        CHECK (status IN ('running', 'completed', 'failed'))
);
```

### 4.2 Indexes

```sql
-- CI searches
CREATE INDEX idx_ci_type ON ci(ci_type);
CREATE INDEX idx_ci_status ON ci(status);
CREATE INDEX idx_ci_owner ON ci(owner);
CREATE INDEX idx_ci_location ON ci(location_id);
CREATE INDEX idx_ci_serial ON ci(serial_number) WHERE serial_number IS NOT NULL;
CREATE INDEX idx_ci_ip ON ci(ip_address) WHERE ip_address IS NOT NULL;
CREATE INDEX idx_ci_asset ON ci(asset_id) WHERE asset_id IS NOT NULL;
CREATE INDEX idx_ci_data_source ON ci(data_source);
CREATE INDEX idx_ci_last_discovered ON ci(last_discovered_at);

-- Composite indexes
CREATE INDEX idx_ci_type_status ON ci(ci_type, status);
CREATE INDEX idx_ci_type_owner ON ci(ci_type, owner);

-- Attribute searches
CREATE INDEX idx_attr_ci_id ON ci_attribute(ci_id);
CREATE INDEX idx_attr_name ON ci_attribute(attr_name);
CREATE INDEX idx_attr_name_value ON ci_attribute(attr_name, attr_value);

-- Relationship searches
CREATE INDEX idx_rel_source ON ci_relationship(source_ci_id);
CREATE INDEX idx_rel_target ON ci_relationship(target_ci_id);
CREATE INDEX idx_rel_type ON ci_relationship(relationship_type);
CREATE INDEX idx_rel_source_type ON ci_relationship(source_ci_id, relationship_type);
CREATE INDEX idx_rel_target_type ON ci_relationship(target_ci_id, relationship_type);

-- GIN index for metadata JSONB
CREATE INDEX idx_rel_metadata ON ci_relationship USING GIN (metadata);

-- Lifecycle
CREATE INDEX idx_lifecycle_ci ON ci_lifecycle(ci_id);
CREATE INDEX idx_lifecycle_changed_at ON ci_lifecycle(changed_at);
CREATE INDEX idx_lifecycle_status ON ci_lifecycle(new_status);

-- Service mapping
CREATE INDEX idx_svc_mapping_service ON ci_service_mapping(service_ci_id);
CREATE INDEX idx_svc_mapping_ci ON ci_service_mapping(ci_id);

-- Reconciliation
CREATE INDEX idx_recon_run_at ON ci_reconciliation_log(run_at);
CREATE INDEX idx_recon_source ON ci_reconciliation_log(source);
```

---

## 5. CI CRUD API

### 5.1 API Design

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/cmdb/ci` | ci.write | Create CI |
| GET | `/api/v1/cmdb/ci` | ci.read | List CIs (paginated, filterable) |
| GET | `/api/v1/cmdb/ci/{id}` | ci.read | Get CI by ID |
| PUT | `/api/v1/cmdb/ci/{id}` | ci.write | Update CI |
| DELETE | `/api/v1/cmdb/ci/{id}` | ci.admin | Soft delete CI |
| POST | `/api/v1/cmdb/ci/bulk` | ci.write | Bulk import CIs |
| GET | `/api/v1/cmdb/ci/search` | ci.read | Search CIs |

### 5.2 Request/Response Schemas

#### Create CI

```json
// POST /api/v1/cmdb/ci
{
  "ci_type": "server",
  "name": "web-server-01",
  "status": "active",
  "owner": "IT Infrastructure",
  "location_id": "550e8400-...",
  "serial_number": "SN-12345678",
  "ip_address": "10.70.1.100",
  "os": "Ubuntu 22.04 LTS",
  "vendor": "Dell",
  "model": "PowerEdge R750",
  "attributes": {
    "cpu": "Intel Xeon Gold 6338",
    "ram_gb": 128,
    "disk_gb": 2048,
    "rack_position": "U12-U16"
  }
}

// Response (201 Created)
{
  "ci_id": "CI-SERVER-001",
  "ci_type": "server",
  "name": "web-server-01",
  "status": "active",
  "created_at": "2026-06-23T14:30:00.000Z"
}
```

#### List CIs with Filters

```json
// GET /api/v1/cmdb/ci?ci_type=server&status=active&page=1&limit=20
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 245,
    "total_pages": 13
  },
  "filters": {
    "ci_type": "server",
    "status": "active"
  }
}
```

---

## 6. Relationship API

### 6.1 API Design

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/cmdb/ci/{id}/relationships` | ci.write | Create relationship |
| GET | `/api/v1/cmdb/ci/{id}/relationships` | ci.read | List CI relationships |
| GET | `/api/v1/cmdb/ci/{id}/relationships/{type}` | ci.read | List by type |
| DELETE | `/api/v1/cmdb/ci/{id}/relationships/{rel_id}` | ci.write | Delete relationship |

### 6.2 Response Schema

```json
// GET /api/v1/cmdb/ci/CI-SERVER-001/relationships
{
  "ci_id": "CI-SERVER-001",
  "relationships": [
    {
      "relationship_id": "...",
      "direction": "outbound",
      "type": "contains",
      "target_ci_id": "CI-DISK-001",
      "target_name": "disk-01",
      "target_type": "storage"
    },
    {
      "relationship_id": "...",
      "direction": "inbound",
      "type": "runs_on",
      "source_ci_id": "CI-APP-001",
      "source_name": "web-application",
      "source_type": "application"
    }
  ],
  "summary": {
    "total_outbound": 5,
    "total_inbound": 3,
    "by_type": {
      "contains": 3,
      "depends_on": 2,
      "runs_on": 2,
      "connected_to": 1
    }
  }
}
```

---

## 7. Topology Engine

### 7.1 Graph Model

```
CI Node:
  - ci_id
  - ci_type
  - name
  - status
  - weight (based on criticality)

Edge:
  - relationship_type
  - direction
  - weight (based on dependency strength)
```

### 7.2 Traversal Algorithms

| Algorithm | Use Case | Complexity |
|-----------|----------|------------|
| BFS | Direct dependencies (1-2 levels) | O(V + E) |
| DFS | Full dependency chain | O(V + E) |
| Dijkstra | Shortest dependency path | O((V + E) log V) |
| PageRank | CI criticality scoring | O(V * iterations) |

### 7.3 Topology API

```
GET /api/v1/cmdb/topology/{ci_id}?depth=3&type=depends_on
GET /api/v1/cmdb/topology/{ci_id}/upstream?depth=5
GET /api/v1/cmdb/topology/{ci_id}/downstream?depth=5
GET /api/v1/cmdb/topology/service/{service_ci_id}
```

### 7.4 Response Schema

```json
// GET /api/v1/cmdb/topology/CI-SERVER-001?depth=3
{
  "root": {
    "ci_id": "CI-SERVER-001",
    "ci_type": "server",
    "name": "web-server-01",
    "status": "active"
  },
  "nodes": [
    { "ci_id": "CI-APP-001", "ci_type": "application", "name": "web-app", "status": "active", "depth": 1 },
    { "ci_id": "CI-SERVICE-001", "ci_type": "service", "name": "email-service", "status": "active", "depth": 2 },
    { "ci_id": "CI-RACK-A1", "ci_type": "rack", "name": "Rack A1", "status": "active", "depth": 1 }
  ],
  "edges": [
    { "source": "CI-APP-001", "target": "CI-SERVER-001", "type": "runs_on" },
    { "source": "CI-SERVICE-001", "target": "CI-APP-001", "type": "depends_on" },
    { "source": "CI-SERVER-001", "target": "CI-RACK-A1", "type": "contains" }
  ],
  "depth": 3,
  "total_nodes": 4,
  "total_edges": 3
}
```

### 7.5 Cache Strategy

```python
# Topology results cached in Redis
# Key: topology:{ci_id}:{depth}:{relationship_type}
# TTL: 5 minutes
# Invalidate on: relationship create/delete
```

---

## 8. Impact Analysis

### 8.1 Impact Model

```
Impact Analysis Flow:
  1. Select CI to analyze (failure/change scenario)
  2. Traverse upstream dependencies (depends_on, runs_on)
  3. Traverse downstream impacts (impacts)
  4. Calculate impact score per affected CI
  5. Group by severity (critical, high, medium, low)
  6. Return impact report
```

### 8.2 Impact Scoring

| Factor | Weight | Calculation |
|--------|--------|-------------|
| CI Criticality | 40% | critical=10, high=7, medium=4, low=1 |
| Dependency Depth | 30% | Direct=10, 2-hop=7, 3-hop=4, 4+=1 |
| CI Type | 20% | service=10, application=8, server=6, other=4 |
| Relationship Type | 10% | depends_on=10, runs_on=8, connected_to=6, contains=4 |

### 8.3 Impact API

```
GET /api/v1/cmdb/impact/{ci_id}?scenario=failure
GET /api/v1/cmdb/impact/{ci_id}?scenario=change
GET /api/v1/cmdb/impact/{ci_id}?scenario=maintenance
```

### 8.4 Response Schema

```json
// GET /api/v1/cmdb/impact/CI-SERVER-001?scenario=failure
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
    },
    {
      "ci_id": "CI-SERVICE-001",
      "ci_type": "service",
      "name": "email-service",
      "impact_score": 7.5,
      "impact_level": "high",
      "reason": "depends_on application that runs_on failed CI",
      "depth": 2
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

---

## 9. Reconciliation Engine

### 9.1 Reconciliation Sources

| Source | Method | Frequency | Match Key |
|--------|--------|-----------|-----------|
| Asset Repository | Kafka consumer (asset.updates) | Daily | serial_number + asset_tag |
| Discovery (NMS) | Scheduled scan | Hourly | serial_number + IP |
| DI&I Gateway | Kafka consumer (cmdb.updates) | Real-time | serial_number |

### 9.2 Matching Logic

```
For each record from source:
  1. Exact match: serial_number → UPDATE CI
  2. IP match: ip_address → VERIFY (IP might be reassigned)
  3. Name match: name → REVIEW (possible rename)
  4. No match → CREATE (if trusted source)
  5. Conflict → Resolution strategy
```

### 9.3 Conflict Resolution

| Scenario | Resolution |
|----------|-----------|
| Asset says active, CMDB says maintenance | CMDB wins (operational truth) |
| Discovery found new device | Auto-create CI with status=active |
| Discovery shows device missing | Flag for review (don't auto-delete) |
| Asset and CMDB disagree on location | Newer timestamp wins |

### 9.4 Implementation

```python
# services/cmdb_reconciliation.py

class CMDBReconciliationEngine:
    def __init__(self, db, redis, kafka_producer):
        self.db = db
        self.redis = redis
        self.kafka = kafka_producer

    async def reconcile_asset(self, asset_records: List[dict]) -> ReconciliationResult:
        """Reconcile Asset Repository with CMDB."""
        result = ReconciliationResult(source="asset")

        for record in asset_records:
            # Match by serial_number
            existing = await self._find_ci(serial_number=record["serial_number"])

            if existing:
                # Update CI with asset data
                updates = self._compute_updates(existing, record)
                if updates:
                    await self._update_ci(existing, updates, source="asset_reconciliation")
                    result.updated += 1
                else:
                    result.matched += 1
            else:
                # Create new CI from asset
                new_ci = self._transform_asset_to_ci(record)
                await self._create_ci(new_ci, source="asset_reconciliation")
                result.created += 1

        # Update asset_id links
        await self._link_asset_ids()

        return result

    async def reconcile_discovery(self, discovery_records: List[dict]) -> ReconciliationResult:
        """Reconcile Discovery data with CMDB."""
        result = ReconciliationResult(source="discovery")

        for record in discovery_records:
            # Match by serial_number first, then IP
            existing = await self._find_ci(
                serial_number=record.get("serial_number"),
                ip_address=record.get("ip_address")
            )

            if existing:
                # Update discovery timestamp
                await self._update_last_discovered(existing.ci_id)
                result.matched += 1
            else:
                # Auto-create from discovery
                new_ci = self._transform_discovery_to_ci(record)
                await self._create_ci(new_ci, source="discovery")
                result.created += 1

        return result
```

---

## 10. Service Mapping

### 10.1 Service Model

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

### 10.2 Service Health

```json
// GET /api/v1/cmdb/services/CI-SERVICE-001/mapping
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
    "by_type": {
      "application": 2,
      "server": 3,
      "storage": 2,
      "network_device": 1
    },
    "critical_path": [
      "CI-SERVICE-001",
      "CI-APP-EMAIL",
      "CI-SERVER-EMAIL-01",
      "CI-SAN-01"
    ]
  },
  "health_summary": {
    "total": 8,
    "healthy": 6,
    "degraded": 1,
    "critical": 1,
    "health_score": 75.0
  },
  "dependency_tiers": [
    { "tier": 1, "cis": ["CI-APP-EMAIL"], "criticality": "critical" },
    { "tier": 2, "cis": ["CI-SERVER-EMAIL-01", "CI-SERVER-EMAIL-02"], "criticality": "high" },
    { "tier": 3, "cis": ["CI-SAN-01", "CI-SW-FLOOR3"], "criticality": "medium" }
  ]
}
```

### 10.3 Service Dependency Graph

```
┌─────────────────────────────────────────────────────────────────┐
│                    Service: email-service                        │
│                    Criticality: CRITICAL                         │
│                    Health Score: 75/100                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Tier 1 (Critical):                                             │
│  ┌──────────────┐                                               │
│  │ email-app    │ ← depends_on                                   │
│  │ [Application]│                                               │
│  └──────┬───────┘                                               │
│         │ runs_on                                                │
│  Tier 2 (High):                                                 │
│  ┌──────────────┐    ┌──────────────┐                           │
│  │ email-srv-01 │    │ email-srv-02 │                           │
│  │ [Server] ✓   │    │ [Server] ⚠️  │ ← degraded                │
│  └──────┬───────┘    └──────┬───────┘                           │
│         │ contains          │ contains                           │
│  Tier 3 (Medium):                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ SAN-01       │    │ SAN-02       │    │ Switch-F3    │      │
│  │ [Storage] ✓  │    │ [Storage] ✓  │    │ [Network] ✓  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 11. Health Dashboard

### 11.1 API Design

```
GET /api/v1/cmdb/health
GET /api/v1/cmdb/health/summary
GET /api/v1/cmdb/health/quality
```

### 11.2 Response Schema

```json
// GET /api/v1/cmdb/health
{
  "timestamp": "2026-06-23T14:30:00.000Z",
  "summary": {
    "total_cis": 1247,
    "by_type": {
      "server": 342,
      "network_device": 156,
      "storage": 89,
      "vm": 445,
      "application": 120,
      "service": 45,
      "other": 50
    },
    "by_status": {
      "active": 980,
      "planned": 45,
      "maintenance": 120,
      "in_use": 50,
      "retired": 32,
      "disposed": 20
    }
  },
  "data_quality": {
    "completeness_score": 92.5,
    "mandatory_fields_complete": 95.0,
    "serial_number_coverage": 88.0,
    "location_coverage": 90.0,
    "orphan_cis": 15,
    "duplicate_suspects": 3
  },
  "reconciliation": {
    "last_asset_run": "2026-06-23T02:00:00Z",
    "last_discovery_run": "2026-06-23T14:00:00Z",
    "asset_match_rate": 95.0,
    "discovery_match_rate": 88.0,
    "pending_conflicts": 2
  },
  "relationships": {
    "total_relationships": 3450,
    "by_type": {
      "contains": 1200,
      "depends_on": 890,
      "connected_to": 650,
      "runs_on": 420,
      "impacts": 290
    },
    "orphan_cis_no_relationship": 15
  }
}
```

---

## 12. Data Quality Framework

### 12.1 Quality Rules

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

### 12.2 Quality Scorecard

```sql
-- CMDB data quality scorecard
CREATE VIEW cmdb_quality_scorecard AS
SELECT
    DATE(NOW()) as check_date,
    COUNT(*) as total_cis,

    -- Completeness
    ROUND(100.0 * COUNT(*) FILTER (WHERE name IS NOT NULL AND name != '') / COUNT(*), 2) as name_complete,
    ROUND(100.0 * COUNT(*) FILTER (WHERE owner IS NOT NULL AND owner != '') / COUNT(*), 2) as owner_complete,
    ROUND(100.0 * COUNT(*) FILTER (WHERE location_id IS NOT NULL) / COUNT(*), 2) as location_complete,
    ROUND(100.0 * COUNT(*) FILTER (WHERE serial_number IS NOT NULL AND ci_type IN ('server', 'storage')) /
        COUNT(*) FILTER (WHERE ci_type IN ('server', 'storage')), 2) as serial_coverage,

    -- Relationships
    (SELECT COUNT(*) FROM ci WHERE ci_id NOT IN (SELECT source_ci_id FROM ci_relationship)
        AND ci_id NOT IN (SELECT target_ci_id FROM ci_relationship)) as orphan_cis,

    -- Lifecycle
    COUNT(*) FILTER (WHERE status = 'active') as active_cis,
    COUNT(*) FILTER (WHERE status = 'retired' AND updated_at < NOW() - INTERVAL '1 year') as stale_retired

FROM ci;
```

---

## 13. Performance & Caching

### 13.1 Performance Targets

| Operation | Target p99 | Target p50 | Throughput |
|-----------|-----------|-----------|------------|
| GET /cmdb/ci/{id} | < 50ms | < 10ms | 1000 req/s |
| GET /cmdb/ci (list) | < 200ms | < 50ms | 100 req/s |
| POST /cmdb/ci | < 100ms | < 20ms | 100 req/s |
| GET /cmdb/topology/{id} | < 200ms | < 50ms | 200 req/s |
| GET /cmdb/impact/{id} | < 500ms | < 100ms | 50 req/s |
| GET /cmdb/health | < 1s | < 200ms | 10 req/s |
| GET /cmdb/services/{id}/mapping | < 1s | < 200ms | 20 req/s |

### 13.2 Redis Cache

```
Key Pattern                           TTL     Purpose
ci:detail:{ci_id}                    5 min   CI detail cache
ci:relationships:{ci_id}             5 min   Relationship cache
ci:topology:{ci_id}:{depth}          5 min   Topology cache
ci:impact:{ci_id}:{scenario}         5 min   Impact analysis cache
ci:health:summary                    5 min   Health summary cache
ci:search:{hash}                     5 min   Search result cache
```

### 13.3 Graph Performance

| Optimization | Description |
|-------------|-------------|
| Adjacency list | PostgreSQL adjacency list for graph queries |
| Recursive CTE | Recursive CTE for traversal |
| Materialized view | Pre-computed service dependency graphs |
| Redis graph cache | Cache frequent topology queries |
| Batch loading | Batch load relationships for bulk operations |

---

## 14. Security

### 14.1 RBAC Matrix

| Role | CI Read | CI Write | CI Delete | Relationship | Topology | Impact | Health |
|------|---------|----------|-----------|--------------|----------|--------|--------|
| viewer | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| operator | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| manager | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ |
| admin | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| auditor | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |

---

## 15. Monitoring & Alerting

### 15.1 Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `cmdb_total_cis` | Gauge | Total CIs in CMDB |
| `cmdb_cis_by_type` | Gauge | CIs by type |
| `cmdb_cis_by_status` | Gauge | CIs by status |
| `cmdb_api_requests_total` | Counter | API requests |
| `cmdb_api_latency_seconds` | Histogram | API latency |
| `cmdb_relationships_total` | Gauge | Total relationships |
| `cmdb_topology_queries_total` | Counter | Topology queries |
| `cmdb_impact_queries_total` | Counter | Impact queries |
| `cmdb_reconciliation_runs_total` | Counter | Reconciliation runs |
| `cmdb_reconciliation_conflicts_total` | Counter | Conflicts |
| `cmdb_data_quality_score` | Gauge | Data quality score |
| `cmdb_orphan_cis_total` | Gauge | CIs without relationships |

### 15.2 Alert Rules

```yaml
groups:
  - name: cmdb
    rules:
      - alert: CMDBAPILatencyHigh
        expr: histogram_quantile(0.99, rate(cmdb_api_latency_seconds_bucket[5m])) > 0.5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "CMDB API p99 latency > 500ms"

      - alert: CMDBDataQualityLow
        expr: cmdb_data_quality_score < 80
        for: 1d
        labels:
          severity: warning
        annotations:
          summary: "CMDB data quality score below 80%"

      - alert: CMDBOrphanCIsHigh
        expr: cmdb_orphan_cis_total > 50
        for: 7d
        labels:
          severity: warning
        annotations:
          summary: "{{ $value }} CIs without relationships"

      - alert: CMDBReconciliationConflicts
        expr: rate(cmdb_reconciliation_conflicts_total[24h]) > 20
        for: 24h
        labels:
          severity: warning
        annotations:
          summary: "High reconciliation conflict rate"

      - alert: CMDBDiscoveryStale
        expr: time() - cmdb_last_discovery_timestamp > 7200
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Discovery data older than 2 hours"
```

---

## 16. Acceptance Criteria — Block 4 Complete

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | CI data model defined | JSON Schema + field specs | ⬜ |
| 2 | CI type taxonomy complete | 10+ CI types defined | ⬜ |
| 3 | Relationship model complete | 7 relationship types | ⬜ |
| 4 | PostgreSQL schema created | Tables, indexes, constraints | ⬜ |
| 5 | CI CRUD API working | All 7 endpoints tested | ⬜ |
| 6 | Relationship API working | Create/read/delete relationships | ⬜ |
| 7 | Topology engine working | Graph traversal returns correct results | ⬜ |
| 8 | Impact analysis working | "What breaks if this CI fails?" works | ⬜ |
| 9 | Asset reconciliation working | CI ↔ Asset sync tested | ⬜ |
| 10 | Discovery reconciliation working | CI ↔ Discovery sync tested | ⬜ |
| 11 | Service mapping working | End-to-end service view | ⬜ |
| 12 | Health dashboard working | CI counts, quality metrics | ⬜ |
| 13 | Data quality rules enforced | Validation tests pass | ⬜ |
| 14 | Redis cache working | Topology/impact cached | ⬜ |
| 15 | RBAC enforced | Unauthorized access blocked | ⬜ |
| 16 | Performance targets met | p99 < 500ms (impact) | ⬜ |
| 17 | Monitoring dashboards | Grafana shows CMDB metrics | ⬜ |
| 18 | Alert rules active | Test alert fires | ⬜ |

---

## 17. Gap Comparison Template

### Gap: [Component Name]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| CI model | [spec fields] | [aktual fields] | [match/mismatch] | P1-P4 |
| CI types | [spec types] | [aktual types] | [gap detail] | P1-P4 |
| Relationships | [spec types] | [aktual types] | [gap detail] | P1-P4 |
| Schema | [spec DDL] | [aktual DDL] | [gap detail] | P1-P4 |
| CRUD API | [spec endpoints] | [aktual endpoints] | [gap detail] | P1-P4 |
| Topology | [spec algorithm] | [aktual algorithm] | [gap detail] | P1-P4 |
| Impact analysis | [spec scoring] | [aktual scoring] | [gap detail] | P1-P4 |
| Reconciliation | [spec logic] | [aktual logic] | [gap detail] | P1-P4 |
| Service mapping | [spec tiers] | [aktual tiers] | [gap detail] | P1-P4 |
| Data quality | [spec rules] | [aktual rules] | [gap detail] | P1-P4 |
| Security | [spec RBAC] | [aktual RBAC] | [gap detail] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

- [[cmdb]]
- [[asset-repository]] — CI/asset reconciliation
- [[data-ingestion-integration]] — CI update events
- [[postgresql]] — primary database
- [[redis]] — cache layer
- [[cmdb-reconciliation-runbook]]
- [[dcim-core-platform]]

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-23
> **Purpose:** Reference for team comparison → gap identification → connection dots
> **Phase 1 Complete:** All 4 blocks reference designs generated
> **Block References:** B1 (Infra), B2 (DI&I), B3 (Asset), B4 (CMDB)
