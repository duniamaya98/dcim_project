---
title: "SOAR Repo vs DCIM-Wiki — Repo Alignment"
created: 2026-07-13
updated: 2026-07-13
type: comparison
tags: [soar, repo-alignment, n8n, wazuh, dfir-iris, virustotal, alienvault, llm, dcim-wiki, gap-analysis, madicemerlang]
sources:
  - https://github.com/madicemerlang/SOAR.git
  - reference-designs/siem-soar.md
  - reference-designs/siem-soar-actual-architecture.md
  - comparisons/siem-soar-gap-analysis.md
  - comparisons/impl-repo-siem-alignment.md
confidence: high
purpose: >-
  Komparasi repo madicemerlang/SOAR.git (n8n SOAR workflow) dengan
  knowledge base DCIM-Wiki untuk mengidentifikasi alignment, gap,
  dan connection points antara implementasi aktual (n8n-based SOAR)
  dan reference design SIEM/SOAR.
---

# SOAR Repo vs DCIM-Wiki — Repo Alignment

> **Purpose:** Komparasi side-by-side antara **madicemerlang/SOAR.git** (n8n SOAR workflow) dengan knowledge base DCIM-Wiki (Reference Design, Actual Architecture, Gap Analysis).
> **Cara pakai:** Review setiap section untuk memahami alignment, identifikasi gap, dan tentukan action items.
> **Related:** [[siem-soar]], [[siem-soar-actual-architecture]], [[impl-repo-siem-alignment]]
> **Constraint:** Dokumen existing TIDAK dimodifikasi.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Repo Inventory](#2-repo-inventory)
3. [DCIM-Wiki Reference Summary](#3-dcim-wiki-reference-summary)
4. [Component-by-Component Alignment](#4-component-by-component-alignment)
5. [UC-Based Mapping](#5-uc-based-mapping)
6. [NFR/Security/Monitoring Mapping](#6-nfrsecuritymonitoring-mapping)
7. [Acceptance Criteria Mapping](#7-acceptance-criteria-mapping)
8. [Gap Analysis Summary](#8-gap-analysis-summary)
9. [Tradeoffs & Pitfalls](#9-tradeoffs--pitfalls)
10. [Unique Items per Source](#10-unique-items-per-source)
11. [Connection Mapping](#11-connection-mapping)
12. [Three-Way Comparison](#12-three-way-comparison)
13. [Recommendations](#13-recommendations)
14. [Quality Gate Checklist](#14-quality-gate-checklist)

---

## 1. Executive Summary

| Aspek | Hasil |
|-------|-------|
| **Status** | ⚠️ **PARTIAL** — Komplementer dengan actual architecture |
| **Repo Role** | n8n SOAR workflow (alert → enrichment → AI analysis → case) |
| **DCIM-Wiki Role** | Full SIEM/SOAR reference design (TraceCat + Temporal + Kafka + MCP) |
| **Alignment Score** | **~25%** vs Reference Design, **~60%** vs Actual Architecture |
| **Repo Coverage** | 1 workflow, 8 nodes, 3 integrations (VT, AlienVault, DFIR IRIS) |
| **Wiki Coverage** | 13+ components, 20 acceptance criteria, 7 playbook categories |
| **Konflik** | 0 konflik kritis — repo complementer, bukan replacement |
| **Kesimpulan** | Repo = valid SOAR MVP. Gap = production hardening (bukan fundamental). |

### Quick Overview

```
Repo (madicemerlang/SOAR.git)                 DCIM-Wiki (Reference Design)
┌──────────────────────────────────┐         ┌──────────────────────────────────┐
│ ✅ Wazuh Webhook Trigger         │← align →│ Alert Ingestion (Kafka/Webhook)  │
│ ✅ IOC Routing (Switch)          │← align →│ Playbook Router                  │
│ ✅ VirusTotal Enrichment         │← align →│ TIP Integration (VT)             │
│ ✅ AlienVault OTX Enrichment     │← align →│ TIP Integration (AbuseIPDB/OTX)  │
│ ✅ Local LLM Analysis (Gemma)    │← diff  →│ MCP Protocol (Claude/Codex)      │
│ ✅ DFIR IRIS Case Creation       │← align →│ Case Management (IRIS)           │
│ ⚠️ n8n Workflow Engine           │← diff  →│ TraceCat + Temporal              │
│ ❌ No Kafka Message Broker       │← MISS  →│ Kafka 3.x (5 topics)            │
│ ❌ No RBAC/OIDC                  │← MISS  →│ OIDC + Keycloak                 │
│ ❌ No Vault (Secrets)            │← MISS  →│ HashiCorp Vault                 │
│ ❌ No Audit Trail                │← MISS  →│ Full action logging             │
│ ❌ No OT-Safe Enforcement        │← MISS  →│ Forbidden actions enforced       │
│ ❌ No Monitoring                 │← MISS  →│ Prometheus + Grafana            │
│ ❌ No HA/DR                      │← MISS  →│ Docker Swarm 3-node             │
│ ❌ No TLS Enforcement            │← MISS  →│ TLS 1.2+ everywhere            │
└──────────────────────────────────┘         └──────────────────────────────────┘
```

---

## 2. Repo Inventory

### 2.1 File Structure

```
madicemerlang/SOAR.git/
├── README.md                    # Documentation (comprehensive, 9.2KB)
├── .gitignore
└── N8N Workflow/
    └── SOAR.json                # n8n workflow export (full config)
```

**Total:** 1 workflow file + 1 README + 1 .gitignore = **3 files**

### 2.2 Workflow Nodes

| # | Node Name | Type | Function |
|---|-----------|------|----------|
| 1 | **Security Alert** | `n8n-nodes-base.webhook` | Webhook trigger — receives Wazuh alerts (POST `/341f0a50-...`) |
| 2 | **Switch** | `n8n-nodes-base.switch` | IOC router — branches by hash/IP/default |
| 3 | **Hash Scan - VirusTotal** | `n8n-nodes-base.httpRequest` | GET VirusTotal API — file hash reputation |
| 4 | **IP Scan - AlienVaultOTX** | `n8n-nodes-base.httpRequest` | GET AlienVault OTX API — IP reputation |
| 5 | **Merge Fields** | `n8n-nodes-base.set` | Combine enrichment results into single payload |
| 6 | **Analyze Alert** | `n8n-nodes-base.httpRequest` | POST to local LLM (Gemma-12B) — SOC analysis |
| 7 | **ITSM - DFIR IRIS** | `n8n-nodes-base.httpRequest` | POST to DFIR IRIS — create case |
| 8 | **Manual Input** | `n8n-nodes-base.set` | Testing node — simulate FIM alert |

### 2.3 Flow Diagram

```
                                    ┌─────────────────┐
                                    │ Manual Input    │
                                    │ (Testing)       │
                                    └────────┬────────┘
                                             │
┌──────────────────┐   POST    ┌─────────────┴─────────────┐
│  Wazuh Manager   │─────────→│    n8n Webhook Trigger     │
│  (level 7+)      │          │    /341f0a50-...           │
└──────────────────┘          └─────────────┬──────────────┘
                                            │
                                    ┌───────┴───────┐
                                    │    Switch     │
                                    │  (IOC Check)  │
                                    └───┬───┬───┬───┘
                                        │   │   │
                          ┌─────────────┘   │   └─────────────┐
                          ▼                 ▼                 ▼
                ┌─────────────────┐ ┌───────────────┐ ┌──────────────┐
                │ VirusTotal API  │ │ AlienVault    │ │ Direct Merge │
                │ (Hash scan)     │ │ OTX (IP scan) │ │ (Default)    │
                └────────┬────────┘ └───────┬───────┘ └──────┬───────┘
                         │                  │                 │
                         └──────────────────┼─────────────────┘
                                            ▼
                                  ┌─────────────────┐
                                  │  Merge Fields   │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │  Analyze Alert  │
                                  │  (Local LLM)    │
                                  │  Gemma-12B      │
                                  └────────┬────────┘
                                           │
                                           ▼
                                  ┌─────────────────┐
                                  │  DFIR IRIS      │
                                  │  (Case Create)  │
                                  └─────────────────┘
```

### 2.4 Integrations

| Integration | Endpoint | Auth | Status |
|------------|----------|------|--------|
| **Wazuh Webhook** | `POST /341f0a50-a4be-41fb-b93f-217712c95238` | None (UUID path) | ✅ Active |
| **VirusTotal** | `GET https://www.virustotal.com/api/v3/files/{hash}` | API Key (n8n credential) | ✅ Active |
| **AlienVault OTX** | `GET https://otx.alienvault.com/api/v1/indicators/IPv4/{ip}/general` | API Key (n8n credential) | ✅ Active |
| **Local LLM** | `POST http://192.168.100.35:8080/v1/chat/completions` | None | ⚠️ Hardcoded IP, no auth |
| **DFIR IRIS** | `POST https://192.168.101.173/manage/cases/add` | API Token (n8n credential) | ⚠️ Hardcoded IP, self-signed cert allowed |

---

## 3. DCIM-Wiki Reference Summary

### 3.1 Reference Design Target (siem-soar.md)

| Layer | Components | Status in Repo |
|-------|-----------|----------------|
| **Alert Ingestion** | Wazuh → Kafka (dcim.siem.alerts) → TraceCat Webhook | ⚠️ Partial (webhook direct, no Kafka) |
| **Workflow Engine** | TraceCat + Temporal (state machine, retry, compensation) | ❌ n8n instead (simpler, no state) |
| **Enrichment** | TIP (MISP, AbuseIPDB, VT), CMDB, GeoIP, Vuln, User Context | ⚠️ Partial (VT + AlienVault only) |
| **AI Agent** | MCP Protocol (Claude Code, Codex, Cursor) | ❌ Local LLM direct API |
| **Case Management** | DFIR IRIS (full lifecycle) | ✅ Match |
| **OT-Safe** | Forbidden actions enforced, playbook validator | ❌ Missing |
| **RBAC** | OIDC + Keycloak (5 roles) | ❌ Missing |
| **Secrets** | HashiCorp Vault (6 secret types) | ❌ Hardcoded IPs |
| **Monitoring** | Prometheus + Grafana (8 metrics, 7 panels) | ❌ Missing |
| **Deployment** | Docker Swarm (3 nodes, 23 replicas) | ❌ Single n8n instance |
| **Network** | 3 VLANs (DMZ/Data/Mgmt) | ❌ No segmentation |

### 3.2 Actual Architecture (siem-soar-actual-architecture.md)

| Layer | Components | Status in Repo |
|-------|-----------|----------------|
| **SIEM** | LME (Wazuh + ES + Kibana + ElastAlert) | ⚠️ Partial (webhook, no ElastAlert) |
| **SOAR** | Tracecat (Enrichment + AI Agent + Playbook) | ❌ n8n instead |
| **ITSM** | DFIR-IRIS | ✅ Match |
| **Enrichment** | AbuseIPDB + VirusTotal | ⚠️ Different (AlienVault instead of AbuseIPDB) |
| **AI** | Tracecat AI Agent (Summary + Recommend) | ⚠️ Different (Gemma-12B direct) |

### 3.3 Existing Gap Analysis (siem-soar-gap-analysis.md)

Previous gap analysis compared Reference Design vs Actual Architecture. Key findings:
- **4/15 Match**, **4/15 Different**, **7/15 Missing**
- Critical gaps: CMDB, OT-Safe, RBAC, Audit Trail, HA/DR, Vault, Monitoring

---

## 4. Component-by-Component Alignment

### 4.1 Alert Ingestion

| Aspect | Repo | DCIM-Wiki Reference | Alignment | Gap Type |
|--------|------|---------------------|-----------|----------|
| **Trigger** | n8n Webhook (POST) | Kafka → TraceCat Webhook | ⚠️ Different | No Kafka buffering |
| **Source** | Wazuh Manager (level 7+) | Wazuh + Deception + Physical-Cyber | ⚠️ Partial | Only Wazuh |
| **Format** | Raw JSON (`$json.body`) | Normalized JSON (ECS/OCSF) | ⚠️ Partial | No normalization |
| **Auth** | UUID-based path (obscurity) | HMAC-SHA256 signature | ❌ Gap (P1) | No real auth |
| **Rate Limit** | None | 1000 req/min | ❌ Gap (P2) | No protection |
| **TLS** | Not enforced | Required (TLS 1.2+) | ❌ Gap (P1) | HTTP for LLM |

**Assessment:** Repo uses direct webhook (simpler). DCIM-Wiki requires Kafka as message broker for buffering, replay, and fan-out. The webhook approach works for <5000 EPS but lacks durability and multi-consumer support.

### 4.2 IOC Routing & Enrichment

| Aspect | Repo | DCIM-Wiki Reference | Alignment | Gap Type |
|--------|------|---------------------|-----------|----------|
| **Routing** | n8n Switch (hash/IP/default) | Temporal workflow branching | ⚠️ Different | No state machine |
| **Hash Intel** | VirusTotal API | MISP + VirusTotal | ✅ Match (VT) | No MISP |
| **IP Intel** | AlienVault OTX API | AbuseIPDB + MISP | ⚠️ Different | OTX vs AbuseIPDB |
| **CMDB Enrichment** | ❌ Not implemented | Asset criticality, owner, location | ❌ Gap (P1) | No asset context |
| **GeoIP** | ❌ Not implemented | Geolocation, ASN | ❌ Gap (P2) | No geo data |
| **Vuln Enrichment** | ❌ Not implemented | CVE, CVSS | ❌ Gap (P2) | No vuln context |
| **User Context** | ❌ Not implemented | Role, department, risk score | ❌ Gap (P2) | No user context |

**Assessment:** Repo has basic IOC enrichment (VT + AlienVault). DCIM-Wiki requires 6 enrichment sources. The 2-source approach covers ~30% of enrichment needs. CMDB integration is the most critical missing piece for DCIM context.

### 4.3 AI Analysis

| Aspect | Repo | DCIM-Wiki Reference | Alignment | Gap Type |
|--------|------|---------------------|-----------|----------|
| **Engine** | Local LLM (Gemma-12B) | MCP Protocol (Claude/Codex) | ❌ Different | No MCP |
| **Endpoint** | `http://192.168.100.35:8080/v1/chat/completions` | MCP Server (TraceCat) | ❌ Different | Direct API |
| **Model** | `gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL` | Claude Code, Codex, Cursor | ⚠️ Different | Local vs cloud |
| **Prompt** | Senior SOC Analyst (Indonesian) | Dynamic via MCP tools | ⚠️ Different | Static prompt |
| **Output** | TP/FP/Inconclusive + Recommendations | Multi-step analysis + playbook gen | ⚠️ Partial | Single-step |
| **Capabilities** | Alert analysis only | Analysis, playbook gen, hunting, reporting | ⚠️ Partial | Limited scope |
| **Temperature** | 0 (deterministic) | Configurable per task | ✅ Match | — |
| **Streaming** | Disabled (`stream: false`) | Configurable | ✅ Match | — |

**Assessment:** Repo uses local LLM for alert triage — valid for cost-sensitive, air-gapped environments. DCIM-Wiki uses MCP protocol for multi-agent flexibility. The local LLM approach is production-viable but lacks the extensibility of MCP (playbook generation, threat hunting, report generation).

### 4.4 Case Management

| Aspect | Repo | DCIM-Wiki Reference | Alignment | Gap Type |
|--------|------|---------------------|-----------|----------|
| **Platform** | DFIR IRIS | DFIR IRIS | ✅ Match | — |
| **Endpoint** | `POST /manage/cases/add` | `POST /api/v2/cases` | ⚠️ Different | API version |
| **Fields** | case_name, case_description, case_soc_id, case_severity_id | Full schema (MITRE, assets, timeline, evidence) | ⚠️ Partial | Minimal fields |
| **Severity** | Hardcoded `2` (Medium) | Dynamic based on risk score | ❌ Gap (P1) | No risk routing |
| **Assignee** | Hardcoded `Falah` | Dynamic (L1/L2/L3 queue) | ❌ Gap (P1) | No escalation |
| **Template** | None | Standard Triage / Incident Response | ❌ Gap (P2) | No templates |
| **TLS Verify** | `allowUnauthorizedCerts: true` | TLS 1.2+ required | ❌ Gap (P1) | Security risk |

**Assessment:** Both use DFIR IRIS — strong alignment. Repo creates basic cases (4 fields). DCIM-Wiki requires full case lifecycle with dynamic severity, assignee routing, and templates. The hardcoded severity/assignee is the most critical gap for production use.

### 4.5 Workflow Engine

| Aspect | Repo | DCIM-Wiki Reference | Alignment | Gap Type |
|--------|------|---------------------|-----------|----------|
| **Engine** | n8n (visual workflow) | TraceCat + Temporal | ❌ Different | Different platform |
| **State Persistence** | In-memory (n8n) | PostgreSQL (Temporal) | ❌ Gap (P2) | No state persistence |
| **Retry** | n8n built-in (basic) | Exponential backoff, configurable | ⚠️ Partial | Less robust |
| **Compensation** | None | Undo/rollback actions | ❌ Gap (P2) | No compensation |
| **Versioning** | JSON export/import | Git-based YAML playbooks | ⚠️ Different | Less structured |
| **Monitoring** | n8n UI | Temporal UI + Prometheus | ⚠️ Partial | Basic only |
| **Playbook-as-Code** | n8n JSON (not human-readable) | YAML (human-readable, version-controlled) | ❌ Gap (P2) | Less maintainable |

**Assessment:** n8n is a valid workflow engine for simple automations. TraceCat + Temporal provides enterprise-grade workflow orchestration with state persistence, compensation, and versioning. For DCIM production, Temporal's guarantees (exactly-once execution, state recovery) are important for incident response reliability.

---

## 5. UC-Based Mapping

Since this is a workflow repo (n8n JSON), mapping is UC-based rather than FR-by-FR.

### 5.1 Use Case Coverage

| UC | Use Case | Repo Status | DCIM-Wiki Target | Gap |
|----|----------|-------------|------------------|-----|
| UC1 | Alert ingestion from Wazuh | ✅ Implemented (webhook) | Kafka + Webhook | No Kafka |
| UC2 | Alert visualization (Kibana) | ❌ Not in scope | Kibana dashboards | Separate component |
| UC3 | Automated enrichment (VT, IP) | ✅ Implemented (VT + AlienVault) | 6 sources | Missing CMDB, GeoIP, Vuln, User |
| UC4 | AI-assisted triage | ✅ Implemented (Gemma-12B) | MCP multi-agent | Single model, static prompt |
| UC5 | Case creation in DFIR IRIS | ✅ Implemented (basic) | Full lifecycle | Hardcoded severity/assignee |
| UC6 | Auto-containment (firewall block) | ❌ Not implemented | Firewall, isolate, disable | Missing |
| UC7 | Escalation (L1→L2→L3) | ❌ Not implemented | Dynamic escalation chain | Missing |
| UC8 | Notification (email/Slack/Teams) | ❌ Not implemented | Multi-channel | Missing |
| UC9 | Forensics collection | ❌ Not implemented | Log collection, memory dump | Missing |
| UC10 | OT-Safe enforcement | ❌ Not implemented | Forbidden actions, playbook validator | Missing |
| UC11 | Audit trail | ❌ Not implemented | Full action logging | Missing |
| UC12 | Threat hunting | ❌ Not implemented | Query generation + execution | Missing |
| UC13 | Compliance checking | ❌ Not implemented | CIS check, gap analysis | Missing |
| UC14 | Playbook management | ⚠️ n8n UI only | YAML playbooks, Git CI/CD | Less structured |

**Coverage:** 5/14 UCs implemented (36%), 1 partial, 8 missing.

### 5.2 MITRE ATT&CK Mapping

Repo handles:
- **Initial Access** — Webhook receives alerts for various TTPs
- **Collection** — Hash + IP enrichment (T1560, T1071)
- **Analysis** — LLM triage (TP/FP determination)

Repo missing:
- **Response** — No containment, isolation, or remediation actions
- **Recovery** — No post-incident workflow
- **Hunting** — No proactive threat hunting

---

## 6. NFR/Security/Monitoring Mapping

### 6.1 Security Requirements

| Requirement | DCIM-Wiki | Repo | Status |
|-------------|-----------|------|--------|
| **TLS 1.2+** | Required everywhere | HTTP for LLM, self-signed for IRIS | ❌ Gap (P1) |
| **RBAC (OIDC)** | Keycloak, 5 roles | None | ❌ Gap (P1) |
| **Secret Management** | Vault (6 secret types) | Hardcoded IPs + n8n credentials | ❌ Gap (P1) |
| **Webhook Auth** | HMAC-SHA256 | UUID path (obscurity) | ❌ Gap (P1) |
| **API Key Rotation** | 90 days | Not configured | ❌ Gap (P2) |
| **Audit Trail** | Every action logged | None | ❌ Gap (P1) |
| **Network Segmentation** | 3 VLANs | None defined | ❌ Gap (P1) |
| **Data Classification** | Sensitivity levels | Not implemented | ❌ Gap (P2) |

### 6.2 Reliability Requirements

| Requirement | DCIM-Wiki | Repo | Status |
|-------------|-----------|------|--------|
| **HA/DR** | Docker Swarm 3-node | Single n8n instance | ❌ Gap (P1) |
| **Retry Policy** | Exponential backoff, configurable | n8n basic retry | ⚠️ Partial |
| **DLQ** | Dead Letter Queue | None | ❌ Gap (P2) |
| **Idempotency** | Workflow-level | Not guaranteed | ❌ Gap (P2) |
| **Backup** | Automated backup | None | ❌ Gap (P2) |
| **RTO/RPO** | Defined per tier | Not defined | ❌ Gap (P2) |

### 6.3 Monitoring Requirements

| Requirement | DCIM-Wiki | Repo | Status |
|-------------|-----------|------|--------|
| **Prometheus Metrics** | 8 custom metrics | None | ❌ Gap (P2) |
| **Grafana Dashboard** | 7 panels | None | ❌ Gap (P2) |
| **Alert Rules** | 5 alert rules | None | ❌ Gap (P2) |
| **Health Check** | `/api/v1/health` | None | ❌ Gap (P2) |
| **SOC Metrics** | MTTA, MTTC, MTTR | None | ❌ Gap (P2) |

---

## 7. Acceptance Criteria Mapping

| # | Criterion (DCIM-Wiki) | Repo Status | Evidence |
|---|----------------------|-------------|----------|
| 1 | TraceCat deployed (Docker Compose/Swarm) | ❌ | n8n used instead |
| 2 | Web UI accessible via HTTPS | ⚠️ | n8n UI (HTTP assumed) |
| 3 | Alert ingestion from Wazuh via Kafka | ❌ | Direct webhook (no Kafka) |
| 4 | Webhook authentication (HMAC) | ❌ | UUID path only |
| 5 | Playbook execution (basic triage) | ✅ | n8n workflow executes |
| 6 | Case creation from alert | ✅ | DFIR IRIS case created |
| 7 | Auto-containment (firewall block) | ❌ | Not implemented |
| 8 | OT-safe enforcement | ❌ | Not implemented |
| 9 | MCP integration (Claude Code) | ❌ | Local LLM (Gemma) |
| 10 | IAM integration (OIDC) | ❌ | Not implemented |
| 11 | ITSM integration (ServiceNow) | ❌ | DFIR IRIS only |
| 12 | TIP integration (MISP) | ❌ | VT + AlienVault only |
| 13 | CMDB integration | ❌ | Not implemented |
| 14 | Notification (email + Slack) | ❌ | Not implemented |
| 15 | Temporal workflow monitoring | ❌ | n8n UI only |
| 16 | Prometheus metrics exported | ❌ | Not implemented |
| 17 | Grafana dashboard loaded | ❌ | Not implemented |
| 18 | Audit trail logged | ❌ | Not implemented |
| 19 | Secret management (Vault) | ❌ | Hardcoded |
| 20 | HA failover test | ❌ | Single instance |

**Score:** 2/20 = **10%** acceptance criteria met (vs reference design target).

---

## 8. Gap Analysis Summary

### P1 Critical (Must Fix for Production)

| # | Gap | Impact | Fix Effort |
|---|-----|--------|------------|
| G1 | No TLS — HTTP for LLM endpoint | Credential/data exposure | Low (nginx/caddy reverse proxy) |
| G2 | Hardcoded IPs (LLM, IRIS) | Inflexible, not portable | Low (env vars or Vault) |
| G3 | No webhook auth (UUID only) | Anyone can trigger workflow | Medium (HMAC or API key) |
| G4 | No RBAC/OIDC | No access control | High (auth middleware) |
| G5 | No audit trail | Compliance failure | High (logging middleware) |
| G6 | No OT-Safe enforcement | DCIM critical systems at risk | High (validation rules) |
| G7 | Hardcoded severity/assignee in IRIS | No risk-based routing | Medium (dynamic fields) |
| G8 | `allowUnauthorizedCerts: true` | MITM vulnerability | Low (proper TLS) |

### P2 High (Important for Operational Maturity)

| # | Gap | Impact | Fix Effort |
|---|-----|--------|------------|
| G9 | No Kafka message broker | No buffering/replay/fan-out | High (infra setup) |
| G10 | No CMDB enrichment | Alerts lack asset context | Medium (API integration) |
| G11 | No monitoring (Prometheus/Grafana) | Blind operation | Medium (metrics export) |
| G12 | No notification channels | Manual alerting only | Low (email/Slack nodes) |
| G13 | No escalation workflow | No L1→L2→L3 routing | Medium (workflow redesign) |
| G14 | No rate limiting on webhook | DDoS vulnerability | Low (n8n or reverse proxy) |
| G15 | n8n single instance | SPOF | Medium (HA setup) |
| G16 | No DLQ for failed workflows | Silent failures | Medium (error handling) |

### P3 Medium (Enhances Capability)

| # | Gap | Impact | Fix Effort |
|---|-----|--------|------------|
| G17 | No MISP integration | Less comprehensive TIP | Medium (API integration) |
| G18 | No GeoIP enrichment | No location context | Low (MaxMind or Wazuh built-in) |
| G19 | No vuln enrichment | No CVE/CVSS context | Medium (NVD API) |
| G20 | No user context enrichment | No risk scoring per user | Medium (AD/LDAP API) |
| G21 | No MCP protocol | Less flexible AI integration | High (MCP server) |
| G22 | No playbook-as-code (YAML) | Less maintainable | Medium (export/converter) |
| G23 | No forensic collection | No evidence gathering | Medium (artifact collector) |
| G24 | No compliance checking | No CIS/SCA integration | High (CIS-CAT integration) |

---

## 9. Tradeoffs & Pitfalls

### 9.1 Strengths of the Repo

| Strength | Evidence | DCIM-Wiki Relevance |
|----------|----------|---------------------|
| **Working MVP** | Complete flow: alert → enrichment → AI → case | Proves the concept works |
| **Local LLM** | Gemma-12B via OpenAI-compatible API | Cost-effective, air-gappable |
| **Dual TIP** | VirusTotal + AlienVault OTX | Good IOC coverage |
| **Clean n8n Workflow** | 8 nodes, clear flow, documented | Easy to understand/modify |
| **DFIR IRIS Integration** | Direct API, case creation | Matches DCIM-Wiki target |
| **Comprehensive README** | Architecture diagram, setup guide, testing | Good documentation |
| **Wazuh Integration** | Webhook config included | Ready to connect |

### 9.2 Risks & Pitfalls

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Hardcoded IPs** — LLM and IRIS IPs are static | P1 | Move to env vars or Vault |
| **No TLS** — HTTP for LLM, self-signed for IRIS | P1 | Add reverse proxy with TLS |
| **UUID as auth** — Security through obscurity | P1 | Add HMAC or API key auth |
| **Single point of failure** — One n8n instance | P2 | Docker Compose with replicas |
| **No retry logic** — Failed API calls lost | P2 | n8n retry settings or Temporal |
| **Hardcoded severity** — Always "Medium" in IRIS | P1 | Dynamic severity from LLM output |
| **n8n JSON not human-readable** — Hard to diff/review | P2 | Consider YAML playbooks |
| **No OT-Safe rules** — Could trigger actions on DCIM systems | P1 | Add validation layer |

### 9.3 Best Practices Check

| Practice | Status | Notes |
|----------|--------|-------|
| Version control | ✅ | Git repo with README |
| Documentation | ✅ | Comprehensive README with diagrams |
| Credential management | ❌ | n8n credentials (better than hardcoded, but no Vault) |
| Error handling | ⚠️ | Basic n8n error nodes, no DLQ |
| Testing | ✅ | Manual input node for testing |
| Code review | ⚠️ | No CI/CD, no automated tests |
| Secrets in code | ❌ | IPs hardcoded in JSON |
| Least privilege | ❌ | No RBAC |

---

## 10. Unique Items per Source

### 10.1 In Repo but NOT in DCIM-Wiki

| Item | Description | Value |
|------|-------------|-------|
| **AlienVault OTX** | IP reputation via OTX API | Free, good IP intel |
| **Gemma-12B Local LLM** | Cost-effective local AI | Air-gappable, no API costs |
| **n8n Visual Workflow** | Low-code SOAR automation | Easy to modify, no Python required |
| **Manual Test Node** | Built-in testing capability | Good for development |
| **Wazuh Webhook Config** | Ready-to-use ossec.conf snippet | Immediate integration |

### 10.2 In DCIM-Wiki but NOT in Repo

| Item | Description | Priority |
|------|-------------|----------|
| **Kafka message broker** | Buffering, replay, fan-out | P1 |
| **TraceCat SOAR platform** | Enterprise SOAR | P2 (n8n works for MVP) |
| **Temporal workflow engine** | State persistence, compensation | P2 |
| **MCP protocol** | Multi-agent AI integration | P3 |
| **OIDC/Keycloak RBAC** | Access control | P1 |
| **Vault secrets** | Secret management | P1 |
| **Prometheus + Grafana** | Monitoring | P2 |
| **OT-Safe enforcement** | DCIM safety | P1 |
| **Audit trail** | Compliance | P1 |
| **CMDB enrichment** | Asset context | P1 |
| **MISP integration** | Comprehensive TIP | P3 |
| **Docker Swarm HA** | High availability | P2 |

---

## 11. Connection Mapping

### 11.1 How Repo Connects to DCIM-Wiki Architecture

```
DCIM-Wiki Target Architecture Flow:
═══════════════════════════════════════════════════════════════

  Source Systems          Data Pipeline         Core Processing
  ┌──────────┐           ┌──────────┐          ┌──────────────┐
  │ Wazuh    │──────────→│ Kafka    │─────────→│ TraceCat     │
  │ Agents   │           │ (5 topics)│          │ (SOAR)       │
  └──────────┘           └──────────┘          │ ┌──────────┐ │
                                               │ │Temporal  │ │
                                               │ └──────────┘ │
  SOAR Repo Connection Points:                 └──────┬───────┘
  ═════════════════════════════                         │
                                                        ▼
  ┌──────────┐    ┌──────────┐    ┌──────────┐   ┌──────────────┐
  │ Wazuh    │───→│ n8n      │───→│ VT +     │──→│ DFIR IRIS    │
  │ Manager  │    │ Webhook  │    │ OTX      │   │ (Case Mgmt)  │
  │ (level 7)│    │ (repo)   │    │ (enrich) │   └──────────────┘
  └──────────┘    └──────────┘    └──────────┘

  ══════════════════════════════════════════════════════════════
  ▲ Repo replaces Kafka + TraceCat with n8n (simpler, less robust)
  ▲ Repo replaces MCP with local LLM direct API
  ▲ Repo replaces MISP with AlienVault OTX
  ▲ Repo adds Wazuh webhook config (complements SIEM repo)
```

### 11.2 Integration with SIEM Repo

The SOAR repo and SIEM repo are **complementary**:

```
SIEM Repo (madicemerlang/SIEM.git)     SOAR Repo (madicemerlang/SOAR.git)
┌─────────────────────────────┐        ┌─────────────────────────────┐
│ ✅ Wazuh Manager Config     │───────→│ ✅ Wazuh Webhook Receiver   │
│ ✅ Custom Decoders          │ alert  │ ✅ IOC Routing              │
│ ✅ Custom Rules             │ flow   │ ✅ VT + AlienVault Enrich   │
│ ✅ CDB Lists (450K+)        │        │ ✅ LLM Analysis             │
│ ✅ Rsyslog Forwarding       │        │ ✅ DFIR IRIS Case Creation  │
│ ✅ Vulnerability Detection  │        └─────────────────────────────┘
│ ✅ SCA + FIM                │
└─────────────────────────────┘

Connection: Wazuh Manager (SIEM repo) → webhook → n8n (SOAR repo)
```

---

## 12. Three-Way Comparison

| Aspect | SOAR Repo | Actual Architecture | Reference Design |
|--------|-----------|--------------------|--------------------|
| **SOAR Engine** | n8n | Tracecat | TraceCat + Temporal |
| **Alert Bridge** | Wazuh webhook | ElastAlert | Kafka → Webhook |
| **Enrichment** | VT + AlienVault | AbuseIPDB + VT | MISP + AbuseIPDB + VT + CMDB + GeoIP |
| **AI Analysis** | Local LLM (Gemma) | Tracecat AI Agent | MCP (Claude/Codex) |
| **Case Mgmt** | DFIR IRIS (basic) | DFIR IRIS | IRIS (full lifecycle) |
| **Workflow** | n8n visual | Tracecat built-in | Temporal (state machine) |
| **RBAC** | None | None | OIDC + Keycloak |
| **Secrets** | Hardcoded | Not specified | Vault |
| **Monitoring** | None | None | Prometheus + Grafana |
| **HA** | None | None | Docker Swarm 3-node |
| **OT-Safe** | None | None | Enforced |
| **Audit** | None | None | Full logging |

### Alignment Scores

| Source Pair | Score | Status |
|------------|-------|--------|
| SOAR Repo vs Reference Design | **~25%** | Partial — valid MVP, many gaps |
| SOAR Repo vs Actual Architecture | **~60%** | Good — similar intent, different tools |
| Actual Architecture vs Reference Design | **~40%** | Partial — existing gap analysis |

---

## 13. Recommendations

### 13.1 Approach: **Hybrid with Phased Hardening**

The SOAR repo is a **valid starting point** that proves the alert → enrichment → AI → case flow works. Do NOT rewrite to TraceCat immediately. Instead, harden incrementally.

### 13.2 Phase 1: Immediate Hardening (P1 Gaps)

| Action | Gap Fixed | Effort |
|--------|-----------|--------|
| Add Caddy/nginx reverse proxy with TLS | G1, G8 | 0.5 day |
| Move hardcoded IPs to env vars | G2 | 0.5 day |
| Add HMAC or API key auth to webhook | G3 | 1 day |
| Add logging middleware (audit trail) | G5 | 1 day |
| Add OT-Safe validation rules | G6 | 2 days |
| Make IRIS severity/assignee dynamic | G7 | 1 day |
| Enable TLS verify for IRIS | G8 | 0.5 day |

### 13.3 Phase 2: Operational Maturity (P2 Gaps)

| Action | Gap Fixed | Effort |
|--------|-----------|--------|
| Add CMDB enrichment API call | G10 | 2 days |
| Add notification nodes (email/Slack) | G12 | 1 day |
| Add escalation workflow | G13 | 2 days |
| Add Prometheus metrics export | G11 | 2 days |
| Add error handling + DLQ | G16 | 1 day |
| Docker Compose for HA | G15 | 1 day |

### 13.4 Phase 3: Advanced Capabilities (P3 Gaps)

| Action | Gap Fixed | Effort |
|--------|-----------|--------|
| Add MISP integration | G17 | 2 days |
| Add GeoIP enrichment | G18 | 1 day |
| Add vuln enrichment (NVD) | G19 | 2 days |
| Evaluate Kafka for high-volume | G9 | 5 days |
| Evaluate TraceCat migration | G21 | 10 days |

### 13.5 What NOT to Change

| Item | Reason |
|------|--------|
| **n8n workflow structure** | Works well for MVP, valid for <5000 EPS |
| **DFIR IRIS integration** | Matches DCIM-Wiki target |
| **VT + AlienVault enrichment** | Good IOC coverage |
| **Local LLM approach** | Cost-effective, air-gappable |
| **README documentation** | Comprehensive and clear |
| **Wazuh webhook integration** | Ready to connect |

---

## 14. Quality Gate Checklist

- [x] Repo cloned and analyzed (3 files, 8 nodes)
- [x] Reference design read (siem-soar.md, 1044 lines)
- [x] Actual architecture read (siem-soar-actual-architecture.md)
- [x] Existing gap analysis reviewed (siem-soar-gap-analysis.md)
- [x] Existing SIEM alignment reviewed (impl-repo-siem-alignment.md)
- [x] Component-by-component alignment (6 areas)
- [x] UC-based mapping (14 use cases)
- [x] NFR/Security/Monitoring mapping (19 requirements)
- [x] Acceptance criteria mapping (20 criteria)
- [x] Gap analysis (8 P1, 8 P2, 8 P3)
- [x] Tradeoffs & pitfalls documented
- [x] Unique items per source listed
- [x] Connection mapping with ASCII diagram
- [x] Three-way comparison table
- [x] Phased recommendations
- [x] What NOT to change table
- [x] No existing documents modified
- [ ] Update index.md (pending)
- [ ] Update log.md (pending)
- [ ] Send to Discord thread (pending)

---

**Document Version:** v1.0
**Last Updated:** 2026-07-13
**Alignment Score:** ~25% (vs Reference Design), ~60% (vs Actual Architecture)
**Status:** PARTIAL — Valid MVP, needs production hardening
