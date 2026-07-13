---
title: Database Replication Comparison
created: 2026-06-23
updated: 2026-06-23
type: comparison
tags: [comparison, postgresql, ha-dr]
sources: []
confidence: medium
---

# Database Replication Comparison

Perbandingan database replication strategies.

## Streaming Replication (PostgreSQL)
- **Type**: Physical replication
- **Strengths**: Simple, real-time, reliable
- **Weaknesses**: Read-only replicas, no partial replication
- **Best for**: HA, read scaling

## Logical Replication (PostgreSQL)
- **Type**: Logical replication
- **Strengths**: Selective replication, multi-master potential
- **Weaknesses**: More complex, limitations
- **Best for**: Selective data sync, upgrades

## Patroni (PostgreSQL HA)
- **Type**: HA clustering
- **Strengths**: Automatic failover, cluster management
- **Weaknesses**: Additional complexity
- **Best for**: Production PostgreSQL HA

## Redis Sentinel
- **Type**: Redis HA
- **Strengths**: Automatic failover, monitoring
- **Weaknesses**: Limited scalability
- **Best for**: Redis HA

## Comparison Matrix

| Feature | Streaming | Logical | Patroni | Sentinel |
|---------|-----------|---------|---------|----------|
| HA | Yes | Limited | Yes | Yes |
| Read Scaling | Yes | Yes | Yes | Yes |
| Write Scaling | No | Limited | No | No |
| Auto-Failover | No | No | Yes | Yes |
| Complexity | Low | Medium | High | Medium |

## Recommendation
- **Patroni**: For PostgreSQL HA in production
- **Sentinel**: For Redis HA
- **Streaming**: For simple read scaling

## Related
- [[postgresql]]
- [[redis]]
- [[ha-dr-strategy]]
- [[backup-recovery-strategy]]
- [[dcim-core-platform]]
