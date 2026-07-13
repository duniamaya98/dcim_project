---
title: PostgreSQL
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [postgresql, infrastructure]
sources: []
confidence: high
---

# PostgreSQL

Primary relational database untuk DCIM platform.

## Version
- PostgreSQL 16

## Usage
- [[cmdb]] — CI data, relationships, topology
- [[asset-repository]] — asset master data, financial, contracts
- Application metadata

## HA Configuration
- Streaming replication (primary + replica)
- Patroni for automatic failover
- Connection pooling: PgBouncer
- Backup: pg_basebackup + WAL archiving

## Schema Management
- Version-controlled migrations
- Separate schemas per component
- Audit triggers for change tracking

## Performance
- Indexing strategy: B-tree for lookups, GIN for JSONB
- Partitioning for large tables (audit logs, events)
- Query optimization: EXPLAIN ANALYZE

## Related
- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[cmdb]]
- [[asset-repository]]
- [[database-replication-comparison]]
