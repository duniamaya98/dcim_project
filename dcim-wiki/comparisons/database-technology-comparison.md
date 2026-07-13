---
title: Database Technology Comparison
created: 2026-06-23
updated: 2026-06-23
type: comparison
tags: [comparison, postgresql, redis, elasticsearch]
sources: []
confidence: high
---

# Database Technology Comparison

Perbandingan database technologies yang digunakan di DCIM.

## PostgreSQL
- **Type**: Relational (OLTP)
- **Version**: 16
- **Usage**: CMDB, Asset Repository, application metadata
- **Strengths**: ACID, complex queries, JSONB, extensions
- **HA**: Streaming replication, Patroni failover
- **Best for**: Structured data, transactions, relationships

## Redis
- **Type**: In-memory key-value
- **Version**: 7
- **Usage**: Caching, session store, pub/sub
- **Strengths**: Sub-ms latency, pub/sub, data structures
- **HA**: Sentinel, Cluster
- **Best for**: Caching, real-time, temporary data

## Elasticsearch / OpenSearch
- **Type**: Search & analytics engine
- **Version**: 8.x / 2.x
- **Usage**: Logging, SIEM, full-text search
- **Strengths**: Full-text search, aggregations, scalability
- **HA**: Multi-node cluster, shard replication
- **Best for**: Logs, search, analytics

## Usage Matrix

| Data Type | Primary Store | Cache | Search |
|-----------|--------------|-------|--------|
| CI data | PostgreSQL | Redis | Elasticsearch |
| Asset data | PostgreSQL | Redis | - |
| Events | Kafka | - | Elasticsearch |
| Logs | Elasticsearch | - | Elasticsearch |
| Security events | Elasticsearch | - | Elasticsearch |
| Metrics | Time-series DB | - | - |

## Related
- [[dcim-core-platform]]
- [[postgresql]]
- [[redis]]
- [[elasticsearch]]
