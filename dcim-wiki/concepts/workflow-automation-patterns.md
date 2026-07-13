---
title: Workflow Automation Patterns
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [workflow-automation, architecture]
sources: []
confidence: high
---

# Workflow Automation Patterns

Patterns untuk workflow automation.

## Ticketing Pattern
```
Alert → Create Ticket → Assign → Track SLA → Close
```

## Approval Pattern
```
Request → Approve/Reject → Execute → Verify
```

## Runbook Pattern
```
Trigger → Execute Steps → Validate → Complete/Rollback
```

## Auto-Remediation Pattern
```
Alert → Check Guards → Execute Remediation → Verify → Close
```

## Escalation Pattern
```
Alert → Level 1 → Timeout → Level 2 → Timeout → Level 3
```

## Safety Guards
- Blast radius check
- Approval for critical actions
- Rollback capability
- Audit trail

## n8n / Temporal
- n8n: visual workflow builder
- Temporal: durable execution engine
- Choice depends on complexity

## Related
- [[workflow-automation]]
- [[workflow-state-machine]]
- [[dcim-core-platform]]
