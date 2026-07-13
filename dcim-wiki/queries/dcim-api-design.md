---
title: DCIM API Design
created: 2026-06-23
updated: 2026-06-23
type: query
tags: [architecture, requirement]
sources: []
confidence: high
---

# DCIM API Design

Complete API design untuk DCIM platform.

## API Standards

### REST API
- Base URL: `/api/v1/`
- Authentication: Bearer token (JWT)
- Content-Type: `application/json`
- Versioning: URL-based (`/api/v1/`, `/api/v2/`)

### Request Format
```json
{
  "data": {},
  "meta": {}
}
```

### Response Format
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

### Error Format
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

## API Endpoints

### CMDB API
```yaml
POST   /api/v1/cmdb/ci              # Create CI
GET    /api/v1/cmdb/ci/{id}         # Get CI
PUT    /api/v1/cmdb/ci/{id}         # Update CI
DELETE /api/v1/cmdb/ci/{id}         # Delete CI
GET    /api/v1/cmdb/ci              # List CIs (filterable)
POST   /api/v1/cmdb/ci/bulk         # Bulk import
GET    /api/v1/cmdb/topology/{id}   # Get topology
GET    /api/v1/cmdb/impact/{id}     # Impact analysis
GET    /api/v1/cmdb/health          # Health dashboard
```

### Asset Repository API
```yaml
POST   /api/v1/assets               # Create asset
GET    /api/v1/assets/{id}          # Get asset
PUT    /api/v1/assets/{id}          # Update asset
DELETE /api/v1/assets/{id}          # Delete asset
GET    /api/v1/assets               # List assets (filterable)
POST   /api/v1/assets/bulk          # Bulk import
GET    /api/v1/assets/enrich/{ci_id} # Enrichment API
GET    /api/v1/assets/{id}/audit    # Audit trail
```

### Event API
```yaml
POST   /api/v1/events               # Ingest event
GET    /api/v1/events               # Query events
GET    /api/v1/events/{id}          # Get event detail
GET    /api/v1/events/dlq           # Get DLQ events
POST   /api/v1/events/dlq/{id}/reprocess # Reprocess DLQ
```

### Workflow API
```yaml
POST   /api/v1/workflows            # Create workflow
GET    /api/v1/workflows/{id}       # Get workflow
PUT    /api/v1/workflows/{id}       # Update workflow
POST   /api/v1/workflows/{id}/approve  # Approve workflow
POST   /api/v1/workflows/{id}/reject   # Reject workflow
GET    /api/v1/workflows            # List workflows
```

### Dashboard API
```yaml
GET    /api/v1/dashboard/noc        # NOC dashboard data
GET    /api/v1/dashboard/soc        # SOC dashboard data
GET    /api/v1/dashboard/facilities # Facilities dashboard data
GET    /api/v1/dashboard/sla        # SLA/KPI data
GET    /api/v1/dashboard/logs       # Log viewer data
GET    /api/v1/dashboard/tasks      # Task board data
```

### Integration API
```yaml
GET    /api/v1/integrations         # List integrations
GET    /api/v1/integrations/{id}    # Get integration status
POST   /api/v1/integrations/{id}/sync # Trigger sync
GET    /api/v1/integrations/{id}/health # Health check
```

## Authentication & Authorization

### JWT Token
```json
{
  "sub": "user123",
  "role": "operator",
  "exp": 1672531200,
  "iat": 1672527600
}
```

### RBAC Roles
- Admin: Full access
- Operator: Read/Write operational data
- Viewer: Read-only
- Auditor: Read + audit logs

### Rate Limiting
- Admin: Unlimited
- Operator: 1000 req/min
- Viewer: 100 req/min
- Auditor: 500 req/min

## Pagination
```json
{
  "meta": {
    "page": 1,
    "limit": 50,
    "total": 1234,
    "pages": 25
  }
}
```

## Filtering
```http
GET /api/v1/cmdb/ci?status=active&type=server&location=rack-1
```

## Sorting
```http
GET /api/v1/assets?sort=created_at:desc
```

## Related
- [[dcim-core-platform]]
- [[api-design-principles]]
- [[api-versioning-strategy]]
- [[api-gateway-strategy]]
- [[cmdb]]
- [[asset-repository]]
