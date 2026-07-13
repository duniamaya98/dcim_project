---
title: "SIEM SOAR: Reference Design Spec"
created: 2026-06-25
updated: 2026-06-25
type: reference-design
phase: 2
status: generated
confidence: high
tags: [siem, soar, security, tracecat, automation, case-management, playbook, temporal, ai-agent, incident-response]
wiki_pages:
  - siem-soc
  - workflow-automation
  - data-ingestion-integration
  - siem-investigation-runbook
  - siem-solution-comparison
purpose: >
  Reference design spec untuk SIEM SOAR (Security Orchestration, Automation & Response).
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# SIEM SOAR: Reference Design Spec

> **Purpose:** Arsitektur lengkap SIEM SOAR — security orchestration, automated response, case management, playbook automation, dan AI-assisted triage untuk DCIM SOC.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi. Setiap gap = connection point.
> **Architecture Diagram:** `diagrams/siem-soar-architecture.html`
> **Depends on:** Block 1 (Infrastructure), Block 2 (DI&I), Block 6 (SIEM/SOC)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [TraceCat Core Components](#2-tracecat-core-components)
3. [Workflow Engine (Temporal)](#3-workflow-engine-temporal)
4. [Case Management](#4-case-management)
5. [Integration Layer](#5-integration-layer)
6. [AI Agent Integration (MCP)](#6-ai-agent-integration-mcp)
7. [Playbook Design](#7-playbook-design)
8. [Alert → Case → Response Flow](#8-alert--case--response-flow)
9. [SIEM Integration (Wazuh → Kafka → TraceCat)](#9-siem-integration-wazuh--kafka--tracecat)
10. [SOC API](#10-soc-api)
11. [Security](#11-security)
12. [Monitoring & Alerting](#12-monitoring--alerting)
13. [Deployment & Sizing](#13-deployment--sizing)
14. [Acceptance Criteria](#14-acceptance-criteria)
15. [Gap Comparison Template](#15-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SIEM SOAR (TraceCat)                                │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              Alert Ingestion                                          │  │
│  │  Wazuh Alerts → Kafka (dcim.siem.alerts) → TraceCat Webhook         │  │
│  │  Deception Alerts → Kafka → TraceCat Webhook                        │  │
│  │  Physical-Cyber Alerts → Kafka → TraceCat Webhook                   │  │
│  └────────────────────────┬─────────────────────────────────────────────┘  │
│                           │                                                 │
│  ┌────────────────────────┴─────────────────────────────────────────────┐  │
│  │              Workflow Engine (Temporal)                               │  │
│  │  Playbook Execution • State Machine • Retry • Timeout • Compensation │  │
│  └────────────────────────┬─────────────────────────────────────────────┘  │
│                           │                                                 │
│              ┌────────────┴────────────┐                                   │
│              ▼                         ▼                                   │
│  ┌───────────────────┐    ┌────────────────────┐                          │
│  │  Case Management  │    │  Integration Hub   │                          │
│  │  (IRIS)           │    │  (100+ connectors) │                          │
│  └───────────────────┘    └────────────────────┘                          │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              AI Agent Layer (MCP)                                     │  │
│  │  Claude Code • Codex • Cursor → TraceCat MCP Server                  │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │              Vault (Secrets) • TIP (Threat Intel) • ITSM            │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
Security Alert (Wazuh/Deception/Physical-Cyber)
  → Kafka (dcim.siem.alerts)
    → TraceCat Webhook Trigger (TLS)
      → Playbook Execution (Temporal)
        → Enrichment (TIP, CMDB, GeoIP)
        → Triage (AI-assisted risk scoring)
        → Case Creation (IRIS)
        → Response Actions:
          ├─ Auto-containment (firewall, isolate)
          ├─ Ticket creation (ITSM)
          ├─ Notification (email, Slack, Teams)
          ├─ Forensics collection
          └─ Escalation (L1 → L2 → L3)
```

### 1.3 Design Principles

| Principle | Description |
|-----------|-------------|
| **Open Source First** | TraceCat (Apache 2.0) + Temporal + PostgreSQL |
| **Workflow-as-Code** | YAML-based playbooks, version-controlled |
| **AI-Native** | MCP integration for LLM-assisted triage |
| **OT-Safe** | No auto-reboot/patch for DCIM critical systems |
| **Audit Trail** | Every action logged, traceable, reversible |
| **Least Privilege** | RBAC + OIDC/SSO, secrets in Vault |

---

## 2. TraceCat Core Components

### 2.1 Component Architecture

| Component | Role | Technology |
|-----------|------|------------|
| **API Server** | REST API, webhook handlers, auth | Python/FastAPI |
| **Worker** | Background task processing | Python + Temporal |
| **Executor** | Workflow step execution | Python + Temporal |
| **Agent Worker** | AI agent task processing | Python + LLM API |
| **Agent Executor** | AI agent action execution | Python + LLM API |
| **UI** | Web dashboard, playbook builder | React/Next.js |
| **MCP Server** | Model Context Protocol endpoint | Python |
| **Caddy** | Reverse proxy, TLS termination | Caddy |
| **PostgreSQL** | Application database | PostgreSQL 16 |
| **Temporal** | Workflow orchestration | Temporal Server |
| **Temporal DB** | Temporal state store | PostgreSQL 16 |
| **Redis** | Cache, rate limiting | Redis 7 |
| **MinIO** | Object storage (evidence, artifacts) | MinIO |

### 2.2 Component Sizing

| Tier | CPU | RAM | Storage | Workflow/sec | Concurrent Users |
|------|-----|-----|---------|-------------|-----------------|
| **Development** | 8 cores | 16 GB | 20 GB SSD | ~5 | 1-10 |
| **Standard** | 16 cores | 32 GB | 50 GB SSD | ~15 | 10-50 |
| **Production** | 32+ cores | 64+ GB | 100+ GB SSD | ~40 | 50+ |

### 2.3 Docker Swarm Resource Allocation (Production)

| Service | CPU | Memory | Replicas |
|---------|-----|--------|----------|
| caddy | 0.25 | 256 Mi | 1 |
| api | 2 | 4 Gi | 2 |
| worker | 2 | 2 Gi | 4 |
| executor | 4 | 8 Gi | 4 |
| agent-worker | 2 | 2 Gi | 2 |
| agent-executor | 4 | 16 Gi | 2 |
| ui | 0.5 | 1 Gi | 2 |
| mcp | 1 | 1 Gi | 1 |
| postgres_db | 2 | 4 Gi | 1 |
| temporal | 4 | 8 Gi | 1 |
| temporal_db | 2 | 4 Gi | 1 |
| redis | 0.5 | 1 Gi | 1 |
| minio | 0.5 | 1 Gi | 1 |
| **Total** | **~25** | **~52 Gi** | **23** |

---

## 3. Workflow Engine (Temporal)

### 3.1 Purpose

Temporal menyediakan workflow orchestration yang reliable, fault-tolerant, dan auditable untuk semua SOAR playbooks.

### 3.2 Key Features

| Feature | Description |
|---------|-------------|
| **Exactly-once execution** | Workflow tidak duplicate meskipun worker crash |
| **State persistence** | Workflow state tersimpan di DB, bisa resume |
| **Retry policies** | Exponential backoff, configurable max attempts |
| **Timeout** | Execution timeout, step timeout |
| **Compensation** | Undo/rollback actions jika workflow gagal |
| **Visibility** | Temporal UI untuk monitor running workflows |
| **Versioning** | Safe workflow versioning tanpa break existing runs |

### 3.3 Workflow Patterns

```
┌─────────────────────────────────────────────────┐
│ Pattern: Alert Triage Workflow                   │
│                                                  │
│  Start                                          │
│    │                                            │
│    ▼                                            │
│  [Receive Alert]                                │
│    │                                            │
│    ▼                                            │
│  [Enrich Alert] ─── TIP, CMDB, GeoIP           │
│    │                                            │
│    ▼                                            │
│  [Risk Scoring] ─── ML Model / Rule-based       │
│    │                                            │
│    ├─ Low Risk ──→ [Auto-close + Log]           │
│    │                                            │
│    ├─ Medium Risk ──→ [Create Case (L1)]        │
│    │                    │                       │
│    │                    ▼                       │
│    │              [Analyst Review]              │
│    │                    │                       │
│    │              [Resolve / Escalate]          │
│    │                                            │
│    └─ High/Critical ──→ [Auto-Containment]      │
│                          │                      │
│                          ▼                      │
│                    [Create Case (L2/L3)]        │
│                          │                      │
│                          ▼                      │
│                    [Forensics Collection]       │
│                          │                      │
│                          ▼                      │
│                    [Stakeholder Notification]   │
│                          │                      │
│                          ▼                      │
│                    [Escalation Chain]           │
│                          │                      │
│                          ▼                      │
│                    [Post-Incident Review]       │
│                                                  │
│  End                                             │
└─────────────────────────────────────────────────┘
```

### 3.4 Workflow as Code (YAML Example)

```yaml
# playbooks/alert-triage.yaml
name: alert-triage
version: 1
description: "Standard alert triage workflow"
triggers:
  - type: webhook
    path: /api/v1/alerts/ingest

steps:
  - id: enrich
    action: enrich_alert
    inputs:
      sources: [tip, cmdb, geoip]
    timeout: 30s
    retry:
      max_attempts: 3
      backoff: exponential

  - id: risk_score
    action: calculate_risk_score
    inputs:
      model: gradient_boosting
      features:
        - asset_criticality
        - vulnerability_score
        - threat_intel_match
        - user_risk_score

  - id: route
    action: conditional_branch
    conditions:
      - if: risk_score < 30
        goto: auto_close
      - if: risk_score < 60
        goto: create_case_l1
      - if: risk_score < 80
        goto: create_case_l2
      - else:
        goto: auto_containment

  - id: auto_close
    action: close_alert
    inputs:
      reason: "Low risk, auto-closed"
      notify: false

  - id: create_case_l1
    action: create_case
    inputs:
      severity: low
      assignee: l1_queue
      template: standard_triage

  - id: auto_containment
    action: execute_containment
    inputs:
      actions:
        - type: firewall_block
          target: source_ip
          duration: 24h
        - type: isolate_host
          target: affected_host
          safe_mode: true  # No reboot for DCIM
    timeout: 60s

  - id: create_case_l2
    action: create_case
    inputs:
      severity: high
      assignee: l2_queue
      template: incident_response

  - id: notify
    action: send_notification
    inputs:
      channels: [email, slack, teams]
      recipients: on_call

compensation:
  - action: undo_containment
    condition: step.auto_containment.failed
```

---

## 4. Case Management

### 4.1 Purpose

Centralized case tracking untuk semua security incidents, dari alert hingga resolution.

### 4.2 Case Lifecycle

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  New     │───→│  Open    │───→│ In Prog  │───→│ Resolved │
│          │    │          │    │          │    │          │
└──────────┘    └──────────┘    └──────────┘    └──────────┘
     │               │               │               │
     │               │               │               ▼
     │               │               │          ┌──────────┐
     │               │               │          │  Closed  │
     │               │               │          └──────────┘
     │               │               │
     │               │          ┌────┴────┐
     │               │          │Escalated│
     │               │          └────┬────┘
     │               │               │
     │               ▼               ▼
     │          ┌──────────┐   ┌──────────┐
     └─────────→│ Deferred │   │ Reopened │
                └──────────┘   └──────────┘
```

### 4.3 Case Schema

```json
{
  "case": {
    "id": "CASE-2026-000123",
    "title": "Brute Force Attack from 203.0.113.50",
    "severity": "high",
    "status": "in_progress",
    "priority": "P2",
    "created_at": "2026-06-25T10:30:00Z",
    "updated_at": "2026-06-25T11:15:00Z",
    "assignee": "analyst@dcim.example.com",
    "reporter": "system",
    "source": "wazuh",
    "mitre_attack": {
      "tactic": "credential-access",
      "technique": "T1110",
      "sub_technique": "Brute Force"
    },
    "affected_assets": [
      {
        "ci_id": "CI-SERVER-001",
        "type": "server",
        "criticality": "P1",
        "location": "DC-Jakarta-Rack-A1"
      }
    ],
    "alerts": ["ALERT-001", "ALERT-002", "ALERT-003"],
    "timeline": [
      {
        "timestamp": "2026-06-25T10:30:00Z",
        "action": "case_created",
        "actor": "system",
        "details": "Auto-created from alert correlation"
      },
      {
        "timestamp": "2026-06-25T10:35:00Z",
        "action": "analyst_assigned",
        "actor": "system",
        "details": "Assigned to L2 queue"
      }
    ],
    "evidence": [
      {
        "type": "log",
        "source": "wazuh",
        "path": "s3://dcim-evidence/CASE-2026-000123/logs.json"
      }
    ],
    "resolution": null
  }
}
```

### 4.4 Case Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Mean Time to Acknowledge (MTTA) | <15 min | Alert → Case assignment |
| Mean Time to Contain (MTTC) | <30 min | Alert → Containment action |
| Mean Time to Resolve (MTTR) | <4 hours | Case → Resolution |
| Auto-closure Rate | >60% | Low-risk alerts auto-closed |
| Escalation Rate | <25% | Cases escalated to L2/L3 |

---

## 5. Integration Layer

### 5.1 Integration Categories

| Category | Systems | Direction | Protocol |
|----------|---------|-----------|----------|
| **SIEM** | Wazuh, Elasticsearch | Inbound | Webhook, API |
| **EDR** | CrowdStrike, SentinelOne | Inbound | API, Webhook |
| **NDR** | Zeek, Suricata | Inbound | Kafka, Syslog |
| **Firewall** | Palo Alto, Fortinet, iptables | Outbound | API |
| **ITSM** | ServiceNow, Jira | Bidirectional | REST API |
| **Threat Intel** | MISP, AbuseIPDB, VirusTotal | Bidirectional | REST API |
| **Identity** | AD, LDAP, Okta | Inbound | LDAP, API |
| **Communication** | Email, Slack, Teams, Telegram | Outbound | SMTP, Webhook |
| **Cloud** | AWS, Azure, GCP | Bidirectional | SDK, API |
| **DCIM** | Wazuh OT, BMS, PDU | Bidirectional | REST, MQTT |
| **Vulnerability** | Tenable, Qualys | Inbound | API |
| **Forensics** | Velociraptor, GRR | Outbound | API |

### 5.2 Integration Pattern

```
┌─────────────────────────────────────────────────────────┐
│                  TraceCat Integration Hub                │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │  Connector   │  │  Connector   │  │  Connector   │   │
│  │  (Webhook)   │  │  (REST API)  │  │  (Kafka)     │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │            │
│         └────────────────┼────────────────┘            │
│                          │                              │
│                   ┌──────┴──────┐                      │
│                   │  Normalizer  │                      │
│                   │  (ECS/OCSF)  │                      │
│                   └──────┬──────┘                      │
│                          │                              │
│                   ┌──────┴──────┐                      │
│                   │  Action     │                      │
│                   │  Executor   │                      │
│                   └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### 5.3 Action Categories

| Category | Actions | Safety |
|----------|---------|--------|
| **Auto-Containment** | Block IP, isolate host, disable user | Requires approval for P1 assets |
| **Enrichment** | Query TIP, CMDB, GeoIP | Always safe |
| **Notification** | Email, Slack, Teams, SMS | Always safe |
| **Ticketing** | Create/update ITSM ticket | Always safe |
| **Forensics** | Collect logs, memory dump, PCAP | Read-only, safe |
| **Remediation** | Reset password, revoke token, patch | **OT-SAFE: No reboot for DCIM** |
| **Escalation** | Page on-call, notify management | Always safe |

### 5.4 OT-Safe Playbook Rules

```
┌─────────────────────────────────────────────────────────┐
│  ⚠️  OT-SAFE ENFORCEMENT                                │
│                                                         │
│  FORBIDDEN ACTIONS (DCIM Critical Systems):             │
│  ✗ Auto-reboot servers                                  │
│  ✗ Auto-patch without maintenance window                │
│  ✗ Auto-shutdown PDU/Cooling/BMS                        │
│  ✗ Modify OT network configuration                      │
│  ✗ Disable access control systems                       │
│                                                         │
│  REQUIRED APPROVAL:                                     │
│  • Any action on P1/P2 DCIM assets                      │
│  • Network configuration changes                        │
│  • User account modifications                           │
│  • Firewall rule changes (production)                   │
│                                                         │
│  ENFORCEMENT:                                           │
│  • Playbook validator rejects forbidden actions         │
│  • Runtime guard checks asset criticality               │
│  • Vault secret injection (no hardcoded creds)          │
└─────────────────────────────────────────────────────────┘
```

---

## 6. AI Agent Integration (MCP)

### 6.1 Purpose

Mengintegrasikan LLM agents (Claude Code, Codex, Cursor) ke TraceCat untuk AI-assisted triage, playbook generation, dan threat analysis.

### 6.2 MCP Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent Layer                        │
│                                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │
│  │ Claude Code  │  │ OpenAI Codex│  │   Cursor     │   │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘   │
│         │                │                │            │
│         └────────────────┼────────────────┘            │
│                          │                              │
│                   ┌──────┴──────┐                      │
│                   │  MCP Server  │                      │
│                   │  (TraceCat)  │                      │
│                   └──────┬──────┘                      │
│                          │                              │
│                   ┌──────┴──────┐                      │
│                   │  TraceCat   │                      │
│                   │  API Layer  │                      │
│                   └─────────────┘                      │
└─────────────────────────────────────────────────────────┘
```

### 6.3 MCP Capabilities

| Capability | Description | Example |
|------------|-------------|---------|
| **Alert Analysis** | LLM analyzes alert context | "Explain this alert and suggest response" |
| **Playbook Generation** | Generate playbook from natural language | "Create playbook for brute force response" |
| **Threat Hunting** | Generate hunting queries | "Hunt for lateral movement patterns" |
| **Case Enrichment** | Auto-enrich cases with context | "What MITRE techniques are relevant?" |
| **Report Generation** | Generate incident reports | "Generate executive summary for this case" |
| **Playbook Review** | Review playbook for gaps | "Review this playbook for OT safety" |

### 6.4 Authentication

| Method | Use Case | Security |
|--------|----------|----------|
| **OAuth (OIDC)** | Interactive use (browser) | SSO with Keycloak |
| **PAT (Personal Access Token)** | Headless/automation | Token rotation every 90 days |
| **Service Account** | CI/CD, scheduled tasks | Least privilege, audit trail |

---

## 7. Playbook Design

### 7.1 Playbook Categories

| Category | Playbooks | Trigger | Automation Level |
|----------|-----------|---------|-----------------|
| **Alert Triage** | Auto-close, L1 queue, escalate | Alert received | Fully automated |
| **Containment** | Block IP, isolate host, disable user | High-risk alert | Semi-automated (approval) |
| **Enrichment** | TIP lookup, CMDB query, GeoIP | Alert received | Fully automated |
| **Notification** | Email, Slack, Teams, SMS | Case created/updated | Fully automated |
| **Forensics** | Log collection, memory dump | Incident confirmed | Semi-automated |
| **Compliance** | CIS check, gap analysis | Scheduled | Fully automated |
| **Threat Hunting** | Query generation, execution | Scheduled/on-demand | Semi-automated |
| **OT-Safe Response** | Read-only containment | OT alert | Automated (no approval for read-only) |

### 7.2 Playbook Template

```yaml
# templates/playbook-template.yaml
name: playbook-name
version: 1
description: "Brief description"
category: triage|containment|enrichment|notification|forensics
ot_safe: true|false
trigger:
  type: webhook|schedule|manual
  path: /api/v1/playbooks/{name}/trigger

inputs:
  - name: alert_id
    type: string
    required: true
  - name: severity
    type: enum
    values: [low, medium, high, critical]

steps:
  - id: step_1
    action: action_name
    inputs:
      param: value
    timeout: 30s
    retry:
      max_attempts: 3
      backoff: exponential
    on_failure: continue|abort|compensate

outputs:
  - name: case_id
    type: string
  - name: actions_taken
    type: array

compensation:
  - step: step_1
    action: undo_action
    condition: on_failure
```

### 7.3 Standard Playbooks

| Playbook | Trigger | Steps | OT-Safe |
|----------|---------|-------|---------|
| **Brute Force Response** | 5+ failed logins in 1min | Enrich → Risk Score → Block IP → Notify | Yes |
| **Malware Detected** | EDR alert | Enrich → Isolate Host → Collect Forensics → Notify | Yes |
| **Phishing Reported** | User report | Analyze URL → Block Domain → Reset Credentials → Notify | Yes |
| **Data Exfiltration** | DLP alert | Enrich → Block Destination → Collect Evidence → Notify | Yes |
| **Privilege Escalation** | IAM alert | Enrich → Revoke Token → Reset Password → Notify | Yes |
| **OT Intrusion** | Physical-Cyber alert | Enrich → Read-only Contain → Notify → Escalate | Yes |
| **DDoS Detected** | Network alert | Enrich → Activate Mitigation → Notify ISP | Yes |
| **Insider Threat** | Behavioral alert | Enrich → Monitor → Escalate to HR/Legal | Yes |

---

## 8. Alert → Case → Response Flow

### 8.1 End-to-End Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    SIEM SOAR Response Flow                                   │
│                                                                             │
│  1. ALERT INGESTION                                                         │
│     Wazuh Agent → Syslog → Kafka (dcim.siem.alerts)                        │
│       → TraceCat Webhook (TLS)                                             │
│                                                                             │
│  2. ENRICHMENT (Auto)                                                       │
│     ├─ Threat Intel (MISP) → IOC match                                     │
│     ├─ CMDB → Asset criticality, owner, location                           │
│     ├─ GeoIP → Geolocation, ASN                                            │
│     ├─ Vulnerability → CVE, CVSS                                           │
│     └─ User Context → Role, department, risk score                         │
│                                                                             │
│  3. TRIAGE (AI-Assisted)                                                    │
│     ├─ Risk Score Calculation (ML model)                                   │
│     ├─ MITRE ATT&CK Mapping                                                │
│     ├─ Similar Case Lookup                                                 │
│     └─ Recommended Response                                                │
│                                                                             │
│  4. ROUTING                                                                 │
│     ├─ Risk < 30 → Auto-close (log only)                                  │
│     ├─ Risk 31-60 → L1 Queue                                              │
│     ├─ Risk 61-80 → L2 Queue + Case                                       │
│     └─ Risk 81-100 → Auto-containment + L3 + Case                         │
│                                                                             │
│  5. RESPONSE                                                                │
│     ├─ Auto-Containment: Block IP, Isolate Host                           │
│     ├─ Case Creation: IRIS (severity, assignee, template)                 │
│     ├─ Notification: Email + Slack + Teams                                │
│     ├─ Ticket: ServiceNow/Jira                                             │
│     ├─ Forensics: Log collection, memory dump                              │
│     └─ Escalation: L1 → L2 → L3 → CISO                                   │
│                                                                             │
│  6. RESOLUTION                                                              │
│     ├─ Root Cause Analysis                                                 │
│     ├─ Remediation Actions                                                 │
│     ├─ Post-Incident Review                                                │
│     └─ Detection Rule Update (if needed)                                   │
│                                                                             │
│  7. FEEDBACK LOOP                                                           │
│     ├─ Analyst feedback → ML model retraining                              │
│     ├─ New detection rules → Git → CI/CD                                   │
│     └─ Playbook improvements → Git                                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 9. SIEM Integration (Wazuh → Kafka → TraceCat)

### 9.1 Integration Architecture

```
Wazuh Manager
  │
  ├─ Alert Output → Syslog (TCP 514)
  │    │
  │    └─→ NiFi Syslog Processor
  │         │
  │         └─→ Kafka (dcim.siem.alerts)
  │              │
  │              ├─→ TraceCat Webhook (TLS)
  │              │    │
  │              │    └─→ Playbook Execution
  │              │
  │              └─→ Elasticsearch (dcim-siem-alerts-*)
  │                   │
  │                   └─→ Kibana Dashboard
  │
  └─ Active Response → TraceCat API (outbound)
```

### 9.2 Kafka Topic Configuration

| Topic | Partitions | Replication | Retention | Consumers |
|-------|-----------|-------------|-----------|-----------|
| `dcim.siem.alerts` | 6 | 3 | 7 days | TraceCat, Elasticsearch |
| `dcim.siem.cases` | 3 | 3 | 30 days | TraceCat, ITSM |
| `dcim.siem.actions` | 3 | 3 | 30 days | TraceCat, Audit |

### 9.3 Webhook Configuration

```yaml
# TraceCat webhook trigger config
webhook:
  path: /api/v1/alerts/ingest
  method: POST
  auth:
    type: hmac_sha256
    secret: vault:secret/tracecat/webhook-secret
  validation:
    schema: wazuh_alert_v4
    required_fields: [alert_id, timestamp, rule_id, agent_id]
  rate_limit:
    max_requests: 1000
    window: 1m
```

### 9.4 Alert Normalization

```json
{
  "tracecat_alert": {
    "alert_id": "WAZUH-2026-06-25-001234",
    "timestamp": "2026-06-25T10:30:00Z",
    "source": "wazuh",
    "severity": "high",
    "rule": {
      "id": 5712,
      "description": "Multiple authentication failures",
      "mitre": {
        "tactic": "credential-access",
        "technique": "T1110"
      }
    },
    "agent": {
      "id": "001",
      "name": "dcim-server-01",
      "ip": "10.0.1.50"
    },
    "source_ip": "203.0.113.50",
    "user": "admin",
    "data": {
      "program": "sshd",
      "action": "failed"
    }
  }
}
```

---

## 10. SOC API

### 10.1 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/alerts/ingest` | Ingest alert from SIEM |
| `GET` | `/api/v1/cases` | List cases |
| `POST` | `/api/v1/cases` | Create case |
| `GET` | `/api/v1/cases/{id}` | Get case details |
| `PUT` | `/api/v1/cases/{id}` | Update case |
| `POST` | `/api/v1/cases/{id}/escalate` | Escalate case |
| `GET` | `/api/v1/playbooks` | List playbooks |
| `POST` | `/api/v1/playbooks/{name}/trigger` | Trigger playbook |
| `GET` | `/api/v1/workflows` | List running workflows |
| `GET` | `/api/v1/workflows/{id}` | Get workflow status |
| `GET` | `/api/v1/metrics` | SOC metrics |
| `GET` | `/api/v1/health` | Health check |

### 10.2 Authentication

| Method | Use Case |
|--------|----------|
| **OIDC (Keycloak)** | Web UI, MCP |
| **API Key** | Service-to-service |
| **HMAC Signature** | Webhook ingestion |

### 10.3 Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/api/v1/alerts/ingest` | 1000 req | 1 min |
| `/api/v1/cases` | 100 req | 1 min |
| `/api/v1/playbooks/*` | 50 req | 1 min |
| `/api/v1/metrics` | 30 req | 1 min |

---

## 11. Security

### 11.1 RBAC Matrix

| Role | Alerts | Cases | Playbooks | Workflows | Settings |
|------|--------|-------|-----------|-----------|----------|
| **SOC Analyst L1** | Read | Read, Update | Read | Read | - |
| **SOC Analyst L2** | Read | Read, Update, Escalate | Read, Execute | Read | - |
| **SOC Analyst L3** | Read, Delete | All | All | All | Read |
| **SOC Manager** | All | All | All | All | Read |
| **Admin** | All | All | All | All | All |

### 11.2 Secret Management

| Secret | Storage | Rotation |
|--------|---------|----------|
| Webhook HMAC Secret | Vault | 90 days |
| API Keys | Vault | 90 days |
| Database Credentials | Vault | 90 days |
| TLS Certificates | Vault | 365 days |
| LLM API Keys | Vault | 90 days |
| SMTP Credentials | Vault | 90 days |

### 11.3 Audit Trail

Every action in TraceCat is logged:
- Who (user/service)
- What (action)
- When (timestamp)
- Where (source IP)
- Result (success/failure)
- Evidence (if applicable)

### 11.4 Network Security

| Zone | Access | TLS |
|------|--------|-----|
| DMZ (Sources) | Alert ingestion only | Required |
| Data (Processing) | Internal only | Required |
| Management (SOAR/IRIS) | SOC team only | Required |
| Vault | All services | Required |

---

## 12. Monitoring & Alerting

### 12.1 Key Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Alert Ingestion Latency | <5s p99 | >10s |
| Playbook Execution Time | <30s p95 | >60s |
| Case Creation Time | <10s p99 | >30s |
| Webhook Success Rate | >99.9% | <99% |
| Temporal Worker Lag | <100 tasks | >500 tasks |
| PostgreSQL Connections | <80% max | >90% |
| Redis Memory | <70% max | >85% |
| MinIO Storage | <80% max | >90% |

### 12.2 Prometheus Metrics

```yaml
# TraceCat custom metrics
metrics:
  - name: tracecat_alerts_ingested_total
    type: counter
    labels: [source, severity]

  - name: tracecat_playbook_execution_duration_seconds
    type: histogram
    labels: [playbook, status]

  - name: tracecat_cases_created_total
    type: counter
    labels: [severity, source]

  - name: tracecat_cases_open_gauge
    type: gauge
    labels: [severity]

  - name: tracecat_webhook_requests_total
    type: counter
    labels: [status, endpoint]
```

### 12.3 Grafana Dashboard

| Panel | Description |
|-------|-------------|
| Alert Volume | Alerts per hour by source/severity |
| Case Volume | Cases per day by status |
| Response Time | MTTA, MTTC, MTTR trends |
| Playbook Performance | Execution time, success rate |
| Top MITRE Techniques | Most common attack patterns |
| Analyst Workload | Cases per analyst |
| SLA Compliance | % cases within SLA |

### 12.4 Alert Rules

| Rule | Condition | Action |
|------|-----------|--------|
| High Alert Volume | >2x normal in 1hr | Notify SOC Manager |
| Playbook Failure | >5% failure rate | Notify DevOps |
| Worker Lag | >500 pending tasks | Scale workers |
| Database Connection | >90% utilization | Notify DBA |
| Storage Capacity | >90% utilization | Notify Infra |

---

## 13. Deployment & Sizing

### 13.1 Deployment Options

| Option | Use Case | Complexity |
|--------|----------|------------|
| **Docker Compose** | Dev, small teams | Low |
| **Docker Swarm** | Standard, medium teams | Medium |
| **Kubernetes** | Production, large teams | High |

### 13.2 Production Deployment (Docker Swarm)

```
┌─────────────────────────────────────────────────────────────┐
│                    Management VLAN (VLAN 30)                 │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  TraceCat Cluster (3 nodes)                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐              │   │
│  │  │ Node 1  │ │ Node 2  │ │ Node 3  │              │   │
│  │  │ API     │ │ API     │ │ Worker  │              │   │
│  │  │ Worker  │ │ Worker  │ │ Worker  │              │   │
│  │  │ Executor│ │ Executor│ │ Executor│              │   │
│  │  └─────────┘ └─────────┘ └─────────┘              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Temporal Cluster                                    │   │
│  │  ┌─────────┐ ┌─────────────┐                       │   │
│  │  │Temporal │ │Temporal DB  │                       │   │
│  │  │Server   │ │(PostgreSQL) │                       │   │
│  │  └─────────┘ └─────────────┘                       │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Data Layer                                          │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐              │   │
│  │  │PostgreSQL│ │ Redis   │ │ MinIO   │              │   │
│  │  └─────────┘ └─────────┘ └─────────┘              │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Caddy (Reverse Proxy + TLS)                        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 13.3 Network Requirements

| Port | Protocol | Source | Destination | Purpose |
|------|----------|--------|-------------|---------|
| 443 | TCP | SOC Analysts | Caddy | Web UI |
| 8080 | TCP | Kafka | TraceCat | Alert ingestion |
| 5432 | TCP | TraceCat | PostgreSQL | App DB |
| 6379 | TCP | TraceCat | Redis | Cache |
| 9000 | TCP | TraceCat | MinIO | Object storage |
| 7233 | TCP | TraceCat | Temporal | Workflow engine |
| 9090 | TCP | Prometheus | TraceCat | Metrics |

---

## 14. Acceptance Criteria

| # | Criterion | Test Method | Status |
|---|-----------|-------------|--------|
| 1 | TraceCat部署成功 (Docker Compose/Swarm) | `docker compose ps` — all healthy | ⬜ |
| 2 | Web UI accessible via HTTPS | Browser access, login with OIDC | ⬜ |
| 3 | Alert ingestion from Wazuh via Kafka | Send test alert, verify in TraceCat | ⬜ |
| 4 | Webhook authentication (HMAC) | Send invalid signature, verify rejection | ⬜ |
| 5 | Playbook execution (basic triage) | Trigger playbook, verify steps complete | ⬜ |
| 6 | Case creation from alert | Alert → Case, verify all fields populated | ⬜ |
| 7 | Auto-containment (firewall block) | Trigger high-risk alert, verify IP blocked | ⬜ |
| 8 | OT-safe enforcement | Try forbidden action, verify blocked | ⬜ |
| 9 | MCP integration (Claude Code) | Connect via MCP, verify capabilities | ⬜ |
| 10 | IAM integration (OIDC) | Login with SSO, verify RBAC roles | ⬜ |
| 11 | ITSM integration (ServiceNow) | Create ticket from case, verify sync | ⬜ |
| 12 | TIP integration (MISP) | Enrich alert with IOCs | ⬜ |
| 13 | CMDB integration | Enrich alert with asset context | ⬜ |
| 14 | Notification (email + Slack) | Send notification, verify delivery | ⬜ |
| 15 | Temporal workflow monitoring | Check Temporal UI for running workflows | ⬜ |
| 16 | Prometheus metrics exported | Query `/metrics` endpoint | ⬜ |
| 17 | Grafana dashboard loaded | Import dashboard, verify panels | ⬜ |
| 18 | Audit trail logged | Perform action, verify audit log | ⬜ |
| 19 | Secret management (Vault) | Verify no hardcoded secrets | ⬜ |
| 20 | HA failover test | Kill one node, verify service continues | ⬜ |

---

## 15. Gap Comparison Template

### Gap: SIEM SOAR

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| SOAR Platform | TraceCat (self-hosted) | [aktual] | [match/mismatch] | P1 |
| Deployment | Docker Swarm (3 nodes) | [aktual] | [match/mismatch] | P1 |
| Workflow Engine | Temporal | [aktual] | [match/mismatch] | P1 |
| Case Management | IRIS integration | [aktual] | [match/mismatch] | P1 |
| Alert Ingestion | Kafka webhook | [aktual] | [match/mismatch] | P1 |
| AI Agent (MCP) | Claude Code, Codex | [aktual] | [match/mismatch] | P2 |
| ITSM Integration | ServiceNow, Jira | [aktual] | [match/mismatch] | P2 |
| TIP Integration | MISP, AbuseIPDB | [aktual] | [match/mismatch] | P2 |
| CMDB Integration | Asset enrichment | [aktual] | [match/mismatch] | P1 |
| OT-Safe Playbooks | Forbidden actions enforced | [aktual] | [match/mismatch] | P1 |
| RBAC | OIDC + Keycloak | [aktual] | [match/mismatch] | P1 |
| Audit Trail | Full action logging | [aktual] | [match/mismatch] | P1 |
| Monitoring | Prometheus + Grafana | [aktual] | [match/mismatch] | P2 |
| HA/DR | Docker Swarm replicas | [aktual] | [match/mismatch] | P1 |
| Secret Management | Vault | [aktual] | [match/mismatch] | P1 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

| Document | Relevance |
|----------|-----------|
| [TraceCat Documentation](https://docs.tracecat.com) | Official TraceCat docs |
| [TraceCat GitHub](https://github.com/TracecatHQ/tracecat) | Source code, issues |
| [Temporal Documentation](https://docs.temporal.io) | Workflow engine docs |
| Block 6 — SIEM/SOC v3 | SIEM architecture, detection rules |
| Block 1 — Infrastructure | Base infrastructure provisioning |
| Block 2 — DI&I | Data ingestion pipeline |
| Block 8 — Workflow Automation | General workflow patterns |

---

**Document Version:** v1.0
**Last Updated:** 2026-06-25
**Architecture Diagram:** `diagrams/siem-soar-architecture.html`
