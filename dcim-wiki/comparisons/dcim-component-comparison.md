---
title: DCIM Component Comparison
created: 2026-06-23
updated: 2026-06-23
type: comparison
tags: [comparison, architecture]
sources: []
confidence: high
---

# DCIM Component Comparison

Perbandingan komponen DCIM dari segi fungsi, data flow, dan dependency.

## Component Overview

| Component | Primary Function | Data Flow | Key Dependency |
|-----------|-----------------|-----------|----------------|
| [[data-ingestion-integration]] | Event ingestion | Source → Kafka → Processors | Kafka, NiFi |
| [[cmdb]] | CI management | Ingest → CMDB → API | PostgreSQL |
| [[asset-repository]] | Asset management | Ingest → Asset → API | PostgreSQL, Redis |
| [[analytics-ai-engine]] | Intelligence | Metrics → Pipeline → Insights | Kafka, Time-series DB |
| [[workflow-automation]] | Automation | Alert → Workflow → Action | n8n/Temporal |
| [[siem-soc]] | Security | Events → Correlation → Incidents | Elasticsearch, Wazuh |
| [[web-dashboard]] | Presentation | Data → Views → Users | React/Vue, API Gateway |
| [[external-integration]] | External sync | External → Adapter → Core | Adapter per system |

## Data Flow Matrix

| From → To | DI&I | CMDB | Asset | Analytics | Workflow | SIEM | Dashboard |
|-----------|------|------|-------|-----------|----------|------|-----------|
| DI&I | - | CI updates | Asset updates | Metrics | Alerts | Security events | - |
| CMDB | - | - | Reconciliation | Topology | Impact | - | Explorer |
| Asset | - | Enrichment | - | - | - | - | - |
| Analytics | - | - | - | - | Alert triggers | - | Viz |
| Workflow | - | Impact check | - | - | - | Incident flow | Task board |
| SIEM | Events | - | - | - | Escalation | - | SOC view |

## Key Interfaces
- DI&I → CMDB/Asset: event schema
- CMDB ↔ Asset: reconciliation API
- Analytics → Workflow: alert format
- SIEM → Workflow: incident format
- Dashboard → API Gateway: REST/GraphQL

## Related
- [[dcim-core-platform]]
