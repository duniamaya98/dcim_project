---
title: CMDB Reconciliation Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [cmdb, data-quality, sop-runbook]
sources: []
confidence: high
---

# CMDB Reconciliation Runbook

CMDB reconciliation procedures.

## Daily Reconciliation

### Asset Reconciliation
```bash
# Run asset reconciliation
python manage.py reconcile_assets --date $(date +%Y%m%d)
```

### Discovery Reconciliation
```bash
# Run discovery reconciliation
python manage.py reconcile_discovery --date $(date +%Y%m%d)
```

## Process

### 1. Extract Data
- CMDB CIs
- Asset Repository assets
- Discovery data

### 2. Match
- By serial_number + asset_tag
- By hostname + IP
- By model + manufacturer

### 3. Identify Conflicts
- Missing in CMDB
- Missing in Asset
- Data mismatch

### 4. Resolve
- Newer data wins
- Log all changes
- Manual review for complex cases

### 5. Update
- Update target system
- Maintain audit trail
- Notify stakeholders

## Metrics
- Match rate: target > 95%
- Conflict rate: target < 5%
- Resolution time: target < 24 hours

## Escalation
- Low match rate: Data quality team
- High conflict rate: Data governance team
- Manual review backlog: Operations team

## Related
- [[reconciliation-strategy]]
- [[cmdb]]
- [[asset-repository]]
- [[data-quality-framework]]
