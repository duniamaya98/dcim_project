---
title: LLM/RAG Explanation Layer
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [analytics-ai, architecture]
sources: []
confidence: high
---

# LLM/RAG Explanation Layer

LLM/RAG untuk natural language explanation di DCIM.

## Purpose
- Natural language explanation of anomalies
- Query interface untuk operators
- Context-aware recommendations
- Reduce cognitive load

## Implementation

### RAG Architecture
```
Query → Retriever → Context → LLM → Response
```

### Knowledge Sources
- [[cmdb]] — CI data, relationships
- Logs — historical events
- Runbooks — procedures
- Metrics — historical trends

### Use Cases
- "Why is this server alerting?"
- "What caused the outage yesterday?"
- "How do I fix this issue?"
- "What is the impact of this change?"

## Integration
- Query interface → [[web-dashboard]]
- Knowledge base → CMDB, logs, runbooks
- Response → Natural language + actions

## Metrics
- Query accuracy
- Response relevance
- User satisfaction
- Resolution time improvement

## Related
- [[dcim-core-platform]]
- [[analytics-ai-engine]]
- [[web-dashboard]]
- [[cmdb]]
