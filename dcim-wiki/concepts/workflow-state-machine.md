---
title: Workflow State Machine
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [workflow-automation, architecture]
sources: []
confidence: high
---

# Workflow State Machine

State machine untuk workflow automation.

## States
```
pending → in_progress → waiting_approval → approved → executing → completed
    ↓           ↓              ↓              ↓           ↓
  cancelled   failed        rejected       failed      failed
```

## State Transitions

| From | To | Trigger |
|------|----|---------|
| pending | in_progress | Auto-assign or manual start |
| in_progress | waiting_approval | Approval required |
| in_progress | failed | Error or timeout |
| waiting_approval | approved | Approver action |
| waiting_approval | rejected | Approver action |
| approved | executing | Auto-trigger |
| executing | completed | Success |
| executing | failed | Error or timeout |
| any | cancelled | Manual cancellation |

## Configuration
- Custom states per workflow type
- Timeout handling
- State persistence
- Audit trail for all transitions

## Related
- [[dcim-core-platform]]
- [[workflow-automation]]
