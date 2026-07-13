---
title: Redis
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [redis, infrastructure]
sources: []
confidence: high
---

# Redis

In-memory data store untuk caching dan real-time features.

## Version
- Redis 7

## Usage
- [[asset-repository]] enrichment API cache (TTL 15 menit)
- Session store
- Real-time pub/sub untuk alerts
- Rate limiting

## HA Configuration
- Redis Sentinel: 3 sentinels
- Automatic failover
- Persistence: RDB + AOF

## Related
- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[asset-repository]]
