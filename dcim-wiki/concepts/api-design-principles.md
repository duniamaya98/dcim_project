---
title: API Design Principles
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [architecture, requirement]
sources: []
confidence: high
---

# API Design Principles

Standar API untuk DCIM platform.

## REST API Standards
- **Base URL**: `/api/v1/`
- **Authentication**: Bearer token (JWT)
- **Content-Type**: `application/json`
- **Pagination**: `?page=1&limit=50`
- **Filtering**: `?status=active&type=server`
- **Sorting**: `?sort=created_at:desc`

## Response Format
```json
{
  "status": "success",
  "data": {},
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 1234
  }
}
```

## Error Format
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Field 'name' is required",
    "details": {}
  }
}
```

## Key APIs

### CMDB
- `POST /api/v1/cmdb/ci` — create CI
- `GET /api/v1/cmdb/ci/{id}` — get CI
- `PUT /api/v1/cmdb/ci/{id}` — update CI
- `DELETE /api/v1/cmdb/ci/{id}` — delete CI
- `GET /api/v1/cmdb/topology/{id}` — get topology
- `GET /api/v1/cmdb/impact/{id}` — impact analysis

### Asset Repository
- `POST /api/v1/assets` — create asset
- `GET /api/v1/assets/{id}` — get asset
- `PUT /api/v1/assets/{id}` — update asset
- `POST /api/v1/assets/bulk` — bulk import
- `GET /api/v1/assets/enrich/{ci_id}` — enrichment

### Events
- `POST /api/v1/events` — ingest event
- `GET /api/v1/events` — query events
- `GET /api/v1/events/{id}` — get event detail

## Versioning
- URL versioning: `/api/v1/`, `/api/v2/`
- Breaking changes require new major version
- Deprecation notice: 6 months

## Related
- [[dcim-core-platform]]
- [[cmdb]]
- [[asset-repository]]
- [[data-ingestion-integration]]
- [[dcim-api-design]]
