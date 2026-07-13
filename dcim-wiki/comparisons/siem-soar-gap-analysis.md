---
title: "SIEM SOAR Gap Analysis"
created: 2026-06-25
updated: 2026-06-25
type: comparison
tags: [siem, soar, gap-analysis, wazuh, tracecat, dfir-iris]
purpose: >
  Perbandingan reference design SIEM SOAR dengan implementasi aktual.
  Gap = connection dots untuk improvement.
---

# SIEM SOAR Gap Analysis

> **Reference:** `siem-soar.md` (Reference Design Spec)
> **Actual:** `siem-soar-actual-architecture.md` (Current Implementation)
> **Date:** 2026-06-25

---

## Gap Comparison Matrix

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| **SOAR Platform** | TraceCat (self-hosted) | Tracecat | ✅ Match | — |
| **SIEM Stack** | Wazuh + ES + Kibana | LME (Wazuh + ES + Kibana + ElastAlert) | ✅ Match (+ElastAlert) | — |
| **Alert Bridge** | Kafka webhook | ElastAlert | ⚠️ Different | P2 |
| **Workflow Engine** | Temporal | Tracecat built-in | ⚠️ Different | P2 |
| **Case Management** | IRIS integration | DFIR-IRIS | ✅ Match | — |
| **AI Agent** | MCP (Claude Code, Codex) | Tracecat AI Agent | ⚠️ Different | P2 |
| **TIP Integration** | MISP + AbuseIPDB | AbuseIPDB + VirusTotal | ⚠️ Partial | P3 |
| **CMDB Integration** | Asset enrichment | ❌ Not implemented | ❌ Missing | P1 |
| **OT-Safe Playbooks** | Forbidden actions enforced | ❌ Not mentioned | ❌ Missing | P1 |
| **RBAC** | OIDC + Keycloak | ❌ Not mentioned | ❌ Missing | P1 |
| **Audit Trail** | Full action logging | ❌ Not mentioned | ❌ Missing | P1 |
| **Monitoring** | Prometheus + Grafana | ❌ Not mentioned | ❌ Missing | P2 |
| **HA/DR** | Docker Swarm (3 nodes) | ❌ Not specified | ❌ Missing | P1 |
| **Secret Management** | Vault | ❌ Not mentioned | ❌ Missing | P1 |
| **Notification** | Email + Slack + Teams | ❌ Not mentioned | ❌ Missing | P2 |

---

## Status Summary

### ✅ Match (4/15)
1. SOAR Platform — Tracecat
2. SIEM Stack — Wazuh + ES + Kibana
3. Case Management — DFIR-IRIS
4. Alert Flow — Agent → Manager → ES → Bridge → SOAR → ITSM

### ⚠️ Different Approach (4/15)
1. Alert Bridge — ElastAlert vs Kafka (simpler, less scalable)
2. Workflow Engine — Tracecat built-in vs Temporal (less robust)
3. AI Agent — Tracecat AI vs MCP (less flexible)
4. TIP — AbuseIPDB+VT vs MISP (less comprehensive)

### ❌ Not Implemented (7/15)
1. CMDB Integration — No asset enrichment
2. OT-Safe Playbooks — No enforcement for DCIM systems
3. RBAC — No OIDC/SSO integration
4. Audit Trail — No action logging
5. Monitoring — No Prometheus/Grafana for SOAR metrics
6. HA/DR — No high availability design
7. Secret Management — No Vault for API keys

---

## Recommendations

### P1 (Critical — must implement)
1. CMDB Integration — enrich alerts with asset context
2. OT-Safe Playbooks — enforce rules for DCIM systems
3. RBAC — implement OIDC/SSO
4. Audit Trail — log all actions for compliance
5. HA/DR — minimum 2 replicas for production

### P2 (Important — soon)
6. Monitoring — Prometheus + Grafana for SOAR metrics
7. Secret Management — HashiCorp Vault for API keys
8. Notification — Email/Slack/Teams integration

### P3 (Nice to have)
9. MISP integration — for more comprehensive threat intel
10. MCP integration — for more flexible AI agent

---

## Decision

**Approach:** Hybrid
**Rationale:** Current stack works well for core flow. Main gaps in security hardening (RBAC, audit, secrets) and operational maturity (monitoring, HA/DR, CMDB).
**Action items:** Prioritize P1 gaps for production readiness.
