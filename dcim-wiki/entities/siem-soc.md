---
title: SIEM/SOC
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [siem-soc, security, architecture]
sources: []
confidence: high
---

# SIEM/SOC Integration

Security event ingestion, correlation, incident response, dan compliance.

## Capabilities

### Security Event Ingestion
- Wazuh agent → Syslog → Kafka → Elasticsearch
- Source: servers, network devices, applications, cloud
- Normalized security event schema

### Correlation Engine
- Rule-based correlation
- Threshold alerts (e.g., 5 failed logins in 1 min)
- Pattern detection
- Cross-source correlation

### Incident Response Workflow
- Auto-create security incidents
- Severity classification
- Integration dengan [[workflow-automation]] untuk escalation
- Forensics data collection

### CIS Benchmark Compliance
- Automated compliance checks
- Gap analysis
- Remediation recommendations
- Compliance reporting

### SOC API
- Query security events
- Get incident status
- Update incident
- Export reports

## Architecture
```
Wazuh Agents → Syslog → Kafka → Elasticsearch → Correlation Engine → Alerts → Workflow Automation
```

## Phase 2 Tasks (Block 6)
- Security event ingestion (Wazuh/Syslog → Kafka → ES)
- Correlation engine
- Incident response workflow
- CIS benchmark compliance checks
- SOC API

## Related
- [[dcim-core-platform]]
- [[data-ingestion-integration]] — event pipeline
- [[elasticsearch]] — security event storage
- [[workflow-automation]] — incident escalation
- [[web-dashboard]] — SOC view
- [[siem-investigation-runbook]]
- [[siem-solution-comparison]]
