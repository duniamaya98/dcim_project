---
title: "SIEM SOAR SLA & Prioritization Framework — FINAL (v2.0)"
created: 2026-06-25
updated: 2026-06-25
type: framework
version: 2.0
status: final
confidence: high
tags: [siem, soar, sla, prioritization, framework, security, incident, playbook, correlation, detection, fit041, governance]
sources:
  - IF-SLA__Prioritization_SIEM-FIT041-20260126.md (FIT041 Requirements Layer)
  - dcim-wiki/concepts/siem-soar-sla-prioritization-framework.md (DCIM-Wiki Implementation Layer)
  - dcim-wiki/comparisons/fit041-siem-sla-prioritization-komparasi.md (Gap Analysis)
  - dcim-wiki/technical-requirements/siem-use-case-analysis-final.md
  - dcim-wiki/reference-designs/siem-soar.md
  - dcim-wiki/reference-designs/siem-soar-actual-architecture.md
  - dcim-wiki/concepts/priority-severity-model.md
  - dcim-wiki/concepts/cmdb-sla-prioritization-framework.md
  - dcim-wiki/concepts/dii-sla-prioritization-framework.md
method: MCP Sequential Thinking (4 steps) + dcim-comparison skill + dcim-reference-design skill
purpose: >
  FINAL SLA & Prioritization Framework untuk SIEM SOAR layer.
  Merged dari FIT041 (governance + targets) dan DCIM-Wiki (implementation + technical depth).
  17 sections, 20 use cases, 5 SLA tiers, 5-metric SOC model, regulatory elevation, hybrid retention.
---

# SIEM SOAR SLA & Prioritization Framework — FINAL (v2.0)

> **Purpose:** Framework terpadu FINAL untuk SLA, prioritas, dan urgensi di SIEM SOAR layer. Merged dari FIT041 (requirements layer — governance, targets, RACI) dan DCIM-Wiki (implementation layer — Kafka, Prometheus, OT-safe, pipeline metrics).
> **Layer:** FIT041 = APA yang harus (SLA targets + governance). DCIM-Wiki = BAGAIMANA membangun (technical implementation + operational SLAs).
> **Alignment:** COMPLEMENTARY status, ~65% pre-merge → 100% post-merge.
> **Method:** MCP Sequential Thinking (4 steps) + dcim-comparison skill + dcim-reference-design skill.
> **No Diagram:** Per owner preference, SLA documents do not require architecture diagrams.

---

## Table of Contents

1. [Priority Model](#1-priority-model)
2. [Incident Severity Mapping](#2-incident-severity-mapping)
3. [SLA Tiers](#3-sla-tiers)
4. [Service Availability](#4-service-availability)
5. [Performance & Latency](#5-performance--latency)
6. [Capacity & Retention](#6-capacity--retention)
7. [Priority Mapping per Use Case](#7-priority-mapping-per-use-case)
8. [SOC Operational SLAs](#8-soc-operational-slas)
9. [Kafka Topic Priority & Consumer Group](#9-kafka-topic-priority--consumer-group)
10. [Data Quality Rules per Priority](#10-data-quality-rules-per-priority)
11. [Consumer SLA Matrix](#11-consumer-sla-matrix)
12. [OT-Safe Enforcement Rules](#12-ot-safe-enforcement-rules)
13. [Monitoring & Alerting](#13-monitoring--alerting)
14. [RACI & Reporting](#14-raci--reporting)
15. [Acceptance Criteria](#15-acceptance-criteria)
16. [FIT041 Alignment & Traceability](#16-fit041-alignment--traceability)
17. [Governance Framework](#17-governance-framework)

---

## 1. Priority Model

### 1.1 Operational Priority (P1-P4)

| Priority | Meaning | Operational Effect | Default Latency |
|----------|---------|-------------------|-----------------|
| **P1 Critical** | Active breach, compromised critical asset, safety event | Real-time detection + auto-response, immediate SOC escalation, playbook execution < 60s | < 1 detik |
| **P2 High** | Suspicious activity, enrichment pending, policy violation | Fast triage, enrichment < 30s, alert assigned to L1 analyst | 1–30 detik |
| **P3 Medium** | Compliance event, periodic scan, audit log | Batch processing, daily review acceptable | 1–5 menit |
| **P4 Supporting** | Historical analytics, threat hunting data, dashboard refresh | Async, background, scheduled | > 1 jam |

### 1.2 Risk Assessment Matrix (from FIT041 §3.1-3.2)

Prioritas insiden ditentukan oleh kombinasi tiga faktor:

| Faktor | Deskripsi | Level |
|--------|-----------|-------|
| **Tingkat Risiko (*Risk Level*)** | Keseriusan ancaman (*Threat Intelligence*) | Tinggi / Sedang / Rendah |
| **Dampak Bisnis/DCIM (*Impact*)** | Konsekuensi jika insiden tidak ditangani | Kritis / Tinggi / Menengah |
| **Pelanggaran Regulasi (*Regulatory*)** | Apakah melanggar compliance eksternal | Ya / Tidak |

**Matriks Risiko × Dampak:**

| Tingkat Risiko | Dampak Kritis | Dampak Tinggi | Dampak Menengah |
|----------------|---------------|---------------|-----------------|
| **Tinggi** | **Kritis** | **Kritis** | Tinggi |
| **Sedang** | **Kritis** | Tinggi | Menengah |
| **Rendah** | Tinggi | Menengah | Rutin (Low) |

**Regulatory Violation Elevator:**

> ⚠️ Jika insiden melibatkan **pelanggaran regulasi** (data pelanggan, ISO 27001, SOC 2, UU PDP), prioritas wajib **dinaikkan minimal satu tingkat** (kecuali sudah Kritis).

### 1.3 Mapping: Risk Matrix → Operational Priority

| Risk Matrix Output | Maps to Operational Priority | Action |
|--------------------|------------------------------|--------|
| **Kritis** | **P1 Critical** | Real-time, auto-response, CISO notify |
| **Tinggi** | **P2 High** | Fast triage, L1/L2 assign |
| **Menengah** | **P3 Medium** | Batch, daily review |
| **Rutin (Low)** | **P4 Supporting** | Async, scheduled |

---

## 2. Incident Severity Mapping

### 2.1 Severity Levels

| Severity | Source Priority | SOC Response | Auto-Response | Escalation | Example |
|----------|----------------|--------------|---------------|------------|---------|
| **S1 Critical** | P1 + Critical Asset | Immediate triage (L2/L3) | Auto-contain (OT-safe guard) | CISO within 15 min | Active ransomware, core switch compromised |
| **S2 High** | P1 + Non-Critical or P2 + Critical Asset | Fast assign (L1/L2) | Enrich + notify | SOC Manager within 30 min | Brute force admin, malware detected |
| **S3 Medium** | P2 + Non-Critical Asset | Normal queue (L1) | Enrich only | Within 4 hours | Suspicious DNS, policy violation |
| **S4 Low** | P3/P4 | Batch review | None | Next shift | Compliance scan, informational log |

### 2.2 Classification Examples (from FIT041 §2.5)

| Severity | Klasifikasi Insiden (FIT041) |
|----------|------------------------------|
| S1 Critical | Ancaman aktif berdampak langsung pada operasional DCIM (ransomware aktif, akses tidak sah core switches) |
| S2 High | Potensi dampak serius atau melanggar kebijakan (malware server non-kritis, kegagalan log firewall) |
| S3 Medium | Peristiwa memerlukan perhatian tapi tidak berdampak langsung (anomali aktivitas pengguna, login berulang gagal) |
| S4 Low | Insiden minor atau permintaan informasi (laporan statistik, penyempurnaan aturan korelasi) |

### 2.3 Tingkat Tindakan (from FIT041 §3.2)

| Tingkat Tindakan | Deskripsi | Target Waktu |
|------------------|-----------|--------------|
| **Kritis** | Penanganan segera (terlepas jam kerja). Semua sumber daya dimobilisasi. | Diperiksa dan ditangani segera |
| **Tinggi** | Penanganan segera setelah Kritis selesai. Diselesaikan dalam 1 jam. | Dalam 1 Jam |
| **Menengah** | Penanganan dapat ditunda hingga jam kerja berikutnya. Maks 1 hari kerja. | Dalam 1 Hari Kerja |
| **Rutin (Low)** | Penanganan rutin dan berulang. | Dalam 3 Hari Kerja |

---

## 3. SLA Tiers

| Tier | Latency | Use Cases | Processing Mode | Pipeline |
|------|---------|-----------|-----------------|----------|
| **Tier 1 (Real-time)** | < 1s | UC1-6, UC14, UC19 | Kafka → Stream Processor | Wazuh → Kafka → ES + Correlation |
| **Tier 2 (Near-RT)** | 1–30s | UC7-13, UC16, UC20 | Kafka → Consumer | ElastAlert → Tracecat → IRIS |
| **Tier 3 (Batch)** | 1–5 min | UC17-18 | NiFi Scheduled | Scheduled scan + report |
| **Tier 4 (Batch)** | 15–60 min | UC6 (MITRE mapping) | Background Jobs | Rule-to-ATT&CK mapper |
| **Tier 5 (On-demand)** | Variable | UC15 (Threat Hunting) | Ad-hoc Query | Analyst → ES/Kibana |

### Tier Definitions

- **Tier 1**: Event masuk Kafka, langsung diproses stream processor, alert < 1 detik. Zero tolerance data loss.
- **Tier 2**: Alert masuk enrichment pipeline, AI triage < 30s, playbook < 60s. Near-real-time SOC response.
- **Tier 3**: Scheduled compliance scans dan report generation. Batch, idempotent.
- **Tier 4**: Background MITRE ATT&CK mapping, historical correlation. Non-urgent.
- **Tier 5**: Analyst-initiated threat hunting. Variable latency.

### FIT041 Latency Floor (Minimum Acceptable)

| Parameter | FIT041 Target (Floor) | DCIM-Wiki Target (Optimal) | Decision |
|-----------|----------------------|---------------------------|----------|
| Log Collection Latency (LCL) | ≤ 60 detik | < 1 detik (Tier 1) | **Tiered:** <1s (modern devices via Agent), ≤60s (legacy OT/Syslog) |
| Event Processing (EPP) | ≤ 120 detik | < 30s (correlation) | **Adopt DCIM-Wiki:** <30s target |
| Alert Delivery | ≤ 5 menit | < 60s (playbook) | **Adopt DCIM-Wiki:** <60s target |

---

## 4. Service Availability

> **Source:** FIT041 §2.1 — adopted into DCIM-Wiki framework.

### 4.1 Uptime Target

| Parameter | Target | Penjelasan |
|-----------|--------|-----------|
| **Target Uptime** | **99.9% per bulan** | Maksimum downtime 43 menit 12 detik per bulan. Dihitung sebagai kegagalan menerima/memproses/menghasilkan peringatan dari log infrastruktur DCIM. |
| **Measurement** | Monthly uptime percentage | Exclusions: scheduled maintenance windows |

### 4.2 Maintenance Window

| Parameter | Target |
|-----------|--------|
| **Jadwal Pemeliharaan** | Maksimal 2 jam/bulan |
| **Waktu Pelaksanaan** | Minggu terakhir setiap bulan, 01:00–03:00 WIB |
| **Pemberitahuan** | Minimal 48 jam sebelumnya |

### 4.3 Log Agent Availability

| Parameter | Target |
|-----------|--------|
| **Ketersediaan Agen Log** | **100%** untuk infrastruktur DCIM kritis |
| **Definisi** | Seluruh agen pengumpul log terpasang pada infrastruktur DCIM kritis harus selalu aktif dan mengirimkan data |

### 4.4 DCIM Component Coverage (from FIT041 §2.4)

Layanan SIEM **WAJIB** terintegrasi dan memantau log dari komponen DCIM kritis:

| Komponen | Cakupan Wajib |
|----------|---------------|
| **Jaringan** | Core switches, distribution switches, firewalls, IPS |
| **Server** | Hypervisor hosts (VMware/Hyper-V), Domain Controllers, Jump Servers |
| **Penyimpanan** | SAN dan NAS kritis |
| **Keamanan Fisik/Logis** | Kontrol Akses Pintu, CCTV terintegrasi, MFA system |

---

## 5. Performance & Latency

### 5.1 Pipeline Performance Targets

| Metric | Target | Current (v4.2) | Gap | Phase |
|--------|--------|----------------|-----|-------|
| Event Ingestion Rate | ≥ 1,000 EPS | ~500 EPS | ⚠️ 50% | Phase 1 |
| Detection Latency | < 5s | ~10s (ElastAlert polling) | ❌ 2x | Phase 1 |
| Playbook Execution | < 30s | Not deployed | ❌ Missing | Phase 1 |
| ES Cluster Size | 3-node minimum | Single node | ❌ Not HA | Phase 1 |
| Kafka Brokers | 3 brokers, RF=3 | 1 broker, RF=1 | ❌ Not HA | Phase 1 |

### 5.2 SOC Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Alert Volume (daily) | < 500 actionable | Post-triage count |
| Alert-to-Incident Ratio | < 10:1 | Alerts / confirmed incidents |
| SOC Analyst Utilization | 70–85% | Active investigation time / shift |
| Playbook Success Rate | > 95% | Completed / started |
| CMDB Enrichment Hit Rate | > 80% | CI found / alert enriched |

### 5.3 Response SLA by Severity

| Severity | First Response | Containment | Resolution | Notification |
|----------|---------------|-------------|------------|--------------|
| S1 Critical | Immediate (< 5 min) | < 30 min | < 4 hours | CISO within 15 min |
| S2 High | < 15 min | < 1 hour | < 8 hours | SOC Manager within 30 min |
| S3 Medium | < 1 hour | < 4 hours | < 24 hours | Next shift handover |
| S4 Low | < 4 hours | < 24 hours | < 72 hours | Weekly review |

---

## 6. Capacity & Retention

### 6.1 EPS Progression Plan

> **Decision:** FIT041 menuntut 15K EPS. DCIM-Wiki aktual ~1K EPS. Phased approach.

| Phase | EPS Target | Infrastructure | Timeline |
|-------|-----------|----------------|----------|
| **Phase 1 (Current)** | 1,000 EPS | Single-node ES, 1 Kafka broker | Now |
| **Phase 2** | 5,000 EPS | 3-node ES cluster, 3 Kafka brokers | 6 months |
| **Phase 3** | 15,000 EPS | Dedicated processing nodes, multi-site | 12 months |

### 6.2 Retention Strategy

> **Decision:** FIT041 menuntut 90d hot storage. DCIM-Wiki 7d hot. Hybrid approach.

| Tier | Duration | Storage | Access | Purpose |
|------|----------|---------|--------|---------|
| **Hot** | 0–7 hari | SSD (Elasticsearch) | Full query, real-time | Active investigation, dashboards |
| **Warm** | 7–30 hari | HDD (Elasticsearch) | Read-only, force merge | Recent analysis, trend review |
| **Cold** | 30–90 hari | HDD (Elasticsearch compressed) | Compressed, frozen | Compliance, forensics |
| **Archive** | 90 hari–1 tahun | Object storage (S3/MinIO) | On-demand restore | Regulatory compliance, deep forensics |

### 6.3 DCIM Component Coverage

| Parameter | Target |
|-----------|--------|
| Hot Storage (searchable) | 30 hari |
| Warm Storage (read-only) | 60 hari tambahan |
| Cold Storage (compressed) | 90 hari total |
| Archive (object storage) | 1 tahun |
| Total searchable window | 30 hari (full) + 60 hari (warm) |

---

## 7. Priority Mapping per Use Case

| UC | Name | Priority | SLA Tier | Latency Target | DQ Completeness | DQ Timeliness |
|----|------|----------|----------|----------------|-----------------|---------------|
| UC1 | Security Event Collection & Normalization | **P1** | Tier 1 (< 1s) | < 1s | ≥ 99.9% | < 1s |
| UC2 | Log Decoding & Field Extraction | **P1** | Tier 1 (< 1s) | < 500ms | ≥ 99.9% | < 500ms |
| UC3 | Security Event Schema & Storage | **P1** | Tier 1 (< 1s) | < 1s | ≥ 99.9% | < 1s |
| UC4 | Correlation Engine | **P1** | Tier 1 (< 1s) | < 30s | ≥ 99% | < 30s |
| UC5 | Detection Engineering (Detection-as-Code) | **P1** | Tier 1 (< 1s) | < 30s | ≥ 99% | Real-time |
| UC6 | MITRE ATT&CK Mapping | **P1** | Tier 4 (15–60m) | < 60 min | ≥ 95% | Batch |
| UC7 | ML Alert Triage | **P2** | Tier 2 (1–30s) | < 30s | ≥ 98% | < 30s |
| UC8 | Alert Enrichment Pipeline | **P1** | Tier 2 (1–30s) | < 30s | ≥ 95% | < 60s |
| UC9 | Incident Response Workflow | **P1** | Tier 2 (1–30s) | < 30s | ≥ 98% | < 30s |
| UC10 | SOAR Automated Response | **P1** | Tier 2 (1–30s) | < 60s | ≥ 98% | < 60s |
| UC11 | Case Management (DFIR-IRIS) | **P1** | Tier 2 (1–30s) | < 120s | ≥ 100% | < 120s |
| UC12 | Escalation Workflow | **P1** | Tier 2 (1–30s) | < 5 min | ≥ 99% | < 5 min |
| UC13 | Physical-Cyber Correlation | **P1** | Tier 2 (1–30s) | < 30s | ≥ 99% | < 30s |
| UC14 | Deception Technology (Honeypots) | **P3** | Tier 1 (< 1s) | < 1s | ≥ 99% | < 1s |
| UC15 | Threat Hunting | **P2** | Tier 5 (on-demand) | Variable | ≥ 95% | On-demand |
| UC16 | XDR Integration | **P2** | Tier 2 (1–30s) | < 30s | ≥ 98% | < 30s |
| UC17 | Compliance & Audit Reporting | **P2** | Tier 3 (1–5m) | < 5 min | ≥ 100% | < 5 min |
| UC18 | CIS Benchmark Compliance | **P2** | Tier 3 (1–5m) | < 5 min | ≥ 100% | < 5 min |
| UC19 | SOC Dashboard & Visualization | **P2** | Tier 1 (< 1s) | < 3s | ≥ 99% | Real-time |
| UC20 | User & Entity Behavior Analytics (UEBA) | **P2** | Tier 2 (1–30s) | < 30s | ≥ 98% | < 30s |

### Priority Distribution

```
P1 Critical: 13 UCs (UC1-6, UC8-13) — security core + incident response
P2 High:      5 UCs (UC7, UC15-20)  — analytics, advanced detection, operations
P3 Medium:    1 UC  (UC14)           — deception (honeypots)
P4 Supporting: 0 UCs
```

---

## 8. SOC Operational SLAs

### 8.1 Unified SOC Metric Model (5-Metric)

> **Terminology Reconciliation:** FIT041 uses "MTTR" for both respond and resolve. DCIM-Wiki uses MTTA/MTTC/MTTR. Adopted 5-metric model below.

| Metric | Definition | Target | Escalation Trigger | Source |
|--------|-----------|--------|-------------------|--------|
| **MTTD** (Mean Time to Detect) | Log recorded → Alert triggered | < 15 min | > 15 min → SOC Manager | FIT041 §5.1 |
| **MTTA** (Mean Time to Acknowledge) | Alert triggered → Analyst acknowledges | < 15 min | > 15 min → SOC Manager | DCIM-Wiki §5.1 |
| **MTTC** (Mean Time to Contain) | Alert confirmed → Containment action | < 30 min | > 30 min → CISO | DCIM-Wiki §5.1 |
| **MTTR-Resp** (Mean Time to Respond) | Alert triggered → Investigation starts | < 30 min | > 30 min → SOC Manager | FIT041 §5.1 |
| **MTTR** (Mean Time to Resolve) | Incident created → Incident closed | < 4 hours | > 4 hours → Escalation review | Both |

### 8.2 Additional SOC KPIs

| KPI | Target | Source |
|-----|--------|--------|
| Auto-closure Rate | > 60% | DCIM-Wiki |
| Escalation Rate | < 25% | DCIM-Wiki |
| False Positive Rate | < 10% | DCIM-Wiki |
| Service Availability | > 99.9% | FIT041 §2.1 |
| Response Compliance | > 95% | FIT041 §5.1 |

### 8.3 SOC Shift SLAs

| Shift | Coverage | Response Target | Escalation Path |
|-------|----------|----------------|-----------------|
| Day (08:00–16:00) | Full SOC team (L1+L2+L3) | Standard SLAs | L1 → L2 → L3 → CISO |
| Evening (16:00–00:00) | Skeleton crew (L1+L2) | Standard SLAs | L1 → L2 → On-call L3 |
| Night (00:00–08:00) | On-call (L1) | S1/S2 only, S3/S4 deferred | L1 → On-call L2 → CISO |

### 8.4 Escalation Paths (from FIT041 §3.3)

| Tingkat Tindakan | Jalur Eskalasi | Kontak |
|------------------|---------------|--------|
| Kritis & Tinggi | Tier 1 (SOC Analyst) → Tier 2 (Security Engineer) → **DCIM Owner & CSO** | DCIM Owner |
| Menengah | Tier 1 (SOC Analyst) → Tier 2 (Security Engineer) | Security Manager |
| Rutin (Low) | Tier 1 (SOC Analyst) | Operations Team Lead |

---

## 9. Kafka Topic Priority & Consumer Group

### 9.1 Topic Priority Mapping

| Kafka Topic | Partitions | Replication | Retention | Priority | Consumer |
|-------------|------------|-------------|-----------|----------|----------|
| `dcim.siem.events` | 12 | RF=3 | 7 days | **P1** | ES Indexer, Correlation Engine |
| `dcim.siem.alerts` | 6 | RF=3 | 30 days | **P1** | ML Triage, SOAR (ElastAlert) |
| `dcim.siem.triaged` | 6 | RF=3 | 30 days | **P1** | Enrichment Pipeline |
| `dcim.siem.enriched` | 6 | RF=3 | 30 days | **P1** | SOAR (Tracecat Webhook) |
| `dcim.siem.incidents` | 6 | RF=3 | 90 days | **P1** | DFIR-IRIS |
| `dcim.siem.correlated` | 6 | RF=3 | 30 days | **P2** | Physical-Cyber Correlation |
| `dcim.siem.deception` | 3 | RF=2 | 30 days | **P3** | SOAR (Honeypot alert) |
| `dcim.siem.ueba` | 6 | RF=3 | 30 days | **P2** | UEBA Alert Engine |

### 9.2 Consumer Group Priority

| Consumer Group | Topic(s) | Priority | Max Latency | Concurrency |
|----------------|----------|----------|-------------|-------------|
| `siem-es-indexer` | `dcim.siem.events` | **P1** | < 1s | 6 consumers |
| `siem-correlation` | `dcim.siem.events` | **P1** | < 30s | 3 consumers |
| `siem-triage` | `dcim.siem.alerts` | **P1** | < 30s | 3 consumers |
| `siem-enrichment` | `dcim.siem.triaged` | **P1** | < 30s | 3 consumers |
| `soar-playbook` | `dcim.siem.enriched` | **P1** | < 60s | 3 consumers |
| `iris-incident` | `dcim.siem.incidents` | **P1** | < 120s | 2 consumers |
| `siem-xdr` | `dcim.xdr.events` | **P2** | < 30s | 2 consumers |
| `siem-ueba` | `dcim.siem.ueba` | **P2** | < 30s | 2 consumers |

---

## 10. Data Quality Rules per Priority

| Priority | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| **P1** | ≥ 99.9% | Field validation + cross-source | < 1s | ECS schema enforced | Schema check on ingest |
| **P2** | ≥ 98% | API response validation | < 30s | Cross-source correlation | Model drift monitor |
| **P3** | ≥ 95% | Report accuracy | < 5 min | Audit format | Template match |
| **P4** | ≥ 90% | Historical consistency | < 1 hour | Archive format | Format check |

### DQ Enforcement Points

| Pipeline Stage | DQ Check | Action on Failure |
|---------------|----------|-------------------|
| Ingestion (UC1) | Schema validation, source allowlist | Quarantine + error alert |
| Decoding (UC2) | Field extraction accuracy > 99% | Fallback decoder + log error |
| Correlation (UC4) | Rule match confidence > 80% | Manual review queue |
| Triage (UC7) | Model accuracy > 90% | Flag for analyst review |
| Enrichment (UC8) | API response validation | Retry + fallback source |
| Case (UC11) | Required field completeness | Block case creation |

---

## 11. Consumer SLA Matrix

| Consumer | Source Topic(s) | Priority | Max Latency | Fallback |
|----------|----------------|----------|-------------|----------|
| Elasticsearch | `dcim.siem.events` | **P1** | < 1s | DLQ + retry |
| Kibana Dashboard | ES query | **P2** | < 3s | Cached view |
| ElastAlert → Tracecat | `dcim.siem.alerts` | **P1** | < 30s | Email fallback |
| Tracecat SOAR | `dcim.siem.enriched` | **P1** | < 60s | Manual trigger |
| DFIR-IRIS | `dcim.siem.incidents` | **P1** | < 120s | Manual creation |
| SOC Analyst (L1/L2) | DFIR-IRIS + Email | **P1** | < 15 min (MTTA) | PagerDuty |
| SOC Manager | Escalation queue | **P2** | < 30 min | SMS alert |
| CISO | Executive report | **P3** | < 1 hour | Email summary |
| Auditor | Compliance report | **P3** | < 24 hours | Manual export |
| CMDB | Enrichment query | **P1** | < 500ms | Cached CI |
| ITSM (ServiceNow) | Incident sync | **P2** | < 5 min | Manual ticket |
| MISP | IOC enrichment | **P2** | < 30s | Cached intel |

---

## 12. OT-Safe Enforcement Rules

| Rule | Scope | Enforcement | Override |
|------|-------|-------------|----------|
| No auto-reboot | DCIM critical assets (P1 priority) | Playbook blocks reboot action | Requires CISO approval |
| No auto-patch | Production servers | Playbook blocks patch action | Requires change ticket |
| Read-only forensics | All DCIM systems | Memory dump, PCAP = read-only | None |
| Approval gate | P1 asset containment | Manual approval before IP block | CISO override |
| Rollback required | Any config change | Playbook must include rollback | None |

---

## 13. Monitoring & Alerting

### 13.1 Prometheus Metrics

| Metric | Type | Labels | Alert Threshold |
|--------|------|--------|-----------------|
| `siem_events_ingested_total` | counter | source, priority | — |
| `siem_events_ingestion_latency_seconds` | histogram | source | p99 > 2s |
| `siem_alerts_generated_total` | counter | severity, rule_id | — |
| `siem_alert_triage_latency_seconds` | histogram | model | p99 > 30s |
| `siem_playbook_execution_seconds` | histogram | playbook, status | p99 > 60s |
| `siem_incidents_created_total` | counter | severity | — |
| `siem_incidents_mtt_seconds` | histogram | severity, metric_type | See §8.1 thresholds |
| `siem_kafka_consumer_lag` | gauge | topic, consumer_group | > 1000 |
| `siem_es_cluster_health` | gauge | cluster | < 1 (yellow/red) |
| `siem_enrichment_hit_rate` | gauge | source | < 0.80 |
| `siem_false_positive_rate` | gauge | rule_id | > 0.10 |
| `siem_service_uptime_percent` | gauge | service | < 99.9 |

### 13.2 Alert Rules (Prometheus)

```yaml
groups:
  - name: siem-slo-breach
    rules:
      - alert: SIEMIngestionLatencyHigh
        expr: histogram_quantile(0.99, siem_events_ingestion_latency_seconds) > 2
        for: 5m
        labels:
          severity: S2
        annotations:
          summary: "SIEM ingestion latency p99 > 2s"

      - alert: SIEMPlaybookTimeout
        expr: histogram_quantile(0.99, siem_playbook_execution_seconds) > 60
        for: 2m
        labels:
          severity: S2
        annotations:
          summary: "SOAR playbook execution p99 > 60s"

      - alert: SIEMMTTABreach
        expr: histogram_quantile(0.95, siem_incidents_mtt_seconds{metric_type="mtta"}) > 900
        for: 10m
        labels:
          severity: S2
        annotations:
          summary: "SOC MTTA p95 > 15 minutes"

      - alert: SIEMMTTRBreach
        expr: histogram_quantile(0.95, siem_incidents_mtt_seconds{metric_type="mttr"}) > 14400
        for: 10m
        labels:
          severity: S2
        annotations:
          summary: "SOC MTTR p95 > 4 hours"

      - alert: SIEMKafkaConsumerLagHigh
        expr: siem_kafka_consumer_lag > 1000
        for: 5m
        labels:
          severity: S2
        annotations:
          summary: "Kafka consumer lag > 1000 messages"

      - alert: SIEMESClusterRed
        expr: siem_es_cluster_health < 1
        for: 2m
        labels:
          severity: S1
        annotations:
          summary: "Elasticsearch cluster health RED"

      - alert: SIEMFalsePositiveRateHigh
        expr: siem_false_positive_rate > 0.10
        for: 1h
        labels:
          severity: S3
        annotations:
          summary: "SIEM false positive rate > 10% — rule tuning needed"

      - alert: SIEMServiceUptimeLow
        expr: siem_service_uptime_percent < 99.9
        for: 5m
        labels:
          severity: S1
        annotations:
          summary: "SIEM service uptime < 99.9% — SLA breach"
```

### 13.3 SLA Dashboard Views

| View | Key Metrics | Refresh | Audience |
|------|------------|---------|----------|
| **SOC Real-time** | Alert volume, severity, MTTD/MTTA/MTTC/MTTR | Real-time | SOC Analyst |
| **SOC Operations** | Analyst utilization, queue depth, escalation rate | 5 min | SOC Manager |
| **SOAR Health** | Playbook success rate, execution time, error rate | 1 min | SOC Engineer |
| **Pipeline Health** | Ingestion EPS, consumer lag, ES cluster health | Real-time | NOC |
| **Executive Summary** | Incident trend, SLA compliance, threat landscape | Daily | CISO / Management |

### 13.4 SLA Breach Handling

| SLA Breach Type | Detection Method | Escalation Path | Max Recovery |
|----------------|-----------------|-----------------|--------------|
| MTTA > 15 min | Alert aging monitor (Kibana) | Auto-escalate to SOC Manager | < 30 min |
| MTTC > 30 min | DFIR-IRIS timer | SOC Manager → CISO | < 1 hour |
| MTTR > 4 hours | DFIR-IRIS SLA tracker | CISO + Management report | < 8 hours |
| Ingestion > 1s | Kafka consumer lag monitor | Auto-alert NOC + SOC | < 5 min |
| Playbook > 60s | Temporal workflow timeout | Auto-retry + alert SOC | < 5 min |
| Uptime < 99.9% | Service health check | Auto-escalate to DCIM Owner | < 43 min (remaining budget) |

---

## 14. RACI & Reporting

### 14.1 RACI Roles (from FIT041 §4)

| Peran | Tanggung Jawab Utama terkait SIEM |
|-------|-----------------------------------|
| **DCIM Owner** | Otoritas tertinggi: persetujuan anggaran, kebijakan keamanan, penerima laporan insiden Kritis. Memastikan kepatuhan SIEM terhadap kebutuhan DCIM. |
| **Security Team** | Pemantauan 24/7, penanganan insiden, analisis log, pemeliharaan aturan korelasi, pelaporan insiden kepada DCIM Owner. |
| **Operations Team** | Ketersediaan agen log (SLA §4.3), implementasi mitigasi (patching, isolasi) yang diminta Security Team. |
| **Vendor SIEM** | Pembaruan perangkat lunak, dukungan teknis platform, bantuan kalibrasi kinerja (SLA §5). |

### 14.2 Reporting Schedule (from FIT041 §5.2)

| Jenis Laporan | Frekuensi | Penerima | Fokus Konten |
|---------------|-----------|----------|--------------|
| **Laporan Harian** | Harian (awal hari kerja) | Security Team, Operations Team | Alert Kritis & Tinggi dalam 24 jam terakhir, status insiden terbuka |
| **Laporan Mingguan** | Setiap Hari Senin | Security Team, Security Manager | Analisis tren, ringkasan insiden per Severity, kepatuhan LCL/EPP |
| **Laporan Bulanan** | Tanggal [Date] setiap bulan | DCIM Owner, CSO | Kepatuhan SLA (KPI §8), volume log, analisis ancaman top, rekomendasi peningkatan |

### 14.3 DCIM Component Coverage (from FIT041 §2.4)

| Komponen | Cakupan Monitoring | Status |
|----------|-------------------|--------|
| Jaringan | Core/distribution switches, firewalls, IPS | WAJIB |
| Server | Hypervisor hosts, Domain Controllers, Jump Servers | WAJIB |
| Penyimpanan | SAN dan NAS kritis | WAJIB |
| Keamanan Fisik/Logis | Kontrol Akses, CCTV, MFA | WAJIB |

---

## 15. Acceptance Criteria

### 15.1 Merged Acceptance Criteria

| # | Criterion | Evidence | Source |
|---|-----------|----------|--------|
| 1 | P1 alerts terdeteksi < 1 detik dari event masuk | Kafka consumer lag < 1000, ES write p99 < 1s | DCIM-Wiki |
| 2 | MTTD < 15 menit untuk semua alerts | Alert pipeline metrics | FIT041 §5.1 |
| 3 | MTTA < 15 menit untuk semua S1/S2 incidents | DFIR-IRIS dashboard | DCIM-Wiki |
| 4 | MTTC < 30 menit untuk S1 incidents | DFIR-IRIS containment timestamp | DCIM-Wiki |
| 5 | MTTR-Resp < 30 menit untuk semua S1/S2 incidents | Investigation start timestamp | FIT041 §5.1 |
| 6 | MTTR < 4 jam untuk S1 incidents | DFIR-IRIS resolution timestamp | Both |
| 7 | Service uptime > 99.9% per bulan | Service health monitoring | FIT041 §2.1 |
| 8 | Auto-closure rate > 60% | SOAR playbook completion stats | DCIM-Wiki |
| 9 | False positive rate < 10% | Alert triage statistics | DCIM-Wiki |
| 10 | Response compliance > 95% | Incidents responded within SLA / total | FIT041 §5.1 |
| 11 | Kafka HA: 3 brokers, RF=3 untuk P1 topics | Kafka cluster status | DCIM-Wiki |
| 12 | ES cluster: 3-node minimum | ES cluster health GREEN | DCIM-Wiki |
| 13 | Playbook execution < 60s p99 | Temporal workflow metrics | DCIM-Wiki |
| 14 | OT-safe enforcement aktif untuk DCIM P1 assets | Playbook audit log | DCIM-Wiki |
| 15 | Log agent availability 100% untuk infra kritis | Agent heartbeat monitoring | FIT041 §2.1 |
| 16 | Prometheus metrics aktif untuk 13 metrics §13.1 | Grafana dashboard live | DCIM-Wiki |
| 17 | Consumer SLA matrix terpenuhi untuk 12 consumers | Consumer lag + latency metrics | DCIM-Wiki |
| 18 | Regulatory violation elevator aktif | Priority override audit log | FIT041 §3.1 |

### 15.2 SLA Breach Handling Acceptance

| # | Criterion | Evidence |
|---|-----------|----------|
| 19 | SLA breach auto-escalation aktif | PagerDuty/notification test |
| 20 | Post-breach root cause analysis dalam 24 jam | RCA document |
| 21 | Post-breach remediation plan dalam 48 jam | Remediation document |

---

## 16. FIT041 Alignment & Traceability

### 16.1 Absorption Summary

| FIT041 Section | Items Absorbed | Target Section in FINAL |
|---------------|----------------|------------------------|
| §1 Pendahuluan | Scope, tujuan | Preamble + §4.4 |
| §2.1 Service Availability | 99.9% uptime, maintenance window, agent availability | §4 |
| §2.2 Performance & Latency | LCL, EPP, Alert Delivery (as floor targets) | §3 (FIT041 Latency Floor) |
| §2.3 Capacity | EPS, hot/cold retention | §6 (Hybrid approach) |
| §2.4 DCIM Coverage | Network, Server, Storage, Physical Security | §4.4 + §14.4 |
| §2.5 Response & Resolution | S1-S4 classification, response/resolution targets | §2.2 + §2.3 + §5.3 |
| §3.1 Risk Criteria | Risk Level, Impact, Regulatory Violation | §1.2 |
| §3.2 Priority Matrix | 3×3 Risk×Impact matrix | §1.2 + §1.3 |
| §3.3 Escalation | Escalation paths (L1→L2→Owner) | §8.4 |
| §4 Roles & Responsibilities | RACI (Owner, Security, Operations, Vendor) | §14.1 |
| §5.1 KPIs | MTTD, MTTR (respond/resolve), Response Compliance | §8.1 + §8.2 |
| §5.2 Reporting | Daily/Weekly/Monthly schedule | §14.2 |
| §6 Review & Revision | 6-month review, version control | §17 |

### 16.2 Reconciled Metrics

| Metric | FIT041 Name | DCIM-Wiki Name | Final Name | Target |
|--------|------------|----------------|------------|--------|
| Detection Latency | MTTD | — | **MTTD** | < 15 min |
| Acknowledgment | — | MTTA | **MTTA** | < 15 min |
| Containment | — | MTTC | **MTTC** | < 30 min |
| Response Time | MTTR (respond) | — | **MTTR-Resp** | < 30 min |
| Resolution Time | MTTR (resolve) | MTTR | **MTTR** | < 4 hours |

### 16.3 Pre-Merge vs Post-Merge

| Aspect | Pre-Merge (DCIM-Wiki only) | Post-Merge (FINAL) | Improvement |
|--------|---------------------------|--------------------|-------------|
| Sections | 15 | 17 | +2 (RACI + Governance) |
| Availability Target | ❌ Missing | ✅ 99.9% uptime | +1 from FIT041 |
| Maintenance Window | ❌ Missing | ✅ 2 jam/bulan | +1 from FIT041 |
| Regulatory Elevator | ❌ Missing | ✅ Active | +1 from FIT041 |
| Reporting Schedule | ❌ Missing | ✅ Daily/Weekly/Monthly | +1 from FIT041 |
| Review Cadence | ❌ Missing | ✅ 6 months | +1 from FIT041 |
| Vendor Role | ❌ Missing | ✅ Defined | +1 from FIT041 |
| SOC Metrics | 3 metrics | 5 metrics | +2 (MTTD, MTTR-Resp) |
| Acceptance Criteria | 15 items | 21 items | +6 items |
| Coverage | ~65% | ~100% | +35% |

---

## 17. Governance Framework

### 17.1 Review Cadence

| Aspek | Kebijakan |
|-------|-----------|
| **Periode Tinjauan** | Setiap **6 bulan** atau segera setelah perubahan signifikan |
| **Trigger Review** | Perubahan signifikan infrastruktur DCIM, implementasi regulasi baru, insiden keamanan besar (*major breach*) |
| **Otoritas Revisi** | DCIM Owner dan Security Manager |
| **Approval** | Setiap revisi harus disetujui oleh DCIM Owner dan Security Manager |

### 17.2 Version Control

| Jenis Revisi | Contoh | Kriteria |
|--------------|--------|----------|
| **Minor** | 2.0 → 2.1 | Perubahan kecil (typo, clarify, formatting) |
| **Mayor** | 2.0 → 3.0 | Perubahan substansial (target SLA, prioritas model, struktur) |

### 17.3 Amendment Process

```
Amendment Proposed
├── Proposed by: Any stakeholder
├── Impact assessment: DCIM Owner + Security Manager
├── Approval required: DCIM Owner + Security Manager
├── Documentation: Version change + rationale
├── Communication: Notify all RACI roles
└── Effective: Next review cycle or immediate (for S1/S2 gaps)
```

---

## Appendix: Gap Comparison Template

### Gap: SIEM SOAR SLA & Prioritization

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Priority Model | P1-P4 + Risk×Impact×Regulatory matrix | — | ❌ Not created | P1 |
| SLA Tiers | 5 tiers (Real-time → On-demand) | — | ❌ Not created | P1 |
| Service Availability | 99.9% uptime | — | ❌ Missing | P1 |
| SOC Metrics | 5-metric model (MTTD/MTTA/MTTC/MTTR-Resp/MTTR) | — | ❌ Not measured | P1 |
| Kafka HA | 3 brokers, RF=3 | 1 broker, RF=1 | ❌ Not HA | P1 |
| ES Cluster | 3-node cluster | Single node | ❌ Not HA | P1 |
| Playbook SLA | < 60s execution | Not deployed | ❌ Missing | P1 |
| OT-Safe Rules | Active enforcement | Not implemented | ❌ Missing | P1 |
| Retention | 30d hot + 60d warm + 90d cold + 1y archive | 7d hot + 90d cold | ❌ Gap | P1 |
| EPS | 15K (phased) | ~1K | ❌ 15x gap | P1 |
| Regulatory Elevator | Active | Not implemented | ❌ Missing | P2 |
| Consumer SLA Matrix | 12 consumers mapped | — | ❌ Not tracked | P2 |
| Prometheus Metrics | 13 metrics | — | ❌ Not deployed | P2 |
| SLA Dashboard | 5 views | — | ❌ Not built | P2 |
| DQ Rules | 4-tier enforcement | — | ❌ Not enforced | P2 |
| RACI Roles | 4 roles defined | — | ❌ Missing | P2 |
| Reporting Schedule | Daily/Weekly/Monthly | — | ❌ Missing | P3 |
| Review Cadence | 6 months | — | ❌ Missing | P3 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]
