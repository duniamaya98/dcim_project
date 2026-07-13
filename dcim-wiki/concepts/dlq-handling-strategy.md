---
title: DLQ Handling Strategy
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [data-quality, kafka, architecture]
sources: []
confidence: high
---

# DLQ Handling Strategy

Dead Letter Queue handling untuk DCIM platform.

## Purpose
- Capture failed events
- Prevent data loss
- Enable reprocessing
- Monitor data quality

## Flow
```
Source → Kafka → Processor → [Success] → Target
                    ↓ [Failure]
                    DLQ → Retry (3x) → DLQ → Alert → Manual Review
```

## DLQ Topics
- `dcim.events.dlq` — general event failures
- `dcim.cmdb.dlq` — CMDB processing failures
- `dcim.asset.dlq` — Asset processing failures

## Retention
- 90 days for investigation
- Archive to cold storage after

## Reprocessing
- Manual trigger via API
- Batch reprocessing
- Validation before re-entry

## Monitoring
- DLQ size metrics
- Failure rate alerts
- Data quality dashboard

## Related
- [[dcim-core-platform]]
- [[data-ingestion-integration]]
- [[kafka]]
- [[data-quality-framework]]
