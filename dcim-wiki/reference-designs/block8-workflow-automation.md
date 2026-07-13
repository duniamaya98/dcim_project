---
title: "Block 8 — Workflow Automation: Reference Design Spec"
created: 2026-06-23
updated: 2026-06-23
type: reference-design
block: 8
phase: 2
status: generated
confidence: high
tags: [workflow, automation, itsm, approval, runbook, remediation, escalation, n8n, temporal]
wiki_pages:
  - workflow-automation
  - analytics-ai-engine
  - siem-soc
  - web-dashboard
  - cmdb
  - auto-remediation-runbook
  - workflow-engine-comparison
purpose: >
  Reference design spec untuk Block 8 Workflow Automation.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Block 8 — Workflow Automation: Reference Design Spec

> **Purpose:** Dokumen referensi lengkap untuk Workflow Automation — ticketing, approval, runbook, remediation, escalation.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi. Setiap gap = connection point.
> **Architecture Diagram:** `diagrams/block8-workflow-automation-architecture.html`
> **Depends on:** Block 2 (DI&I), Block 4 (CMDB)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Workflow State Machine](#2-workflow-state-machine)
3. [ITSM Ticketing Integration](#3-itsm-ticketing-integration)
4. [Multi-Level Approval Workflows](#4-multi-level-approval-workflows)
5. [Runbook Engine](#5-runbook-engine)
6. [Auto-Remediation](#6-auto-remediation)
7. [Escalation Rules](#7-escalation-rules)
8. [n8n/Temporal Integration](#8-n8ntemporal-integration)
9. [Workflow Types](#9-workflow-types)
10. [Performance & Sizing](#10-performance--sizing)
11. [Security](#11-security)
12. [Monitoring & Alerting](#12-monitoring--alerting)
13. [Acceptance Criteria](#13-acceptance-criteria)
14. [Gap Comparison Template](#14-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                  Workflow Automation                            │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Workflow State Machine                       │  │
│  │  Define • Execute • Track • Persist                       │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐  │
│  │              Automation Services                         │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ ITSM     │ │ Approval │ │ Runbook  │ │ Auto-    │   │  │
│  │  │ Ticketing│ │ Workflows│ │ Engine   │ │Remediation│   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  │  ┌──────────┐ ┌──────────┐                              │  │
│  │  │Escalation│ │ n8n/     │                              │  │
│  │  │ Rules    │ │ Temporal │                              │  │
│  │  └──────────┘ └──────────┘                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Notification Layer                          │  │
│  │  Email • SMS • Slack • Teams • Webhook • PagerDuty       │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                 │                │
         ▼                 ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │   CMDB   │    │   SIEM   │    │  Analytics   │
  │(impact)  │    │(incidents)│   │  (alerts)    │
  └──────────┘    └──────────┘    └──────────────┘
```

### 1.2 Data Flow

```
Triggers:
  1. Alert (Analytics/SIEM) → Workflow Engine → Create Workflow
  2. Manual (Dashboard) → API → Create Workflow
  3. Scheduled (Cron) → Create Recurring Workflow
  4. Event (DI&I) → Webhook → Create Workflow

Workflow Execution:
  1. State Machine processes workflow
  2. Assign approvers based on rules
  3. Execute runbook steps
  4. Notify stakeholders
  5. Escalate if needed
  6. Complete / Fail / Rollback
```

### 1.3 Core Responsibilities

| Responsibility | Description | SLA |
|---------------|-------------|-----|
| State Management | Define, execute, track workflows | 99.9% availability |
| ITSM Integration | Auto-create/sync tickets | < 30s ticket creation |
| Approval Management | Multi-level approval chains | < 1min notification |
| Runbook Execution | Execute predefined procedures | < 5min per runbook |
| Auto-Remediation | Automated fix with safety guards | < 2min execution |
| Escalation | Time-based escalation | SLA-driven |
| Orchestration | n8n/Temporal integration | Real-time |

---

## 2. Workflow State Machine

### 2.1 States

```
┌─────────┐    ┌──────────┐    ┌──────────────┐    ┌──────────┐
│ Pending │───→│ In       │───→│ Waiting      │───→│ Approved │
│         │    │ Progress │    │ Approval     │    │          │
└─────────┘    └──────────┘    └──────────────┘    └─────┬────┘
                                        │                  │
                                        ▼                  ▼
                                   ┌──────────┐    ┌──────────┐
                                   │ Rejected │    │ Executing│
                                   └──────────┘    └─────┬────┘
                                                         │
                                              ┌──────────┴──────────┐
                                              ▼                     ▼
                                        ┌──────────┐         ┌──────────┐
                                        │ Completed│         │ Failed   │
                                        └──────────┘         └─────┬────┘
                                                                   │
                                                                   ▼
                                                             ┌──────────┐
                                                             │Rollback  │
                                                             └──────────┘
```

### 2.2 State Definitions

| State | Description | Allowed Transitions |
|-------|-------------|---------------------|
| `pending` | Created, not started | → `in_progress`, → `cancelled` |
| `in_progress` | Being processed | → `waiting_approval`, → `executing`, → `failed` |
| `waiting_approval` | Awaiting approval | → `approved`, → `rejected` |
| `approved` | Approved, ready to execute | → `executing` |
| `rejected` | Approval denied | → `cancelled`, → `in_progress` (resubmit) |
| `executing` | Runbook/action running | → `completed`, → `failed` |
| `completed` | Successfully done | (terminal) |
| `failed` | Execution failed | → `rollback`, → `in_progress` (retry) |
| `rollback` | Rolling back changes | → `completed`, → `failed` |
| `cancelled` | Cancelled by user/system | (terminal) |

### 2.3 State Machine Implementation

```python
# workflow/state_machine.py

from enum import Enum
from typing import Dict, Set, Optional
from datetime import datetime

class WorkflowState(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLBACK = "rollback"
    CANCELLED = "cancelled"

class Transition(Enum):
    START = "start"
    REQUEST_APPROVAL = "request_approval"
    APPROVE = "approve"
    REJECT = "reject"
    BEGIN_EXECUTION = "begin_execution"
    COMPLETE = "complete"
    FAIL = "fail"
    ROLLBACK = "rollback"
    CANCEL = "cancel"

# Valid transitions
VALID_TRANSITIONS: Dict[WorkflowState, Dict[Transition, WorkflowState]] = {
    WorkflowState.PENDING: {
        Transition.START: WorkflowState.IN_PROGRESS,
        Transition.CANCEL: WorkflowState.CANCELLED,
    },
    WorkflowState.IN_PROGRESS: {
        Transition.REQUEST_APPROVAL: WorkflowState.WAITING_APPROVAL,
        Transition.BEGIN_EXECUTION: WorkflowState.EXECUTING,
        Transition.FAIL: WorkflowState.FAILED,
    },
    WorkflowState.WAITING_APPROVAL: {
        Transition.APPROVE: WorkflowState.APPROVED,
        Transition.REJECT: WorkflowState.REJECTED,
    },
    WorkflowState.APPROVED: {
        Transition.BEGIN_EXECUTION: WorkflowState.EXECUTING,
    },
    WorkflowState.REJECTED: {
        Transition.CANCEL: WorkflowState.CANCELLED,
        Transition.START: WorkflowState.IN_PROGRESS,  # resubmit
    },
    WorkflowState.EXECUTING: {
        Transition.COMPLETE: WorkflowState.COMPLETED,
        Transition.FAIL: WorkflowState.FAILED,
    },
    WorkflowState.FAILED: {
        Transition.ROLLBACK: WorkflowState.ROLLBACK,
        Transition.START: WorkflowState.IN_PROGRESS,  # retry
    },
    WorkflowState.ROLLBACK: {
        Transition.COMPLETE: WorkflowState.COMPLETED,
        Transition.FAIL: WorkflowState.FAILED,  # rollback also failed
    },
}

class WorkflowStateMachine:
    def __init__(self, db):
        self.db = db

    async def transition(self, workflow_id: str, action: Transition, actor: str, reason: str = "") -> dict:
        """Execute state transition with validation."""

        # Get current state
        workflow = await self.db.get_workflow(workflow_id)
        current_state = WorkflowState(workflow["status"])

        # Validate transition
        if current_state not in VALID_TRANSITIONS:
            raise ValueError(f"Cannot transition from terminal state: {current_state}")

        if action not in VALID_TRANSITIONS[current_state]:
            raise ValueError(f"Invalid transition: {current_state.value} → {action.value}")

        new_state = VALID_TRANSITIONS[current_state][action]

        # Record transition
        await self.db.record_transition(
            workflow_id=workflow_id,
            old_state=current_state.value,
            new_state=new_state.value,
            action=action.value,
            actor=actor,
            reason=reason,
            timestamp=datetime.utcnow()
        )

        # Update workflow
        await self.db.update_workflow_status(workflow_id, new_state.value)

        # Trigger side effects
        await self._on_transition(workflow_id, current_state, new_state, workflow)

        return {
            "workflow_id": workflow_id,
            "old_state": current_state.value,
            "new_state": new_state.value,
            "action": action.value,
            "actor": actor,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def _on_transition(self, workflow_id: str, old_state: WorkflowState, new_state: WorkflowState, workflow: dict):
        """Handle side effects on state transitions."""

        if new_state == WorkflowState.WAITING_APPROVAL:
            await self._notify_approvers(workflow_id, workflow)

        elif new_state == WorkflowState.EXECUTING:
            await self._start_execution(workflow_id, workflow)

        elif new_state == WorkflowState.COMPLETED:
            await self._on_complete(workflow_id, workflow)
            await self._notify_completion(workflow_id, workflow)

        elif new_state == WorkflowState.FAILED:
            await self._on_failure(workflow_id, workflow)
            await self._trigger_escalation(workflow_id, workflow)

        elif new_state == WorkflowState.ROLLBACK:
            await self._start_rollback(workflow_id, workflow)
```

---

## 3. ITSM Ticketing Integration

### 3.1 Integration Matrix

| System | Protocol | Auth | Sync Direction | Use Case |
|--------|----------|------|----------------|----------|
| ServiceNow | REST API | OAuth2 | Bidirectional | Incident, Change, Request |
| Jira | REST API | API Key | Bidirectional | Issue, Task, Epic |
| Custom ITSM | REST API | API Key | Outbound | Ticket creation |

### 3.2 Ticket Creation Flow

```
Alert/Incident Created
  → Determine ticket type (Incident/Change/Request)
  → Map severity to ITSM priority
  → Create ticket via ITSM API
  → Store mapping (workflow_id ↔ ticket_id)
  → Sync status updates bidirectionally
  → Close ticket on workflow completion
```

### 3.3 Priority Mapping

| DCIM Severity | ServiceNow Priority | Jira Priority |
|---------------|--------------------:|--------------:|
| Critical (P1) | 1 - Critical | Highest |
| High (P2) | 2 - High | High |
| Medium (P3) | 3 - Moderate | Medium |
| Low (P4) | 4 - Low | Low |

### 3.4 Bidirectional Sync

```python
# workflow/itsm_integration.py

class ITSMIntegration:
    def __init__(self, snow_client, jira_client, db):
        self.snow = snow_client
        self.jira = jira_client
        self.db = db

    async def create_ticket(self, workflow: dict, system: str = "servicenow") -> dict:
        """Create ITSM ticket from workflow."""

        # Determine ticket type
        ticket_type = self._determine_ticket_type(workflow)

        # Map severity to priority
        priority = self._map_priority(workflow["severity"])

        # Create ticket
        if system == "servicenow":
            ticket = await self.snow.create_incident({
                "short_description": workflow["title"],
                "description": workflow["description"],
                "priority": priority,
                "category": workflow.get("category", "hardware"),
                "assignment_group": self._get_assignment_group(workflow),
                "impact": self._map_impact(workflow["severity"]),
                "urgency": self._map_urgency(workflow["severity"]),
            })
        elif system == "jira":
            ticket = await self.jira.create_issue({
                "project": "DCIM",
                "issuetype": "Incident",
                "summary": workflow["title"],
                "description": workflow["description"],
                "priority": {"name": priority},
            })

        # Store mapping
        await self.db.create_ticket_mapping(
            workflow_id=workflow["id"],
            ticket_id=ticket["id"],
            ticket_number=ticket["number"],
            system=system
        )

        return ticket

    async def sync_status(self, ticket_id: str, new_status: str):
        """Sync ticket status from workflow."""

        mapping = await self.db.get_ticket_mapping(ticket_id)

        # Update ITSM system
        if mapping["system"] == "servicenow":
            await self.snow.update_incident(ticket_id, {"state": new_status})
        elif mapping["system"] == "jira":
            await self.jira.update_issue(ticket_id, {"status": new_status})

        # Update workflow status
        await self._sync_to_workflow(mapping["workflow_id"], new_status)
```

---

## 4. Multi-Level Approval Workflows

### 4.1 Approval Chain Configuration

```yaml
# approval-changes.yaml

approval_chains:
  # Low-risk changes
  standard_change:
    levels:
      - level: 1
        approvers:
          - role: "team_lead"
        timeout_hours: 4
        escalation: "manager"

  # Medium-risk changes
  normal_change:
    levels:
      - level: 1
        approvers:
          - role: "team_lead"
        timeout_hours: 4
        escalation: "manager"
      - level: 2
        approvers:
          - role: "change_manager"
        timeout_hours: 24
        escalation: "director"

  # High-risk changes (P1/P2)
  emergency_change:
    levels:
      - level: 1
        approvers:
          - role: "on_call_lead"
        timeout_hours: 1
        escalation: "director"
      - level: 2
        approvers:
          - role: "change_manager"
        timeout_hours: 4
        escalation: "vp_infrastructure"

  # Critical infrastructure changes
  critical_change:
    levels:
      - level: 1
        approvers:
          - role: "team_lead"
        timeout_hours: 2
        escalation: "change_manager"
      - level: 2
        approvers:
          - role: "change_manager"
        timeout_hours: 4
        escalation: "director"
      - level: 3
        approvers:
          - role: "director"
        timeout_hours: 24
        escalation: "vp_infrastructure"
```

### 4.2 Approval API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/workflow/approvals/pending` | List pending approvals |
| POST | `/api/v1/workflow/approvals/{id}/approve` | Approve |
| POST | `/api/v1/workflow/approvals/{id}/reject` | Reject with reason |
| POST | `/api/v1/workflow/approvals/batch` | Batch approve |
| GET | `/api/v1/workflow/approvals/history` | Approval history |

---

## 5. Runbook Engine

### 5.1 Runbook Definition

```yaml
# runbook-java-restart.yaml

runbook:
  id: RB-001
  name: "Restart Java Application"
  description: "Restart a Java application service with safety checks"
  version: "1.2"

  triggers:
    - type: "alert"
      alert_name: "high_cpu_usage"
      threshold: 90

  steps:
    - id: step_1
      name: "Pre-flight checks"
      type: "automated"
      script: "scripts/check_service_health.py"
      parameters:
        service_name: "{{workflow.service_name}}"
        timeout: 30
      on_failure: "abort"

    - id: step_2
      name: "Notify stakeholders"
      type: "notification"
      channel: "slack"
      message: "Restarting {{workflow.service_name}} on {{workflow.target_host}}"

    - id: step_3
      name: "Stop application"
      type: "automated"
      script: "scripts/stop_service.py"
      parameters:
        service_name: "{{workflow.service_name}}"
        timeout: 60
      on_failure: "alert_only"

    - id: step_4
      name: "Wait for graceful shutdown"
      type: "wait"
      duration_seconds: 10

    - id: step_5
      name: "Start application"
      type: "automated"
      script: "scripts/start_service.py"
      parameters:
        service_name: "{{workflow.service_name}}"
        timeout: 120
      on_failure: "rollback"

    - id: step_6
      name: "Verify health"
      type: "automated"
      script: "scripts/verify_health.py"
      parameters:
        service_name: "{{workflow.service_name}}"
        expected_status: "healthy"
        timeout: 30
      on_failure: "rollback"

    - id: step_7
      name: "Manual verification"
      type: "manual"
      assignee: "{{workflow.requester}}"
      instruction: "Verify the service is responding correctly"
      timeout_hours: 1
      on_timeout: "escalate"

  rollback:
    - id: rollback_1
      name: "Restore previous version"
      type: "automated"
      script: "scripts/restore_previous.py"
```

### 5.2 Runbook Engine Implementation

```python
# workflow/runbook_engine.py

from typing import List, Dict, Any
import asyncio

class RunbookEngine:
    def __init__(self, db, script_runner, notification_service, cmdb_client):
        self.db = db
        self.scripts = script_runner
        self.notifications = notification_service
        self.cmdb = cmdb_client

    async def execute_runbook(self, runbook_id: str, workflow_id: str, context: dict) -> dict:
        """Execute a runbook."""

        runbook = await self.db.get_runbook(runbook_id)
        execution_id = str(uuid.uuid4())

        execution = {
            "execution_id": execution_id,
            "runbook_id": runbook_id,
            "workflow_id": workflow_id,
            "status": "running",
            "current_step": None,
            "step_results": [],
            "started_at": datetime.utcnow(),
        }

        try:
            for step in runbook["steps"]:
                execution["current_step"] = step["id"]

                result = await self._execute_step(step, context, execution_id)
                execution["step_results"].append(result)

                # Log step result
                await self.db.log_step_result(execution_id, step["id"], result)

                if not result["success"]:
                    if step.get("on_failure") == "abort":
                        execution["status"] = "failed"
                        await self._handle_failure(execution, step, runbook)
                        return execution
                    elif step.get("on_failure") == "rollback":
                        await self._execute_rollback(runbook, execution, context)
                        execution["status"] = "rolled_back"
                        return execution

            execution["status"] = "completed"
            execution["completed_at"] = datetime.utcnow()

        except Exception as e:
            execution["status"] = "error"
            execution["error"] = str(e)
            await self._execute_rollback(runbook, execution, context)

        return execution

    async def _execute_step(self, step: dict, context: dict, execution_id: str) -> dict:
        """Execute a single runbook step."""

        step_type = step["type"]

        if step_type == "automated":
            # Execute script
            script_path = step["script"]
            parameters = self._resolve_parameters(step.get("parameters", {}), context)

            result = await self.scripts.run(script_path, parameters, timeout=step.get("timeout", 60))

            return {
                "step_id": step["id"],
                "type": "automated",
                "success": result["exit_code"] == 0,
                "output": result["stdout"],
                "error": result.get("stderr"),
                "duration_ms": result["duration_ms"],
            }

        elif step_type == "notification":
            # Send notification
            await self.notifications.send(
                channel=step["channel"],
                message=self._resolve_template(step["message"], context)
            )

            return {
                "step_id": step["id"],
                "type": "notification",
                "success": True,
                "output": f"Notification sent to {step['channel']}",
            }

        elif step_type == "manual":
            # Wait for manual action
            await self.db.create_manual_step(
                execution_id=execution_id,
                step_id=step["id"],
                assignee=self._resolve_template(step.get("assignee", ""), context),
                instruction=self._resolve_template(step["instruction"], context),
                timeout_hours=step.get("timeout_hours", 24)
            )

            return {
                "step_id": step["id"],
                "type": "manual",
                "success": True,
                "output": "Waiting for manual action",
            }

        elif step_type == "wait":
            # Wait for specified duration
            await asyncio.sleep(step["duration_seconds"])

            return {
                "step_id": step["id"],
                "type": "wait",
                "success": True,
                "output": f"Waited {step['duration_seconds']} seconds",
            }
```

---

## 6. Auto-Remediation

### 6.1 Safety Guards

| Guard | Description | Action on Violation |
|-------|-------------|---------------------|
| Blast Radius Check | Max CIs affected by remediation | Block if > threshold |
| Approval Required | Critical actions need approval | Route to approval |
| Time Window | Only execute during maintenance | Queue for window |
| Rate Limit | Max remediation attempts per hour | Block if exceeded |
| Dry Run | Preview changes before apply | Show preview, await confirm |

### 6.2 Remediation Rules

```yaml
# remediation-rules.yaml

rules:
  - id: AR-001
    name: "Restart crashed service"
    trigger:
      alert_name: "service_down"
      severity: "high"
    action:
      type: "runbook"
      runbook_id: "RB-001"
    safety:
      blast_radius_max: 3
      approval_required: false
      time_window: "any"

  - id: AR-002
    name: "Block malicious IP"
    trigger:
      alert_name: "brute_force_detected"
      severity: "critical"
    action:
      type: "script"
      script: "scripts/block_ip.sh"
    safety:
      blast_radius_max: 1
      approval_required: false
      rate_limit: 10

  - id: AR-003
    name: "Scale up server"
    trigger:
      alert_name: "capacity_threshold"
      metric: "cpu_usage"
      threshold: 90
      duration_minutes: 15
    action:
      type: "api_call"
      api: "cloud_api"
      method: "scale_up"
    safety:
      blast_radius_max: 1
      approval_required: true
      time_window: "any"
      max_instances: 10

  - id: AR-004
    name: "Restart database replica"
    trigger:
      alert_name: "replication_lag"
      threshold_seconds: 300
      duration_minutes: 10
    action:
      type: "runbook"
      runbook_id: "RB-003"
    safety:
      blast_radius_max: 5
      approval_required: false
      time_window: "off_peak"
```

### 6.3 Remediation Implementation

```python
# workflow/auto_remediation.py

class AutoRemediation:
    def __init__(self, db, cmdb_client, runbook_engine, notification_service):
        self.db = db
        self.cmdb = cmdb_client
        self.runbooks = runbook_engine
        self.notifications = notification_service

    async def evaluate_alert(self, alert: dict) -> dict:
        """Evaluate alert against remediation rules."""

        # Find matching rules
        matching_rules = await self._find_matching_rules(alert)

        for rule in matching_rules:
            # Safety checks
            safety_result = await self._check_safety(rule, alert)

            if not safety_result["passed"]:
                await self._log_safety_block(rule["id"], alert, safety_result)
                continue

            # Execute remediation
            result = await self._execute_remediation(rule, alert)

            return {
                "rule_id": rule["id"],
                "alert_id": alert["id"],
                "action_taken": result["action"],
                "success": result["success"],
                "safety_checks": safety_result,
            }

        return {"action_taken": "none", "reason": "no matching rules or safety blocked"}

    async def _check_safety(self, rule: dict, alert: dict) -> dict:
        """Perform safety checks before remediation."""

        checks = []

        # 1. Blast radius check
        affected_cis = await self._estimate_blast_radius(alert)
        blast_radius_ok = len(affected_cis) <= rule["safety"]["blast_radius_max"]
        checks.append({"check": "blast_radius", "passed": blast_radius_ok, "affected_count": len(affected_cis)})

        # 2. Rate limit check
        recent_count = await self._get_recent_remediation_count(rule["id"], hours=1)
        rate_limit_ok = recent_count < rule["safety"].get("rate_limit", 100)
        checks.append({"check": "rate_limit", "passed": rate_limit_ok, "recent_count": recent_count})

        # 3. Time window check
        time_window_ok = await self._check_time_window(rule["safety"].get("time_window", "any"))
        checks.append({"check": "time_window", "passed": time_window_ok})

        all_passed = all(c["passed"] for c in checks)

        return {
            "passed": all_passed,
            "checks": checks,
            "requires_approval": rule["safety"].get("approval_required", False)
        }
```

---

## 7. Escalation Rules

### 7.1 Escalation Matrix

| Severity | Level 1 (Initial) | Level 2 (+30min) | Level 3 (+1h) | Level 4 (+4h) |
|----------|-------------------|-------------------|----------------|----------------|
| Critical | On-call Engineer | Team Lead | Manager | Director |
| High | On-call Engineer | Team Lead | Manager | — |
| Medium | Team Lead | Manager | — | — |
| Low | Team Lead | — | — | — |

### 7.2 Escalation Implementation

```python
# workflow/escalation.py

class EscalationService:
    def __init__(self, db, notification_service, schedule_client):
        self.db = db
        self.notifications = notification_service
        self.schedule = schedule_client

    async def check_escalations(self):
        """Check all active workflows for escalation needs."""

        active_workflows = await self.db.get_active_workflows()

        for workflow in active_workflows:
            elapsed = (datetime.utcnow() - workflow["created_at"]).total_seconds() / 60

            # Get escalation rules for severity
            rules = await self._get_escalation_rules(workflow["severity"])

            for rule in rules:
                if elapsed >= rule["trigger_minutes"] and not workflow.get(f"escalated_level_{rule['level']}"):
                    await self._escalate(workflow, rule)

    async def _escalate(self, workflow: dict, rule: dict):
        """Execute escalation."""

        # Get assignee
        assignee = await self._get_assignee(rule["role"], workflow)

        if not assignee:
            # Try next level
            return

        # Send escalation notification
        await self.notifications.send(
            channel="email",
            to=assignee["email"],
            subject=f"ESCALATION: {workflow['title']} [{workflow['severity']}]",
            message=self._format_escalation_message(workflow, rule)
        )

        await self.notifications.send(
            channel="slack",
            to=rule.get("slack_channel", "#noc-alerts"),
            message=f"⬆️ ESCALATED: {workflow['title']} → @{assignee['name']}"
        )

        # Mark as escalated
        await self.db.mark_escalated(workflow["id"], rule["level"], assignee["id"])
```

---

## 8. n8n/Temporal Integration

### 8.1 Integration Architecture

```
n8n/Temporal Workflow Engine
  ← REST API triggers from DCIM
  → Webhook callbacks to DCIM
  ← Custom nodes for DCIM actions
  → Visual workflow designer
```

### 8.2 Workflow Orchestration

| Feature | n8n | Temporal |
|---------|-----|----------|
| Visual designer | ✅ Excellent | ❌ Code-based |
| Self-hosted | ✅ | ✅ |
| Scalability | Medium | High |
| State persistence | ✅ | ✅ |
| Retry logic | ✅ | ✅ (advanced) |
| Community workflows | ✅ Many | ❌ Limited |
| Best for | Simple automations | Complex, long-running |

### 8.3 REST API Integration

```python
# workflow/orchestration.py

class WorkflowOrchestrator:
    def __init__(self, n8n_client, temporal_client, db):
        self.n8n = n8n_client
        self.temporal = temporal_client
        self.db = db

    async def trigger_workflow(self, workflow_type: str, payload: dict) -> dict:
        """Trigger workflow in n8n or Temporal."""

        # Determine which engine to use
        if workflow_type in ["incident_response", "change_management"]:
            # Complex workflows → Temporal
            result = await self.temporal.start_workflow(
                workflow_type=workflow_type,
                payload=payload
            )
        else:
            # Simple automations → n8n
            result = await self.n8n.trigger_webhook(
                webhook_id=f"dcim-{workflow_type}",
                data=payload
            )

        # Store orchestration reference
        await self.db.create_orchestration_ref(
            workflow_type=workflow_type,
            payload=payload,
            engine="temporal" if workflow_type in ["incident_response", "change_management"] else "n8n",
            external_id=result["workflow_id"]
        )

        return result

    async def handle_callback(self, engine: str, external_id: str, status: str, result: dict):
        """Handle callback from n8n/Temporal."""

        # Update internal workflow
        mapping = await self.db.get_orchestration_ref(external_id)

        if status == "completed":
            await self.db.complete_workflow(mapping["workflow_id"], result)
        elif status == "failed":
            await self.db.fail_workflow(mapping["workflow_id"], result)
```

---

## 9. Workflow Types

| Type | Trigger | State Machine | Approval | Runbook | ITSM |
|------|---------|---------------|----------|---------|------|
| Incident Response | Alert (SIEM/Analytics) | Full | Optional | Yes | Auto-create |
| Change Management | Manual request | Full | Multi-level | Yes | Auto-create |
| Auto-Remediation | Alert threshold | Simplified | Safety guard | Yes | Log only |
| Provisioning | API/Manual | Full | Single-level | Yes | Auto-create |
| Decommission | Manual request | Full | Multi-level | Yes | Auto-create |
| Compliance Remediation | CIS violation | Simplified | Required | Yes | Auto-create |
| Maintenance Window | Scheduled | Simplified | Required | Yes | Auto-create |

---

## 10. Performance & Sizing

### 10.1 Processing Targets

| Operation | Target | Resource |
|-----------|--------|----------|
| Workflow creation | < 100ms | 1 vCPU |
| State transition | < 50ms | 1 vCPU |
| Ticket creation | < 30s | 1 vCPU |
| Approval notification | < 1min | 1 vCPU |
| Runbook execution | < 5min | 2 vCPU |
| Auto-remediation | < 2min | 1 vCPU |
| Escalation check | < 30s | 1 vCPU |

### 10.2 Resource Allocation

| Component | vCPU | RAM | Storage | Instances |
|-----------|------|-----|---------|-----------|
| Workflow State Machine | 2 | 4 GB | 10 GB | 2 |
| ITSM Integration | 1 | 2 GB | — | 2 |
| Runbook Engine | 2 | 4 GB | — | 2 |
| Auto-Remediation | 1 | 2 GB | — | 1 |
| Escalation Service | 1 | 2 GB | — | 1 |
| n8n | 2 | 4 GB | 10 GB | 1 |
| Temporal (optional) | 2 | 4 GB | 10 GB | 1 |
| **Total** | **~11** | **~22 GB** | **~30 GB** | **~10** |

---

## 11. Security

| Control | Implementation |
|---------|---------------|
| RBAC | 5 roles: admin, operator, viewer, approver, auditor |
| Approval audit | Every approval logged with user + timestamp |
| Runbook access | Only authorized scripts can be executed |
| Remediation guards | Blast radius + approval for critical |
| Secret management | Vault for ITSM credentials |
| Audit trail | Every workflow action logged |

---

## 12. Monitoring & Alerting

| Metric | Type | Description |
|--------|------|-------------|
| `workflow_total_active` | Gauge | Active workflows |
| `workflow_total_completed` | Counter | Completed workflows |
| `workflow_total_failed` | Counter | Failed workflows |
| `workflow_duration_seconds` | Histogram | Workflow duration |
| `workflow_approval_pending` | Gauge | Pending approvals |
| `workflow_approval_sla_breach` | Counter | SLA breaches |
| `workflow_escalation_total` | Counter | Escalations triggered |
| `workflow_ticket_created` | Counter | ITSM tickets created |
| `workflow_ticket_sync_errors` | Counter | Sync errors |
| `workflow_remediation_total` | Counter | Auto-remediation attempts |
| `workflow_remediation_success` | Counter | Successful remediations |
| `workflow_runbook_steps_total` | Counter | Runbook steps executed |

---

## 13. Acceptance Criteria — Block 8 Complete

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | State machine working | All transitions tested | ⬜ |
| 2 | State persistence | States survive restart | ⬜ |
| 3 | ITSM integration (ServiceNow) | Ticket create/sync/close | ⬜ |
| 4 | ITSM integration (Jira) | Ticket create/sync/close | ⬜ |
| 5 | Approval workflows | Multi-level approval chains | ⬜ |
| 6 | Approval timeout + escalation | Timeout triggers escalation | ⬜ |
| 7 | Batch approval | Batch approve works | ⬜ |
| 8 | Runbook engine | Predefined procedure execution | ⬜ |
| 9 | Runbook conditional logic | On_failure routing works | ⬜ |
| 10 | Runbook manual steps | Manual step + timeout | ⬜ |
| 11 | Auto-remediation | Alert → action flow | ⬜ |
| 12 | Safety guards | Blast radius + approval check | ⬜ |
| 13 | Rollback capability | Failed remediation rolls back | ⬜ |
| 14 | Escalation rules | Time-based escalation | ⬜ |
| 15 | Notification channels | Email/Slack/Teams/SMS | ⬜ |
| 16 | n8n integration | Workflow trigger works | ⬜ |
| 17 | Webhook support | External trigger works | ⬜ |
| 18 | Monitoring dashboards | Grafana workflow metrics | ⬜ |

---

## 14. Gap Comparison Template

### Gap: [Component Name]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| State machine | [spec states] | [aktual states] | [match/mismatch] | P1-P4 |
| ITSM | [spec systems] | [aktual systems] | [gap detail] | P1-P4 |
| Approval | [spec chains] | [aktual chains] | [gap detail] | P1-P4 |
| Runbook | [spec features] | [aktual features] | [gap detail] | P1-P4 |
| Remediation | [spec guards] | [aktual guards] | [gap detail] | P1-P4 |
| Escalation | [spec matrix] | [aktual matrix] | [gap detail] | P1-P4 |
| Orchestration | [spec engine] | [aktual engine] | [gap detail] | P1-P4 |
| Security | [spec controls] | [aktual controls] | [gap detail] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

- [[workflow-automation]]
- [[analytics-ai-engine]] — alert triggers
- [[siem-soc]] — security incident workflows
- [[web-dashboard]] — task board view
- [[cmdb]] — impact assessment
- [[auto-remediation-runbook]]
- [[workflow-engine-comparison]]
- [[dcim-core-platform]]

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-23
> **Purpose:** Reference for team comparison → gap identification → connection dots
> **Phase 2 Progress:** B5 ✅ → B6 ✅ → B7 ✅ → B8 ✅ → B9 ⬜
