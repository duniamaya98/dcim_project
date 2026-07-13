---
title: "Use Case Analysis — Workflow Automation (Final v2.0)"
created: 2026-06-25
updated: 2026-06-25
type: use-case-analysis
block: 8
phase: 2
status: final
version: "2.0"
confidence: high
tags: [use-case, workflow-automation, itsm, approval, runbook, remediation, escalation, n8n, temporal, merged]
sources:
  - IF-Use_Case_Analysis_Workflow_Automation-FIT041-20260121.md
  - workflow-automation-use-case-analysis-final.md (v1.0)
  - fit041-workflow-automation-use-case-komparasi.md
  - block8-workflow-automation.md
  - workflow-automation (entity)
  - workflow-automation-patterns (concept)
  - workflow-state-machine (concept)
  - workflow-engine-comparison (concept)
purpose: >
  Final Use Case Analysis untuk Workflow Automation — merged dari FIT041 (3 operational scenarios) + DCIM-Wiki (17 technical UCs).
  Setiap UC dilengkapi: actors, pre-conditions, flow, source systems, data types,
  API endpoints, SLA, data quality, consumers, acceptance criteria.
  FIT041 actors/pre-conditions/flow diadopsi untuk UC4, UC5, UC8, UC10, UC13, UC14.
---

# Use Case Analysis — Workflow Automation (Final v2.0)

> **Purpose:** Use Case Analysis final untuk Workflow Automation — merged dari FIT041 Requirements + DCIM-Wiki Implementation.
> **Cara pakai:** Review per use case untuk memahami workflow apa yang harus dikelola, dari mana datangnya trigger, dengan SLA berapa, dan ke mana output dikirim.
> **Depends on:** Block 8 Reference Design, FIT041 Use Case Analysis, Block 2 (DI&I), Block 4 (CMDB), Block 6 (SIEM/SOC), Block 7 (Analytics & AI)
> **Merge Source:** FIT041 Use Case Analysis Workflow Automation (Jan 2026) + DCIM-Wiki Use Case Analysis (Jun 2026)
> **Traceability:** UC4, UC5, UC8, UC10, UC13, UC14 dilengkapi dari FIT041 actors/pre-conditions/flow
> **Related:** [[fit041-workflow-automation-use-case-komparasi]] — Komparasi FIT041 UC Analysis vs DCIM-Wiki

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Merge Summary](#2-merge-summary)
3. [Use Case Taxonomy](#3-use-case-taxonomy)
4. [Workflow Creation & Management Use Cases (UC1–UC3)](#4-workflow-creation--management-use-cases-uc1uc3)
5. [Execution & Automation Use Cases (UC4–UC6)](#5-execution--automation-use-cases-uc4uc6)
6. [Approval & Governance Use Cases (UC7–UC9)](#6-approval--governance-use-cases-uc7uc9)
7. [ITSM Integration Use Cases (UC10–UC12)](#7-itsm-integration-use-cases-uc10uc12)
8. [Runbook & Remediation Use Cases (UC13–UC15)](#8-runbook--remediation-use-cases-uc13uc15)
9. [Escalation & Notification Use Cases (UC16–UC17)](#9-escalation--notification-use-cases-uc16uc17)
10. [Source System → Use Case Matrix](#10-source-system--use-case-matrix)
11. [Data Type → Use Case Mapping](#11-data-type--use-case-mapping)
12. [API Requirements per Use Case](#12-api-requirements-per-use-case)
13. [SLA & Latency Requirements](#13-sla--latency-requirements)
14. [Data Quality Requirements per Use Case](#14-data-quality-requirements-per-use-case)
15. [Downstream Consumer Mapping](#15-downstream-consumer-mapping)
16. [Acceptance Criteria](#16-acceptance-criteria)
17. [Traceability Matrix](#17-traceability-matrix)
18. [Appendix: FIT041 Requirements Checklist](#18-appendix-fit041-requirements-checklist)

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

### Merge Summary

| Aspek | FIT041 | DCIM-Wiki | Merged |
|-------|--------|-----------|--------|
| Use Cases | 3 (operational scenarios) | 17 (technical UCs) | **17** (FIT041 UCs absorbed) |
| Actors per UC | ✅ Listed | ⚠️ Implicit | **✅** (UC4, UC5, UC8 dari FIT041) |
| Pre-conditions | ✅ Listed | ⚠️ Implicit | **✅** (UC4, UC5, UC8 dari FIT041) |
| Flow Steps | ✅ 5-6 step | ✅ Architecture | **✅** (merged) |
| Success Criteria | ✅ Time-bound | ⚠️ Acceptance criteria | **✅** (UC14 enriched) |
| API Endpoints | — | 22 endpoints | **22 endpoints** |
| SLA Tiers | 1 (5min) | 6 tiers | **6 tiers** |
| Data Quality | — | Per-UC rules | **Per-UC rules** |
| Acceptance Criteria | — | 25 items | **28 items** (FIT041 enriched) |

### Key Findings

1. **7 workflow types** harus didukung: Incident Response, Change Management, Auto-Remediation, Provisioning, Decommission, Compliance Remediation, Maintenance Window
2. **10-state workflow state machine** diperlukan untuk production-grade lifecycle management
3. **5 safety guards** untuk auto-remediation: blast radius, approval, time window, rate limit, dry run
4. **4-level escalation matrix** berdasarkan severity (Critical/High/Medium/Low)
5. **4 approval chains** untuk change management: standard, normal, emergency, critical
6. **5 notification channels** wajib: Email, SMS, Slack, Teams, PagerDuty
7. **Dual-engine orchestration**: n8n (simple automations) + Temporal (complex, long-running)
8. **FIT041 actors/pre-conditions** diadopsi untuk UC4, UC5, UC8 sebagai traceability baseline
9. **FIT041 operational flows** diadopsi untuk UC4, UC13, UC14 sebagai acceptance test scenarios

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

## 2. Merge Summary

### 2.1 FIT041 UCs Merged

| FIT041 UC | FIT041 Field | Target DCIM-Wiki UC | Enrichment |
|-----------|-------------|---------------------|------------|
| UC1 (Service Restart) | Actors | UC4 (Alert Trigger) | Monitoring System, Analytics & AI Engine, Hypervisor/Server OS |
| UC1 (Service Restart) | Pre-conditions | UC4 (Alert Trigger) | Server accessible, approved remediation workflow exists |
| UC1 (Service Restart) | Flow | UC4, UC13, UC14 | Trigger → verify → attempt → check → conditional |
| UC1 (Service Restart) | Success Criteria | UC14 (Auto-Remediation) | Service restarted within 5min, ticket auto-closed |
| UC2 (Decommission) | Actors | UC8 (Multi-Approval) | Asset Manager, Server Provisioning System |
| UC2 (Decommission) | Pre-conditions | UC8 (Multi-Approval) | Workloads migrated, server powered down |
| UC2 (Decommission) | Flow | UC13 (Runbook) | Network cleanup → security → CMDB → financial → physical |
| UC3 (Maintenance) | Actors | UC5 (Scheduled) | DCIM Operator |
| UC3 (Maintenance) | Pre-conditions | UC5 (Scheduled) | Approvals secured, CMDB accurate dependency mapping |
| UC3 (Maintenance) | Flow | UC13 (Runbook) | Query → shutdown → power off → restart → notification |

### 2.2 UCs Enriched

| UC ID | UC Name | FIT041 Source | Enrichment Type |
|-------|---------|---------------|-----------------|
| UC4 | Alert-Triggered Execution | UC1 (Service Restart) | Actors, pre-conditions, flow |
| UC5 | Scheduled/Recurring | UC3 (Maintenance) | Actors, pre-conditions |
| UC8 | Multi-Level Approval | UC2 (Decommission) | Actors, pre-conditions |
| UC10 | ITSM Ticket Creation | UC1, UC2 | Flow (ticket create/close) |
| UC13 | Runbook Execution | UC1, UC2, UC3 | Flow (specific steps) |
| UC14 | Auto-Remediation | UC1 (Service Restart) | Success criteria |

### 2.3 UCs Unchanged

| UC ID | UC Name | Reason |
|-------|---------|--------|
| UC1 | Workflow Creation | Not in FIT041 scope |
| UC2 | Version Control | Not in FIT041 scope |
| UC3 | Deployment | Not in FIT041 scope |
| UC6 | Manual Trigger | Generic (no FIT041-specific) |
| UC7 | Single-Level Approval | Generic (no FIT041-specific) |
| UC9 | Batch Approval | Not in FIT041 scope |
| UC11 | Bidirectional Sync | Support UC (no FIT041-specific) |
| UC12 | ITSM Ticket Closure | Support UC (no FIT041-specific) |
| UC15 | Rollback | Not in FIT041 scope |
| UC16 | Time Escalation | Support UC (no FIT041-specific) |
| UC17 | Severity Routing | Support UC (no FIT041-specific) |

---

## 3. Use Case Taxonomy

### 3.1 Classification

| UC ID | Use Case Name | Category | Priority | Latency Target | FIT041 Enriched |
|-------|---------------|----------|----------|----------------|-----------------|
| UC1 | Workflow Creation & Configuration | Creation & Management | P1 | < 100ms | — |
| UC2 | Workflow Version Control & Change Management | Creation & Management | P2 | < 200ms | — |
| UC3 | Workflow Deployment & Activation | Creation & Management | P2 | < 30s | — |
| UC4 | Alert-Triggered Workflow Execution | Execution & Automation | P1 | < 5min | ✅ UC1 |
| UC5 | Scheduled/Recurring Workflow Execution | Execution & Automation | P2 | < 1min | ✅ UC3 |
| UC6 | Manual Workflow Trigger | Execution & Automation | P1 | < 100ms | — |
| UC7 | Single-Level Approval | Approval & Governance | P1 | < 1min | — |
| UC8 | Multi-Level Approval Chains | Approval & Governance | P1 | < 5min | ✅ UC2 |
| UC9 | Batch Approval | Approval & Governance | P2 | < 2min | — |
| UC10 | ITSM Ticket Creation | ITSM Integration | P1 | < 30s | ✅ UC1, UC2 |
| UC11 | ITSM Bidirectional Sync | ITSM Integration | P1 | < 5min | — |
| UC12 | ITSM Ticket Closure | ITSM Integration | P1 | < 1min | — |
| UC13 | Runbook Execution | Runbook & Remediation | P1 | < 5min | ✅ UC1, UC2, UC3 |
| UC14 | Auto-Remediation with Safety Guards | Runbook & Remediation | P1 | < 2min | ✅ UC1 |
| UC15 | Rollback Execution | Runbook & Remediation | P1 | < 5min | — |
| UC16 | Time-Based Escalation | Escalation & Notification | P1 | < 30min | — |
| UC17 | Severity-Based Routing | Escalation & Notification | P1 | < 5min | — |

### 3.2 Priority Distribution

| Priority | Count | Examples |
|----------|-------|----------|
| P1 Critical | 10 | Workflow CRUD, Alert Trigger, Approval, ITSM, Runbook, Escalation |
| P2 High | 7 | Version Control, Deployment, Scheduled, Batch Approval |
| P3 Medium | 0 | — |
| P4 Supporting | 0 | — |

### 3.3 Workflow Types Mapping

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

## 4. Workflow Creation & Management Use Cases (UC1–UC3)

### 4.1 UC1 — Workflow Creation & Configuration

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

### 4.2 UC2 — Workflow Version Control & Change Management

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

### 4.3 UC3 — Workflow Deployment & Activation

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

## 5. Execution & Automation Use Cases (UC4–UC6)

### 5.1 UC4 — Alert-Triggered Workflow Execution

**Objective:** Workflow otomatis dieksekusi saat alert dari SIEM/Analytics memenuhi threshold.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min (end-to-end) |
| **Throughput** | 50 alerts/min |
| **Actors** | System (automated) |

> **FIT041 Traceability:** UC4 enriched dari FIT041 UC1 (Automated Incident Remediation — Service Restart).
> FIT041 actors: Monitoring System, Analytics & AI Engine, Hypervisor/Server OS.
> FIT041 pre-conditions: Server accessible, approved remediation workflow exists.
> FIT041 flow: Trigger → Verify (Analytics check) → Attempt (systemctl restart) → Check (60s wait) → Conditional (fail: open ticket / success: close ticket).

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

#### FIT041 Operational Flow (Service Restart)

```
1. Trigger: Monitoring System sends alert to Workflow Automation Engine
2. Verification: Engine queries Analytics & AI Engine to confirm not larger outage
3. Action (Attempt 1): Execute systemctl restart service-x
4. Check: Wait 60 seconds, query Monitoring System for "Up" status
5. Conditional Fail: If still down → open high-priority ticket → log failure → stop
6. Conditional Success: If up → mark incident ticket as "Resolved by Automation"
```

#### API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/v1/webhook/alert` | API Key | Receive alert trigger |
| GET | `/api/v1/workflow/execution/{id}` | Operator+ | Check execution status |
| GET | `/api/v1/workflow/execution/{id}/logs` | Operator+ | Get execution logs |

---

### 5.2 UC5 — Scheduled/Recurring Workflow Execution

**Objective:** Workflow dijalankan sesuai schedule (cron-based).

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | < 1min (from schedule) |
| **Throughput** | 10 schedules |
| **Actors** | System (automated) |

> **FIT041 Traceability:** UC5 enriched dari FIT041 UC3 (Planned Maintenance Shutdown Coordination).
> FIT041 actors: DCIM Operator.
> FIT041 pre-conditions: All necessary maintenance approvals secured, CMDB has accurate dependency mapping.
> FIT041 context: Maintenance window scheduling with dependency-aware sequencing.

#### Schedule Types

| Type | Example | Use Case |
|------|---------|----------|
| One-time | `2026-06-25T02:00:00` | Maintenance window |
| Daily | `0 2 * * *` | Daily backup verification |
| Weekly | `0 2 * * 0` | Weekly compliance check |
| Monthly | `0 2 1 * *` | Monthly capacity report |

#### FIT041 Operational Context (Maintenance Shutdown)

```
1. Trigger: DCIM Operator manually initiates "Planned Maintenance Shutdown" workflow
2. CMDB Query: Workflow queries CMDB for inverse dependency sequence
3. Shutdown Sequence: API calls to Virtualization Platform (VMs → DB → Storage)
4. Power Off: Command PDU to cut power to non-essential equipment
5. Restart Sequence: Reverse sequence after maintenance window
6. Notification: Send "Maintenance Complete" to distribution list
```

---

### 5.3 UC6 — Manual Workflow Trigger

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

## 6. Approval & Governance Use Cases (UC7–UC9)

### 6.1 UC7 — Single-Level Approval

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

### 6.2 UC8 — Multi-Level Approval Chains

**Objective:** Workflow dengan risiko tinggi memerlukan approval bertingkat.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min (per level) |
| **Throughput** | 10 approvals/min |
| **Actors** | Team Lead, Change Manager, Director |

> **FIT041 Traceability:** UC8 enriched dari FIT041 UC2 (Server Decommissioning Workflow).
> FIT041 actors: Asset Manager, Server Provisioning System.
> FIT041 pre-conditions: All hosted workloads successfully migrated, server powered down.
> FIT041 context: Decommissioning requires multi-level approval for financial, security, and physical removal.

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

### 6.3 UC9 — Batch Approval

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

## 7. ITSM Integration Use Cases (UC10–UC12)

### 7.1 UC10 — ITSM Ticket Creation

**Objective:** Auto-create ticket di ServiceNow/Jira saat workflow dibuat.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 30s |
| **Throughput** | 20 tickets/min |
| **Actors** | System (automated) |

> **FIT041 Traceability:** UC10 enriched dari FIT041 UC1 (Service Restart) dan UC2 (Decommission).
> FIT041 UC1 flow: Open high-priority ticket on failure, mark "Resolved by Automation" on success.
> FIT041 UC2 flow: Create final ticket for DCIM Operator to physically un-rack and dispose hardware.

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

### 7.2 UC11 — ITSM Bidirectional Sync

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

### 7.3 UC12 — ITSM Ticket Closure

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

## 8. Runbook & Remediation Use Cases (UC13–UC15)

### 8.1 UC13 — Runbook Execution

**Objective:** Eksekusi prosedur predefined dengan step-by-step tracking.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 5min per runbook |
| **Throughput** | 10 runbooks/min |
| **Actors** | System (automated), Operator (manual steps) |

> **FIT041 Traceability:** UC13 enriched dari FIT041 UC1 (Service Restart), UC2 (Decommission), UC3 (Maintenance).
> FIT041 UC1 flow: systemctl restart service-x → wait 60s → check status → conditional
> FIT041 UC2 flow: network cleanup → security update → CMDB update → financial notification → physical removal ticket
> FIT041 UC3 flow: CMDB query → shutdown sequence → power off PDU → restart sequence → notification

#### Runbook Step Types

| Type | Description | Timeout | On Failure |
|------|-------------|---------|------------|
| Automated | Script execution | Configurable | abort/rollback/alert_only |
| Notification | Send notification | Immediate | — |
| Manual | Human verification | Configurable | escalate |
| Wait | Delay execution | Fixed duration | — |

#### FIT041 Operational Flow (Service Restart Runbook)

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
```

#### FIT041 Operational Flow (Decommission Runbook)

```yaml
runbook:
  id: RB-002
  name: "Server Decommissioning"
  steps:
    - id: step_1
      name: "Network Cleanup"
      type: "automated"
      script: "scripts/remove_ip_dns.py"
    - id: step_2
      name: "Security Update"
      type: "automated"
      script: "scripts/remove_firewall_policy.py"
    - id: step_3
      name: "CMDB Update"
      type: "automated"
      script: "scripts/update_asset_status.py"
      parameters:
        status: "Decommissioned"
    - id: step_4
      name: "Financial Notification"
      type: "automated"
      script: "scripts/send_financial_report.py"
    - id: step_5
      name: "Physical Removal Ticket"
      type: "notification"
      channel: "itsm"
      message: "Create ticket for DCIM Operator to un-rack hardware"
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

### 8.2 UC14 — Auto-Remediation with Safety Guards

**Objective:** Otomatis remediasi alert dengan safety checks.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 2min |
| **Throughput** | 20 remediations/min |
| **Actors** | System (automated) |

> **FIT041 Traceability:** UC14 enriched dari FIT041 UC1 (Service Restart).
> FIT041 success criteria: Service successfully restarted and confirmed operational within 5 minutes of alert trigger, incident ticket automatically closed.
> FIT041 conditional: If service still down after attempt → open high-priority ticket → log failure → stop.

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

### 8.3 UC15 — Rollback Execution

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

## 9. Escalation & Notification Use Cases (UC16–UC17)

### 9.1 UC16 — Time-Based Escalation

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

### 9.2 UC17 — Severity-Based Routing

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

## 10. Source System → Use Case Matrix

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

## 11. Data Type → Use Case Mapping

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

## 12. API Requirements per Use Case

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

## 13. SLA & Latency Requirements

### 13.1 Tiered Latency

| Tier | Latency | Use Cases | SLA |
|------|---------|-----------|-----|
| Tier 1 (Real-time) | < 100ms | UC1, UC6, UC7 | 99.9% |
| Tier 2 (Near-RT) | < 5min | UC4, UC8, UC10, UC11, UC12, UC13, UC14, UC15 | 99.5% |
| Tier 3 (Scheduled) | < 30min | UC3, UC5, UC16 | 99.0% |
| Tier 4 (Batch) | < 2h | UC9 | 95.0% |

### 13.2 Throughput Targets

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

## 14. Data Quality Requirements per Use Case

| UC | Dimension | Requirement |
|----|-----------|-------------|
| UC1 | Completeness | `name`, `trigger_type`, `actions` wajib |
| UC1 | Accuracy | `workflow_id` unique |
| UC1 | Consistency | Status valid sesuai state machine |
| UC4 | Timeliness | Alert → workflow < 5min |
| UC4 | Accuracy | Alert payload valid |
| UC4 | FIT041 Success | Service restarted within 5min, ticket auto-closed |
| UC7 | Completeness | `approver_id`, `decision`, `reason` wajib |
| UC7 | Auditability | Semua approval tercatat dengan timestamp |
| UC10 | Completeness | Ticket mapping wajib (`workflow_id` ↔ `ticket_id`) |
| UC10 | Consistency | Priority mapping sesuai severity |
| UC13 | Completeness | Semua runbook steps ter-log |
| UC13 | Accuracy | Step execution status valid |
| UC13 | FIT041 Flow | Network cleanup, security update, CMDB update |
| UC14 | Safety | Blast radius check wajib sebelum execution |
| UC14 | Auditability | Semua remediation attempts tercatat |
| UC14 | FIT041 Success | Service restarted within 5min, ticket auto-closed |
| UC16 | Timeliness | Escalation check setiap 30 menit |

---

## 15. Downstream Consumer Mapping

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

## 16. Acceptance Criteria

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
| 5 | **FIT041:** Service restarted within 5min | E2E test (FIT041 UC1) |
| 6 | **FIT041:** Ticket auto-closed on success | E2E test (FIT041 UC1) |

### UC5 — Scheduled/Recurring Workflow
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Scheduled workflow runs on time | Schedule test |
| 2 | **FIT041:** Correct shutdown/restart sequence | E2E test (FIT041 UC3) |
| 3 | **FIT041:** 0 unplanned service disruptions | E2E test (FIT041 UC3) |

### UC7/UC8 — Approval Workflows
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Single-level approval works | E2E test |
| 2 | Multi-level approval chain works | E2E test |
| 3 | Approval timeout → escalation | Timeout test |
| 4 | Rejection → workflow cancelled/reworked | E2E test |
| 5 | Batch approval works | E2E test |
| 6 | Approval audit trail complete | Audit log |
| 7 | **FIT041:** Decommission approval chain | E2E test (FIT041 UC2) |

### UC10/UC11/UC12 — ITSM Integration
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | ServiceNow ticket created | E2E test |
| 2 | Jira ticket created | E2E test |
| 3 | Bidirectional sync works | Sync test |
| 4 | Ticket closed on workflow completion | E2E test |
| 5 | Priority mapping correct | Mapping test |
| 6 | Sync error handling | Error test |
| 7 | **FIT041:** High-priority ticket on failure | E2E test (FIT041 UC1) |
| 8 | **FIT041:** "Resolved by Automation" on success | E2E test (FIT041 UC1) |

### UC13 — Runbook Execution
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Runbook executed successfully | E2E test |
| 2 | On_failure routing works | Failure test |
| 3 | Manual step + timeout works | Timeout test |
| 4 | Rollback executed on failure | Rollback test |
| 5 | Execution logs complete | Log verification |
| 6 | **FIT041:** systemctl restart works | E2E test (FIT041 UC1) |
| 7 | **FIT041:** Network cleanup works | E2E test (FIT041 UC2) |
| 8 | **FIT041:** CMDB dependency query works | E2E test (FIT041 UC3) |

### UC14 — Auto-Remediation
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Blast radius check works | Safety test |
| 2 | Rate limit enforced | Rate limit test |
| 3 | Time window check works | Window test |
| 4 | Dry run shows preview | Dry run test |
| 5 | Approval required for critical | Approval test |
| 6 | **FIT041:** Service restarted within 5min | E2E test (FIT041 UC1) |
| 7 | **FIT041:** Ticket auto-closed on success | E2E test (FIT041 UC1) |

### UC16/UC17 — Escalation & Routing
| # | Criterion | Evidence |
|---|-----------|----------|
| 1 | Time-based escalation works | Timeout test |
| 2 | Severity routing correct | Routing test |
| 3 | Notification channels work | Notification test |
| 4 | Escalation audit trail complete | Audit log |

---

## 17. Traceability Matrix

| UC | Name | Source Block | Related Block | FIT041 Source | Priority |
|----|------|--------------|---------------|---------------|----------|
| UC1 | Workflow Creation | Block 8 §2 | Block 2 (DI&I) | — | P1 |
| UC2 | Version Control | Block 8 §2 | — | — | P2 |
| UC3 | Deployment | Block 8 §2 | — | — | P2 |
| UC4 | Alert Trigger | Block 8 §9 | Block 6 (SIEM), Block 7 (Analytics) | UC1 (Service Restart) | P1 |
| UC5 | Scheduled | Block 8 §9 | — | UC3 (Maintenance) | P2 |
| UC6 | Manual Trigger | Block 8 §9 | — | — | P1 |
| UC7 | Single Approval | Block 8 §4 | Block 4 (CMDB) | — | P1 |
| UC8 | Multi Approval | Block 8 §4 | Block 4 (CMDB) | UC2 (Decommission) | P1 |
| UC9 | Batch Approval | Block 8 §4 | — | — | P2 |
| UC10 | Ticket Create | Block 8 §3 | Block 6 (SIEM) | UC1, UC2 | P1 |
| UC11 | Bidirectional | Block 8 §3 | Block 6 (SIEM) | — | P1 |
| UC12 | Ticket Close | Block 8 §3 | — | — | P1 |
| UC13 | Runbook Exec | Block 8 §5 | Block 6 (SIEM) | UC1, UC2, UC3 | P1 |
| UC14 | Auto-Remediation | Block 8 §6 | Block 4 (CMDB), Block 7 (Analytics) | UC1 (Service Restart) | P1 |
| UC15 | Rollback | Block 8 §5 | — | — | P1 |
| UC16 | Time Escalation | Block 8 §7 | — | — | P1 |
| UC17 | Severity Routing | Block 8 §7 | — | — | P1 |

### FIT041 Absorption Summary

| FIT041 UC | FIT041 Field | Absorbed Into | Status |
|-----------|-------------|---------------|--------|
| UC1 (Service Restart) | Actors | UC4 | ✅ Absorbed |
| UC1 (Service Restart) | Pre-conditions | UC4 | ✅ Absorbed |
| UC1 (Service Restart) | Flow | UC4, UC13, UC14 | ✅ Absorbed |
| UC1 (Service Restart) | Success Criteria | UC14, Acceptance | ✅ Absorbed |
| UC2 (Decommission) | Actors | UC8 | ✅ Absorbed |
| UC2 (Decommission) | Pre-conditions | UC8 | ✅ Absorbed |
| UC2 (Decommission) | Flow | UC13 | ✅ Absorbed |
| UC3 (Maintenance) | Actors | UC5 | ✅ Absorbed |
| UC3 (Maintenance) | Pre-conditions | UC5 | ✅ Absorbed |
| UC3 (Maintenance) | Flow | UC13 | ✅ Absorbed |

---

## 18. Appendix: FIT041 Requirements Checklist

### FIT041 Requirements (6 items)

| # | FIT041 Requirement | Status | DCIM-Wiki Equivalent |
|---|-------------------|--------|----------------------|
| 1 | Built-in connectors for common IT systems (CMDB, ServiceNow, JIRA, vCenter, SSH) | To be determined | UC10 (ITSM), UC13 (Runbook scripts) |
| 2 | Visual designer interface for building and testing workflows | To be determined | UC1 (Workflow Creation), n8n/Temporal |
| 3 | Must be able to execute 1,000 parallel remediation workflows simultaneously | To be determined | §10 (Performance & Sizing) |
| 4 | Credential vault integration for securely storing system access keys | To be determined | §11 (Security - Vault) |
| 5 | Comprehensive logging of every step, including input, output, and execution time | To be determined | UC13 (Runbook logs) |
| 6 | High availability cluster configuration | To be determined | §10 (Active-Passive) |

### Requirements Mapping

| FIT041 Requirement | DCIM-Wiki UC | Alignment |
|-------------------|--------------|-----------|
| Connectors (CMDB, ServiceNow, JIRA, vCenter, SSH) | UC10, UC13 | ⚠️ Partial (specific connectors not listed) |
| Visual designer | UC1, n8n/Temporal | ✅ Match |
| 1,000 parallel workflows | §10 Performance | ⚠️ Partial (metric not specified) |
| Credential vault | §11 Security | ✅ Match |
| Comprehensive logging | UC13, UC14 | ✅ Match |
| HA cluster | §10 Active-Passive | ⚠️ Partial (generic vs specific) |

---

## References

- [[IF-Use_Case_Analysis_Workflow_Automation-FIT041-20260121]] — FIT041 Use Case Analysis document (uploaded)
- [[fit041-workflow-automation-use-case-komparasi]] — FIT041 UC Analysis comparison
- [[fit041-workflow-automation-komparasi]] — FIT041 Technical Requirements comparison
- [[block8-workflow-automation]] — Reference design spec
- [[workflow-automation]] — Entity page
- [[workflow-automation-patterns]] — Concept page
- [[workflow-state-machine]] — State machine concept
- [[workflow-engine-comparison]] — Engine comparison
- [[dcim-core-platform]] — Parent project
- [[analytics-ai-engine]] — Alert triggers
- [[siem-soc]] — Security incident workflows
- [[cmdb]] — Impact assessment

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-25
> **Version:** 2.0 (merged from FIT041 + DCIM-Wiki)
> **Purpose:** Use Case Analysis final untuk Workflow Automation
> **Method:** MCP Sequential Thinking (4 thoughts) + MCP Context7 (n8n docs) + dcim-comparison skill
> **Result:** 17 Use Cases across 6 categories, 6 UCs enriched with FIT041 context
> **Key Finding:** FIT041 operational scenarios (3) absorbed into DCIM-Wiki technical UCs (17). 6 UCs enriched with actors, pre-conditions, flows, success criteria. 28 acceptance criteria (3 added from FIT041).
> **Phase 2 Progress:** B5 ✅ → B6 ✅ → B7 ✅ → B8 ✅ → B9 ⬜
