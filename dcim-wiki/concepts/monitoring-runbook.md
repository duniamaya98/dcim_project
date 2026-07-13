---
title: Monitoring Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [observability, sop-runbook]
sources: []
confidence: high
---

# Monitoring Runbook

Monitoring procedures untuk DCIM platform.

## Health Checks

### Application
```bash
curl http://localhost:8080/health
# Expected: {"status": "healthy"}
```

### PostgreSQL
```bash
docker exec postgres pg_isready -U dcim
# Expected: accepting connections
```

### Redis
```bash
docker exec redis redis-cli ping
# Expected: PONG
```

### Kafka
```bash
docker exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
# Expected: connection successful
```

### Elasticsearch
```bash
curl http://localhost:9200/_cluster/health
# Expected: "status": "green" or "yellow"
```

## Alert Response

### P1: Service Down
1. Check health endpoints
2. Review logs
3. Restart service if needed
4. Escalate if not resolved in 15 min

### P2: High Error Rate
1. Identify error source
2. Check dependencies
3. Review recent changes
4. Implement fix or rollback

### P3: Performance Degradation
1. Check metrics (CPU, memory, disk)
2. Review query performance
3. Check connection pools
4. Optimize or scale

## Dashboard Access
- NOC: http://grafana:3000/d/noc
- SOC: http://grafana:3000/d/soc
- Facilities: http://grafana:3000/d/facilities

## Related
- [[observability-strategy]]
- [[prometheus]]
- [[grafana]]
- [[ha-dr-strategy]]
- [[dcim-operational-procedures]]
