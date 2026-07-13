---
title: Integration Health Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [external-integration, sop-runbook]
sources: []
confidence: high
---

# Integration Health Runbook

External integration health monitoring procedures.

## Health Checks

### ITSM Integration
```bash
# ServiceNow connectivity
curl -u user:pass "https://instance.service-now.com/api/now/table/sysparm_limit=1"

# Jira connectivity
curl -u user:token "https://jira.example.com/rest/api/2/serverInfo"
```

### ERP Integration
```bash
# SAP connectivity
# Check SAP RFC connection

# Oracle connectivity
# Check Oracle REST API
```

### Cloud Integration
```bash
# AWS
aws sts get-caller-identity

# GCP
gcloud auth list

# Azure
az account show
```

## Monitoring
- Connectivity status per integration
- Sync status and latency
- Error rate
- Last successful sync time

## Troubleshooting

### Connection Failure
1. Check network connectivity
2. Verify credentials
3. Check API endpoint status
4. Review firewall rules

### Sync Failure
1. Check data format
2. Verify field mapping
3. Review error logs
4. Check rate limits

### Data Mismatch
1. Compare source/target data
2. Check transformation rules
3. Verify field mapping
4. Review audit trail

## Escalation
- Level 1: Operations team
- Level 2: Integration team
- Level 3: Vendor support

## Related
- [[external-integration]]
- [[external-integration-adapters]]
- [[data-ingestion-integration]]
