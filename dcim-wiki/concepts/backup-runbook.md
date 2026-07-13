---
title: Backup Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [ha-dr, sop-runbook]
sources: []
confidence: high
---

# Backup Runbook

Backup procedures untuk DCIM platform.

## Daily Backup

### PostgreSQL
```bash
# Base backup
pg_basebackup -U dcim -D /backup/postgres/$(date +%Y%m%d) -Ft -z

# WAL archiving (continuous)
archive_command = 'cp %p /backup/postgres/wal/%f'
```

### Redis
```bash
# RDB snapshot
redis-cli BGSAVE
cp /var/lib/redis/dump.rdb /backup/redis/$(date +%Y%m%d)/
```

### Elasticsearch
```bash
# Snapshot
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_$(date +%Y%m%d)"
```

### Configuration
```bash
# Backup config files
tar -czf /backup/config/$(date +%Y%m%d).tar.gz /etc/dcim/
```

## Weekly Backup
- Full backup verification
- Restore test (sample)
- Backup integrity check

## Monthly Backup
- Full DR drill
- Backup retention cleanup
- Documentation update

## Retention
- Daily: 30 days
- Weekly: 12 weeks
- Monthly: 12 months

## Verification
- Check backup files exist
- Verify checksums
- Test restore (sample)
- Monitor backup jobs

## Related
- [[backup-recovery-strategy]]
- [[ha-dr-strategy]]
- [[postgresql]]
- [[redis]]
- [[elasticsearch]]
