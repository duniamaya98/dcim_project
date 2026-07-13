---
title: CMDB
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [cmdb, data-quality, architecture, ha-dr]
sources: []
confidence: high
---

# Configuration Management Database (CMDB)

Single Source of Truth (SSOT) untuk Configuration Items (CIs) dan relationships.

## Fungsi
- Menyimpan semua CI data: servers, network devices, storage, VMs, applications, services
- Relationship modeling: containment, dependency, connectivity
- Topology engine untuk service mapping dan impact analysis
- Reconciliation dengan [[asset-repository]] dan discovery data

## CI Data Model
- **CI_ID**: unique identifier, format `CI-{type}-{seq}`
- **CI Type**: Server, NetworkDevice, Storage, VM, Application, Service, etc.
- **Mandatory Attributes**: name, type, status, owner, location, serial_number (if applicable)
- **Lifecycle Status**: Planned → Active → Maintenance → Retired → Disposed
- **Custom Attributes**: extensible per CI type

## Relationship Model
- **Containment**: Rack contains Server, Server contains Disk
- **Dependency**: Service depends on Application, Application depends on Server
- **Connectivity**: Server connected_to Switch, Switch connected_to Router
- **Impact**: Change on Server impacts Service

## Topology Engine
- Graph-based relationship traversal
- Service mapping: end-to-end service dependency view
- Impact analysis: "what breaks if this CI fails?"
- Root cause analysis support

## PostgreSQL Schema
```sql
-- Core tables
ci (ci_id, ci_type, name, status, owner, location_id, serial_number, created_at, updated_at)
ci_attribute (ci_id, attr_name, attr_value, attr_type)
ci_relationship (source_ci_id, target_ci_id, relationship_type, metadata)
ci_lifecycle (ci_id, status, changed_by, changed_at, reason)
```

## APIs
- CRUD: POST/GET/PUT/DELETE `/api/v1/cmdb/ci`
- Bulk import: POST `/api/v1/cmdb/ci/bulk`
- Relationship: POST `/api/v1/cmdb/ci/{id}/relationships`
- Topology: GET `/api/v1/cmdb/topology/{ci_id}`
- Impact: GET `/api/v1/cmdb/impact/{ci_id}`
- Health dashboard: GET `/api/v1/cmdb/health`

## Reconciliation
- **Asset reconciliation**: match CI with [[asset-repository]] by serial_number + asset_tag
- **Discovery reconciliation**: match discovered CIs with CMDB entries
- Conflict resolution: newer data wins, log all changes
- Reconciliation frequency: daily for asset, hourly for discovery

## Data Quality
- CI_ID uniqueness enforced
- Mandatory attribute validation
- Lifecycle status transitions validated
- Relationship integrity: referential constraints
- Audit trail: every change logged with user + timestamp

## Phase 1 Tasks (Block 4)
- Data model design
- PostgreSQL schema
- CI CRUD API
- Relationship modeling
- Topology engine
- Impact analysis
- Reconciliation (Asset + Discovery)
- Service mapping
- Integration hooks
- Health dashboard

## Related
- [[dcim-core-platform]]
- [[asset-repository]] — CI/asset reconciliation
- [[data-ingestion-integration]] — CI update events
- [[postgresql]]
- [[cmdb-reconciliation-runbook]]
