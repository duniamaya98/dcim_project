---
title: NiFi Flow Design
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [nifi, architecture]
sources: []
confidence: high
---

# NiFi Flow Design

Data flow design untuk NiFi processors.

## Source Flows

### BMS/EPMS Flow
```
GetFile → Validate → Transform → PublishKafka(dcim.events.raw)
```

### NMS Flow
```
ConsumeSNMP → Validate → Transform → PublishKafka(dcim.events.raw)
```

### Server/Storage Flow
```
GetJMX → Validate → Transform → PublishKafka(dcim.events.raw)
```

### Cloud Flow
```
GetCloudWatch → Validate → Transform → PublishKafka(dcim.events.raw)
```

## Processing Flow
```
ConsumeKafka(raw) → Validate → Enrich → PublishKafka(validated)
ConsumeKafka(validated) → Enrich → PublishKafka(enriched)
```

## Key Processors
- **GetFile/GetSFTP**: Batch file ingestion
- **ConsumeSNMP**: SNMP polling
- **ConsumeJMX**: JMX metrics
- **ConsumeKafka/PublishKafka**: Kafka integration
- **QueryDatabase**: PostgreSQL lookup
- **JoltTransformJSON**: Data transformation
- **ValidateRecord**: Schema validation

## Error Handling
- Retry: 3 attempts
- DLQ: Publish to dcim.events.dlq
- Alert: Prometheus metrics

## Related
- [[nifi]]
- [[kafka]]
- [[data-ingestion-integration]]
