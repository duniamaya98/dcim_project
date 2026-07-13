---
title: Service Catalog
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [cmdb, architecture]
sources: []
confidence: high
---

# Service Catalog

Service catalog untuk DCIM platform.

## Service Categories

### Core Services
- **CMDB Service**: CI management, relationships, topology
- **Asset Service**: Asset management, lifecycle, financial
- **Data Ingestion Service**: Event processing, validation, enrichment
- **Analytics Service**: Anomaly detection, predictive, RCA

### Platform Services
- **Authentication Service**: SSO, MFA, token management
- **Authorization Service**: RBAC, permissions, policies
- **Notification Service**: Email, SMS, Slack, Teams
- **Workflow Service**: Ticketing, approval, escalation

### Infrastructure Services
- **Database Service**: PostgreSQL, Redis, Elasticsearch
- **Messaging Service**: Kafka, NiFi
- **Monitoring Service**: Prometheus, Grafana
- **Storage Service**: File, object, backup

## Service Dependencies
- Core services depend on Infrastructure services
- Platform services are shared
- Core services are independent where possible

## Service Health
- Health checks per service
- Dependency monitoring
- SLA tracking
- Performance metrics

## Service Ownership
- Team assignment
- On-call rotation
- Documentation ownership
- Improvement responsibility

## Related
- [[dcim-core-platform]]
- [[cmdb]]
- [[service-mapping-strategy]]
- [[sla-framework]]
