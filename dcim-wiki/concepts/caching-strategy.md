---
title: Caching Strategy
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [architecture, performance]
sources: []
confidence: high
---

# Caching Strategy

Caching design untuk DCIM platform.

## Cache Layers

### Application Cache
- In-memory caching (Redis)
- Session data
- Frequently accessed data
- Computed results

### Database Cache
- PostgreSQL buffer cache
- Query result cache
- Connection pooling

### CDN Cache
- Static assets
- API responses (read-only)
- Dashboard assets

## Cache Policies

### TTL (Time-to-Live)
- **Asset enrichment**: 15 minutes
- **CMDB data**: 5 minutes
- **User sessions**: 24 hours
- **Static assets**: 1 hour

### Cache Invalidation
- **Event-driven**: Invalidate on data change
- **Time-based**: TTL expiration
- **Manual**: Admin trigger

### Cache Patterns
- **Cache-aside**: Application manages cache
- **Write-through**: Write to cache and DB
- **Write-behind**: Write to cache, async to DB

## Monitoring
- Cache hit rate
- Memory usage
- Eviction rate
- Latency impact

## Related
- [[dcim-core-platform]]
- [[redis]]
- [[performance-requirements]]
- [[api-design-principles]]
- [[caching-solution-comparison]]
