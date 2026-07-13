---
title: Multi-Agent Structure
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [requirement, architecture]
sources: []
confidence: high
---

# Multi-Agent Structure

Agent system untuk DCIM platform development.

## Roles

### Orchestrator (Hermes)
- System coherence
- Work routing
- Ambiguity resolution
- Architecture consistency
- Cross-component decisions
- Quality gates
- Recovery planning

### Scout — Research & Source Intelligence
- Standards, tools, vendor research
- Best practices validation
- Alternative comparison
- DCIM: DCIM platforms, CMDB/NetBox, Kafka, NiFi, Telegraf, Wazuh, Grafana, n8n

### Scribe — Documentation & Knowledge Engineering
- HLD, LLD, SOP, SLA
- Requirements, use cases, acceptance criteria
- Runbooks, meeting notes
- DCIM: project documentation

### Reach — Stakeholder, Strategy & Delivery Planning
- Roadmap, prioritization
- Adoption plan
- Stakeholder briefs
- 30/60/90-day plans

### Dev — Engineering, Automation & Integration
- Scripts, APIs, dashboards
- Data pipelines
- Automation workflows
- DCIM: Kafka/NiFi/Flink, REST APIs, Python/Go

## Routing Rules
- Source research → Scout
- Documentation → Scribe
- Strategy/roadmap → Reach
- Code/automation → Dev
- Cross-component/architecture → Orchestrator

## Related
- [[dcim-core-platform]]
