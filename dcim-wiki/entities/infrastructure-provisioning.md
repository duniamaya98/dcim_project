---
title: Infrastructure Provisioning
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [infrastructure, docker, kubernetes, postgresql, redis, kafka, nifi, elasticsearch, prometheus, grafana, vault]
sources: []
confidence: high
---

# Infrastructure Provisioning

Foundation untuk seluruh DCIM platform.

## Requirements
- VM/container: 4vCPU, 16GB RAM, 200GB SSD
- Docker Compose / Kubernetes manifests
- Network segmentation: VLAN/firewall
- Base monitoring

## Components

### PostgreSQL 16
- Primary database untuk [[cmdb]] dan [[asset-repository]]
- Streaming replication untuk HA
- Backup: pg_basebackup + WAL archiving
- Connection pooling: PgBouncer

### Redis 7
- Cache layer untuk [[asset-repository]] enrichment API
- Session store
- Real-time pub/sub
- Sentinel untuk HA

### Kafka 3.x
- Message broker untuk [[data-ingestion-integration]]
- 3 brokers, KRaft (no ZooKeeper)
- Topics: dcim.events.raw, validated, enriched, dlq
- Replication factor: 3
- Min.insync.replicas: 2

### Apache NiFi 1.x
- Data flow orchestration
- Visual flow designer
- Source connectors: BMS, NMS, Server, Cloud
- Validation and enrichment processors

### Elasticsearch 8.x / OpenSearch 2.x
- Central logging
- SIEM data store
- Full-text search
- Index lifecycle management

### Prometheus
- Metrics collection
- Alert manager integration
- Service discovery
- Long-term storage: Thanos or Cortex

### Grafana
- Dashboard visualization
- Data source: Prometheus, Elasticsearch, PostgreSQL
- Alerting rules
- NOC/SOC/Facilities views

### HashiCorp Vault
- Secret management
- Dynamic credentials
- Encryption as a service
- Audit logging

## Network Architecture
- Management VLAN: 10.70.0.0/24
- Data VLAN: 10.70.1.0/24
- DMZ VLAN: 10.70.2.0/24
- Firewall rules: least privilege
- TLS 1.2+ all internal traffic

## Phase 1 Tasks (Block 1)
- VM/container provisioning
- PostgreSQL 16 setup + replication
- Redis 7 setup + Sentinel
- Kafka 3.x cluster (3 brokers, KRaft)
- NiFi 1.x deployment
- Elasticsearch 8.x cluster
- Prometheus + Grafana base
- Vault deployment
- Docker Compose / K8s manifests
- Network segmentation
- Base monitoring

## Related
- [[dcim-core-platform]]
- [[postgresql]]
- [[redis]]
- [[kafka]]
- [[nifi]]
- [[elasticsearch]]
- [[prometheus]]
- [[grafana]]
- [[vault]]
- [[network-architecture]]
- [[load-balancer-comparison]]
- [[service-discovery-comparison]]
- [[dcim-deployment-architecture]]
