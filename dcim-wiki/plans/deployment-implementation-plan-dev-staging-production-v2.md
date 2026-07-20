---
title: "DCIM Core Platform — Deployment & Implementation Plan v2.0 (Dev, Staging, Production)"
version: "2.0"
created: 2026-07-14
updated: 2026-07-14
type: summary
status: proposed
tags: [deployment, implementation, environment, architecture, infrastructure, ha-dr, security, observability, testing, dii, asset-repository, cmdb, siem-soc, soar, analytics-ai, llm, rag, gemma, workflow-automation, dashboard, external-integration]
supersedes: "deployment-implementation-plan-dev-staging-production.md"
sources:
  - plans/implementation-plan.md
  - guides/deployment-implementation-guide.md
  - reference-designs/staging-production-environment.md
  - reference-designs/block1-infrastructure-provisioning.md
  - reference-designs/block2-data-ingestion-integration.md
  - reference-designs/block3-asset-repository.md
  - reference-designs/block4-cmdb.md
  - reference-designs/block5-web-dashboard.md
  - reference-designs/block6-siem-soc-v3.md
  - reference-designs/siem-soar.md
  - reference-designs/block7-analytics-ai-engine.md
  - reference-designs/block8-workflow-automation.md
  - reference-designs/block9-external-integrations.md
  - comparisons/mt023-private-llm-platform-alignment.md
  - product-description/dcim-core-platform-product-description.md
  - FIT041 Technical Requirements, Use Case Analysis, SLA & Prioritization, Definition of Baseline, SOP Definition
external_sources:
  - https://huggingface.co/unsloth/gemma-4-12B-it-qat-GGUF
  - https://ai.google.dev/gemma/docs/core/model_card_4
  - https://github.com/ggml-org/llama.cpp
confidence: high
contested: true
contradictions: [implementation-plan, staging-production-environment, mt023-private-llm-platform-alignment]
---

# DCIM Core Platform — Deployment & Implementation Plan v2.0

**Environment:** Development, Staging, Production  
**Document status:** Proposed implementation baseline  
**Repository path:** `plans/deployment-implementation-plan-dev-staging-production-v2.md`  
**Change policy:** add-only; dokumen existing tidak diubah oleh change set ini.

> **Perubahan utama v2:** Analytics & AI Engine menggunakan arsitektur **hybrid**. Python/statistical/ML services tetap menjadi deterministic analytics plane untuk scoring numerik, forecasting, PUE, anomaly detection, dan feature engineering. Local open LLM menjadi cognitive plane untuk RAG, explanation, evidence synthesis, tool selection, structured recommendation, dan natural-language interaction. Model baseline yang diminta adalah `unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL`, dengan promotion ke Production bergantung pada benchmark, security, grounding, failover, dan operational acceptance gates.

---

## 1. Executive Summary

DCIM Core Platform dibangun sebagai platform berlapis untuk visibility, control, analytics, automation, security, dan audit atas infrastruktur data center.

```text
Source Systems
  BMS / EPMS / EMS / NMS / Server / Storage / Virtualization / Cloud
  Access Control / Surveillance / Fire & Safety / ITSM / ERP / DMS
        ↓
Data Ingestion & Integration
  Collectors + NiFi + Kafka + Validation + Enrichment + DLQ + Lineage
        ↓
Authoritative Data and Evidence
  Asset Repository + CMDB + Time-Series + SIEM/Search + Object/Evidence Store
        ↓
Deterministic Analytics Plane
  Rules + Z-score + Isolation Forest + Forecasting + PUE + Capacity + Graph RCA
        ↓ scores, trends, evidence, topology context
DCIM LLM Intelligence Plane
  AI Gateway + Gemma 4 12B + Hybrid RAG + Tool Calls + Citations + Structured Output
        ↓ advisory recommendation only
Policy and Workflow Plane
  Temporal / TraceCat / n8n + Approval + Allowlist + Impact Check + Rollback
        ↓ controlled action
Presentation and Operations
  API Gateway + NOC / SOC / Facilities / Asset / CMDB / AI Copilot / Management
```

### 1.1 Core architectural decisions

| ID | Decision |
|---|---|
| ADR-001 | Dev dapat menggunakan Docker Compose/local Kubernetes; Staging dan Production menggunakan Kubernetes dengan Helm/Kustomize overlays dan GitOps. |
| ADR-002 | Dev, Staging, dan Production dipisahkan pada account/project, namespace, database, Kafka prefix, bucket, vector collection, service account, secret, dan network segment. |
| ADR-003 | PostgreSQL 16 adalah transactional system of record; Redis digunakan untuk cache/session; Kafka KRaft sebagai streaming backbone. |
| ADR-004 | Staging mirror Production architecture pada skala lebih kecil dan hanya menggunakan synthetic atau approved masked data. |
| ADR-005 | Production deployment menggunakan manual approval gate, canary/blue-green, tested rollback, dan post-deploy verification. |
| ADR-006 | Analytics & AI harus hybrid: deterministic analytics tetap authoritative untuk angka, alert threshold, dan safety logic; LLM tidak menjadi satu-satunya engine. |
| ADR-007 | Gemma 4 12B adalah default candidate untuk v2, bukan unconditional lock-in. Qwen/secondary model dari MT-023 dipertahankan sebagai comparative benchmark dan fallback sampai acceptance selesai. |
| ADR-008 | Facts yang berubah cepat berada di RAG dan tools; fine-tuning digunakan untuk behavior, terminology, output format, tool use, dan safety policy. |
| ADR-009 | LLM tidak menerima direct privileged credential, direct database write, atau direct OT command. Semua action melewati Workflow/Policy Gate. |
| ADR-010 | LLM outage tidak boleh menghentikan ingestion, monitoring, alerting, deterministic analytics, SIEM, atau workflow kritikal. |

### 1.2 Scope

Plan mencakup:

- Hardware requirements dan capacity planning.
- Dev/Staging/Production environment strategy.
- Base infrastructure, installation, configuration, CI/CD, GitOps, backup, DR, HA, clustering.
- Data Ingestion & Integration, Asset Repository, CMDB, SIEM/SOC, SOAR, Analytics & AI, Workflow Automation, External Integration, Monitoring & Observability, Web Dashboard.
- LLM/RAG architecture, corpus governance, tool layer, fine-tuning, model serving, evaluation, security, LLMOps, rollback.
- Migration, testing, UAT, cutover, hypercare, documentation, training, and operational handover.

### 1.3 Out of scope for the initial release

- LLM-controlled autonomous physical/OT actuation without approved workflow and human authorization.
- Full retraining of a foundation model from scratch.
- Embedding all raw telemetry/log events as the primary real-time query path.
- Production use of unreviewed documents, user conversations, secrets, or raw personal data as training corpus.
- Replacing proven deterministic controls with probabilistic model output.

---

## 2. Environment Strategy

### 2.1 Environment profile

| Aspect | Development | Staging | Production |
|---|---|---|---|
| Purpose | Coding, unit tests, connector prototypes, prompt/tool development | Integration, UAT, model/RAG bake-off, performance, security, failover rehearsal | Live operations, HA, DR, governed corpus/model, 24×7 support for critical paths |
| Data | Synthetic fixtures only | Synthetic or approved masked snapshots | Live authoritative data |
| Orchestration | Docker Compose or local K8s | Kubernetes | Kubernetes HA |
| HA | Not required | Selected parity tests | Required for critical services |
| LLM mode | Optional local single instance | 1–2 instances, shadow/advisory | 2+ replicas, advisory/read-only initially |
| Deployment | Developer-triggered | Automated after CI | Manual approval + blue-green/canary |
| Access | Developer RBAC | QA/UAT/Engineering RBAC | Least privilege, MFA/SSO, bastion/VPN |
| SLA | None | Business-hours support | Per component SLO/SLA |

### 2.2 Isolation requirements

1. Separate VLAN/subnet and firewall policy per environment.
2. Separate secrets, certificates, database users, Kafka topics, object buckets, vector collections, and IAM roles.
3. Production has no outbound access to Dev/Staging.
4. Staging may only receive masked snapshots through an approved one-way transfer workflow.
5. No Production credentials in developer `.env`, CI logs, prompt templates, or vector metadata.
6. NetworkPolicies default deny; allow only documented service flows.
7. Every resource is tagged with environment, owner, data classification, cost center, and retention policy.

### 2.3 Naming conventions

```text
Namespace: dcim-dev | dcim-stg | dcim-prd
Kafka:     dev.dcim.* | stg.dcim.* | prd.dcim.*
Database:  dcim_dev_* | dcim_stg_* | dcim_prd_*
Bucket:    dcim-dev-* | dcim-stg-* | dcim-prd-*
Qdrant:    dcim_dev_<domain> | dcim_stg_<domain> | dcim_prd_<domain>
Model:     <model>-<revision>-<quant>-<environment>
Corpus:    corpus-<domain>-<yyyy.mm.dd>-<manifest-sha>
Prompt:    prompt-<usecase>-v<major.minor>
```

---

## 3. Hardware Requirements

Sizing berikut adalah planning baseline. Final sizing wajib divalidasi menggunakan event volume, average event size, EPS, active CI/asset count, query concurrency, retention, replication, index overhead, model context, and 30% minimum headroom.

### 3.1 Minimum platform sizing — core foundation

| Component | Nodes | vCPU/node | RAM/node | Storage/node | Network |
|---|---:|---:|---:|---:|---:|
| PostgreSQL primary/replica | 2 | 2 | 8 GB | 100 GB SSD | 1 Gbps |
| Redis primary/replica | 2 | 1 | 4 GB | 20 GB SSD | 1 Gbps |
| Kafka KRaft | 3 | 2 | 8 GB | 200 GB SSD | 1 Gbps |
| NiFi | 1 | 2 | 4 GB | 50 GB SSD | 1 Gbps |
| Elasticsearch/OpenSearch | 3 | 2 | 8 GB | 200 GB SSD | 1 Gbps |
| Prometheus | 1 | 1 | 4 GB | 50 GB SSD | 1 Gbps |
| Grafana | 1 | 1 | 2 GB | 10 GB SSD | 1 Gbps |
| Vault | 1 | 1 | 2 GB | 20 GB SSD | 1 Gbps |
| **Core minimum** | — | **±22 vCPU** | **±80 GB** | **±1 TB SSD** | **1 Gbps** |

Core minimum tidak termasuk full application stack, SIEM/SOAR capacity, long-term archive, NVR/video retention, model training, or Production GPU.

### 3.2 Environment hardware profile

| Environment | Compute | RAM | Usable SSD | Archive/Backup | GPU | Internal Network |
|---|---:|---:|---:|---:|---:|---:|
| Dev | 16–24 vCPU | 64–96 GB | 1–2 TB | 1–2 TB | Optional 16 GB VRAM | 1 Gbps |
| Staging | 48–80 vCPU | 192–256 GB | 4–8 TB | 5–10 TB | 1 × 24–48 GB VRAM | 10 Gbps recommended |
| Production pilot, 430–1,000 EPS | 140–220 vCPU | 512–768 GB | 15–25 TB | 30–60 TB | 2 × 24–48 GB VRAM on separate nodes | 10/25 Gbps |
| Production scale, 5,000–15,000 EPS | Capacity-model driven | Capacity-model driven | ILM/retention driven | Object archive | Benchmark driven multi-GPU | 25 Gbps recommended |

### 3.3 LLM/GPU profile

| Use | Baseline |
|---|---|
| Developer/PoC | 16 GB VRAM or 32–64 GB system RAM for CPU/offload testing; bounded context. |
| Staging | 24–48 GB VRAM, context default 16K–32K, one primary replica plus optional fallback. |
| Production pilot | Two inference nodes, each 24–48 GB VRAM, separate failure domains, load balancer and queue. |
| Higher concurrency/context | Benchmark 48 GB+ accelerators, tensor parallel serving, continuous batching, and KV-cache capacity. |
| Fine-tuning | Dedicated non-Production training GPU pool; isolate from serving. Use LoRA/QLoRA, not GGUF as the primary trainable artifact. |

The selected `UD-Q4_K_XL` GGUF is a serving artifact. Training should start from an approved trainable checkpoint; adapter is merged, evaluated, signed, and exported to the serving format.

### 3.4 Network requirements

| Zone/Flow | Requirement |
|---|---|
| User → Gateway | HTTPS 443 via WAF/reverse proxy, SSO/OIDC, rate limiting. |
| Collector → NiFi/Kafka | TLS/mTLS, source allowlist, protocol-specific ports. |
| Kafka inter-broker/controller | Dedicated cluster network, TLS/SASL, low latency. |
| App → PostgreSQL/Redis | Internal-only, TLS, service account, NetworkPolicy. |
| Model/RAG → tools | Read-only service APIs through AI Gateway, no arbitrary egress. |
| Admin | Bastion/VPN, MFA, session recording, no public SSH. |
| Time | Redundant NTP mandatory for correlation and audit. |
| DNS/PKI | Internal DNS, automated certificate lifecycle, revocation and rotation. |

### 3.5 Storage and retention

| Data | Baseline Retention | Storage Pattern |
|---|---|---|
| Kafka raw events | 7 days | Replication factor 3, encrypted disks |
| Kafka validated/enriched | 14–30 days | Replayable topics |
| DLQ | 30 days or until disposition | Kafka + error metadata store |
| Time-series raw | 90 days | TimescaleDB/InfluxDB hypertables |
| Time-series aggregates | 1–5 years | Hourly/daily aggregates/object archive |
| SIEM hot | 90 days | Elasticsearch/OpenSearch hot/warm |
| SIEM archive | 1–5 years by compliance | Object storage with integrity controls |
| CMDB | Lifecycle + history | PostgreSQL PITR |
| Asset/Audit | 5–7 years where financial/compliance requires | PostgreSQL + immutable archive |
| Workflow audit | Minimum 1 year; critical actions longer | PostgreSQL + immutable log |
| RAG corpus | Active + prior approved releases | Source docs + manifest + vector snapshots |
| Model artifacts | All Production releases | Registry/object storage, checksums, signatures |
| Query/audit traces | According to privacy/security policy | Restricted log store; redact secrets and sensitive data |

Storage formula:

```text
Daily raw = EPS × average event bytes × 86,400
Usable hot = daily raw × hot days × index overhead × replication × headroom
Archive = daily raw × archive days × compression factor
Vector = chunks × embedding dimensions × bytes/dimension × index overhead × replicas
LLM capacity = model weights + KV cache + runtime buffers + batch/concurrency headroom
```

---

## 4. Architecture Stack and Prerequisites

### 4.1 Technology baseline

| Layer | Baseline |
|---|---|
| Container | Docker; Kubernetes for Staging/Production |
| IaC/GitOps | Terraform/Ansible as applicable, Helm/Kustomize, Argo CD or equivalent |
| Relational | PostgreSQL 16, PgBouncer |
| Cache | Redis 7 with Sentinel/managed HA |
| Streaming | Kafka 3.x KRaft, Schema Registry recommended |
| Data Flow | Apache NiFi; optional Flink/Python workers |
| Search/SIEM | Wazuh + Elasticsearch/OpenSearch |
| Time-series | TimescaleDB or InfluxDB |
| Monitoring | Prometheus, Alertmanager, Grafana |
| Tracing/Logs | OpenTelemetry, centralized logs, optional Jaeger/Tempo |
| Secrets | HashiCorp Vault; Kubernetes Secrets only for bootstrap/integration |
| API | FastAPI/Go services, OpenAPI, API Gateway |
| Frontend | Vue 3 or approved React baseline |
| Workflow/SOAR | Temporal/TraceCat; n8n for governed low-code integration |
| LLM serving | `llama.cpp` OpenAI-compatible server baseline; optimized vLLM-compatible artifact only after benchmark |
| Vector/RAG | Qdrant for Staging/Production; lexical search with PostgreSQL FTS/OpenSearch; reranker |
| Model lifecycle | Model registry, artifact store, eval pipeline, corpus/prompt/policy/tool registry |

### 4.2 Mandatory prerequisites

- Approved target architecture and data flow diagram.
- Finalized source inventory, owner, protocol, data classification, EPS estimate, and maintenance window.
- DNS, NTP, internal CA, certificate automation, load balancer, backup repository.
- Kubernetes clusters and storage classes for Staging/Production.
- Container registry and model artifact mirror that do not depend on public internet at runtime.
- SSO/OIDC groups and RBAC matrix.
- Vault initialized with secure unseal/recovery process.
- Kafka, PostgreSQL, Redis, object storage, Qdrant, and search backup/restore design.
- Approved data retention and privacy policy.
- Approved LLM acceptable-use policy, prohibited actions, and escalation path.
- Named owners for model, corpus, prompt, tool, data source, workflow, and security response.

---

## 5. HA, Clustering, Backup, and DR

### 5.1 Production HA requirements

| Component | Production Pattern | Failover Gate |
|---|---|---|
| Kubernetes control plane | 3+ control-plane nodes | Node loss does not stop scheduling/API |
| PostgreSQL | Primary + 2 replicas or managed HA; PgBouncer | Automated promotion, no split brain, tested PITR |
| Redis | Primary/replicas + Sentinel or managed HA | Session/cache failover within target |
| Kafka | 3+ brokers, RF=3, min ISR=2 | Broker loss without data loss; ISR alert |
| NiFi | 2–3 node cluster when required by workload | Queue survives node loss |
| Elasticsearch/OpenSearch | 3+ nodes, shard replicas | Cluster remains yellow/green under node loss |
| Wazuh | Manager/indexer cluster | Agent/event ingestion continues |
| Temporal/TraceCat | Multiple workers/API replicas; durable DB | Workflow resumes without duplicate unsafe action |
| Qdrant | 3-node/replicated collections or approved managed topology | Collection remains readable under node loss |
| AI Gateway | 2+ stateless replicas | Requests route to healthy model/tool service |
| LLM inference | 2 replicas in separate failure domains | Fallback model or degraded advisory mode |
| Dashboard/API | 2+ replicas behind LB | Rolling upgrade with no user outage |
| Monitoring | HA/federated Prometheus, redundant Alertmanager | Alerts continue during one instance loss |
| Vault | 3-node integrated storage or managed HA | Auto-unseal and audit continuity |

### 5.2 DR targets

| Environment | RPO | RTO | Strategy |
|---|---:|---:|---|
| Dev | 24 hours | 8 hours | Rebuild from Git/IaC |
| Staging | 24 hours | 8 hours | Rebuild + selected backups |
| Production platform | ≤1 hour | ≤4 hours | Cross-site/offsite backups and documented recovery |
| Critical PostgreSQL data | 5–15 minutes target | 30–60 minutes target | WAL archive + replica + PITR |
| Configuration/GitOps | Near zero | ≤30 minutes | Git repository and registry mirror |
| Vector corpus | ≤24 hours or corpus release interval | ≤4 hours | Restore snapshot or deterministic rebuild from signed manifest |
| Model artifacts | Per release | ≤1 hour | Registry/object mirror and pinned revision |

### 5.3 Backup matrix

- PostgreSQL: continuous WAL, daily full/logical, monthly restore rehearsal.
- Redis: RDB + AOF according to persistence need; do not treat cache as sole source of truth.
- Kafka: topic configuration backup, selected critical topic export, source replay strategy.
- Search/SIEM: snapshot lifecycle to object storage.
- NiFi: versioned flow definitions and parameter contexts.
- Vault: integrated storage snapshots, recovery keys process, audit log archive.
- Qdrant: collection snapshots plus corpus manifest and embedding version.
- Models: weights/adapters/tokenizer/config/license/manifest/checksum/signature.
- Workflow: definitions, versions, connection metadata, DB, audit, compensation state.
- Grafana/Prometheus: dashboards, rules, Alertmanager configuration in Git.

No component is accepted until a restore test demonstrates usable data and documented recovery time.

---

## 6. Repository and Project Structure

```text
dcim-core/
├── apps/
│   ├── api-gateway/
│   ├── asset-repository/
│   ├── cmdb/
│   ├── analytics/
│   ├── ai-gateway/
│   ├── workflow/
│   ├── siem-bridge/
│   └── frontend/
├── data-platform/
│   ├── kafka/
│   ├── nifi/
│   ├── schemas/
│   ├── lineage/
│   ├── timeseries/
│   └── search/
├── ai/
│   ├── inference/
│   ├── embeddings/
│   ├── reranker/
│   ├── rag/
│   ├── tools/
│   ├── prompts/
│   ├── policies/
│   ├── evaluations/
│   ├── training/
│   └── registry/
├── integrations/
├── workflows/
├── observability/
├── security/
├── infrastructure/
│   ├── terraform/
│   ├── ansible/
│   ├── helm/
│   ├── kustomize/base/
│   └── kustomize/overlays/{dev,staging,production}/
├── migrations/
├── tests/
├── docs/
├── Makefile
├── docker-compose.yml
└── .env.example
```

Rules:

1. No real secret in Git.
2. All images, models, schemas, prompts, policies, tools, and workflows are version-pinned.
3. Environment differences are overlays, not copied manifests.
4. Database and index changes use forward/rollback migration plans.
5. Model/corpus/prompt/tool releases are independently versioned and auditable.
6. Every connector and tool has owner, timeout, retry, rate limit, data classification, and test contract.

---

## 7. Pre-Implementation Checklist

### 7.1 Governance and readiness

- [ ] Scope, success criteria, exclusions, owners, RACI, and budget approved.
- [ ] Source-system inventory complete with protocol, endpoint, owner, credentials, EPS, payload, schema, and maintenance window.
- [ ] Dev/Staging/Production environments provisioned and isolated.
- [ ] Network, firewall, DNS, NTP, PKI, certificates, load balancer, proxy, and outbound allowlist approved.
- [ ] SSO/OIDC groups, service accounts, RBAC, privileged-access process, and break-glass procedure approved.
- [ ] Retention, privacy, audit, data residency, backup, RPO/RTO, and destruction policies approved.
- [ ] Production capacity model reviewed with at least 30% headroom.
- [ ] Vendor/open-source license and model license review complete.
- [ ] Threat model covers IT/OT convergence, API abuse, supply chain, prompt injection, RAG poisoning, tool abuse, model extraction, and data exfiltration.
- [ ] Model/corpus use cases, non-use cases, risk tier, human approval, and kill switch approved.

### 7.2 Engineering readiness

- [ ] Repositories, branch protection, code review, CI runners, registries, artifact stores, and GitOps configured.
- [ ] IaC plan/apply and destroy protections tested.
- [ ] Base images and model artifacts mirrored internally, scanned, and signed.
- [ ] Schema Registry and compatibility policy available.
- [ ] Test data and masked snapshots approved.
- [ ] Observability standards, SLOs, alert routes, on-call rota, and escalation contacts defined.
- [ ] Runbook templates and evidence requirements defined.

---

## 8. Installation and Configuration Sequence

### Phase A — Foundation

1. Provision network zones, DNS, NTP, PKI, bastion, load balancer, Kubernetes, storage classes, registry, backup repository.
2. Deploy Vault and establish secret engines, policies, audit, recovery, and rotation.
3. Deploy PostgreSQL HA, PgBouncer, migrations framework, backup and PITR.
4. Deploy Redis HA with authentication and TLS.
5. Deploy Kafka KRaft cluster, TLS/SASL, ACLs, quotas, topic defaults, exporters.
6. Deploy NiFi and versioned flow registry/parameter contexts.
7. Deploy Elasticsearch/OpenSearch, ILM, snapshots, security, and dashboards.
8. Deploy Prometheus, Alertmanager, Grafana, exporters, centralized logs, traces, and synthetic probes.
9. Validate component health, security, node failure, backup, and restore.

### Phase B — Application services

1. Deploy API Gateway, SSO integration, rate limiting, request validation, audit middleware.
2. Deploy Asset Repository database, API, cache, bulk import, lifecycle, contract/warranty, reconciliation, and audit.
3. Deploy CMDB data model, CI/relationship APIs, topology, impact, reconciliation, service mapping, cache, and health metrics.
4. Deploy common schema, validation, enrichment, DLQ, lineage, and router services.
5. Deploy source connectors in priority waves.
6. Deploy SIEM/SOC stack, correlation, case and SOAR bridge.
7. Deploy deterministic analytics services and time-series pipeline.
8. Deploy AI/RAG foundation, Gemma serving, AI Gateway, tools, and evaluation stack.
9. Deploy workflow automation, approvals, runbooks, notifications, compensation and rollback.
10. Deploy dashboard views and AI Copilot UI.

### Phase C — Post-install configuration

- Replace all bootstrap credentials.
- Apply RBAC and data classification policies.
- Load approved schema, reference data, topic ACLs, index templates, retention and backup policies.
- Load only approved runbooks, detection rules, workflows, prompts, tools, corpus manifests, and model artifacts.
- Run vulnerability scan, SBOM review, dependency/license scan, and configuration benchmark.
- Run E2E, failover, restore, performance, security, RAG quality, prompt injection, unauthorized tool, and rollback tests.
- Produce evidence package and sign-off.

---

## 9. Implementation Work Packages

## 9.1 Infrastructure & Foundation

**Deliverables**

- IaC and GitOps repositories.
- Kubernetes namespaces, quotas, limits, PDBs, NetworkPolicies, storage classes.
- PostgreSQL, Redis, Kafka, NiFi, search, object storage, Vault, Prometheus/Grafana.
- PKI, DNS, NTP, LB, bastion, registry, backup and DR.
- Base SLO dashboards and runbooks.

**Acceptance**

- No critical SPOF in Production path.
- Node/component failover passes.
- Backup/restore passes.
- TLS and authentication enforced.
- All targets monitored and alert routes tested.

## 9.2 Data Ingestion & Integration

**Scope**

- Common event schema and schema compatibility.
- BMS/EPMS/EMS, NMS, server/storage, virtualization/cloud, access control/surveillance, ITSM/ERP/DMS connectors.
- Kafka raw, validated, enriched, DLQ, CMDB, asset, SIEM, analytics, workflow topics.
- Validation: schema, mandatory, type, range, format, uniqueness, referential integrity, timestamp freshness.
- Enrichment: CI, asset, location, owner, criticality, SLA, maintenance window.
- Retry, DLQ, reprocessing, lineage and data-quality scorecard.

**Targets**

- Sustained throughput baseline ≥5,000 records/sec where required; platform design supports 10,000 EPS target and SIEM scaling toward 15,000 EPS.
- P1/P2 NRT SLA ≤60 seconds; internal critical streaming benchmark should be substantially lower.
- Data accuracy ≥99.9%; accepted schema integrity 100%.
- No silent drop; every failed record has disposition.

## 9.3 Asset Repository

**Scope**

- Asset master, location, financial, contract, warranty, lifecycle, audit.
- CRUD, search, bulk import, enrichment, reporting.
- Reconciliation with CMDB, discovery, ERP/procurement, and physical audit.
- Barcode/RFID integration where available.

**Targets**

- ≥100,000 assets baseline.
- Lookup p99 ≤200 ms; cached enrichment target ≤50 ms.
- Inventory accuracy and warranty/contract completeness measured.
- Financial and lifecycle writes require granular RBAC and immutable audit.

## 9.4 CMDB

**Scope**

- CI taxonomy, mandatory attributes, lifecycle, relationships, topology, impact, service mapping, reconciliation, data quality.
- PostgreSQL adjacency/recursive CTE baseline with Redis cache; graph database only after benchmark proves requirement.

**Targets**

- ≥150,000 CI and ≥500,000 relationships baseline.
- Standard API p99 ≤500 ms.
- Impact analysis p99 ≤500 ms for accepted depth/profile.
- P1 CI accuracy ≥99.5%; critical relationship integrity 100%.
- Orphan, duplicate, stale, conflicting source and cycle checks active.

## 9.5 SIEM/SOC

**Scope**

- Wazuh agents/managers, Syslog, Kafka, normalization, search/index lifecycle.
- Detection-as-code, correlation, UEBA inputs, physical-cyber correlation, threat intelligence, compliance.
- Case management and SOAR/Workflow integration.

**Targets**

- 10,000 EPS baseline; scale test to approved peak, with 15,000 EPS target where required.
- 90-day hot retention; archive according to compliance.
- Alert delivery and SOC response meet severity SLA.
- Every automated response includes CI criticality and impact context.

## 9.6 SOAR Platform

**Scope**

- TraceCat/Temporal orchestration, case integration, enrichment, playbooks, notifications, evidence, compensation.
- OT-safe rule: no unapproved reboot, power action, setpoint change, network isolation, credential disable, or configuration change on critical DCIM assets.

**Acceptance**

- Durable workflow state survives worker restart.
- Retry is idempotent.
- Approval, timeout, escalation, rollback and evidence are complete.
- Playbook change is versioned, reviewed, tested in Staging, and signed off.

## 9.7 Analytics & AI Engine — Hybrid Architecture

### 9.7.1 Deterministic analytics plane

Remains authoritative for:

- Time-series aggregation and data readiness.
- Z-score, statistical thresholds, Isolation Forest and approved ML anomaly scoring.
- Capacity, energy/PUE, utilization and trend calculations.
- Forecasting and failure probability.
- CMDB graph traversal and correlation-assisted RCA.
- Numerical confidence, threshold, and safety constraints.

Services publish structured evidence, not only prose:

```json
{
  "analysis_id": "uuid",
  "event_type": "temperature_anomaly",
  "affected_ci": "CRAC-JKT-03",
  "anomaly_score": 0.94,
  "baseline": 21.8,
  "current_value": 28.6,
  "trend_minutes": 17,
  "related_events": ["PDU-JKT-04 load increased 13%"],
  "impacted_services": ["Payment Cluster"],
  "recommended_runbooks": ["RB-COOLING-004"],
  "evidence_refs": ["metric-window-9821", "topology-snapshot-401"]
}
```

### 9.7.2 LLM intelligence plane

Responsibilities:

- Explain anomalies, predictions, topology impact, incidents, compliance findings, capacity and PUE trends.
- Retrieve current approved documentation with citations.
- Select read-only tools and assemble multi-source evidence.
- Produce structured summaries, hypotheses, recommendations, draft tickets, draft change plans, and management narratives.
- Never replace the source of truth or deterministic score.

Baseline model candidate:

```text
unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL
```

Serving baseline:

```text
User/API → AI Gateway → policy/RBAC → retrieval/tools → context builder
         → llama.cpp OpenAI-compatible inference → output validator
         → citation/grounding checks → response/audit
```

Production may use another optimized serving artifact after comparative benchmark, provided model identity, behavior, license, quality, and rollback are controlled.

### 9.7.3 RAG knowledge sources

Approved corpus domains:

- DCIM-Wiki active pages and reference designs.
- FIT041 Technical Requirements, Use Case Analysis, SLA/Prioritization, Baseline, SOP.
- Architecture Decision Records.
- OpenAPI/API documentation, schemas and data dictionaries.
- Approved operational runbooks and SOAR playbooks.
- Detection-rule documentation.
- Approved incident postmortems and known-error records.
- Installation, backup, restore, DR, troubleshooting and UAT evidence.

Mandatory metadata:

```json
{
  "document_id": "reference-design-block7",
  "version": "2.0",
  "environment": "production",
  "classification": "internal",
  "owner": "MLOps",
  "effective_date": "2026-07-14",
  "supersedes": "version-1.0",
  "allowed_roles": ["operator", "architect", "auditor"],
  "source_path": "reference-designs/block7-analytics-ai-engine.md",
  "manifest_sha": "sha256"
}
```

Retrieval pipeline:

1. Authenticate and derive user roles/domain/environment.
2. Classify intent and risk tier.
3. Apply metadata and classification filters before retrieval.
4. Run hybrid semantic + lexical search.
5. Rerank, deduplicate, prioritize current/effective sources.
6. Reject revoked, superseded, expired, unapproved, cross-role, or untrusted sources.
7. Assemble bounded context with source IDs and timestamps.
8. Invoke model.
9. Validate claims, citations, schema, prohibited content, and tool intent.
10. Audit model, corpus, embedding, reranker, prompt, policy and tool versions.

### 9.7.4 Tool retrieval for live state

Dynamic facts are fetched from read-only APIs, not trusted from embeddings:

- `query_cmdb_topology(ci_id, depth)`
- `calculate_impact(ci_id, scenario)`
- `get_asset_context(asset_id)`
- `query_timeseries(metric, ci_id, window)`
- `get_active_alerts(severity, site)`
- `search_siem_events(query, time_range)`
- `get_incident_history(ci_id)`
- `get_current_sla(priority, component)`
- `get_runbook(alert_type)`
- `get_workflow_status(execution_id)`
- `create_draft_ticket(...)`

Tool controls:

- JSON Schema arguments and output.
- Read-only credentials by default.
- Fixed host allowlist; no arbitrary URL, SQL, shell, SSH, or file access.
- Per-tool RBAC, timeout, retry, circuit breaker, query budget and rate limit.
- Sensitive-field redaction before model context.
- Every call records user, intent, arguments hash, result reference, status and latency.
- Write-capable tools exist only behind Workflow Automation and approval gates.

### 9.7.5 Training and adaptation

**Stage 1 — RAG-only baseline**

- Validate base model language, retrieval, citations, tool selection, latency and safety before tuning.

**Stage 2 — LoRA/QLoRA behavior tuning**

Train behavior such as:

- DCIM terminology and Bahasa Indonesia/technical English style.
- Incident, RCA, change-risk, capacity and management report formats.
- P1–P4 and severity reasoning.
- Correct tool selection and JSON output.
- Citation and evidence discipline.
- Refusal and escalation for prohibited actions.
- Separation of fact, inference, assumption, and recommendation.

Do not use fine-tuning to memorize changing CI, asset, topology, metric, incident, SLA, or runbook state.

**Stage 3 — controlled continuous improvement**

Eligible feedback:

- Analyst-approved RCA and incident summaries.
- Accepted/rejected recommendations with reason.
- Tool traces and retrieval failures.
- Approved new runbooks and architecture decisions.

Every training dataset requires provenance, classification, de-identification, owner approval, split integrity, data card, license review and reproducible build.

### 9.7.6 LLM output contract

```json
{
  "summary": "string",
  "classification": "P1|P2|P3|P4",
  "confidence": 0.87,
  "assumptions": ["string"],
  "affected_cis": ["CI-UPS-001"],
  "evidence": [
    {
      "source_type": "timeseries|cmdb|siem|document|tool",
      "reference": "metric-window-9821",
      "timestamp": "2026-07-14T08:21:00Z"
    }
  ],
  "recommended_actions": [
    {
      "action": "create_maintenance_ticket",
      "risk": "low",
      "requires_approval": false
    },
    {
      "action": "change_cooling_setpoint",
      "risk": "high",
      "requires_approval": true
    }
  ]
}
```

### 9.7.7 Safety requirements

- Advisory/read-only default.
- Every factual claim cites evidence and timestamp.
- Retrieved documents are untrusted data; embedded instructions are ignored.
- No secrets, passwords, private keys, raw tokens or unnecessary PII in prompts.
- No direct DB write, shell, SSH, arbitrary URL, OT credential or network device credential.
- P1/P2 and destructive actions require approved workflow, impact check, maintenance window, allowlist, human approval and rollback.
- Model failure, low confidence, missing evidence or conflicting sources produces escalation, not fabricated certainty.
- Kill switch disables model/tools without affecting critical deterministic services.

### 9.7.8 Model and RAG acceptance gates

| Gate | Minimum evidence |
|---|---|
| Model artifact | Pinned revision, SHA-256, license, model card, SBOM, vulnerability scan, signature |
| Quality | Domain benchmark, Bahasa Indonesia, RCA, tool selection, structured output, long-context, hallucination tests |
| Retrieval | Recall@k/nDCG sample, current-source preference, citation validity, RBAC isolation, freshness, supersession |
| Grounding | Required evidence coverage; unsupported-claim and contradiction rate below approved threshold |
| Security | Prompt injection, RAG poisoning, exfiltration, cross-role retrieval, arbitrary tool, model extraction tests pass |
| Performance | TTFT, tokens/sec, p50/p95/p99 latency, concurrency, queue, VRAM, KV cache under workload profile |
| Resilience | Replica failure, fallback model, Qdrant failure, tool timeout, degraded mode and rollback pass |
| Operations | Dashboards, alerts, runbooks, on-call, model/corpus rollback and incident process complete |

## 9.8 Workflow Automation

- State machine and durable persistence.
- ITSM bidirectional sync.
- Multi-level approval, timeout and escalation.
- Runbook-as-code and versioning.
- Safety guards, impact assessment, allowlist, dry-run and compensation.
- Temporal/TraceCat for critical durable workflows; n8n limited to approved use cases consistent with its HA/security capabilities.
- Full execution audit and evidence.

## 9.9 Security Hardening

- CIS/hardening baselines for host, Kubernetes, database, Kafka, NiFi, search, Vault and model servers.
- TLS/mTLS, strong cipher policy, certificate rotation.
- SSO/OIDC, MFA, granular RBAC, service identity, least privilege.
- Image/model/dependency scanning, SBOM, signature verification and admission control.
- NetworkPolicy, egress allowlist, WAF, API quotas, bot/tool abuse limits.
- Secrets in Vault; dynamic credentials where possible.
- Immutable audit for admin, data, model, corpus, prompt, tool, workflow and security-rule changes.
- Secure model/corpus supply chain and artifact quarantine.
- Log redaction and privacy controls.

## 9.10 External Integration

Adapter pattern with contract tests for:

- ServiceNow/Jira/other ITSM.
- SAP/Oracle/ERP.
- DMS.
- NMS and discovery.
- VMware/Hyper-V/Proxmox.
- AWS/GCP/Azure where approved.
- BMS/EPMS/EMS and physical security platforms.

Each integration defines owner, direction, protocol, auth, schema, rate, idempotency, retry, DLQ, circuit breaker, health, SLA, data classification, retention and decommission plan.

## 9.11 Monitoring & Observability

Metrics by domain:

| Domain | Key signals |
|---|---|
| Platform | CPU, RAM, disk, network, node/pod health, saturation, certificates |
| PostgreSQL | availability, connections, locks, query latency, cache hit, replication lag, WAL/archive |
| Kafka | throughput, ISR, under-replicated partitions, lag, disk, request latency, controller |
| NiFi | queue, backpressure, processor errors, provenance, flow latency |
| DI&I | source freshness, validation pass, enrichment, DLQ, end-to-end latency |
| CMDB | API latency, CI/relationship count, orphan/stale/duplicate, reconciliation conflicts |
| Asset | lookup/import latency, inventory variance, warranty/contract completeness |
| SIEM | EPS, source coverage, parse failure, correlation latency, alert delivery, false positives |
| Workflow | queue, running, success/failure, retry, approval wait, compensation, MTTE |
| Deterministic analytics | scoring latency, prediction quality, drift, data readiness, feature quality |
| LLM/RAG | TTFT, tokens/sec, p95/p99, queue, context tokens, VRAM, retrieval latency, citation coverage, groundedness, tool success/deny, injection attempts, model/corpus/prompt/policy version |
| Dashboard | API latency, errors, WebSocket/SSE status, frontend performance, auth failures |

Observability must include RED/USE metrics, centralized logs, trace IDs, correlation IDs, synthetic probes, SLO burn-rate alerts, and runbook links.

## 9.12 Documentation & Training

Mandatory deliverables:

- Architecture, network, data flow, security and deployment diagrams.
- Installation, configuration, backup, restore, DR, upgrade, rollback and troubleshooting guides.
- Data dictionary, schema catalog, source/target mapping, lineage, retention, ownership.
- API/OpenAPI and integration contracts.
- CMDB and Asset data models.
- Detection rules and SOAR playbooks.
- Workflow designer/operations guides.
- Model card, corpus card, prompt/policy/tool registry, RAG ingestion, evaluation, red-team, fine-tuning and rollback guides.
- NOC, SOC, Facilities, Platform, Data, Security, MLOps/LLMOps, Auditor and Service Desk training.
- Hands-on recovery, failover, incident and model/corpus rollback exercises.

## 9.13 Web Dashboard

Views:

- NOC: real-time health, alerts, capacity, service impact.
- SOC: security events, incidents, compliance, investigation.
- Facilities: power, cooling, environment, alarms and site/rack context.
- Asset: inventory, lifecycle, warranty, contracts, audit.
- CMDB Explorer: search, topology, impact, service maps.
- Analytics: anomaly, prediction, RCA, capacity, energy/PUE.
- AI Copilot: evidence-grounded explanations, citations, tool traces, confidence, draft recommendations.
- Workflow: execution, approvals, SLA countdown, audit and rollback.
- Management: SLA/KPI, risk, capacity, cost, energy and trend narratives.

The UI must visibly distinguish deterministic result, retrieved evidence, LLM inference, assumption, confidence and actionable recommendation.

---

## 10. CI/CD, Promotion, and Release Management

### 10.1 Pipeline

```text
Commit/PR
  → lint + unit + schema + policy tests
  → SAST + dependency + secret + license scan
  → build signed image/artifact/SBOM
  → integration and contract tests
  → deploy Dev
  → automated E2E
  → deploy Staging
  → performance + resilience + security + UAT + AI evaluation
  → manual Production approval
  → canary/blue-green
  → post-deploy verification
  → promote or rollback
```

### 10.2 Independent promotion units

- Application image.
- Infrastructure/chart/configuration.
- Database migration.
- Kafka/schema release.
- Detection rule and playbook.
- Workflow definition.
- Model artifact.
- Corpus manifest/vector collection.
- Embedding/reranker.
- Prompt/policy/tool bundle.

A model release does not automatically promote corpus, prompt or tool changes. Each unit has compatibility matrix and rollback.

### 10.3 Production gates

- 100% required tests pass.
- No unresolved Critical/High security finding unless formally accepted.
- Backup and rollback point verified.
- Capacity and SLO tests pass.
- DB migration backward/forward compatibility verified.
- RAG current-source, citation, RBAC and injection tests pass.
- Model, corpus, prompt, policy and tool versions pinned.
- Change record, owner, maintenance window and communication approved.

---

## 11. Data Migration, Seeding, and Source Onboarding

### 11.1 Migration flow

```text
Inventory → classify → extract → quarantine → map → cleanse → validate
→ dry-run → owner review → load → reconcile → sign-off → monitor
```

Rules:

- No destructive delete during initial migration.
- Preserve source identifier, lineage and reconciliation result.
- Unknown/ambiguous records are quarantined.
- Use idempotent upsert and controlled merge.
- Define precedence per attribute and source.
- Rehearse rollback before Production load.

### 11.2 Onboarding waves

1. Foundation reference data: site, room, rack, taxonomy, owners.
2. Asset master and contracts.
3. P1/P2 CI and relationships.
4. BMS/EPMS/EMS telemetry.
5. NMS/server/storage/virtualization.
6. SIEM/security and access control.
7. ERP/ITSM/DMS and other enterprise sources.
8. Historical incidents and approved knowledge corpus.

### 11.3 Knowledge corpus lifecycle

```text
Propose source → classify → security/license review → owner approval
→ parse/chunk → attach metadata → embed/index → evaluate
→ sign manifest → publish alias → monitor → supersede/revoke/archive
```

Revocation must remove or disable retrieval promptly and schedule embedding/index deletion according to policy.

---

## 12. Testing and Quality Gates

### 12.1 Mandatory tests

- Unit, integration, API contract, schema compatibility and migration tests.
- End-to-end source-to-dashboard/workflow tests.
- Performance, soak, burst and backpressure tests.
- HA, chaos, network partition, node failure and dependency timeout tests.
- Backup, restore, PITR and full DR rehearsal.
- RBAC, authentication, TLS, secret, vulnerability and penetration tests.
- Data-quality, idempotency, reconciliation, DLQ and replay tests.
- SIEM detection, alert, case and SOAR tests.
- Workflow approval, retry, idempotency, compensation, rollback and OT-safe tests.
- Model accuracy, drift, bias relevance, latency and resource tests.
- RAG retrieval, current-source, citation, grounding, injection, poisoning, cross-role and tool-abuse tests.
- Browser, accessibility, responsive and dashboard freshness tests.

### 12.2 Non-functional baseline

| Area | Target |
|---|---|
| DI&I availability | 99.95% for critical ingestion target |
| DI&I accuracy | ≥99.9% |
| Critical schema integrity | 100% accepted events |
| CMDB availability | ≥99.9% |
| Asset availability | ≥99.9% |
| SIEM availability | ≥99.9% |
| Workflow engine | 99.95% target for critical workflow path |
| Deterministic analytics | 99.5–99.9% according to priority and design |
| LLM advisory | ≥99.5% pilot target; failure cannot suppress critical operation |
| Production RPO/RTO | ≤1 hour / ≤4 hours platform target |

Where source documents contain different latency or availability targets, the strictest applicable target is tested or an ADR records the accepted profile by use case.

### 12.3 LLM/RAG evaluation set

Minimum categories:

- DCIM terminology and product architecture.
- Anomaly explanation.
- Predictive maintenance evidence.
- RCA and dependency reasoning.
- Capacity and PUE recommendation.
- SIEM incident triage.
- Change risk and impact.
- Runbook selection.
- Bahasa Indonesia and technical English.
- Fictitious entity/hallucination resistance.
- Conflicting and superseded sources.
- Missing evidence and low-confidence escalation.
- Structured JSON and citation validity.
- Tool choice, arguments and denial behavior.
- Prompt injection, poisoned document and unauthorized data request.

Production promotion requires signed evaluation report and risk acceptance.

---

## 13. Cutover, Rollback, and Hypercare

### 13.1 Cutover sequence

1. Freeze approved configuration/model/corpus/workflow releases.
2. Confirm backup, restore points, capacity, on-call and communication.
3. Load final delta and reconcile.
4. Enable read traffic and dashboards.
5. Enable ingestion by source wave.
6. Enable deterministic analytics.
7. Enable SIEM and workflow in controlled mode.
8. Enable Gemma/RAG in shadow mode and compare against approved answers/secondary model.
9. Promote AI Copilot to advisory users after quality and security sign-off.
10. Keep privileged actions disabled until separate approval.

### 13.2 Rollback triggers

- Data loss/corruption or unexplained reconciliation variance.
- Critical SLO or error-rate breach.
- Security finding, credential leakage or unauthorized access.
- Failed migration or incompatible schema.
- Model unsupported-claim/citation/tool error beyond threshold.
- Cross-role data exposure, stale/superseded source preference, prompt injection or tool-abuse failure.
- Workflow duplicates, unsafe target or failed compensation.

Rollback options:

- Traffic switch to previous application/model endpoint.
- GitOps revert.
- Database rollback/restore or forward fix per approved plan.
- Schema/topic compatibility rollback.
- Corpus alias switch to previous signed collection.
- Prompt/policy/tool bundle rollback.
- Disable AI tools and retain deterministic services.

### 13.3 Hypercare

- 14–30 day Production hypercare.
- Daily health, data quality, alert, incident, model/RAG and user feedback review.
- Dedicated escalation bridge for P1/P2.
- No major architecture/model/corpus change without emergency change control.
- Exit requires stable SLO, no unresolved critical defect, complete handover and accepted operational ownership.

---

## 14. Governance, RACI, and Timeline

### 14.1 Core RACI

| Activity | Accountable | Responsible | Consulted |
|---|---|---|---|
| Platform architecture | Solution Architect | Platform/DevOps | Security, Data, App teams |
| DI&I | Integration Lead | Integration Engineers | Source Owners, Data Governance |
| Asset | Asset Manager | Asset App/Data team | Finance, Procurement, Facilities |
| CMDB | CMDB Manager | CMDB Engineers | Service Owners, Operations |
| SIEM/SOC | Security Manager | SOC/Security Engineers | Platform, Source Owners |
| SOAR/Workflow | Process Owner | Automation Engineers | Security, Operations, Change Manager |
| Deterministic analytics | Analytics Lead | Data Scientists/MLOps | Operations, Capacity, Facilities |
| LLM/RAG | AI Product Owner | LLMOps/Knowledge Engineers | Security, Legal/License, Data Owners, SMEs |
| Corpus approval | Knowledge/Data Owner | Knowledge Engineer | Security, Compliance, SMEs |
| Model promotion | AI Product Owner | MLOps/LLMOps | Security, QA, Architecture |
| Production release | Change Authority | DevOps/Release Manager | All component owners |

### 14.2 Indicative timeline

The previous 15–18 day estimate remains useful only for a code skeleton. A governed Production rollout including integrations, HA/DR, SIEM/SOAR, Gemma/RAG/LLMOps, UAT and training is estimated at **20–28 weeks** with parallel teams and no procurement/access delay.

| Weeks | Wave | Outcome |
|---|---|---|
| 1–3 | Readiness & Foundation | Environments, network, PKI, K8s, registry, Vault, observability |
| 3–7 | Core Data Platform | PostgreSQL, Redis, Kafka, NiFi, search, object storage, schemas |
| 5–10 | DI&I + Asset + CMDB | Connectors, data quality, asset, CI, relationships, reconciliation |
| 8–13 | SIEM/SOC + SOAR/Workflow | Security ingestion, detection, cases, playbooks, approvals |
| 10–16 | Deterministic Analytics | Time-series, anomaly, prediction, RCA, capacity, energy |
| 12–18 | LLM/RAG Foundation | Corpus, embeddings, Qdrant, tools, AI Gateway, Gemma bake-off |
| 14–20 | Dashboard & Integrations | Views, Copilot, ITSM/ERP/DMS/NMS/cloud adapters |
| 19–23 | E2E/UAT | Performance, resilience, DR, security, AI evaluation |
| 23–28 | Cutover/Hypercare | Production promotion, operations handover, stabilization |

---

## 15. Risk Register and Stop Conditions

### 15.1 Key risks

| ID | Risk | Severity | Mitigation |
|---|---|---|---|
| R-01 | Source access/schema unavailable | High | Owner and contract readiness gate; mocks and staged onboarding |
| R-02 | Data quality undermines CMDB/analytics | Critical | Validation, lineage, reconciliation, data-owner sign-off |
| R-03 | Capacity underestimated | Critical | Load model, 30% headroom, soak/burst tests, scale plan |
| R-04 | n8n/community limitations conflict with critical HA/audit | Critical | Use Temporal/TraceCat for critical path; ADR and product boundary |
| R-05 | Gemma candidate underperforms MT-023 model | High | Comparative benchmark, fallback, no forced promotion |
| R-06 | LLM hallucinates or cites wrong/stale source | Critical | RAG/current-source filters, citations, grounding tests, human review |
| R-07 | Prompt injection/RAG poisoning | Critical | Signed manifests, treat corpus as data, policy outside model, red-team |
| R-08 | Unauthorized tool/action | Critical | Read-only tools, allowlist, schema, workflow gate, approval, audit |
| R-09 | Cross-role/classification data exposure | Critical | Pre-retrieval RBAC filters, tenant/domain isolation, tests |
| R-10 | Model/corpus supply-chain compromise | Critical | Internal mirror, checksums, signatures, scan, quarantine |
| R-11 | GPU procurement/serving performance delay | High | CPU/offload PoC, alternate serving, staged pilot, capacity benchmark |
| R-12 | Workflow unsafe on OT critical systems | Critical | OT-safe policy, impact check, maintenance window, human approval, rollback |

### 15.2 Stop conditions

Stop Production promotion and escalate when:

1. Critical architecture differences require changing multiple existing approved documents without owner decision.
2. Environment isolation, security zoning or least privilege cannot be implemented.
3. Capacity model cannot support approved EPS, retention or concurrency with headroom.
4. Backup/restore, PITR, failover or DR tests fail.
5. P1/P2 source data quality or CMDB relationship integrity is below acceptance.
6. Critical/High security findings remain unresolved without formal acceptance.
7. Workflow can duplicate or execute unsafe action without compensation.
8. LLM produces unsupported critical claims beyond threshold or cannot provide evidence.
9. RAG exposes unauthorized data or prefers revoked/superseded sources.
10. Prompt injection, RAG poisoning, secret leakage, arbitrary URL/shell/SQL or unauthorized tool tests fail.
11. Model artifact/license/provenance cannot be verified.
12. Operational owner, on-call, runbook or rollback authority is missing.

The Qwen-versus-Gemma difference is not an automatic stop condition because v2 treats it as a controlled benchmark/ADR with fallback. It becomes a stop condition only if stakeholders demand unconditional replacement without passing quality, security and capacity gates.

---

## 16. Final Delivery Acceptance Checklist

### Infrastructure

- [ ] Dev, Staging, Production are isolated.
- [ ] Kubernetes, storage, network, DNS, NTP, PKI, LB and bastion pass.
- [ ] PostgreSQL, Redis, Kafka, NiFi, search, Vault, monitoring and backup pass HA/restore tests.
- [ ] No plaintext secret or public management endpoint.

### Data and applications

- [ ] Source-to-store E2E flow passes with validation, enrichment, lineage and DLQ.
- [ ] Asset Repository CRUD, import, reconciliation, audit and enrichment pass.
- [ ] CMDB CI, relationships, topology, impact, service mapping, quality and reconciliation pass.
- [ ] SIEM ingestion, detection, alert, case, compliance and SOAR bridge pass.
- [ ] Deterministic analytics anomaly, prediction, RCA, capacity and PUE calculations pass.
- [ ] Workflow approval, runbook, escalation, compensation and rollback pass.
- [ ] Dashboard views and RBAC pass.

### Gemma/RAG/LLMOps

- [ ] Model artifact is pinned, licensed, scanned, checksummed and signed.
- [ ] Comparative benchmark against approved fallback passes or decision is documented.
- [ ] Corpus manifests, classification, ownership, freshness, supersession and rollback pass.
- [ ] Hybrid retrieval, reranker, citations, grounding and RBAC filters pass.
- [ ] CMDB, metrics, SIEM, incident, SLA and runbook tools pass read-only contract tests.
- [ ] Prompt injection, RAG poisoning, exfiltration, cross-role and unauthorized tool tests pass.
- [ ] Output schema, evidence, confidence and escalation behavior pass.
- [ ] Inference replica failure, fallback and degraded mode pass.
- [ ] Model/corpus/prompt/policy/tool monitoring and audit are active.
- [ ] LLM remains advisory and cannot directly execute privileged/OT actions.

### Operations and governance

- [ ] SLOs, dashboards, alerts, on-call and escalation tested.
- [ ] Installation, configuration, operation, security, backup, restore, DR and troubleshooting docs approved.
- [ ] Model card, corpus card, prompt/tool/policy registry and evaluation reports approved.
- [ ] Training and recovery exercises completed.
- [ ] Change record, UAT, security, architecture, data owner and operations sign-offs complete.
- [ ] Rollback point and hypercare plan approved.

---

## 17. Required Deliverables

1. This Deployment & Implementation Plan v2.
2. Approved architecture and environment diagrams.
3. Hardware/capacity calculation workbook.
4. IaC, Helm/Kustomize and GitOps configurations.
5. Network/firewall/PKI matrix.
6. Source integration catalog and data contracts.
7. Asset and CMDB data model/schema/API documentation.
8. SIEM rules, SOAR playbooks and workflow catalog.
9. Deterministic analytics specifications and model registry.
10. Gemma model card, benchmark, serving profile and fallback plan.
11. Corpus card, signed manifests, embedding/reranker versions and Qdrant backup.
12. AI Gateway, tool registry, prompt/policy registry and output schemas.
13. Security threat model, SBOM, scan and test evidence.
14. Performance, HA, DR, UAT and AI evaluation reports.
15. Runbooks, training material and operational handover package.

---

## 18. References

### Internal repository

- `plans/implementation-plan.md`
- `guides/deployment-implementation-guide.md`
- `reference-designs/staging-production-environment.md`
- `reference-designs/block1-infrastructure-provisioning.md`
- `reference-designs/block2-data-ingestion-integration.md`
- `reference-designs/block3-asset-repository.md`
- `reference-designs/block4-cmdb.md`
- `reference-designs/block5-web-dashboard.md`
- `reference-designs/block6-siem-soc-v3.md`
- `reference-designs/siem-soar.md`
- `reference-designs/block7-analytics-ai-engine.md`
- `reference-designs/block8-workflow-automation.md`
- `reference-designs/block9-external-integrations.md`
- `comparisons/mt023-private-llm-platform-alignment.md`
- `product-description/dcim-core-platform-product-description.md`

### External model/runtime references

- Unsloth Gemma 4 12B QAT GGUF: https://huggingface.co/unsloth/gemma-4-12B-it-qat-GGUF
- Google Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4
- llama.cpp: https://github.com/ggml-org/llama.cpp

---

> **Version 2 position:** Gemma 4 12B is introduced as the primary local cognitive/RAG candidate, while Python/statistical/ML services remain the deterministic authority. This preserves numerical reliability, enables full DCIM knowledge grounding and tool integration, and prevents an LLM from becoming an unsafe single point of decision or execution.
