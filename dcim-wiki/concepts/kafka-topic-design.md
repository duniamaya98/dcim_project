---
title: Kafka Topic Design
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [kafka, architecture]
sources: []
confidence: high
---

# Kafka Topic Design

Topic structure untuk DCIM event streaming.

## Topics

### dcim.events.raw
- **Purpose**: Raw events from all sources
- **Partitions**: 12
- **Replication**: 3
- **Retention**: 7 days
- **Consumers**: Validation processor

### dcim.events.validated
- **Purpose**: Events that passed validation
- **Partitions**: 12
- **Replication**: 3
- **Retention**: 7 days
- **Consumers**: Enrichment processor

### dcim.events.enriched
- **Purpose**: Events with CI/asset metadata
- **Partitions**: 12
- **Replication**: 3
- **Retention**: 30 days
- **Consumers**: CMDB, Asset, Analytics, SIEM

### dcim.events.dlq
- **Purpose**: Failed events for reprocessing
- **Partitions**: 6
- **Replication**: 3
- **Retention**: 90 days
- **Consumers**: Manual review, reprocessor

### dcim.cmdb.updates
- **Purpose**: CI create/update events
- **Partitions**: 6
- **Replication**: 3
- **Retention**: 30 days
- **Consumers**: CMDB consumers

### dcim.asset.updates
- **Purpose**: Asset create/update events
- **Partitions**: 6
- **Replication**: 3
- **Retention**: 30 days
- **Consumers**: Asset consumers

### dcim.security.events
- **Purpose**: Security events for SIEM
- **Partitions**: 6
- **Replication**: 3
- **Retention**: 90 days
- **Consumers**: Wazuh, SIEM processor

## Naming Convention
`dcim.{domain}.{purpose}`

## Related
- [[kafka]]
- [[data-ingestion-integration]]
- [[dcim-core-platform]]
