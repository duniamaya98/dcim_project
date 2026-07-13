---
title: Kafka
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [kafka, infrastructure]
sources: []
confidence: high
---

# Kafka

Message broker untuk event streaming di DCIM platform.

## Configuration
- **Version**: 3.x
- **Brokers**: 3
- **Controller**: KRaft (no ZooKeeper)
- **Replication Factor**: 3
- **Min.Insync.Replicas**: 2

## Topics
- `dcim.events.raw` — raw events from all sources
- `dcim.events.validated` — events passed validation
- `dcim.events.enriched` — events with CI/asset metadata
- `dcim.events.dlq` — dead letter queue
- `dcim.cmdb.updates` — CI create/update events
- `dcim.asset.updates` — asset create/update events
- `dcim.security.events` — security events for SIEM

## Usage
- [[data-ingestion-integration]] — event ingestion pipeline
- [[analytics-ai-engine]] — metric streaming
- [[siem-soc]] — security event pipeline

## Monitoring
- Consumer lag metrics
- Broker health
- Topic partition distribution
- Replication status

## Related
- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[data-ingestion-integration]]
- [[kafka-topic-design]]
- [[data-pipeline-comparison]]
- [[message-queue-comparison]]
