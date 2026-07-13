---
title: Disaster Recovery Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [ha-dr, sop-runbook]
sources: []
confidence: high
---

# Disaster Recovery Runbook

DR runbook untuk DCIM platform.

## Prerequisites
- Backup available
- Access to infrastructure
- Communication channels

## Procedure

### 1. Assess Situation
- Identify affected systems
- Determine RTO/RPO
- Notify stakeholders
- Activate DR team

### 2. Restore PostgreSQL
```bash
# Stop application
docker stop dcim-app

# Restore base backup
pg_restore -d dcim /backup/base/latest

# Replay WAL
pg_wal_replay /backup/wal/

# Verify data
psql -c "SELECT COUNT(*) FROM ci;"
```

### 3. Restore Redis
```bash
# Restore from RDB
cp /backup/redis/dump.rdb /var/lib/redis/
redis-server /etc/redis/redis.conf
```

### 4. Restore Elasticsearch
```bash
# Restore snapshot
curl -X POST "localhost:9200/_snapshot/backup/snapshot_1/_restore"
```

### 5. Verify Application
- Start application
- Run health checks
- Verify data integrity
- Test critical functions

### 6. Switch Traffic
- Update DNS/load balancer
- Monitor for issues
- Communicate to users

### 7. Post-DR
- Document timeline
- Lessons learned
- Update runbook
- Schedule DR test

## Escalation
- Level 1: Operations team
- Level 2: Management
- Level 3: Vendor support

## Related
- [[ha-dr-strategy]]
- [[backup-recovery-strategy]]
- [[postgresql]]
- [[redis]]
- [[elasticsearch]]
