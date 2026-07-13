---
title: Elasticsearch
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [elasticsearch, infrastructure]
sources: []
confidence: high
---

# Elasticsearch

Search dan analytics engine untuk logging dan SIEM.

## Version
- Elasticsearch 8.x / OpenSearch 2.x

## Usage
- Central logging: application logs, audit trails
- [[siem-soc]] data store: security events
- Full-text search untuk CMDB, logs
- Index lifecycle management (ILM)

## Index Strategy
- `dcim-logs-*` — application logs (7-day retention)
- `dcim-audit-*` — audit trails (90-day retention)
- `dcim-security-*` — security events (1-year retention)
- `dcim-metrics-*` — metrics (30-day retention)

## Related
- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[siem-soc]]
- [[elasticsearch-index-strategy]]
- [[log-management-comparison]]
