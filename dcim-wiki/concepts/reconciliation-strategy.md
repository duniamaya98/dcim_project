---
title: Reconciliation Strategy
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [cmdb, asset-repository, data-quality]
sources: []
confidence: high
---

# Reconciliation Strategy

Reconciliation antara CMDB, Asset Repository, dan discovery data.

## CMDB ↔ Asset Reconciliation
- **Match criteria**: serial_number + asset_tag
- **Frequency**: Daily
- **Conflict resolution**: Newer data wins
- **Logging**: All changes logged

## CMDB ↔ Discovery Reconciliation
- **Match criteria**: hostname + IP + serial_number
- **Frequency**: Hourly
- **Conflict resolution**: Discovery data wins (more current)
- **Logging**: All changes logged

## Asset ↔ Discovery Reconciliation
- **Match criteria**: serial_number + model
- **Frequency**: Daily
- **Conflict resolution**: Newer data wins
- **Logging**: All changes logged

## Reconciliation Process
1. Extract data from sources
2. Match by criteria
3. Identify conflicts
4. Resolve conflicts
5. Update target
6. Log changes
7. Report metrics

## Metrics
- Match rate
- Conflict rate
- Resolution time
- Data quality score

## Related
- [[dcim-core-platform]]
- [[cmdb]]
- [[asset-repository]]
- [[data-quality-framework]]
