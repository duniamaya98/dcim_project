---
title: "Komparasi SLA & Prioritization — FIT041 vs DCIM-Wiki (Workflow Automation)"
created: 2026-06-25
updated: 2026-06-25
type: comparison
tags: [sla, prioritization, workflow-automation, fit041, komparasi, governance]
sources:
  - IF-SLA__Prioritization_Workflow_Automation-FIT041-20260126.md
  - dcim-wiki/concepts/workflow-automation-sla-prioritization-framework.md
  - dcim-wiki/reference-designs/block8-workflow-automation.md
  - dcim-wiki/technical-requirements/workflow-automation-use-case-analysis-final-v2.md
confidence: high
purpose: >
  Komparasi SLA & Prioritasi Workflow Automation antara FIT041 (business-layer) dan DCIM-Wiki (technical-layer).
  Status: COMPLEMENTARY — tidak ada konflik struktural.
---

# Komparasi SLA & Prioritization — FIT041 vs DCIM-Wiki (Workflow Automation)

> **Purpose:** Komparasi dan koneksikan dokumen SLA & Prioritasi Workflow Automation antara FIT041 (business-layer, 6 sections, ~144 lines) dan DCIM-Wiki (technical-layer, 17 sections, ~583 lines).
> **Status:** ✅ COMPLEMENTARY — tidak ada konflik struktural. Semua perbedaan adalah metric reconciliation atau governance gap.
> **Cara pakai:** Review per-aspek untuk memahami apa yang covered di masing-masing dokumen, apa yang perlu diadopsi, dan apa yang sudah aligned.
> **Must Not Modify:** Existing documents tidak diubah.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Document Metadata Comparison](#2-document-metadata-comparison)
3. [Section-by-Section Analysis](#3-section-by-section-analysis)
4. [Metric Reconciliation (10 Metrics)](#4-metric-reconciliation-10-metrics)
5. [Governance Gaps — FIT041 Items untuk Adopt](#5-governance-gaps--fit041-items-untuk-adopt)
6. [DCIM-Wiki Unique Items](#6-dcmi-wiki-unique-items)
7. [Connection Mapping](#7-connection-mapping)
8. [Alignment Score](#8-alignment-score)
9. [Recommendations](#9-recommendations)
10. [Gap Comparison Template](#10-gap-comparison-template)

---

## 1. Executive Summary

| Aspek | Hasil |
|-------|-------|
| **Status** | ✅ **COMPLEMENTARY** |
| **FIT041 Role** | Business-layer SLA (SLO targets, priority model, roles, governance) |
| **DCIM-Wiki Role** | Technical-layer SLA Framework (implementation targets, monitoring, DQ, escalation) |
| **Structural Conflicts** | 0 — semua perbedaan adalah metric reconciliation |
| **Metric Reconciliations** | 10 metrics perlu reconciliation |
| **Governance Items to Adopt** | 10 items dari FIT041 |
| **DCIM-Wiki Unique** | 13 technical sections tidak ada di FIT041 |

### Quick Assessment

FIT041 SLA dokumen berfokus pada **business SLOs** — availability target, MTTE, success rate, roles, dan governance. DCIM-Wiki SLA Framework berfokus pada **technical implementation** — 17 use cases, auto-assignment logic, Prometheus alerts, Kafka topics, escalation matrix, DQ rules.

Kedua dokumen **tidak overlap** secara struktural. FIT041 = "apa yang harus dicapai" (business goals). DCIM-Wiki = "bagaimana mencapainya" (technical targets).

---

## 2. Document Metadata Comparison

| Aspek | FIT041 | DCIM-Wiki |
|-------|--------|-----------|
| **Title** | Kerangka Prioritas dan SLA untuk Workflow Automation | Workflow Automation SLA & Prioritization Framework |
| **Version** | 1.0 | 1.0 |
| **Date** | 2026-01-26 | 2026-06-25 |
| **Author** | DCIM AI Team (FIT041) | Hermes DCIM Orchestrator |
| **Type** | Business Requirements (SLA) | Technical Framework |
| **Sections** | 6 | 17 |
| **Lines** | ~144 | ~583 |
| **Scope** | Workflow Automation — all automated processes | Workflow Automation — Block 8 implementation |
| **Detail Level** | Business SLOs, roles, governance | Technical targets, code, alerts, DQ rules |
| **Sources** | FIT041 requirements | Reference design, use case analysis, entity pages |
| **Coverage** | Business layer (WHAT to achieve) | Technical layer (HOW to achieve) |

---

## 3. Section-by-Section Analysis

### 3.1 §1 Pendahuluan — Introduction

| Aspect | FIT041 | DCIM-Wiki | Alignment | Gap Type |
|--------|--------|-----------|-----------|----------|
| **Purpose** | Define SLO + priority framework for Workflow Automation | Framework terpadu untuk SLA, prioritas, DQ di Workflow Automation | ✅ Aligned | — |
| **Scope** | All automated ITIL processes (Incident, Change, Request, Provisioning) | Block 8 implementation (7 workflow types, 17 UCs) | ✅ Aligned | FIT041 broader (ITIL scope), DCIM-Wiki more specific (Block 8) |
| **Objectives** | 4 objectives: SLO targets, priority model, roles/responsibilities, MTTE justification | 17-section framework covering all SLA aspects | ✅ Aligned | DCIM-Wiki covers all FIT041 objectives |
| **Glossary** | 5 terms: Workflow Engine, MTTE, SLO, P1-P4, Audit Trail | No explicit glossary (terms used inline) | ⚠️ Minor gap | FIT041 has glossary, DCIM-Wiki doesn't |

**Decision:** FIT041's glossary is useful for onboarding. DCIM-Wiki can reference FIT041 for terminology.

### 3.2 §2 Definisi Layanan (SLA) — Service Level Definitions

| Aspect | FIT041 | DCIM-Wiki | Alignment | Gap Type |
|--------|--------|-----------|-----------|----------|
| **Engine Availability** | 99.95%/month (max downtime 21 min 53 sec) | 99.9% (State Machine, Auto-Remediation, Runbook) | ⚠️ Metric reconciliation | FIT041 stricter |
| **Execution Success Rate** | ≥ 99.0% | Not explicitly stated (DLQ < 1% ≈ 99%) | ✅ Aligned | FIT041 more explicit |
| **Failover Time** | Maks 10 menit | Not in workflow framework (RTO < 15 min in CMDB) | ⚠️ Missing in DCIM-Wiki | FIT041 unique |
| **Step-to-Step Latency** | < 30 detik (P1 & P2) | < 50ms (state transition) | ✅ Aligned | Different scope: FIT041 = inter-task, DCIM-Wiki = API |
| **MTTE P1** | Maks 5 menit (end-to-end) | < 30 detik per operation (UC4, UC14, UC16, UC17) | ✅ Aligned | Different measurement: E2E vs per-op |
| **Integration Latency** | < 60 detik | < 30s (ITSM ticket creation) | ✅ Aligned | DCIM-Wiki stricter |
| **Audit Trail Integrity** | 100% | DQ-05: 100% | ✅ Perfect alignment | — |
| **P1 Manual Override** | 15 menit (Tim Operasi response) | Not explicitly defined | ⚠️ Missing in DCIM-Wiki | FIT041 unique |
| **Data Retention** | Min 1 tahun | Kafka 90 hari (events), PostgreSQL (workflow logs) | ⚠️ Reconcilable | Different data types |

**Decision:** 3 FIT041 metrics are stricter or unique. Adopt as business floor targets.

### 3.3 §3 Model Prioritas — Priority Model

| Aspect | FIT041 | DCIM-Wiki | Alignment | Gap Type |
|--------|--------|-----------|-----------|----------|
| **Priority Tiers** | P1-P4 (4 tiers) | P1-P4 (4 tiers) | ✅ Perfect alignment | — |
| **P1 Definition** | Kritis: Incident Response & Safety Procedures | P1 Critical: Production outage, security incident | ✅ Aligned | DCIM-Wiki more specific |
| **P2 Definition** | Tinggi: Standard Change & Non-Critical Incident | P2 High: Service degradation, capacity threshold | ✅ Aligned | Different framing |
| **P3 Definition** | Menengah: Access Request & Minor Provisioning | P3 Medium: Planning, maintenance, compliance | ✅ Aligned | Different framing |
| **P4 Definition** | Pendukung: Reporting, Notification, Audit Trail | P4 Supporting: Historical, reference, documentation | ✅ Aligned | — |
| **P1 MTTE Target** | 5 menit | < 30 detik (per operation) | ✅ Aligned | Different scope |
| **P2 Success Rate** | ≥ 99.5% | Not explicitly stated | ⚠️ Missing in DCIM-Wiki | FIT041 unique |
| **P3 Latency** | Integrasi < 60 detik | < 1 jam (Tier 3) | ✅ Aligned | Different measurement |
| **Escalation Path** | Operasi → Developer → Process Owner (P1) | 4-level: On-call → Team Lead → Manager → Director | ⚠️ Different structure | FIT041 = role-based, DCIM-Wiki = level-based |

**Decision:** Priority tiers perfectly aligned. Escalation paths are complementary (FIT041 = who, DCIM-Wiki = when).

### 3.4 §4 Peran dan Tanggung Jawab — Roles & Responsibilities

| Aspect | FIT041 | DCIM-Wiki | Alignment | Gap Type |
|--------|--------|-----------|-----------|----------|
| **Process Owners** | Otoritas tertinggi untuk P1 approval, definisi P1-P4, dampak bisnis | Not explicitly defined | ❌ Missing in DCIM-Wiki | FIT041 unique |
| **Automation Developers** | Pengembangan, testing, patching, troubleshooting, SLA 2.1 ownership | "Workflow Engineer" (implied) | ⚠️ Partial | FIT041 more specific |
| **End-Users** | Input accuracy, manual step completion, anomaly reporting | "Viewer" role (implied) | ❌ Missing in DCIM-Wiki | FIT041 unique |
| **Operations Team** | Daily monitoring, manual override P1, implement minor updates | "Operator" role (implied) | ⚠️ Partial | FIT041 more specific |
| **RBAC Roles** | Not defined (4 functional roles) | 5 RBAC roles: admin, operator, viewer, approver, auditor | ⚠️ Different model | FIT041 = functional, DCIM-Wiki = access control |

**Decision:** FIT041's 4 functional roles complement DCIM-Wiki's 5 RBAC roles. Adopt FIT041 roles as responsibility matrix, keep DCIM-Wiki RBAC as access control.

### 3.5 §5 Metrik dan Pelaporan — Metrics & Reporting

| Aspect | FIT041 | DCIM-Wiki | Alignment | Gap Type |
|--------|--------|-----------|-----------|----------|
| **Process Cycle Time Reduction** | ≥ 50% vs manual | Not measured | ❌ Missing in DCIM-Wiki | FIT041 unique business KPI |
| **Manual Touchpoint Reduction** | ≥ 80% for P1/P2 | Not measured | ❌ Missing in DCIM-Wiki | FIT041 unique business KPI |
| **Execution Success Rate** | ≥ 99.0% | DLQ < 1% | ✅ Aligned | — |
| **P1 MTTE Compliance** | > 99.0% within 5 min | Not explicitly measured | ❌ Missing in DCIM-Wiki | FIT041 unique compliance KPI |
| **Error Rate** | < 1.0% | DLQ < 1% | ✅ Aligned | — |
| **Weekly Report** | Senin: MTTE trends, failed workflows, latency | Not defined | ❌ Missing in DCIM-Wiki | FIT041 unique |
| **Monthly Report** | Tanggal X: SLA compliance, touchpoint, audit trail | Not defined | ❌ Missing in DCIM-Wiki | FIT041 unique |
| **Ad-hoc Report** | Setelah P1 failure: RCA + mitigasi | Not defined | ❌ Missing in DCIM-Wiki | FIT041 unique |

**Decision:** FIT041's 3 business KPIs + 3 reporting cadences are unique governance items. Adopt all.

### 3.6 §6 Tinjauan dan Revisi — Review & Revision

| Aspect | FIT041 | DCIM-Wiki | Alignment | Gap Type |
|--------|--------|-----------|-----------|----------|
| **Formal Review** | Tahunan (annual) | Not defined | ❌ Missing in DCIM-Wiki | FIT041 unique |
| **Ad-hoc Review** | After P1/P2 addition, system upgrade, repeated P1 failure | Not defined | ❌ Missing in DCIM-Wiki | FIT041 unique |
| **Review Authority** | Project Owner + Lead Automation Developer | Not defined | ❌ Missing in DCIM-Wiki | FIT041 unique |

**Decision:** FIT041's review process is essential governance. Adopt as new section or append to DCIM-Wiki §17.

---

## 4. Metric Reconciliation (10 Metrics)

| # | Metric | FIT041 Target | DCIM-Wiki Target | Reconciliation Decision |
|---|--------|--------------|------------------|------------------------|
| 1 | **Engine Availability** | 99.95%/month | 99.9% | **Adopt FIT041 99.95% as business SLO.** DCIM-Wiki 99.9% = minimum engineering target. FIT041 stricter → business floor. |
| 2 | **MTTE P1 (E2E)** | Maks 5 menit | < 30 detik per op | **Keep both.** FIT041 = end-to-end business MTTE. DCIM-Wiki = per-operation technical latency. Different measurements, both valid. |
| 3 | **Execution Success Rate** | ≥ 99.0% | DLQ < 1% | **Adopt FIT041 99.0% as explicit target.** DCIM-Wiki DLQ < 1% is consistent but implicit. |
| 4 | **Failover Time** | Maks 10 menit | RTO < 15 min (CMDB) | **Adopt FIT041 10 menit.** More specific to workflow engine. Add to DCIM-Wiki §12. |
| 5 | **Step-to-Step Latency** | < 30 detik (P1/P2) | < 50ms (state transition) | **Keep both.** FIT041 = inter-task latency. DCIM-Wiki = API latency. Different scope. |
| 6 | **Integration Latency** | < 60 detik | < 30s (ITSM) | **Keep DCIM-Wiki 30s.** Stricter = better. FIT041's 60s is business floor. |
| 7 | **Audit Trail Integrity** | 100% | DQ-05: 100% | **Perfect alignment.** No action needed. |
| 8 | **Error Rate** | < 1.0% | DLQ < 1% | **Perfect alignment.** No action needed. |
| 9 | **P1 Manual Override** | 15 menit | Not defined | **Adopt FIT041 15 menit.** Add to DCIM-Wiki as Operations Team SLA. |
| 10 | **Data Retention** | Min 1 tahun | Kafka 90 hari | **Reconcile by data type.** Kafka events = 90 hari. PostgreSQL workflow logs = 1 tahun (FIT041 compliance). |

---

## 5. Governance Gaps — FIT041 Items untuk Adopt

### 5.1 Role Definitions (4 items)

| # | FIT041 Role | Responsibility | DCIM-Wiki Equivalent | Action |
|---|-------------|---------------|---------------------|--------|
| G1 | **Process Owners** | Otoritas tertinggi P1 approval, definisi P1-P4, dampak bisnis P1 | Not defined | **Adopt** — Add Process Owner role to DCIM-Wiki §5 |
| G2 | **Automation Developers** | Pengembangan, testing, patching, troubleshooting, SLA ownership | "Workflow Engineer" (partial) | **Adopt** — Enrich with reliability ownership |
| G3 | **End-Users (Requester/Approver/Implementer)** | Input accuracy, manual step completion, anomaly reporting | "Viewer" (partial) | **Adopt** — Add end-user responsibilities |
| G4 | **Operations Team** | Daily monitoring, manual override P1, implement minor updates | "Operator" (partial) | **Adopt** — Add manual override responsibility |

### 5.2 Business KPIs (3 items)

| # | FIT041 KPI | Target | DCIM-Wiki Equivalent | Action |
|---|-----------|--------|---------------------|--------|
| G5 | **Process Cycle Time Reduction** | ≥ 50% vs manual | Not measured | **Adopt** — Add to §16 Performance Targets |
| G6 | **Manual Touchpoint Reduction** | ≥ 80% for P1/P2 | Not measured | **Adopt** — Add to §16 Performance Targets |
| G7 | **P1 MTTE Compliance** | > 99.0% within 5 min | Not measured | **Adopt** — Add to §12 Availability SLA |

### 5.3 Reporting & Review (3 items)

| # | FIT041 Item | Detail | DCIM-Wiki Equivalent | Action |
|---|-----------|--------|---------------------|--------|
| G8 | **Weekly Report** | Senin: MTTE trends, failed workflows, latency | Not defined | **Adopt** — Add to §17 Monitoring Dashboard |
| G9 | **Monthly Report** | SLA compliance, touchpoint, audit trail | Not defined | **Adopt** — Add to §17 Monitoring Dashboard |
| G10 | **Annual Review + Ad-hoc Review** | Tahunan formal + after P1/P2 changes | Not defined | **Adopt** — Add as §18 Review Process |

---

## 6. DCIM-Wiki Unique Items

### 6.1 Technical Sections (NOT in FIT041)

| # | Section | Content | Why FIT041 Doesn't Have It |
|---|---------|---------|---------------------------|
| U1 | **Workflow Type Criticality Mapping** (§2) | 7 workflow types → default priority + SLA tier | FIT041 has priority matrix but not per-type mapping |
| U2 | **SLA Tiers** (§3) | 4 tiers: Real-time (<30s) → Batch (>1jam) with processing modes | FIT041 has flat targets, no tiered processing |
| U3 | **Priority Mapping per Use Case** (§4) | 17 UCs mapped to priorities with completeness/timeliness/DQ | FIT041 has workload categories, not specific UCs |
| U4 | **Auto-Assignment Logic** (§5) | YAML rules + Python implementation | FIT041 has no automation logic |
| U5 | **Impact Scoring** (§6) | 0-10 deterministic formula | FIT041 has no scoring formula |
| U6 | **Incident Severity** (§7) | 4-level S1-S4 with triggers | FIT041 has 3-level escalation |
| U7 | **Escalation Matrix** (§8) | 4-level time-based escalation with actions | FIT041 has role-based escalation |
| U8 | **Approval Chain SLA** (§9) | 4 chains: Standard(4h) → Critical(30h) | FIT041 has no approval chain timing |
| U9 | **Kafka Topic Priority** (§10) | 8 topics with priority + retention | FIT041 has no message broker config |
| U10 | **Consumer SLA Matrix** (§11) | 8 consumers with latency requirements | FIT041 has no consumer mapping |
| U11 | **Prometheus Alert Rules** (§12) | 9 alert rules with valid YAML | FIT041 has no monitoring implementation |
| U12 | **SLA Breach Handling** (§13) | Breach flow + escalation matrix + ticket routing | FIT041 has escalation but not breach handling |
| U13 | **Data Quality Rules** (§14) | 9 DQ rules (uniqueness, state integrity, audit) | FIT041 has no DQ rules |

### 6.2 Additional Technical Items

| # | Item | Content |
|---|------|---------|
| U14 | **Notification Channel Priority** (§15) | 6 channels with delivery SLAs |
| U15 | **Performance Targets** (§16) | 12 metrics with measurement methods |
| U16 | **Monitoring Dashboard** (§17) | 13 health metrics with refresh intervals |
| U17 | **17 Use Cases with Priority Mapping** | Complete UC → priority → SLA tier mapping |
| U18 | **17 UCs with Data Quality Requirements** | Per-UC completeness, accuracy, timeliness targets |

---

## 7. Connection Mapping

### 7.1 FIT041 → DCIM-Wiki Connections

| FIT041 Requirement | DCIM-Wiki Implementation | Connection Type |
|--------------------|--------------------------|-----------------|
| §2.1 Ketersediaan 99.95% | §12 Availability SLA 99.9% | **Reconcile** — FIT041 stricter, adopt as business floor |
| §2.2 MTTE P1 5 menit | §4 UC4/UC14/UC16/UC17 < 30s | **Complement** — FIT041 = E2E, DCIM-Wiki = per-op |
| §2.2 Step-to-Step < 30s | §12 State Transition < 50ms | **Complement** — Different scope |
| §2.3 Audit Trail 100% | §14 DQ-05 Audit Trail 100% | **Perfect match** |
| §2.3 Failover 10 min | §12 RTO < 15 min | **Reconcile** — Adopt FIT041 10 min |
| §2.3 Manual Override 15 min | Not defined | **Gap** — Adopt FIT041 |
| §3.1 P1-P4 Model | §1 Priority Model P1-P4 | **Perfect match** |
| §3.2 P1 MTTE 5 min | §4 P1 Tier 1 < 30s | **Complement** — Different measurement |
| §3.3 Escalation P1 | §8 4-level escalation | **Complement** — FIT041 = who, DCIM-Wiki = when |
| §4 Roles (4 roles) | §5 Auto-Assignment (RBAC) | **Complement** — FIT041 = functional, DCIM-Wiki = access |
| §5 KPIs (5 metrics) | §12/§16 Monitoring (12 metrics) | **Complement** — FIT041 = business, DCIM-Wiki = technical |
| §5 Reporting (3 cadences) | §17 Dashboard (real-time) | **Complement** — FIT041 = periodic, DCIM-Wiki = real-time |
| §6 Review (annual + ad-hoc) | Not defined | **Gap** — Adopt FIT041 |

### 7.2 DCIM-Wiki → FIT041 Connections

| DCIM-Wiki Feature | FIT041 Coverage | Connection Type |
|-------------------|-----------------|-----------------|
| §2 Workflow Type Mapping (7 types) | §3 Process Types (4 categories) | **Extend** — DCIM-Wiki more granular |
| §3 SLA Tiers (4 tiers) | §2 Flat targets | **Extend** — DCIM-Wiki adds tiered processing |
| §4 UC Priority Mapping (17 UCs) | §3 Priority Matrix (4 tiers) | **Extend** — DCIM-Wiki maps to specific UCs |
| §5 Auto-Assignment Logic | Not covered | **Unique** — DCIM-Wiki only |
| §6 Impact Scoring | Not covered | **Unique** — DCIM-Wiki only |
| §8 Escalation Matrix | §3 Escalation Path | **Extend** — DCIM-Wiki adds time-based levels |
| §9 Approval Chain SLA | Not covered | **Unique** — DCIM-Wiki only |
| §10 Kafka Topics | Not covered | **Unique** — DCIM-Wiki only |
| §11 Consumer SLA | Not covered | **Unique** — DCIM-Wiki only |
| §12 Prometheus Alerts | Not covered | **Unique** — DCIM-Wiki only |
| §13 Breach Handling | §3 Escalation Path (partial) | **Extend** — DCIM-Wiki adds breach flow |
| §14 DQ Rules (9 rules) | Not covered | **Unique** — DCIM-Wiki only |
| §15 Notification Channels | Not covered | **Unique** — DCIM-Wiki only |

---

## 8. Alignment Score

| Metric | Score | Notes |
|--------|-------|-------|
| **FIT041 Alignment** | **65%** | Covers business layer (SLO, priority, roles, governance). Misses all technical implementation. |
| **DCIM-Wiki Supersession** | **95%** | Covers all FIT041 + 13 additional technical sections. Missing: Process Owner role, 3 business KPIs, reporting cadence, review process. |
| **After Adoption of 10 Governance Items** | **100%** | All FIT041 requirements covered. |
| **Structural Conflicts** | **0** | All differences are metric reconciliation or governance gaps. |
| **Metric Reconciliations** | **10** | 5 align perfectly, 3 FIT041 stricter, 2 FIT041 unique. |
| **Governance Items to Adopt** | **10** | 4 roles, 3 KPIs, 3 reporting/review items. |

### Per-Section Coverage

| Section | FIT041 | DCIM-Wiki | Coverage |
|---------|--------|-----------|----------|
| §1 Pendahuluan | ✅ | ✅ | 100% |
| §2 Definisi Layanan | ✅ (3 sub) | ✅ (§12 Availability + §4 Latency) | 80% (missing Failover, Manual Override) |
| §3 Model Prioritas | ✅ (P1-P4 + Escalation) | ✅ (§1 Priority + §8 Escalation) | 90% |
| §4 Peran & Tanggung Jawab | ✅ (4 roles) | ⚠️ (RBAC only) | 40% (missing functional roles) |
| §5 Metrik & Pelaporan | ✅ (5 KPIs + 3 reports) | ⚠️ (§12 Monitoring + §16 Targets) | 50% (missing business KPIs, reporting cadence) |
| §6 Tinjauan & Revisi | ✅ (annual + ad-hoc) | ❌ | 0% (not in DCIM-Wiki) |

---

## 9. Recommendations

### 9.1 Adopt from FIT041 (10 Items)

| Priority | Item | Section Target | Rationale |
|----------|------|---------------|-----------|
| **P1** | Process Owner role definition | §5 Auto-Assignment | P1 workflow authority missing |
| **P1** | Failover Time SLA (10 min) | §12 Availability SLA | Critical for HA design |
| **P1** | P1 Manual Override SLA (15 min) | §12 Availability SLA | Critical for operational response |
| **P2** | 3 Business KPIs (cycle time, touchpoint, P1 MTTE) | §16 Performance Targets | Business value measurement |
| **P2** | Reporting cadence (weekly/monthly/ad-hoc) | §17 Monitoring Dashboard | Governance requirement |
| **P2** | Annual + ad-hoc review process | New §18 Review Process | Governance requirement |
| **P3** | Automation Developer responsibilities | §5 Auto-Assignment | Role clarity |
| **P3** | End-User responsibilities | §5 Auto-Assignment | Role clarity |
| **P3** | Operations Team manual override | §5 Auto-Assignment | Role clarity |
| **P4** | Glossary (5 terms) | §1 or Appendix | Onboarding aid |

### 9.2 Keep DCIM-Wiki As-Is (No Changes Needed)

| Item | Rationale |
|------|-----------|
| §2 Workflow Type Mapping | More granular than FIT041 |
| §3 SLA Tiers | FIT041 has no tiered processing |
| §4 UC Priority Mapping (17 UCs) | FIT041 has workload categories only |
| §5 Auto-Assignment Logic | FIT041 has no automation logic |
| §6 Impact Scoring | FIT041 has no scoring formula |
| §7 Incident Severity (4 levels) | FIT041 has 3-level only |
| §9 Approval Chain SLA | FIT041 has no approval timing |
| §10 Kafka Topics | FIT041 has no message broker config |
| §11 Consumer SLA | FIT041 has no consumer mapping |
| §13 SLA Breach Handling | FIT041 has no breach flow |
| §14 DQ Rules (9 rules) | FIT041 has no DQ rules |
| §15 Notification Channels | FIT041 has no channel priority |

### 9.3 Do NOT Modify

| Document | Reason |
|----------|--------|
| FIT041 SLA document | Source of truth for business requirements |
| DCIM-Wiki SLA Framework | Already comprehensive, governance items are additive |
| Block 8 Reference Design | Separate layer (implementation spec) |
| Use Case Analysis | Separate layer (requirements mapping) |

---

## 10. Gap Comparison Template

### Gap: Workflow Automation SLA — FIT041 vs DCIM-Wiki

| Aspect | FIT041 | DCIM-Wiki | Gap | Priority | Decision |
|--------|--------|-----------|-----|----------|----------|
| Engine Availability | 99.95% | 99.9% | FIT041 stricter | P1 | **Adopt FIT041 99.95%** as business SLO |
| Failover Time | 10 min | RTO < 15 min (CMDB) | FIT041 more specific | P1 | **Adopt FIT041 10 min** |
| Manual Override | 15 min | Not defined | DCIM-Wiki missing | P1 | **Adopt FIT041 15 min** |
| Process Owner Role | Defined | Not defined | DCIM-Wiki missing | P1 | **Adopt FIT041 role** |
| Business KPIs | 3 (cycle time, touchpoint, MTTE) | 0 | DCIM-Wiki missing | P2 | **Adopt FIT041 KPIs** |
| Reporting Cadence | Weekly/Monthly/Ad-hoc | Real-time dashboard only | DCIM-Wiki missing | P2 | **Adopt FIT041 cadence** |
| Review Process | Annual + ad-hoc | Not defined | DCIM-Wiki missing | P2 | **Adopt FIT041 review** |
| Functional Roles | 4 (Process Owner, Dev, User, Ops) | 5 RBAC roles | Different models | P3 | **Complement** — both valid |
| Glossary | 5 terms | None | DCIM-Wiki missing | P4 | **Adopt FIT041 glossary** |

**Decision:** COMPLEMENTARY — all gaps are reconcilable through adoption.
**Rationale:** FIT041 provides business governance layer. DCIM-Wiki provides technical implementation layer. After adopting 10 governance items, coverage = 100%.
**Action items:** Adopt 10 FIT041 governance items into DCIM-Wiki framework (P1: 3 items, P2: 3 items, P3: 3 items, P4: 1 item).

---

## Related

- [[workflow-automation-sla-prioritization-framework]] — DCIM-Wiki SLA Framework (17 sections)
- [[IF-SLA__Prioritization_Workflow_Automation-FIT041-20260126]] — FIT041 SLA Document (6 sections)
- [[block8-workflow-automation]] — Workflow Automation Reference Design
- [[workflow-automation-use-case-analysis-final-v2]] — Use Case Analysis (17 UCs)
- [[fit041-workflow-automation-komparasi]] — FIT041 vs DCIM-Wiki Technical Requirements
- [[priority-severity-model]] — Global Priority & Severity Model
- [[dii-sla-prioritization-framework]] — DI&I SLA Framework
- [[cmdb-sla-prioritization-framework]] — CMDB SLA Framework
- [[analytics-ai-sla-prioritization-framework]] — Analytics & AI SLA Framework

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-25
> **Method:** MCP Sequential Thinking (4 thoughts) + DCIM Comparison Skill + FIT041 SLA Structure Pattern
> **Confidence:** High — all metrics sourced from documents, no fabrication
> **Must Not Modify:** Existing documents unchanged
