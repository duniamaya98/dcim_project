---
title: Data Quality Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [data-quality, sop-runbook]
sources: []
confidence: high
---

# Data Quality Runbook

Data quality monitoring dan remediation procedures.

## Daily Checks

### Validation Rate
```sql
-- Check validation pass rate
SELECT
  date_trunc('hour', created_at) as hour,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) as passed,
  ROUND(SUM(CASE WHEN status = 'passed' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) as pass_rate
FROM events
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY 1
ORDER BY 1;
```

### DLQ Monitoring
```sql
-- Check DLQ size
SELECT COUNT(*) as dlq_count
FROM events
WHERE status = 'dlq'
AND created_at > NOW() - INTERVAL '24 hours';
```

### Completeness Check
```sql
-- Check mandatory fields
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN ci_id IS NULL THEN 1 ELSE 0 END) as missing_ci,
  SUM(CASE WHEN asset_id IS NULL THEN 1 ELSE 0 END) as missing_asset
FROM events
WHERE created_at > NOW() - INTERVAL '24 hours';
```

## Weekly Review
- Data quality metrics review
- DLQ trend analysis
- Enrichment rate review
- Duplicate detection

## Monthly Review
- Comprehensive data quality audit
- Schema compliance check
- Reference integrity verification
- Quality improvement planning

## Remediation Actions
- **DLQ**: Investigate, fix, reprocess
- **Missing data**: Enrichment backfill
- **Duplicates**: Deduplication process
- **Schema drift**: Update validation rules

## Related
- [[data-quality-framework]]
- [[data-ingestion-integration]]
- [[dlq-handling-strategy]]
- [[data-lineage-strategy]]
