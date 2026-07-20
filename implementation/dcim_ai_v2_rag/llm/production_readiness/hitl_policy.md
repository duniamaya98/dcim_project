# Human-in-the-loop Policy for DCIM Agent

## Approval Required

Human approval is mandatory for:

- Restarting service, server, network device, BMS connector, or collector.
- Power cycle through PDU, UPS path, breaker, or smart plug.
- Configuration change on network, power, cooling, monitoring, alert routing.
- Suppressing or muting alerts.
- Closing high or critical severity incident.
- Any action when SOP is missing, stale, ambiguous, or conflicts with live data.

## Default Approver Roles

| Risk | Approver |
|---|---|
| Low | NOC operator |
| Medium | DCIM engineer |
| High | SRE lead or DCIM lead |
| Critical | Incident commander plus domain owner |

## Approval Payload

Every approval request must include:

- `id`
- `requested_action_id`
- `approver_role`
- `reason`
- `risk`
- `evidence_ids`
- `expires_at`

## Timeout Behavior

- Low or medium risk approval timeout: escalate to next on-call.
- High or critical risk approval timeout: do not execute, update ticket, page
  incident commander.
- Expired approval must not be reused.

## Audit Trail

Persist these records:

- Prompt context hash.
- Model response raw JSON.
- Validation result.
- Tool call request and response.
- Approver identity and decision.
- Final incident outcome.
- Operator correction and SOP gap.
