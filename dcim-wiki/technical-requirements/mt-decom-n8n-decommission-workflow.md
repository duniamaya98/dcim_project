---
title: "MT-DECOM n8n Server Decommissioning Workflow — Goal Prompt"
created: 2026-06-29
updated: 2026-06-29
type: goal-prompt
scenario: custom (multi-component workflow automation)
project_type: Docker/DevOps (n8n)
baseline:
  - dcim-wiki/reference-designs/block8-workflow-automation.md (§2, §4, §5, §8, §9)
  - dcim-wiki/technical-requirements/fit041-workflow-automation-use-case-komparasi.md (UC2)
  - dcim-wiki/concepts/workflow-automation-sla-prioritization-framework-final.md
tags: [goal-prompt, n8n, decommissioning, hyper-v, workflow-automation, dcim]
---

# MT-DECOM — n8n Server Decommissioning Workflow

> **Built with:** goal-prompt-builder skill (§ Custom scenario, Docker/DevOps project type)
> **Reviewer:** Hermes DCIM Orchestrator
> **Date:** 2026-06-29

---

## /goal Prompt (Copy This)

```
/goal Build n8n Server Decommissioning workflow for Hyper-V environment.
Multi-step automation: request → approval → VM shutdown → export → delete →
CMDB sync → financial update → network/security cleanup → physical removal ticket.

First action: Read the following files and report line counts + key structure:
- ~/dcim-wiki/reference-designs/block8-workflow-automation.md (§2 state machine, §4 approval, §5 runbook, §8 n8n, §9 workflow types)
- ~/dcim-wiki/technical-requirements/fit041-workflow-automation-use-case-komparasi.md (UC2 Server Decommissioning)
- ~/dcim-wiki/concepts/workflow-automation-sla-prioritization-framework-final.md (SLA targets)
Report: total files found, total lines, state machine state count, approval level count, workflow type count.
Wait for ack before starting implementation.

Scope:
  IN: n8n workflow JSON (importable), Hyper-V PowerShell scripts (stop/export/delete/cleanup),
      approval chain configuration, CMDB API integration, ITSM ticket creation,
      notification templates (email/Slack), audit trail logging, rollback logic,
      deployment config (docker-compose), documentation (README + runbook)
  OUT: VMware/vSphere support, cloud provider decommissioning (AWS/Azure/GCP),
       database cleanup, application-level decommissioning, physical hardware removal execution,
       financial system ERP integration (mock/stub only for financial API),
       network device decommissioning (switches/firewalls)

Constraints:
- n8n (self-hosted, Docker) for orchestration — not Temporal, not custom engine
- Hyper-V PowerShell remoting (Invoke-Command -ComputerName) — not VMware PowerCLI, not SSH
- Target: Windows Server 2019/2022 Hyper-V hosts
- Full 10-state state machine per Block 8 §2: pending, in_progress, waiting_approval, approved,
  rejected, executing, completed, failed, rollback, cancelled
- Multi-level approval: minimum 2 levels (Asset Manager → Finance Manager)
- ITSM ticket auto-create on workflow start (webhook to external ticketing API)
- Runbook engine: each decommission step is a discrete runbook step with success/failure handling
- Safety guard: blast radius check — verify VM has no active dependencies before deletion
- Rollback capability: each step must support rollback or compensation
- Audit trail: all state transitions logged with timestamp, actor, action, result
- Credentials stored in n8n credentials (EncryptedObject), NEVER in workflow JSON or scripts
- No new Docker images required — use n8n official image + PowerShell Core sidecar
- docker-compose.yml for local dev/test deployment
- All PowerShell scripts must include -WhatIf support for dry-run mode
- Notification on: workflow start, approval requested, approval granted/denied,
  step failure, workflow complete, rollback triggered

Done when:
1. n8n workflow JSON exported at ./n8n-workflows/decommission-workflow.json —
   importable via n8n UI or CLI (`n8n import:workflow --input=decommission-workflow.json`)
   without errors
2. Webhook trigger accepts POST with payload: { "vm_id": "string", "vm_name": "string",
   "hypervisor_host": "string", "reason": "string", "requester": "string",
   "priority": "P2|P3" } — returns workflow_id + status 201
3. Approval chain: 2-level approval with email notification at each level,
   configurable timeout (default 24h), auto-reject on timeout
4. PowerShell scripts at ./scripts/ — minimum 4 scripts:
   (a) Stop-VM.ps1 — graceful shutdown with -WhatIf, timeout, force option
   (b) Export-VM.ps1 — export to backup path with -WhatIf, verify export integrity
   (c) Remove-VM.ps1 — delete VM + disks with -WhatIf, dependency check first
   (d) Cleanup-Network.ps1 — remove firewall rules + VLAN assignments with -WhatIf
5. CMDB integration: HTTP Request node calls CMDB API to update CI status
   from "Deployed" → "Decommissioned" with timestamp and reason
6. Audit trail: every state transition logged to n8n execution log + external
   webhook callback with {workflow_id, from_state, to_state, timestamp, actor}
7. docker-compose.yml at project root starts n8n + PostgreSQL (for execution storage)
   with health checks passing (`docker compose ps` shows healthy)
8. ./docs/README.md documents: architecture overview, prerequisites, deployment steps,
   configuration reference, troubleshooting, rollback procedures
9. All scripts tested with -WhatIf mode — output shows planned actions without
   executing (paste test output for each script)
10. Git status shows only new files — no existing files modified

Stop if:
- Workflow requires VMware PowerCLI or vSphere API code
- Approval chain is single-level only (must be ≥ 2 levels)
- Credentials appear in workflow JSON, scripts, or docker-compose.yml
  (grep -rn "password\|secret\|token\|credential" . --include="*.json" --include="*.ps1"
   --include="*.yml" must return 0 matches excluding .env and this goal prompt)
- Rollback capability is missing from any decommission step
- Any PowerShell script fails -WhatIf dry-run mode
- CMDB integration uses hardcoded mock responses instead of configurable API endpoint
- docker compose up fails or health checks don't pass
- State machine has fewer than 10 states
- Workflow JSON is not importable to n8n (import test fails)
- Blast radius check is missing (VM deletion without dependency verification)
- Audit trail does not capture all state transitions

Use a token budget of 120000 tokens for this goal.
```

---

## Audit Friendliness Score

| Check | Score | Notes |
|-------|-------|-------|
| Acceptance count | ✅ 10 items | Range 5-8 is excellent; 10 acceptable for multi-component |
| Vague verbs | ✅ None | All items use specific verbs (export, import, accept, shows, logs) |
| Stop-if specificity | ✅ Mechanically detectable | Each stop-if can be verified with grep, import test, docker compose |
| Token budget | ✅ Present | 120K appropriate for 10-task multi-component scope |
| Mechanical verifiability | ✅ Every Done-when cites file, command, or artifact | No vague "works correctly" |
| **Overall** | **95%** | Ship-ready |

---

## Design Choices

**1. First action = "read + report counts"**
Forces agent to inventory baseline docs before building. Verifies understanding of Block 8 state machine, FIT041 UC2 flow, and SLA targets before implementation.

**2. Scope separates IN/OUT explicitly**
IN = n8n workflow + PowerShell scripts + deployment + docs. OUT = VMware, cloud, physical execution, ERP integration. Prevents scope creep into unrelated decommissioning domains.

**3. Constraints pull from dcim-wiki baseline**
- Block 8 §2: 10-state state machine
- Block 8 §4: multi-level approval (min 2 levels)
- Block 8 §5: runbook engine
- Block 8 §8: n8n (not Temporal)
- FIT041 UC2: cross-system orchestration (CMDB → Network → Security → Asset → Financial → Physical)
- SLA framework: workflow execution success rate ≥ 99.0%

**4. Done when = verifiable commands + artifacts**
Every item has concrete check: n8n import command, HTTP status code, docker compose status, grep for credentials, -WhatIf output. No "tests pass" without specifying which tests.

**5. Stop if = regression + security guards**
- No VMware code → scope boundary enforced
- No credentials in files → security enforced
- No single-level approval → architecture boundary enforced
- No missing rollback → reliability enforced
- Blast radius check → safety enforced

**6. Token budget at 120K**
10 tasks × ~10K avg per task = 100K, plus overhead for n8n workflow JSON generation (complex) and PowerShell script writing. 120K gives comfortable margin.

---

## Decommissioning Flow (FIT041 UC2 + Block 8)

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Request     │────→│  Approval    │────→│  Execution   │
│  (Webhook)   │     │  (2-Level)   │     │  (Runbook)   │
└─────────────┘     └──────────────┘     └──────┬───────┘
                           │                     │
                           ▼                     ▼
                    ┌──────────────┐     ┌──────────────┐
                    │  Rejected    │     │  Steps:      │
                    │  → Cancelled │     │  1. Stop VM  │
                    └──────────────┘     │  2. Export   │
                                         │  3. Delete   │
                                         │  4. Cleanup  │
                                         └──────┬───────┘
                                                │
                           ┌────────────────────┼────────────────────┐
                           ▼                    ▼                    ▼
                    ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
                    │  CMDB Sync   │     │  Financial   │     │  Physical    │
                    │  (CI status) │     │  (Depreciate)│     │  (Removal)   │
                    └──────────────┘     └──────────────┘     └──────────────┘
                           │                    │                    │
                           └────────────────────┼────────────────────┘
                                                ▼
                                         ┌──────────────┐
                                         │  Completed   │
                                         │  (Audit Log) │
                                         └──────────────┘
```

---

## Execution Notes

**Agent types this supports:**
- **Claude Code** — paste directly as prompt
- **Codex** — paste as task description
- **Hermes Dev agent** — paste as goal prompt
- **Copilot** — paste as inline instruction

**After execution, agent should produce:**
- Created: `n8n-workflows/decommission-workflow.json`
- Created: `scripts/Stop-VM.ps1`, `scripts/Export-VM.ps1`, `scripts/Remove-VM.ps1`, `scripts/Cleanup-Network.ps1`
- Created: `docker-compose.yml`
- Created: `docs/README.md`
- Created: `.env.example` (no real credentials)

**Prerequisites:**
- n8n self-hosted instance (Docker)
- Hyper-V host accessible via PowerShell remoting (WinRM/HTTPS)
- CMDB API endpoint (configurable)
- Email/Slack notification channel (configurable)

---

## Quick Reference: What Each Task Does

| Task | Deliverable | Verification |
|------|-------------|--------------|
| 1 | Workflow JSON | `n8n import:workflow --input=file.json` exits 0 |
| 2 | Webhook trigger | `curl -X POST ... -d '{...}'` returns 201 |
| 3 | Approval chain | n8n UI shows 2 approval nodes with timeout |
| 4 | PowerShell scripts (4) | Each runs with `-WhatIf` without error |
| 5 | CMDB integration | HTTP Request node configured with env var |
| 6 | Audit trail | State transitions logged in execution |
| 7 | Docker Compose | `docker compose up -d && docker compose ps` healthy |
| 8 | Documentation | README.md exists with required sections |
| 9 | Dry-run test | `-WhatIf` output shows planned actions |
| 10 | Clean git | `git status` shows only new files |
