---
title: Integration Patterns
created: 2026-06-23
updated: 2026-06-23
type: concept
tags: [architecture, external-integration]
sources: []
confidence: high
---

# Integration Patterns

Patterns untuk integrasi di DCIM platform.

## Adapter Pattern
- Per-system adapter for [[external-integration]]
- Normalizer:统一 data format
- Error handling: DLQ + retry
- Health monitoring

## Event-Driven Pattern
- Kafka as event backbone
- Pub/sub for decoupling
- Event sourcing for audit

## API Gateway Pattern
- Single entry point
- Authentication/authorization
- Rate limiting
- Request routing

## Circuit Breaker Pattern
- Prevent cascade failures
- Fallback behavior
- Health check integration

## Retry Pattern
- Exponential backoff
- Max retry limit
- Dead letter queue
- Idempotency support

## Related
- [[dcim-core-platform]]
- [[external-integration]]
- [[data-ingestion-integration]]
- [[kafka]]
