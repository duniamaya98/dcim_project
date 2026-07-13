---
title: "FIT041 SLA & Prioritization SIEM vs DCIM-Wiki — Komparasi"
created: 2026-06-25
updated: 2026-06-25
type: comparison
status: final
confidence: high
tags: [siem, sla, prioritization, fit041, comparison, gap-analysis]
sources:
  - IF-SLA__Prioritization_SIEM-FIT041-20260126.md
  - dcim-wiki/concepts/siem-soar-sla-prioritization-framework.md
  - dcim-wiki/technical-requirements/siem-use-case-analysis-final.md
  - dcim-wiki/reference-designs/siem-soar.md
  - dcim-wiki/concepts/sla-framework.md
method: MCP Sequential Thinking (5 steps) + MCP Context7 (Wazuh docs) + dcim-comparison skill
purpose: >
  Komparasi dokumen FIT041 SLA & Prioritization SIEM dengan DCIM-Wiki knowledge base.
  Identifikasi alignment, gaps, dan rekomendasi. COMPLEMENTARY status.
---

# FIT041 SLA & Prioritization SIEM vs DCIM-Wiki — Komparasi

> **Purpose:** Komparasi dokumen FIT041 SLA & Prioritization SIEM dengan knowledge base DCIM-Wiki.
> **Input A:** `IF-SLA__Prioritization_SIEM-FIT041-20260126.md` (FIT041 Requirements Layer)
> **Input B:** `siem-soar-sla-prioritization-framework.md` + `siem-use-case-analysis-final.md` + `siem-soar.md` (DCIM-Wiki Implementation Layer)
> **Method:** MCP Sequential Thinking (5 steps) + dcim-comparison skill
> **Status:** COMPLEMENTARY — FIT041 = governance + targets, DCIM-Wiki = implementation + technical depth
> **Alignment Score:** ~65%

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Metadata Comparison](#2-metadata-comparison)
3. [Section-by-Section Analysis](#3-section-by-section-analysis)
4. [Gap Analysis Summary](#4-gap-analysis-summary)
5. [Critical Decision Points](#5-critical-decision-points)
6. [Unique Items](#6-unique-items)
7. [Terminology Reconciliation](#7-terminology-reconciliation)
8. [Recommendations](#8-recommendations)
9. [Quality Gate Checklist](#9-quality-gate-checklist)

---

## 1. Executive Summary

### Overall Status

| Aspect | FIT041 | DCIM-Wiki | Status |
|--------|--------|-----------|--------|
| **Layer** | Requirements (APA) | Implementation (BAGAIMANA) | ✅ Complementary |
| **Focus** | SLA targets + governance | Technical implementation + operational SLAs | ✅ Complementary |
| **Approach** | Top-down (policy → targets) | Bottom-up (pipeline → targets) | ⚠️ Different but convergent |
| **Alignment Score** | — | — | ~65% |

### Key Findings

| # | Finding | Severity | Action |
|---|---------|----------|--------|
| 1 | Retention gap: FIT041 90d hot vs DCIM-Wiki 7d hot | **P1** | Hybrid retention strategy needed |
| 2 | EPS gap: FIT041 15K vs DCIM-Wiki 1K | **P1** | Progression plan: 1K → 5K → 15K |
| 3 | Latency approach differs: FIT041 60s vs DCIM-Wiki <1s | **P2** | Tiered approach (fast devices <1s, legacy ≤60s) |
| 4 | Regulatory violation as priority elevator missing in DCIM-Wiki | **P2** | Adopt from FIT041 |
| 5 | Reporting cadence missing in DCIM-Wiki | **P3** | Adopt from FIT041 |
| 6 | Review cadence missing in DCIM-Wiki | **P3** | Adopt from FIT041 |

### What FIT041 Does Better

- ✅ Governance structure (RACI roles, reporting, review cadence)
- ✅ Regulatory violation as priority elevator
- ✅ Formal reporting schedule (daily/weekly/monthly)
- ✅ Clear escalation paths with named roles
- ✅ Availability target (99.9% uptime)

### What DCIM-Wiki Does Better

- ✅ Technical depth (Kafka topics, consumer groups, Prometheus metrics)
- ✅ OT-safe enforcement rules
- ✅ Consumer SLA matrix (12 consumers)
- ✅ Data quality enforcement per priority
- ✅ Pipeline performance targets
- ✅ SOC operational SLAs (MTTA/MTTC/MTTR with auto-closure rate)
- ✅ SLA breach handling + escalation automation

---

## 2. Metadata Comparison

| Aspect | FIT041 | DCIM-Wiki |
|--------|--------|-----------|
| **Document Type** | SLA & Prioritization Framework | SLA & Prioritization Framework |
| **Version** | 1.0 | 1.0 (initial) |
| **Created** | 2026-01-26 | 2026-06-25 |
| **Scope** | Komponen SIEM dalam DCIM | SIEM SOAR layer dalam DCIM |
| **Sections** | 6 (Pendahuluan, SLA, Prioritas, Roles, Metrics, Review) | 15 (Priority, Severity, SLA Tiers, UC Mapping, SOC Ops, Kafka, Consumer, Breach, DQ, Performance, Consumer Matrix, OT-Safe, Monitoring, Acceptance, Gap) |
| **Use Cases** | 0 (policy-level) | 20 UCs mapped |
| **KPIs** | 5 | 12 Prometheus metrics + 6 alert rules |
| **Tables** | 12 | 30+ |

---

## 3. Section-by-Section Analysis

### 3.1 FIT041 §1 Pendahuluan vs DCIM-Wiki

| Aspect | FIT041 | DCIM-Wiki | Gap | Priority |
|--------|--------|-----------|-----|----------|
| Tujuan | 3 tujuan (SLO, model prioritas, RACI) | Aligned via 15-section framework | ✅ Match | — |
| Ruang Lingkup | Log collection → incident response | Event ingestion → case management + SOAR | ✅ Match | — |
| DCIM Focus | Server, jaringan, storage, physical security | + OT sensors, BMS, access control, honeypots | ⚠️ DCIM-Wiki lebih luas | — |

**Decision:** DCIM-Wiki scope lebih komprehensif. FIT041 covered.

### 3.2 FIT041 §2 Definisi Layanan vs DCIM-Wiki

#### 3.2.1 Service Availability

| Parameter | FIT041 | DCIM-Wiki | Gap | Priority |
|-----------|--------|-----------|-----|----------|
| Uptime | 99.9%/bulan (43m12s downtime) | Tidak ada explicit target | ❌ **Missing in DCIM-Wiki** | **P1** |
| Maintenance Window | 2 jam/bulan, Minggu 01:00-03:00 | Tidak ada formal window | ❌ **Missing in DCIM-Wiki** | **P2** |
| Log Agent Availability | 100% untuk DCIM kritis | Tidak ada formal target | ❌ **Missing in DCIM-Wiki** | **P2** |

**Impact:** DCIM-Wiki tidak mendefinisikan availability SLA secara eksplisit. Pipeline performance ada, tapi "uptime" sebagai SLO tidak ada.

#### 3.2.2 Performance & Latency

| Parameter | FIT041 | DCIM-Wiki | Gap | Priority |
|-----------|--------|-----------|-----|----------|
| Log Collection Latency (LCL) | ≤ 60 detik | < 1 detik (Tier 1) | ⚠️ **10-60x difference** | **P2** |
| Event Processing (EPP) | ≤ 120 detik | < 30s (correlation) | ⚠️ **4x difference** | **P2** |
| Alert Delivery | ≤ 5 menit | < 60s (playbook) | ⚠️ **5x difference** | **P2** |

**Analysis:** FIT041 target JAUH lebih longgar dari DCIM-Wiki. DCIM-Wiki menargetkan real-time (<1s) untuk ingestion via Kafka streaming. FIT041 mengizinkan 60 detik — mungkin lebih realistis untuk environment dengan legacy devices (SNMP, Syslog UDP).

**Tradeoff:**
- FIT041 approach: Lebih mudah dicapai, cocok untuk mixed environment (modern + legacy)
- DCIM-Wiki approach: Lebih aggressive, cocok untuk Kafka-based streaming pipeline
- **Recommendation:** Tiered approach — <1s untuk devices dengan Wazuh Agent (modern), ≤60s untuk legacy OT devices

#### 3.2.3 Capacity

| Parameter | FIT041 | DCIM-Wiki | Gap | Priority |
|-----------|--------|-----------|-----|----------|
| EPS | 15.000 | ~1.000 (current) | ❌ **15x difference** | **P1** |
| Hot Storage | 90 hari | 7 hari (ES ILM) | ❌ **13x difference** | **P1** |
| Cold Storage | 1 tahun | 90 hari (ES ILM) | ❌ **4x difference** | **P1** |

**Analysis:** Ini gap TERBESAR. FIT041 menuntut enterprise-grade capacity (15K EPS, 90d hot, 1y cold) yang membutuhkan:
- 3-node ES cluster minimum (saat ini single node)
- Kafka cluster 3 brokers (saat ini 1 broker)
- Petabytes SSD storage untuk 90d hot retention
- Cold storage archive system

**Tradeoff:**
- FIT041: Compliance-friendly, threat hunting optimal, tapi STORAGE COST sangat tinggi
- DCIM-Wiki: Cost-effective, tapi retention terbatas untuk advanced analysis
- **Recommendation:** Phased approach: Phase 1 (current) → Phase 2 (30d hot) → Phase 3 (90d hot + 1y cold)

### 3.3 FIT041 §3 Model Prioritas vs DCIM-Wiki

| Aspect | FIT041 | DCIM-Wiki | Gap | Priority |
|--------|--------|-----------|-----|----------|
| Model | 3-factor (Risk × Impact × Regulatory) | P1-P4 + S1-S4 | ⚠️ **Different approach** | **P2** |
| Matrix | 3×3 (Risk × Impact) | 4-level P + 4-level S | ⚠️ **Different structure** | **P2** |
| Regulatory Elevator | ✅ Ya (naikkan 1 tingkat) | ❌ Tidak ada | ❌ **Missing in DCIM-Wiki** | **P2** |
| Escalation | Named roles (DCIM Owner, CSO) | Tier 1/2/3 + CISO | ✅ Both present | — |

**FIT041 Priority Matrix:**

| Risk \ Impact | Kritis | Tinggi | Menengah |
|---------------|--------|--------|----------|
| **Tinggi** | Kritis | Kritis | Tinggi |
| **Sedang** | Kritis | Tinggi | Menengah |
| **Rendah** | Tinggi | Menengah | Rutin |

**DCIM-Wiki Priority Model:**

| Priority | Meaning | Default Latency |
|----------|---------|-----------------|
| P1 Critical | Active breach, compromised critical asset | < 1s |
| P2 High | Suspicious activity, enrichment pending | 1–30s |
| P3 Medium | Compliance event, periodic scan | 1–5 min |
| P4 Supporting | Historical analytics, dashboard refresh | > 1 hour |

**Analysis:** FIT041 model lebih FORMAL dan GOVERNANCE-oriented (risk assessment framework). DCIM-Wiki model lebih OPERATIONAL dan PIPELINE-oriented (Kafka topic priority). Keduanya valid dari sudut pandang berbeda.

**Critical Missing in DCIM-Wiki:** "Regulatory Violation" sebagai priority elevator. Untuk DCIM environment yang harus comply ISO 27001, SOC 2, ini penting. Compliance-driven escalation harus ada.

### 3.4 FIT041 §4 Peran vs DCIM-Wiki

| FIT041 Role | DCIM-Wiki Equivalent | Gap |
|-------------|---------------------|-----|
| DCIM Owner | Project Owner | ✅ Match |
| Security Team | SOC Team (L1/L2/L3) | ✅ Match |
| Operations Team | NOC Team | ✅ Match |
| Vendor SIEM | — | ❌ **Missing in DCIM-Wiki** |

**Analysis:** FIT041 punya vendor accountability yang DCIM-Wiki tidak ada. Untuk deployment dengan vendor SIEM support, ini penting.

### 3.5 FIT041 §5 Metrik vs DCIM-Wiki

| KPI | FIT041 | DCIM-Wiki | Gap | Priority |
|-----|--------|-----------|-----|----------|
| Availability | > 99.9% | — | ❌ Missing | **P1** |
| MTTD (Detect) | < 15 min | — (use MTTA) | ⚠️ Different metric | **P2** |
| MTTA (Acknowledge) | — | < 15 min | — | — |
| MTTR (Respond) | < 30 min | — (use MTTC) | ⚠️ Different metric | **P2** |
| MTTC (Contain) | — | < 30 min | — | — |
| MTTR (Resolve) | sesuai SLA 2.5 | < 4 hours | ✅ Both present | — |
| Response Compliance | > 95% | — | ❌ Missing | **P3** |
| Auto-closure Rate | — | > 60% | ❌ Missing in FIT041 | **P3** |
| False Positive Rate | — | < 10% | ❌ Missing in FIT041 | **P3** |

**Critical Terminology Issue:** FIT041 uses "MTTR" for BOTH "Mean Time to Respond" AND "Mean Time to Resolve". DCIM-Wiki separates into MTTC (contain) and MTTR (resolve). This terminology conflict MUST be resolved.

**Reporting:**

| Report | FIT041 | DCIM-Wiki | Gap |
|--------|--------|-----------|-----|
| Daily | ✅ Alert Kritis/Tinggi + open incidents | ❌ Not formalized | ❌ Missing |
| Weekly | ✅ Trend analysis + LCL/EPP compliance | ❌ Not formalized | ❌ Missing |
| Monthly | ✅ SLA KPI + volume + threat analysis | ❌ Not formalized | ❌ Missing |

### 3.6 FIT041 §6 Tinjauan vs DCIM-Wiki

| Aspect | FIT041 | DCIM-Wiki | Gap | Priority |
|--------|--------|-----------|-----|----------|
| Review Period | 6 bulan | — | ❌ **Missing** | **P3** |
| Review Trigger | Infra change, regulation, major breach | — | ❌ **Missing** | **P3** |
| Approval | DCIM Owner + Security Manager | — | ❌ **Missing** | **P3** |
| Version Control | Minor (1.0→1.1) vs Major (1.0→2.0) | — | ❌ **Missing** | **P3** |

---

## 4. Gap Analysis Summary

### 4.1 Complete Comparison Matrix

| # | Aspect | FIT041 | DCIM-Wiki | Gap | Priority | Recommendation |
|---|--------|--------|-----------|-----|----------|----------------|
| 1 | Uptime Target | 99.9%/bulan | — | ❌ Missing | **P1** | Adopt from FIT041 |
| 2 | EPS Target | 15.000 | ~1.000 | ❌ 15x gap | **P1** | Phased: 1K→5K→15K |
| 3 | Hot Retention | 90 hari | 7 hari | ❌ 13x gap | **P1** | Tiered: 7d→30d→90d |
| 4 | Cold Retention | 1 tahun | 90 hari | ❌ 4x gap | **P1** | Add cold archive tier |
| 5 | Log Agent Availability | 100% | — | ❌ Missing | **P2** | Adopt from FIT041 |
| 6 | Maintenance Window | 2 jam/bulan | — | ❌ Missing | **P2** | Adopt from FIT041 |
| 7 | Log Collection Latency | 60 detik | < 1 detik | ⚠️ Different | **P2** | Tiered: <1s (modern), ≤60s (legacy) |
| 8 | Event Processing | 120 detik | < 30 detik | ⚠️ Different | **P2** | Adopt DCIM-Wiki (<30s) |
| 9 | Alert Delivery | 5 menit | < 60 detik | ⚠️ Different | **P2** | Adopt DCIM-Wiki (<60s) |
| 10 | Priority Model | 3-factor (Risk×Impact×Reg) | P1-P4 + S1-S4 | ⚠️ Different | **P2** | Adopt FIT041 matrix as overlay |
| 11 | Regulatory Elevator | ✅ Ya | ❌ Tidak | ❌ Missing | **P2** | Adopt from FIT041 |
| 12 | Vendor SIEM Role | ✅ Ada | ❌ Tidak | ❌ Missing | **P3** | Adopt from FIT041 |
| 13 | Daily Reporting | ✅ Formal | ❌ Dashboard only | ❌ Missing | **P3** | Adopt from FIT041 |
| 14 | Weekly Reporting | ✅ Formal | ❌ Dashboard only | ❌ Missing | **P3** | Adopt from FIT041 |
| 15 | Monthly Reporting | ✅ Formal | ❌ Dashboard only | ❌ Missing | **P3** | Adopt from FIT041 |
| 16 | Review Cadence | 6 bulan | — | ❌ Missing | **P3** | Adopt from FIT041 |
| 17 | Response Compliance KPI | > 95% | — | ❌ Missing | **P3** | Adopt from FIT041 |
| 18 | Kafka Topic Priority | — | ✅ 8 topics, RF=3 | ❌ FIT041 gap | — | FIT041 doesn't cover infra |
| 19 | Consumer SLA Matrix | — | ✅ 12 consumers | ❌ FIT041 gap | — | FIT041 doesn't cover infra |
| 20 | OT-Safe Rules | — | ✅ 5 enforcement rules | ❌ FIT041 gap | — | FIT041 doesn't cover OT |
| 21 | Prometheus Metrics | — | ✅ 12 metrics + 6 alerts | ❌ FIT041 gap | — | FIT041 doesn't cover monitoring |
| 22 | Data Quality Rules | — | ✅ 4-tier DQ enforcement | ❌ FIT041 gap | — | FIT041 doesn't cover DQ |
| 23 | SOC Shift SLAs | — | ✅ Day/Evening/Night | ❌ FIT041 gap | — | FIT041 doesn't cover shift ops |
| 24 | SLA Breach Handling | — | ✅ Auto-escalation | ❌ FIT041 gap | — | FIT041 doesn't cover automation |
| 25 | DCIM Component Coverage | ✅ Network, Server, Storage, Physical | ✅ Source System Matrix | ✅ Both present | — | DCIM-Wiki more detailed |

### 4.2 Gap Distribution by Priority

```
P1 Critical: 4 gaps (Uptime, EPS, Hot Retention, Cold Retention)
P2 High:     7 gaps (Agent Avail, Maint Window, Latency, Processing, Alert, Priority Model, Regulatory)
P3 Medium:   6 gaps (Vendor Role, Daily/Weekly/Monthly Reporting, Review Cadence, Response Compliance)
Total:      17 gaps
```

### 4.3 Unique to FIT041 (Not in DCIM-Wiki)

1. Service Availability (99.9% uptime)
2. Maintenance Window (2 jam/bulan)
3. Log Agent Availability (100%)
4. Regulatory Violation as priority elevator
5. Vendor SIEM role definition
6. Daily/Weekly/Monthly reporting schedule
7. Review cadence (6 bulan)
8. Version control policy
9. Response Compliance KPI (>95%)

### 4.4 Unique to DCIM-Wiki (Not in FIT041)

1. Kafka topic priority & consumer groups
2. OT-safe enforcement rules
3. Consumer SLA matrix (12 consumers)
4. Data quality enforcement per priority
5. Pipeline performance targets
6. SOC operational SLAs (MTTA/MTTC/MTTR)
7. SLA breach handling & auto-escalation
8. Prometheus metrics & alert rules
9. SOC shift SLAs
10. 20 use cases mapped to priority + SLA tier

---

## 5. Critical Decision Points

### Decision 1: Retention Strategy

| Option | FIT041 (90d hot) | DCIM-Wiki (7d hot) | Hybrid |
|--------|-----------------|-------------------|--------|
| Storage Cost | Very High (SSD) | Low (SSD→HDD) | Medium |
| Threat Hunting | Optimal (90d fast query) | Limited (7d) | Good (30d) |
| Compliance | Meets ISO 27001 | May not meet | Meets with warm tier |
| Implementation | Complex (3-node ES) | Simple (single node) | Medium |

**Recommendation:** Hybrid — 30d hot (SSD) + 60d warm (HDD, read-only) + 90d cold (compressed) + 1y archive (S3/object storage). Meets FIT041 compliance needs at manageable cost.

### Decision 2: EPS Target

| Option | FIT041 (15K) | DCIM-Wiki (1K) | Phased |
|--------|-------------|----------------|--------|
| Infrastructure | 3-node ES, 3-broker Kafka | Single ES, single Kafka | Scale progressively |
| Cost | Enterprise-grade | Small-medium | Scaled investment |
| Timeline | 6-12 months | Current | Phase 1→2→3 |
| Risk | High (big bang) | Low | Managed risk |

**Recommendation:** Phased progression:
- Phase 1 (current): 1K EPS, single-node ES, single Kafka broker
- Phase 2 (6 months): 3K EPS, 3-node ES cluster, 3-broker Kafka
- Phase 3 (12 months): 15K EPS, dedicated processing nodes, multi-site

### Decision 3: Priority Model

| Option | FIT041 (3-factor) | DCIM-Wiki (P1-P4) | Hybrid |
|--------|------------------|-------------------|--------|
| Formality | Governance-oriented | Operations-oriented | Both |
| Regulatory | ✅ Included | ❌ Missing | ✅ Added |
| Technical Depth | ❌ Missing | ✅ Deep | ✅ Combined |
| Usability | Complex matrix | Simple levels | Matrix + levels |

**Recommendation:** Adopt FIT041 3-factor matrix as PRIORITY INPUT → maps to DCIM-Wiki P1-P4 as OPERATIONAL ACTION. Regulatory violation = auto-escalate by 1 level.

### Decision 4: Terminology Standard

| Term | FIT041 | DCIM-Wiki | Standard |
|------|--------|-----------|----------|
| Detection Latency | MTTD | — | MTTD (Mean Time to Detect) |
| Acknowledgment | — | MTTA | MTTA (Mean Time to Acknowledge) |
| Containment | — | MTTC | MTTC (Mean Time to Contain) |
| Response | MTTR (respond) | — | MTTR-Resp (Mean Time to Respond) |
| Resolution | MTTR (resolve) | MTTR | MTTR (Mean Time to Resolve) |

**Recommendation:** Adopt 5-metric model: MTTD → MTTA → MTTC → MTTR-Resp → MTTR. Avoid dual-meaning MTTR.

---

## 6. Unique Items

### 6.1 FIT041 Unique (Transfer to DCIM-Wiki)

| # | Item | Source Section | Recommendation |
|---|------|---------------|----------------|
| 1 | 99.9% uptime target | §2.1 | Add to DCIM-Wiki §9 Performance Targets |
| 2 | 2 jam/bulan maintenance window | §2.1 | Add to DCIM-Wiki §7 SLA Breach Handling |
| 3 | 100% log agent availability | §2.1 | Add to DCIM-Wiki §8 Data Quality Rules |
| 4 | Regulatory violation priority elevator | §3.1 | Add to DCIM-Wiki §1 Priority Model |
| 5 | Vendor SIEM role | §4 | Add to DCIM-Wiki §5 Consumer SLA Matrix |
| 6 | Daily/weekly/monthly reporting | §5.2 | Add to DCIM-Wiki §13 SLA Dashboard Views |
| 7 | 6-month review cadence | §6 | Add to DCIM-Wiki as new section |
| 8 | Version control policy | §6 | Add to DCIM-Wiki as new section |
| 9 | Response Compliance KPI (>95%) | §5.1 | Add to DCIM-Wiki §5 SOC Operational SLAs |

### 6.2 DCIM-Wiki Unique (Not in FIT041)

| # | Item | Source Section | FIT041 Coverage |
|---|------|---------------|----------------|
| 1 | 8 Kafka topics with RF=3 | §6 Kafka | ❌ Not covered |
| 2 | 8 consumer groups with priority | §6 Consumer | ❌ Not covered |
| 3 | OT-safe enforcement rules | §11 OT-Safe | ❌ Not covered |
| 4 | 12 Prometheus metrics + 6 alerts | §12 Monitoring | ❌ Not covered |
| 5 | 4-tier DQ enforcement | §8 DQ Rules | ❌ Not covered |
| 6 | SOC shift SLAs (Day/Evening/Night) | §5 SOC Ops | ❌ Not covered |
| 7 | SLA breach auto-escalation | §7 Breach | ❌ Not covered |
| 8 | 20 UCs mapped to priority + SLA tier | §4 UC Mapping | ❌ Not covered |
| 9 | Consumer SLA matrix (12 consumers) | §10 Consumer | ❌ Not covered |
| 10 | 5 OT-safe enforcement rules | §11 OT-Safe | ❌ Not covered |

---

## 7. Terminology Reconciliation

### 7.1 Conflict: MTTR Dual Meaning

| Context | FIT041 Meaning | DCIM-Wiki Meaning | Resolution |
|---------|---------------|-------------------|------------|
| MTTR | Mean Time to **Respond** (alert → investigation start) | Mean Time to **Resolve** (incident → closed) | Use MTTR-Resp and MTTR-Resolve |

### 7.2 Conflict: MTTD vs MTTA

| Term | FIT041 | DCIM-Wiki | Resolution |
|------|--------|-----------|------------|
| MTTD | Mean Time to Detect (log → alert trigger) | — | Keep MTTD |
| MTTA | — | Mean Time to Acknowledge (alert → analyst ACK) | Keep MTTA |

**Analysis:** MTTD and MTTA measure DIFFERENT things. MTTD = system performance (how fast SIEM detects). MTTA = human performance (how fast analyst acknowledges). Both are needed.

### 7.3 Recommended Unified Metric Set

| Metric | Definition | Target | FIT041 Source | DCIM-Wiki Source |
|--------|-----------|--------|---------------|-----------------|
| **MTTD** | Log recorded → Alert triggered | < 15 min | §5.1 | — |
| **MTTA** | Alert triggered → Analyst acknowledges | < 15 min | — | §5.1 SOC Ops |
| **MTTC** | Analyst acknowledges → Containment action | < 30 min | — | §5.1 SOC Ops |
| **MTTR-Resp** | Alert triggered → Investigation starts | < 30 min | §5.1 | — |
| **MTTR** | Incident created → Incident closed | < 4 hours | §2.5 | §5.1 SOC Ops |

---

## 8. Recommendations

### 8.1 Immediate Actions (P1)

| # | Action | Source | Impact |
|---|--------|--------|--------|
| 1 | Add 99.9% uptime SLO to DCIM-Wiki | FIT041 §2.1 | Compliance alignment |
| 2 | Create EPS progression plan (1K→5K→15K) | FIT041 §2.3 | Capacity roadmap |
| 3 | Define tiered retention strategy (7d→30d→90d→1y) | FIT041 §2.3 + DCIM-Wiki §3 | Storage planning |
| 4 | Add log agent availability target (100%) | FIT041 §2.1 | Agent monitoring |

### 8.2 Short-term Actions (P2)

| # | Action | Source | Impact |
|---|--------|--------|--------|
| 5 | Adopt regulatory violation priority elevator | FIT041 §3.1 | Compliance escalation |
| 6 | Standardize terminology (MTTD/MTTA/MTTC/MTTR) | Both | Clarity |
| 7 | Add maintenance window policy | FIT041 §2.1 | Ops scheduling |
| 8 | Create tiered latency model (modern vs legacy) | FIT041 §2.2 + DCIM-Wiki §3 | Realistic targets |

### 8.3 Medium-term Actions (P3)

| # | Action | Source | Impact |
|---|--------|--------|--------|
| 9 | Add formal reporting schedule (daily/weekly/monthly) | FIT041 §5.2 | Governance |
| 10 | Add 6-month review cadence | FIT041 §6 | Governance |
| 11 | Add vendor SIEM role definition | FIT041 §4 | Vendor management |
| 12 | Add Response Compliance KPI (>95%) | FIT041 §5.1 | SLA tracking |

### 8.4 What NOT to Change

| # | DCIM-Wiki Element | Reason |
|---|-------------------|--------|
| 1 | Kafka topic architecture | Technical implementation detail, not SLA |
| 2 | OT-safe enforcement rules | DCIM-specific, not in FIT041 scope |
| 3 | Consumer SLA matrix | Infrastructure detail |
| 4 | Prometheus metrics | Monitoring implementation |
| 5 | SOC shift SLAs | Operational detail |
| 6 | 20 use case mapping | Implementation layer |

---

## 9. Quality Gate Checklist

- [x] All 6 FIT041 sections analyzed against DCIM-Wiki
- [x] All 17 gaps identified with priority (P1-P3)
- [x] Unique items from both documents catalogued
- [x] Terminology conflicts identified and resolved
- [x] Critical decision points documented with options
- [x] Recommendations prioritized (immediate/short/medium-term)
- [x] "What NOT to change" documented
- [x] No existing documents modified
- [x] Source documents cited
- [x] Status: COMPLEMENTARY

---

## Appendix: Scorecard

| Section | FIT041 Coverage | DCIM-Wiki Coverage | Alignment |
|---------|----------------|-------------------|-----------|
| §1 Pendahuluan | ✅ Complete | ✅ Complete | ✅ 90% |
| §2 Definisi Layanan | ✅ Detailed targets | ⚠️ Partial (missing availability) | ⚠️ 55% |
| §3 Model Prioritas | ✅ 3-factor matrix | ⚠️ P1-P4 (missing regulatory) | ⚠️ 60% |
| §4 Peran & Tanggung Jawab | ✅ RACI | ✅ SOC tiers | ✅ 75% |
| §5 Metrik & Pelaporan | ✅ KPIs + Reporting | ⚠️ Metrics (no reporting) | ⚠️ 65% |
| §6 Tinjauan & Revisi | ✅ 6-month review | ❌ Missing | ❌ 10% |
| **Overall** | **✅ Complete** | **⚠️ Partial** | **~65%** |
