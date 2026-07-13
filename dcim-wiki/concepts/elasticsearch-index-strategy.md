---
title: Elasticsearch Index Strategy
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [elasticsearch, architecture]
sources: []
confidence: high
---

# Elasticsearch Index Strategy

Index lifecycle management untuk Elasticsearch.

## Indices

### dcim-logs-*
- **Purpose**: Application logs
- **Retention**: 7 days
- **Shards**: 3
- **Replicas**: 1
- **ILM**: Hot → Warm → Delete

### dcim-audit-*
- **Purpose**: Audit trails
- **Retention**: 90 days
- **Shards**: 3
- **Replicas**: 1
- **ILM**: Hot → Warm → Delete

### dcim-security-*
- **Purpose**: Security events
- **Retention**: 1 year
- **Shards**: 3
- **Replicas**: 1
- **ILM**: Hot → Warm → Cold → Delete

### dcim-metrics-*
- **Purpose**: Metrics (if using ES for metrics)
- **Retention**: 30 days
- **Shards**: 3
- **Replicas**: 1
- **ILM**: Hot → Delete

## Naming Convention
`dcim-{type}-{YYYY.MM.DD}`

## ILM Policy
- **Hot**: Active writes, fast storage
- **Warm**: Read-only, slower storage
- **Cold**: Archive, cheapest storage
- **Delete**: Remove after retention

## Related
- [[elasticsearch]]
- [[siem-soc]]
- [[dcim-core-platform]]
