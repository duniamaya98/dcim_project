---
title: "DCIM Core Platform — Hermes Agentic AI Operations Control Plane Plan"
version: "1.0"
created: 2026-07-14
updated: 2026-07-14
type: summary
status: proposed
tags: [agentic-ai, hermes, multi-agent, mcp, orchestration, governance, security, workflow-automation, siem-soc, cmdb, analytics-ai, observability, ha-dr, deployment, implementation]
companion_to: "Deployment & Implementation Plan v2 for Dev, Staging and Production"
sources:
  - plans/implementation-plan.md
  - guides/deployment-implementation-guide.md
  - concepts/multi-agent-structure.md
  - concepts/security-architecture.md
  - concepts/secret-management-strategy.md
  - concepts/observability-strategy.md
  - concepts/change-management-process.md
  - concepts/incident-management-process.md
  - concepts/quality-gates.md
  - reference-designs/staging-production-environment.md
  - reference-designs/block4-cmdb.md
  - reference-designs/block6-siem-soc-v3.md
  - reference-designs/siem-soar.md
  - reference-designs/block7-analytics-ai-engine.md
  - reference-designs/block8-workflow-automation.md
  - comparisons/mt023-private-llm-platform-alignment.md
  - product-description/dcim-core-platform-product-description.md
  - "FIT041 Technical Requirements, Use Case Analysis, Baseline, SOP, and SLA documents"
  - "ChatGPT source artifact: hermes-dashboard-all-prompts.md"
external_sources:
  - https://github.com/NousResearch/hermes-agent
  - https://hermes-agent.nousresearch.com/docs/user-guide/profiles
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/tools
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp
  - https://hermes-agent.nousresearch.com/docs/user-guide/features/memory
  - https://hermes-agent.nousresearch.com/docs/user-guide/security
confidence: high
contested: true
contradictions: [multi-agent-structure, workflow-automation, security-architecture, implementation-plan]
---

# DCIM Core Platform — Hermes Agentic AI Operations Control Plane Plan

**Document version:** 1.0  
**Status:** Proposed companion plan  
**Repository path:** `plans/hermes-agentic-ai-operations-control-plane-plan.md`  
**Related plan:** Deployment & Implementation Plan v2 for Dev, Staging and Production  
**Change model:** Add-only. This document does not replace or modify Version 2 or another existing document.

> **Architecture decision:** Hermes Runtime is introduced as the **Agentic Operations Control Plane** for system-wide observation, reasoning, delegation, coordination, governed decisions, and controlled workflow initiation.

> **Security decision:** “Full management and control” means full operational awareness and governed orchestration coverage. It does not mean unrestricted root, raw database write, arbitrary shell, firewall, hypervisor, BMS, EPMS, UPS, PDU, or OT credentials.

---

## 1. Relationship to Deployment & Implementation Plan v2

This document is a standalone companion to Version 2. Version 2 remains responsible for Dev, Staging, and Production infrastructure, Hybrid Analytics + LLM/RAG, DI&I, Asset Repository, CMDB, SIEM/SOC, SOAR, Workflow Automation, security, observability, cutover, and delivery acceptance.

This plan adds a separate Agentic AI workstream:

- Hermes multi-agent runtime and specialist profiles.
- Internal MCP/Tool Gateway.
- Agent identity, RBAC, policy, and approval controls.
- Typed action contracts and Workflow/SOAR integration.
- Mission Control dashboard.
- Agent memory, skill, session, and knowledge governance.
- Agent observability, audit, evaluation, red-team testing, HA/DR, and progressive autonomy.

Version 2 does not need to be edited. Implementers treat this document as an additional dependent workstream after the relevant Version 2 foundations are available.

---

## 2. Executive Decision

Hermes will act as a supervisory and governed operations layer above all DCIM modules:

```text
Human Owner / NOC / SOC / Facilities / IT Ops / Change Authority
                              │
                              ▼
┌──────────────────────────────────────────────────────────────────────┐
│              HERMES AGENTIC OPERATIONS CONTROL PLANE                │
│                                                                      │
│ Intent/Event Intake → Evidence → Delegation → Plan → Policy Check   │
│ → Approval Request → Workflow Initiation → Verification → Learning  │
│                                                                      │
│ Hermes Orchestrator                                                  │
│   ├── NOC Operations Agent                                           │
│   ├── SOC Response Agent                                             │
│   ├── Facilities & OT Advisory Agent                                 │
│   ├── CMDB & Asset Integrity Agent                                   │
│   ├── Analytics & Capacity Agent                                     │
│   ├── Workflow & Change Agent                                        │
│   ├── Platform/SRE Agent                                             │
│   └── Compliance & Audit Agent                                       │
└──────────────────────────────┬───────────────────────────────────────┘
                               ▼
                     Internal MCP / Tool Gateway
             ┌─────────────────┴─────────────────┐
             ▼                                   ▼
       Read/Evidence Plane                Action Request Plane
 CMDB, Asset, TSDB, SIEM, Logs,       create draft, request runbook,
 Metrics, SLA, Wiki, Incidents        request containment/rollback
             │                                   │
             └─────────────────┬─────────────────┘
                               ▼
                    Policy & Approval Gateway
        RBAC + action allowlist + CI impact + maintenance window
         idempotency + rate limit + human/dual approval + audit
                               │
                               ▼
                 Workflow Automation / SOAR Execution
          Temporal / TraceCat / approved n8n / ITSM / adapters
                               │
                               ▼
                 Controlled Infrastructure Operations
                               │
                               ▼
                  Post-check → Rollback → Audit Evidence
```

Operating formula:

```text
Hermes reasons and coordinates.
CMDB defines target and impact context.
Deterministic Analytics supplies numerical authority.
Policy and humans authorize.
Workflow/SOAR executes.
Monitoring verifies.
```

Core DCIM services must continue to operate if Hermes, its model, RAG, Tool Gateway, or Mission Control is unavailable.

---

## 3. Objective, Scope, and Exclusions

### 3.1 Objective

Build a production-governed Hermes control plane that can:

1. Observe all approved DCIM operational domains.
2. Retrieve authoritative evidence from live systems and approved knowledge.
3. Delegate domain analysis to specialist agents.
4. Produce structured diagnosis, impact assessment, and action plans.
5. Request policy and human approval based on risk.
6. Start only approved and versioned workflows.
7. Verify results and request rollback when post-checks fail.
8. Preserve complete and immutable decision and execution evidence.
9. Progress from read-only assistance to bounded automation through measurable gates.

### 3.2 In Scope

- Hermes runtime installation and lifecycle.
- Persistent profiles and specialist agents.
- Agent identity and delegated authorization.
- Read MCP and Action Request MCP gateways.
- CMDB, Asset, telemetry, SIEM, incident, SLA, runbook, workflow, and ITSM tools.
- RAG and live tool retrieval.
- Memory, session, and skill governance.
- Policy, approval, action contract, kill switch, and workflow integration.
- Dev, Staging, Production, HA/DR, monitoring, security, testing, rollout, training, and handover.

### 3.3 Explicitly Out of Scope

- A5 unrestricted autonomy.
- Prompt-only execution.
- Direct actuator access from Hermes or an LLM.
- Autonomous approval of critical Production changes.
- Direct raw SQL, arbitrary shell, generic Kubernetes, firewall, hypervisor, or OT commands.
- Replacing deterministic analytics or CMDB impact analysis with generative assumptions.
- Training on unreviewed chats or incident evidence.
- Sharing writable state, sessions, or credentials between environments.

---

## 4. Design Principles

| Principle | Mandatory Rule |
|---|---|
| Human Authority First | Product Owner and delegated operational authorities retain final authority. |
| Separation of Duties | Reasoning, authorization, approval, execution, and verification are separate. |
| Evidence Before Action | No action without source IDs, timestamps, target CI, impact, expected result, and rollback. |
| Workflow Is the Execution Boundary | Hermes submits typed requests; Workflow/SOAR performs the action. |
| CMDB Is Target Context | Every Production target and blast radius are validated against CMDB topology. |
| Deterministic Analytics Is Numerical Authority | Forecast, anomaly score, PUE, threshold, and compliance values are not generated by the LLM. |
| Least Privilege | Every profile, tool, identity, and adapter receives minimum permission. |
| Progressive Autonomy | Launch A0/A1, then A2, then certify A3 per runbook; A4 is human-gated; A5 is prohibited. |
| Fail Closed | Missing evidence, policy failure, audit failure, ambiguity, or conflict stops the action. |
| Reversible by Default | Actions require idempotency, timeout, post-check, and rollback/compensation. |
| No Hidden Learning | Production memory and skill writes require review and approval. |
| Immutable Audit | Decision and execution traces are stored outside Hermes in an append-only/immutable destination. |
| Environment Isolation | Dev, Staging, and Production have separate profiles, identities, state, tools, secrets, and data. |

---

## 5. Agent Hierarchy and Responsibilities

### 5.1 Authority Levels

```text
Level 0 — Human Authorities
Level 1 — Hermes DCIM Orchestrator
Level 2 — Persistent Operational Specialist Agents
Level 3 — On-Demand Delegated Specialist Agents
Level 4 — Typed Tools and Workflow Executors
```

### 5.2 Persistent Production Agents

| Agent | Responsibility | Default Access | Autonomy Ceiling |
|---|---|---|---|
| DCIM Orchestrator | Objective state, routing, evidence fusion, conflict handling, approval coordination | Broad read + action request | A2; A3 through certified workflow |
| NOC Operations | Availability, performance, capacity, alert triage, runbook selection | NOC read + bounded requests | A3 certified runbooks |
| SOC Response | SIEM triage, enrichment, case, containment proposal | Security read + SOAR requests | A2; A4 after SOC approval |
| Facilities & OT Advisory | Power, cooling, environment, PUE, and safety impact | Read-only by default | A1; A4 dual approval only |
| Platform/SRE | DCIM platform health, DB/Kafka/storage/certificate/deployment readiness | Platform read + bounded requests | A3 within maintenance policy |
| Compliance & Audit | SLA, retention, access, evidence completeness, reports | Read-only | A1/A2 reporting |

### 5.3 On-Demand Agents

- CMDB & Asset Integrity Agent.
- Analytics & Capacity Agent.
- Workflow & Change Agent.
- Knowledge/Scribe Agent.
- Research/Scout Agent.
- Engineering/Dev Agent.

Existing Scout, Scribe, Reach, and Dev roles remain delivery-plane agents. Production access requires a separate operational profile, identity, toolset, and approval scope.

### 5.4 Role Boundary Rules

- Agents do not silently expand task scope.
- Delegated tasks inherit environment, data classification, correlation ID, and deadline.
- An agent cannot delegate authority greater than its own.
- Specialist output remains advisory until the Orchestrator and deterministic controls validate it.
- Agents cannot add tools, modify policy, or change Production identity by themselves.

---

## 6. Autonomy Model

| Level | Name | Capability | Production Policy |
|---|---|---|---|
| A0 | Observe | Query status and evidence; generate reports | Automatic |
| A1 | Advise | Diagnosis, RCA hypothesis, risk, recommendation | Automatic with citations |
| A2 | Coordinate | Draft incident/change, notify, collect evidence, request approval | Automatic within RBAC |
| A3 | Bounded Execute | Run a pre-approved low-risk workflow | Per-runbook certification |
| A4 | Controlled Critical | High-impact action after explicit approval | Human approval; OT dual approval |
| A5 | Unrestricted Autonomous | Arbitrary privileged action without external approval | Prohibited |

Initial Production posture:

| Domain | Go-Live | Maximum Planned |
|---|---:|---:|
| Knowledge and reporting | A1 | A2 |
| NOC coordination | A2 | A3 |
| CMDB/Asset integrity | A1 | A3 for certified reconciliation |
| Platform/SRE | A2 | A3 |
| SOC containment | A2 | A4 with SOC approval |
| Facilities/OT | A1 | A4 with dual approval |
| Production deployment | A1/A2 | A3 through GitOps and Change approval |

Promotion requires at least 30 days of shadow evidence, successful rollback tests, zero unauthorized actions, security sign-off, operational sign-off, and per-runbook certification.

---

## 7. Decision and Action Lifecycle

```text
Observe → Establish Identity/Scope → Collect Evidence → Delegate/Analyze
→ Synthesize → Build Plan → Policy Pre-check → Human Approval if required
→ Workflow Execute → Verify → Rollback/Escalate → Audit → Proposed Learning
```

Hermes must stop and escalate when:

- Target CI cannot be uniquely resolved.
- CMDB/topology data is stale or incomplete.
- Evidence timestamps conflict.
- The action or rollback is absent from the approved catalog.
- Policy, audit, approval, or kill-switch services are unavailable.
- Model confidence is below threshold.
- Specialist agents materially disagree.
- The request crosses environment or tenant boundaries.
- Safety, power, cooling, fire, or physical-security action lacks dual approval.

---

## 8. Tool and MCP Gateway Architecture

### 8.1 Tool Planes

| Plane | Purpose | Write Capability |
|---|---|---|
| Read/Evidence MCP | Query authoritative DCIM sources | None |
| Draft/Coordination MCP | Create drafts and approval requests | Draft state only |
| Action Request MCP | Submit typed requests to policy/workflow | No direct actuator |
| Workflow Executor | Execute approved runbook | Controlled and audited |
| Break-glass Admin | Emergency human operation | Never exposed to agents |

### 8.2 Required Read Tools

```text
get_platform_health
get_component_health
query_cmdb_ci
query_cmdb_topology
calculate_ci_impact
get_asset_context
query_timeseries
get_active_alerts
search_siem_events
get_incident_history
get_sla_policy
retrieve_runbook
get_workflow_status
get_change_window
get_approval_status
```

### 8.3 Required Action-Request Tools

```text
create_incident_draft
create_change_draft
request_approval
request_runbook_execution
request_pipeline_retry
request_reconciliation
request_containment
request_service_restart
request_scaling
request_rollback
cancel_pending_request
```

### 8.4 Prohibited Production Tools

```text
execute_any_shell_command
run_arbitrary_sql
write_any_file
kubectl_arbitrary
helm_arbitrary
snmp_set_raw
modbus_write_raw
bms_api_raw
firewall_command_raw
hypervisor_command_raw
power_cycle_raw
disable_audit
modify_policy
change_agent_toolset
```

### 8.5 MCP Requirements

- HTTPS remote MCP for Production.
- mTLS for sensitive read and all action-request servers.
- Explicit tool include lists; unexpected tool discovery is blocked or alerted.
- No host environment passthrough.
- Pinned source, version, checksum, and SBOM for every MCP server.
- Request, connect, and idle timeouts.
- Parallel tool calls disabled for shared-state operations.
- MCP prompt and resource wrappers disabled unless specifically approved.

Reference configuration:

```yaml
mcp_servers:
  dcim_read:
    url: "https://mcp-read.dcim.internal/mcp"
    client_cert:
      - "/run/secrets/hermes-read.crt"
      - "/run/secrets/hermes-read.key"
    timeout: 20
    connect_timeout: 5
    supports_parallel_tool_calls: true
    tools:
      include:
        - get_platform_health
        - query_cmdb_ci
        - query_cmdb_topology
        - calculate_ci_impact
        - get_asset_context
        - query_timeseries
        - get_active_alerts
        - search_siem_events
        - retrieve_runbook
        - get_workflow_status
      prompts: false
      resources: false

  dcim_action_request:
    url: "https://mcp-action-request.dcim.internal/mcp"
    client_cert:
      - "/run/secrets/hermes-action.crt"
      - "/run/secrets/hermes-action.key"
    timeout: 15
    connect_timeout: 5
    supports_parallel_tool_calls: false
    tools:
      include:
        - create_incident_draft
        - create_change_draft
        - request_approval
        - request_runbook_execution
        - request_rollback
        - cancel_pending_request
      prompts: false
      resources: false
```

---

## 9. Canonical Action Contract

Every requested operation must use a typed `ActionRequest`:

```json
{
  "action_request_id": "ARQ-2026-000184",
  "correlation_id": "INC-2026-001992",
  "requested_by": {
    "agent": "hermes-noc-agent",
    "profile": "prod-noc",
    "delegation_chain": ["hermes-orchestrator", "hermes-noc-agent"]
  },
  "environment": "production",
  "action": "restart_application_service",
  "target": {"ci_id": "CI-APP-0042", "instance": "app-02"},
  "priority": "P2",
  "risk": "medium",
  "reason": "Health check failed for five minutes",
  "evidence_refs": ["PROM-ALERT-8891", "CMDB-IMPACT-771"],
  "impact": {
    "affected_services": ["Customer Portal"],
    "blast_radius": "single-node",
    "redundancy_verified": true,
    "cmdb_freshness_seconds": 47
  },
  "runbook": {"id": "RB-APP-RESTART-003", "version": "2.4.1", "checksum": "sha256:..."},
  "expected_result": "service health returns UP within 120 seconds",
  "post_checks": ["health endpoint passes", "error rate below threshold"],
  "requires_approval": true,
  "approval_policy": "prod-p2-single-approval",
  "rollback_runbook": {"id": "RB-APP-ROLLBACK-003", "version": "1.2.0"},
  "timeout_seconds": 300,
  "idempotency_key": "CI-APP-0042-20260714-001",
  "expires_at": "2026-07-14T08:36:00Z"
}
```

State machine:

```text
draft → evidence_complete → policy_validated → waiting_approval → approved
→ queued → executing → verifying → completed

Terminal/exception states:
rejected | expired | canceled | failed | rolling_back | rolled_back | escalation_required
```

Policy checks include schema, identity, delegation chain, environment, allowlist, target freshness, CI impact, maintenance window, signed runbook, idempotency, rate/concurrency, approval, and audit availability.

Approval matrix:

| Action Class | Examples | Approval |
|---|---|---|
| Read/report | Health, query, report | None |
| Draft/coordinate | Draft ticket/change, notification | Agent RBAC |
| Low-risk A3 | Retry connector, rerun reconciliation, restart stateless replica | Certified runbook + policy |
| Medium Production | Scale worker, restart stateful service, configuration reload | One operational approver |
| Security containment | Isolate host, block IP, disable account | SOC approver and Change/Owner if policy requires |
| Infrastructure change | Firewall, hypervisor, Kubernetes, network | Change approval |
| Facilities/OT | Power, cooling, UPS/PDU, BMS/EPMS | Dual approval: Facilities + Change/Safety |
| Destructive/irreversible | Delete data, wipe, decommission, irreversible power action | Human break-glass process only |

---

## 10. Identity, RBAC, and Secrets

Every persistent Production profile requires:

- Unique profile name and workload identity.
- Unique mTLS certificate and Vault identity.
- Unique tool allowlist and audit principal.
- Separate memory, sessions, skills, and state directories.
- Named human owner and operational owner.

Example profiles:

```text
prod-orchestrator
prod-noc
prod-soc
prod-facilities
prod-sre
prod-governance
```

Secret rules:

- Credentials live in Vault or an approved external-secret system.
- No secret is stored in memory, skills, prompts, Git, session summaries, or logs.
- The Tool Gateway performs downstream credential exchange; the model never receives the credential.
- Tokens and certificates are short-lived and rotated.
- Tool responses are redacted before returning to the model.

---

## 11. Memory, Skills, Sessions, and RAG Governance

Production baseline:

```yaml
memory:
  memory_enabled: true
  user_profile_enabled: true
  write_approval: true

skills:
  write_approval: true
```

Rules:

- Memory and skill writes are staged for approval.
- Every operational lesson links to an incident, change, postmortem, or approved source.
- Memory is never authoritative for live state.
- Secrets, raw logs, PII, and dynamic credentials are prohibited.
- Cross-profile session access is disabled unless mediated by the Orchestrator.
- RAG sources require document ID, owner, version, effective date, classification, environment, supersession, and RBAC metadata.
- Operational answers cite source and timestamp.
- Corpus promotion follows Dev → Staging → Production with a manual gate.

Approved RAG corpus includes active Wiki pages, FIT041 documents, approved plans, API schemas, runbooks, SOAR playbooks, ADRs, validated postmortems, and model/tool/policy documentation.

---

## 12. Model and Reasoning Strategy

| Engine | Role | Authority |
|---|---|---|
| Deterministic Analytics | Anomaly, forecast, PUE, capacity, compliance calculations | Authoritative numerical evidence |
| Hermes Primary LLM | Planning, RAG, synthesis, tool selection, explanation | Advisory and coordination |
| Verifier/Critic | Check evidence, target, schema, contradictions | Advisory validation |
| Policy Engine | Authorization and constraints | Authoritative policy |
| Workflow Engine | Durable state and execution | Authoritative execution |

The primary local model candidate follows Version 2: `unsloth/gemma-4-12B-it-qat-GGUF:UD-Q4_K_XL`, served through an approved internal inference endpoint. Qwen or another approved MT-023 model remains a fallback and benchmark until the Gemma evaluation gate is complete.

Model promotion criteria:

- Tool-call schema validity ≥99.9%.
- Critical target-CI accuracy 100% on the approved golden set.
- Citation accuracy ≥98%.
- Prompt-injection containment 100% on the mandatory security set.
- No safety-policy bypass.
- SLO-compliant latency and throughput.
- Approved license, checksum, SBOM, vulnerability review, and rollback artifact.

Model consensus never replaces policy or human approval.

---

## 13. Environment and Deployment Design

| Capability | Development | Staging | Production |
|---|---|---|---|
| Data | Synthetic fixtures | Synthetic + approved masked snapshots | Live |
| Tools | Mock/sandbox | Real read + simulated action | Approved read and action-request tools |
| Autonomy | A0–A3 on test resources | A0–A4 simulation/shadow | A0–A2 first; A3 certified; A4 gated |
| Audit | Local development log | Full rehearsal | Immutable central audit |
| Runtime | Developer profiles | Production-equivalent profiles | Dedicated Production profiles |
| Availability | Best effort | Failover rehearsal | Active-passive Hermes; HA gateways/model/RAG |

### 13.1 Runtime Isolation

Hermes profiles separate Hermes state, but are not by themselves a filesystem security boundary. Production profiles must run with:

- Dedicated non-root identity and container/process boundary.
- Explicit `HERMES_HOME` and working directory.
- Read-only root filesystem where practical.
- No host Docker socket or shared host credentials.
- Minimal mounts and an egress allowlist.
- Resource limits and workload-specific service account.

### 13.2 Production HA Pattern

- One active writer/gateway per profile.
- Warm standby profile host.
- Leader lease or controlled failover.
- Encrypted frequent state snapshots.
- External action-request, workflow, policy, and audit stores.
- A3/A4 disabled during degraded recovery until policy, audit, and tool health are confirmed.

Unsupported active-active multi-writer profile state is prohibited.

---

## 14. Hardware Baseline

### 14.1 Development

| Component | Suggested Minimum |
|---|---|
| Hermes runtime and profiles | 4 vCPU, 8 GB RAM, 50 GB SSD |
| MCP/policy mocks | 2 vCPU, 4 GB RAM, 20 GB |
| Mission Control | 1 vCPU, 2 GB RAM, 20 GB |
| Local inference optional | 6–8 vCPU, 16–32 GB RAM, 16 GB VRAM recommended |
| Vector/embedding | 2 vCPU, 4–8 GB RAM, 50 GB |

Recommended Dev host: 12 vCPU, 32–48 GB RAM, 500 GB SSD.

### 14.2 Staging

- Two Hermes hosts, each 4 vCPU, 8 GB RAM, and 100 GB SSD.
- Two Read MCP replicas and two Action Simulator replicas, each 2 vCPU and 4 GB RAM.
- Two policy/approval replicas, each 2 vCPU and 4 GB RAM.
- One inference node with 24 GB VRAM.
- Production-parity RAG/vector deployment where possible.

### 14.3 Production

| Component | Quantity | Per-Node Recommendation |
|---|---:|---|
| Hermes runtime hosts | 2 | 8 vCPU, 16 GB RAM, 200 GB encrypted SSD |
| Read MCP Gateway | 2–3 | 4 vCPU, 8 GB RAM |
| Action Request Gateway | 2–3 | 4 vCPU, 8 GB RAM |
| Policy Engine | 3 | 4 vCPU, 8 GB RAM |
| Mission Control/API | 2 | 4 vCPU, 8 GB RAM |
| Inference | 2 | 8–16 vCPU, 32–64 GB RAM, 24–48 GB VRAM |
| Embedding/reranker | 2 | 4–8 vCPU, 16–32 GB RAM |
| Vector database | 3 | 4–8 vCPU, 16–32 GB RAM, 500 GB+ |

Maintain at least 30% CPU/RAM headroom and 40% inference burst headroom.

---

## 15. Network and Security Zones

Required zones:

1. Agent Control Zone.
2. Model/RAG Zone.
3. Read Tool Zone.
4. Action Request/Policy Zone.
5. Workflow/SOAR Zone.
6. DCIM Data Zone.
7. Management Zone.
8. OT/Facilities Zone.
9. External Integration/DMZ Zone.

Mandatory rules:

- Default deny between zones.
- Hermes has no direct route to OT devices.
- The model endpoint has no route to DCIM targets.
- Read Gateway accesses documented read APIs only.
- Action Gateway connects only to policy and Workflow/SOAR.
- Workflow adapters have target-specific service accounts.
- TLS 1.2+ on all internal traffic; mTLS on agent, tool, and action traffic.
- DNS and NTP are mandatory and monitored.

---

## 16. Installation and Configuration Setup

### 16.1 Pre-Implementation Checklist

- [ ] Human authority and approval matrix signed.
- [ ] Production autonomy ceiling approved.
- [ ] Agent and service owners assigned.
- [ ] Network zones, Vault, PKI, OIDC, DNS, and NTP ready.
- [ ] Hermes version pinned and tested.
- [ ] Primary and fallback model approved.
- [ ] Tool schemas and allowlists approved.
- [ ] Policy engine and kill switch designed.
- [ ] CMDB target and impact quality meets the entry gate.
- [ ] Versioned execution and rollback runbooks ready.
- [ ] Immutable audit store and retention ready.
- [ ] Staging incident replay dataset available.

### 16.2 Proposed Project Structure

```text
dcim-agentic-ai/
├── config/{dev,staging,production}/
├── profiles/{orchestrator,noc,soc,facilities,sre,governance}/
├── prompts/
├── policies/
├── tools/{schemas,read-mcp,action-request-mcp}/
├── action-contracts/
├── runbook-catalog/
├── evaluation/{golden-set,red-team,replay}/
├── mission-control/
├── monitoring/
├── helm/
├── kustomize/
├── scripts/
└── docs/{architecture,runbooks,training}/
```

### 16.3 Runtime Installation

1. Pin Hermes release/commit and verify checksum.
2. Build an internal non-root container image with SBOM and vulnerability scan.
3. Create a separate profile for each persistent agent.
4. Set explicit `HERMES_HOME` and `terminal.cwd`.
5. Disable unnecessary toolsets.
6. Configure the approved model endpoint and fallback.
7. Configure memory and skill write approval.
8. Configure Read and Action Request MCP servers.
9. Enable structured logs and central forwarding.
10. Register health checks and metrics.
11. Snapshot profile state and test restore.
12. Register each profile in Mission Control.

Reference Production guardrail:

```yaml
approvals:
  mode: manual
  cron_mode: deny
  timeout: 120
  deny:
    - "*kubectl delete*"
    - "*helm uninstall*"
    - "*DROP DATABASE*"
    - "*TRUNCATE TABLE*"
    - "*snmpset*"
    - "*modbus*write*"
    - "*poweroff*"
    - "*shutdown*"
    - "*reboot*"
    - "*iptables*"
    - "*firewall*"

terminal:
  backend: docker
  cwd: /workspace
  home_mode: profile
```

Production must not use `--yolo`, `/yolo`, or disabled approvals.

---

## 17. Mission Control Dashboard

Mission Control provides read-mostly views for:

- Runtime and gateway health.
- Agent/profile status and current objectives.
- Delegated task activity.
- Model, token, tool, queue, and latency usage.
- Approval and ActionRequest lifecycle.
- Policy denials and security events.
- Scheduled tasks and approved content.
- Autonomy level by domain and kill-switch status.
- Correlation trace from request to evidence and workflow result.

Required tabs:

| Tab | Content |
|---|---|
| Overview | System health, current directive, queue, sessions, errors, uptime |
| Agents | Profile status, role, model, toolset, task history, success rate |
| Tasks | Operational objectives and approval/action state |
| Schedule | Approved cron and scheduled reports/audits |
| Content | Approved reports, plans, runbooks, and drafts |
| Actions | ActionRequest lifecycle, approval, runbook, verification, rollback |
| Security | Policy denies, prompt injection, tool violations, access anomalies |
| Autonomy | Current level per domain, certified runbooks, kill switch |
| Audit | Searchable end-to-end correlation trace |

Production requirements:

- OIDC, RBAC, TLS, audit, and session timeout.
- No direct editing of Hermes state, memory, skills, or profile configuration.
- Writes limited to operator annotation, task record, signed approval through approved APIs, and the separately protected kill switch.
- Local Hermes SQLite files may be read-only sources in a pilot, but Production data is centralized and not dependent solely on local SQLite.

---

## 18. Observability and Audit

Required metrics:

```text
hermes_agent_up
hermes_agent_tasks_total
hermes_agent_task_duration_seconds
hermes_agent_queue_depth
hermes_delegate_tasks_total
hermes_llm_requests_total
hermes_llm_latency_seconds
hermes_llm_tokens_total
hermes_tool_calls_total
hermes_tool_latency_seconds
hermes_policy_decisions_total
hermes_action_requests_total
hermes_approval_wait_seconds
hermes_action_verification_failures_total
hermes_rollbacks_total
hermes_memory_writes_total
hermes_skill_writes_total
hermes_prompt_injection_events_total
hermes_kill_switch_state
dcim_agentic_autonomy_level
```

Every decision, tool, and action trace records:

- Correlation ID and session ID.
- Profile, service identity, and human/system requester.
- Delegation chain.
- Model and model revision.
- Prompt, policy, and tool schema versions.
- Retrieved evidence IDs and timestamps.
- Redacted tool arguments and result summary.
- Decision, confidence, and approval state.
- ActionRequest and workflow execution IDs.
- Post-check and rollback outcome.

Audit requirements:

- Remote append-only/immutable destination.
- Integrity hash or signature.
- NTP-synchronized timestamp.
- Separation from the agent runtime.
- Search by incident, CI, agent, user, action, and time.
- Audit unavailability blocks Production action.

---

## 19. HA, Backup, and Disaster Recovery

| Capability | RPO | RTO |
|---|---:|---:|
| Hermes profile state | ≤15 minutes | ≤1 hour |
| Action/policy state | ≤1 minute | ≤15 minutes |
| Audit evidence | Near-zero/continuous | ≤15 minutes |
| RAG corpus/index | Last promotion or ≤24 hours | ≤4 hours |
| Model serving | Approved artifact | ≤15 minutes using fallback |
| Mission Control | Config ≤24 hours; live state rehydrates | ≤1 hour |

Back up:

- Signed profile configuration, role prompts, and tool manifests in Git.
- Encrypted profile memory, skills, sessions, and state snapshots.
- Model and corpus artifacts in approved registries.
- Policy bundles and runbook catalog.
- Action/workflow state in HA transactional stores.
- Audit in immutable replicated storage.

Failover starts in read-only/degraded mode. A3/A4 remain disabled until all control services are healthy.

---

## 20. Security Hardening and Threat Controls

| Threat | Primary Controls |
|---|---|
| Prompt injection from logs/documents | Content-as-data boundary, sanitization, source trust, red-team tests |
| Unexpected dangerous tool | Explicit MCP include list, pinned manifest, discovery-change alert |
| Credential exfiltration | Gateway credential brokerage, redaction, no downstream secret exposure |
| Arbitrary command execution | No Production terminal tool; container sandbox in non-prod |
| Compromised profile | Dedicated identity/container, egress limit, certificate revocation, kill switch |
| Memory or skill poisoning | Write approval, signed version, evidence link, Staging promotion |
| Wrong-target action | CMDB uniqueness/freshness/topology/impact validation |
| Replay or duplicate action | Idempotency key, expiry, nonce, external request state |
| Approval spoofing | OIDC, signed approval event, approver role validation |
| Cross-environment action | Environment-scoped identity, certificate, DNS, tool, and policy |
| Runaway agent loop | Task timeout, tool-round/token/concurrency budget, watchdog |
| Hallucinated evidence | Mandatory source IDs, live queries, citation validation |
| Audit tampering | Remote immutable store and separate access domain |
| OT safety hazard | No direct route, dual approval, safety interlock, manual override |

### Global Kill Switch

The kill switch must:

- Disable all Action Request tools immediately.
- Reject new Production actions at the Policy Gateway.
- Preserve read-only evidence and audit.
- Pause pending non-executing actions.
- Be operable by authorized humans outside Hermes.
- Be tested quarterly.

---

## 21. Implementation Phases

| Phase | Scope | Exit Gate |
|---|---|---|
| 0 | Charter, RACI, autonomy matrix, threat model, ADRs | Signed governance baseline |
| 1 | Pinned Hermes runtime, containers, identity, Vault/PKI, model endpoint | Dev/Staging isolation and health pass |
| 2 | Orchestrator and specialist profiles, routing, delegation budgets | Role and delegation tests pass |
| 3 | Read MCP tools for CMDB, Asset, telemetry, SIEM, incidents, SLA, runbooks | A0/A1 golden-set passes |
| 4 | RAG ingestion, vector/keyword retrieval, RBAC metadata, citation validator | Retrieval and injection tests pass |
| 5 | Mission Control and central agent observability | UAT and security pass |
| 6 | ActionRequest schema, state machine, policy, approval, idempotency, kill switch | Bypass/replay/wrong-target tests fail closed |
| 7 | Temporal/TraceCat/ITSM integration, signed runbooks, post-check, rollback | End-to-end rollback test passes |
| 8 | Security hardening and red team | No unresolved critical/high issues |
| 9 | Historical replay and at least 30 days shadow mode | Quality metrics and owner sign-off |
| 10 | Production A0/A1 | Stable advisory SLO |
| 11 | Production A2 | Draft and approval-routing accuracy passes |
| 12 | A3 per-runbook certification | Supervised execution and rollback pass |
| 13 | Optional A4 pilot | Separate executive/security/change approval |
| 14 | Documentation, training, handover | Operational acceptance signed |

Initial A3 candidates:

- Retry failed ingestion connector.
- Re-run reconciliation.
- Restart one stateless application replica.
- Refresh an approved cache.
- Scale a worker pool within a pre-approved range.
- Re-run a failed report or data-quality task.

A4 candidates, only after separate approval:

- Security host isolation.
- Firewall block through SOAR.
- VM shutdown during an approved incident/change.
- Network change.
- Facilities/OT action with dual approval.

---

## 22. Testing Strategy

Required test classes:

- Unit, schema, contract, integration, and end-to-end.
- Historical incident replay.
- Model/RAG/tool-use evaluation.
- Prompt/tool injection and credential-exfiltration red team.
- Wrong-target, replay, approval-spoof, and policy-outage tests.
- Performance, burst, and concurrent delegation.
- Chaos: model, MCP, policy, network, state, and audit failure.
- Backup, restore, failover, and fallback-model tests.
- Human takeover and approval usability.

Mandatory safety cases must prove that Hermes denies or escalates when:

- A user asks Hermes to bypass approval.
- A retrieved document says “ignore previous instructions.”
- An unexpected tool appears.
- Staging and Production targets conflict.
- CMDB target data is stale or ambiguous.
- Audit or policy service is unavailable.
- The kill switch is active.
- A model returns malformed or adversarial output.
- Memory suggests a superseded runbook.

---

## 23. Operations and Training

### 23.1 Daily

- Verify active/standby profile health.
- Verify MCP, policy, audit, model, RAG, and Mission Control health.
- Review denied tool/action events.
- Review pending memory/skill writes.
- Review approval timeouts and failed verification/rollback events.
- Confirm autonomy and kill-switch state.

### 23.2 Weekly

- Review success, latency, queue, token, and tool metrics.
- Review human overrides and agent disagreements.
- Verify state backup and replication.
- Review profile access, certificates, corpus changes, and stale sources.

### 23.3 Monthly/Quarterly

- Restore and failover test.
- Kill-switch test.
- Prompt-injection and red-team regression.
- Autonomy review per domain/runbook.
- MCP/tool source and supply-chain review.
- Model and dependency patch review.
- Memory/skills cleanup and access review.

Mandatory runbooks:

- Hermes Orchestrator unavailable.
- Profile gateway crash loop.
- Model endpoint unavailable/degraded.
- MCP or Policy Gateway outage.
- Audit write failure.
- Compromised profile.
- Credential leakage suspicion.
- Memory/skill poisoning.
- Runaway task/tool loop.
- Wrong-target action.
- Rollback failure.
- Mission Control outage.
- State database corruption.

---

## 24. RACI and Team

| Activity | Accountable | Responsible | Consulted |
|---|---|---|---|
| Agentic AI charter | Project Owner | Solution Architect | NOC, SOC, Facilities, Security, Change |
| Runtime and profiles | Solution Architect | Platform/SRE | AI Platform, Security |
| Tool/MCP Gateway | Solution Architect | Integration/MCP Team | CMDB, SIEM, Workflow, Security |
| Model/RAG | AI Platform Lead | AI/LLMOps Team | Domain SMEs, Security |
| Policy and approval | Security/Change Authority | Security + Workflow Team | Operations, Architect |
| Runbook execution | Change Manager | Workflow/SOAR Team | NOC/SOC/Facilities/SRE |
| Mission Control | Product Owner | Application Team | Operations, Security |
| Production promotion | Project Owner | Solution Architect/Release Manager | All authorities |
| Autonomy promotion | Project Owner | Domain Lead + Security + Change | AI Platform, Architect |

Minimum team guidance:

- 1 Solution/Agentic Architect.
- 2 Platform/SRE engineers.
- 1–2 AI Platform/LLMOps engineers.
- 2 Integration/MCP engineers.
- 1–2 Workflow/SOAR engineers.
- 1–2 Security engineers.
- 1–2 Mission Control/application engineers.
- 1–2 QA/automation engineers.
- Part-time NOC, SOC, Facilities, CMDB/Asset, and Change SMEs.

Indicative A0–A2 program: 22–33 weeks. A3 is incremental and certified per runbook.

---

## 25. Risk Register

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| AAI-01 | “Full control” interpreted as unrestricted privilege | Critical | Formal boundary and A5 prohibition |
| AAI-02 | Prompt injection creates unsafe plan | Critical | Content isolation, no direct actuator, policy and red team |
| AAI-03 | Wrong CI selected | Critical | Unique CMDB resolution, freshness, topology, impact, approval |
| AAI-04 | Approval bypass | Critical | External signed Policy/Approval Gateway |
| AAI-05 | Profile treated as a security sandbox | Critical | Dedicated container, identity, egress, and filesystem controls |
| AAI-06 | Local state used as active-active shared state | High | Active-passive profile pattern and external action state |
| AAI-07 | Memory/skill poisoning | High | Approval, signing, staging promotion, evidence link |
| AAI-08 | MCP exposes a new dangerous tool | High | Include list, manifest pinning, discovery alert |
| AAI-09 | LLM hallucination becomes action | Critical | Typed contract, deterministic validation, policy, approval |
| AAI-10 | Credential leakage in tool result | Critical | Brokered credentials, redaction, DLP |
| AAI-11 | Audit failure loses trace | Critical | Fail closed and immutable remote audit |
| AAI-12 | Human approval fatigue | High | Risk-based approval and per-runbook A3 certification |
| AAI-13 | OT action creates safety impact | Critical | No direct route, dual approval, safety interlocks, A1 default |
| AAI-14 | Model outage blocks operations | Medium | Core DCIM independence, fallback model, manual operations |
| AAI-15 | Mission Control becomes a backdoor | Critical | Read-mostly, separate protected approval/kill endpoints |
| AAI-16 | Supply-chain compromise | Critical | Pin, sign, SBOM, scan, internal registry |

---

## 26. Acceptance Criteria

### Architecture and Governance

- [ ] Human authority and approval matrix approved.
- [ ] A5 prohibited in policy and implementation.
- [ ] Reasoning, authorization, approval, execution, and verification are separate.
- [ ] Version 2 and existing documents remain unmodified.

### Runtime and Isolation

- [ ] Unique profile, identity, certificate, and toolset per Production agent.
- [ ] Dedicated container/process boundary, non-root, no Docker socket, no host credential inheritance.
- [ ] Active-passive failover and state restore tested.

### Tools and Evidence

- [ ] Typed schema-validated tools only.
- [ ] Separate Read and Action Request MCP planes with mTLS and include lists.
- [ ] Live state comes from tools, not memory-only.
- [ ] Every operational answer has source and timestamp.

### Policy and Execution

- [ ] Every action uses canonical `ActionRequest`.
- [ ] Target and impact validated against CMDB.
- [ ] Idempotency, expiry, concurrency, maintenance-window, and approval checks work.
- [ ] OT requires dual approval.
- [ ] Signed/versioned runbook and rollback exist.
- [ ] Kill switch and manual takeover tested.

### Security and Audit

- [ ] Memory and skill write approval enabled.
- [ ] Prompt/tool injection, replay, spoofing, exfiltration, and wrong-target tests pass.
- [ ] No direct root, raw SQL, generic actuator, or audit-disable tool.
- [ ] Immutable external audit is complete and blocks action when unavailable.
- [ ] No unresolved critical/high findings.

### Operational Quality

- [ ] Minimum 30-day shadow mode completed.
- [ ] Critical target-CI accuracy is 100% on the approved golden set.
- [ ] Unauthorized Production actions are zero.
- [ ] Rollback success is 100% for certified A3 runbooks.
- [ ] Core DCIM remains operational during Hermes outage.
- [ ] Operations, Security, Change, Facilities, and Product Owner sign-off complete.

---

## 27. Production Stop Conditions

Stop deployment or autonomy promotion when:

1. Hermes has direct privileged credentials or an OT route.
2. Arbitrary shell, raw SQL, or generic actuator tools are visible.
3. Policy or audit is not fail-closed.
4. CMDB cannot uniquely resolve critical targets.
5. Rollback is missing or untested.
6. Memory/skill writes are not approval-gated.
7. Profiles share secrets or writable state across environments.
8. Runtime isolation is not approved.
9. A3/A4 lacks replay and shadow certification.
10. Critical/high security findings remain open.
11. Human takeover or kill switch fails.
12. Core DCIM depends on Hermes for basic monitoring or safety.
13. Model, corpus, tool, policy, or runbook lacks version/checksum/owner/rollback.
14. Approval identity cannot be independently validated.
15. Production audit trace is incomplete.

---

## 28. Architecture Decision Records

| ADR | Decision |
|---|---|
| AAI-001 | Hermes is the Agentic Operations Control Plane, not an unrestricted actuator. |
| AAI-002 | Human authority remains highest. |
| AAI-003 | Workflow/SOAR is the only Production execution boundary. |
| AAI-004 | Read and Action Request tools are separated. |
| AAI-005 | Production MCP uses mTLS and explicit include lists. |
| AAI-006 | Profiles separate state; containers provide security isolation. |
| AAI-007 | Production profile state uses active-passive, not unsupported active-active writers. |
| AAI-008 | Memory and skill writes require approval. |
| AAI-009 | A0–A2 first; A3 per runbook; A4 separately approved; A5 prohibited. |
| AAI-010 | Deterministic analytics remains numerical authority. |
| AAI-011 | Model selection is replaceable and cannot alter the policy boundary. |
| AAI-012 | CMDB target and impact validation is mandatory before action. |
| AAI-013 | Actions are idempotent, expiring, versioned, verified, and reversible where possible. |
| AAI-014 | Audit unavailability blocks action. |
| AAI-015 | Mission Control is read-mostly and cannot patch Hermes state directly. |
| AAI-016 | Core DCIM operation must not depend on Hermes availability. |

---

## 29. Open Decisions

1. Authoritative ITSM/Change approval platform.
2. Policy engine selection: OPA, custom service, or workflow-native hybrid.
3. Primary Production model after Gemma versus Qwen bake-off.
4. First five A3 runbooks.
5. Session and audit retention by domain.
6. Production Hermes version and patch/support strategy.
7. Mission Control as a separate application or integrated DCIM Dashboard module.
8. Allowed Production messaging channels and user allowlist/pairing policy.
9. Whether Facilities/OT remains A1 for the first 12 months.
10. Break-glass process when approval services are unavailable during a critical incident.

---

## References

### DCIM

- Deployment & Implementation Plan v2 for Dev, Staging and Production.
- `concepts/multi-agent-structure.md`
- `reference-designs/block4-cmdb.md`
- `reference-designs/block6-siem-soc-v3.md`
- `reference-designs/siem-soar.md`
- `reference-designs/block7-analytics-ai-engine.md`
- `reference-designs/block8-workflow-automation.md`
- `reference-designs/staging-production-environment.md`
- `guides/deployment-implementation-guide.md`
- `product-description/dcim-core-platform-product-description.md`
- FIT041 Technical Requirements, Use Case Analysis, Baseline, SOP, and SLA documents.
- `hermes-dashboard-all-prompts.md`

### Hermes Runtime

- `https://github.com/NousResearch/hermes-agent`
- `https://hermes-agent.nousresearch.com/docs/user-guide/profiles`
- `https://hermes-agent.nousresearch.com/docs/user-guide/features/tools`
- `https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp`
- `https://hermes-agent.nousresearch.com/docs/user-guide/features/memory`
- `https://hermes-agent.nousresearch.com/docs/user-guide/security`

### Related Wiki Links

- [[multi-agent-structure]]
- [[workflow-automation]]
- [[security-architecture]]
- [[observability-strategy]]
- [[cmdb]]
- [[analytics-ai-engine]]

---

> **Final recommendation:** Implement Hermes as a supervisory, evidence-driven, and governed operations layer. Begin with A0/A1, promote to A2 after operational validation, certify A3 one runbook at a time, require explicit human approval for A4, and keep A5 disabled.
