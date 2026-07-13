---
title: Quality Gates
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [requirement, architecture]
sources: []
confidence: high
---

# Quality Gates

Checklist mandatory untuk setiap deliverable.

## 1. Requirement Gate
- Component identified
- Objective clear
- Scope defined
- Actors / source systems listed
- Functional requirements
- Non-functional requirements
- Integration points
- Security requirements
- Observability requirements
- Acceptance criteria
- Risks documented
- Open questions

## 2. Architecture Gate
- Context defined
- Component boundaries clear
- Data flow documented
- API/interface contract
- Storage model
- Failure modes analyzed
- HA/DR design
- Security design
- Monitoring/logging design
- Deployment model
- Trade-offs documented
- Decision record

## 3. SOP / Runbook Gate
- Purpose defined
- Scope limited
- Trigger identified
- Preconditions listed
- Roles/RACI assigned
- Step-by-step procedure
- Validation steps
- Rollback procedure
- Escalation path
- Logging/audit evidence
- Post-incident review

## 4. Build Gate
- Plan documented
- Files to change listed
- Backup approach
- Commands documented
- Tests defined
- Verification steps
- Rollback plan
- Known limitations

## Usage
- Applied to every phase deliverable
- Checked during review
- Blocker if not met

## Related
- [[dcim-core-platform]]
