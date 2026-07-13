---
title: "Block 3 — Asset Repository: Technical Requirements"
created: 2026-06-25
updated: 2026-06-25
type: technical-requirements
block: 3
phase: 1
status: generated
confidence: high
tags: [asset-repository, technical-requirements, crud, bulk-import, reconciliation, audit-trail, enrichment, nvr, camera, location-validation]
reference_design: block3-asset-repository.md
purpose: >
  Technical Requirements document untuk Block 3 Asset Repository.
  Mendefinisikan semua functional, non-functional, integration, security,
  dan observability requirements yang HARUS dipenuhi.
  Tim development gunakan sebagai contract specification.
---

# Block 3 — Asset Repository: Technical Requirements

> **Purpose:** Dokumen technical requirements lengkap untuk Asset Repository — SSOT aset fisik, finansial, dan kontrak.
> **Reference Design:** `~/dcim-wiki/reference-designs/block3-asset-repository.md`
> **Architecture Diagram:** `diagrams/block3-asset-repository-architecture.html`
> **Depends on:** Block 1 (Infrastructure Provisioning)

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Requirements](#2-system-requirements)
3. [Functional Requirements](#3-functional-requirements)
4. [Non-Functional Requirements](#4-non-functional-requirements)
5. [Data Requirements](#5-data-requirements)
6. [API Requirements](#6-api-requirements)
7. [Integration Requirements](#7-integration-requirements)
8. [Security Requirements](#8-security-requirements)
9. [Observability Requirements](#9-observability-requirements)
10. [Acceptance Criteria](#10-acceptance-criteria)
11. [Risk & Mitigation](#11-risk--mitigation)
12. [Open Questions](#12-open-questions)

---

## 1. Executive Summary

### 1.1 Objective

Membangun **Asset Repository** yang menjadi Single Source of Truth (SSOT) untuk semua aset fisik, finansial, dan kontrak di seluruh data center. Repository ini melayani kebutuhan CMDB, Analytics, DI&I Gateway, dan operasional NOC/SOC.

### 1.2 Scope

| In Scope | Out of Scope |
|----------|--------------|
| Asset CRUD operations | CI management (handled by CMDB Block 4) |
| Bulk import (CSV/JSON) | Real-time discovery (handled by DI&I Block 2) |
| Reconciliation engine | Financial depreciation scheduling |
| Audit trail (immutable) | User management (handled by IAM) |
| Enrichment API (Redis cache) | Asset procurement workflow |
| NVR/Camera integration | Contract negotiation workflow |
| Location tracking (building → rack → U) | Physical asset movement (handled by workflow) |

### 1.3 Actors / Source Systems

| Actor | Role | Interaction |
|-------|------|-------------|
| NOC Operators | Read asset status, location, health | Enrichment API |
| SOC Analysts | Correlate security events with assets | Enrichment API |
| Facilities Team | Track physical location, rack utilization | CRUD API |
| Finance Team | Asset value, depreciation tracking | CRUD API |
| IT Operations | Asset lifecycle management | CRUD API + Bulk Import |
| DI&I Gateway | Automated asset updates from discovery | Kafka consumer |
| CMDB | CI ↔ Asset relationship mapping | Enrichment API |
| Analytics Engine | Asset metrics, capacity planning | Enrichment API |
| External Systems | ERP, ITSM asset sync | REST API adapters |

---

## 2. System Requirements

### 2.1 Infrastructure Requirements

| Component | Minimum Spec | Recommended | HA Requirement |
|-----------|-------------|-------------|----------------|
| PostgreSQL | v16, 4 vCPU, 16GB RAM, 200GB SSD | 8 vCPU, 32GB RAM, 500GB SSD | Primary-Replica (1 primary, 2 replicas) |
| Redis | v7, 2 vCPU, 8GB RAM | 4 vCPU, 16GB RAM | Sentinel (3 nodes) or Cluster |
| API Server | 2 vCPU, 4GB RAM | 4 vCPU, 8GB RAM | 2+ instances behind LB |
| Kafka Consumer | 2 vCPU, 4GB RAM | 4 vCPU, 8GB RAM | Consumer group (2+ instances) |

### 2.2 Database Requirements

| Requirement | Specification |
|-------------|--------------|
| ACID Compliance | Full transactional support |
| Concurrent Connections | Max 200 connections (connection pooling via PgBouncer) |
| Backup Strategy | Full daily, WAL archiving every 5 min, PITR enabled |
| RTO | ≤ 15 minutes |
| RPO | ≤ 5 minutes (WAL-based) |
| Encryption at Rest | AES-256 (PostgreSQL TDE or disk-level) |
| Encryption in Transit | TLS 1.2+ for all connections |

---

## 3. Functional Requirements

### 3.1 Asset CRUD Operations

#### FR-ASSET-001: Create Asset
- **Priority:** P1 Critical
- **Description:** System SHALL accept asset creation via REST API with full validation
- **Input:** Asset JSON payload (see Reference Design Section 4.2)
- **Validation:**
  - `asset_tag` must be unique
  - `serial_number` + `manufacturer` combination must be unique
  - `location_id` must reference valid `asset_location`
  - `lifecycle_status` must be valid enum value
  - All required fields must be present
- **Output:** Created asset with auto-generated `asset_id`, `created_at`, `created_by`
- **Side Effects:**
  - Write to `asset_audit_log` (action: create)
  - Invalidate Redis cache for affected queries
  - Publish event to Kafka topic `asset.events` (optional, for CMDB sync)

#### FR-ASSET-002: Read Asset
- **Priority:** P1 Critical
- **Description:** System SHALL retrieve asset by ID or search with filters
- **Operations:**
  - GET by `asset_id` → single asset with location, financial, contract data
  - GET list with filters: `manufacturer`, `model`, `owner_dept`, `location_id`, `lifecycle_status`, `warranty_end` range
  - Pagination: `page`, `page_size` (max 100)
  - Sorting: `created_at`, `updated_at`, `purchase_date`, `warranty_end`
- **Response Time:** p99 < 50ms (cached), p99 < 200ms (uncached)

#### FR-ASSET-003: Update Asset
- **Priority:** P1 Critical
- **Description:** System SHALL update asset fields with audit logging
- **Behavior:**
  - Partial updates allowed (PATCH semantics)
  - Full field-level audit logging (old_value → new_value)
  - Optimistic locking via `updated_at` timestamp
  - Redis cache invalidation on update
- **Validation:** Same as create, but uniqueness checks exclude current record

#### FR-ASSET-004: Soft Delete Asset
- **Priority:** P2 High
- **Description:** System SHALL soft-delete assets (set `lifecycle_status = 'disposed'`)
- **Hard Delete:** Forbidden for assets with financial records or active contracts
- **Cascade:** Soft delete does NOT cascade to location or contract records

### 3.2 Bulk Import

#### FR-IMPORT-001: CSV/JSON Import
- **Priority:** P1 Critical
- **Description:** System SHALL accept bulk asset import via CSV or JSON file
- **File Limits:** Max 10,000 records per file, max 50MB file size
- **Processing:**
  - Async processing with job tracking
  - Row-level validation (skip invalid rows, continue processing)
  - Upsert semantics: match by `asset_tag` or `serial_number` + `manufacturer`
  - Progress reporting via polling endpoint
- **Output:** Import summary (total, created, updated, skipped, errors)

#### FR-IMPORT-002: Import Validation
- **Priority:** P1 Critical
- **Description:** System SHALL validate each row against field specifications
- **Validation Rules:** See Reference Design Section 2.3
- **Error Handling:**
  - Return row-level errors with field name, error type, and original value
  - Store errors in `import_error_log` for review
  - Allow re-import of corrected rows

### 3.3 Reconciliation Engine

#### FR-RECON-001: CMDB Reconciliation
- **Priority:** P1 Critical
- **Description:** System SHALL reconcile assets with CMDB CIs
- **Matching Logic:**
  - Primary: `serial_number` + `manufacturer`
  - Secondary: `asset_tag` ↔ CI `name` or `asset_tag` attribute
  - Tertiary: `name` + `model` + `location` fuzzy match
- **Conflict Resolution:**
  - Asset Repository is SSOT for: financial, warranty, contract, location
  - CMDB is SSOT for: CI relationships, service mapping
  - Conflicts logged in `reconciliation_conflict` table for manual review

#### FR-RECON-002: Discovery Reconciliation
- **Priority:** P1 Critical
- **Description:** System SHALL reconcile assets with DI&I discovery data
- **Triggers:** Scheduled (daily) or on-demand via API
- **Output:** `asset_reconciliation_log` entry with match/create/update/conflict counts

### 3.4 Audit Trail

#### FR-AUDIT-001: Immutable Audit Log
- **Priority:** P1 Critical
- **Description:** System SHALL log all asset changes to immutable audit table
- **Fields Logged:**
  - `asset_id`, `action` (create/update/delete/import/reconcile)
  - `field_name`, `old_value`, `new_value`
  - `changed_by`, `changed_at`, `source`, `ip_address`
- **Partitioning:** Monthly by `changed_at`
- **Retention:** Minimum 7 years (configurable)
- **Immutability:** No UPDATE or DELETE allowed on audit table (enforced via PostgreSQL row-level security)

### 3.5 Enrichment API

#### FR-ENRICH-001: Asset Enrichment
- **Priority:** P1 Critical
- **Description:** System SHALL provide read-optimized API for CMDB and Analytics
- **Endpoints:**
  - `GET /api/v1/enrich/asset/{asset_id}` → full asset profile
  - `GET /api/v1/enrich/asset/serial/{serial_number}` → lookup by serial
  - `GET /api/v1/enrich/asset/tag/{asset_tag}` → lookup by tag
  - `GET /api/v1/enrich/assets/batch` → batch lookup (max 100 IDs)
- **Caching:** Redis with 5-minute TTL, invalidated on asset update
- **Response Time:** p99 < 50ms

### 3.6 NVR/Camera Integration

#### FR-NVR-001: NVR Asset Management
- **Priority:** P2 High
- **Description:** System SHALL manage NVR and camera assets with location mapping
- **Tables:** `asset_nvr`, `asset_camera`, `camera_location_map`
- **API:** Dedicated endpoints for NVR/Camera CRUD and location mapping
- **Kafka Topics:** `dcim.nvr.*` (5 topics for NVR events)

### 3.7 Location Management

#### FR-LOC-001: Location CRUD
- **Priority:** P1 Critical
- **Description:** System SHALL manage location hierarchy: site → building → floor → room → rack → U position
- **Constraint:** Unique `(room, rack, position_u)` combination
- **Cascade:** Soft delete location only if no assets reference it

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Metric | Target | Measurement |
|--------|--------|-------------|
| API Response Time (read) | p99 < 50ms (cached), p99 < 200ms (uncached) | Application logs + Prometheus |
| API Response Time (write) | p99 < 500ms | Application logs + Prometheus |
| Bulk Import Throughput | ≥ 1,000 records/second | Import job metrics |
| Reconciliation Throughput | ≥ 5,000 records/minute | Reconciliation job metrics |
| Concurrent Users | ≥ 100 simultaneous API users | Connection pooling metrics |
| Database Query Time | p99 < 100ms for indexed queries | pg_stat_statements |

### 4.2 Scalability

| Dimension | Current | Growth Target | Strategy |
|-----------|---------|---------------|----------|
| Asset Records | 50,000 | 500,000 | Table partitioning, read replicas |
| Audit Records | 10,000/month | 100,000/month | Monthly partitioning, archival |
| API Requests | 1,000/min | 10,000/min | Horizontal scaling, caching |
| Bulk Import Jobs | 10/day | 100/day | Async processing, queue management |

### 4.3 Availability

| Requirement | Target | Implementation |
|-------------|--------|----------------|
| System Uptime | 99.9% (8.76 hours downtime/year) | HA deployment, auto-failover |
| Database HA | Automatic failover ≤ 30s | PostgreSQL streaming replication + Patroni |
| Redis HA | Automatic failover ≤ 10s | Redis Sentinel (3 nodes) |
| API HA | Zero-downtime deployments | Rolling updates behind load balancer |
| Backup Frequency | Daily full, hourly WAL | pg_basebackup + WAL archiving |
| DR Strategy | Cross-region replication | Async replication to secondary DC |

### 4.4 Reliability

| Requirement | Specification |
|-------------|--------------|
| Idempotency | All write operations idempotent via `asset_tag` or `serial_number` + `manufacturer` |
| Retry Policy | Exponential backoff: 1s, 2s, 4s, 8s, 16s (max 5 retries) |
| DLQ | Failed imports/reconciliation routed to Dead Letter Queue |
| Data Integrity | Foreign key constraints, check constraints, unique constraints enforced |
| Graceful Degradation | Cache miss → direct DB query; DB read replica down → primary fallback |

### 4.5 Maintainability

| Requirement | Specification |
|-------------|--------------|
| Code Coverage | ≥ 80% unit tests, ≥ 60% integration tests |
| Documentation | API docs (OpenAPI 3.0), runbooks, architecture decision records |
| Migration Strategy | Versioned SQL migrations (Flyway or Alembic) |
| Configuration | Environment-based config (12-factor app), no hardcoded values |
| Logging | Structured JSON logs, correlation IDs for request tracing |

---

## 5. Data Requirements

### 5.1 Data Quality Rules

| Rule Type | Specification | Enforcement |
|-----------|--------------|-------------|
| Mandatory Fields | `asset_id`, `asset_tag`, `serial_number`, `name`, `model`, `manufacturer`, `owner_dept`, `location_id`, `lifecycle_status` | DB NOT NULL + API validation |
| Uniqueness | `asset_tag` (global), `serial_number` + `manufacturer` (composite) | DB UNIQUE + API validation |
| Referential Integrity | `location_id` → `asset_location`, `contract_id` → `asset_contract` | DB FK constraints |
| Format Validation | `asset_tag`: alphanumeric + dash; `serial_number`: no special chars | Regex in API validation |
| Range Validation | `purchase_cost` ≥ 0, `useful_life_years` 1-30, `book_value` ≥ 0 | DB CHECK constraints |
| Date Logic | `warranty_end` ≥ `warranty_start`, `end_date` ≥ `start_date` | DB CHECK constraints |

### 5.2 Data Lineage

| Source | Data Flow | Destination |
|--------|-----------|-------------|
| CSV/JSON Import | API → Validation → Upsert | PostgreSQL |
| DI&I Gateway | Kafka → Consumer → Validate → Upsert | PostgreSQL |
| CMDB Reconciliation | Scheduled job → Match → Update | PostgreSQL |
| Manual API | REST → Validate → Write | PostgreSQL |

### 5.3 Data Retention

| Data Type | Retention | Archival Strategy |
|-----------|-----------|-------------------|
| Asset Records | Indefinite (lifecycle tracking) | None (active data) |
| Audit Logs | 7 years minimum | Monthly partitioning, cold storage archival |
| Reconciliation Logs | 2 years | Yearly archival to data lake |
| Import Error Logs | 90 days | Auto-cleanup after review |
| Redis Cache | 5 minutes TTL | Auto-expiry |

---

## 6. API Requirements

### 6.1 API Design Principles

| Principle | Specification |
|-----------|--------------|
| Protocol | REST over HTTPS |
| Authentication | OAuth 2.0 / JWT tokens |
| Authorization | RBAC with resource-level permissions |
| Versioning | URI-based (`/api/v1/`) |
| Pagination | Cursor-based for large datasets |
| Rate Limiting | Per-user, per-endpoint (see Reference Design Section 4.1) |
| Error Format | RFC 7807 Problem Details |
| Content Type | `application/json` |

### 6.2 API Endpoints

| Method | Endpoint | Auth | Rate Limit | Description |
|--------|----------|------|------------|-------------|
| POST | `/api/v1/assets` | `asset.write` | 100/min | Create asset |
| GET | `/api/v1/assets` | `asset.read` | 1000/min | List assets |
| GET | `/api/v1/assets/{id}` | `asset.read` | 1000/min | Get asset |
| PUT | `/api/v1/assets/{id}` | `asset.write` | 100/min | Update asset |
| DELETE | `/api/v1/assets/{id}` | `asset.admin` | 50/min | Soft delete |
| GET | `/api/v1/assets/search` | `asset.read` | 500/min | Search assets |
| POST | `/api/v1/assets/import` | `asset.write` | 10/min | Bulk import |
| GET | `/api/v1/assets/import/{job_id}` | `asset.read` | 100/min | Import status |
| GET | `/api/v1/enrich/asset/{id}` | `enrichment.read` | 1000/min | Enrichment lookup |
| GET | `/api/v1/enrich/asset/serial/{sn}` | `enrichment.read` | 1000/min | Serial lookup |
| GET | `/api/v1/enrich/asset/tag/{tag}` | `enrichment.read` | 1000/min | Tag lookup |
| POST | `/api/v1/enrich/assets/batch` | `enrichment.read` | 100/min | Batch enrichment |
| GET | `/api/v1/locations` | `location.read` | 500/min | List locations |
| POST | `/api/v1/locations` | `location.write` | 100/min | Create location |
| GET | `/api/v1/contracts` | `contract.read` | 500/min | List contracts |
| POST | `/api/v1/contracts` | `contract.write` | 100/min | Create contract |

### 6.3 Error Handling

| HTTP Status | Error Code | Description |
|-------------|------------|-------------|
| 400 | `VALIDATION_ERROR` | Request validation failed |
| 401 | `UNAUTHORIZED` | Missing or invalid authentication |
| 403 | `FORBIDDEN` | Insufficient permissions |
| 404 | `NOT_FOUND` | Resource not found |
| 409 | `CONFLICT` | Duplicate asset_tag or serial+manufacturer |
| 422 | `UNPROCESSABLE` | Business rule violation |
| 429 | `RATE_LIMITED` | Rate limit exceeded |
| 500 | `INTERNAL_ERROR` | Server error (with correlation ID) |

---

## 7. Integration Requirements

### 7.1 CMDB Integration

| Requirement | Specification |
|-------------|--------------|
| Direction | Bidirectional (Asset ↔ CMDB) |
| Protocol | REST API + Kafka events |
| Topics | `cmdb.asset.sync` (CMDB → Asset), `asset.cmdb.sync` (Asset → CMDB) |
| Frequency | Real-time (event-driven) + daily reconciliation |
| Data Mapping | `asset.asset_id` ↔ `cmdb.ci_id` via `asset_cmdb_mapping` table |
| Conflict Resolution | Asset Repository wins for financial/warranty/contract; CMDB wins for CI relationships |

### 7.2 DI&I Gateway Integration

| Requirement | Specification |
|-------------|--------------|
| Direction | Inbound (DI&I → Asset) |
| Protocol | Kafka consumer |
| Topics | `dcim.asset.updates` (normalized asset events) |
| Consumer Group | `asset-repository-consumer` |
| Processing | Async, at-least-once delivery |
| Idempotency | Upsert by `asset_tag` or `serial_number` + `manufacturer` |

### 7.3 Analytics Engine Integration

| Requirement | Specification |
|-------------|--------------|
| Direction | Outbound (Asset → Analytics) |
| Protocol | Enrichment API (REST) + Kafka events |
| Topics | `asset.lifecycle.events`, `asset.location.events` |
| Data | Asset profile, location, financial summary |
| Use Cases | Capacity planning, depreciation forecasting, asset utilization |

### 7.4 ERP/ITSM Integration

| Requirement | Specification |
|-------------|--------------|
| Direction | Bidirectional |
| Protocol | REST API adapters |
| Frequency | Scheduled (daily/weekly) |
| Data Mapping | `asset.asset_id` ↔ ERP `material_id`, ITSM `ci_id` |
| Conflict Resolution | ERP wins for procurement; Asset wins for lifecycle |

### 7.5 Kafka Topics

| Topic | Partitions | Retention | Consumer |
|-------|-----------|-----------|----------|
| `asset.events` | 6 | 7 days | CMDB, Analytics |
| `asset.lifecycle.events` | 3 | 30 days | Analytics |
| `asset.location.events` | 3 | 30 days | Analytics, Workflow |
| `dcim.nvr.*` (5 topics) | 3 each | 7 days | NVR consumers |
| `asset.reconciliation.events` | 3 | 7 days | CMDB, DI&I |

---

## 8. Security Requirements

### 8.1 Authentication & Authorization

| Requirement | Specification |
|-------------|--------------|
| Authentication | OAuth 2.0 / JWT (via central IAM) |
| Authorization | RBAC with resource-level permissions |
| Roles | `asset.read`, `asset.write`, `asset.admin`, `enrichment.read`, `location.read`, `location.write`, `contract.read`, `contract.write` |
| API Keys | Service accounts for system-to-system (DI&I, CMDB, Analytics) |
| Token Expiry | 15 minutes (access), 7 days (refresh) |

### 8.2 Data Protection

| Requirement | Specification |
|-------------|--------------|
| Encryption at Rest | AES-256 (PostgreSQL TDE or disk-level) |
| Encryption in Transit | TLS 1.2+ for all connections |
| Secret Storage | HashiCorp Vault / Kubernetes Secrets |
| Sensitive Fields | `purchase_cost`, `book_value`, `total_value` encrypted at field level |
| Data Classification | Public: asset name, model; Internal: location, owner; Confidential: financial, contract |

### 8.3 Audit & Compliance

| Requirement | Specification |
|-------------|--------------|
| Audit Trail | Immutable, field-level logging for all changes |
| Access Logging | All API calls logged with user, timestamp, endpoint, IP |
| Compliance | SOC 2 Type II, ISO 27001 (audit-ready) |
| Data Retention | 7 years for audit logs, configurable for other data |
| Immutability | PostgreSQL row-level security: no UPDATE/DELETE on audit tables |

### 8.4 Network Security

| Requirement | Specification |
|-------------|--------------|
| Network Segmentation | Asset Repository in Management VLAN |
| Firewall Rules | API port (443) open to internal network only |
| Database Access | Direct access restricted to application servers only |
| Redis Access | Direct access restricted to application servers only |

---

## 9. Observability Requirements

### 9.1 Metrics

| Metric | Type | Description | Alert Threshold |
|--------|------|-------------|-----------------|
| `asset_api_requests_total` | Counter | Total API requests by endpoint, status | — |
| `asset_api_request_duration_seconds` | Histogram | API response time distribution | p99 > 500ms |
| `asset_import_jobs_total` | Counter | Total import jobs by status | — |
| `asset_import_records_processed` | Counter | Records processed per import job | — |
| `asset_reconciliation_runs_total` | Counter | Total reconciliation runs | — |
| `asset_reconciliation_conflicts` | Gauge | Current unresolved conflicts | > 100 |
| `asset_db_connection_pool_active` | Gauge | Active database connections | > 80% pool |
| `asset_redis_cache_hit_ratio` | Gauge | Cache hit ratio | < 80% |
| `asset_warranty_expiry_alerts` | Gauge | Assets with warranty expiring in 30 days | > 0 (info) |
| `asset_contract_expiry_alerts` | Gauge | Contracts expiring in 30 days | > 0 (warning) |

### 9.2 Logging

| Log Type | Level | Format | Destination |
|----------|-------|--------|-------------|
| Application Logs | INFO/WARN/ERROR | Structured JSON | Central Logging (ELK/Loki) |
| Access Logs | INFO | Structured JSON | Central Logging |
| Audit Logs | INFO | Structured JSON | PostgreSQL (immutable) |
| Error Logs | ERROR | Structured JSON + stack trace | Central Logging + Alerting |

### 9.3 Tracing

| Requirement | Specification |
|-------------|--------------|
| Distributed Tracing | OpenTelemetry / Jaeger |
| Correlation ID | Generated per request, propagated through all services |
| Span Attributes | `asset_id`, `operation`, `user_id`, `source` |

### 9.4 Alerting

| Alert | Condition | Severity | Action |
|-------|-----------|----------|--------|
| API Degradation | p99 > 500ms for 5 min | P2 High | Investigate API server |
| Database Connection Pool Exhaustion | Active > 80% for 5 min | P1 Critical | Scale connection pool |
| Cache Miss Storm | Hit ratio < 80% for 10 min | P3 Medium | Investigate cache invalidation |
| Import Job Failure | Job status = failed | P2 High | Check import logs |
| Reconciliation Conflict Spike | Conflicts > 100 | P2 High | Manual review required |
| Warranty Expiry | Asset warranty expiring in 30 days | P4 Supporting | Notification to owner |
| Contract Expiry | Contract expiring in 30 days | P3 Medium | Notification to owner |
| Disk Usage | PostgreSQL disk > 80% | P2 High | Scale storage |

---

## 10. Acceptance Criteria

### 10.1 Functional Acceptance

| ID | Criterion | Test Method |
|----|-----------|-------------|
| AC-F-001 | Create asset via API returns 201 with valid `asset_id` | API test |
| AC-F-002 | Create duplicate `asset_tag` returns 409 Conflict | API test |
| AC-F-003 | Create duplicate `serial_number` + `manufacturer` returns 409 Conflict | API test |
| AC-F-004 | Update asset logs field-level changes to audit trail | DB query test |
| AC-F-005 | Soft delete sets `lifecycle_status = 'disposed'` | API + DB test |
| AC-F-006 | Bulk import processes 10,000 records in < 30 seconds | Performance test |
| AC-F-007 | Bulk import skips invalid rows and returns row-level errors | Import test |
| AC-F-008 | Reconciliation matches assets to CMDB CIs by serial + manufacturer | Integration test |
| AC-F-009 | Enrichment API returns full asset profile in < 50ms (cached) | Performance test |
| AC-F-010 | Enrichment API cache invalidated on asset update | Integration test |
| AC-F-011 | Audit log is immutable (no UPDATE/DELETE allowed) | Security test |
| AC-F-012 | Location uniqueness enforced (room + rack + position_u) | DB constraint test |

### 10.2 Non-Functional Acceptance

| ID | Criterion | Test Method |
|----|-----------|-------------|
| AC-NF-001 | API p99 latency < 50ms (cached) under 100 concurrent users | Load test |
| AC-NF-002 | API p99 latency < 200ms (uncached) under 100 concurrent users | Load test |
| AC-NF-003 | System handles 10,000 assets with < 10% performance degradation | Stress test |
| AC-NF-004 | Database failover completes in < 30 seconds | HA test |
| AC-NF-005 | Redis failover completes in < 10 seconds | HA test |
| AC-NF-006 | All API endpoints require authentication | Security test |
| AC-NF-007 | RBAC enforced: user without `asset.write` cannot create/update | Security test |
| AC-NF-008 | TLS 1.2+ enforced on all connections | Security test |
| AC-NF-009 | Audit logs retained for 7 years | Compliance test |
| AC-NF-010 | Backup restoration completes within RTO (15 minutes) | DR test |

### 10.3 Integration Acceptance

| ID | Criterion | Test Method |
|----|-----------|-------------|
| AC-I-001 | DI&I Gateway asset updates processed within 5 seconds | Integration test |
| AC-I-002 | CMDB reconciliation runs daily and completes within 10 minutes | Integration test |
| AC-I-003 | Kafka events published on asset lifecycle changes | Integration test |
| AC-I-004 | ERP asset sync runs daily and matches records | Integration test |

---

## 11. Risk & Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Data quality issues from legacy import | High | High | Data cleansing pipeline, validation rules, staging area |
| Performance degradation at scale | Medium | High | Read replicas, caching, query optimization, monitoring |
| CMDB ↔ Asset sync conflicts | Medium | Medium | Clear SSOT boundaries, conflict resolution rules, manual review queue |
| Audit log storage growth | Medium | Low | Monthly partitioning, archival to cold storage |
| API abuse / rate limit bypass | Low | Medium | Rate limiting, API key rotation, monitoring |
| Database corruption | Low | Critical | Daily backups, WAL archiving, PITR, DR replication |
| Security breach | Low | Critical | Encryption, RBAC, audit logging, network segmentation |
| NVR integration complexity | Medium | Medium | Phased rollout, dedicated NVR team, extensive testing |

---

## 12. Open Questions

| ID | Question | Owner | Priority | Status |
|----|----------|-------|----------|--------|
| OQ-001 | Apakah perlu support hard delete untuk asset tertentu (compliance requirement)? | Owner | P2 | Open |
| OQ-002 | Berapa lama retensi data audit log yang dibutuhkan untuk compliance? (7 tahun vs 10 tahun) | Finance/Legal | P2 | Open |
| OQ-003 | Apakah perlu real-time sync dengan ERP, atau batch daily sudah cukup? | ERP Team | P2 | Open |
| OQ-004 | Bagaimana handle aset yang sudah tidak aktif tapi belum disposed? (lifecycle_status = 'retired' tapi masih ada di lapangan) | Facilities | P3 | Open |
| OQ-005 | Apakah perlu multi-site support sejak awal, atau single-site dulu? | Architecture | P1 | Open |
| OQ-006 | Bagaimana handle aset yang dipindahkan antar site? (location transfer workflow) | Facilities | P3 | Open |
| OQ-007 | Apakah perlu approval workflow untuk asset create/update/delete? | ITSM | P3 | Open |
| OQ-008 | Berapa lama data import error log perlu disimpan? | Operations | P4 | Open |
| OQ-009 | Apakah NVR integration termasuk dalam scope Phase 1 atau Phase 2? | Owner | P1 | Open |
| OQ-010 | Bagaimana handle aset yang dibuat melalui CMDB tapi belum ada di Asset Repository? (CI-first workflow) | CMDB Team | P2 | Open |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| SSOT | Single Source of Truth |
| CMDB | Configuration Management Database |
| DI&I | Data Ingestion & Integration |
| NVR | Network Video Recorder |
| CI | Configuration Item |
| RBAC | Role-Based Access Control |
| DLQ | Dead Letter Queue |
| WAL | Write-Ahead Log |
| RTO | Recovery Time Objective |
| RPO | Recovery Point Objective |
| PITR | Point-in-Time Recovery |
| U Position | Rack unit position (1U = 44.45mm) |

---

## Appendix B: Related Documents

| Document | Path |
|----------|------|
| Reference Design Spec | `~/dcim-wiki/reference-designs/block3-asset-repository.md` |
| Architecture Diagram | `diagrams/block3-asset-repository-architecture.html` |
| NVR Integration Spec | `~/dcim-wiki/reference-designs/nvr-asset-repository-integration.md` |
| NVR Architecture Diagram | `diagrams/nvr-asset-repository-integration.html` |
| Block 2 (DI&I) Reference Design | `~/dcim-wiki/reference-designs/block2-data-ingestion-integration.md` |
| Block 4 (CMDB) Reference Design | `~/dcim-wiki/reference-designs/block4-cmdb.md` |
| Implementation Plan | `~/dcim-wiki/implementation-plan.md` |

---

*Generated by Hermes DCIM Orchestrator — 2026-06-25*
*Reference: Block 3 Asset Repository Reference Design Spec*