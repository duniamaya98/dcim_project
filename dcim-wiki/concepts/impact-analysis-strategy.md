---
title: Impact Analysis Strategy
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [cmdb, architecture, reliability]
sources: []
confidence: high
---

# Impact Analysis Strategy

Impact analysis untuk CMDB topology.

## Purpose
- Understand CI dependencies
- Assess change impact
- Support incident response
- Capacity planning

## Implementation

### Graph Traversal
- BFS/DFS on relationship graph
- Depth limit: 5 levels
- Filter by relationship type

### Impact Scoring
- Direct impact: 1.0
- Indirect impact: 0.5 per level
- Aggregated impact score

### Visualization
- Interactive topology graph
- Impact radius highlighting
- Dependency path highlighting

## Use Cases

### Change Impact
- "What breaks if I change this CI?"
- Show dependent CIs and services

### Incident Impact
- "What is affected by this failure?"
- Show upstream and downstream impact

### Capacity Impact
- "What if this server fails?"
- Show service degradation

## API
- `GET /api/v1/cmdb/impact/{ci_id}`
- `GET /api/v1/cmdb/topology/{ci_id}`

## Related
- [[dcim-core-platform]]
- [[cmdb]]
- [[cmdb-data-model]]
