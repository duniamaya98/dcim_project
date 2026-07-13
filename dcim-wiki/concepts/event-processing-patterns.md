---
title: Event Processing Patterns
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [architecture, data-quality, performance]
sources: []
confidence: high
---

# Event Processing Patterns

Patterns untuk event processing di DCIM platform.

## Real-Time Processing
- **Trigger**: P1 events (outage, safety)
- **Latency**: < 1 second
- **Pipeline**: Source → Kafka → Stream Processor → Action
- **Tools**: Kafka Streams, Flink

## Near-Real-Time (NRT) Processing
- **Trigger**: P2 events (degradation)
- **Latency**: < 5 minutes
- **Pipeline**: Source → Kafka → Batch Processor → Store
- **Tools**: NiFi, Python consumers

## Batch Processing
- **Trigger**: P3/P4 events (planning, historical)
- **Latency**: Hours to days
- **Pipeline**: Source → File/API → ETL → Store
- **Tools**: NiFi, custom scripts

## Dead Letter Queue (DLQ) Pattern
```
Source → Kafka → Processor → [Success] → Target
                    ↓ [Failure]
                    DLQ → Retry → DLQ → Alert → Manual Review
```

## Enrichment Pattern
```
Raw Event → Validation → Enrichment (CI/Asset lookup) → Normalized Event → Store
```

## Related
- [[dcim-core-platform]]
- [[data-ingestion-integration]]
- [[kafka]]
- [[nifi]]
