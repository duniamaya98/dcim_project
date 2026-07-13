# DCIM Core Platform — Task Breakdown (Phase 1 + Phase 2)

**Date:** 2026-06-22
**Status:** Draft for approval
**Source:** SOUL.md, project memory, architecture mental model

---

## Executive Summary

- **Phase 1:** 4 blocks, ~32 task items. Focus: infra, DI&I, CMDB, Asset Repo.
- **Phase 2:** 5 blocks, ~30 task items. Focus: Analytics/AI, Workflow, SIEM, Dashboard, External.
- **Total:** 8 blocks, 62+ task items
- **Critical path:** Infra → Kafka/NiFi → CMDB core → DI&I pipeline → Analytics → Dashboard
- **Biggest parallel win:** Infra provisioning (3 sub-blocks concurrent) and Component development (Phase 2 blocks mostly independent)

---

## PHASE 1: Infrastructure & Core Foundation

### Block 1: Infrastructure Provisioning [P1]
> **Goal:** Ready-to-use base infra for all components.
> **Depends on:** Nothing (starting point)
> **Blocks:** All subsequent blocks

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 1.1 | Provision VM/container: 4vCPU, 16GB RAM, 200GB SSD minimum | 0.5d | — | — |
| 1.2 | Install & configure PostgreSQL 16 (CMDB + Asset + central logging) | 0.5d | 1.1 | — |
| 1.3 | Install & configure Redis 7 (session cache, real-time pub/sub) | 0.5d | 1.1 | — |
| 1.4 | Install & configure Kafka 3.x cluster (3 brokers, 3 ZK/KRaft) | 1d | 1.1 | — |
| 1.5 | Install & configure Apache NiFi 1.x (dataflow orchestrator) | 1d | 1.1 | — |
| 1.6 | Install & configure Elasticsearch 8.x / OpenSearch 2.x (central logging) | 1d | 1.1 | — |
| 1.7 | Install & configure Prometheus + Grafana (metrics + dashboards) | 0.5d | 1.1 | — |
| 1.8 | Install & configure HashiCorp Vault (secrets management) | 0.5d | 1.1 | — |
| 1.9 | Set up Docker Compose / K8s manifests for all services | 1d | 1.2-1.8 | — |
| 1.10 | Network segmentation: VLAN/firewall rules for management vs data plane | 0.5d | 1.1 | — |
| 1.11 | Base monitoring: host metrics, service health checks, alerting rules | 0.5d | 1.7, 1.9 | — |

**Validation gate:** All services running, health endpoints responding, Grafana showing host metrics.

---

### Block 2: Data Ingestion & Integration (DI&I) [P1]
> **Goal:** Single gateway ingesting from source systems, normalizing, routing to Kafka topics.
> **Depends on:** Block 1 (Kafka, NiFi, PostgreSQL)
> **Blocks:** Block 4 (CMDB consumption), Block 7 (Analytics)

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 2.1 | Design data model: normalized event schema (source, timestamp, metric, value, tags, CI reference) | 1d | — | — |
| 2.2 | Define Kafka topic structure (per-source-type topics + DLQ topic) | 0.5d | 2.1 | — |
| 2.3 | Build NiFi dataflow: BMS/EPMS ingestion (Modbus, BACnet, MQTT adapters) | 2d | 1.5, 2.2 | — |
| 2.4 | Build NiFi dataflow: NMS ingestion (SNMP trap + SNMP poll) | 1.5d | 1.5, 2.2 | Parallel with 2.3 |
| 2.5 | Build NiFi dataflow: Server/storage monitoring (REST API, WMI, SSH) | 1.5d | 1.5, 2.2 | Parallel with 2.3-2.4 |
| 2.6 | Build NiFi dataflow: Virtualization/cloud (vCenter API, AWS/GCP API) | 1.5d | 1.5, 2.2 | Parallel with 2.3-2.5 |
| 2.7 | Build NiFi dataflow: Access control/surveillance (ONVIF, API) | 1d | 1.5, 2.2 | Parallel with 2.3-2.6 |
| 2.8 | Implement validation & cleansing layer (schema check, range, format, dedup) | 1.5d | 2.1 | Parallel with 2.3-2.7 |
| 2.9 | Implement enrichment layer (CI lookup from CMDB, geo, owner) | 1d | 2.8 | — |
| 2.10 | Implement normalization (unit conversion, timestamp alignment, enum mapping) | 1d | 2.8 | Parallel with 2.9 |
| 2.11 | Implement DLQ handling: retry, dead-letter queue, reprocessing API | 1d | 2.8 | — |
| 2.12 | Implement data lineage tracking (source → topic → consumer) | 0.5d | 2.2 | — |
| 2.13 | Build ITSM/ERP/DMS integration connectors (REST API adapters) | 1.5d | 1.5 | Parallel with 2.3-2.7 |
| 2.14 | End-to-end integration test: simulated BMS + NMS → Kafka → normalized output | 1d | 2.3-2.13 | — |

**Validation gate:** Simulated events from 3+ source types flow through NiFi → Kafka → normalized output with lineage metadata. DLQ catches malformed events.

---

### Block 3: Asset Repository [P1]
> **Goal:** SSOT for asset master data, financial/contract attributes, lifecycle.
> **Depends on:** Block 1 (PostgreSQL, Redis)
> **Blocks:** Block 4 (CMDB enrichment), Block 7 (Analytics)

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 3.1 | Design Asset data model (Asset_ID, serial, asset_tag, PO, warranty, contract, owner, location, lifecycle_status, CI_ID) | 1d | — | — |
| 3.2 | PostgreSQL schema: asset master, warranty, contract, financial, location tables | 1d | 3.1 | — |
| 3.3 | Implement CRUD API (REST): create, read, update, delete, list, search | 1.5d | 3.2 | — |
| 3.4 | Implement bulk import API (CSV/Excel → validation → upsert) | 1d | 3.3 | — |
| 3.5 | Implement reconciliation engine: asset ↔ CI cross-reference, serial/tag consistency | 1.5d | 3.2 | Parallel with 3.3 |
| 3.6 | Implement audit trail: every change logged with timestamp, user, before/after | 0.5d | 3.3 | — |
| 3.7 | Build enrichment API for CMDB & analytics (read-optimized, cache in Redis) | 1d | 3.3, 1.3 | — |
| 3.8 | Unit + integration tests: CRUD, bulk import, reconciliation, audit | 1d | 3.3-3.7 | — |

**Validation gate:** CRUD operations work, bulk import handles 1000+ records, reconciliation catches mismatched CI_ID, audit trail records all changes.

---

### Block 4: CMDB [P1]
> **Goal:** SSOT for CI, relationships, topology, dependency mapping.
> **Depends on:** Block 1 (PostgreSQL, Redis), Block 3 (Asset enrichment API)
> **Blocks:** Block 5 (Dashboard), Block 7 (Analytics), Block 8 (Workflow)

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 4.1 | Design CMDB data model: CI types, mandatory attributes, lifecycle states, relationship types | 1.5d | — | — |
| 4.2 | PostgreSQL schema: CI table, relationship table, attribute table, lifecycle audit | 1d | 4.1 | — |
| 4.3 | Implement CI CRUD API with field validation & uniqueness constraints | 1.5d | 4.2 | — |
| 4.4 | Implement relationship model: contains, connects_to, depends_on, runs_on, part_of | 1d | 4.3 | — |
| 4.5 | Implement topology engine: graph queries, dependency traversal, blast radius | 2d | 4.4 | — |
| 4.6 | Implement impact analysis: cascade dependency → affected services list | 1.5d | 4.5 | — |
| 4.7 | Implement asset ↔ CMDB reconciliation (cross-reference with Block 3) | 1d | 4.3 | Parallel with 4.4-4.6 |
| 4.8 | Implement discovery reconciliation: auto-discovered CI merge with CMDB | 1.5d | 4.3 | Parallel with 4.4-4.6 |
| 4.9 | Implement service mapping: business service → CI hierarchy | 1.5d | 4.5 | — |
| 4.10 | Implement change/incident/capacity integration hooks (ITSM connector) | 1d | 4.3 | Parallel with 4.5-4.9 |
| 4.11 | Build CMDB health dashboard (completeness, freshness, accuracy KPIs) | 1d | 4.3, 1.7 | — |
| 4.12 | Unit + integration tests: CRUD, relationships, topology, impact, reconciliation | 1.5d | 4.3-4.11 | — |

**Validation gate:** 500+ CIs with relationships, topology traversal finds dependency paths, impact analysis returns correct blast radius, CMDB health KPIs computed.

---

## PHASE 2: Intelligence, Automation & Presentation

### Block 5: Web Dashboard [P2]
> **Goal:** NOC/SOC/Facilities views, SLA/KPI, task board, log viewer.
> **Depends on:** Block 4 (CMDB API), Block 3 (Asset API)
> **Blocks:** Block 7 (Analytics feeds into dashboard), Block 8 (Workflow feeds into dashboard)

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 5.1 | Tech stack selection & scaffolding (React/Vue + backend API gateway) | 1d | — | — |
| 5.2 | Authentication & RBAC (SSO/LDAP integration, role-based views) | 1.5d | 5.1 | — |
| 5.3 | NOC view: real-time rack diagram, power/cooling, alert feed | 2d | 5.1 | Parallel with 5.2 |
| 5.4 | SOC view: security events, SIEM alerts, compliance status | 1.5d | 5.1 | Parallel with 5.2, 5.3 |
| 5.5 | Facilities view: floor plan, environmental monitoring, energy dashboard | 1.5d | 5.1 | Parallel with 5.2-5.4 |
| 5.6 | CMDB explorer: CI search, relationship graph, dependency visualization | 1.5d | 5.1 | Parallel with 5.2-5.5 |
| 5.7 | Asset management view: asset list, lifecycle status, warranty tracking | 1d | 5.1 | Parallel with 5.2-5.6 |
| 5.8 | SLA/KPI dashboard: service health, uptime, latency, incident metrics | 1.5d | 5.1 | Parallel with 5.2-5.7 |
| 5.9 | Log viewer: centralized logs, search, filter, export | 1d | 5.1, 1.6 | — |
| 5.10 | Task board: workflow tasks, assignments, status, escalation | 1d | 5.1 | Parallel with 5.2-5.9 |
| 5.11 | Responsive design + mobile view (basic) | 1d | 5.2-5.10 | — |
| 5.12 | E2E tests: login, navigation, key views render with mock data | 1d | 5.11 | — |

**Validation gate:** Dashboard loads, all views render, RBAC works, real-time data updates via WebSocket/SSE.

---

### Block 6: SIEM / SOC Integration [P1]
> **Goal:** Security log collection, correlation, incident response, compliance.
> **Depends on:** Block 1 (Kafka, Elasticsearch), Block 2 (DI&I pipeline)
> **Blocks:** Block 5 (SOC view), Block 8 (Security workflows)

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 6.1 | Design SIEM data model: events, alerts, incidents, compliance checks | 1d | — | — |
| 6.2 | Implement security event ingestion (Wazuh/Syslog → Kafka → Elasticsearch) | 1.5d | 2.2, 1.6 | — |
| 6.3 | Implement correlation engine (rule-based: event sequences → alert) | 2d | 6.2 | — |
| 6.4 | Implement incident response workflow (auto-create, assign, escalate) | 1.5d | 6.3 | — |
| 6.5 | Implement compliance checks (CIS benchmarks, access policy, audit) | 1.5d | 6.2 | Parallel with 6.3 |
| 6.6 | Implement SOC API: events query, alert management, incident CRUD | 1d | 6.2-6.4 | — |
| 6.7 | Build Wazuh integration (if using Wazuh as primary SIEM) | 1d | 6.2 | Parallel with 6.3-6.5 |
| 6.8 | Integration tests: event ingestion, correlation rules, incident flow | 1d | 6.2-6.7 | — |

**Validation gate:** Security events ingested, correlation rules trigger alerts, incidents auto-created, compliance checks pass/fail correctly.

---

### Block 7: Analytics & AI Engine [P2]
> **Goal:** Anomaly detection, predictive maintenance, RCA, capacity/energy optimization.
> **Depends on:** Block 2 (normalized data in Kafka), Block 3 (Asset data), Block 4 (CMDB topology)
> **Blocks:** Block 5 (Dashboard feeds results), Block 8 (Workflow automation)

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 7.1 | Design analytics data model: time-series storage schema, metric metadata | 1d | — | — |
| 7.2 | Implement time-series data pipeline (Kafka → TimescaleDB/InfluxDB) | 1.5d | 2.2, 1.2 | — |
| 7.3 | Implement anomaly detection (statistical + ML: Isolation Forest, Z-score) | 2d | 7.2 | — |
| 7.4 | Implement predictive maintenance (failure prediction from sensor trends) | 2d | 7.2 | Parallel with 7.3 |
| 7.5 | Implement RCA engine (root cause analysis using CMDB topology + event correlation) | 2d | 7.2, 4.5 | — |
| 7.6 | Implement capacity forecasting (trend analysis, projection, threshold alert) | 1.5d | 7.2 | Parallel with 7.3-7.5 |
| 7.7 | Implement energy optimization recommendations (PUE, load balancing) | 1.5d | 7.2 | Parallel with 7.3-7.6 |
| 7.8 | Build analytics API: query, dashboard data, export | 1d | 7.2-7.7 | — |
| 7.9 | Implement model training pipeline (retrain on new data, A/B testing) | 1.5d | 7.3-7.7 | — |
| 7.10 | Implement LLM/RAG explanation layer (natural language insights) | 2d | 7.8 | — |
| 7.11 | Integration tests: anomaly detection accuracy, prediction validation, RCA correctness | 1.5d | 7.2-7.10 | — |

**Validation gate:** Anomaly detection finds known anomalies, predictions validated on historical data, RCA returns correct root cause in test scenarios, capacity forecast matches historical trends within 10%.

---

### Block 8: Workflow Automation [P2]
> **Goal:** Ticketing, approval, runbook, remediation, escalation.
> **Depends on:** Block 4 (CMDB), Block 3 (Asset), Block 7 (Analytics triggers)
> **Blocks:** Block 5 (Task board), Block 6 (Security workflows)

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 8.1 | Design workflow engine: trigger → condition → action → approval → execution | 1.5d | — | — |
| 8.2 | Implement workflow state machine (pending, running, waiting, completed, failed) | 1d | 8.1 | — |
| 8.3 | Implement ticketing integration (ITSM: create/update/close tickets) | 1d | 8.2 | — |
| 8.4 | Implement approval workflow (multi-level approval with SLA) | 1d | 8.2 | Parallel with 8.3 |
| 8.5 | Implement runbook engine (parameterized scripts, safety checks) | 2d | 8.2 | Parallel with 8.3-8.4 |
| 8.6 | Implement auto-remediation (triggered by analytics/anomaly alerts) | 1.5d | 8.5, 7.3 | — |
| 8.7 | Implement escalation rules (time-based, severity-based) | 1d | 8.2 | Parallel with 8.3-8.6 |
| 8.8 | Build workflow API: CRUD, execute, monitor, history | 1d | 8.2-8.7 | — |
| 8.9 | Build n8n/Temporal integration (if using external workflow engine) | 1d | 8.8 | — |
| 8.10 | Integration tests: end-to-end workflow from trigger to remediation | 1d | 8.2-8.9 | — |

**Validation gate:** Workflow triggers on alert, approval gate works, runbook executes safely, escalation fires on timeout, ticket created/updated in ITSM.

---

### Block 9: External Integrations [P2]
> **Goal:** ITSM, ERP, DMS, NMS, external platform connectors.
> **Depends on:** Block 2 (DI&I), Block 4 (CMDB), Block 3 (Asset)
> **Blocks:** All downstream consumers

| ID | Task | Effort | Depends | Parallel? |
|----|------|--------|---------|-----------|
| 9.1 | Design integration framework: adapter pattern, auth, retry, circuit breaker | 1d | — | — |
| 9.2 | Implement ITSM connector (ServiceNow/Jira: incident, change, asset sync) | 1.5d | 9.1 | — |
| 9.3 | Implement ERP connector (SAP/Oracle: procurement, asset lifecycle) | 1.5d | 9.1 | Parallel with 9.2 |
| 9.4 | Implement DMS connector (document management: policies, procedures) | 1d | 9.1 | Parallel with 9.2-9.3 |
| 9.5 | Implement NMS connector (network management: topology, performance) | 1d | 9.1 | Parallel with 9.2-9.4 |
| 9.6 | Implement cloud provider connectors (AWS, GCP, Azure: resource inventory) | 1.5d | 9.1 | Parallel with 9.2-9.5 |
| 9.7 | Build integration health monitoring (uptime, latency, error rates) | 0.5d | 9.1, 1.7 | — |
| 9.8 | Integration tests: each connector with mock/staging environment | 1.5d | 9.2-9.7 | — |

**Validation gate:** Each connector syncs data bidirectionally, circuit breaker trips on failure, retry works, health monitoring shows status.

---

## DEPENDENCY GRAPH (Simplified)

```
Block 1: Infrastructure ─────────────────────────────────────────────┐
  ├── Block 2: DI&I ────────────┐                                   │
  │   ├── Block 4: CMDB ────────┤                                   │
  │   │   ├── Block 5: Dashboard (Phase 2)                           │
  │   │   ├── Block 7: Analytics ───────┐                           │
  │   │   └── Block 8: Workflow ────────┤                           │
  │   └── Block 6: SIEM/SOC ───────────┤                           │
  ├── Block 3: Asset Repo ─────────────┤                           │
  └── Block 9: External Integrations ──┘                           │
                                                                    │
Phase 1: Blocks 1-4 ──────────────────────── Phase 2: Blocks 5-9  │
(all must complete)                      (mostly parallel work)     │
                                                                    │
Estimated total: 32 tasks (Phase 1) + 30 tasks (Phase 2) = 62+    │
```

---

## CRITICAL PATH (Longest Dependency Chain)

```
1.1 → 1.4 → 2.2 → 2.3 → 2.8 → 2.9 → 4.1 → 4.2 → 4.3 → 4.5 → 7.2 → 7.5 → 8.5 → 8.6
  VM    Kafka  Schema NiFi  Clean  Enrich Model  DB   API  Topo   TS    RCA   Run   Remed
  0.5   1      1      2     1.5    1     1.5    1    1.5  2     1.5   2     2     1.5
  ───────────── ~17d ───────────────────────────── ~10.5d ────────────────────────────
  Total critical path: ~27.5 working days (single-threaded)
```

**With parallelism:** ~15-18 working days (2 teams of 2-3)

---

## PARALLEL OPPORTUNITIES

### Phase 1 (can start simultaneously)
- **Infra sub-blocks (1.2-1.8):** All parallel after 1.1
- **DI&I adapters (2.3-2.7, 2.13):** All parallel after Kafka + NiFi ready
- **Asset + CMDB model design (3.1, 4.1):** Parallel, no dependency
- **Validation logic (2.8-2.10):** Parallel with adapters

### Phase 2 (can start in parallel after Phase 1 blocks)
- **Dashboard (5.1-5.10):** Mostly parallel after scaffolding
- **SIEM (6.1-6.7):** Independent of Analytics/Workflow
- **Analytics (7.1-7.10):** Independent of Workflow
- **Workflow (8.1-8.9):** Independent of Analytics
- **External integrations (9.1-9.7):** Independent, can start early

---

## ESTIMATED TIMELINE

| Phase | Tasks | Calendar Days (2 teams) | Calendar Days (1 team) |
|-------|-------|------------------------|----------------------|
| Phase 1 | 32 | 8-10 | 16-20 |
| Phase 2 | 30 | 7-9 | 14-18 |
| **Total** | **62** | **15-19** | **30-38** |

---

## RECOMMENDED TEAM STRUCTURE (for parallel execution)

| Role | Blocks | Focus |
|------|--------|-------|
| Infra Engineer | 1.1-1.11 | Provisioning, networking, monitoring |
| Data Engineer | 2.1-2.14 | DI&I, Kafka, NiFi, data pipelines |
| Backend Developer 1 | 3.1-3.8 | Asset Repository |
| Backend Developer 2 | 4.1-4.12 | CMDB |
| Backend Developer 3 | 6.1-6.8 | SIEM/SOC |
| AI/ML Engineer | 7.1-7.11 | Analytics & AI |
| Full-stack Developer | 5.1-5.12 | Dashboard |
| Integration Engineer | 8.1-8.10, 9.1-9.8 | Workflow + External |
| QA/DevOps | All blocks | Testing, CI/CD, deployment |

---

## OPEN QUESTIONS

1. **CMDB vs NetBox:** Using custom CMDB or extending NetBox? Affects Block 4 effort by ±30%.
2. **Analytics stack:** TimescaleDB vs InfluxDB vs Elasticsearch for time-series? Affects Block 7.2 effort.
3. **Workflow engine:** Custom state machine vs n8n/Temporal? Affects Block 8.9 effort.
4. **Dashboard framework:** React + TypeScript vs Vue? Team skillset dependent.
5. **Cloud vs on-prem:** Affects Block 1 provisioning significantly.
6. **Scale targets:** Expected CIs count, events/day, concurrent users? Affects all performance requirements.

---

## NEXT STEP

**For MASTER to approve:**
1. Confirm team structure and available resources
2. Resolve open questions (especially #1, #3, #4)
3. Confirm priority: Phase 1 first, or can any Phase 2 blocks start in parallel?
4. Approve task breakdown, then we generate Kanban cards and kick off execution
