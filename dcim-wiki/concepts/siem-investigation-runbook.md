---
title: SIEM Investigation Runbook
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [siem-soc, sop-runbook]
sources: []
confidence: high
---

# SIEM Investigation Runbook

SIEM/SOC investigation procedures.

## Investigation Process

### 1. Alert Triage
- Review alert details
- Check severity/priority
- Identify affected systems
- Initial scope assessment

### 2. Data Collection
- Collect relevant logs
- Gather network data
- Review system metrics
- Check user activity

### 3. Analysis
- Timeline reconstruction
- Pattern analysis
- Correlation with other events
- Root cause identification

### 4. Response
- Containment actions
- Evidence preservation
- Stakeholder notification
- Documentation

## Common Investigation Patterns

### Brute Force Attack
```sql
-- Find failed login attempts
SELECT source_ip, COUNT(*) as attempts
FROM security_events
WHERE event_type = 'failed_login'
AND created_at > NOW() - INTERVAL '1 hour'
GROUP BY source_ip
HAVING COUNT(*) > 5;
```

### Data Exfiltration
```sql
-- Find unusual data transfers
SELECT destination_ip, SUM(bytes_sent) as total_bytes
FROM network_events
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY destination_ip
HAVING SUM(bytes_sent) > 1000000000;
```

### Unauthorized Access
```sql
-- Find access outside business hours
SELECT user_id, event_type, created_at
FROM access_events
WHERE EXTRACT(HOUR FROM created_at) NOT BETWEEN 8 AND 18
AND created_at > NOW() - INTERVAL '7 days';
```

## Evidence Handling
- Chain of custody
- Secure storage
- Documentation
- Legal requirements

## Escalation
- Level 1: SOC analyst
- Level 2: Security engineer
- Level 3: CISO

## Related
- [[siem-soc]]
- [[siem-correlation-rules]]
- [[incident-response-workflow]]
- [[compliance-framework]]
