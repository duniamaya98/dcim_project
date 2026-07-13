---
title: "Use Case Analysis — Workflow Automation (Final)"
created: 2026-06-25
updated: 2026-06-25
type: use-case-analysis
block: 8
phase: 2
status: final
confidence: high
tags: [use-case, workflow-automation, itsm, approval, runbook, remediation, escalation, n8n, temporal]
sources:
  - block8-workflow-automation.md
  - workflow-automation (entity)
  - workflow-automation-patterns (concept)
  - workflow-state-machine (concept)
  - workflow-engine-comparison (concept)
  - fit041-workflow-automation-komparasi.md
purpose: >
  Final Use Case Analysis untuk Workflow Automation.
  Setiap UC dilengkapi: actors, pre-conditions, flow, source systems, data types,
  API endpoints, SLA, data quality, consumers, acceptance criteria.
  Coverage: 7 workflow types, 6 use case categories, 17 use cases.
---

# Use Case Analysis — Workflow Automation (Final)

> **Purpose:** Use Case Analysis final untuk Workflow Automation — ticketing, approval, runbook, remediation, escalation.
> **Cara pakai:** Review per use case untuk memahami workflow apa yang harus dikelola, dari mana datangnya trigger, dengan SLA berapa, dan ke mana output dikirim.
> **Depends on:** Block 8 Reference Design, Block 2 (DI&I), Block 4 (CMDB), Block 6 (SIEM/SOC), Block 7 (Analytics & AI)
> **Related:** [[fit041-workflow-automation-komparasi]] — Komparasi FIT041 Requirements vs DCIM-Wiki

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Use Case Taxonomy](#2-use-case-taxonomy)
3. [Workflow Creation & Management Use Cases (UC1–UC3)](#3-workflow-creation--management-use-cases-uc1uc3)
4. [Execution & Automation Use Cases (UC4–UC6)](#4-execution--automation-use-cases-uc4uc6)
5. [Approval & Governance Use Cases (UC7–UC9)](#5-approval--governance-use-cases-uc7uc9)
6. [ITSM Integration Use Cases (UC10–UC12)](#6-itsm-integration-use-cases-uc10uc12)
7. [Runbook & Remediation Use Cases (UC13–UC15)](#7-runbook--remediation-use-cases-uc13uc15)
8. [Escalation & Notification Use Cases (UC16–UC17)](#8-escalation--notification-use-cases-uc16uc17)
9. [Source System → Use Case Matrix](#9-source-system--use-case-matrix)
10. [Data Type → Use Case Mapping](#10-data-type--use-case-mapping)
11. [API Requirements per Use Case](#11-api-requirements-per-use-case)
12. [SLA & Latency Requirements](#12-sla--latency-requirements)
13. [Data Quality Requirements per Use Case](#13-data-quality-requirements-per-use-case)
14. [Downstream Consumer Mapping](#14-downstream-consumer-mapping)
15. [Acceptance Criteria](#15-acceptance-criteria)
16. [Traceability Matrix](#16-traceability-matrix)

---

## 1. Executive Summary

### Scope

DCIM Core Platform memiliki **6 kategori use case** untuk Workflow Automation:

| Kategori | Jumlah | Prioritas Rata-rata |
|----------|--------|---------------------|
| **Workflow Creation & Management** | 3 use case (UC1–UC3) | P1–P2 |
| **Execution & Automation** | 3 use case (UC4–UC6) | P1–P2 |
| **Approval & Governance** | 3 use case (UC7–UC9) | P1–P2 |
| **ITSM Integration** | 3 use case (UC10–UC12) | P1–P2 |
| **Runbook & Remediation** | 3 use case (UC13–UC15) | P1–P2 |
| **Escalation & Notification** | 2 use case (UC16–UC17) | P1–P2 |
| **Total** | **17 use case** | — |

### Key Findings

1. **7 workflow types** harus didukung: Incident Response, Change Management, Auto-Remediation, Provisioning, Decommission, Compliance Remediation, Maintenance Window
2. **10-state workflow state machine** diperlukan untuk production-grade lifecycle management
3. **5 safety guards** untuk auto-remediation: blast radius, approval, time window, rate limit, dry run
4. **4-level escalation matrix** berdasarkan severity (Critical/High/Medium/Low)
5. **4 approval chains** untuk change management: standard, normal, emergency, critical
6. **5 notification channels** wajib: Email, SMS, Slack, Teams, PagerDuty
7. **Dual-engine orchestration**: n8n (simple automations) + Temporal (complex, long-running)
8. **FIT041 gaps** kritis: Approval Workflows, Auto-Remediation, Escalation Rules tidak ada di FIT041

### Quick Architecture View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                  USE CASES REQUIRING WORKFLOW AUTOMATION                 │
│                                                                         │
│  UC1 Workflow CRUD    UC2 Version Control    UC3 Deployment            │
│  UC4 Alert Trigger    UC5 Scheduled Trigger  UC6 Manual Trigger         │
│  UC7 Single-Level     UC8 Multi-Level        UC9 Batch Approval         │
│  UC10 Ticket Create   UC11 Bidirectional     UC12 Ticket Close          │
│  UC13 Runbook Exec    UC14 Auto-Remediation  UC15 Rollback              │
│  UC16 Time Escalation UC17 Severity Routing                            │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    WORKFLOW AUTOMATION (Block 8)                         │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  Workflow State Machine                           │  │
│  │  Pending → In Progress → Waiting Approval → Approved → Executing │  │
│  │  → Completed / Failed → Rollback                                  │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│  ┌────────────────────────┴─────────────────────────────────────────┐  │
│  │                  Automation Services                              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │  │
│  │  │ ITSM     │ │ Approval │ │ Runbook  │ │ Auto-    │           │  │
│  │  │ Ticketing│ │ Workflows│ │ Engine   │ │Remediation│           │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │  │
│  │  ┌──────────┐ ┌──────────┐                                      │  │
│  │  │Escalation│ │ n8n/     │                                      │  │
│  │  │ Rules    │ │ Temporal │                                      │  │
│  │  └──────────┘ └──────────┘                                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  Notification Layer                               │  │
│  │  Email • SMS • Slack • Teams • Webhook • PagerDuty               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
         │                 │                │
         ▼                 ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │   CMDB   │    │   SIEM   │    │  Analytics   │
  │(impact)  │    │(incidents)│   │  (alerts)    │
  └──────────┘    └──────────┘    └──────────────┘
```

---

## 2. Use Case Taxonomy

### 2.1 Classification

| UC ID | Use Case Name | Category | Priority | Latency Target |
|-------|---------------|----------|----------|----------------|
| UC1 | Workflow Creation & Configuration | Creation & Management | P1 | < 100ms |
| UC2 | Workflow Version Control & Change Management | Creation & Management | P2 | < 200ms |
| UC3 | Workflow Deployment & Activation | Creation & Management | P2 | < 30s |
| UC4 | Alert-Triggered Workflow Execution | Execution & Automation | P1 | < 5min |
| UC5 | Scheduled/Recurring Workflow Execution | Execution & Automation | P2 | < 1min |
| UC6 | Manual Workflow Trigger | Execution & Automation | P1 | < 100ms |
| UC7 | Single-Level Approval | Approval & Governance | P1 | < 1min |
| UC8 | Multi-Level Approval Chains | Approval & Governance | P1 | < 5min |
| UC9 | Batch Approval | Approval & Governance | P2 | < 2min |
| UC10 | ITSM Ticket Creation | ITSM Integration | P1 | < 30s |
| UC11 | ITSM Bidirectional Sync | ITSM Integration | P1 | < 5min |
| UC12 | ITSM Ticket Closure | ITSM Integration | P1 | < 1min |
| UC13 | Runbook Execution | Runbook & Remediation | P1 | < 5min |
| UC14 | Auto-Remediation with Safety Guards | Runbook & Remediation | P1 | < 2min |
| UC15 | Rollback Execution | Runbook & Remediation | P1 | < 5min |
| UC16 | Time-Based Escalation | Escalation & Notification | P1 | < 30min |
| UC17 | Severity-Based Routing | Escalation & Notification | P1 | < 5min |

### 2.2 Priority Distribution

| Priority | Count | Examples |
|----------|-------|----------|
| P1 Critical | 10 | Workflow CRUD, Alert Trigger, Approval, ITSM, Runbook, Escalation |
| P2 High | 7 | Version Control, Deployment, Scheduled, Batch Approval |
| P3 Medium | 0 | — |
| P4 Supporting | 0 | — |

### 2.3 Workflow Types Mapping

| Workflow Type | UCs | Trigger | State Machine | Approval | Runbook | ITSM |
|---------------|-----|---------|---------------|----------|---------|------|
| Incident Response | UC4, UC10, UC16, UC17 | Alert (SIEM/Analytics) | Full | Optional | Yes | Auto-create |
| Change Management | UC8, UC10 | Manual request | Full | Multi-level | Yes | Auto-create |
| Auto-Remediation | UC14, UC15 | Alert threshold | Simplified | Safety guard | Yes | Log only |
| Provisioning | UC6, UC10 | API/Manual | Full | Single-level | Yes | Auto-create |
| Decommission | UC8, UC10 | Manual request | Full | Multi-level | Yes | Auto-create |
| Compliance Remediation | UC14 | CIS violation | Simplified | Required | Yes | Auto-create |
| Maintenance Window | UC5 | Scheduled | Simplified | Required | Yes | Auto-create |

---

## 3. Workflow Creation & Management Use Cases (UC1–UC3)

### 3.1 UC1 — Workflow Creation & Configuration

**Objective:** Operator dapat membuat workflow baru dengan trigger, action, dan logic nodes.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 100ms |
| **Throughput** | 10 req/s |
| **Actors** | Operator, Admin |

#### Workflow Definition

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `workflow_id` | UUID | Auto | Unique identifier |
| `name` | String(100) | Yes | Workflow name |
| `description` | Text | No | Description |
| `owner` | User ID | Yes | Creator |
| `status` | Enum | Auto | Draft/Active/Inactive |
| `trigger_type` | Enum | Yes | Alert/Scheduled/Manual/Webhook |
| `trigger_config` | JSON | Yes | Trigger-specific configuration |
| `actions` | Array | Yes | List of action nodes |
| `logic` | Array | No | Conditional logic nodes |
| `created_at` | Timestamp | Auto | Creation timestamp |
| `updated_at` | Timestamp | Auto | Last update timestamp |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/workflow` | Operator+ | Create workflow |
| GET | `/api/v1/workflow/{id}` | Operator+ | Get workflow detail |
| PUT | `/api/v1/workflow/{id}` | Owner | Update workflow |
| DELETE | `/api/v1/workflow/{id}` | Owner | Delete workflow (soft) |
| GET | `/api/v1/workflow` | Operator+ | List workflows |
| POST | `/api/v1/workflow/{id}/validate` | Operator+ | Validate workflow config |

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | `name`, `trigger_type`, `actions` wajib terisi |
| Accuracy | `trigger_config` harus valid sesuai `trigger_type` |
| Timeliness | Created within 100ms |
| Consistency | `workflow_id` unique across system |
| Validity | `actions` array harus minimal 1 item |

---

### 3.2 UC2 — Workflow Version Control & Change Management

**Objective:** Setiap perubahan workflow ter-version dengan audit trail.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 200ms |
| **Throughput** | 5 req/s |
| **Actors** | Owner, Admin |

#### Version Control Rules

| Rule | Description |
|------|-------------|
| Auto-versioning | Major version saat status change, Minor saat edit |
| Immutability | Published version tidak bisa diubah |
| Rollback | Dapat restore ke version sebelumnya |
| Diff | Perlihatkan perubahan antar version |
| Audit | Semua change tercatat dengan actor + timestamp |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/workflow/{id}/versions` | Operator+ | List versions |
| GET | `/api/v1/workflow/{id}/versions/{v}` | Operator+ | Get specific version |
| POST | `/api/v1/workflow/{id}/versions/{v}/rollback` | Owner | Rollback to version |
| GET | `/api/v1/workflow/{id}/diff` | Operator+ | Compare versions |

---

### 3.3 UC3 — Workflow Deployment & Activation

**Objective:** Deploy workflow dari draft ke active state dengan validasi.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 30s |
| **Throughput** | 1 req/s |
| **Actors** | Operator, Admin |

#### Deployment Flow

```
Draft → Validate Config → Test Run (optional) → Activate → Running
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/workflow/{id}/deploy` | Operator+ | Deploy workflow |
| POST | `/api/v1/workflow/{id}/deactivate` | Operator+ | Deactivate workflow |
| POST | `/api/v1/workflow/{id}/test` | Operator+ | Test run workflow |

---

## 4. Execution & Automation Use Cases (UC4–UC6)

### 4.1 UC4 — Alert-Triggered Workflow Execution

**Objective:** Workflow otomatis dieksekusi saat alert dari SIEM/Analytics memenuhi threshold.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min (end-to-end) |
| **Throughput** | 50 alerts/min |
| **Actors** | System (automated) |

#### Trigger Sources

| Source | Protocol | Data Format |
|--------|----------|-------------|
| SIEM (Wazuh/ES) | Webhook | JSON alert payload |
| Analytics Engine | Webhook | JSON alert with threshold |
| ELK/ElastAlert | Webhook | JSON alert rule match |
| n8n | Webhook | JSON callback |

#### Alert → Workflow Mapping

| Alert Type | Workflow Type | Priority | Timeout |
|------------|---------------|----------|---------|
| Service Down | Incident Response | P1 | 15min |
| High CPU/Memory | Auto-Remediation | P2 | 5min |
| Security Breach | Incident Response | P1 | 10min |
| Capacity Threshold | Auto-Remediation | P2 | 10min |
| CIS Violation | Compliance Remediation | P2 | 30min |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/webhook/alert` | API Key | Receive alert trigger |
| GET | `/api/v1/workflow/execution/{id}` | Operator+ | Check execution status |
| GET | `/api/v1/workflow/execution/{id}/logs` | Operator+ | Get execution logs |

---

### 4.2 UC5 — Scheduled/Recurring Workflow Execution

**Objective:** Workflow dijalankan sesuai schedule (cron-based).

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 1min (from schedule) |
| **Throughput** | 10 schedules |
| **Actors** | System (automated) |

#### Schedule Types

| Type | Example | Use Case |
|------|---------|----------|
| One-time | `2026-06-25T02:00:00` | Maintenance window |
| Daily | `0 2 * * *` | Daily backup verification |
| Weekly | `0 2 * * 0` | Weekly compliance check |
| Monthly | `0 2 1 * *` | Monthly capacity report |

---

### 4.3 UC6 — Manual Workflow Trigger

**Objective:** Operator dapat trigger workflow manual dari dashboard atau API.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 100ms |
| **Throughput** | 10 req/s |
| **Actors** | Operator, Admin |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/workflow/{id}/trigger` | Operator+ | Manual trigger |
| POST | `/api/v1/workflow/{id}/trigger` | Operator+ | Trigger with parameters |

---

## 5. Approval & Governance Use Cases (UC7–UC9)

### 5.1 UC7 — Single-Level Approval

**Objective:** Workflow dengan risiko rendah memerlukan 1 approver.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 1min notification |
| **Throughput** | 20 approvals/min |
| **Actors** | Approver, Operator |

#### Approval Chain Configuration

```yaml
standard_change:
  levels:
    - level: 1
      approvers:
        - role: "team_lead"
      timeout_hours: 4
      escalation: "manager"
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/workflow/approvals/pending` | Approver+ | List pending approvals |
| POST | `/api/v1/workflow/approvals/{id}/approve` | Approver | Approve |
| POST | `/api/v1/workflow/approvals/{id}/reject` | Approver | Reject with reason |

---

### 5.2 UC8 — Multi-Level Approval Chains

**Objective:** Workflow dengan risiko tinggi memerlukan approval bertingkat.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min (per level) |
| **Throughput** | 10 approvals/min |
| **Actors** | Team Lead, Change Manager, Director |

#### Approval Chain Matrix

| Change Type | Level 1 | Level 2 | Level 3 | Level 4 |
|-------------|---------|---------|---------|---------|
| Standard | Team Lead (4h) | — | — | — |
| Normal | Team Lead (4h) | Change Manager (24h) | — | — |
| Emergency | On-call Lead (1h) | Change Manager (4h) | — | — |
| Critical | Team Lead (2h) | Change Manager (4h) | Director (24h) | — |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/workflow/approvals/pending` | Approver+ | List pending approvals |
| POST | `/api/v1/workflow/approvals/{id}/approve` | Approver | Approve current level |
| POST | `/api/v1/workflow/approvals/{id}/reject` | Approver | Reject with reason |
| GET | `/api/v1/workflow/approvals/history` | Operator+ | Approval history |

---

### 5.3 UC9 — Batch Approval

**Objective:** Approve multiple workflows sekaligus untuk efisiensi.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 2min |
| **Throughput** | 50 items/batch |
| **Actors** | Approver, Admin |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/workflow/approvals/batch` | Approver+ | Batch approve |

---

## 6. ITSM Integration Use Cases (UC10–UC12)

### 6.1 UC10 — ITSM Ticket Creation

**Objective:** Auto-create ticket di ServiceNow/Jira saat workflow dibuat.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 30s |
| **Throughput** | 20 tickets/min |
| **Actors** | System (automated) |

#### Integration Matrix

| System | Protocol | Auth | Sync Direction |
|--------|----------|------|----------------|
| ServiceNow | REST API | OAuth2 | Bidirectional |
| Jira | REST API | API Key | Bidirectional |
| Custom ITSM | REST API | API Key | Outbound |

#### Priority Mapping

| DCIM Severity | ServiceNow Priority | Jira Priority |
|---------------|--------------------:|--------------:|
| Critical (P1) | 1 - Critical | Highest |
| High (P2) | 2 - High | High |
| Medium (P3) | 3 - Moderate | Medium |
| Low (P4) | 4 - Low | Low |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/workflow/tickets` | Operator+ | List workflow tickets |
| GET | `/api/v1/workflow/tickets/{id}` | Operator+ | Get ticket detail |
| POST | `/api/v1/workflow/tickets/{id}/sync` | System | Force sync status |

---

### 6.2 UC11 — ITSM Bidirectional Sync

**Objective:** Status workflow dan ticket tetap sinkron secara real-time.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min |
| **Throughput** | 100 syncs/min |
| **Actors** | System (automated) |

#### Sync Rules

| Direction | Trigger | Action |
|-----------|---------|--------|
| Workflow → ITSM | Status change | Update ticket state |
| ITSM → Workflow | Ticket update | Update workflow status |
| Conflict | Both changed | Last-write-wins + audit log |

---

### 6.3 UC12 — ITSM Ticket Closure

**Objective:** Ticket otomatis ditutup saat workflow completed/failed.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 1min |
| **Throughput** | 20 closures/min |
| **Actors** | System (automated) |

#### Closure Rules

| Workflow Status | Ticket Action | Notes |
|-----------------|---------------|-------|
| Completed | Close (Resolved) | Include resolution notes |
| Failed | Close (Incurred) | Include error details |
| Cancelled | Close (Cancelled) | Include cancellation reason |

---

## 7. Runbook & Remediation Use Cases (UC13–UC15)

### 7.1 UC13 — Runbook Execution

**Objective:** Eksekusi prosedur predefined dengan step-by-step tracking.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min per runbook |
| **Throughput** | 10 runbooks/min |
| **Actors** | System (automated), Operator (manual steps) |

#### Runbook Step Types

| Type | Description | Timeout | On Failure |
|------|-------------|---------|------------|
| Automated | Script execution | Configurable | abort/rollback/alert_only |
| Notification | Send notification | Immediate | — |
| Manual | Human verification | Configurable | escalate |
| Wait | Delay execution | Fixed duration | — |

#### Runbook Definition Example

```yaml
runbook:
  id: RB-001
  name: "Restart Java Application"
  triggers:
    - type: "alert"
      alert_name: "high_cpu_usage"
      threshold: 90
  steps:
    - id: step_1
      name: "Pre-flight checks"
      type: "automated"
      script: "scripts/check_service_health.py"
      on_failure: "abort"
    - id: step_2
      name: "Notify stakeholders"
      type: "notification"
      channel: "slack"
    - id: step_3
      name: "Stop application"
      type: "automated"
      script: "scripts/stop_service.py"
      on_failure: "alert_only"
    - id: step_4
      name: "Start application"
      type: "automated"
      script: "scripts/start_service.py"
      on_failure: "rollback"
    - id: step_5
      name: "Verify health"
      type: "automated"
      script: "scripts/verify_health.py"
      on_failure: "rollback"
    - id: step_6
      name: "Manual verification"
      type: "manual"
      assignee: "{{workflow.requester}}"
      timeout_hours: 1
      on_timeout: "escalate"
  rollback:
    - id: rollback_1
      name: "Restore previous version"
      type: "automated"
      script: "scripts/restore_previous.py"
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/runbook` | Operator+ | List runbooks |
| GET | `/api/v1/runbook/{id}` | Operator+ | Get runbook detail |
| POST | `/api/v1/runbook/{id}/execute` | Operator+ | Execute runbook |
| GET | `/api/v1/runbook/execution/{id}` | Operator+ | Get execution status |
| GET | `/api/v1/runbook/execution/{id}/logs` | Operator+ | Get execution logs |

---

### 7.2 UC14 — Auto-Remediation with Safety Guards

**Objective:** Otomatis remediasi alert dengan safety checks.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 2min |
| **Throughput** | 20 remediations/min |
| **Actors** | System (automated) |

#### Safety Guards

| Guard | Description | Action on Violation |
|-------|-------------|---------------------|
| Blast Radius Check | Max CIs affected | Block if > threshold |
| Approval Required | Critical actions need approval | Route to approval |
| Time Window | Only execute during maintenance | Queue for window |
| Rate Limit | Max remediation attempts/hour | Block if exceeded |
| Dry Run | Preview changes before apply | Show preview, await confirm |

#### Remediation Rules

| Rule ID | Name | Trigger | Action | Safety |
|---------|------|---------|--------|--------|
| AR-001 | Restart crashed service | service_down alert | Runbook RB-001 | blast_radius: 3, no approval |
| AR-002 | Block malicious IP | brute_force_detected | Script block_ip.sh | blast_radius: 1, rate_limit: 10 |
| AR-003 | Scale up server | capacity_threshold | Cloud API scale_up | blast_radius: 1, approval required |
| AR-004 | Restart DB replica | replication_lag > 300s | Runbook RB-003 | blast_radius: 5, off_peak |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/remediation/rules` | Admin | List remediation rules |
| POST | `/api/v1/remediation/rules` | Admin | Create remediation rule |
| GET | `/api/v1/remediation/execution/{id}` | Operator+ | Get remediation status |
| POST | `/api/v1/remediation/{id}/dry-run` | Operator+ | Dry run remediation |

---

### 7.3 UC15 — Rollback Execution

**Objective:** Rollback perubahan saat remediation atau runbook gagal.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min |
| **Throughput** | 10 rollbacks/min |
| **Actors** | System (automated), Operator |

#### Rollback Flow

```
Execution Failed → Check Rollback Steps → Execute Rollback → Verify → Complete/Rollback Failed
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/workflow/{id}/rollback` | Operator+ | Trigger rollback |
| GET | `/api/v1/workflow/{id}/rollback/status` | Operator+ | Check rollback status |

---

## 8. Escalation & Notification Use Cases (UC16–UC17)

### 8.1 UC16 — Time-Based Escalation

**Objective:** Escalate workflow ke level berikutnya jika tidak direspon dalam waktu tertentu.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 30min (escalation check interval) |
| **Throughput** | 100 active workflows |
| **Actors** | System (automated) |

#### Escalation Matrix

| Severity | Level 1 (Initial) | Level 2 (+30min) | Level 3 (+1h) | Level 4 (+4h) |
|----------|-------------------|-------------------|----------------|----------------|
| Critical | On-call Engineer | Team Lead | Manager | Director |
| High | On-call Engineer | Team Lead | Manager | — |
| Medium | Team Lead | Manager | — | — |
| Low | Team Lead | — | — | — |

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/api/v1/workflow/escalations` | Operator+ | List escalations |
| GET | `/api/v1/workflow/{id}/escalations` | Operator+ | Get workflow escalations |
| POST | `/api/v1/workflow/{id}/escalations/{level}/acknowledge` | Assignee | Acknowledge escalation |

---

### 8.2 UC17 — Severity-Based Routing

**Objective:** Route workflow ke assignee/queue berdasarkan severity.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min |
| **Throughput** | 50 routings/min |
| **Actors** | System (automated) |

#### Routing Rules

| Severity | Primary Route | Fallback | SLA |
|----------|---------------|----------|-----|
| Critical | On-call Engineer | Team Lead | 15min |
| High | On-call Engineer | Team Lead | 30min |
| Medium | Team Lead | Manager | 2h |
| Low | Team Lead | — | 8h |

#### Notification Channels

| Channel | Use Case | Latency |
|---------|----------|---------|
| Email | All severities | < 5min |
| SMS | Critical, High | < 1min |
| Slack | All severities | < 1min |
| Teams | All severities | < 1min |
| PagerDuty | Critical | < 1min |

---

## 9. Source System → Use Case Matrix

| Source System | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | UC10 | UC11 | UC12 | UC13 | UC14 | UC15 | UC16 | UC17 |
|---------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|------|------|------|------|------|------|------|
| SIEM (Wazuh/ES) | — | — | — | ✓ | — | — | — | — | — | ✓ | — | — | — | — | — | ✓ | ✓ |
| Analytics Engine | — | — | — | ✓ | — | — | — | — | — | ✓ | — | — | — | — | — | ✓ | ✓ |
| ELK/ElastAlert | — | — | — | ✓ | — | — | — | — | — | ✓ | — | — | — | — | — | ✓ | ✓ |
| n8n | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — |
| Dashboard | ✓ | ✓ | ✓ | — | — | ✓ | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ | — | ✓ | ✓ | ✓ |
| ITSM (ServiceNow) | — | — | — | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — |
| ITSM (Jira) | — | — | — | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — |
| CMDB | — | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | — | — | — |
| Webhook (External) | — | — | — | ✓ | — | ✓ | — | — | — | — | — | — | — | — | — | — | — |

---

## 10. Data Type → Use Case Mapping

| Data Type | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | UC10 | UC11 | UC12 | UC13 | UC14 | UC15 | UC16 | UC17 |
|-----------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|------|------|------|------|------|------|------|
| Workflow Definition | ✓ | ✓ | ✓ | — | — | — | — | — | — | — | — | — | — | — | — | — | — |
| Workflow State | — | — | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | — | — | — | — | — | — | ✓ | ✓ |
| Approval Record | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — | — | — | — |
| ITSM Ticket | — | — | — | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — |
| Runbook Definition | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — |
| Execution Log | — | — | — | ✓ | ✓ | ✓ | — | — | — | — | — | — | ✓ | ✓ | ✓ | — | — |
| Escalation Record | — | — | — | — | — | — | — | — | — | — | — | — | — | — | — | ✓ | ✓ |
| Notification | — | — | — | ✓ | — | — | ✓ | ✓ | — | ✓ | — | — | — | — | — | ✓ | ✓ |

---

## 11. API Requirements per Use Case

| UC | Method | Endpoint | Auth | Cache | Rate Limit |
|----|--------|----------|------|-------|------------|
| UC1 | POST | `/api/v1/workflow` | Operator+ | No | 10/min |
| UC1 | GET | `/api/v1/workflow/{id}` | Operator+ | Yes (5min) | 100/min |
| UC1 | PUT | `/api/v1/workflow/{id}` | Owner | No | 10/min |
| UC1 | DELETE | `/api/v1/workflow/{id}` | Owner | No | 5/min |
| UC2 | GET | `/api/v1/workflow/{id}/versions` | Operator+ | Yes (5min) | 50/min |
| UC3 | POST | `/api/v1/workflow/{id}/deploy` | Operator+ | No | 5/min |
| UC4 | POST | `/api/v1/webhook/alert` | API Key | No | 100/min |
| UC5 | — | (internal scheduler) | System | — | — |
| UC6 | POST | `/api/v1/workflow/{id}/trigger` | Operator+ | No | 10/min |
| UC7 | GET | `/api/v1/workflow/approvals/pending` | Approver+ | No | 50/min |
| UC7 | POST | `/api/v1/workflow/approvals/{id}/approve` | Approver | No | 20/min |
| UC8 | GET | `/api/v1/workflow/approvals/pending` | Approver+ | No | 50/min |
| UC8 | POST | `/api/v1/workflow/approvals/{id}/approve` | Approver | No | 20/min |
| UC9 | POST | `/api/v1/workflow/approvals/batch` | Approver+ | No | 5/min |
| UC10 | GET | `/api/v1/workflow/tickets` | Operator+ | Yes (1min) | 50/min |
| UC11 | POST | `/api/v1/workflow/tickets/{id}/sync` | System | No | 100/min |
| UC12 | — | (auto on completion) | System | — | — |
| UC13 | POST | `/api/v1/runbook/{id}/execute` | Operator+ | No | 10/min |
| UC14 | GET | `/api/v1/remediation/rules` | Admin | Yes (5min) | 50/min |
| UC14 | POST | `/api/v1/remediation/{id}/dry-run` | Operator+ | No | 10/min |
| UC15 | POST | `/api/v1/workflow/{id}/rollback` | Operator+ | No | 10/min |
| UC16 | GET | `/api/v1/workflow/escalations` | Operator+ | No | 50/min |
| UC17 | — | (internal routing) | System | — | — |

---

## 12. SLA & Latency Requirements

### 12.1 Tiered Latency

| Tier | Latency | Use Cases | SLA |
|------|---------|-----------|-----|
| Tier 1 (Real-time) | < 100ms | UC1, UC6, UC7 | 99.9% |
| Tier 2 (Near-RT) | < 5min | UC4, UC8, UC10, UC11, UC12, UC13, UC14, UC15 | 99.5% |
| Tier 3 (Scheduled) | < 30min | UC3, UC5, UC16 | 99.0% |
| Tier 4 (Batch) | < 2h | UC9 | 95.0% |

### 12.2 Throughput Targets

| Operation | Target | Resource |
|-----------|--------|----------|
| Workflow creation | < 100ms | 1 vCPU |
| State transition | < 50ms | 1 vCPU |
| Ticket creation | < 30s | 1 vCPU |
| Approval notification | < 1min | 1 vCPU |
| Runbook execution | < 5min | 2 vCPU |
| Auto-remediation | < 2min | 1 vCPU |
| Escalation check | < 30s | 1 vCPU |

---

## 13. Data Quality Requirements per Use Case

| UC | Dimension | Requirement |
|----|-----------|-------------|
| UC1 | Completeness | `name`, `trigger_type`, `actions` wajib |
| UC1 | Accuracy | `workflow_id` unique |
| UC1 | Consistency | Status valid sesuai state machine |
| UC4 | Timeliness | Alert → workflow < 5min |
| UC4 | Accuracy | Alert payload valid |
| UC7 | Completeness | `approver_id`, `decision`, `reason` wajib |
| UC7 | Auditability | Semua approval tercatat dengan timestamp |
| UC10 | Completeness | Ticket mapping wajib (`workflow_id` ↔ `ticket_id`) |
| UC10 | Consistency | Priority mapping sesuai severity |
| UC13 | Completeness | Semua runbook steps ter-log |
| UC13 | Accuracy | Step execution status valid |
| UC14 | Safety | Blast radius check wajib sebelum execution |
| UC14 | Auditability | Semua remediation attempts tercatat |
| UC16 | Timeliness | Escalation check setiap 30 menit |

---

## 14. Downstream Consumer Mapping

| Consumer | Data Consumed | SLA | Protocol |
|----------|---------------|-----|----------|
| CMDB | Impact assessment data | < 5min | REST API |
| SIEM/SOC | Security incident workflows | Real-time | Webhook |
| Analytics Engine | Alert trigger data | < 5min | REST API |
| Dashboard | Workflow status, metrics | < 1min | REST API |
| Notification Service | Email, SMS, Slack, Teams | < 1min | SMTP, API |
| ITSM (ServiceNow) | Ticket data | < 30s | REST API |
| ITSM (Jira) | Issue data | < 30s | REST API |
| PagerDuty | Critical alerts | < 1min | REST API |
| Audit System | Workflow logs | < 5min | REST API |
| Compliance | Audit trail | < 1h | REST API |

---

## 15. Acceptance Criteria

### UC1 — Workflow Creation & Configuration
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Workflow created dengan semua required fields | API response + DB record |
| 2 | Workflow ID unique | Duplicate test |
| 3 | Invalid trigger_type ditolak | Validation error |
| 4 | Empty actions array ditolak | Validation error |
| 5 | Created within 100ms | Performance test |

### UC4 — Alert-Triggered Workflow Execution
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Alert → workflow < 5min | End-to-end test |
| 2 | Alert payload valid → workflow created | Integration test |
| 3 | Invalid alert payload → logged + rejected | Error handling test |
| 4 | Concurrent alerts handled correctly | Load test |

### UC7/UC8 — Approval Workflows
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Single-level approval works | E2E test |
| 2 | Multi-level approval chain works | E2E test |
| 3 | Approval timeout → escalation | Timeout test |
| 4 | Rejection → workflow cancelled/reworked | E2E test |
| 5 | Batch approval works | E2E test |
| 6 | Approval audit trail complete | Audit log |

### UC10/UC11/UC12 — ITSM Integration
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | ServiceNow ticket created | E2E test |
| 2 | Jira ticket created | E2E test |
| 3 | Bidirectional sync works | Sync test |
| 4 | Ticket closed on workflow completion | E2E test |
| 5 | Priority mapping correct | Mapping test |
| 6 | Sync error handling | Error test |

### UC13 — Runbook Execution
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Runbook executed successfully | E2E test |
| 2 | On_failure routing works | Failure test |
| 3 | Manual step + timeout works | Timeout test |
| 4 | Rollback executed on failure | Rollback test |
| 5 | Execution logs complete | Log verification |

### UC14 — Auto-Remediation
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Blast radius check works | Safety test |
| 2 | Rate limit enforced | Rate limit test |
| 3 | Time window check works | Window test |
| 4 | Dry run shows preview | Dry run test |
| 5 | Approval required for critical | Approval test |

### UC16/UC17 — Escalation & Routing
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Time-based escalation works | Timeout test |
| 2 | Severity routing correct | Routing test |
| 3 | Notification channels work | Notification test |
| 4 | Escalation audit trail complete | Audit log |

---

## 16. Traceability Matrix

| UC | Name | Source Block | Related Block | FIT041 Gap | Priority |
|----|------|--------------|---------------|------------|----------|
| UC1 | Workflow Creation | Block 8 §2 | Block 2 (DI&I) | ✅ Aligned (FIT041 §2.1) | P1 |
| UC2 | Version Control | Block 8 §2 | — | ✅ Aligned (FIT041 §2.1.3) | P2 |
| UC3 | Deployment | Block 8 §2 | — | ✅ Aligned (FIT041 §2.1) | P2 |
| UC4 | Alert Trigger | Block 8 §9 | Block 6 (SIEM), Block 7 (Analytics) | ✅ Aligned (FIT041 §4) | P1 |
| UC5 | Scheduled | Block 8 §9 | — | ⚠️ Partial | P2 |
| UC6 | Manual Trigger | Block 8 §9 | — | ✅ Aligned (FIT041 §2.2) | P1 |
| UC7 | Single Approval | Block 8 §4 | Block 4 (CMDB) | ❌ **Missing in FIT041** | P1 |
| UC8 | Multi Approval | Block 8 §4 | Block 4 (CMDB) | ❌ **Missing in FIT041** | P1 |
| UC9 | Batch Approval | Block 8 §4 | — | ❌ **Missing in FIT041** | P2 |
| UC10 | Ticket Create | Block 8 §3 | Block 6 (SIEM) | ⚠️ Generik (FIT041 §4) | P1 |
| UC11 | Bidirectional | Block 8 §3 | Block 6 (SIEM) | ⚠️ Partial | P1 |
| UC12 | Ticket Close | Block 8 §3 | — | ⚠️ Partial | P1 |
| UC13 | Runbook Exec | Block 8 §5 | Block 6 (SIEM) | ❌ **Missing in FIT041** | P1 |
| UC14 | Auto-Remediation | Block 8 §6 | Block 4 (CMDB), Block 7 (Analytics) | ❌ **Missing in FIT041** | P1 |
| UC15 | Rollback | Block 8 §5 | — | ❌ **Missing in FIT041** | P1 |
| UC16 | Time Escalation | Block 8 §7 | — | ❌ **Missing in FIT041** | P1 |
| UC17 | Severity Routing | Block 8 §7 | — | ❌ **Missing in FIT041** | P1 |

### FIT041 Gap Summary

| Gap Type | Count | UCs |
|----------|-------|-----|
| ✅ Aligned | 4 | UC1, UC2, UC3, UC6 |
| ⚠️ Partial | 5 | UC4, UC5, UC10, UC11, UC12 |
| ❌ Missing in FIT041 | 8 | UC7, UC8, UC9, UC13, UC14, UC15, UC16, UC17 |

**Key Finding:** 8 dari 17 use cases (47%) tidak ada di FIT041 requirements. Ini gap kritis untuk:
- **Approval Workflows** (UC7, UC8, UC9) — Change management
- **Runbook Engine** (UC13) — Operational procedures
- **Auto-Remediation** (UC14, UC15) — NOC safety
- **Escalation Rules** (UC16, UC17) — Incident response

---

## References

- [[block8-workflow-automation]] — Reference design spec
- [[workflow-automation]] — Entity page
- [[workflow-automation-patterns]] — Concept page
- [[workflow-state-machine]] — State machine concept
- [[workflow-engine-comparison]] — Engine comparison
- [[fit041-workflow-automation-komparasi]] — FIT041 comparison
- [[dcim-core-platform]] — Parent project
- [[analytics-ai-engine]] — Alert triggers
- [[siem-soc]] — Security incident workflows
- [[cmdb]] — Impact assessment

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-25
> **Purpose:** Use Case Analysis final untuk Workflow Automation
> **Method:** Reference Design (Block 8) + Entity + Concepts + FIT041 Comparison
> **Result:** 17 Use Cases across 6 categories
> **Key Finding:** 47% of UCs missing in FIT041 — Approval, Runbook, Remediation, Escalation are critical gaps
