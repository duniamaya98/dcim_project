---
title: Workflow Automation SLA & Prioritization Framework
created: 2026-06-25
updated: 2026-06-25
type: framework
tags: [sla, prioritization, workflow, automation, itsm, escalation, remediation]
sources:
  - dcim-wiki/concepts/priority-severity-model.md
  - dcim-wiki/concepts/cmdb-sla-prioritization-framework.md
  - dcim-wiki/technical-requirements/workflow-automation-use-case-analysis-final-v2.md
  - dcim-wiki/reference-designs/block8-workflow-automation.md
confidence: high
---

# Workflow Automation SLA & Prioritization Framework

Framework terpadu untuk SLA, prioritas, dan kualitas data di Workflow Automation layer (Block 8).

---

## 1. Priority Model (Workflow / Task / Approval)

| Priority | Meaning | Operational Effect | Default Latency |
|----------|---------|-------------------|-----------------|
| **P1 Critical** | Workflow mempengaruhi service kritis (production outage, security incident) | Real-time execution, immediate escalation, auto-remediation allowed | < 30 detik |
| **P2 High** | Workflow mempengaruhi service penting (degradation, capacity threshold) | Fast execution, time-bound approval, escalation aktif | < 5 menit |
| **P3 Medium** | Workflow untuk planning, maintenance, compliance | Normal queue, batch execution acceptable | < 1 jam |
| **P4 Supporting** | Workflow historis, reference, dokumentasi | Async, background, scheduled | > 1 jam |

---

## 2. Workflow Type Criticality Mapping

| Workflow Type | Default Priority | SLA Tier | Approval Required | Auto-Remediation | ITSM |
|---------------|----------------:|----------|-------------------|------------------|------|
| **Incident Response** | **P1** | Tier 1 | Optional (severity-dependent) | Conditional | Auto-create |
| **Change Management** | **P2** | Tier 2 | Multi-level | No | Auto-create |
| **Auto-Remediation** | **P1** | Tier 1 | Safety guard | Yes | Log only |
| **Provisioning** | P2 | Tier 2 | Single-level | No | Auto-create |
| **Decommission** | P3 | Tier 3 | Multi-level | No | Auto-create |
| **Compliance Remediation** | **P1** | Tier 1 | Required | No | Auto-create |
| **Maintenance Window** | P3 | Tier 3 | Required | No | Auto-create |

### Priority Distribution by Type

```
P1 Critical: 3 types (Incident Response, Auto-Remediation, Compliance Remediation)
P2 High:     2 types (Change Management, Provisioning)
P3 Medium:   2 types (Decommission, Maintenance Window)
P4 Supporting: 0 types
```

---

## 3. SLA Tiers (End-to-End Latency)

| Tier | Latency | Use Cases | Processing Mode |
|------|---------|-----------|-----------------|
| **Tier 1 (Real-time)** | < 30 detik | UC4 Alert Trigger, UC14 Auto-Remediation, UC16 Time Escalation | Direct execution, synchronous, no approval gate |
| **Tier 2 (Near-RT)** | < 5 menit | UC7 Single-Level, UC8 Multi-Level (simplified), UC10 Ticket Create, UC17 Severity Routing | Fast-track approval, notification-first |
| **Tier 3 (Standard)** | < 1 jam | UC1 Workflow CRUD, UC2 Version Control, UC5 Scheduled, UC9 Batch Approval, UC11 Bidirectional, UC12 Ticket Close | Normal queue, approval pipeline |
| **Tier 4 (Batch)** | > 1 jam | UC3 Deployment, UC6 Manual Trigger, UC13 Runbook (complex), UC15 Rollback | Scheduled execution, batch processing |

### Tier Definitions

- **Tier 1**: Trigger langsung eksekusi. Tidak ada approval gate kecuali safety guard. Notifikasi real-time ke operator + manager.
- **Tier 2**: Fast-track approval (1 level, timeout 15 menit). Jika timeout → auto-escalate ke L2.
- **Tier 3**: Full approval pipeline. Timeout sesuai approval chain config. Retry enabled, DLQ untuk failures.
- **Tier 4**: Batch execution. Jadwal tetap (misal 02:00 WIB). Idempotent, retry enabled, DLQ untuk failures.

---

## 4. Priority Mapping per Use Case

| Use Case | Priority | SLA Tier | Completeness | Timeliness | Data Quality |
|----------|----------|----------|-------------|------------|--------------|
| UC1 Workflow Creation | P2 | Tier 3 (< 1 jam) | ≥ 95% | Near-RT | Schema + business rules |
| UC2 Version Control | P3 | Tier 3 (< 1 jam) | 100% | Near-RT | Audit trail + version chain |
| UC3 Deployment | P3 | Tier 4 (batch) | 99% | Scheduled | Rollback capability |
| UC4 Alert-Triggered Execution | **P1** | Tier 1 (< 30 detik) | ≥ 99% | Real-time | Source alert accurate |
| UC5 Scheduled/Recurring | P3 | Tier 3 (cron) | 99% | Scheduled | Schedule accuracy 100% |
| UC6 Manual Trigger | P4 | Tier 4 (batch) | 100% | On-demand | Input validation |
| UC7 Single-Level Approval | P2 | Tier 2 (< 5 menit) | ≥ 95% | Near-RT | Approver assignment valid |
| UC8 Multi-Level Approval | P2 | Tier 2 (< 30 menit) | 100% | Near-RT | Chain integrity |
| UC9 Batch Approval | P3 | Tier 3 (< 1 jam) | 100% | Batch | Batch consistency |
| UC10 ITSM Ticket Creation | **P1** | Tier 1 (< 30 detik) | ≥ 99% | Real-time | Mapping accurate |
| UC11 ITSM Bidirectional Sync | **P1** | Tier 1 (< 1 menit) | ≥ 99% | Real-time | Status consistency |
| UC12 ITSM Ticket Closure | P2 | Tier 2 (< 5 menit) | 100% | Near-RT | Closure rules satisfied |
| UC13 Runbook Execution | **P1** | Tier 2 (< 5 menit) | ≥ 99% | Near-RT | Step-by-step audit |
| UC14 Auto-Remediation | **P1** | Tier 1 (< 2 menit) | ≥ 99% | Real-time | Safety guard pass |
| UC15 Rollback | P2 | Tier 3 (< 1 jam) | 100% | Near-RT | State consistency |
| UC16 Time Escalation | **P1** | Tier 1 (< 30 detik) | 100% | Real-time | Timer accuracy |
| UC17 Severity Routing | **P1** | Tier 1 (< 10 detik) | 100% | Real-time | Routing rules valid |

### Priority Distribution

| Priority | Count | Use Cases |
|----------|-------|-----------|
| **P1 Critical** | 8 | UC4, UC10, UC11, UC13, UC14, UC16, UC17 |
| **P2 High** | 4 | UC1, UC7, UC8, UC12, UC15 |
| **P3 Medium** | 4 | UC2, UC3, UC5, UC9 |
| **P4 Supporting** | 1 | UC6 |

---

## 5. Auto-Assignment Logic

### 5.1 Workflow Priority Assignment

```yaml
# workflow-priority-rules.yaml
rules:
  - name: security_incident
    condition:
      workflow_type: ["incident_response"]
      source: ["siem", "wazuh"]
      severity: ["critical", "high"]
    action:
      set_priority: "P1"
      set_escalation: "immediate"
      set_approval: "safety_guard_only"
      set_engine: "temporal"

  - name: auto_remediation
    condition:
      workflow_type: ["auto_remediation"]
      alert_severity: ["critical", "high"]
    action:
      set_priority: "P1"
      set_escalation: "immediate"
      set_approval: "safety_guard"
      set_engine: "temporal"

  - name: compliance_violation
    condition:
      workflow_type: ["compliance_remediation"]
      cis_benchmark: true
      severity: ["critical", "high"]
    action:
      set_priority: "P1"
      set_escalation: "30min"
      set_approval: "required"
      set_engine: "temporal"

  - name: change_management
    condition:
      workflow_type: ["change_management"]
      risk: ["medium", "high"]
    action:
      set_priority: "P2"
      set_escalation: "2h"
      set_approval: "multi_level"
      set_engine: "n8n"

  - name: provisioning
    condition:
      workflow_type: ["provisioning"]
    action:
      set_priority: "P2"
      set_escalation: "4h"
      set_approval: "single_level"
      set_engine: "n8n"

  - name: maintenance
    condition:
      workflow_type: ["maintenance_window"]
    action:
      set_priority: "P3"
      set_escalation: "next_business_day"
      set_approval: "required"
      set_engine: "n8n"
```

### 5.2 Escalation Priority Assignment

```python
def _assign_escalation_priority(self, workflow: dict) -> str:
    """Assign escalation priority based on severity + elapsed time."""
    severity = workflow.get("severity", "medium")
    elapsed_minutes = (datetime.utcnow() - workflow["created_at"]).total_seconds() / 60

    # P1: Immediate escalation for critical
    if severity == "critical" and elapsed_minutes > 5:
        return "P1"

    # P2: Fast escalation for high severity
    if severity == "high" and elapsed_minutes > 30:
        return "P2"

    # P3: Standard escalation
    if severity == "medium" and elapsed_minutes > 120:
        return "P3"

    # P4: No escalation needed
    return "P4"
```

### 5.3 Priority Override

- Source system dapat override via field `metadata.priority`
- SIEM/Analytics mengirim priority dari severity scoring
- Manual override oleh admin (role: `workflow.admin`) dengan audit trail
- Override P1 membutuhkan justification wajib

---

## 6. Impact Scoring

Impact score (0–10) digunakan untuk triage dan eskalasi:

```python
def _calculate_workflow_impact(self, workflow: dict) -> float:
    """Calculate workflow impact score for prioritization."""
    base = 5.0

    # Workflow type adjustment
    type_adj = {
        "incident_response": 4,
        "auto_remediation": 4,
        "compliance_remediation": 3,
        "change_management": 2,
        "provisioning": 1,
        "decommission": 1,
        "maintenance_window": 0,
    }
    base += type_adj.get(workflow.get("workflow_type", ""), 0)

    # Affected CI count adjustment
    affected_cis = workflow.get("affected_cis", 0)
    if affected_cis > 10:
        base += 2
    elif affected_cis > 5:
        base += 1

    # Severity adjustment
    severity = workflow.get("severity", "medium")
    severity_adj = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    base += severity_adj.get(severity, 0)

    # Time-sensitive adjustment
    if workflow.get("time_sensitive", False):
        base += 1

    return max(0, min(10, base))
```

### Impact Score Thresholds

| Score | Action |
|-------|--------|
| 8–10 | Immediate execution, P1 ticket, real-time notification, no approval gate |
| 5–7 | Fast-track execution, P2 ticket, 15-min approval timeout |
| 2–4 | Normal queue, P3 ticket, standard approval pipeline |
| 0–1 | Low priority, background, batch processing |

---

## 7. Incident Severity (untuk Escalation)

| Severity | Meaning | Default Response | Trigger |
|----------|---------|-----------------|---------|
| **S1 Critical** | Workflow engine total failure / P1 workflow stuck | Immediate triage & escalation, war room | Engine down / state machine failure |
| **S2 High** | Workflow degraded / approval SLA breach | Fast owner assignment | API latency > 5s / approval pending > 30 min |
| **S3 Medium** | ITSM sync lag / notification delay | Planned remediation | Sync lag > 5 min / notification failed |
| **S4 Low** | Ad-hoc query / minor workflow issue | Normal queue | Non-urgent request |

---

## 8. Escalation Matrix

### 8.1 Time-Based Escalation

| Severity | Level 1 (Initial) | Level 2 (+15 min) | Level 3 (+1 jam) | Level 4 (+4 jam) |
|----------|-------------------|--------------------|-------------------|-------------------|
| **Critical** | On-call Engineer | Team Lead | Manager | Director |
| **High** | On-call Engineer | Team Lead | Manager | — |
| **Medium** | Team Lead | Manager | — | — |
| **Low** | Team Lead | — | — | — |

### 8.2 Escalation Actions per Level

| Level | Action | Notification Channel | Auto-Action |
|-------|--------|---------------------|-------------|
| L1 | Assign + Notify | Email + Slack | — |
| L2 | Re-assign + Urgent Notify | Email + Slack + SMS | — |
| L3 | Manager Override | All channels + PagerDuty | — |
| L4 | Director War Room | All channels + Phone call | Auto-remediation if configured |

---

## 9. Approval Chain SLA

| Chain Type | Level 1 Timeout | Level 2 Timeout | Level 3 Timeout | Max Total |
|------------|----------------|----------------|----------------|-----------|
| **Standard Change** | 4 jam | — | — | 4 jam |
| **Normal Change** | 4 jam | 24 jam | — | 28 jam |
| **Emergency Change** | 1 jam | 4 jam | — | 5 jam |
| **Critical Change** | 2 jam | 4 jam | 24 jam | 30 jam |

### Approval Breach Handling

| Breach | Auto Action | Escalation |
|--------|-------------|------------|
| L1 timeout | Route to escalation contact | Slack alert ke L2 |
| L2 timeout | Route to manager | PagerDuty alert |
| L3 timeout | Route to director | Phone call + war room |

---

## 10. Kafka Topic Priority (Workflow Events)

| Topic | Priority | Partition Key | Retention | Use Case |
|-------|----------|---------------|-----------|----------|
| `dcim.workflow.commands` | **P1** | workflow_id | 90 hari | State transition commands |
| `dcim.workflow.events` | **P1** | workflow_id | 90 hari | State change events |
| `dcim.workflow.approvals` | **P1** | workflow_id | 90 hari | Approval requests/results |
| `dcim.workflow.remediation` | **P1** | alert_id | 90 hari | Auto-remediation actions |
| `dcim.workflow.escalation` | **P1** | workflow_id | 90 hari | Escalation triggers |
| `dcim.workflow.tickets` | P2 | workflow_id | 30 hari | ITSM ticket sync |
| `dcim.workflow.audit` | P2 | workflow_id | 1 tahun | Audit trail |
| `dcim.workflow.dlq` | **P1** | event_id | 30 hari | Failed events |

---

## 11. Consumer SLA Matrix

| Consumer | Input Topics | Required SLA | Protocol | Notification |
|----------|-------------|-------------|----------|--------------|
| **NOC Dashboard** | `dcim.workflow.events` | Tier 1 (< 5 detik) | WebSocket | Real-time push |
| **SOC (SIEM/Wazuh)** | `dcim.workflow.commands` | Tier 1 (< 30 detik) | REST API | Immediate |
| **ITSM (ServiceNow/Jira)** | `dcim.workflow.tickets` | Tier 2 (< 1 menit) | REST API | Event-driven |
| **Analytics & AI** | `dcim.workflow.events` | Tier 3 (< 5 menit) | Direct read | Batch aggregation |
| **CMDB** | `dcim.workflow.events` | Tier 2 (< 1 menit) | REST API | Event-driven |
| **Dashboard** | `dcim.workflow.events` | Tier 2 (< 5 detik) | WebSocket | Real-time push |
| **Compliance** | `dcim.workflow.audit` | Tier 4 (async) | REST API | Daily report |
| **Email/Slack** | `dcim.workflow.escalation` | Tier 1 (< 30 detik) | Webhook | Immediate |

---

## 12. SLA Monitoring & Alerting

### 12.1 Per-Operation Latency SLA

| Operation | SLA Target | Alert Threshold |
|-----------|-----------|----------------|
| POST /workflow/create | p99 < 100ms | > 100ms |
| POST /workflow/{id}/transition | p99 < 50ms | > 50ms |
| POST /workflow/{id}/approve | p99 < 100ms | > 100ms |
| POST /workflow/{id}/reject | p99 < 100ms | > 100ms |
| POST /itsm/ticket/create | p99 < 30s | > 30s |
| POST /remediation/evaluate | p99 < 2min | > 2min |
| GET /workflow/pending-approvals | p99 < 200ms | > 200ms |
| Escalation check cycle | < 30s | > 30s |
| Notification delivery | < 10s | > 10s |

### 12.2 Availability SLA

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| Workflow State Machine | 99.9% | < 15 min | 0 (PostgreSQL WAL) |
| ITSM Integration | 99.5% | < 30 min | N/A (external) |
| Auto-Remediation | 99.9% | < 10 min | N/A (stateless) |
| Runbook Engine | 99.9% | < 15 min | 0 (state in PostgreSQL) |
| n8n | 99.5% | < 30 min | N/A (external) |
| Temporal | 99.9% | < 15 min | 0 (built-in persistence) |
| Notification Service | 99.5% | < 30 min | N/A (multi-channel fallback) |

### 12.3 Prometheus Alert Rules

```yaml
groups:
  - name: workflow_sla_alerts
    rules:
      - alert: WorkflowCreationLatencyHigh
        expr: histogram_quantile(0.99, rate(workflow_creation_latency_seconds_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Workflow creation p99 latency > 100ms"

      - alert: WorkflowTransitionLatencyHigh
        expr: histogram_quantile(0.99, rate(workflow_transition_latency_seconds_bucket[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Workflow transition p99 latency > 50ms"

      - alert: ITSMTicketCreationLatencyHigh
        expr: histogram_quantile(0.99, rate(itsm_ticket_creation_latency_seconds_bucket[5m])) > 30
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "ITSM ticket creation p99 latency > 30s"

      - alert: WorkflowApprovalSLABreach
        expr: workflow_approval_pending_duration_seconds > 1800
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Workflow approval pending > 30 minutes"

      - alert: AutoRemediationLatencyHigh
        expr: histogram_quantile(0.99, rate(remediation_execution_latency_seconds_bucket[5m])) > 120
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Auto-remediation execution p99 latency > 2 minutes"

      - alert: WorkflowDLQRateHigh
        expr: rate(workflow_dlq_total[5m]) > 0.01
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Workflow DLQ rate > 1%"

      - alert: EscalationRateHigh
        expr: rate(workflow_escalation_total[5m]) > 5
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Escalation rate > 5/min — possible systemic issue"

      - alert: WorkflowAvailabilityLow
        expr: (1 - rate(workflow_api_errors_total[5m]) / rate(workflow_api_requests_total[5m])) < 0.999
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Workflow API availability < 99.9%"

      - alert: NotificationDeliveryFailure
        expr: rate(notification_delivery_failures_total[5m]) > 0.05
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Notification delivery failure rate > 5%"
```

---

## 13. SLA Breach Handling

### 13.1 Breach Detection Flow

```
Metric Check → Threshold Breach → Alert Firing → Escalation
                                                    │
                                        ┌───────────┼───────────┐
                                        ▼           ▼           ▼
                                    S4: Log     S3: Auto    S2: Alert
                                    + Monitor   Escalate    Owner
                                                        │
                                                        ▼
                                                    S1: War Room
                                                    + Incident
```

### 13.2 Escalation Matrix per Tier

| SLA Tier | Breach → Auto Action | Breach → Escalation |
|----------|---------------------|---------------------|
| Tier 1 | Retry + DLQ + fallback execution | PagerDuty P1, on-call < 5 min |
| Tier 2 | Queue hold + alert | Slack alert, owner < 15 min |
| Tier 3 | Retry next cycle + DLQ | Dashboard flag, owner < 1 hour |
| Tier 4 | Retry in next batch | Email report, next business day |

### 13.3 SLA Breach → Ticket Routing

| Priority | Ticket Type | Assignment | Resolution SLA |
|----------|------------|------------|----------------|
| P1 | Incident | Workflow Admin → On-Call | 30 menit |
| P2 | Problem | Workflow Engineer | 4 jam |
| P3 | Service Request | Workflow Engineer | 1 hari kerja |
| P4 | Task | Scheduled | Sprint berikutnya |

---

## 14. Data Quality per Priority

| Priority | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| P1 | ≥ 99% | State machine valid, no orphan workflows | Real-time | Status enum valid | CHECK + audit trail |
| P2 | ≥ 98% | Approval chain intact, ITSM mapping valid | < 5 menit | Status in allowed values | Schema + business rules |
| P3 | ≥ 95% | Batch-valid, no duplicate runs | < 1 jam | Consistent format | Schema |
| P4 | ≥ 90% | Best-effort | > 1 jam | Async-valid | Basic format |

### 9 Data Quality Rules

| Rule | Dimension | Check | Target |
|------|-----------|-------|--------|
| DQ-01 | Uniqueness | workflow_id UNIQUE constraint | 100% |
| DQ-02 | State Integrity | Valid transition only (state machine) | 100% |
| DQ-03 | Referential Integrity | affected_ci_id exist in CMDB | 100% |
| DQ-04 | Approval Chain | Every P1/P2 workflow has approval record | 100% |
| DQ-05 | Audit Trail | Every state change logged with actor + timestamp | 100% |
| DQ-06 | Mandatory Fields | workflow_id, type, status, severity not null | 100% |
| DQ-07 | ITSM Sync | workflow ↔ ticket mapping consistent | > 99% |
| DQ-08 | Escalation Chain | Escalation levels follow severity matrix | 100% |
| DQ-09 | Idempotency | Duplicate trigger → single execution | 100% |

---

## 15. Notification Channel Priority

| Priority | Channels | Delivery SLA | Fallback |
|----------|----------|-------------|----------|
| **P1** | PagerDuty + SMS + Email + Slack + Teams | < 30 detik | Phone call |
| **P2** | Email + Slack + Teams | < 1 menit | SMS |
| **P3** | Email + Slack | < 5 menit | — |
| **P4** | Email | < 1 jam | — |

### Channel Reliability

| Channel | Availability | Latency (p95) | Rate Limit |
|---------|-------------|---------------|------------|
| Email | 99.9% | < 30 detik | 100/min |
| Slack | 99.9% | < 5 detik | 50/min |
| Teams | 99.5% | < 10 detik | 50/min |
| SMS | 99.5% | < 15 detik | 20/min |
| PagerDuty | 99.9% | < 5 detik | Unlimited |
| Webhook | 99.9% | < 5 detik | 100/min |

---

## 16. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total Active Workflows | ≥ 500 concurrent | PostgreSQL |
| Workflow Throughput | 100 workflows/min | Aggregate |
| State Transition Latency | p99 < 50ms | Prometheus |
| ITSM Ticket Creation | p99 < 30s | Prometheus |
| Approval Notification | p99 < 1min | Prometheus |
| Runbook Execution | < 5min per runbook | Prometheus |
| Auto-Remediation | < 2min per action | Prometheus |
| Escalation Check Cycle | < 30s | Prometheus |
| DLQ Rate | < 1% | Kafka |
| Notification Delivery | > 99% | Multi-channel |
| Approval SLA Compliance | > 95% | Within timeout |
| Rollback Success | > 99% | Successful rollbacks |

---

## 17. Monitoring Dashboard

### Workflow Health Metrics

| Metric | Source | Refresh |
|--------|--------|---------|
| Active Workflows by Status | PostgreSQL | Real-time |
| Active Workflows by Priority | PostgreSQL | Real-time |
| Workflow Throughput (min/hour/day) | PostgreSQL | Real-time |
| State Transition Latency (p50, p95, p99) | Prometheus | Real-time |
| Approval Pending Count | PostgreSQL | Real-time |
| Approval SLA Compliance | PostgreSQL | Real-time |
| Escalation Rate | Prometheus | Real-time |
| ITSM Sync Status | PostgreSQL | Real-time |
| Auto-Remediation Success Rate | PostgreSQL | Real-time |
| DLQ Count | Kafka | Real-time |
| Notification Delivery Rate | Multi-source | Real-time |
| Runbook Execution Duration | PostgreSQL | Real-time |
| Error Rate | Prometheus | Real-time |

---

## Related

- [[priority-severity-model]] — Global priority & severity model
- [[dii-sla-prioritization-framework]] — DI&I SLA framework
- [[cmdb-sla-prioritization-framework]] — CMDB SLA framework
- [[analytics-ai-sla-prioritization-framework]] — Analytics & AI SLA framework
- [[workflow-automation-use-case-analysis-final-v2]] — Workflow Automation use case analysis (17 UCs)
- [[block8-workflow-automation]] — Workflow Automation reference design spec
- [[workflow-state-machine]] — State machine implementation details
- [[incident-response-workflow]] — Incident response workflow procedures
