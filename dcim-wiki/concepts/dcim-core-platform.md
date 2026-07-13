---
title: DCIM Core Platform
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [requirement, architecture, decision-record]
sources: []
confidence: high
---

# DCIM Core Platform

Data Center Infrastructure Management untuk visibility, control, automation, analytics, dan audit.

## Mission
Bantu owner merancang, membangun, mengevaluasi, mengoperasikan DCIM guna mencapai:
- **Visibility**: monitoring real-time semua infrastruktur data center
- **Control**: otorisasi, akses, konfigurasi terpusat
- **Automation**: workflow, remediation, provisioning
- **Analytics**: anomaly detection, predictive maintenance, RCA
- **Audit**: compliance, security, audit trail

## Arsitektur Layer

```
Source Systems → Data Ingestion & Integration → Core Data Stores → Intelligence → Automation → Presentation
```

1. **Source Systems**: BMS, EPMS, EMS, NMS, server/storage monitoring, virtualization/cloud, access control/surveillance, ITSM, ERP, DMS
2. **Data Ingestion & Integration**: REST API, SNMP, Modbus, MQTT, Syslog, SSH, JDBC/ODBC, SFTP; Kafka/NiFi/Flink; validation, cleansing, normalization, enrichment
3. **Core Data Stores**: CMDB, Asset Repository, time-series/data lake, central logging/SIEM
4. **Intelligence**: Analytics & AI Engine (anomaly detection, capacity forecasting, predictive maintenance, RCA, LLM/RAG)
5. **Automation**: Workflow Automation (ticketing, remediation, provisioning, escalation)
6. **Presentation**: Web dashboard, mobile app, BI tools, NOC/SOC/Facilities views

## Components

- [[data-ingestion-integration]] — single gateway untuk semua data masuk
- [[cmdb]] — SSOT untuk Configuration Items dan relationships
- [[asset-repository]] — SSOT untuk aset fisik/finansial/kontrak
- [[analytics-ai-engine]] — anomaly, predictive, RCA, optimization
- [[workflow-automation]] — ticketing, approval, runbook, remediation
- [[siem-soc]] — security logs, correlation, incident response
- [[web-dashboard]] — NOC/SOC/Facilities view

## Phase & Timeline

### Phase 1: Infrastructure & Core Foundation (32 tasks, 4 blocks)
- [[infrastructure-provisioning]] — VM/container, PostgreSQL, Redis, Kafka, NiFi, ES, Prometheus, Grafana, Vault, Docker/K8s, network segmentation
- [[data-ingestion-integration]] — event schema, Kafka topics, NiFi flows, DLQ, lineage
- [[asset-repository]] — data model, PostgreSQL schema, CRUD APIs, reconciliation, audit
- [[cmdb]] — data model, schema, CI CRUD, relationships, topology, impact analysis

**Critical path**: ~27.5 hari single-threaded / 15-18 hari dengan 2 parallel teams

### Phase 2: Intelligence, Automation & Presentation (30 tasks, 5 blocks)
- [[web-dashboard]] — React/Vue, API gateway, RBAC/SSO, NOC/SOC views
- [[siem-soc]] — Wazuh/Syslog, correlation, compliance
- [[analytics-ai-engine]] — time-series pipeline, anomaly, predictive, RCA
- [[workflow-automation]] — state machine, ITSM, approval, runbook, remediation
- [[external-integration]] — adapter pattern, ITSM/ERP/DMS/NMS/Cloud connectors

## Non-Negotiables

### Data Quality
Mandatory fields, type/range/format validation, referential integrity, duplicate prevention, missing value handling, data lineage, error tagging, DLQ handling, reprocessing strategy

### Security
TLS 1.2+, RBAC, least privilege, vault/secrets, token protection, audit trail, data classification, encryption at rest, no plaintext credentials

### Reliability
HA/no SPOF, failover, idempotency, retry with backoff, DLQ, backup/restore, RTO/RPO, monitoring, graceful degradation

## Authority Model
1. Owner (MASTER) — otoritas tertinggi
2. Hermes DCIM Orchestrator — koordinasi agent system
3. Specialist agents — execute dalam role boundaries
4. Project source documents — primary truth

## Open Questions
- Timeline kickoff belum ditentukan
- Environment production vs staging belum didefinisikan
- Tim development belum diidentifikasi

## Related
- [[infrastructure-provisioning]]
- [[data-ingestion-integration]]
- [[cmdb]]
- [[asset-repository]]
- [[service-catalog]]
- [[dcim-component-comparison]]
- [[dcim-platform-comparison]]
- [[dcim-implementation-checklist]]
- [[dcim-technology-decisions]]
