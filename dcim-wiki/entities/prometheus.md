---
title: Prometheus
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [prometheus, infrastructure, observability]
sources: []
confidence: high
---

# Prometheus

Metrics collection dan alerting untuk DCIM platform.

## Usage
- Metrics collection dari semua services
- Alert manager integration
- Service discovery
- Long-term storage: Thanos atau Cortex

## Key Metrics
- System: CPU, memory, disk, network
- Application: request rate, latency, error rate
- Infrastructure: Kafka lag, PostgreSQL connections, Redis hit rate
- DCIM: event throughput, processing latency, DLQ size

## Alerting Rules
- Service down (P1)
- High error rate (P2)
- Disk space low (P2)
- Consumer lag high (P3)

## Related
- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[grafana]]
- [[monitoring-solution-comparison]]
