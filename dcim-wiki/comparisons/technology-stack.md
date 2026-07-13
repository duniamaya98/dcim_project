---
title: Technology Stack
created: 2026-06-23
updated: 2026-06-23
type: comparison
tags: [comparison, architecture]
sources: []
confidence: high
---

# Technology Stack

Complete technology stack untuk DCIM platform.

## Infrastructure
- **Compute**: VM/container (4vCPU, 16GB RAM, 200GB SSD)
- **Containerization**: Docker Compose / Kubernetes
- **Network**: VLAN segmentation, firewall rules

## Data Stores
- **Relational**: PostgreSQL 16
- **Cache**: Redis 7
- **Search/Analytics**: Elasticsearch 8.x / OpenSearch 2.x
- **Time-Series**: TimescaleDB / InfluxDB

## Messaging
- **Broker**: Kafka 3.x (3 brokers, KRaft)
- **ETL**: Apache NiFi 1.x
- **Stream Processing**: Flink (optional)

## Application
- **Backend**: Python/Go
- **Frontend**: React/Vue
- **API Gateway**: Kong/NGINX/Traefik

## Monitoring
- **Metrics**: Prometheus
- **Visualization**: Grafana
- **Logging**: Elasticsearch
- **Tracing**: Jaeger (optional)

## Security
- **Secret Management**: HashiCorp Vault
- **Authentication**: SSO/MFA
- **Authorization**: RBAC
- **SIEM**: Wazuh

## Workflow
- **Automation**: n8n / Temporal
- **Ticketing**: ServiceNow / Jira integration

## Analytics & AI
- **Models**: Isolation Forest, Prophet, LSTM
- **Explanation**: LLM/RAG layer
- **Training**: Offline pipeline

## Related
- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[database-technology-comparison]]
- [[monitoring-stack-comparison]]
