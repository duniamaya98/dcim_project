---
title: "Block 1 — Infrastructure Provisioning: Reference Design Spec"
created: 2026-06-23
updated: 2026-06-23
type: reference-design
block: 1
phase: 1
status: generated
confidence: high
tags: [infrastructure, postgresql, redis, kafka, nifi, elasticsearch, prometheus, grafana, vault, docker, kubernetes, network, nvr, onvif, snmp]
wiki_pages:
  - infrastructure-provisioning
  - postgresql
  - redis
  - kafka
  - nifi
  - elasticsearch
  - prometheus
  - grafana
  - vault
  - network-architecture
  - dcim-deployment-architecture
purpose: >
  Reference design spec untuk Block 1 Infrastructure Provisioning.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Block 1 — Infrastructure Provisioning: Reference Design Spec

> **Purpose:** Dokumen referensi lengkap untuk seluruh komponen infrastruktur DCIM.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi aktual. Setiap gap dicatat sebagai connection point.
> **Architecture Diagram:** `diagrams/block1-infrastructure-architecture.html` — buka di browser untuk visualisasi interaktif.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Component 1: PostgreSQL 16](#2-component-1-postgresql-16)
3. [Component 2: Redis 7](#3-component-2-redis-7)
4. [Component 3: Kafka 3.x](#4-component-3-kafka-3x)
5. [Component 4: Apache NiFi 1.x](#5-component-4-apache-nifi-1x)
6. [Component 5: Elasticsearch 8.x](#6-component-5-elasticsearch-8x)
7. [Component 6: Prometheus](#7-component-6-prometheus)
8. [Component 7: Grafana](#8-component-7-grafana)
9. [Component 8: HashiCorp Vault](#9-component-8-hashicorp-vault)
10. [Network Architecture](#10-network-architecture)
11. [Deployment Strategy](#11-deployment-strategy)
12. [Base Monitoring & Alerting](#12-base-monitoring--alerting)
13. [Security Hardening](#13-security-hardening)
14. [Backup & Recovery](#14-backup--recovery)
15. [Sizing & Capacity](#15-sizing--capacity)
16. [Acceptance Criteria](#16-acceptance-criteria)
17. [Gap Comparison Template](#17-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌──────────────────────────────────────────────────────────┐
│                    DCIM Core Platform                    │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │PostgreSQL│  │  Redis   │  │  Kafka   │  │   NiFi   │  │
│  │  16      │  │    7     │  │  3.x     │  │   1.x    │  │
│  │ (primary)│  │(sentinel)│  │(3 broker)│  │          │  │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  │
│       │             │             │             │        │
│  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  ┌────┴─────┐  │
│  │PostgreSQL│  │  Redis   │  │  Kafka   │  │          │  │
│  │ (replica)│  │ (replica)│  │ (broker) │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │Elastic-  │  │Prometheus│  │ Grafana  │  │  Vault   │  │
│  │search 8.x│  │          │  │          │  │          │  │
│  │ (3 nodes)│  │          │  │          │  │          │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────────┐│
│  │              Network Layer (VLAN/Firewall)           ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘
```

### 1.2 Component Dependency Map

```
Vault ──────→ All services (secrets)
PostgreSQL ──→ CMDB, Asset Repository, Lineage, Workflow
Redis ──────→ Asset Enrichment Cache, Session Store, Real-time Pub/Sub
Kafka ──────→ DI&I Gateway, Analytics Pipeline, SIEM Ingestion
NiFi ───────→ Source System Connectors (BMS, NMS, Server, Cloud)
Elasticsearch → SIEM Store, Central Logging, Full-text Search
Prometheus ──→ All services (metrics)
Grafana ────→ Prometheus, Elasticsearch, PostgreSQL (dashboards)
NVR ────────→ ONVIF/SNMP/Syslog → NiFi → Kafka → Asset Repository
```

### 1b. NVR Infrastructure Notes

> **Full NVR integration spec:** `nvr-asset-repository-integration.md`
> **Architecture diagram:** `diagrams/nvr-asset-repository-integration.html`

| Requirement | Value | Notes |
|-------------|-------|-------|
| NVR VLAN | 10.70.2.0/24 | Separate from Management (10.70.0.0) and Data (10.70.1.0) |
| NVR Storage | 4 TB per NVR head unit | NAS/SAN for video retention |
| ONVIF Port | TCP 80/443 | NVR web management |
| RTSP Port | TCP 554 | Video streaming |
| SNMP Port | UDP 161 | Health monitoring |
| Syslog Port | UDP 5140 | Event forwarding |
| NiFi Connector | Dedicated flow | ONVIF discovery, SNMP poller, syslog receiver |
| Kafka Topics | 5 new topics | dcim.nvr.* (discovery, health, events, cameras, location) |

### 1.3 Minimum Hardware Requirements

> **Note:** NVR storage (4 TB per unit) is separate from DCIM infrastructure sizing above. See NVR Integration Spec for details.

| Component | vCPU | RAM | Storage | Network |
|-----------|------|-----|---------|---------|
| PostgreSQL (primary) | 2 | 8 GB | 100 GB SSD | 1 Gbps |
| PostgreSQL (replica) | 2 | 8 GB | 100 GB SSD | 1 Gbps |
| Redis (primary) | 1 | 4 GB | 20 GB SSD | 1 Gbps |
| Redis (replica) | 1 | 4 GB | 20 GB SSD | 1 Gbps |
| Kafka (3 brokers) | 2 each | 8 GB each | 200 GB SSD each | 1 Gbps |
| NiFi | 2 | 4 GB | 50 GB SSD | 1 Gbps |
| Elasticsearch (3 nodes) | 2 each | 8 GB each | 200 GB SSD each | 1 Gbps |
| Prometheus | 1 | 4 GB | 50 GB SSD | 1 Gbps |
| Grafana | 1 | 2 GB | 10 GB SSD | 1 Gbps |
| Vault | 1 | 2 GB | 20 GB SSD | 1 Gbps |
| NVR Storage (NAS) | — | — | 4 TB per NVR | 1 Gbps |
| **Total Minimum** | **~22** | **~80 GB** | **~1 TB** | — |

---

## 2. Component 1: PostgreSQL 16

### 2.1 Purpose

Primary relational database untuk [[cmdb]], [[asset-repository]], lineage tracking, dan workflow state.

### 2.2 Architecture

```
┌──────────────┐     streaming       ┌──────────────┐
│  PostgreSQL  │ ──── replication ──→│  PostgreSQL  │
│   Primary    │                     │   Replica    │
│  (read/write)│                     │  (read-only) │
└──────┬───────┘                     └──────────────┘
       │
       ▼
┌──────────────┐
│  PgBouncer   │ ← Connection Pooler
│  (port 6432) │
└──────────────┘
```

### 2.3 Configuration Spec

#### postgresql.conf (Primary)

```ini
# === Connection ===
listen_addresses = '*'
port = 5432
max_connections = 200

# === Memory ===
shared_buffers = 4GB                    # 50% of 8GB RAM
effective_cache_size = 12GB             # 75% of total RAM
work_mem = 16MB
maintenance_work_mem = 512MB
huge_pages = try

# === WAL & Replication ===
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1GB
hot_standby = on
synchronous_commit = on                 # P1 data integrity
synchronous_standby_names = 'replica1'

# === Checkpoint ===
checkpoint_timeout = 15min
checkpoint_completion_target = 0.9
max_wal_size = 4GB
min_wal_size = 1GB

# === Query Planning ===
random_page_cost = 1.1                  # SSD-optimized
effective_io_concurrency = 200          # SSD
default_statistics_target = 100

# === Logging ===
log_destination = 'stderr'
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d.log'
log_min_duration_statement = 1000       # Log slow queries >1s
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_line_prefix = '%m [%p] %q%u@%d '

# === Security ===
ssl = on
ssl_cert_file = '/etc/ssl/certs/server.crt'
ssl_key_file = '/etc/ssl/private/server.crt'
password_encryption = scram-sha-256

# === Autovacuum ===
autovacuum = on
autovacuum_max_workers = 3
autovacuum_naptime = 30s
```

#### pg_hba.conf

```ini
# TYPE  DATABASE    USER        ADDRESS         METHOD
local   all         all                         scram-sha-256
host    all         all         10.70.0.0/24    scram-sha-256
host    all         all         10.70.1.0/24    scram-sha-256
host    replication replica1    10.70.1.0/24    scram-sha-256
hostssl all         all         0.0.0.0/0       scram-sha-256
```

#### PgBouncer Configuration (pgbouncer.ini)

```ini
[databases]
dcim = host=postgres-primary port=5432 dbname=dcim

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = scram-sha-256
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 500
default_pool_size = 40
min_pool_size = 10
reserve_pool_size = 5
reserve_pool_timeout = 3
server_lifetime = 3600
server_idle_timeout = 600
log_connections = 1
log_disconnections = 1
stats_period = 60
```

### 2.4 Streaming Replication Setup

```sql
-- On PRIMARY: Create replication user
CREATE ROLE replica1 WITH REPLICATION LOGIN PASSWORD '<secure-password>';

-- On PRIMARY: Create standby signal
-- pg_basebackup -h primary -D /var/lib/postgresql/standby -U replica1 -Fp -Xs -P -R
```

#### recovery.conf / standby.signal (PostgreSQL 12+)

```ini
primary_conninfo = 'host=postgres-primary port=5432 user=replica1 password=<secure-password> application_name=replica1'
primary_slot_name = 'replica1_slot'
recovery_target_timeline = 'latest'
```

### 2.5 Database Initialization (init.sql)

```sql
-- Create databases
CREATE DATABASE dcim_cmdb;
CREATE DATABASE dcim_asset;
CREATE DATABASE dcim_lineage;
CREATE DATABASE dcim_workflow;

-- Create roles
CREATE ROLE dcim_app WITH LOGIN PASSWORD '<app-password>';
CREATE ROLE dcim_readonly WITH LOGIN PASSWORD '<readonly-password>';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE dcim_cmdb TO dcim_app;
GRANT ALL PRIVILEGES ON DATABASE dcim_asset TO dcim_app;
GRANT ALL PRIVILEGES ON DATABASE dcim_lineage TO dcim_app;
GRANT ALL PRIVILEGES ON DATABASE dcim_workflow TO dcim_app;

-- Read-only access
GRANT CONNECT ON DATABASE dcim_cmdb TO dcim_readonly;
GRANT USAGE ON SCHEMA public TO dcim_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO dcim_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO dcim_readonly;

-- Extensions
\c dcim_cmdb;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c dcim_asset;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
```

### 2.6 Backup Strategy

| Method | Frequency | Retention | RPO | RTO |
|--------|-----------|-----------|-----|-----|
| pg_basebackup | Daily 02:00 | 7 days | 24h | 30min |
| WAL archiving | Continuous | 7 days | 5min | 15min |
| pg_dump (logical) | Weekly Sun 01:00 | 30 days | 7 days | 1h |

```bash
# Daily base backup
pg_basebackup -h primary -D /backup/pg_base/$(date +%Y%m%d) -Ft -z -Xs -P

# WAL archiving (archive_command in postgresql.conf)
archive_command = 'cp %p /archive/wal/%f'
archive_timeout = 300                    # Force archive every 5min
```

### 2.7 Health Checks

```sql
-- Replication lag
SELECT client_addr, state, sent_lsn, write_lsn, replay_lsn,
       replay_lag FROM pg_stat_replication;

-- Connection count
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';

-- Database size
SELECT datname, pg_size_pretty(pg_database_size(datname)) FROM pg_database;

-- Table bloat
SELECT schemaname, relname, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables WHERE n_dead_tup > 10000 ORDER BY n_dead_tup DESC;
```

### 2.8 Prometheus Metrics

```yaml
# postgresql_exporter config
- targets: ['postgres-primary:9187']
  labels:
    role: primary
    env: production
- targets: ['postgres-replica:9187']
  labels:
    role: replica
    env: production
```

### 2.9 Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | PostgreSQL 16 running | `SELECT version();` |
| 2 | Streaming replication active | `pg_stat_replication` shows `streaming` |
| 3 | Replication lag < 1s | `replay_lag < 1 second` |
| 4 | SSL connections enforced | `ssl = on` in postgresql.conf |
| 5 | PgBouncer pooling active | `SHOW POOLS;` shows active clients |
| 6 | Backup completes | `pg_basebackup` exit code 0 |
| 7 | Failover works | Kill primary, replica promotes within 30s |
| 8 | Prometheus metrics flowing | `pg_up = 1` in Prometheus |

---

## 3. Component 2: Redis 7

### 3.1 Purpose

Cache layer untuk [[asset-repository]] enrichment API, session store, real-time pub/sub, dan rate limiting.

### 3.2 Architecture

```
┌──────────────┐     sentinel      ┌──────────────┐
│    Redis     │ ◄── monitoring ── │   Sentinel   │
│   Primary    │ ──── sync ──────→ │  (3 nodes)   │
│  (read/write)│                   └──────────────┘
└──────┬───────┘                          │
       │                                  │
       ▼                                  ▼
┌──────────────┐                   failover signal
│    Redis     │                   (automatic)
│   Replica    │
│  (read-only) │
└──────────────┘
```

### 3.3 Configuration Spec

#### redis.conf (Primary)

```ini
# === Network ===
bind 0.0.0.0
port 6379
protected-mode yes
requirepass <redis-primary-password>
masterauth <redis-primary-password>
tcp-backlog 511
timeout 300
tcp-keepalive 300

# === Memory ===
maxmemory 6gb
maxmemory-policy allkeys-lru
maxmemory-samples 10

# === Persistence ===
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# AOF
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# === Security ===
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
aclfile /etc/redis/acl.conf

# === Logging ===
loglevel notice
logfile /data/redis.log

# === Slow Log ===
slowlog-log-slower-than 10000
slowlog-max-len 128

# === Replication ===
replica-read-only yes
repl-diskless-sync yes
repl-diskless-sync-delay 5
repl-ping-replica-period 10
```

#### sentinel.conf

```ini
port 26379
sentinel monitor dcim-primary redis-primary 6379 2
sentinel auth-pass dcim-primary <redis-primary-password>
sentinel down-after-milliseconds dcim-primary 5000
sentinel failover-timeout dcim-primary 30000
sentinel parallel-syncs dcim-primary 1
sentinel resolve-hostnames yes
sentinel announce-hostnames yes
```

### 3.4 ACL Configuration (acl.conf)

```ini
# Default user - no access
user default on ><default-password> -@all

# Application user - full access to dcim:* namespace
user dcim_app on >dcim-secure-password +@all -FLUSHALL -FLUSHDB -DEBUG ~dcim:*

# Read-only user
user dcim_readonly on >readonly-password +@read ~dcim:*

# Monitoring user
user dcim_monitor on >monitor-password +info +ping +echo +role +memory +keyspace ~*
```

### 3.5 Key Schema

```
dcim:cache:asset:{asset_id}          → Hash (TTL: 1h)
dcim:cache:ci:{ci_id}                → Hash (TTL: 1h)
dcim:cache:enrichment:{asset_id}     → Hash (TTL: 30min)
dcim:session:{session_id}            → Hash (TTL: 8h)
dcim:ratelimit:{client_id}           → String (TTL: 1min)
dcim:pubsub:events                   → Channel (no TTL)
dcim:lock:reconciliation             → String (TTL: 5min, NX)
dcim:counter:events:{date}           → String (TTL: 24h)
```

### 3.6 Sentinel Topology

| Node | Host | Port | Role |
|------|------|------|------|
| sentinel-1 | redis-sentinel-1 | 26379 | Sentinel |
| sentinel-2 | redis-sentinel-2 | 26379 | Sentinel |
| sentinel-3 | redis-sentinel-3 | 26379 | Sentinel |
| redis-primary | redis-primary | 6379 | Master |
| redis-replica | redis-replica | 6379 | Replica |

### 3.7 Health Checks

```bash
# Ping
redis-cli -a <password> PING

# Replication info
redis-cli -a <password> INFO replication

# Memory usage
redis-cli -a <password> INFO memory | grep used_memory_human

# Sentinel status
redis-cli -p 26379 SENTINEL masters
redis-cli -p 26379 SENTINEL get-master-addr-by-name dcim-primary
```

### 3.8 Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | Redis primary running | `PING` → `PONG` |
| 2 | Sentinel monitoring active | `SENTINEL masters` shows dcim-primary |
| 3 | Failover works | Kill primary, replica promotes < 10s |
| 4 | ACL enforced | `dcim_readonly` cannot write |
| 5 | Persistence working | AOF file grows, RDB snapshots exist |
| 6 | Memory limit enforced | `maxmemory` reached → LRU eviction |
| 7 | Prometheus metrics flowing | `redis_up = 1` |

---

## 4. Component 3: Kafka 3.x

### 4.1 Purpose

Event streaming broker untuk [[data-ingestion-integration]], analytics pipeline, dan SIEM ingestion.

### 4.2 Architecture

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Kafka      │  │  Kafka      │  │  Kafka      │
│  Broker 1   │  │  Broker 2   │  │  Broker 3   │
│  (KRaft)    │  │  (KRaft)    │  │  (KRaft)    │
│  controller │  │  broker     │  │  broker     │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
              ┌─────────┴─────────┐
              │  Producers        │
              │  (NiFi, Apps)     │
              └───────────────────┘
              ┌───────────────────┐
              │  Consumers        │
              │  (Analytics, SIEM)│
              └───────────────────┘
```

### 4.3 KRaft Configuration

#### server.properties (Controller)

```properties
# Node identity
node.id=1
controller.quorum.voters=1@kafka-controller:9093,2@kafka-broker-2:9093,3@kafka-broker-3:9093

# Controller listener
controller.listener.names=CONTROLLER
listeners=PLAINTEXT://:9092,CONTROLLER://:9093
advertised.listeners=PLAINTEXT://kafka-controller:9092
listener.security.protocol.map=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT

# Log dirs
log.dirs=/var/lib/kafka/data
num.partitions=6
default.replication.factor=3
min.insync.replicas=2

# Retention
log.retention.hours=168                     # 7 days
log.retention.bytes=-1
log.segment.bytes=1073741824                # 1GB
log.cleanup.policy=delete

# Performance
num.network.threads=8
num.io.threads=16
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

# Security
allow.plaintext.listener.on.plaintext.port=true
# production: enable SASL_SSL
```

### 4.4 Topic Design

| Topic | Partitions | Replication | Retention | Cleanup | Purpose |
|-------|------------|-------------|-----------|---------|---------|
| `dcim.events.raw` | 6 | 3 | 7 days | delete | Raw events dari source systems |
| `dcim.events.validated` | 6 | 3 | 30 days | delete | Validated events |
| `dcim.events.enriched` | 6 | 3 | 90 days | delete | Enriched events (CI, location, priority) |
| `dcim.events.dlq` | 3 | 3 | 30 days | compact | Dead letter queue |
| `dcim.cmdb.updates` | 3 | 3 | 90 days | compact | CMDB change events |
| `dcim.asset.updates` | 3 | 3 | 90 days | compact | Asset change events |
| `dcim.siem.events` | 6 | 3 | 30 days | delete | Security events |
| `dcim.analytics.metrics` | 3 | 3 | 7 days | delete | Metrics for analytics |
| `dcim.workflow.events` | 3 | 3 | 30 days | delete | Workflow state changes |

#### Topic Creation Script

```bash
#!/bin/bash
BOOTSTRAP="kafka-controller:9092"

declare -A TOPICS=(
  ["dcim.events.raw"]="6:3:7d:delete"
  ["dcim.events.validated"]="6:3:30d:delete"
  ["dcim.events.enriched"]="6:3:90d:delete"
  ["dcim.events.dlq"]="3:3:30d:compact"
  ["dcim.cmdb.updates"]="3:3:90d:compact"
  ["dcim.asset.updates"]="3:3:90d:compact"
  ["dcim.siem.events"]="6:3:30d:delete"
  ["dcim.analytics.metrics"]="3:3:7d:delete"
  ["dcim.workflow.events"]="3:3:30d:delete"
)

for TOPIC in "${!TOPICS[@]}"; do
  IFS=':' read -r PARTITIONS REPLICATION RETENTION POLICY <<< "${TOPICS[$TOPIC]}"

  kafka-topics.sh --bootstrap-server $BOOTSTRAP \
    --create --if-not-exists \
    --topic $TOPIC \
    --partitions $PARTITIONS \
    --replication-factor $REPLICATION \
    --config retention.ms=$(echo $RETENTION | sed 's/d/*86400000/' | bc) \
    --config cleanup.policy=$POLICY \
    --config min.insync.replicas=2

  echo "Created topic: $TOPIC (P=$PARTITIONS, R=$REPLICATION)"
done
```

### 4.5 Producer Configuration

```yaml
bootstrap.servers: kafka-controller:9092
acks: all                               # Wait for all ISR
retries: 3
retry.backoff.ms: 1000
max.in.flight.requests.per.connection: 5
enable.idempotence: true                # Exactly-once semantics
compression.type: lz4
batch.size: 32768
linger.ms: 10
buffer.memory: 67108864                 # 64MB
```

### 4.6 Consumer Configuration

```yaml
bootstrap.servers: kafka-controller:9092
group.id: dcim-consumer-group
auto.offset.reset: earliest
enable.auto.commit: false               # Manual commit for reliability
max.poll.records: 500
max.poll.interval.ms: 300000
session.timeout.ms: 30000
heartbeat.interval.ms: 10000
fetch.min.bytes: 1
fetch.max.wait.ms: 500
```

### 4.7 Health Checks

```bash
# Cluster health
kafka-broker-api-versions.sh --bootstrap-server localhost:9092

# List topics
kafka-topics.sh --bootstrap-server localhost:9092 --list

# Describe topic
kafka-topics.sh --bootstrap-server localhost:9092 --topic dcim.events.raw --describe

# Consumer group status
kafka-consumer-groups.sh --bootstrap-server localhost:9092 --group dcim-consumer-group --describe

# Check under-replicated partitions
kafka-topics.sh --bootstrap-server localhost:9092 --describe --under-replicated-partitions
```

### 4.8 Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | 3 brokers running | `kafka-broker-api-versions` returns 3 nodes |
| 2 | KRaft mode (no ZK) | `process.roles` in server.properties |
| 3 | All topics created | `kafka-topics --list` shows 9 topics |
| 4 | min.insync.replicas=2 | `kafka-topics --describe` shows ISR ≥ 2 |
| 5 | Producer sends successfully | `kafka-console-producer` + verify |
| 6 | Consumer receives | `kafka-console-consumer` reads messages |
| 7 | Failover works | Kill 1 broker, cluster still serves |
| 8 | Prometheus metrics flowing | `kafka_up = 1` |

---

## 5. Component 4: Apache NiFi 1.x

### 5.1 Purpose

Data flow orchestration untuk [[data-ingestion-integration]]. Visual flow designer untuk source system connectors.

### 5.2 Architecture

```
┌────────────────────────────────────────────────┐
│                    Apache NiFi                 │
│                                                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ BMS/EPMS │  │   NMS    │  │  Server  │      │
│  │  Flow    │  │  Flow    │  │  Flow    │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │             │            │
│  ┌────┴─────────────┴─────────────┴─────┐      │
│  │         Validation Processor         │      │
│  └────────────────┬─────────────────────┘      │
│                   │                            │
│  ┌────────────────┴───────────────────────┐    │
│  │        Enrichment Processor            │    │
│  └────────────────┬───────────────────────┘    │
│                   │                            │
│  ┌────────────────┴───────────────────────┐    │
│  │         PublishKafka Processor         │    │
│  └────────────────┬───────────────────────┘    │
│                   │                            │
└───────────────────┼────────────────────────────┘
                    │
                    ▼
              ┌──────────┐
              │  Kafka   │
              │ dcim.events.raw
              └──────────┘
```

### 5.3 NiFi Configuration

#### nifi.properties

```properties
# === Web ===
nifi.web.http.host=0.0.0.0
nifi.web.http.port=8080
nifi.web.https.port=8443
nifi.web.https.host=0.0.0.0
nifi.web.jetty.work=./work/jetty

# === Security ===
nifi.sensitive.props.algorithm=NIFI_PBKDF2_AES_256_64
nifi.security.keystore=./conf/keystore.jks
nifi.security.keystoreType=JKS
nifi.security.keystorePasswd=<keystore-password>
nifi.security.keyPasswd=<key-password>
nifi.security.truststore=./conf/truststore.jks
nifi.security.truststoreType=JKS
nifi.security.truststorePasswd=<truststore-password>
nifi.security.needClientAuth=false

# === Cluster ===
nifi.cluster.is.node=false
nifi.cluster.node.address=
nifi.cluster.load平衡.port=6000

# === Flow Analysis ===
nifi.flowanalysis.enable=false

# === Provenance ===
nifi.provenance.repository.enable=true
nifi.provenance.repository.max.storage.size=8 GB
nifi.provenance.repository.rollover.time=10 mins
nifi.provenance.repository.rollover.size=100 MB

# === Content Repository ===
nifi.content.repository.implementation=org.apache.nifi.repository.content.FileSystemContentRepository
nifi.content.repository.max.storage.size=8 GB
nifi.content.repository.archive.max.storage.size=4 GB

# === FlowFile Repository ===
nifi.flowfile.repository.implementation=org.apache.nifi.repository.repository.VolatileFlowFileRepository
nifi.volatile.flowfile.repository.max.storage.size=64 MB

# === Site-to-Site ===
nifi.remote.input.host=
nifi.remote.input.secure=false

# === Performance ===
nifi.concurrent.scheduled.input.ports=2
nifi.scheduled.thread.pcore.count=4
nifi.scheduled.thread.pmax.count=8
nifi.scheduled.thread.pkeep.alive=30 secs
nifi.scheduled.thread.pallow.interrupt=true
```

### 5.4 Flow Design — BMS/EPMS

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐
│  GetHTTP    │───→│ JoltTransform│───→│ ValidateRecord│
│  (BMS API)  │    │   JSON       │    │ (JSON Schema) │
└─────────────┘    │ (normalize)  │    └───────┬───────┘
                   └──────────────┘            │
                                          ┌────┴────┐
                                          │ RouteOn │
                                          │  Status │
                                          └────┬────┘
                                         pass  │  fail
                                    ┌──────────┴──────────┐
                                    ▼                      ▼
                             ┌──────────────┐      ┌──────────┐
                             │ PublishKafka │      │ PutS3    │
                             │ dcim.events  │      │ (DLQ)    │
                             │ .raw         │      └──────────┘
                             └──────────────┘
```

#### NiFi Processors

| Processor | Class | Purpose |
|-----------|-------|---------|
| GetHTTP | org.apache.nifi.processors.standard.GetHTTP | Ingest from BMS REST API |
| GetSNMP | org.apache.nifi.processors.snmp.GetSNMP | Ingest from NMS via SNMP |
| GetFile | org.apache.nifi.processors.standard.GetFile | Ingest from file drops |
| ExecuteStreamCommand | org.apache.nifi.processors.standard.ExecuteStreamCommand | SSH-based collection |
| JoltTransformJSON | org.apache.nifi.processors.standard.JoltTransformJSON | Normalize payload |
| ValidateRecord | org.apache.nifi.processors.standard.ValidateRecord | Schema validation |
| RouteOnAttribute | org.apache.nifi.processors.standard.RouteOnAttribute | Route pass/fail |
| PublishKafka | org.apache.nifi.processors.kafka.PublishKafka_2_0 | Publish to Kafka |
| PutS3 | org.apache.nifi.processors.aws.s3.PutS3Object | Archive failed events |
| LogAttribute | org.apache.nifi.processors.standard.LogAttribute | Debug logging |

### 5.5 Error Handling

| Error Type | Handler | Retry | Max Attempts |
|------------|---------|-------|--------------|
| Connection timeout | Retry with backoff | Yes | 3 |
| Schema validation fail | Route to DLQ | No | — |
| Authentication fail | Stop processor, alert | No | — |
| Kafka publish fail | Retry with backoff | Yes | 5 |
| Payload too large | Log + DLQ | No | — |

### 5.6 Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | NiFi UI accessible | `curl -k https://localhost:8443/nifi-api/system-diagnostics` |
| 2 | BMS flow imported | NiFi UI shows BMS/EPMS flow |
| 3 | NMS flow imported | NiFi UI shows NMS flow |
| 4 | Validation works | Send bad record → routed to DLQ |
| 5 | Kafka publish works | Event appears in `dcim.events.raw` |
| 6 | Error handling works | Timeout → retry → DLQ |
| 7 | TLS enabled | HTTPS access only |

---

## 6. Component 5: Elasticsearch 8.x

### 6.1 Purpose

Central logging, [[siem-soc]] data store, full-text search, dan log analytics.

### 6.2 Architecture

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ ES Node 1   │  │ ES Node 2   │  │ ES Node 3   │
│ (master,    │  │ (master,    │  │ (master,    │
│  data,      │  │  data,      │  │  data,      │
│  ingest)    │  │  ingest)    │  │  ingest)    │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┼────────────────┘
                        │
              ┌─────────┴─────────┐
              │   Kibana (opt)    │
              └───────────────────┘
```

### 6.3 Configuration Spec

#### elasticsearch.yml

```yaml
# === Cluster ===
cluster.name: dcim-cluster
node.name: es-node-1
node.roles: [master, data, ingest]

# === Network ===
network.host: 0.0.0.0
http.port: 9200
transport.port: 9300

# === Discovery ===
discovery.seed_hosts:
  - es-node-1:9300
  - es-node-2:9300
  - es-node-3:9300
cluster.initial_master_nodes:
  - es-node-1
  - es-node-2
  - es-node-3

# === Security ===
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.keystore.path: /usr/share/elasticsearch/config/certs/transport.p12
xpack.security.transport.ssl.truststore.path: /usr/share/elasticsearch/config/certs/transport.p12
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.keystore.path: /usr/share/elasticsearch/config/certs/http.p12

# === Memory ===
bootstrap.memory_lock: true

# === Paths ===
path.data: /usr/share/elasticsearch/data
path.logs: /usr/share/elasticsearch/logs

# === Index ===
action.auto_create_index: true
action.destructive_requires_name: true
```

### 6.4 Index Lifecycle Management (ILM)

```json
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_primary_shard_size": "50gb",
            "max_age": "1d"
          },
          "set_priority": {
            "priority": 100
          }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": {
            "number_of_shards": 1
          },
          "forcemerge": {
            "max_num_segments": 1
          },
          "set_priority": {
            "priority": 50
          }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "set_priority": {
            "priority": 0
          }
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
}
```

### 6.5 Index Templates

```json
{
  "index_patterns": ["dcim-logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.lifecycle.name": "dcim-logs-policy",
      "index.lifecycle.rollover_alias": "dcim-logs"
    },
    "mappings": {
      "properties": {
        "@timestamp": { "type": "date" },
        "level": { "type": "keyword" },
        "service": { "type": "keyword" },
        "message": { "type": "text" },
        "source_ip": { "type": "ip" },
        "event_type": { "type": "keyword" },
        "correlation_id": { "type": "keyword" },
        "payload": { "type": "object", "enabled": false }
      }
    }
  },
  "priority": 200
}
```

### 6.6 Health Checks

```bash
# Cluster health
curl -k -u elastic:<password> https://localhost:9200/_cluster/health?pretty

# Node stats
curl -k -u elastic:<password> https://localhost:9200/_nodes/stats?pretty

# Index list
curl -k -u elastic:<password> https://localhost:9200/_cat/indices?v

# Shard allocation
curl -k -u elastic:<password> https://localhost:9200/_cat/shards?v
```

### 6.7 Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | 3 nodes in cluster | `_cluster/health` shows 3 nodes |
| 2 | Cluster status green | `_cluster/health` shows `"status":"green"` |
| 3 | Security enabled | Unauthenticated request → 401 |
| 4 | ILM policy active | `_ilm/explain` shows policy applied |
| 5 | Index rollover works | Wait for rollover, new index created |
| 6 | Prometheus metrics flowing | `elasticsearch_cluster_health_status_green = 1` |

---

## 7. Component 6: Prometheus

### 7.1 Purpose

Metrics collection dari semua DCIM services, [[prometheus]] alerting, service discovery.

### 7.2 Configuration Spec

#### prometheus.yml

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s
  scrape_timeout: 10s

# === Alert Rules ===
rule_files:
  - /etc/prometheus/rules/*.yml

# === Alertmanager ===
alerting:
  alertmanagers:
    - static_configs:
        - targets: ['alertmanager:9093']

# === Scrape Targets ===
scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # PostgreSQL
  - job_name: 'postgresql'
    static_configs:
      - targets: ['postgres-primary:9187']
        labels:
          role: primary
      - targets: ['postgres-replica:9187']
        labels:
          role: replica

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis-primary:9121']
        labels:
          role: primary
      - targets: ['redis-replica:9121']
        labels:
          role: replica

  # Kafka
  - job_name: 'kafka'
    static_configs:
      - targets: ['kafka-broker-1:9308']
      - targets: ['kafka-broker-2:9308']
      - targets: ['kafka-broker-3:9308']

  # Elasticsearch
  - job_name: 'elasticsearch'
    static_configs:
      - targets: ['es-node-1:9114']
      - targets: ['es-node-2:9114']
      - targets: ['es-node-3:9114']

  # NiFi
  - job_name: 'nifi'
    static_configs:
      - targets: ['nifi:9092']

  # Vault
  - job_name: 'vault'
    static_configs:
      - targets: ['vault:9102']

  # Grafana
  - job_name: 'grafana'
    static_configs:
      - targets: ['grafana:3000']

  # Node Exporter (all hosts)
  - job_name: 'node'
    static_configs:
      - targets: ['node-exporter:9100']
```

### 7.3 Alert Rules

```yaml
groups:
  - name: dcim-infrastructure
    rules:
      # PostgreSQL down
      - alert: PostgreSQLDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "PostgreSQL is down"
          description: "PostgreSQL instance {{ $labels.instance }} is down for more than 1 minute."

      # PostgreSQL replication lag
      - alert: PostgreSQLReplicationLag
        expr: pg_replication_lag > 30
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "PostgreSQL replication lag is high"
          description: "Replication lag is {{ $value }}s."

      # Redis down
      - alert: RedisDown
        expr: redis_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis is down"

      # Kafka under-replicated
      - alert: KafkaUnderReplicated
        expr: kafka_server_replicamanager_underreplicatedpartitions > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Kafka has under-replicated partitions"

      # Elasticsearch cluster red
      - alert: ElasticsearchClusterRed
        expr: elasticsearch_cluster_health_status{color="red"} == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Elasticsearch cluster is RED"

      # High CPU
      - alert: HighCPU
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"

      # High memory
      - alert: HighMemory
        expr: (1 - node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100 > 85
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"

      # Disk space low
      - alert: DiskSpaceLow
        expr: (1 - node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Disk space low on {{ $labels.instance }}"

      # Disk space critical
      - alert: DiskSpaceCritical
        expr: (1 - node_filesystem_avail_bytes{fstype!~"tmpfs|overlay"} / node_filesystem_size_bytes) * 100 > 90
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Disk space critical on {{ $labels.instance }}"
```

### 7.4 Retention & Storage

| Data | Retention | Storage Est |
|------|-----------|-------------|
| Raw metrics | 30 days | ~50 GB |
| Recording rules | 90 days | ~10 GB |
| Alert history | 365 days | ~5 GB |

```yaml
# Prometheus startup flags
--storage.tsdb.retention.time=30d
--storage.tsdb.retention.size=100GB
--storage.tsdb.path=/prometheus
```

### 7.5 Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | Prometheus running | `curl http://localhost:9090/-/healthy` |
| 2 | All targets scraped | `http://localhost:9090/api/v1/targets` — all UP |
| 3 | Alert rules loaded | `http://localhost:9090/api/v1/rules` — no errors |
| 4 | Alertmanager connected | `http://localhost:9090/api/v1/alertmanagers` |
| 5 | TSDB writing | `prometheus_tsdb_head_chunks` > 0 |

---

## 8. Component 7: Grafana

### 8.1 Purpose

Dashboard visualization untuk NOC, SOC, Facilities views. Data sources: Prometheus, Elasticsearch, PostgreSQL.

### 8.2 Configuration Spec

#### grafana.ini

```ini
[server]
protocol = http
http_port = 3000
domain = grafana.dcim.local
root_url = %(protocol)s://%(domain)s:%(http_port)s/

[database]
type = sqlite3
path = /var/lib/grafana/grafana.db

[security]
admin_user = admin
admin_password = <admin-password>
disable_gravatar = true
cookie_secure = true
cookie_samesite = strict

[auth]
disable_login_form = false

[auth.generic_oauth]
enabled = false
# Enable when OIDC is configured

[users]
allow_sign_up = false
auto_assign_org = true
auto_assign_org_role = Viewer

[log]
mode = console file
level = info

[metrics]
enabled = true

[alerting]
enabled = true
execute_alerts = true

[unified_alerting]
enabled = true
```

#### provisioning/datasources/datasources.yml

```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    jsonData:
      timeInterval: '15s'

  - name: Elasticsearch
    type: elasticsearch
    access: proxy
    url: https://es-node-1:9200
    database: "dcim-logs-*"
    jsonData:
      esVersion: "8.0.0"
      timeField: "@timestamp"
      logMessageField: message
      logLevelField: level
      maxConcurrentShardRequests: 5
    secureJsonData:
      basicAuthPassword: <es-password>

  - name: PostgreSQL
    type: postgres
    access: proxy
    url: pgbouncer:6432
    database: dcim_cmdb
    user: dcim_readonly
    secureJsonData:
      password: <readonly-password>
    jsonData:
      sslmode: require
      maxOpenConns: 10
      maxIdleConns: 5
      connMaxLifetime: 14400
```

### 8.3 Dashboard Structure

```
Dashboards/
├── Infrastructure/
│   ├── overview.json              # System overview (all components)
│   ├── postgresql.json            # PostgreSQL metrics
│   ├── redis.json                 # Redis metrics
│   ├── kafka.json                 # Kafka metrics
│   ├── elasticsearch.json         # ES cluster health
│   └── network.json               # Network metrics
├── NOC/
│   ├── datacenter-overview.json   # DC-wide health
│   └── capacity.json              # Capacity metrics
├── SOC/
│   ├── security-events.json       # Security event overview
│   └── compliance.json            # CIS benchmark status
├── Facilities/
│   ├── power.json                 # Power metrics (BMS)
│   ├── cooling.json               # Cooling metrics
│   └── environment.json           # Temperature/humidity
└── Business/
    ├── sla-dashboard.json         # SLA/KPI metrics
    └── cost-analysis.json         # Cost metrics
```

### 8.4 Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | Grafana running | `curl http://localhost:3000/api/health` |
| 2 | Prometheus datasource connected | Grafana UI → Datasources → Test |
| 3 | Elasticsearch datasource connected | Grafana UI → Datasources → Test |
| 4 | PostgreSQL datasource connected | Grafana UI → Datasources → Test |
| 5 | Infrastructure dashboard loaded | Dashboard shows real metrics |
| 6 | Alerting works | Create test alert → fires |

---

## 9. Component 8: HashiCorp Vault

### 9.1 Purpose

Secret management, dynamic credentials, encryption as a service, audit logging.

### 9.2 Configuration Spec

#### config.hcl

```hcl
storage "file" {
  path = "/vault/data"
}

listener "tcp" {
  address     = "0.0.0.0:8200"
  tls_disable = 0

  tls_cert_file      = "/vault/certs/server.crt"
  tls_key_file       = "/vault/certs/server.key"
  tls_client_ca_file = "/vault/certs/ca.crt"
}

api_addr = "https://vault.dcim.local:8200"
cluster_addr = "https://vault.dcim.local:8201"

ui = true

log_level = "info"

telemetry {
  prometheus_retention_time = "30s"
  disable_hostname = true
}
```

### 9.3 Secrets Engine Layout

```
secret/
├── dcim/
│   ├── postgresql/         # Database credentials
│   │   ├── app             # Application user
│   │   └── readonly        # Read-only user
│   ├── redis/              # Redis passwords
│   │   ├── primary
│   │   └── sentinel
│   ├── kafka/              # Kafka credentials
│   │   └── sasl
│   ├── elasticsearch/      # ES credentials
│   │   └── elastic
│   ├── grafana/            # Grafana admin
│   │   └── admin
│   ├── nifi/               # NiFi credentials
│   │   └── admin
│   └── api/                # API keys
│       ├── itsm
│       ├── erp
│       └── cloud
```

### 9.4 Policies

#### dcim-app.hcl

```hcl
# Read secrets for all DCIM services
path "secret/dcim/postgresql/*" {
  capabilities = ["read"]
}

path "secret/dcim/redis/*" {
  capabilities = ["read"]
}

path "secret/dcim/kafka/*" {
  capabilities = ["read"]
}

path "secret/dcim/elasticsearch/*" {
  capabilities = ["read"]
}

path "secret/dcim/api/*" {
  capabilities = ["read"]
}

# Deny access to Vault system paths
path "sys/*" {
  capabilities = ["deny"]
}

path "auth/*" {
  capabilities = ["deny"]
}
```

#### dcim-admin.hcl

```hcl
# Full access to DCIM secrets
path "secret/dcim/*" {
  capabilities = ["create", "read", "update", "delete", "list"]
}

# Read-only access to system
path "sys/*" {
  capabilities = ["read"]
}

# Audit management
path "sys/audit/*" {
  capabilities = ["create", "read", "update", "delete"]
}
```

### 9.5 Dynamic Database Credentials

```bash
# Enable database secrets engine
vault secrets enable database

# Configure PostgreSQL connection
vault write database/config/dcim-postgresql \
  plugin_name=postgresql-database-plugin \
  connection_url="postgresql://{{username}}:{{password}}@postgres-primary:5432/dcim_cmdb?sslmode=require" \
  allowed_roles="dcim-app,dcim-readonly" \
  username="vault_admin" \
  password="<admin-password>"

# Create role for app
vault write database/roles/dcim-app \
  db_name=dcim-postgresql \
  default_ttl="1h" \
  max_ttl="24h" \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT dcim_app TO \"{{name}}\";"

# Get dynamic credentials
vault read database/creds/dcim-app
```

### 9.6 Health Checks

```bash
# Vault status
vault status

# Health check
curl -s https://localhost:8200/v1/sys/health | jq .

# List secrets
vault secrets list

# List policies
vault policy list

# Audit status
vault audit list
```

### 9.7 Acceptance Criteria

| # | Criterion | Test Method |
|---|-----------|-------------|
| 1 | Vault running & unsealed | `vault status` shows initialized + unsealed |
| 2 | UI accessible | `https://vault.dcim.local:8200/ui` |
| 3 | Secrets engines enabled | `vault secrets list` shows `secret/`, `database/` |
| 4 | Policies loaded | `vault policy list` shows dcim policies |
| 5 | Dynamic credentials work | `vault read database/creds/dcim-app` returns credentials |
| 6 | Audit logging active | `vault audit list` shows file audit device |
| 7 | TLS enabled | HTTP redirect to HTTPS |

---

## 10. Network Architecture

### 10.1 VLAN Design

| VLAN | CIDR | Purpose | Components |
|------|------|---------|------------|
| Management | 10.70.0.0/24 | Admin access, monitoring | Prometheus, Grafana, Vault UI |
| Data | 10.70.1.0/24 | Application traffic | PostgreSQL, Redis, Kafka, NiFi, ES |
| DMZ | 10.70.2.0/24 | External-facing | API Gateway, Dashboard |
| Storage | 10.70.3.0/24 | Backup traffic | Backup servers |

### 10.2 Firewall Rules

```bash
# Default policy: DROP ALL
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT

# Management VLAN → Services (specific ports only)
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 5432 -j ACCEPT   # PostgreSQL
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 6379 -j ACCEPT   # Redis
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 9092 -j ACCEPT   # Kafka
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 8443 -j ACCEPT   # NiFi UI
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 9200 -j ACCEPT   # Elasticsearch
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 9090 -j ACCEPT   # Prometheus
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 3000 -j ACCEPT   # Grafana
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 8200 -j ACCEPT   # Vault

# Data VLAN → Data VLAN (inter-service)
iptables -A INPUT -s 10.70.1.0/24 -d 10.70.1.0/24 -j ACCEPT

# DMZ → Dashboard only
iptables -A INPUT -s 10.70.2.0/24 -d 10.70.2.0/24 -j ACCEPT

# SSH (Management only)
iptables -A INPUT -s 10.70.0.0/24 -p tcp --dport 22 -j ACCEPT

# ICMP (ping)
iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT
```

### 10.3 DNS Resolution

```bash
# /etc/hosts (dev/staging)
10.70.1.10  postgres-primary
10.70.1.11  postgres-replica
10.70.1.20  redis-primary
10.70.1.21  redis-replica
10.70.1.30  kafka-controller
10.70.1.31  kafka-broker-2
10.70.1.32  kafka-broker-3
10.70.1.40  nifi
10.70.1.50  es-node-1
10.70.1.51  es-node-2
10.70.1.52  es-node-3
10.70.0.10  prometheus
10.70.0.11  grafana
10.70.0.20  vault
10.70.0.30  alertmanager
```

---

## 11. Deployment Strategy

### 11.1 Environments

| Environment | Purpose | Infrastructure | Scale |
|-------------|---------|----------------|-------|
| Development | Local dev, unit test | Docker Compose | Single node |
| Staging | Integration test, UAT | Docker Compose | Multi-container |
| Production | Live operations | Kubernetes | HA multi-node |

### 11.2 Docker Compose (Dev/Staging)

```yaml
# docker-compose.yml — minimal structure
version: '3.8'

services:
  postgres-primary:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    volumes: ["pgdata:/var/lib/postgresql/data"]
    environment:
      POSTGRES_DB: dcim
      POSTGRES_USER: dcim
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U dcim"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis-primary:
    image: redis:7-alpine
    ports: ["6379:6379"]
    command: redis-server /etc/redis/redis.conf
    volumes: ["redis-data:/data", "./redis/redis.conf:/etc/redis/redis.conf"]
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  kafka-controller:
    image: confluentinc/cp-kafka:7.5.0
    ports: ["9092:9092"]
    environment:
      KAFKA_NODE_ID: 1
      KAFKA_PROCESS_ROLES: controller,broker
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka-controller:9093
      KAFKA_LISTENERS: PLAINTEXT://:9092,CONTROLLER://:9093
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-controller:9092
    volumes: ["kafka-data:/var/lib/kafka/data"]

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    ports: ["9200:9200"]
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    volumes: ["es-data:/usr/share/elasticsearch/data"]

  prometheus:
    image: prom/prometheus:latest
    ports: ["9090:9090"]
    volumes: ["./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml"]

  grafana:
    image: grafana/grafana:latest
    ports: ["3000:3000"]
    volumes: ["grafana-data:/var/lib/grafana"]

  vault:
    image: hashicorp/vault:latest
    ports: ["8200:8200"]
    cap_add: [IPC_LOCK]
    environment:
      VAULT_ADDR: "http://0.0.0.0:8200"

volumes:
  pgdata:
  redis-data:
  kafka-data:
  es-data:
  grafana-data:
```

### 11.3 Kubernetes (Production)

```
k8s/
├── namespace.yml
├── configmaps/
│   ├── postgresql-config.yml
│   ├── redis-config.yml
│   ├── kafka-config.yml
│   ├── elasticsearch-config.yml
│   ├── prometheus-config.yml
│   ├── grafana-config.yml
│   └── vault-config.yml
├── secrets/
│   ├── postgresql-secrets.yml
│   ├── redis-secrets.yml
│   ├── kafka-secrets.yml
│   └── vault-secrets.yml
├── deployments/
│   ├── postgresql.yml
│   ├── redis.yml
│   ├── kafka.yml
│   ├── nifi.yml
│   ├── elasticsearch.yml
│   ├── prometheus.yml
│   ├── grafana.yml
│   └── vault.yml
├── services/
│   ├── postgresql.yml
│   ├── redis.yml
│   ├── kafka.yml
│   ├── nifi.yml
│   ├── elasticsearch.yml
│   ├── prometheus.yml
│   ├── grafana.yml
│   └── vault.yml
├── statefulsets/
│   ├── postgresql.yml
│   ├── redis.yml
│   ├── kafka.yml
│   └── elasticsearch.yml
├── ingress.yml
├── networkpolicies/
│   ├── default-deny.yml
│   ├── allow-monitoring.yml
│   └── allow-data-flow.yml
└── persistentvolumes/
    ├── postgresql-pv.yml
    ├── redis-pv.yml
    ├── kafka-pv.yml
    └── elasticsearch-pv.yml
```

---

## 12. Base Monitoring & Alerting

### 12.1 Metrics Collection Summary

| Component | Exporter | Port | Key Metrics |
|-----------|----------|------|-------------|
| PostgreSQL | postgres_exporter | 9187 | connections, replication lag, cache hit ratio, dead tuples |
| Redis | redis_exporter | 9121 | memory, hits/misses, connections, keys, commands/sec |
| Kafka | kafka_exporter | 9308 | messages in/out, under-replicated, consumer lag |
| Elasticsearch | elasticsearch_exporter | 9114 | cluster health, nodes, indices, shards |
| NiFi | NiFi REST API | 9092 | flow throughput, processor stats |
| Vault | vault_exporter | 9102 | seal status, requests, token count |
| Node | node_exporter | 9100 | CPU, memory, disk, network |
| Prometheus | self | 9090 | TSDB, scrape duration, rules |

### 12.2 Alert Escalation Matrix

| Alert | Severity | Notification | Escalation |
|-------|----------|-------------|------------|
| Component down | Critical | Slack + Email + PagerDuty | Immediate |
| Replication lag > 30s | Warning | Slack | 30min → Critical |
| Disk > 80% | Warning | Slack | 7d → Critical |
| Disk > 90% | Critical | Slack + Email | Immediate |
| CPU > 80% | Warning | Slack | 1h → investigate |
| Consumer lag > 10k | Warning | Slack | 30min → investigate |
| DLQ growing | Warning | Slack | 1h → investigate |

### 12.3 Notification Channels

```yaml
# alertmanager.yml
global:
  slack_api_url: '${SLACK_WEBHOOK_URL}'
  smtp_smarthost: 'smtp.dcim.local:587'
  smtp_from: 'alertmanager@dcim.local'
  smtp_auth_username: 'alertmanager@dcim.local'
  smtp_auth_password: '${SMTP_PASSWORD}'

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'slack-critical'
  routes:
    - match:
        severity: critical
      receiver: 'pagerduty-critical'
    - match:
        severity: warning
      receiver: 'slack-warning'

receivers:
  - name: 'slack-critical'
    slack_configs:
      - channel: '#dcim-alerts-critical'
        send_resolved: true
        title: '{{ .GroupLabels.alertname }}'
        text: '{{ range .Alerts }}{{ .Annotations.description }}{{ end }}'

  - name: 'slack-warning'
    slack_configs:
      - channel: '#dcim-alerts-warning'
        send_resolved: true

  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '${PAGERDUTY_SERVICE_KEY}'
```

---

## 13. Security Hardening

### 13.1 TLS everywhere

| Component | TLS Port | Cert Source | Min Version |
|-----------|----------|-------------|-------------|
| PostgreSQL | 5432 | Internal CA | TLS 1.2 |
| Redis | 6379 | Internal CA | TLS 1.2 |
| Kafka | 9093 | Internal CA | TLS 1.2 |
| NiFi | 8443 | Internal CA | TLS 1.2 |
| Elasticsearch | 9200 | Internal CA | TLS 1.2 |
| Vault | 8200 | Internal CA | TLS 1.2 |
| Grafana | 3000 | Internal CA | TLS 1.2 |
| Prometheus | 9090 | Internal CA | TLS 1.2 |

### 13.2 Authentication Matrix

| Component | Auth Method | Credential Store |
|-----------|-------------|-----------------|
| PostgreSQL | SCRAM-SHA-256 | Vault dynamic creds |
| Redis | ACL + password | Vault |
| Kafka | SASL/SCRAM | Vault |
| NiFi | TLS client cert | Internal CA |
| Elasticsearch | xpack security | Vault |
| Vault | Token / AppRole | Unseal keys (HSM) |
| Grafana | OAuth2 / local | Vault |

### 13.3 Secret Rotation

| Secret | Rotation Period | Method |
|--------|----------------|--------|
| PostgreSQL app password | 30 days | Vault dynamic |
| Redis password | 90 days | Manual + Vault |
| Kafka SASL credentials | 90 days | Manual + Vault |
| ES elastic password | 90 days | Manual + Vault |
| API keys | 30 days | Vault |

### 13.4 Audit Logging

```bash
# Enable Vault audit
vault audit enable file file_path=/vault/logs/audit.log

# PostgreSQL audit (pgAudit)
CREATE EXTENSION IF NOT EXISTS pgaudit;
SET pgaudit.log = 'write, ddl, role';
SET pgaudit.log_catalog = on;
```

---

## 14. Backup & Recovery

### 14.1 Backup Matrix

| Component | Method | Frequency | Retention | RPO | RTO |
|-----------|--------|-----------|-----------|-----|-----|
| PostgreSQL | pg_basebackup + WAL | Daily + continuous | 7d + 30d logical | 5min | 30min |
| Redis | RDB + AOF | On save + everysec | 7 days | 1s | 5min |
| Kafka | Topic snapshots | Daily | 7 days | 1h | 1h |
| Elasticsearch | Snapshot API | Daily | 30 days | 24h | 2h |
| Vault | File snapshot | Daily | 30 days | 24h | 1h |
| Grafana | Dashboard export | On change | 30 days | 24h | 30min |
| NiFi | Flow export | On change | 30 days | 24h | 30min |
| Configs | Git | On change | indefinite | 0 | 5min |

### 14.2 Recovery Procedures

```bash
# PostgreSQL failover
pg_ctl promote -D /var/lib/postgresql/standby

# Redis failover
redis-cli -p 26379 SENTINEL failover dcim-primary

# Kafka broker recovery
kafka-server-start.sh config/server.properties

# Elasticsearch node recovery
# Elasticsearch auto-recovers when node rejoins cluster

# Vault unseal
vault operator unseal <key1>
vault operator unseal <key2>
vault operator unseal <key3>
```

---

## 15. Sizing & Capacity

### 15.1 Event Volume Estimates

| Source | Events/sec | Events/day | Storage/day |
|--------|------------|------------|-------------|
| BMS/EPMS | 100 | 8.6M | ~5 GB |
| NMS | 50 | 4.3M | ~2.5 GB |
| Server/Storage | 200 | 17.3M | ~10 GB |
| Virtualization/Cloud | 50 | 4.3M | ~2.5 GB |
| Access Control | 30 | 2.6M | ~1.5 GB |
| **Total** | **430** | **37.1M** | **~21.5 GB/day** |

### 15.2 Storage Projection (90 days)

| Data Type | Daily | 30-day | 90-day |
|-----------|-------|--------|--------|
| Raw events (Kafka) | 5 GB | 150 GB | — |
| Validated events | 5 GB | 150 GB | — |
| Enriched events | 5 GB | 150 GB | 450 GB |
| ES logs | 21.5 GB | 645 GB | 1.9 TB |
| PostgreSQL | 1 GB | 30 GB | 90 GB |
| Prometheus metrics | 1.5 GB | 45 GB | 135 GB |
| **Total** | **~39 GB** | **~1.2 TB** | **~2.7 TB** |

### 15.3 Recommended Production Sizing

| Component | Nodes | vCPU/node | RAM/node | Storage/node |
|-----------|-------|-----------|----------|-------------|
| PostgreSQL | 2 | 4 | 16 GB | 200 GB SSD |
| Redis | 2 | 2 | 8 GB | 40 GB SSD |
| Kafka | 3 | 4 | 16 GB | 500 GB SSD |
| NiFi | 2 | 4 | 8 GB | 100 GB SSD |
| Elasticsearch | 3 | 4 | 16 GB | 500 GB SSD |
| Prometheus | 1 | 2 | 8 GB | 100 GB SSD |
| Grafana | 1 | 2 | 4 GB | 20 GB SSD |
| Vault | 3 | 2 | 4 GB | 20 GB SSD |
| **Total** | **17** | **54** | **192 GB** | **~2.5 TB** |

---

## 16. Acceptance Criteria — Block 1 Complete

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | Project structure created | `docker-compose.yml`, `.env.example`, `Makefile` exist | ⬜ |
| 2 | PostgreSQL 16 running with HA | `pg_isready` + `pg_stat_replication` streaming | ⬜ |
| 3 | Redis 7 running with Sentinel | `redis-cli PING` + `SENTINEL masters` | ⬜ |
| 4 | Kafka 3.x running with KRaft | 3 brokers, no ZK, 9 topics created | ⬜ |
| 5 | NiFi deployed with base flows | NiFi UI accessible, flows imported | ⬜ |
| 6 | Elasticsearch 8.x running | 3 nodes, cluster green | ⬜ |
| 7 | Prometheus scraping all targets | All targets UP in `/api/v1/targets` | ⬜ |
| 8 | Grafana with dashboards | Dashboard shows real metrics | ⬜ |
| 9 | Vault deployed with policies | `vault status` + policies loaded | ⬜ |
| 10 | Network segmentation | VLANs configured, firewall rules active | ⬜ |
| 11 | Base monitoring & alerting | Alert rules loaded, test alert fires | ⬜ |
| 12 | Security hardening | TLS everywhere, auth enforced | ⬜ |
| 13 | Backup configured | Test backup + restore successful | ⬜ |
| 14 | Docker Compose validates | `docker-compose config` passes | ⬜ |
| 15 | K8s manifests validate | `kubectl apply --dry-run=client` passes | ⬜ |

---

## 17. Gap Comparison Template

Gunakan template ini untuk setiap komponen:

```markdown
### Gap: [Komponen]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Version | [versi di spec] | [versi aktual] | [match/mismatch] | P1-P4 |
| HA Config | [spec detail] | [aktual detail] | [gap detail] | P1-P4 |
| Security | [spec detail] | [aktual detail] | [gap detail] | P1-P4 |
| Monitoring | [spec detail] | [aktual detail] | [gap detail] | P1-P4 |
| Backup | [spec detail] | [aktual detail] | [gap detail] | P1-P4 |
| Network | [spec detail] | [aktual detail] | [gap detail] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]
```

---

## References

- [[infrastructure-provisioning]]
- [[postgresql]]
- [[redis]]
- [[kafka]]
- [[nifi]]
- [[elasticsearch]]
- [[prometheus]]
- [[grafana]]
- [[vault]]
- [[network-architecture]]
- [[dcim-deployment-architecture]]
- [[dcim-core-platform]]

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-23
> **Purpose:** Reference for team comparison → gap identification → connection dots
