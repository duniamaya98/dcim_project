---
title: Service Mapping Strategy
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [cmdb, architecture]
sources: []
confidence: high
---

# Service Mapping Strategy

Service mapping untuk CMDB.

## Purpose
- End-to-end service dependency view
- Service health monitoring
- Impact analysis per service
- Capacity planning per service

## Implementation

### Service Definition
- Service: logical grouping of CIs
- Example: "Email Service" = App + Server + DB + Network

### Dependency Mapping
- Service → Application → Server → Network
- Graph-based traversal
- Dynamic updates from discovery

### Health Aggregation
- Service health = weighted average of CI health
- Critical path identification
- Redundancy detection

## Views
- Service topology graph
- Service health dashboard
- Service dependency matrix
- Service impact analysis

## Related
- [[dcim-core-platform]]
- [[cmdb]]
- [[impact-analysis-strategy]]
