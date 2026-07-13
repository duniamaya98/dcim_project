---
title: Performance Tuning Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [performance, sop-runbook]
sources: []
confidence: high
---

# Performance Tuning Runbook

Performance tuning procedures untuk DCIM platform.

## Application Performance

### Slow API Response
1. Check database queries
2. Review connection pools
3. Check cache hit rate
4. Verify network latency

### High CPU Usage
1. Identify process
2. Check for runaway queries
3. Review thread usage
4. Scale horizontally

### Memory Issues
1. Check for memory leaks
2. Review garbage collection
3. Check connection pools
4. Scale vertically

## Database Performance

### Slow Queries
```sql
-- Find slow queries
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

### Connection Pool Issues
```sql
-- Check connections
SELECT count(*) FROM pg_stat_activity;
```

### Index Optimization
```sql
-- Find missing indexes
SELECT * FROM pg_stat_user_tables WHERE seq_scan > 100;
```

## Cache Performance

### Low Hit Rate
```bash
redis-cli INFO stats | grep keyspace_hits
```

### High Memory Usage
```bash
redis-cli INFO memory
```

## Kafka Performance

### Consumer Lag
```bash
kafka-consumer-groups.sh --describe --group dcim-consumer
```

### Broker Issues
```bash
kafka-broker-api-versions.sh --bootstrap-server localhost:9092
```

## Related
- [[performance-requirements]]
- [[observability-strategy]]
- [[postgresql]]
- [[redis]]
- [[kafka]]
