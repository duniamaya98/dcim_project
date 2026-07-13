---
title: Change Management Process
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [workflow-automation, architecture]
sources: []
confidence: high
---

# Change Management Process

Change management untuk DCIM platform.

## Process

### Request
- Change request submission
- Impact analysis via [[cmdb]]
- Risk assessment
- Approval workflow

### Approval
- Multi-level approval
- CAB (Change Advisory Board) for major changes
- Emergency change process
- Rollback approval

### Implementation
- Change window scheduling
- Pre-change verification
- Change execution
- Post-change verification

### Review
- Success verification
- Documentation update
- Lessons learned
- CMDB update

## Change Types
- **Standard**: Pre-approved, low risk
- **Normal**: Requires approval
- **Emergency**: Expedited approval
- **Major**: CAB review required

## Integration
- CMDB impact → [[cmdb]]
- Approval → [[workflow-automation]]
- Notification → Email/Slack
- Audit → [[siem-soc]]

## Related
- [[dcim-core-platform]]
- [[cmdb]]
- [[workflow-automation]]
- [[incident-response-workflow]]
