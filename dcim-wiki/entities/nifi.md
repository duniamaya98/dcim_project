---
title: NiFi
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [nifi, infrastructure]
sources: []
confidence: high
---

# Apache NiFi

Data flow orchestration untuk DCIM data ingestion.

## Version
- Apache NiFi 1.x

## Usage
- Visual flow designer untuk data pipelines
- Source connectors: BMS, EPMS, NMS, Server, Cloud
- Validation processors
- Enrichment processors
- Destination: Kafka topics

## Key Processors
- GetFile / GetSFTP — batch file ingestion
- ConsumeKafka / PublishKafka — Kafka integration
- QueryDatabase / PutDatabase — PostgreSQL integration
- JoltTransformJSON — data transformation
- ValidateRecord — schema validation

## Flow Design
```
Source → Ingest → Validate → Transform → Enrich → Publish to Kafka
```

## Related
- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[data-ingestion-integration]]
- [[kafka]]
- [[nifi-flow-design]]
- [[data-integration-comparison]]
