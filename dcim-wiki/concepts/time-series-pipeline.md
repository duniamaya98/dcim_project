---
title: Time-Series Pipeline
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [analytics-ai, architecture, performance]
sources: []
confidence: high
---

# Time-Series Pipeline

Time-series data pipeline untuk DCIM analytics.

## Architecture
```
Kafka → Flink/Python → TimescaleDB/InfluxDB → Grafana
```

## Components

### Ingestion
- Kafka topics: metrics stream
- Consumer groups per pipeline
- Batch size: 1000 records
- Flush interval: 5 seconds

### Processing
- Flink: real-time aggregation
- Python: batch processing
- Windowing: tumbling, sliding
- Aggregation: avg, min, max, p95, p99

### Storage
- **TimescaleDB**: PostgreSQL extension, good for SQL queries
- **InfluxDB**: Purpose-built, good for high cardinality
- Choice depends on query patterns

### Visualization
- Grafana dashboards
- Real-time charts
- Historical trends
- Alert rules

## Metrics Stored
- System: CPU, memory, disk, network
- Application: request rate, latency, error rate
- Infrastructure: Kafka lag, DB connections
- DCIM: event throughput, DLQ size

## Retention
- Raw metrics: 30 days
- Aggregated metrics: 1 year
- Downsampled: 5 years

## Related
- [[dcim-core-platform]]
- [[analytics-ai-engine]]
- [[kafka]]
- [[grafana]]
