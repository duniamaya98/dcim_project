---
title: Asset Repository
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [asset-repository, data-quality, ha-dr]
sources: []
confidence: high
---

# Asset Repository

Single Source of Truth (SSOT) untuk aset fisik, finansial, dan kontrak.

## Fungsi
- Master data aset: physical assets, financial attributes, warranty, contract
- Lifecycle tracking dari procurement sampai disposal
- Location tracking fisik (building, floor, room, rack, position)
- Read-optimized enrichment API untuk [[cmdb]] dan analytics

## Asset Data Model
- **Asset_ID**: unique identifier, format `AST-{seq}`
- **Serial Number**: unique per manufacturer
- **Asset Tag**: internal barcode/RFID tag
- **Owner**: department/person responsible
- **PO Number**: purchase order reference
- **Warranty**: start_date, end_date, provider
- **Contract**: contract_id, vendor, SLA terms
- **Financial**: purchase_cost, depreciation_method, book_value
- **Lifecycle Status**: On Order → Received → Deployed → In Storage → Maintenance → Retired → Disposed

## PostgreSQL Schema
```sql
asset (asset_id, serial_number, asset_tag, name, model, manufacturer,
       owner_dept, location_id, po_number, purchase_date, purchase_cost,
       warranty_start, warranty_end, contract_id, lifecycle_status,
       created_at, updated_at)

asset_location (location_id, building, floor, room, rack, position_u,
                latitude, longitude, created_at)

asset_financial (asset_id, depreciation_method, useful_life_years,
                 book_value, last_depreciation_date)

asset_contract (contract_id, vendor, contract_type, start_date, end_date,
                sla_terms, renewal_date)
```

## APIs
- CRUD: POST/GET/PUT/DELETE `/api/v1/assets`
- Bulk import: POST `/api/v1/assets/bulk` (CSV/JSON)
- Enrichment: GET `/api/v1/assets/enrich/{ci_id}` (untuk CMDB)
- Search: GET `/api/v1/assets/search?serial=X&tag=Y`
- Audit: GET `/api/v1/assets/{id}/audit-trail`

## Enrichment API
- Read-optimized endpoint untuk CMDB dan analytics
- Returns: asset_id, serial, owner, warranty_status, contract_status, location
- Redis cache: TTL 15 menit
- Used by [[cmdb]] reconciliation engine

## Reconciliation
- Match dengan CMDB berdasarkan serial_number + asset_tag
- Match dengan discovery data
- Conflict resolution: newer data wins
- Log semua perubahan

## Data Quality
- Asset_ID uniqueness enforced
- Serial number / asset tag consistency
- Mandatory fields: asset_id, serial_number, name, model, lifecycle_status
- Referential integrity: location_id, contract_id valid
- Duplicate prevention: serial_number + manufacturer unique

## Phase 1 Tasks (Block 3)
- Asset data model design
- PostgreSQL schema
- CRUD API
- Bulk import API
- Reconciliation engine
- Audit trails
- Enrichment API (Redis cache)
- Testing

## Related
- [[dcim-core-platform]]
- [[cmdb]] — CI/asset reconciliation
- [[data-ingestion-integration]] — asset update events
- [[postgresql]]
- [[redis]]
- [[asset-data-model]]
