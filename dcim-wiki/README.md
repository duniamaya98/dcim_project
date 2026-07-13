# DCIM Core Platform Wiki

Knowledge base untuk proyek **DCIM (Data Center Infrastructure Management) Core Platform** — mencakup arsitektur, desain, referensi teknis, dan runbook operasional.

> **Terakhir disinkronkan:** 13 Juli 2026
> **Status:** Wiki terintegrasi dengan implementasi Analytics & AI, deployment container/Kubernetes, dan pengujian empiris 23 capability model.

---

## Apa Isi Repo Ini

Repo ini berisi **knowledge base wiki** yang menjadi single source of truth untuk seluruh aspek desain dan implementasi DCIM platform:

| Komponen | Jumlah | Deskripsi |
|----------|--------|-----------|
| **Wiki Pages** | 163 | 19 entity, 91 concept, 37 comparison, 16 query |
| **Reference Designs** | 16 | Spec arsitektur, integrasi, dan environment |
| **Architecture Diagrams** | 17 | Diagram HTML/SVG interaktif |
| **Technical Requirements** | 34 | Requirement, use-case, SLA, dan komparasi FIT041 |
| **Implementation Plans** | 2 | Rencana implementasi & task breakdown |

---

## Struktur Repository

```
dcim-wiki/
├── index.md                          # Content catalog — mulai dari sini
├── log.md                            # Action log
├── SCHEMA.md                         # Wiki conventions & taxonomy
│
├── entities/                         # 19 entity pages
│   ├── cmdb.md
│   ├── kafka.md
│   ├── postgresql.md
│   └── ... (19 total)
│
├── concepts/                         # 91 concept pages
│   ├── data-quality-framework.md
│   ├── ha-dr-strategy.md
│   ├── anomaly-detection-strategy.md
│   └── ... (91 total)
│
├── comparisons/                      # 37 comparison pages
│   ├── kafka-vs-rabbitmq.md
│   ├── elasticsearch-vs-opensearch.md
│   └── ... (37 total)
│
├── queries/                          # 16 query/FAQ pages
│   └── ...
│
├── technical-requirements/           # 34 requirements, use-case, SLA, comparison pages
│
├── raw/                              # Source articles & references
│   └── articles/
│
├── _archive/                         # Deprecated pages
│
├── reference-designs/                # Reference design specs (markdown)
│   ├── block1-infrastructure-provisioning.md
│   ├── block2-data-ingestion-integration.md
│   ├── block3-asset-repository.md
│   ├── block4-cmdb.md
│   ├── block5-web-dashboard.md
│   ├── block6-siem-soc.md
│   ├── block7-analytics-ai-engine.md
│   ├── block8-workflow-automation.md
│   ├── block9-external-integrations.md
│   └── staging-production-environment.md
│
│   └── diagrams/                     # Architecture diagrams (HTML/SVG)
│       ├── block1-infrastructure-architecture.html
│       ├── block2-data-ingestion-architecture.html
│       ├── block3-asset-repository-architecture.html
│       ├── block4-cmdb-architecture.html
│       ├── block5-web-dashboard-architecture.html
│       ├── block6-siem-soc-architecture.html
│       ├── block6-siem-soc-improved-v2.html
│       ├── block6-siem-soc-kafka-vs-nokafka-comparison.html
│       ├── block6-siem-soc-no-kafka-architecture.html
│       ├── block7-analytics-ai-architecture.html
│       ├── block8-workflow-automation-architecture.html
│       ├── block9-external-integrations-architecture.html
│       └── staging-production-architecture.html
│
└── plans/                            # Implementation plans
    ├── implementation-plan.md
    └── phase12-task-breakdown.md
```

---

## Reference Design Blocks

| Block | Nama | Fokus |
|-------|------|-------|
| B1 | Infrastructure Provisioning | PostgreSQL, Redis, Kafka, NiFi, ES, Prometheus, Grafana, Vault, Docker/K8s |
| B2 | Data Ingestion & Integration | Kafka topics, NiFi flows, validation, enrichment, DLQ, lineage |
| B3 | Asset Repository | Asset data model, CRUD API, bulk import, reconciliation, audit trail |
| B4 | CMDB | CI model, relationship, topology engine, impact analysis, reconciliation |
| B5 | Web Dashboard | Vue 3 frontend, API Gateway, RBAC/SSO, NOC/SOC/Facilities views |
| B6 | SIEM/SOC | Wazuh, Syslog, Kafka→ES, correlation, incident response, compliance |
| — | SIEM SOAR | TraceCat + Temporal, playbook automation, case management, AI-assisted triage |
| B7 | Analytics & AI | Anomaly detection, predictive maintenance, RCA, capacity forecasting |
| B8 | Workflow Automation | State machine, ITSM, approvals, runbook, auto-remediation, escalation |
| B9 | External Integrations | Adapter pattern, ServiceNow, Jira, SAP/Oracle ERP, DMS connectors |
| — | Staging & Production | Environment sizing, network topology, VLAN segmentation, deployment |

---

## Cara Menggunakan

### 1. Mulai dari Index

Buka [`index.md`](index.md) untuk melihat seluruh content catalog. Setiap halaman punya one-line summary.

### 2. Baca Wiki Pages

Wiki pages menggunakan format markdown dengan YAML frontmatter:

```yaml
---
title: Page Title
created: 2026-06-22
updated: 2026-06-24
type: entity | concept | comparison | query
tags: [cmdb, kafka, ha-dr]
confidence: high
---
```

Internal links menggunakan wikilink format: `[[page-name]]`

### 3. Buka Architecture Diagrams

Buka file `.html` di browser untuk melihat diagram arsitektur interaktif. Setiap diagram:
- Dark-themed SVG
- Color-coded components
- VLAN boundaries
- Connection flows
- Info cards

### 4. Baca Reference Design Specs

Setiap blok punya reference design spec yang mencakup:
- Objective & Scope
- Component Architecture
- Data Flow
- API/Interface Contract
- Storage Model
- Security Design
- HA/DR Design
- Monitoring & Observability
- Deployment Model
- Acceptance Criteria
- Risks & Open Questions

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Database | PostgreSQL 16 |
| Cache | Redis 7 |
| Message Broker | Apache Kafka 3.x |
| Data Flow | Apache NiFi 1.x |
| Search/Analytics | Elasticsearch 8.x |
| Monitoring | Prometheus + Grafana |
| Secret Management | HashiCorp Vault |
| Container | Docker Compose / Kubernetes |
| Frontend | Vue 3, Pinia, ECharts, Tailwind |
| Workflow | n8n / Temporal |
| SIEM | Wazuh + Elasticsearch |
| SOAR | Tracecat (self-hosted) |

---

## Kontribusi

Repo ini dikelola oleh **Hermes DCIM Orchestrator** (AI agent) dan tim proyek.

### Update Wiki

1. Buat halaman baru sesuai format di `SCHEMA.md`
2. Tambahkan ke `index.md` di section yang sesuai
3. Append action ke `log.md`
4. Commit dengan format: `type: description` (Conventional Commits)

### Commit Convention

```
feat:     penambahan content baru
fix:      koreksi/error
reorganize: restrukturisasi
docs:     dokumentasi
```

---

## License

Private — DCIM Core Platform Project. For internal use only.

---

## Contacts

- **Project Owner**: shuffahaqgzz
- **Orchestrator**: Hermes DCIM (AI Agent)
- **Repository**: https://github.com/duniamaya98/dcim_project/tree/main/dcim-wiki
