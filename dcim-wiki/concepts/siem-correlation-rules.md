---
title: SIEM Correlation Rules
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [siem-soc, security, architecture]
sources: []
confidence: high
---

# SIEM Correlation Rules

Correlation rules untuk SIEM/SOC integration.

## Rule Categories

### Authentication
- Failed login threshold (5 in 1 min)
- Brute force detection
- Impossible travel
- Privilege escalation

### Network
- Port scanning
- Data exfiltration
- Lateral movement
- Anomalous traffic

### System
- Service crash
- Configuration change
- Unauthorized access
- Malware detection

### Compliance
- CIS benchmark violations
- Policy violations
- Access control violations
- Data handling violations

## Rule Structure
```yaml
rule:
  name: "Failed Login Threshold"
  description: "Detect 5+ failed logins in 1 minute"
  severity: medium
  source: authentication
  condition:
    count: 5
    time_window: 1m
    group_by: source_ip
  action:
    - alert
    - log
    - block_ip (optional)
```

## Integration
- Rules defined in Elasticsearch or Wazuh
- Alerts sent to [[workflow-automation]]
- Incidents tracked in [[web-dashboard]]

## Related
- [[siem-soc]]
- [[elasticsearch]]
- [[workflow-automation]]
