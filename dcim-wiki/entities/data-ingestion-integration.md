---
title: Data Ingestion & Integration
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [dii, kafka, nifi, data-quality, architecture]
sources: []
confidence: high
---

# Data Ingestion & Integration (DI&I)

Single gateway untuk semua data masuk ke DCIM platform.

## Fungsi
- Ingest dari semua source systems
- Normalize, cleanse, validate, enrich
- Route ke core data stores berdasarkan priority dan data type
- Support real-time, near-real-time, dan batch processing

## Source Systems
- **BMS/EPMS/EMS**: Building Management, Electrical Power, Energy Management
- **NMS**: Network Management System
- **Server & Storage Monitoring**: CPU, memory, disk, I/O
- **Virtualization/Cloud**: VMware, KVM, AWS, GCP, Azure
- **Access Control/Surveillance**: badge, CCTV
- **ITSM/ERP/DMS**: ticketing, finance, document management

## Protocol & Ingestion Methods
- REST API, SNMP (v2c/v3), Modbus, MQTT
- Syslog, SSH, JDBC/ODBC
- SFTP/FTPS (batch files)

## Processing Pipeline
1. **Validation**: schema check, type check, range check
2. **Cleansing**: missing value handling, format normalization
3. **Normalization**:统一 event schema
4. **Enrichment**: add CI reference, location, priority metadata
5. **Routing**: direct to CMDB, Asset, time-series, SIEM

## Kafka Topic Structure
- `dcim.events.raw` — raw events from all sources
- `dcim.events.validated` — events passed validation
- `dcim.events.enriched` — events with CI/asset metadata
- `dcim.events.dlq` — dead letter queue
- `dcim.cmdb.updates` — CI create/update events
- `dcim.asset.updates` — asset create/update events

## Data Quality Controls
- Schema validation setiap event
- Mandatory fields: timestamp, source_system, event_type, payload
- Duplicate detection via event_id + source_system
- DLQ handling dengan retry mechanism
- Data lineage tracking: source → validation → enrichment → store
- Enrichment status tracking

## Technology Stack
- [[kafka]] — message broker, 3 brokers, KRaft
- [[nifi]] — data flow orchestration
- Flink — stream processing (optional)
- Python — custom processors

## Phase 1 Tasks (Block 2)
- Normalized event schema design
- Kafka topic structure
- NiFi integration: BMS/EPMS, NMS, Server/storage, Virtualization/cloud, Access control/surveillance
- Validation, enrichment, normalization
- DLQ handling
- Data lineage tracking
- ITSM/ERP/DMS connectors

## Related
- [[dcim-core-platform]]
- [[cmdb]] — receives CI updates
- [[asset-repository]] — receives asset updates
- [[kafka]]
- [[nifi]]
- [[data-quality-runbook]]
- [[dcim-data-flow-architecture]]
