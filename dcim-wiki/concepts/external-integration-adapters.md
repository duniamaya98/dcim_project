---
title: External Integration Adapters
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [external-integration, architecture]
sources: []
confidence: high
---

# External Integration Adapters

Adapter design untuk external integrations.

## Adapter Pattern
```
External System → Adapter → Normalizer → DCIM Core
```

## ITSM Adapters

### ServiceNow Adapter
- **API**: REST API v2
- **Auth**: OAuth 2.0
- **Operations**: Create/Update/Query incidents
- **Sync**: Bi-directional

### Jira Adapter
- **API**: REST API v3
- **Auth**: API token
- **Operations**: Create/Update/Query issues
- **Sync**: Bi-directional

## ERP Adapters

### SAP Adapter
- **API**: RFC/BAPI
- **Auth**: SAP credentials
- **Operations**: Asset master sync
- **Sync**: Batch (daily)

### Oracle Adapter
- **API**: REST API
- **Auth**: OAuth 2.0
- **Operations**: Procurement sync
- **Sync**: Batch (daily)

## Cloud Adapters

### AWS Adapter
- **API**: SDK (boto3)
- **Auth**: IAM roles
- **Operations**: Resource discovery, metrics
- **Sync**: Real-time + batch

### GCP Adapter
- **API**: SDK
- **Auth**: Service account
- **Operations**: Resource discovery, metrics
- **Sync**: Real-time + batch

### Azure Adapter
- **API**: SDK
- **Auth**: Managed identity
- **Operations**: Resource discovery, metrics
- **Sync**: Real-time + batch

## Health Monitoring
- Connectivity check
- Sync status
- Error rate
- Latency

## Related
- [[external-integration]]
- [[data-ingestion-integration]]
- [[dcim-core-platform]]
