---
title: "DCIM Core Platform — Deployment & Implementation Guide"
created: 2026-06-30
updated: 2026-06-30
type: guide
status: draft
tags: [deployment, implementation, guide, siem-soar, infrastructure, devops, kafka, nifi, message-broker]
sources:
  - reference-designs/siem-soar.md
  - reference-designs/siem-soar-actual-architecture.md
  - concepts/deployment-runbook.md
  - plans/implementation-plan.md
  - technical-requirements/siem-soar-uac.md
  - concepts/siem-soar-sla-prioritization-framework-final.md
confidence: high
purpose: >
  Comprehensive deployment & implementation guide untuk DCIM Core Platform.
  Step-by-step deployment instructions, verification procedures, rollback steps,
  dan troubleshooting guide berdasarkan actual architecture + reference design.
  Includes Apache Kafka 3.x (KRaft mode) as message broker and Apache NiFi
  as data flow processor for production-grade event streaming.
---

# DCIM Core Platform — Deployment & Implementation Guide

> **Purpose:** Panduan deployment & implementation komprehensif untuk DCIM Core Platform.
> **Cara pakai:** Ikuti phase-by-phase. Verifikasi setiap step sebelum lanjut.
> **Based on:** Actual architecture (Wazuh + Kafka + NiFi + ES + Kibana) + Reference Design (siem-soar.md)
> **Architecture Diagram:** `../reference-designs/diagrams/block6-siem-soc-architecture.html`

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Prerequisites](#2-prerequisites)
3. [Environment Setup](#3-environment-setup)
4. [Phase A — Infrastructure & Foundation](#4-phase-a--infrastructure--foundation)
5. [Phase B — SIEM Core (Wazuh + Kafka + ES + Kibana)](#5-phase-b--siem-core-wazuh--kafka--es--kibana)
6. [Phase C — Data Flow (NiFi + Kafka Streams)](#6-phase-c--data-flow-nifi--kafka-streams)
7. [Phase D — Alert Bridge (ElastAlert on Kafka)](#7-phase-d--alert-bridge-elastalert-on-kafka)
8. [Phase E — SOAR Platform (TraceCat + DFIR-IRIS)](#8-phase-e--soar-platform-tracecat--dfir-iris)
9. [Phase F — Enrichment & Integration](#9-phase-f--enrichment--integration)
10. [Phase G — Security Hardening](#10-phase-g--security-hardening)
11. [Phase H — Monitoring & Observability](#11-phase-h--monitoring--observability)
12. [Phase I — Documentation & Training](#12-phase-i--documentation--training)
13. [Verification & Acceptance Criteria](#13-verification--acceptance-criteria)
14. [Rollback Procedures](#14-rollback-procedures)
15. [Troubleshooting](#15-troubleshooting)
16. [Reference Documents](#16-reference-documents)

---

## 1. Architecture Overview

### 1.1 Target Stack (with Kafka + NiFi)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                       DCIM SIEM/SOAR Platform                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────────────┐                                                              │
│  │   Wazuh      │                                                              │
│  │   Manager    │──┐                                                           │
│  │   (3 nodes)  │  │                                                           │
│  └──────────────┘  │                                                           │
│                     │                                                           │
│                     ▼                                                           │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │              Apache Kafka 3.x (KRaft Mode — 3 Brokers)                  │  │
│  │                                                                          │  │
│  │  dcim.siem.events       ← Wazuh raw events                             │  │
│  │  dcim.siem.alerts       ← ElastAlert processed alerts                   │  │
│  │  dcim.siem.cases        ← DFIR-IRIS case updates                        │  │
│  │  dcim.siem.actions      ← SOAR automated actions                        │  │
│  │  dcim.siem.enrichment   ← Enriched events (NiFi output)                │  │
│  └──────────┬──────────┬──────────┬──────────┬──────────┬──────────────────┘  │
│             │          │          │          │          │                       │
│             ▼          ▼          ▼          ▼          ▼                       │
│  ┌─────────────┐ ┌───────────┐ ┌─────────┐ ┌─────────────┐ ┌──────────────┐  │
│  │ Apache NiFi  │ │ElastAlert │ │   ES    │ │  TraceCat   │ │   Archive    │  │
│  │ (Data Flow)  │ │ (Alerts)  │ │(Kibana) │ │  (SOAR)     │ │  (Cold Stor) │  │
│  └──────┬──────┘ └─────┬─────┘ └────┬────┘ └──────┬──────┘ └──────────────┘  │
│         │               │            │              │                           │
│         ▼               ▼            ▼              ▼                           │
│  ┌──────────────────────────────────────────────────────────────────────┐      │
│  │  Enrichment Pipeline                                                │      │
│  │  NiFi → AbuseIPDB / VirusTotal / MISP → dcim.siem.enrichment      │      │
│  └──────────────────────────────────────────────────────────────────────┘      │
│                     │                                                           │
│                     ▼                                                           │
│  ┌──────────────────────────────────────┐                                      │
│  │           TraceCat (SOAR)            │                                      │
│  │  ┌────────────┐  ┌────────────────┐  │                                      │
│  │  │  Temporal   │  │  AI Agent      │  │                                      │
│  │  │  (built-in) │  │  (Gemma/Local) │  │                                      │
│  │  └────────────┘  └────────────────┘  │                                      │
│  └──────────────────┬───────────────────┘                                      │
│                     │                                                           │
│         ┌───────────┼───────────┐                                              │
│         ▼           ▼           ▼                                              │
│  ┌────────────┐ ┌────────┐ ┌──────────┐                                       │
│  │  AbuseIPDB │ │VirusTotal│ │ DFIR-IRIS│                                     │
│  │  (Enrich)  │ │(Enrich) │ │ (Case)   │                                      │
│  └────────────┘ └────────┘ └──────────┘                                       │
│                                                                                 │
│  ┌──────────────────────────────────────────────────────────────────────────┐  │
│  │  Authentik (OIDC/SSO)  │  Prometheus  │  Grafana                        │  │
│  └──────────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow Architecture

```
                    ┌─────────────┐
                    │  Wazuh      │
                    │  Agents     │
                    └──────┬──────┘
                           │ Syslog (TCP/1514)
                           ▼
                    ┌─────────────┐
                    │  Wazuh      │
                    │  Manager    │
                    └──────┬──────┘
                           │ Wazuh Output Plugin → Kafka Producer
                           ▼
              ┌────────────────────────────┐
              │     Apache Kafka 3.x       │
              │     (KRaft Mode)           │
              │                            │
              │  Topic: dcim.siem.events   │──── consumers below
              └──┬────────┬────────┬───┬───┘
                 │        │        │   │
    ┌────────────┘   ┌────┘   ┌───┘   └──────────────┐
    ▼                ▼        ▼                       ▼
┌────────┐    ┌─────────┐ ┌────────┐          ┌────────────┐
│  NiFi  │    │ElastAlert│ │  ES   │          │  Archive   │
│        │    │         │ │Kibana │          │ (S3/HDFS)  │
└───┬────┘    └────┬────┘ └───┬────┘          └────────────┘
    │              │           │
    │              ▼           │
    │       ┌──────────┐      │
    │       │  TraceCat│      │
    │       │  (SOAR)  │      │
    │       └──────────┘      │
    ▼
┌──────────────────┐
│ Enrichment       │
│ (AbuseIPDB, VT)  │──→ dcim.siem.enrichment → ES / Archive
└──────────────────┘
```

### 1.3 Component Summary

| Component | Technology | Role | Cluster Size |
|-----------|-----------|------|-------------|
| SIEM Core | Wazuh 4.7+ | Log collection, detection | 3 nodes |
| Message Broker | Apache Kafka 3.x (KRaft) | Event streaming backbone | 3 brokers |
| Data Flow | Apache NiFi | Enrichment, routing, transformation | 1 node (dev) / 3 (prod) |
| Search & Analytics | Elasticsearch 8.x | Log storage, search, dashboards | 3 nodes |
| Dashboard | Kibana 8.x | Visualization | 1 node |
| Alert Bridge | ElastAlert 2.x | Detection rules → Kafka alerts | 1 instance |
| SOAR | TraceCat + Temporal | Playbook orchestration | 1 node |
| Case Management | DFIR-IRIS | Incident cases | 1 node |
| Auth | Authentik | OIDC/SSO | 1 node |
| Monitoring | Prometheus + Grafana | Metrics & dashboards | 1+1 |

### 1.4 Kafka Topic Design

| Topic | Purpose | Partitions | Replication | Retention | Producers | Consumers |
|-------|---------|-----------|-------------|-----------|-----------|-----------|
| `dcim.siem.events` | Raw security events from Wazuh | 6 | 3 | 7 days | Wazuh Manager | NiFi, ElastAlert, ES Archive |
| `dcim.siem.alerts` | Correlated alerts from ElastAlert | 3 | 3 | 30 days | ElastAlert | TraceCat, ES |
| `dcim.siem.cases` | Case updates from DFIR-IRIS | 3 | 3 | 90 days | DFIR-IRIS | Kafka → Dashboard |
| `dcim.siem.actions` | SOAR action results from TraceCat | 3 | 3 | 30 days | TraceCat | ES, Audit Log |
| `dcim.siem.enrichment` | Enriched events from NiFi | 6 | 3 | 14 days | Apache NiFi | ES, PostgreSQL Archive |

### 1.5 Reference Design Stack

| Component | Reference | Actual | Status |
|-----------|-----------|--------|--------|
| SIEM Core | Wazuh + Kafka + NiFi + ES | Wazuh + Kafka + NiFi + ES | ✅ Match |
| Alert Bridge | Kafka consumer | ElastAlert (Kafka consumer mode) | ✅ Match |
| SOAR | TraceCat + Temporal | TraceCat (built-in Temporal) | ✅ Match |
| ITSM | IRIS | DFIR-IRIS | ✅ Match |
| Enrichment | MISP + AbuseIPDB + VirusTotal | AbuseIPDB + VirusTotal (NiFi-enriched) | ⚠️ Partial |
| AI Agent | MCP (Claude/Codex) | Lokal Gemma (Unsloth) | ✅ Match |
| OIDC/SSO | Keycloak | Authentik | ✅ Match |
| Network | 3 VLANs | VLAN setup | ✅ Match |
| Monitoring | Prometheus + Grafana | Prometheus + Grafana | ✅ Match |
| Secrets | Vault | Manual config | ❌ Missing |
| HA | Docker Swarm (3 nodes) | Single instances | ❌ Missing |

---

## 2. Prerequisites

### 2.1 Hardware Requirements

| Component | Dev/Staging | Production |
|-----------|-------------|------------|
| **Wazuh Manager (×3)** | 4 vCPU, 8 GB RAM, 100 GB SSD | 8+ vCPU, 16+ GB RAM, 200+ GB SSD |
| **Kafka Brokers (×3)** | 8 vCPU, 16 GB RAM, 200 GB SSD | 25+ vCPU, 64+ GB RAM, 500+ GB SSD |
| **NiFi** | 4 vCPU, 8 GB RAM, 100 GB SSD | 8+ vCPU, 16+ GB RAM, 200+ GB SSD |
| **Elasticsearch (×3)** | 4 vCPU, 16 GB RAM, 200 GB SSD | 8+ vCPU, 32+ GB RAM, 1+ TB SSD |
| **TraceCat** | 4 vCPU, 8 GB RAM, 100 GB SSD | 8+ vCPU, 16+ GB RAM, 200+ GB SSD |
| **DFIR-IRIS** | 2 vCPU, 4 GB RAM, 50 GB SSD | 4+ vCPU, 8+ GB RAM, 100+ GB SSD |
| **Authentik** | 2 vCPU, 4 GB RAM, 50 GB SSD | 4+ vCPU, 8+ GB RAM, 100+ GB SSD |
| **Prometheus + Grafana** | 2 vCPU, 4 GB RAM, 100 GB SSD | 4+ vCPU, 8+ GB RAM, 500+ GB SSD |
| **PostgreSQL** | 2 vCPU, 4 GB RAM, 100 GB SSD | 4+ vCPU, 16+ GB RAM, 500+ GB SSD |
| **Redis** | 2 vCPU, 2 GB RAM, 50 GB SSD | 4+ vCPU, 8+ GB RAM, 100+ GB SSD |

**Minimum Production Cluster (all services):** 100+ vCPU, 256+ GB RAM, 5+ TB SSD

### 2.2 Software Requirements

| Software | Version | Purpose |
|----------|---------|---------|
| Docker | 24.0+ | Container runtime |
| Docker Compose | 2.20+ | Multi-container orchestration |
| PostgreSQL | 16+ | Primary database |
| Redis | 7+ | Caching, session store |
| Elasticsearch | 8.x | Search & analytics |
| Wazuh Manager | 4.7+ | SIEM core |
| **Apache Kafka** | **3.7+** | **Message broker (KRaft mode)** |
| **Apache NiFi** | **1.26+** | **Data flow processor** |
| Kibana | 8.x | Dashboard |
| ElastAlert | 2.x | Alert bridge (Kafka consumer mode) |
| TraceCat | Latest | SOAR platform |
| DFIR-IRIS | Latest | Case management |
| Authentik | Latest | OIDC/SSO |
| Prometheus | 2.x | Metrics collection |
| Grafana | 10+ | Dashboard visualization |

### 2.3 Network Requirements

| Port | Service | Protocol | Direction |
|------|---------|----------|-----------|
| 5601 | Kibana | HTTPS | Inbound |
| 9200 | Elasticsearch | HTTPS | Internal |
| 1514 | Wazuh Manager | TCP/UDP | Inbound |
| 1515 | Wazuh Registration | TCP | Inbound |
| 55000 | Wazuh API | HTTPS | Internal |
| **9092** | **Kafka Broker** | **TCP** | **Internal** |
| **9093** | **Kafka Controller** | **TCP** | **Internal** |
| **8080** | **NiFi Web UI** | **HTTPS** | **Internal** |
| 443 | TraceCat UI | HTTPS | Inbound |
| 8081 | TraceCat API | HTTPS | Internal |
| 4443 | DFIR-IRIS | HTTPS | Inbound |
| 5432 | PostgreSQL | TCP | Internal |
| 6379 | Redis | TCP | Internal |
| 9000 | Authentik | HTTP | Internal |
| 9443 | Authentik | HTTPS | Internal |
| 9090 | Prometheus | HTTP | Internal |
| 3000 | Grafana | HTTPS | Internal |

---

## 3. Environment Setup

### 3.1 Directory Structure

```bash
# Create deployment directory
mkdir -p /opt/dcim/{config,data,logs,backups}
cd /opt/dcim

# Create subdirectories
mkdir -p {wazuh,kafka,nifi,elasticsearch,kibana,elastalert,tracecat,iris,authentik,prometheus,grafana}

# Create Kafka-specific directories
mkdir -p /opt/dcim/kafka/{config,data-0,data-1,data-2,logs}
mkdir -p /opt/dcim/nifi/{config,flow,logs}
```

### 3.2 Environment Variables

```bash
# /opt/dcim/.env
COMPOSE_PROJECT_NAME=dcim
TZ=Asia/Jakarta

# PostgreSQL
POSTGRES_DB=dcim
POSTGRES_USER=dcim_admin
POSTGRES_PASSWORD=<USE_VAULT_IN_PRODUCTION>

# Elasticsearch
ES_JAVA_OPTS="-Xms2g -Xmx2g"
ELASTIC_PASSWORD=<USE_VAULT_IN_PRODUCTION>

# Wazuh
WAZUH_API_PASSWORD=<USE_VAULT_IN_PRODUCTION>

# Kafka
KAFKA_VERSION=3.7.0
KAFKA_BROKER_ID_1=1
KAFKA_BROKER_ID_2=2
KAFKA_BROKER_ID_3=3
KAFKA_ZOOKEEPER_CONNECT=""  # Not used in KRaft mode
KAFKA_CLUSTER_ID="MkU3OEVBNTcwNTJENDM2Qk"
KAFKA_ADMIN_PASSWORD=<USE_VAULT_IN_PRODUCTION>

# NiFi
NIFI_WEB_HTTP_PORT=8080
NIFI_WEB_HTTP_HOST=0.0.0.0

# Authentik
AUTHENTIK_SECRET_KEY=<USE_VAULT_IN_PRODUCTION>
AUTHENTIK_BOOTSTRAP_PASSWORD=<USE_VAULT_IN_PRODUCTION>

# TraceCat
TRACECAT__DB_CONNECTOR=postgresql
TRACECAT__DB_URI=postgresql://dcim_admin:***@postgres:5432/dcim
```

### 3.3 Docker Compose Base

```yaml
# /opt/dcim/docker-compose.yml
version: '3.8'

services:
  # === Infrastructure ===
  postgres:
    image: postgres:16-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # === Kafka Cluster (KRaft Mode) ===
  kafka-broker-1:
    image: apache/kafka:3.7.0
    container_name: kafka-broker-1
    hostname: kafka-broker-1
    ports:
      - "9092:9092"
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-broker-1:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-broker-1:9093,2@kafka-broker-2:9093,3@kafka-broker-3:9093
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      CLUSTER_ID: ${KAFKA_CLUSTER_ID}
      KAFKA_NUM_PARTITIONS: 6
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
      KAFKA_LOG_RETENTION_CHECK_INTERVAL_MS: 300000
      KAFKA_JMX_PORT: 9999
      KAFKA_JMX_OPTS: "-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false"
    volumes:
      - kafka_broker_1_data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD-SHELL", "kafka-broker-api-versions --bootstrap-server localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 10
      start_period: 30s

  kafka-broker-2:
    image: apache/kafka:3.7.0
    container_name: kafka-broker-2
    hostname: kafka-broker-2
    ports:
      - "9093:9092"
    environment:
      KAFKA_NODE_ID: 2
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-broker-2:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-broker-1:9093,2@kafka-broker-2:9093,3@kafka-broker-3:9093
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      CLUSTER_ID: ${KAFKA_CLUSTER_ID}
      KAFKA_NUM_PARTITIONS: 6
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_JMX_PORT: 9999
      KAFKA_JMX_OPTS: "-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false"
    volumes:
      - kafka_broker_2_data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD-SHELL", "kafka-broker-api-versions --bootstrap-server localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 10
      start_period: 30s

  kafka-broker-3:
    image: apache/kafka:3.7.0
    container_name: kafka-broker-3
    hostname: kafka-broker-3
    ports:
      - "9094:9092"
    environment:
      KAFKA_NODE_ID: 3
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-broker-3:9092
      KAFKA_CONTROLLER_LISTENER_NAMES: CONTROLLER
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-broker-1:9093,2@kafka-broker-2:9093,3@kafka-broker-3:9093
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      CLUSTER_ID: ${KAFKA_CLUSTER_ID}
      KAFKA_NUM_PARTITIONS: 6
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_JMX_PORT: 9999
      KAFKA_JMX_OPTS: "-Dcom.sun.management.jmxremote -Dcom.sun.management.jmxremote.authenticate=false -Dcom.sun.management.jmxremote.ssl=false"
    volumes:
      - kafka_broker_3_data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD-SHELL", "kafka-broker-api-versions --bootstrap-server localhost:9092"]
      interval: 10s
      timeout: 10s
      retries: 10
      start_period: 30s

  # === Data Flow Processor ===
  nifi:
    image: apache/nifi:1.26.0
    container_name: nifi
    ports:
      - "8080:8080"
    environment:
      SINGLE_USER_CREDENTIALS_USERNAME: admin
      SINGLE_USER_CREDENTIALS_PASSWORD: ${NIFI_PASSWORD}
      NIFI_WEB_HTTP_PORT: 8080
    volumes:
      - nifi_data:/opt/nifi/nifi-current
      - ./nifi/flow:/opt/nifi/flow
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8080/nifi-api/flow/process-groups/root || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 10
      start_period: 60s

  # === SIEM Core ===
  wazuh-manager:
    image: wazuh/wazuh-manager:4.7
    volumes:
      - wazuh_api_configuration:/var/ossec/api/configuration
      - wazuh_etc:/var/ossec/etc
      - wazuh_logs:/var/ossec/logs
    ports:
      - "1514:1514"
      - "1515:1515"
      - "55000:55000"

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.12.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=true
      - xpack.security.http.ssl.enabled=false
      - ES_JAVA_OPTS=${ES_JAVA_OPTS}
    volumes:
      - es_data:/usr/share/elasticsearch/data
    ports:
      - "9200:9200"

  kibana:
    image: docker.elastic.co/kibana/kibana:8.12.0
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"

  # === Alert Bridge (Kafka Consumer Mode) ===
  elastalert:
    image: jertel/elastalert2:latest
    volumes:
      - ./elastalert/config.yaml:/opt/elastalert/config.yaml
      - ./elastalert/rules:/opt/elastalert/rules
    depends_on:
      - kafka-broker-1
      - kafka-broker-2
      - kafka-broker-3

  # === SOAR ===
  tracecat:
    image: ghcr.io/tracecat-dev/tracecat:latest
    environment:
      - TRACECAT__DB_URI=${TRACECAT__DB_URI}
    ports:
      - "443:443"
      - "8081:8080"
    depends_on:
      - postgres
      - redis

  iris:
    image: dfir-iris/iriswebapp-docker:latest
    ports:
      - "4443:4443"
    depends_on:
      - postgres

  # === Security ===
  authentik:
    image: ghcr.io/goauthentik/server:latest
    environment:
      - AUTHENTIK_SECRET_KEY=${AUTHENTIK_SECRET_KEY}
      - AUTHENTIK_BOOTSTRAP_PASSWORD=${AUTHENTIK_BOOTSTRAP_PASSWORD}
    ports:
      - "9000:9000"
      - "9443:9443"

  # === Monitoring ===
  prometheus:
    image: prom/prometheus:latest
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - ./prometheus/alerts.yml:/etc/prometheus/alerts.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana:latest
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards
      - ./grafana/provisioning:/etc/grafana/provisioning
    ports:
      - "3000:3000"

volumes:
  postgres_data:
  redis_data:
  es_data:
  grafana_data:
  wazuh_api_configuration:
  wazuh_etc:
  wazuh_logs:
  kafka_broker_1_data:
  kafka_broker_2_data:
  kafka_broker_3_data:
  nifi_data:
```

---

## 4. Phase A — Infrastructure & Foundation

### A1. Deploy PostgreSQL

```bash
# Start PostgreSQL
docker compose up -d postgres

# Verify
docker compose exec postgres psql -U dcim_admin -d dcim -c "SELECT version();"

# Expected: PostgreSQL 16.x
```

### A2. Deploy Redis

```bash
# Start Redis
docker compose up -d redis

# Verify
docker compose exec redis redis-cli -a ${REDIS_PASSWORD} ping

# Expected: PONG
```

### A3. Network Verification

```bash
# Test connectivity between services
docker compose exec postgres ping -c 3 redis
docker compose exec redis ping -c 3 postgres

# Verify DNS resolution
docker compose exec postgres nslookup elasticsearch
docker compose exec postgres nslookup kafka-broker-1
docker compose exec postgres nslookup kafka-broker-2
docker compose exec postgres nslookup kafka-broker-3
```

**✅ Gate A Complete:** PostgreSQL + Redis running, network connectivity verified.

---

## 5. Phase B — SIEM Core (Wazuh + Kafka + ES + Kibana)

### B1. Deploy Elasticsearch

```bash
# Start Elasticsearch
docker compose up -d elasticsearch

# Wait for cluster health
sleep 30

# Verify cluster health
curl -u elastic:${ELASTIC_PASSWORD} \
  "http://localhost:9200/_cluster/health?pretty"

# Expected: "status" : "green" or "yellow" (single node)
```

### B2. Deploy Wazuh Manager

```bash
# Start Wazuh Manager
docker compose up -d wazuh-manager

# Verify Wazuh API
curl -k -u admin:${WAZUH_API_PASSWORD} \
  "https://localhost:55000/"

# Expected: Wazuh API version info
```

### B3. Deploy Kafka Cluster (KRaft Mode)

> **Important:** Kafka 3.x uses KRaft (Kafka Raft) mode — no ZooKeeper required.
> This is the recommended deployment mode for Kafka 3.4+.

#### B3.1 Start Kafka Brokers

```bash
# Start all 3 Kafka brokers
docker compose up -d kafka-broker-1 kafka-broker-2 kafka-broker-3

# Wait for cluster formation (KRaft mode needs ~30-60s)
echo "Waiting for Kafka cluster to form..."
sleep 60

# Verify cluster health from any broker
docker compose exec kafka-broker-1 kafka-metadata.sh --snapshot /var/lib/kafka/data/__cluster_metadata-0/00000000000000000000.log --cluster-id ${KAFKA_CLUSTER_ID}

# Expected: All 3 brokers listed as "alive"
```

#### B3.2 Verify Cluster

```bash
# Check broker list
docker compose exec kafka-broker-1 kafka-broker-api-versions.sh --bootstrap-server kafka-broker-1:9092 2>/dev/null | head -5

# Describe cluster
docker compose exec kafka-broker-1 kafka-metadata.sh --bootstrap-server kafka-broker-1:9092 --describe --cluster-id ${KAFKA_CLUSTER_ID}

# Expected: 3 brokers, all healthy
```

#### B3.3 Create Kafka Topics

```bash
# Create all 5 DCIM SIEM topics
docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --create \
  --topic dcim.siem.events \
  --partitions 6 \
  --replication-factor 3 \
  --config min.insync.replicas=2 \
  --config retention.ms=604800000 \
  --config cleanup.policy=delete \
  --config compression.type=lz4

docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --create \
  --topic dcim.siem.alerts \
  --partitions 3 \
  --replication-factor 3 \
  --config min.insync.replicas=2 \
  --config retention.ms=2592000000 \
  --config cleanup.policy=delete \
  --config compression.type=lz4

docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --create \
  --topic dcim.siem.cases \
  --partitions 3 \
  --replication-factor 3 \
  --config min.insync.replicas=2 \
  --config retention.ms=7776000000 \
  --config cleanup.policy=compact,delete \
  --config compression.type=lz4

docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --create \
  --topic dcim.siem.actions \
  --partitions 3 \
  --replication-factor 3 \
  --config min.insync.replicas=2 \
  --config retention.ms=2592000000 \
  --config cleanup.policy=delete \
  --config compression.type=lz4

docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --create \
  --topic dcim.siem.enrichment \
  --partitions 6 \
  --replication-factor 3 \
  --config min.insync.replicas=2 \
  --config retention.ms=1209600000 \
  --config cleanup.policy=delete \
  --config compression.type=lz4
```

#### B3.4 Verify Topics

```bash
# List all topics
docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --list

# Expected:
# dcim.siem.actions
# dcim.siem.alerts
# dcim.siem.cases
# dcim.siem.enrichment
# dcim.siem.events

# Describe topics
docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --describe

# Expected: All topics with 3 replicas, min.insync.replicas=2
```

#### B3.5 Test Produce/Consume

```bash
# Test produce
docker compose exec kafka-broker-1 kafka-console-producer.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --topic dcim.siem.events \
  <<< '{"event_id":"test-001","timestamp":"2026-06-30T00:00:00Z","source":"wazuh","rule":{"id":"5712","description":"Brute force"}}'

# Test consume
docker compose exec kafka-broker-1 kafka-console-consumer.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --topic dcim.siem.events \
  --from-beginning \
  --timeout-events 5 \
  --max-messages 1

# Expected: {"event_id":"test-001",...}
```

### B4. Configure Wazuh Output to Kafka

```bash
# Add Kafka output plugin to Wazuh configuration
# Edit /var/ossec/etc/ossec.conf on Wazuh Manager

cat > /tmp/wazuh-kafka-output.xml << 'EOF'
<ossec_config>
  <global>
    <jsonout_output>yes</jsonout_output>
  </global>

  <output>
    <name>kafka-output</name>
    <type>kafka</type>
    <disabled>no</disabled>
    <host>kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092</host>
    <topic>dcim.siem.events</topic>
    <version>0.10</version>
    <compression_type>lz4</compression_type>
    <max_block_ms>500</max_block_ms>
    <linger_ms>5</linger_ms>
    <batch_size>16384</batch_size>
    <send_timeout>5000</send_timeout>
  </output>
</ossec_config>
EOF

# Copy to Wazuh container
docker cp /tmp/wazuh-kafka-output.xml dcim-wazuh-manager-1:/var/ossec/etc/ossec.conf

# Restart Wazuh Manager
docker compose restart wazuh-manager

# Verify Kafka output in logs
docker compose logs -f wazuh-manager | grep -i kafka

# Expected: No errors, connection established
```

### B5. Deploy Kibana

```bash
# Start Kibana
docker compose up -d kibana

# Wait for Kibana to be ready
sleep 60

# Verify
curl -s "http://localhost:5601/api/status" | jq .status.overall

# Expected: "available"
```

### B6. Configure Security Event Schema

```bash
# Create normalized event index template
curl -X PUT "http://localhost:9200/_index_template/dcim-security-events" \
  -u elastic:${ELASTIC_PASSWORD} \
  -H 'Content-Type: application/json' \
  -d '{
    "index_patterns": ["dcim-security-events-*"],
    "template": {
      "settings": {
        "number_of_shards": 3,
        "number_of_replicas": 1,
        "index.lifecycle.name": "dcim-security-events-policy"
      },
      "mappings": {
        "properties": {
          "timestamp": {"type": "date"},
          "source": {"type": "keyword"},
          "event_type": {"type": "keyword"},
          "severity": {"type": "keyword"},
          "source_ip": {"type": "ip"},
          "destination_ip": {"type": "ip"},
          "user": {"type": "keyword"},
          "action": {"type": "keyword"},
          "outcome": {"type": "keyword"},
          "raw_event": {"type": "text"},
          "kafka_topic": {"type": "keyword"},
          "kafka_partition": {"type": "integer"},
          "kafka_offset": {"type": "long"},
          "enrichment": {"type": "object"}
        }
      }
    }
  }'
```

### B7. Configure ILM Policy

```bash
# Create ILM policy
curl -X PUT "http://localhost:9200/_ilm/policy/dcim-security-events-policy" \
  -u elastic:${ELASTIC_PASSWORD} \
  -H 'Content-Type: application/json' \
  -d '{
    "policy": {
      "phases": {
        "hot": {
          "min_age": "0ms",
          "actions": {
            "rollover": {
              "max_primary_shard_size": "50gb",
              "max_age": "7d"
            }
          }
        },
        "warm": {
          "min_age": "7d",
          "actions": {
            "shrink": {"number_of_shards": 1},
            "forcemerge": {"max_num_segments": 1}
          }
        },
        "cold": {
          "min_age": "30d",
          "actions": {
            "freeze": {}
          }
        },
        "delete": {
          "min_age": "90d",
          "actions": {
            "delete": {}
          }
        }
      }
    }
  }'
```

### B8. Install Wazuh Agents

```bash
# On each target server:
curl -sO https://packages.wazuh.com/4.7/wazuh-agent_4.7.0-1_amd64.deb
sudo dpkg -i ./wazuh-agent_4.7.0-1_amd64.deb

# Configure agent
sudo sed -i 's/<address>MANAGER_IP<\/address>/address>10.70.0.27<\/address/' /var/ossec/etc/ossec.conf
sudo sed -i 's/<protocol>udp<\/protocol>/protocol>tcp<\/protocol>/' /var/ossec/etc/ossec.conf

# Start agent
sudo systemctl enable wazuh-agent
sudo systemctl start wazuh-agent

# Verify on Wazuh Manager
curl -k -u admin:${WAZUH_API_PASSWORD} \
  "https://localhost:55000/agents?pretty"
```

### B9. Verify Wazuh → Kafka Pipeline

```bash
# Check events in Kafka topic from Wazuh
docker compose exec kafka-broker-1 kafka-console-consumer.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --topic dcim.siem.events \
  --timeout-events 10 \
  --max-messages 3

# Expected: JSON events from Wazuh agents

# Check topic metrics
docker compose exec kafka-broker-1 kafka-run-class.sh kafka.tools.GetOffsetShell \
  --broker-list kafka-broker-1:9092 \
  --topic dcim.siem.events \
  --time -1

# Expected: Non-zero offset count (events being produced)
```

**✅ Gate B Complete:** Elasticsearch cluster green, Kafka cluster healthy (3 brokers), Wazuh Manager running with Kafka output, Kibana accessible, agents connected, events flowing to `dcim.siem.events`.

---

## 6. Phase C — Data Flow (NiFi + Kafka Streams)

### C1. Configure NiFi

#### C1.1 NiFi Flow Configuration

```xml
<!-- /opt/dcim/nifi/flow/dcim-pipeline-flow.xml -->
<!-- Apache NiFi flow for DCIM SIEM event processing -->

<processGroup id="dcim-pipeline" name="DCIM SIEM Pipeline">
  <!-- Consume from Kafka: dcim.siem.events -->
  <processor id="consume-kafka" type="org.apache.nifi.processors.kafka.ConsumeKafka_2_6">
    <property name="Kafka Brokers">kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092</property>
    <property name="Topic Names">dcim.siem.events</property>
    <property name="Consumer Group">dcim-nifi-events-consumer</property>
    <property name="Offset Reset">latest</property>
    <property name="Record Reader">JsonTreeReader</property>
    <property name="Record Writer">JsonRecordSetWriter</property>
  </processor>

  <!-- Enrich: AbuseIPDB lookup -->
  <processor id="enrich-abuseipdb" type="org.apache.nifi.processors.standard.InvokeHTTP">
    <property name="HTTP Method">GET</property>
    <property name="Remote URL">https://api.abuseipdb.com/api/v2/check?ipAddress=${srcip}</property>
    <property name="Header Key 1">Key</property>
    <property name="Header Value 1">${env:ABUSEIPDB_KEY}</property>
    <property name="Header Key 2">Accept</property>
    <property name="Header Value 2">application/json</property>
  </processor>

  <!-- Enrich: VirusTotal lookup -->
  <processor id="enrich-virustotal" type="org.apache.nifi.processors.standard.InvokeHTTP">
    <property name="HTTP Method">GET</property>
    <property name="Remote URL">https://www.virustotal.com/api/v3/ip_addresses/${srcip}</property>
    <property name="Header Key 1">x-apikey</property>
    <property name="Header Value 1">${env:VIRUSTOTAL_KEY}</property>
  </processor>

  <!-- Merge enrichment data -->
  <processor id="merge-enrichment" type="org.apache.nifi.processors.standard.MergeContent">
    <property name="Maximum Entries">50</property>
    <property name="Timeout">5 secs</property>
  </processor>

  <!-- Produce to Kafka: dcim.siem.enrichment -->
  <processor id="produce-enrichment" type="org.apache.nifi.processors.kafka.PublishKafka_2_6">
    <property name="Kafka Brokers">kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092</property>
    <property name="Topic Name">dcim.siem.enrichment</property>
    <property name="Use Transactions">true</property>
    <property name="Record Reader">JsonTreeReader</property>
    <property name="Record Writer">JsonRecordSetWriter</property>
  </processor>

  <!-- Route high-severity alerts -->
  <processor id="route-severity" type="org.apache.nifi.processors.standard.RouteOnAttribute">
    <property name="high_severity">${severity:equals('high') || severity:equals('critical')}</property>
    <property name="medium_severity">${severity:equals('medium')}</property>
  </processor>

  <!-- Produce to Kafka: dcim.siem.alerts -->
  <processor id="produce-alerts" type="org.apache.nifi.processors.kafka.PublishKafka_2_6">
    <property name="Kafka Brokers">kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092</property>
    <property name="Topic Name">dcim.siem.alerts</property>
  </processor>

  <!-- Put to Elasticsearch -->
  <processor id="put-es" type="org.apache.nifi.processors.elasticsearch.PutElasticsearchHttp">
    <property name="Elasticsearch URL">http://elasticsearch:9200</property>
    <property name="Index">dcim-security-events-${now():format('yyyy.MM.dd')}</property>
    <property name="Type">_doc</property>
  </processor>
</processGroup>
```

#### C1.2 Import Flow to NiFi

```bash
# Import the flow configuration
docker compose exec nifi curl -X POST \
  -H "Content-Type: application/json" \
  -d @/opt/nifi/flow/dcim-pipeline-flow.json \
  http://localhost:8080/nifi-api/flow/process-groups/root

# Or via NiFi UI: Access http://localhost:8080/nifi
# Import flow template via UI
```

### C2. Start NiFi

```bash
# Start NiFi
docker compose up -d nifi

# Wait for NiFi to be ready
sleep 60

# Verify NiFi API
docker compose exec nifi curl -s http://localhost:8080/nifi-api/flow/process-groups/root | jq .processGroupFlow.id

# Expected: process group ID (root)
```

### C3. Verify NiFi Data Flow

```bash
# Check NiFi processor status via API
docker compose exec nifi curl -s http://localhost:8080/nifi-api/flow/process-groups/root | jq '.processGroupFlow.processGroups[] | {id: .id, name: .name, running: .runningCount}'

# Expected: dcim-pipeline running

# Verify events flowing through NiFi
# Check dcim.siem.enrichment topic for enriched events
docker compose exec kafka-broker-1 kafka-console-consumer.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --topic dcim.siem.enrichment \
  --timeout-events 10 \
  --max-messages 2

# Expected: Enriched event JSON with abuseipdb/virustotal data
```

**✅ Gate C Complete:** NiFi deployed, data flow configured, enriched events flowing to `dcim.siem.enrichment`.

---

## 7. Phase D — Alert Bridge (ElastAlert on Kafka)

### D1. Configure ElastAlert for Kafka

```yaml
# /opt/dcim/elastalert/config.yaml
# ElastAlert 2.x — Kafka Consumer Mode

# Kafka configuration (replaces ES polling)
kafka_bootstrap_servers: "kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092"
kafka_group_id: "dcim-elastalert-consumer"
kafka_topic: "dcim.siem.events"
kafka_consumer_timeout: 10
kafka_auto_offset_reset: "latest"

# Elasticsearch (for rule queries and alert state)
es_host: elasticsearch
es_port: 9200
writeback_index: elastalert_status

# Alerting
alert_time_limit:
  days: 2
run_every:
  seconds: 30
buffer_time:
  minutes: 1

# TraceCat webhook output
alert:
  - "tracecat_alert"
tracecat_webhook_url: "https://tracecat:8080/api/webhooks/alerts"
tracecat_webhook_method: POST
```

### D2. Create Alert Rules

```yaml
# /opt/dcim/elastalert/rules/brute_force_kafka.yaml
name: "Brute Force Detection (Kafka)"
type: frequency

# Consume from Kafka topic
kafka_topic: "dcim.siem.events"
kafka_group_id: "dcim-elastalert-brute-force"

num_events: 5
timeframe:
  minutes: 5

filter:
  - query:
      query_string:
        query: "rule.groups:authentication AND rule.id: 5712"

alert:
  - "tracecat_alert"

alert_subject: "Brute Force Detected from {0}"
alert_subject_args:
  - "srcip"

tracecat_webhook_url: "https://tracecat:8080/api/webhooks/alerts"
tracecat_webhook_method: POST
```

```yaml
# /opt/dcim/elastalert/rules/malware_detection_kafka.yaml
name: "Malware Detection (Kafka)"
type: frequency

kafka_topic: "dcim.siem.events"
kafka_group_id: "dcim-elastalert-malware"

num_events: 1
timeframe:
  minutes: 1

filter:
  - query:
      query_string:
        query: "rule.groups:malware"

alert:
  - "tracecat_alert"

alert_subject: "Malware Detected: {0}"
alert_subject_args:
  - "rule.description"

tracecat_webhook_url: "https://tracecat:8080/api/webhooks/alerts"
tracecat_webhook_method: POST
```

```yaml
# /opt/dcim/elastalert/rules/privilege_escalation_kafka.yaml
name: "Privilege Escalation (Kafka)"
type: frequency

kafka_topic: "dcim.siem.events"
kafka_group_id: "dcim-elastalert-privesc"

num_events: 3
timeframe:
  minutes: 10

filter:
  - query:
      query_string:
        query: "rule.groups:syslog AND rule.id: 5904"

alert:
  - "tracecat_alert"

alert_subject: "Privilege Escalation Attempt from {0}"
alert_subject_args:
  - "srcip"

tracecat_webhook_url: "https://tracecat:8080/api/webhooks/alerts"
tracecat_webhook_method: POST
```

### D3. Deploy ElastAlert

```bash
# Start ElastAlert
docker compose up -d elastalert

# Verify
docker compose logs elastalert | grep -i "running\|started\|kafka"

# Expected: "ElastAlert 2.x.x started" + Kafka consumer connected

# Verify Kafka consumer group
docker compose exec kafka-broker-1 kafka-consumer-groups.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --group dcim-elastalert-consumer \
  --describe

# Expected: Consumer group active, consuming from dcim.siem.events
```

**✅ Gate D Complete:** ElastAlert running in Kafka consumer mode, rules loaded, alerts flowing to TraceCat via `dcim.siem.alerts`.

---

## 8. Phase E — SOAR Platform (TraceCat + DFIR-IRIS)

### E1. Deploy TraceCat

```bash
# Start TraceCat
docker compose up -d tracecat

# Verify
curl -k "https://localhost:443/health" | jq .

# Expected: {"status": "healthy"}
```

### E2. Deploy DFIR-IRIS

```bash
# Start DFIR-IRIS
docker compose up -d iris

# Verify
curl -k "https://localhost:4443/health" | jq .

# Expected: {"status": "healthy"}
```

### E3. Configure Playbooks

```yaml
# /opt/dcim/tracecat/playbooks/brute-force-response.yaml
name: Brute Force Response
description: Auto-respond to brute force attacks
version: 1.0.0

triggers:
  - type: webhook
    path: /alerts/brute-force
  - type: kafka
    topic: dcim.siem.alerts
    consumer_group: tracecat-brute-force-consumer

steps:
  - id: enrich
    type: action
    action: http_request
    config:
      url: "https://api.abuseipdb.com/api/v2/check"
      method: GET
      headers:
        Key: "{{ secrets.ABUSEIPDB_KEY }}"
      params:
        ipAddress: "{{ trigger.srcip }}"

  - id: risk_score
    type: action
    action: python
    config:
      code: |
        abuse_score = enrich.response.data.abuseConfidenceScore
        if abuse_score >= 80:
          return {"risk": "high", "action": "block"}
        elif abuse_score >= 50:
          return {"risk": "medium", "action": "monitor"}
        else:
          return {"risk": "low", "action": "log"}

  - id: contain
    type: action
    action: http_request
    config:
      url: "https://firewall/api/block"
      method: POST
      body:
        ip: "{{ trigger.srcip }}"
        reason: "Brute force detection"
    condition: "{{ risk_score.action == 'block' }}"

  - id: create_case
    type: action
    action: http_request
    config:
      url: "https://iris:4443/api/cases"
      method: POST
      body:
        title: "Brute Force - {{ trigger.srcip }}"
        severity: "{{ risk_score.risk }}"
        alert_source: "DCIM SIEM"

  - id: publish_action
    type: action
    action: kafka_producer
    config:
      brokers: "kafka-broker-1:9092,kafka-broker-2:9092,kafka-broker-3:9092"
      topic: dcim.siem.actions
      message:
        action: "block_ip"
        target_ip: "{{ trigger.srcip }}"
        risk: "{{ risk_score.risk }}"
        timestamp: "{{ now() }}"

  - id: notify
    type: action
    action: send_notification
    config:
      channels:
        - type: email
          to: soc@dcim.local
        - type: slack
          channel: "#soc-alerts"
      message: "Brute force detected from {{ trigger.srcip }}. Risk: {{ risk_score.risk }}"
```

### E4. Configure TraceCat Webhook

```bash
# Register webhook with TraceCat API
curl -X POST "https://tracecat:8080/api/webhooks" \
  -H "Authorization: Bearer ${TRAC...EY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "alert-bridge",
    "path": "/alerts",
    "method": "POST",
    "auth": {
      "type": "api_key",
      "header": "X-API-Key"
    }
  }'
```

### E5. Verify Kafka → TraceCat Integration

```bash
# Manually send test alert to Kafka
docker compose exec kafka-broker-1 kafka-console-producer.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --topic dcim.siem.alerts \
  <<< '{"alert_id":"test-001","severity":"high","srcip":"192.168.1.100","rule":{"description":"Brute force test"}}'

# Check TraceCat for received alert
curl -k "https://tracecat:8080/api/alerts" \
  -H "Authorization: Bearer ${TRAC...EY}" | jq .

# Expected: Alert received by TraceCat

# Verify action published to Kafka
docker compose exec kafka-broker-1 kafka-console-consumer.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --topic dcim.siem.actions \
  --timeout-events 10 \
  --max-messages 1

# Expected: Action JSON with action details
```

**✅ Gate E Complete:** TraceCat + DFIR-IRIS running, playbooks configured with Kafka integration, webhooks active, actions publishing to `dcim.siem.actions`.

---

## 9. Phase F — Enrichment & Integration

### F1. AbuseIPDB Integration

```bash
# Configure in TraceCat
curl -X POST "https://tracecat:8080/api/enrichments" \
  -H "Authorization: Bearer ${TRAC...EY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "abuseipdb",
    "type": "http",
    "config": {
      "base_url": "https://api.abuseipdb.com/api/v2",
      "auth": {
        "type": "header",
        "header": "Key",
        "value": "{{ secrets.ABUSEIPDB_KEY }}"
      }
    }
  }'
```

### F2. VirusTotal Integration

```bash
curl -X POST "https://tracecat:8080/api/enrichments" \
  -H "Authorization: Bearer ${TRAC...EY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "virustotal",
    "type": "http",
    "config": {
      "base_url": "https://www.virustotal.com/api/v3",
      "auth": {
        "type": "header",
        "header": "x-apikey",
        "value": "{{ secrets.VIRUSTOTAL_KEY }}"
      }
    }
  }'
```

### F3. NiFi Enrichment Flow (Kafka → NiFi → Kafka)

```bash
# Verify NiFi enrichment pipeline
# NiFi consumes from dcim.siem.events → enriches → produces to dcim.siem.enrichment

# Check enrichment topic for enriched events
docker compose exec kafka-broker-1 kafka-console-consumer.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --topic dcim.siem.enrichment \
  --timeout-events 15 \
  --max-messages 2

# Expected: Enriched events with abuse_score, vt_score fields
```

### F4. CMDB Integration (iTop)

```bash
# Configure iTop connector in TraceCat
curl -X POST "https://tracecat:8080/api/connectors" \
  -H "Authorization: Bearer ${TRAC...EY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "itop-cmdb",
    "type": "http",
    "config": {
      "base_url": "https://itop.internal/itop",
      "auth": {
        "type": "basic",
        "username": "{{ secrets.ITOP_USER }}",
        "password": "{{ secrets.ITOP_PASS }}"
      }
    }
  }'
```

**✅ Gate F Complete:** Enrichment sources connected, NiFi enrichment pipeline verified, enriched events flowing to `dcim.siem.enrichment`.

---

## 10. Phase G — Security Hardening

### G1. Authentik OIDC/SSO

```bash
# Start Authentik
docker compose up -d authentik

# Access admin UI
# https://authentik.local:9443
# Default: admin / ${AUTHENTIK_BOOTSTRAP_PASSWORD}

# Create OIDC Application for TraceCat
# 1. Go to Applications → Applications
# 2. Create OIDC Provider
# 3. Set redirect URIs: https://tracecat.local/callback
# 4. Copy Client ID and Client Secret
```

### G2. TLS Configuration

```bash
# Generate self-signed certs (dev) or use Let's Encrypt (prod)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /opt/dcim/config/tls.key \
  -out /opt/dcim/config/tls.crt \
  -subj "/CN=dcim.local"

# Configure in docker-compose.yml for each service
# nginx/caddy reverse proxy with TLS termination
```

### G3. Secret Management

```bash
# For dev: Use .env file (NEVER commit to git)
# For production: Use HashiCorp Vault or Docker Secrets

# Create Docker secret
echo "${ELASTIC_PASSWORD}" | docker secret create elastic_password -
echo "${KAFKA_ADMIN_PASSWORD}" | docker secret create kafka_admin_password -

# Reference in docker-compose.yml
services:
  elasticsearch:
    secrets:
      - elastic_password
  kafka-broker-1:
    secrets:
      - kafka_admin_password
secrets:
  elastic_password:
    external: true
  kafka_admin_password:
    external: true
```

### G4. RBAC Configuration

```yaml
# Authentik RBAC Roles
roles:
  - name: analyst_l1
    permissions:
      - alert:read
      - alert:acknowledge
      - case:read

  - name: analyst_l2
    permissions:
      - alert:read
      - alert:acknowledge
      - alert:investigate
      - case:read
      - case:update

  - name: analyst_l3
    permissions:
      - alert:*
      - case:*
      - playbook:execute
      - containment:execute

  - name: soc_manager
    permissions:
      - alert:*
      - case:*
      - playbook:*
      - report:*
      - user:*

  - name: admin
    permissions:
      - "*"
```

**✅ Gate G Complete:** OIDC configured, TLS enabled, secrets secured, RBAC roles defined.

---

## 11. Phase H — Monitoring & Observability

### H1. Prometheus Configuration

```yaml
# /opt/dcim/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'wazuh'
    static_configs:
      - targets: ['wazuh-manager:55000']

  - job_name: 'kafka-brokers'
    static_configs:
      - targets: ['kafka-broker-1:9999', 'kafka-broker-2:9999', 'kafka-broker-3:9999']
    metrics_path: '/metrics'
    relabel_configs:
      - source_labels: [__address__]
        regex: '(.*):9999'
        target_label: broker

  - job_name: 'kafka-consumer-groups'
    static_configs:
      - targets: ['kafka-broker-1:9092']
    metrics_path: '/metrics'
    honor_labels: true

  - job_name: 'nifi'
    static_configs:
      - targets: ['nifi:8080']
    metrics_path: '/nifi-api/system-diagnostics'

  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['elasticsearch:9200']
    metrics_path: '/_metrics'

  - job_name: 'tracecat'
    static_configs:
      - targets: ['tracecat:8080']
    metrics_path: '/metrics'

  - job_name: 'iris'
    static_configs:
      - targets: ['iris:4443']

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
```

### H2. Grafana Dashboards

```bash
# Import pre-built dashboards
# Wazuh: https://grafana.com/grafana/dashboards/12489
# Elasticsearch: https://grafana.com/grafana/dashboards/14510
# Kafka: https://grafana.com/grafana/dashboards/7589
# NiFi: https://grafana.com/grafana/dashboards/12668
# Custom DCIM: /opt/dcim/grafana/dashboards/dcim-siem.json
```

### H3. Alert Rules

```yaml
# /opt/dcim/prometheus/alerts.yml
groups:
  - name: dcim-alerts
    rules:
      - alert: SIEMIngestionDrop
        expr: rate(wazuh_events_total[5m]) < 10
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "SIEM ingestion rate dropped below 10 events/sec"

      - alert: KafkaBrokerDown
        expr: up{job="kafka-brokers"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Kafka broker {{ $labels.instance }} is down"

      - alert: KafkaConsumerLagHigh
        expr: kafka_consumergroup_lag_sum > 100000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka consumer group {{ $labels.consumergroup }} lag exceeds 100K messages"

      - alert: KafkaReplicationFactor
        expr: kafka_topic_replication_factor < 3
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka topic {{ $labels.topic }} replication factor below 3"

      - alert: KafkaUnderReplicatedPartitions
        expr: kafka_server_replicamanager_underreplicatedpartitions > 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Kafka has under-replicated partitions"

      - alert: ElasticsearchClusterRed
        expr: elasticsearch_cluster_health_status{color="red"} == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Elasticsearch cluster is RED"

      - alert: NiFiFlowStopped
        expr: nifi_processor_running_count == 0
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "NiFi flow has no running processors"

      - alert: HighMTTR
        expr: avg_over_time(case_resolution_time_seconds[1h]) > 1800
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Average MTTR exceeds 30 minutes"
```

**✅ Gate H Complete:** Prometheus scraping Kafka + all services, Grafana dashboards loaded, alert rules active (Kafka-specific + infrastructure).

---

## 12. Phase I — Documentation & Training

### I1. Documentation Checklist

| Document | Status | Location |
|----------|--------|----------|
| Architecture Diagram | ✅ | `../reference-designs/diagrams/block6-siem-soc-architecture.html` |
| Deployment Guide | ✅ | This document |
| Kafka Operations Guide | ⬜ | `runbooks/kafka-operations-runbook.md` |
| NiFi Flow Documentation | ⬜ | `docs/nifi-flow-reference.md` |
| Operational Runbook | ⬜ | `runbooks/siem-operational-runbook.md` |
| Incident Response Playbook | ⬜ | `playbooks/ir-runbook.md` |
| SOC Onboarding Guide | ⬜ | `docs/soc-onboarding.md` |
| API Documentation | ⬜ | `docs/api-reference.md` |

### I2. Training Requirements

| Training | Audience | Duration | Status |
|----------|----------|----------|--------|
| Wazuh Administration | SOC L1/L2 | 2 days | ⬜ |
| **Kafka Operations & Monitoring** | **DevOps / SOC L2/L3** | **3 days** | ⬜ |
| **NiFi Flow Management** | **Data Engineers** | **2 days** | ⬜ |
| TraceCat Playbook Development | SOC L2/L3 | 3 days | ⬜ |
| Incident Response Procedures | All SOC | 1 day | ⬜ |
| Dashboard & Reporting | SOC Manager | 0.5 day | ⬜ |

**✅ Gate I Complete:** Documentation complete, team trained.

---

## 13. Verification & Acceptance Criteria

### 13.1 Infrastructure Health

| # | Criterion | Test | Expected | Status |
|---|-----------|------|----------|--------|
| 1 | PostgreSQL running | `docker compose ps postgres` | Up | ⬜ |
| 2 | Redis running | `docker compose exec redis redis-cli ping` | PONG | ⬜ |
| 3 | Elasticsearch healthy | `curl localhost:9200/_cluster/health` | green/yellow | ⬜ |
| 4 | Wazuh Manager running | `curl localhost:55000/` | API response | ⬜ |
| 5 | Kibana accessible | `curl localhost:5601/api/status` | available | ⬜ |

### 13.2 Kafka Cluster Health

| # | Criterion | Test | Expected | Status |
|---|-----------|------|----------|--------|
| 6 | All 3 brokers alive | `kafka-broker-api-versions --bootstrap-server kafka-broker-1:9092` | 3 brokers | ⬜ |
| 7 | Topics created (5 topics) | `kafka-topics --list` | 5 topics listed | ⬜ |
| 8 | Replication factor correct | `kafka-topics --describe` | RF=3, min.ISR=2 | ⬜ |
| 9 | Producer/Consumer working | Produce + consume test message | Message roundtrip | ⬜ |
| 10 | Consumer lag < 1000 | `kafka-consumer-groups --describe` | Lag < 1000 | ⬜ |

### 13.3 Data Ingestion

| # | Criterion | Test | Expected | Status |
|---|-----------|------|----------|--------|
| 11 | Agent connected | `curl localhost:55000/agents` | Agent listed | ⬜ |
| 12 | Events in Kafka topic | `kafka-console-consumer --topic dcim.siem.events` | Events visible | ⬜ |
| 13 | Events in Elasticsearch | Kibana → Discover | Events visible | ⬜ |
| 14 | NiFi processing events | NiFi UI → Processor status | Events flowing | ⬜ |

### 13.4 Detection & Alerting

| # | Criterion | Test | Expected | Status |
|---|-----------|------|----------|--------|
| 15 | ElastAlert consuming from Kafka | `kafka-consumer-groups --describe dcim-elastalert-consumer` | Consumer active | ⬜ |
| 16 | Brute force detection | Simulate 5 failed logins | Alert triggered in `dcim.siem.alerts` | ⬜ |
| 17 | Alert enrichment | Check alert details in TraceCat | AbuseIPDB data present | ⬜ |
| 18 | Playbook execution | Trigger brute-force playbook | Steps complete | ⬜ |
| 19 | Case created | Check DFIR-IRIS | Case with alert data | ⬜ |
| 20 | Action published | `kafka-console-consumer --topic dcim.siem.actions` | Action visible | ⬜ |

### 13.5 Security

| # | Criterion | Test | Expected | Status |
|---|-----------|------|----------|--------|
| 21 | OIDC login | Login via Authentik | SSO works | ⬜ |
| 22 | RBAC enforced | Try unauthorized action | Access denied | ⬜ |
| 23 | TLS working | `curl -k https://tracecat` | TLS handshake | ⬜ |
| 24 | Audit trail | Check audit logs | Actions logged | ⬜ |

### 13.6 Monitoring

| # | Criterion | Test | Expected | Status |
|---|-----------|------|----------|--------|
| 25 | Prometheus metrics | `curl localhost:9090/metrics` | Metrics present | ⬜ |
| 26 | Grafana dashboard | Access `localhost:3000` | Dashboard loaded | ⬜ |
| 27 | Alert rules active | Check Prometheus alerts | Rules loaded | ⬜ |

**Pass Criteria:** All 27 criteria must pass.

---

## 14. Rollback Procedures

### 14.1 Rollback Strategy

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROLLBACK DECISION TREE                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Issue detected                                                  │
│       │                                                          │
│       ▼                                                          │
│  ┌─────────────────┐    YES    ┌─────────────────────────────┐  │
│  │ Kafka broker    │──────────→│ Stop all, restart brokers,  │  │
│  │ down?           │           │ re-elect controller          │  │
│  └────────┬────────┘           └─────────────────────────────┘  │
│           │ NO                                                   │
│           ▼                                                      │
│  ┌─────────────────┐    YES    ┌─────────────────────────────┐  │
│  │ Service down?   │──────────→│ Stop all, restore from      │  │
│  └────────┬────────┘           │ backup, restart              │  │
│           │ NO                  └─────────────────────────────┘  │
│           ▼                                                      │
│  ┌─────────────────┐    YES    ┌─────────────────────────────┐  │
│  │ Data corruption?│──────────→│ Restore DB snapshot,        │  │
│  └────────┬────────┘           │ replay WAL                   │  │
│           │ NO                  └─────────────────────────────┘  │
│           ▼                                                      │
│  ┌─────────────────┐    YES    ┌─────────────────────────────┐  │
│  │ Config error?   │──────────→│ Revert config, restart      │  │
│  └────────┬────────┘           │ affected service             │  │
│           │ NO                  └─────────────────────────────┘  │
│           ▼                                                      │
│  ┌─────────────────┐    YES    ┌─────────────────────────────┐  │
│  │ Performance?    │──────────→│ Scale up, optimize queries, │  │
│  └─────────────────┘           │ check resources              │  │
│                                └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 14.2 Backup Commands

```bash
# Backup PostgreSQL
docker compose exec postgres pg_dump -U dcim_admin dcim > /opt/dcim/backups/dcim_$(date +%Y%m%d).sql

# Backup Elasticsearch
curl -X PUT "http://localhost:9200/_snapshot/backup/snapshot_$(date +%Y%m%d)?wait_for_completion=true"

# Backup Kafka offsets (export consumer group offsets)
docker compose exec kafka-broker-1 kafka-consumer-groups.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --group dcim-elastalert-consumer \
  --reset-offsets \
  --to-latest \
  --dry-run \
  --topic dcim.siem.events

# Backup NiFi flow
docker compose exec nifi curl -X GET http://localhost:8080/nifi-api/flow/process-groups/root \
  -o /opt/dcim/backups/nifi-flow-$(date +%Y%m%d).json

# Backup configs
tar -czf /opt/dcim/backups/config_$(date +%Y%m%d).tar.gz /opt/dcim/config/ /opt/dcim/elastalert/ /opt/dcim/nifi/
```

### 14.3 Restore Commands

```bash
# Restore PostgreSQL
docker compose exec -T postgres psql -U dcim_admin dcim < /opt/dcim/backups/dcim_YYYYMMDD.sql

# Restore Elasticsearch
curl -X POST "http://localhost:9200/_snapshot/backup/snapshot_YYYYMMDD/_restore"

# Kafka rollback — recreate topics (data lost, re-ingest from Wazuh)
docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --delete \
  --topic dcim.siem.events

# Re-create topic (see B3.3)
docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --create \
  --topic dcim.siem.events \
  --partitions 6 \
  --replication-factor 3 \
  --config min.insync.replicas=2

# Full stack rollback
docker compose down
tar -xzf /opt/dcim/backups/config_YYYYMMDD.tar.gz -C /
docker compose up -d
```

### 14.4 Kafka-Specific Rollback

```bash
# If Kafka cluster is unhealthy:
# 1. Stop all Kafka brokers
docker compose stop kafka-broker-1 kafka-broker-2 kafka-broker-3

# 2. Clear corrupted data (CAUTION: loses all Kafka data)
rm -rf /opt/dcim/kafka/data-{0,1,2}/*

# 3. Restart brokers (KRaft will re-initialize)
docker compose up -d kafka-broker-1 kafka-broker-2 kafka-broker-3

# 4. Wait for cluster formation
sleep 60

# 5. Re-create topics
# Follow B3.3 steps to recreate all 5 topics

# 6. Verify cluster health
docker compose exec kafka-broker-1 kafka-broker-api-versions.sh \
  --bootstrap-server kafka-broker-1:9092 | head -5
```

---

## 15. Troubleshooting

### 15.1 Common Issues

| Issue | Symptom | Diagnosis | Fix |
|-------|---------|-----------|-----|
| **Kafka broker won't start** | Container exits immediately | `docker compose logs kafka-broker-1` | Check KRaft config, CLUSTER_ID consistency, port conflicts |
| **Kafka controller election fails** | Only 1 broker active | `kafka-metadata.sh --describe` | Verify quorum voters, restart all brokers simultaneously |
| **Kafka topic not created** | Topic missing from list | `kafka-topics --list` | Check broker connectivity, re-run topic creation |
| **High consumer lag** | Alerts delayed, lag growing | `kafka-consumer-groups --describe` | Increase consumers, check consumer processing speed |
| **Kafka replication not working** | Under-replicated partitions | `kafka-topics --describe` | Check broker health, network, min.insync.replicas |
| **NiFi flow stopped** | No events processed | NiFi UI → processor status | Restart NiFi, check Kafka connection, verify credentials |
| **NiFi enrichment fails** | Enrichment topic empty | NiFi → bulletins | Check AbuseIPDB/VT API keys, rate limits |
| **Wazuh → Kafka not flowing** | No events in dcim.siem.events | `docker compose logs wazuh-manager` | Check Wazuh output config, Kafka broker connectivity |
| **ElastAlert not consuming** | No alerts in dcim.siem.alerts | `docker compose logs elastalert` | Check consumer group, topic permissions, offset reset |
| **Elasticsearch won't start** | Container exits immediately | `docker compose logs elasticsearch` | Check disk space, JVM heap, permissions |
| **Wazuh agent offline** | Agent not in list | `systemctl status wazuh-agent` | Check network, restart agent |
| **Kibana 502** | Cannot access dashboard | Check ES status | ES must be green before Kibana starts |
| **TraceCat webhook failing** | No alerts in TraceCat | Check webhook URL | Verify TLS, API key |
| **High memory usage** | OOM kills | `docker stats` | Increase limits, optimize queries |

### 15.2 Kafka Troubleshooting

#### Consumer Lag Investigation

```bash
# Check all consumer groups and their lag
docker compose exec kafka-broker-1 kafka-consumer-groups.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --describe \
  --group dcim-elastalert-consumer

# Reset consumer offsets (if needed)
docker compose exec kafka-broker-1 kafka-consumer-groups.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --group dcim-elastalert-consumer \
  --reset-offsets \
  --to-latest \
  --topic dcim.siem.events \
  --execute

# Check per-partition lag
docker compose exec kafka-broker-1 kafka-consumer-groups.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --describe \
  --group dcim-nifi-events-consumer
```

#### Kafka Broker Health Check

```bash
# Check broker status
docker compose exec kafka-broker-1 kafka-broker-api-versions.sh \
  --bootstrap-server kafka-broker-1:9092 2>/dev/null | head -5

# Check cluster metadata
docker compose exec kafka-broker-1 kafka-metadata.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --describe \
  --cluster-id ${KAFKA_CLUSTER_ID}

# Check disk usage per broker
docker compose exec kafka-broker-1 du -sh /var/lib/kafka/data/*

# Check topic partition distribution
docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --describe \
  --topic dcim.siem.events
```

#### Kafka Quick Fix Commands

```bash
# Delete stuck consumer group
docker compose exec kafka-broker-1 kafka-consumer-groups.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --delete \
  --group <group-id>

# Check topic config
docker compose exec kafka-broker-1 kafka-topics.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --describe \
  --topic dcim.siem.events \
  --topics-with-overrides

# Alter topic config
docker compose exec kafka-broker-1 kafka-configs.sh \
  --bootstrap-server kafka-broker-1:9092 \
  --entity-type topics \
  --entity-name dcim.siem.events \
  --alter \
  --add-config retention.ms=1209600000
```

### 15.3 Log Locations

| Service | Log Command |
|---------|-------------|
| PostgreSQL | `docker compose logs postgres` |
| Elasticsearch | `docker compose logs elasticsearch` |
| Wazuh | `docker compose logs wazuh-manager` |
| **Kafka Broker 1** | **`docker compose logs kafka-broker-1`** |
| **Kafka Broker 2** | **`docker compose logs kafka-broker-2`** |
| **Kafka Broker 3** | **`docker compose logs kafka-broker-3`** |
| **NiFi** | **`docker compose logs nifi`** |
| Kibana | `docker compose logs kibana` |
| ElastAlert | `docker compose logs elastalert` |
| TraceCat | `docker compose logs tracecat` |
| DFIR-IRIS | `docker compose logs iris` |
| Authentik | `docker compose logs authentik` |
| Prometheus | `docker compose logs prometheus` |
| Grafana | `docker compose logs grafana` |

### 15.4 Health Checks

```bash
# Quick health check all services
for svc in postgres redis elasticsearch wazuh-manager kafka-broker-1 kafka-broker-2 kafka-broker-3 nifi kibana elastalert tracecat iris authentik prometheus grafana; do
  status=$(docker compose ps $svc --format '{{.State}}')
  echo "$svc: $status"
done

# Expected: All "Up"

# Kafka-specific health check
for broker in kafka-broker-1 kafka-broker-2 kafka-broker-3; do
  echo "--- $broker ---"
  docker compose exec $broker kafka-broker-api-versions.sh \
    --bootstrap-server $broker:9092 2>/dev/null | head -3 || echo "UNREACHABLE"
done

# Expected: All 3 brokers responding
```

---

## 16. Reference Documents

| Document | Path | Purpose |
|----------|------|---------|
| SIEM SOAR Reference Design | `reference-designs/siem-soar.md` | Target architecture spec |
| Actual Architecture | `reference-designs/siem-soar-actual-architecture.md` | Current implementation |
| **Kafka Pipeline Architecture** | **`technical-requirements/kafka-pipeline-architecture.md`** | **Kafka topic & flow design** |
| **Layer 4 Storage & Delivery** | **`technical-requirements/layer-4-kafka-consumer.md`** | **Consumer patterns** |
| Deployment Runbook | `concepts/deployment-runbook.md` | Docker Compose deployment steps |
| Implementation Plan | `plans/implementation-plan.md` | Full DCIM implementation plan |
| UAC Document | `technical-requirements/siem-soar-uac.md` | 27 acceptance criteria |
| SLA Framework | `concepts/siem-soar-sla-prioritization-framework-final.md` | Priority & SLA model |
| Gap Analysis | `comparisons/siem-soar-gap-analysis.md` | Reference vs Actual gaps |
| Architecture Diagram | `../reference-designs/diagrams/block6-siem-soc-architecture.html` | Visual architecture |

---

## Appendix A: Quick Reference Commands

```bash
# Start all services
docker compose up -d

# Stop all services
docker compose down

# Restart a specific service
docker compose restart <service>

# View logs (live)
docker compose logs -f <service>

# Scale a service
docker compose up -d --scale <service>=3

# Execute command in container
docker compose exec <service> <command>

# Check disk usage
docker system df

# Prune unused resources
docker system prune -a

# --- Kafka Quick Commands ---
# List topics
docker compose exec kafka-broker-1 kafka-topics.sh --bootstrap-server kafka-broker-1:9092 --list

# Describe topics
docker compose exec kafka-broker-1 kafka-topics.sh --bootstrap-server kafka-broker-1:9092 --describe

# Check consumer groups
docker compose exec kafka-broker-1 kafka-consumer-groups.sh --bootstrap-server kafka-broker-1:9092 --describe

# Produce test message
docker compose exec kafka-broker-1 kafka-console-producer.sh --bootstrap-server kafka-broker-1:9092 --topic dcim.siem.events

# Consume messages
docker compose exec kafka-broker-1 kafka-console-consumer.sh --bootstrap-server kafka-broker-1:9092 --topic dcim.siem.events --from-beginning --timeout-events 10

# Check broker metrics
docker compose exec kafka-broker-1 kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list kafka-broker-1:9092 --topic dcim.siem.events --time -1

# --- NiFi Quick Commands ---
# Check NiFi status
docker compose exec nifi curl -s http://localhost:8080/nifi-api/flow/process-groups/root | jq .processGroupFlow.id

# Restart NiFi
docker compose restart nifi
```

## Appendix B: Port Reference

| Port | Service | Protocol | External? |
|------|---------|----------|-----------|
| 5601 | Kibana | HTTPS | Yes |
| 9200 | Elasticsearch | HTTPS | No |
| 1514 | Wazuh Agent | TCP/UDP | Yes |
| 1515 | Wazuh Registration | TCP | Yes |
| 55000 | Wazuh API | HTTPS | Yes |
| **9092** | **Kafka Broker 1** | **TCP** | **No** |
| **9093** | **Kafka Broker 2** | **TCP** | **No** |
| **9094** | **Kafka Broker 3** | **TCP** | **No** |
| **8080** | **NiFi Web UI** | **HTTPS** | **No** |
| 443 | TraceCat | HTTPS | Yes |
| 8081 | TraceCat API | HTTP | No |
| 4443 | DFIR-IRIS | HTTPS | Yes |
| 9000 | Authentik | HTTP | Yes |
| 9443 | Authentik | HTTPS | Yes |
| 5432 | PostgreSQL | TCP | No |
| 6379 | Redis | TCP | No |
| 9090 | Prometheus | HTTP | No |
| 3000 | Grafana | HTTPS | Yes |

## Appendix C: Kafka Topic Quick Reference

| Topic | Partitions | Replication | Retention | Cleanup |
|-------|-----------|-------------|-----------|---------|
| `dcim.siem.events` | 6 | 3 | 7 days | delete |
| `dcim.siem.alerts` | 3 | 3 | 30 days | delete |
| `dcim.siem.cases` | 3 | 3 | 90 days | compact,delete |
| `dcim.siem.actions` | 3 | 3 | 30 days | delete |
| `dcim.siem.enrichment` | 6 | 3 | 14 days | delete |

---

> **Status:** Draft — Ready for review
> **Date:** 2026-06-30
> **Author:** Hermes DCIM Orchestrator
> **Based on:** Actual architecture (Wazuh + Kafka + NiFi + ES) + Reference design + UAC + SLA framework
> **Total Phases:** 9 (A through I)
> **Total Acceptance Criteria:** 27
> **Key Changes:** Added Apache Kafka 3.x (KRaft mode), Apache NiFi data flow processor, Kafka topic design (5 topics), Kafka-specific deployment phase, Kafka monitoring & troubleshooting, updated data flow to Kafka-centric architecture
