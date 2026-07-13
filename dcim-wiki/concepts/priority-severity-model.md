---
title: Priority & Severity Model
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [requirement, architecture]
sources: []
confidence: high
---

# Priority & Severity Model

Standar prioritas untuk data, CI, aset, dan insiden.

## Data / Asset / CI Priority

| Priority | Meaning | Operational Effect |
|----------|---------|-------------------|
| P1 Critical | Outage or safety impact | Must be real-time or near-real-time |
| P2 High | Significant service degradation | Fast sync and high accuracy required |
| P3 Medium | Planning, audit, reporting impact | Batch acceptable |
| P4 Supporting | Historical/reference support | Async or scheduled processing acceptable |

## Incident Severity

| Severity | Meaning | Default Response |
|----------|---------|-----------------|
| S1 Critical | Total failure or P1 source failure | Immediate triage and escalation |
| S2 High | P2 failure or major performance degradation | Fast owner assignment |
| S3 Medium | Persistent latency, sync issue, minor data integrity issue | Planned remediation |
| S4 Low | Ad-hoc report, minor request, question | Normal queue |

## Usage
- [[data-ingestion-integration]]: route events by priority
- [[workflow-automation]]: escalation rules by severity
- [[web-dashboard]]: display by priority/severity
- [[siem-soc]]: security incident classification

## Related
- [[dcim-core-platform]]
- [[workflow-automation]]
