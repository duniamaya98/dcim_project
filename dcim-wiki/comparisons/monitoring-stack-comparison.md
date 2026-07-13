---
title: Monitoring Stack Comparison
created: 2026-06-23
updated: 2026-06-23
type: comparison
tags: [comparison, prometheus, grafana, elasticsearch]
sources: []
confidence: high
---

# Monitoring Stack Comparison

Perbandingan monitoring tools di DCIM platform.

## Prometheus
- **Type**: Metrics collection & alerting
- **Best for**: Time-series metrics, system health
- **Data model**: Labels, metrics, alerts
- **Query**: PromQL
- **Storage**: Local + Thanos/Cortex for long-term
- **Alerting**: Alertmanager integration

## Grafana
- **Type**: Visualization & dashboard
- **Best for**: Dashboard, alert visualization, trend analysis
- **Data sources**: Prometheus, Elasticsearch, PostgreSQL
- **Features**: Panels, alerts, annotations, variables
- **Dashboards**: NOC, SOC, Facilities, Management

## Elasticsearch
- **Type**: Search & analytics
- **Best for**: Logs, security events, full-text search
- **Data model**: Documents, indices, shards
- **Query**: KQL, Lucene, DSL
- **Features**: Aggregations, ILM, cross-cluster

## Usage Matrix

| Need | Tool | Why |
|------|------|-----|
| System metrics | Prometheus | Purpose-built for metrics |
| Log analysis | Elasticsearch | Full-text search, aggregations |
| Dashboards | Grafana | Multi-source visualization |
| Alerting | Prometheus + Alertmanager | Metric-based alerts |
| Security events | Elasticsearch + Wazuh | SIEM-specific |

## Integration
```
Prometheus → Grafana (metrics viz)
Elasticsearch → Grafana (log viz)
PostgreSQL → Grafana (CMDB/asset viz)
All → Alertmanager → [[workflow-automation]]
```

## Related
- [[dcim-core-platform]]
- [[prometheus]]
- [[grafana]]
- [[elasticsearch]]
