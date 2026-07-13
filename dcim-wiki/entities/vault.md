---
title: Vault
created: 2026-06-23
updated: 2026-06-23
type: entity
tags: [vault, security, infrastructure]
sources: []
confidence: high
---

# HashiCorp Vault

Secret management dan encryption untuk DCIM platform.

## Usage
- Secret storage: database credentials, API keys, tokens
- Dynamic credentials: short-lived database passwords
- Encryption as a service: transit engine
- Audit logging: all secret access logged

## Engines
- **KV**: static secrets (API keys, tokens)
- **Database**: dynamic PostgreSQL credentials
- **Transit**: encryption/decryption
- **PKI**: internal certificate management

## Integration
- Application auth: AppRole, Kubernetes
- CI/CD: token-based auth
- Monitoring: Prometheus metrics

## Related
- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[secret-management-comparison]]
