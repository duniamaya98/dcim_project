# Wiki Schema

## Domain
DCIM Core Platform — Data Center Infrastructure Management untuk visibility, control, automation, analytics, dan audit. Mencakup DI&I, CMDB, Asset Repository, Analytics & AI, Workflow Automation, SIEM/SOC, Dashboard, dan integrasi eksternal (ITSM/ERP/DMS).

## Conventions
- File names: lowercase, hyphens, no spaces (e.g., `cmdb-data-model.md`)
- Every wiki page starts with YAML frontmatter
- Use `[[wikilinks]]` to link between pages (minimum 2 outbound links per page)
- When updating a page, always bump the `updated` date
- Every new page must be added to `index.md` under the correct section
- Every action must be appended to `log.md`
- **Provenance markers:** On pages synthesizing 3+ sources, append `^[raw/articles/source-file.md]` at the end of paragraphs whose claims trace to a specific source
- Language: Bahasa Indonesia; technical terms (component names, protocols, tools) tetap English

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
confidence: high | medium | low
contested: true
contradictions: [other-page-slug]
---
```

### raw/ Frontmatter
```yaml
---
source_url: https://example.com/article
ingested: YYYY-MM-DD
sha256: <hex digest of body>
---
```

## Tag Taxonomy

### Components
- dii (Data Ingestion & Integration)
- cmdb
- asset-repository
- analytics-ai
- workflow-automation
- siem-soc
- dashboard
- external-integration

### Infrastructure
- postgresql
- redis
- kafka
- nifi
- elasticsearch
- prometheus
- grafana
- vault
- docker
- kubernetes

### Architecture
- ha-dr
- data-quality
- security
- reliability
- observability
- performance

### Process
- requirement
- architecture
- sop-runbook
- implementation
- testing
- deployment
- operation

### Meta
- comparison
- timeline
- decision-record
- risk

## Page Thresholds
- **Create a page** when an entity/concept appears in 2+ sources OR is central to one block of the DCIM project
- **Add to existing page** when a source mentions something already covered
- **DON'T create a page** for passing mentions, minor details, or things outside the domain
- **Split a page** when it exceeds ~200 lines
- **Archive a page** when its content is fully superseded

## Entity Pages
One page per notable entity (component, tool, service, integration point). Include:
- Overview / what it is
- Key facts, versions, configuration
- Relationships to other entities ([[wikilinks]])
- Source references

## Concept Pages
One page per concept or topic. Include:
- Definition / explanation
- Current state of knowledge in this project
- Open questions or debates
- Related concepts ([[wikilinks]])

## Comparison Pages
Side-by-side analyses. Include:
- What is being compared and why
- Dimensions of comparison
- Verdict or synthesis
- Sources

## Priority Model
- P1 Critical: outage/safety, real-time requirement
- P2 High: significant degradation, fast sync
- P3 Medium: planning/audit/reporting, batch acceptable
- P4 Supporting: historical/reference, async acceptable

## Incident Severity
- S1 Critical: total failure or P1 source failure → immediate triage
- S2 High: P2 failure or major degradation → fast assignment
- S3 Medium: persistent latency/sync issue → planned remediation
- S4 Low: ad-hoc report/question → normal queue

## Update Policy
When new information conflicts with existing content:
1. Check dates — newer sources generally supersede older
2. If contradictory, note both positions with dates and sources
3. Mark contradiction in frontmatter: `contradictions: [page-name]`
4. Flag for user review in lint report
