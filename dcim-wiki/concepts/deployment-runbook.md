---
title: Deployment Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [deployment, sop-runbook]
sources: []
confidence: high
---

# Deployment Runbook

Deployment process untuk DCIM platform.

## Prerequisites
- Code reviewed and merged
- Tests passing
- Backup completed
- Maintenance window scheduled

## Docker Compose Deployment

### 1. Pre-Deployment
```bash
# Backup current state
docker exec postgres pg_dump -U dcim dcim > backup_$(date +%Y%m%d).sql

# Pull new images
docker compose pull

# Verify images
docker images | grep dcim
```

### 2. Deploy
```bash
# Stop services
docker compose down

# Start services
docker compose up -d

# Verify health
docker compose ps
curl http://localhost:8080/health
```

### 3. Post-Deployment
```bash
# Run migrations
docker exec dcim-app python manage.py migrate

# Verify functionality
curl http://localhost:8080/api/v1/cmdb/health

# Monitor logs
docker compose logs -f
```

### 4. Rollback (if needed)
```bash
# Stop new version
docker compose down

# Restore previous version
git checkout v1.0.0
docker compose up -d

# Restore database
docker exec -i postgres psql -U dcim dcim < backup_20260623.sql
```

## Kubernetes Deployment
- Use Helm charts or K8s manifests
- Rolling update strategy
- Health checks configured
- Rollback via K8s

## Related
- [[dcim-core-platform]]
- [[docker]]
- [[kubernetes]]
- [[backup-recovery-strategy]]
