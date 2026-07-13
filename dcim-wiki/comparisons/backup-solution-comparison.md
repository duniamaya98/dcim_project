---
title: Backup Solution Comparison
created: 2026-06-23
updated: 2026-06-23
type: comparison
tags: [comparison, ha-dr]
sources: []
confidence: medium
---

# Backup Solution Comparison

Perbandingan backup solutions.

## pg_basebackup (PostgreSQL)
- **Type**: Native PostgreSQL backup
- **Strengths**: Simple, reliable, WAL integration
- **Weaknesses**: PostgreSQL only, no compression
- **Best for**: PostgreSQL databases

## pg_dump / pg_restore
- **Type**: Logical backup
- **Strengths**: Flexible, selective restore
- **Weaknesses**: Slower for large databases
- **Best for**: Small databases, selective restore

## Barman
- **Type**: PostgreSQL backup tool
- **Strengths**: Remote backup, retention, WAL archiving
- **Weaknesses**: Additional complexity
- **Best for**: Enterprise PostgreSQL

## pgBackRest
- **Type**: PostgreSQL backup tool
- **Strengths**: Parallel backup, compression, encryption
- **Weaknesses**: Complex setup
- **Best for**: Large PostgreSQL databases

## Comparison Matrix

| Feature | pg_basebackup | pg_dump | Barman | pgBackRest |
|---------|---------------|---------|--------|------------|
| Speed | Fast | Slow | Fast | Fast |
| Compression | No | Yes | Yes | Yes |
| Incremental | No | No | Yes | Yes |
| Remote | No | Yes | Yes | Yes |
| Complexity | Low | Low | Medium | High |

## Recommendation
- **pg_basebackup**: For simple deployments
- **pgBackRest**: For large databases, enterprise features
- **Barman**: For managed PostgreSQL

## Related
- [[backup-recovery-strategy]]
- [[ha-dr-strategy]]
- [[postgresql]]
- [[dcim-core-platform]]
