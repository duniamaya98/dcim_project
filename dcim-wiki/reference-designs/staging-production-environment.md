---
title: "Staging & Production Environment: Reference Design Spec"
created: 2026-06-24
updated: 2026-06-24
type: reference-design
block: infrastructure
phase: 1
status: generated
confidence: high
tags: [infrastructure, staging, production, deployment, dr, monitoring]
wiki_pages:
  - dcim-deployment-architecture
  - dcim-infrastructure-provisioning
purpose: >
  Reference design spec untuk Staging & Production Environment DCIM Core Platform.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Staging & Production Environment: Reference Design Spec

> **Purpose:** Mendefinisikan arsitektur dual-environment (Staging & Production) untuk DCIM Core Platform, termasuk isolation strategy, deployment pipeline, DR, monitoring, dan security hardening.
> **Cara pakai:** Tim DevOps/Infra compare spec ini dengan actual deployment. Document gap di Section 11.
> **Architecture Diagram:** `diagrams/staging-production-architecture.html`
> **Depends on:** Block 1 (Infrastructure Provisioning)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Environment Isolation Strategy](#2-environment-isolation-strategy)
3. [Network Architecture](#3-network-architecture)
4. [Component Sizing Matrix](#4-component-sizing-matrix)
5. [Deployment Pipeline](#5-deployment-pipeline)
6. [Data Separation Strategy](#6-data-separation-strategy)
7. [Disaster Recovery](#7-disaster-recovery)
8. [Monitoring & Alerting](#8-monitoring--alerting)
9. [Security Hardening](#9-security-hardening)
10. [Acceptance Criteria](#10-acceptance-criteria)
11. [Gap Comparison Template](#11-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 Context

DCIM Core Platform membutuhkan dua environment terisolasi:

- **Staging**: Untuk testing, validation, dan pre-production verification
- **Production**: Untuk live operation dengan HA, DR, dan security hardening

### 1.2 Design Principles

| Principle | Description |
|-----------|-------------|
| **Architecture Parity** | Staging mirror production architecture at reduced scale |
| **Network Isolation** | Separate VLANs per environment, no cross-env data leaks |
| **Data Separation** | Staging uses synthetic/masked data, never raw production data |
| **Deployment Promotion** | Code flows staging → production with manual gate |
| **Security by Default** | Production hardening applied from day one |
| **Observability First** | Both environments fully monitored, production with HA |

### 1.3 High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CI/CD Pipeline                               │
│  Code Commit → CI Test → Build → Deploy Staging → Validate → Prod  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    STAGING ENVIRONMENT  │     │   PRODUCTION ENVIRONMENT │
│    VLAN 100-109         │     │   VLAN 200-209           │
│                         │     │                          │
│  ┌─────────────────┐   │     │  ┌─────────────────┐    │
│  │ Single-node     │   │     │  │ HA Clusters     │    │
│  │ components      │   │     │  │ (3-node each)   │    │
│  └─────────────────┘   │     │  └─────────────────┘    │
│                         │     │                          │
│  ┌─────────────────┐   │     │  ┌─────────────────┐    │
│  │ Synthetic data  │   │     │  │ Live data       │    │
│  └─────────────────┘   │     │  └─────────────────┘    │
│                         │     │                          │
│  ┌─────────────────┐   │     │  ┌─────────────────┐    │
│  │ Basic monitoring│   │     │  │ HA monitoring   │    │
│  └─────────────────┘   │     │  └─────────────────┘    │
└─────────────────────────┘     └─────────────────────────┘
```

---

## 2. Environment Isolation Strategy

### 2.1 Isolation Model: Full Isolation (Recommended)

| Aspect | Staging | Production |
|--------|---------|------------|
| **VMs/Servers** | Dedicated staging servers | Dedicated production servers |
| **Kafka** | Single broker, staging topics | 3-broker cluster, production topics |
| **PostgreSQL** | Single node | 3-node cluster (primary + 2 replicas) |
| **Redis** | Single node | Sentinel (3 nodes) |
| **NiFi** | Single node | 2-node cluster |
| **Elasticsearch** | Single node | 3-node cluster |
| **Prometheus** | Single node | Federation (2 nodes) |
| **Grafana** | Single node | HA (2 nodes + LB) |
| **Vault** | Single node | 3-node cluster |

### 2.2 Why Full Isolation

| Risk | Mitigation |
|------|------------|
| Resource contention | Separate VMs, no shared resources |
| Blast radius | Network isolation prevents cross-env impact |
| Data contamination | Separate databases, no shared storage |
| Configuration drift | IaC manages both environments identically |
| Security breach | Production network completely isolated |

### 2.3 Cost Optimization

| Component | Staging Cost | Production Cost | Ratio |
|-----------|-------------|-----------------|-------|
| VMs | 4 vCPU, 16GB RAM | 8 vCPU, 32GB RAM per node | 1:4 |
| Storage | 200GB SSD | 500GB SSD per node | 1:5 |
| Network | 1 Gbps | 10 Gbps | 1:10 |
| License | Same | Same | 1:1 |

**Total Cost Ratio**: Staging ≈ 25-30% of Production

---

## 3. Network Architecture

### 3.1 VLAN Segmentation

#### Staging Environment (VLAN 100-109)

| VLAN | Name | Purpose | CIDR |
|------|------|---------|------|
| 100 | staging-mgmt | Management & CI/CD | 10.100.0.0/24 |
| 101 | staging-data | Data services (PG, Redis, Kafka) | 10.100.1.0/24 |
| 102 | staging-dmz | External access (API, Dashboard) | 10.100.2.0/24 |

#### Production Environment (VLAN 200-209)

| VLAN | Name | Purpose | CIDR |
|------|------|---------|------|
| 200 | prod-mgmt | Management & monitoring | 10.200.0.0/24 |
| 201 | prod-data | Data services (PG, Redis, Kafka) | 10.200.1.0/24 |
| 202 | prod-dmz | External access (API, Dashboard) | 10.200.2.0/24 |
| 203 | prod-cluster | HA cluster communication | 10.200.3.0/24 |

### 3.2 Cross-Environment Connectivity

| Direction | Access | Purpose |
|-----------|--------|---------|
| Staging → Production | READ-ONLY replicas | Data sync validation |
| Production → Staging | No access | Security isolation |
| CI/CD → Staging | Full access | Deployment pipeline |
| CI/CD → Production | Controlled access | Promoted deployments |

### 3.3 Firewall Rules

#### Staging

| Rule | Source | Destination | Port | Protocol |
|------|--------|-------------|------|----------|
| Developer SSH | 10.100.0.0/24 | All staging | 22 | TCP |
| API Access | 10.100.2.0/24 | API Gateway | 8080 | TCP |
| Dashboard | 10.100.2.0/24 | Grafana | 3000 | TCP |

#### Production

| Rule | Source | Destination | Port | Protocol |
|------|--------|-------------|------|----------|
| Jump Host Only | 10.200.0.10 | All prod | 22 | TCP |
| API Gateway | 10.200.2.0/24 | LB | 443 | TCP |
| Inter-VLAN | As needed | Specific services | As needed | TCP |

### 3.4 Load Balancer

| Environment | LB Type | Services |
|-------------|---------|----------|
| Staging | None (single node) | N/A |
| Production | HAProxy/Nginx | PostgreSQL, API, Dashboard, Grafana |

---

## 4. Component Sizing Matrix

### 4.1 Staging (Single-Node)

| Component | vCPU | RAM | Storage | Replicas |
|-----------|------|-----|---------|----------|
| PostgreSQL 16 | 2 | 4GB | 50GB SSD | 1 |
| Redis 7 | 1 | 2GB | 10GB SSD | 1 |
| Kafka 3.x | 2 | 4GB | 50GB SSD | 1 broker |
| NiFi 1.x | 2 | 4GB | 50GB SSD | 1 |
| Elasticsearch 8.x | 2 | 4GB | 100GB SSD | 1 |
| Prometheus | 1 | 2GB | 20GB SSD | 1 |
| Grafana | 1 | 1GB | 10GB SSD | 1 |
| Vault | 1 | 1GB | 10GB SSD | 1 |
| **Total** | **12** | **22GB** | **300GB** | - |

### 4.2 Production (HA Clusters)

| Component | vCPU | RAM | Storage | Replicas |
|-----------|------|-----|---------|----------|
| PostgreSQL 16 | 4 | 16GB | 500GB SSD | 3 (1 primary + 2 replicas) |
| Redis 7 | 2 | 4GB | 50GB SSD | 3 (Sentinel) |
| Kafka 3.x | 4 | 16GB | 500GB SSD | 3 brokers |
| NiFi 1.x | 4 | 16GB | 200GB SSD | 2 |
| Elasticsearch 8.x | 4 | 16GB | 1TB SSD | 3 |
| Prometheus | 2 | 8GB | 100GB SSD | 2 (federation) |
| Grafana | 2 | 4GB | 20GB SSD | 2 + LB |
| Vault | 2 | 4GB | 20GB SSD | 3 |
| **Total** | **52** | **184GB** | **2.9TB** | - |

### 4.3 Network Bandwidth

| Environment | Internal | External | Notes |
|-------------|----------|----------|-------|
| Staging | 1 Gbps | 100 Mbps | Developer access |
| Production | 10 Gbps | 1 Gbps | Load balanced |

---

## 5. Deployment Pipeline

### 5.1 CI/CD Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CI/CD Pipeline                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Developer commits code                                          │
│     ↓                                                              │
│  2. CI runs tests (unit, integration)                              │
│     ↓                                                              │
│  3. Build artifacts (Docker images, configs)                       │
│     ↓                                                              │
│  4. Deploy to Staging (automatic)                                  │
│     ↓                                                              │
│  5. Staging validation (automated + manual)                        │
│     ↓                                                              │
│  6. Production approval (manual gate)                              │
│     ↓                                                              │
│  7. Deploy to Production (canary or blue-green)                    │
│     ↓                                                              │
│  8. Post-deploy verification                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2 Deployment Strategies

| Environment | Strategy | Rollback Time |
|-------------|----------|---------------|
| Staging | Rolling update | 5 minutes |
| Production | Blue-green | Instant (switch LB) |
| Critical services | Canary (10% → 50% → 100%) | 2 minutes |

### 5.3 Promotion Criteria

| Criterion | Staging → Production |
|-----------|---------------------|
| Unit tests | ✅ 100% pass |
| Integration tests | ✅ 100% pass |
| Performance benchmarks | ✅ Meet SLA |
| Security scan | ✅ No critical/high |
| Manual approval | ✅ Lead sign-off |
| Rollback plan | ✅ Documented |

### 5.4 Deployment Tools

| Tool | Purpose |
|------|---------|
| Docker/Kubernetes | Container orchestration |
| Helm Charts | Package management |
| ArgoCD | GitOps deployment |
| Vault | Secret management |
| Ansible | Configuration management |

---

## 6. Data Separation Strategy

### 6.1 Staging Data

| Data Type | Source | Refresh Cycle |
|-----------|--------|---------------|
| Synthetic test data | Generated | On demand |
| Masked production snapshots | Production (anonymized) | Weekly |
| Test fixtures | Code repository | Each deploy |

### 6.2 Production Data

| Data Type | Source | Retention |
|-----------|--------|-----------|
| Live telemetry | BMS, EPMS, NMS | 90 days hot, 1 year warm |
| Asset data | ITSM, ERP | Permanent |
| CI data | Discovery tools | Permanent |
| Audit logs | All systems | 7 years |
| Metrics | Prometheus | 30 days |

### 6.3 Data Masking Rules

| Field | Masking Method |
|-------|---------------|
| IP addresses | Partial hash (keep last octet) |
| Hostnames | Replace with generic names |
| User emails | Hash + domain preserved |
| Credentials | Fully redacted |
| Financial data | Random within range |

---

## 7. Disaster Recovery

### 7.1 RTO/RPO Targets

| Environment | RPO | RTO | Strategy |
|-------------|-----|-----|----------|
| Staging | 24 hours | 8 hours | Rebuild from IaC |
| Production | 1 hour | 4 hours | Cross-site replication |

### 7.2 Backup Strategy

#### Staging

| Component | Backup Type | Frequency | Retention |
|-----------|-------------|-----------|-----------|
| PostgreSQL | pg_dump | Daily | 7 days |
| Redis | RDB snapshot | Daily | 7 days |
| Kafka | Topic backup | Daily | 7 days |
| Elasticsearch | Snapshot | Daily | 7 days |
| Config files | Git | Per commit | Permanent |

#### Production

| Component | Backup Type | Frequency | Retention |
|-----------|-------------|-----------|-----------|
| PostgreSQL | WAL archiving | Continuous | 30 days |
| PostgreSQL | pg_dump | Daily | 30 days |
| Redis | RDB + AOF | Hourly | 7 days |
| Kafka | Topic backup | Hourly | 30 days |
| Elasticsearch | Snapshot | Hourly | 30 days |
| Vault | Auto-unseal | Continuous | Permanent |
| Config files | Git | Per commit | Permanent |

### 7.3 Replication

| Component | Staging | Production |
|-----------|---------|------------|
| PostgreSQL | None | Streaming replication (2 replicas) |
| Redis | None | Sentinel with 2 replicas |
| Kafka | None | Replication factor 3 |
| Elasticsearch | None | Replication factor 3 |

### 7.4 Failover Procedures

| Scenario | Detection | Action | RTO |
|----------|-----------|--------|-----|
| Primary DB down | Health check failover | Promote replica | 5 min |
| Kafka broker down | ISR shrink alert | Rebalance partitions | 2 min |
| ES node down | Cluster health red | Reallocate shards | 5 min |
| Full site failure | External monitoring | Activate DR site | 4 hours |

---

## 8. Monitoring & Alerting

### 8.1 Monitoring Architecture

#### Staging

```
Prometheus (single) → Grafana (single)
                    → Alertmanager → Email
```

#### Production

```
Prometheus Federation (2x) → Grafana (HA)
                           → Alertmanager → Email + Slack + PagerDuty
                           → Elasticsearch (logs)
                           → Jaeger (tracing)
```

### 8.2 Metrics Collection

| Metric Type | Staging | Production |
|-------------|---------|------------|
| System metrics | Node Exporter | Node Exporter |
| Application metrics | Custom exporters | Custom exporters |
| Database metrics | PG Exporter, Redis Exporter | PG Exporter, Redis Exporter |
| Kafka metrics | Kafka Exporter | Kafka Exporter |
| Network metrics | Blackbox Exporter | Blackbox Exporter |

### 8.3 Alert Escalation

| Severity | Staging | Production |
|----------|---------|------------|
| P1 Critical | Email | PagerDuty + SMS + Slack |
| P2 High | Email | Slack + Email (15 min) |
| P3 Medium | Email | Email (1 hour) |
| P4 Low | Daily digest | Daily digest |

### 8.4 Log Aggregation

| Environment | Pipeline |
|-------------|----------|
| Staging | Filebeat → Elasticsearch (single) |
| Production | Filebeat → Kafka → Elasticsearch (3-node) |

### 8.5 Dashboards

| Dashboard | Staging | Production |
|-----------|---------|------------|
| System Overview | Basic | Full (HA metrics) |
| Database Performance | Basic | Detailed (replication lag) |
| Kafka Throughput | Basic | Detailed (ISR, consumer lag) |
| Application Metrics | Basic | Full (APM traces) |
| Security Events | Basic | Full (SIEM integration) |

---

## 9. Security Hardening

### 9.1 Production-Only Security

| Measure | Implementation |
|---------|----------------|
| Network segmentation | Strict VLAN rules, no cross-env access |
| Secret rotation | Vault auto-rotate (90-day cycle) |
| Audit logging | All API calls logged to immutable store |
| Rate limiting | API gateway (1000 req/min per client) |
| DDoS protection | CloudFlare/reverse proxy |
| TLS everywhere | Internal + external encryption |
| mTLS | Service-to-service (optional) |
| RBAC | Role-based access control |
| Least privilege | Minimal permissions per service |
| Data encryption | AES-256 at rest |

### 9.2 Staging Security

| Measure | Implementation |
|---------|----------------|
| Access control | Developer VPN + SSH keys |
| No production data | Synthetic/masked data only |
| Basic audit | API call logging |
| TLS | External endpoints only |

### 9.3 Compliance Checklist

| Requirement | Staging | Production |
|-------------|---------|------------|
| TLS 1.2+ | External | All traffic |
| RBAC | Basic | Full |
| Audit trail | API calls | All operations |
| Secret management | Vault | Vault (HA) |
| Data classification | Basic | Full |
| Encryption at rest | Optional | Required |

---

## 10. Acceptance Criteria

| # | Criterion | Test Method | ⬜ |
|---|-----------|-------------|-----|
| 1 | Staging and production on separate VLANs | Network config review | ⬜ |
| 2 | No direct network access between environments | Penetration test | ⬜ |
| 3 | Staging mirrors production architecture at reduced scale | Architecture review | ⬜ |
| 4 | CI/CD pipeline deploys to staging automatically | Pipeline test | ⬜ |
| 5 | Production deployment requires manual approval | Process audit | ⬜ |
| 6 | Blue-green deployment works for production | Deployment test | ⬜ |
| 7 | Rollback completes within 5 minutes | Rollback test | ⬜ |
| 8 | Staging uses synthetic/masked data only | Data audit | ⬜ |
| 9 | Production backups run on schedule | Backup verification | ⬜ |
| 10 | Production RPO ≤ 1 hour | DR test | ⬜ |
| 11 | Production RTO ≤ 4 hours | DR test | ⬜ |
| 12 | Monitoring covers all components | Dashboard review | ⬜ |
| 13 | Alerts route to correct channels | Alert test | ⬜ |
| 14 | Production has HA for all critical services | HA test | ⬜ |
| 15 | Vault manages all secrets | Security audit | ⬜ |
| 16 | TLS enabled for all production traffic | SSL check | ⬜ |
| 17 | Audit logging captures all API calls | Log review | ⬜ |
| 18 | Rate limiting prevents abuse | Load test | ⬜ |
| 19 | Documentation is complete and current | Doc review | ⬜ |
| 20 | Runbook exists for common operations | Runbook review | ⬜ |

---

## 11. Gap Comparison Template

### Gap: [Component Name]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| {aspect} | [spec detail] | [aktual detail] | [match/mismatch] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

### Gap: Network Isolation

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| VLAN separation | Separate VLANs per env | | ⬜ | P1 |
| Firewall rules | Strict inter-VLAN rules | | ⬜ | P1 |
| Cross-env access | No direct access | | ⬜ | P1 |

**Decision:** ⬜
**Rationale:** ⬜
**Action items:** ⬜

---

### Gap: Deployment Pipeline

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| CI/CD automation | Full pipeline | | ⬜ | P1 |
| Promotion gate | Manual approval | | ⬜ | P2 |
| Rollback capability | Blue-green | | ⬜ | P1 |

**Decision:** ⬜
**Rationale:** ⬜
**Action items:** ⬜

---

### Gap: Disaster Recovery

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| RPO | 1 hour | | ⬜ | P1 |
| RTO | 4 hours | | ⬜ | P1 |
| Backup strategy | Continuous + daily | | ⬜ | P2 |
| Replication | Cross-site | | ⬜ | P2 |

**Decision:** ⬜
**Rationale:** ⬜
**Action items:** ⬜

---

### Gap: Security Hardening

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| TLS everywhere | Internal + external | | ⬜ | P1 |
| Secret management | Vault HA | | ⬜ | P1 |
| Audit logging | All API calls | | ⬜ | P2 |
| Rate limiting | API gateway | | ⬜ | P3 |

**Decision:** ⬜
**Rationale:** ⬜
**Action items:** ⬜

---

## References

| Document | Path |
|----------|------|
| Block 1 Infrastructure | `block1-infrastructure-provisioning.md` |
| Deployment Architecture | `dcim-deployment-architecture` |
| Implementation Plan | `implementation-plan.md` |
| Architecture Diagram | `diagrams/staging-production-architecture.html` |
