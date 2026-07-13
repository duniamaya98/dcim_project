---
title: "DI&I SLA & Prioritization Framework — FINAL (FIT041 + DCIM-Wiki)"
created: 2026-06-25
updated: 2026-06-25
type: framework
version: "2.0-final"
tags: [sla, prioritization, data-ingestion, dii, framework, fit041, final]
sources:
  - IF-SLA__Prioritization_Data_Ingestion-FIT041-20260126.md
  - dcim-wiki/concepts/dii-sla-prioritization-framework.md
  - dcim-wiki/concepts/priority-severity-model.md
  - dcim-wiki/technical-requirements/dii-use-case-analysis-final.md
  - dcim-wiki/reference-designs/block2-data-ingestion-integration.md
  - dcim-wiki/technical-requirements/fit041-dii-sla-prioritization-komparasi.md
confidence: high
purpose: >
  Final merged SLA & Prioritization Framework untuk DI&I component.
  Combines FIT041 requirements layer (business targets, roles, governance)
  with DCIM-Wiki implementation layer (technical logic, monitoring, automation).
  17 sections, 14 use cases, 5 SLA tiers, complete operational governance.
---

# DI&I SLA & Prioritization Framework — FINAL

> **Version:** 2.0-final (merged)
> **Sources:** FIT041 SLA (2026-01-26) + DCIM-Wiki SLA Framework (2026-06-25)
> **Status:** Complete — all gaps reconciled, no conflicts
> **Layer:** Requirements (WHAT) + Implementation (HOW)
> **Scope:** Data Ingestion & Integration component, end-to-end

---

## Table of Contents

1. [Executive Summary & Scope](#1-executive-summary--scope)
2. [SLA Definitions](#2-sla-definitions)
3. [Priority Mapping per Use Case](#3-priority-mapping-per-use-case)
4. [Priority Assignment Logic](#4-priority-assignment-logic)
5. [Impact Scoring](#5-impact-scoring)
6. [Incident Severity & Response Times](#6-incident-severity--response-times)
7. [Kafka Topic Priority](#7-kafka-topic-priority)
8. [Consumer Group Priority](#8-consumer-group-priority)
9. [SLA Monitoring & Alerting](#9-sla-monitoring--alerting)
10. [SLA Breach Handling](#10-sla-breach-handling)
11. [Data Quality per Priority](#11-data-quality-per-priority)
12. [Consumer SLA Matrix](#12-consumer-sla-matrix)
13. [Roles & Responsibilities](#13-roles--responsibilities)
14. [Reporting Framework](#14-reporting-framework)
15. [Review Process](#15-review-process)
16. [Maintenance Policy](#16-maintenance-policy)
17. [Glossary](#17-glossary)

---

## Merge Summary

| Section | Source | What Was Absorbed |
|---------|--------|-------------------|
| §1 Executive Summary | FIT041 + DCIM-Wiki | Scope, objectives, glossary |
| §2 SLA Definitions | FIT041 §2 + DCIM-Wiki §9.2 | **FIT041 adopted:** 99.95% uptime, 10K EPS, 99.9% accuracy |
| §3 Priority Mapping | DCIM-Wiki §3 + FIT041 §2.4 | 14 UCs with source coverage from FIT041 |
| §4 Auto-Assignment | DCIM-Wiki §4 | YAML rules + Python logic |
| §5 Impact Scoring | DCIM-Wiki §5 | 0-10 formula with priority + CI criticality |
| §6 Incident Severity | FIT041 §2.5 + §3.3 + DCIM-Wiki §6 | **FIT041 adopted:** Specific response/resolution times |
| §7 Kafka Topics | DCIM-Wiki §7 | 10 topics with priority + retention |
| §8 Consumer Groups | DCIM-Wiki §8 | 6 groups with max lag thresholds |
| §9 SLA Monitoring | FIT041 §5.1 + DCIM-Wiki §9 | KPIs merged with Prometheus alerts |
| §10 Breach Handling | DCIM-Wiki §10 + FIT041 §3.3 | Escalation flow with FIT041 escalation paths |
| §11 Data Quality | DCIM-Wiki §11 + FIT041 §2.3 | **FIT041 adopted:** 99.9% for P1 |
| §12 Consumer SLA | DCIM-Wiki §12 | 8 consumers with latency + protocol |
| §13 Roles | **FIT041 §4** | 5 roles (Project Owner, Integration Team, Data Source Owners, Operations, Vendor) |
| §14 Reporting | **FIT041 §5.2** | Daily/Weekly/Monthly with recipients |
| §15 Review | **FIT041 §6** | Quarterly with triggers and authority |
| §16 Maintenance | **FIT041 §2.1** | 1hr/month, 72hr notice, 02:00-03:00 WIB |
| §17 Glossary | **FIT041 §1.3** | DI&I, NRT, Batch, MTTR, EPS |

---

## 1. Executive Summary & Scope

### 1.1 Purpose

1. Menetapkan Target Tingkat Layanan (*Service Level Objectives/SLO*) yang terukur untuk ketersediaan, kinerja, dan akurasi data.
2. Menciptakan model terstruktur untuk memprioritaskan sumber data dan insiden integrasi berdasarkan dampak bisnis dan kebutuhan *real-time*.
3. Menentukan peran dan tanggung jawab yang jelas untuk pemeliharaan dan respons terhadap masalah integrasi data.

### 1.2 Scope

Dokumen ini berlaku untuk seluruh proses *end-to-end* Komponen DI&I, mencakup:
- Koneksi ke sistem sumber (BMS, EPMS, CMDB, Virtualization Platform, NMS, etc.)
- Mekanisme transmisi data (SNMP, REST, Syslog, MQTT, Modbus)
- Pipeline normalisasi dan enrichment
- Pengiriman data ke repositori utama DCIM (CMDB, Asset Repository, Time-Series DB, SIEM)

### 1.3 Component Availability Targets

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| DI&I Gateway | **99.95%** | 5 min | 0 (Kafka replay) |
| Kafka Cluster | 99.95% | 30s | 0 (RF=3) |
| NiFi Cluster | 99.9% | 2 min | 1 min |
| Enrichment API | 99.9% | 1 min | N/A |

> **FIT041 Traceability:** Uptime target 99.95%/month adopted from FIT041 §2.1. Equivalent to max 21min 53s downtime per month.

---

## 2. SLA Definitions

### 2.1 Service Availability

| Parameter | Target SLA | Justifikasi |
|-----------|-----------|-------------|
| Target *Uptime* | **99.95% (Per Bulan)** | Waktu henti maksimum 21 menit 53 detik per bulan. Waktu henti dihitung sebagai kegagalan dalam memproses data dari sumber kritis. |
| Jadwal Pemeliharaan Terjadwal | Maksimal **1 jam/bulan** | Dilakukan pada periode dampak terendah (02:00 - 03:00 WIB), dengan pemberitahuan minimal 72 jam sebelumnya kepada Data Source Owners. |
| Pemulihan Kegagalan (*Failover Time*) | Maksimal **5 Menit** | Waktu yang dibutuhkan sistem untuk beralih ke komponen cadangan setelah terdeteksi kegagalan pada *primary processing node*. |

> **FIT041 Traceability:** §2.1 adopted verbatim from FIT041.

### 2.2 Performance & Latency

#### SLA Tiers (End-to-End Latency)

| Tier | Latency | Processing Mode | Use Cases | Priority |
|------|---------|-----------------|-----------|----------|
| **Tier 1 (Real-time)** | < 1s | Kafka → Stream Processor | UC4 NOC, UC5 SIEM | P1 |
| **Tier 2 (Near-RT)** | 1–30s | Kafka → Consumer | UC1 Predictive, UC6 Incident, UC8 CMDB | P1-P2 |
| **Tier 3 (Near-RT)** | 1–5 min | Kafka → Batch Consumer | UC3 Energy, UC7 Asset, UC10 Energy Mgmt | P2-P3 |
| **Tier 4 (Batch)** | 15–60 min | NiFi Scheduled | UC2 Capacity, UC9–13 | P3-P4 |
| **Tier 5 (Async)** | > 1 hour | Background Jobs | UC14 Audit Trail | P4 |

> **FIT041 Traceability:** FIT041 §2.2 uses 2 tiers (NRT ≤60s, Batch ≤2hr). DCIM-Wiki expands to 5 tiers for operational granularity. FIT041's NRT tier encompasses DCIM-Wiki's Tier 1-3; FIT041's Batch tier encompasses Tier 4-5.

#### Throughput Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total EPS | **≥ 10,000** | Events per second aggregate |
| Kafka Throughput | ≥ 100,000 msg/s | Per broker cluster |
| Batch Records | ≥ 5,000 rec/s | Per batch job |
| API Response | < 200ms p99 | Enrichment API |

> **FIT041 Traceability:** 10,000 EPS target adopted from FIT041 §2.2. DCIM-Wiki previously targeted 5,000 EPS.

### 2.3 Data Accuracy & Integrity

| Parameter | Target SLA | Penjelasan |
|-----------|-----------|------------|
| Akurasi Data (P1) | **≥ 99.9%** | Persentase data P1 yang bebas dari kesalahan pipeline. |
| Akurasi Data (P2) | ≥ 98% | Persentase data P2 yang akurat. |
| Akurasi Data (P3) | ≥ 95% | Persentase data P3 yang akurat. |
| Akurasi Data (P4) | ≥ 90% | Best-effort accuracy. |
| Integritas Skema | **100%** | Skema data harus selalu konsisten. Penyimpangan wajib memicu *alert* Kritis. |

> **FIT041 Traceability:** 99.9% accuracy for P1 adopted from FIT041 §2.3. Tiered approach for P2-P4 from DCIM-Wiki.

---

## 3. Priority Mapping per Use Case

### 3.1 Priority Criteria (from FIT041)

Prioritas setiap Sumber Data ditentukan oleh kombinasi tiga kriteria:
1. **Dampak pada Operasi DCIM:** Konsekuensi dari *missing data*.
2. **Kebutuhan Real-Time:** Apakah data digunakan untuk peringatan/kontrol otomatis.
3. **Kompleksitas Integrasi:** Tingkat kesulitan pemeliharaan dan normalisasi data.

### 3.2 Priority Matrix

| Priority | Dampak Operasi | Kebutuhan Real-Time | Target Latency |
|----------|---------------|---------------------|----------------|
| **P1: Kritis** | Kegagalan Total (*Outage*) | **WAJIB Real-Time (NRT)** | < 1 detik |
| **P2: Tinggi** | Degradasi Layanan Signifikan | **Real-Time atau NRT** | 1–30 detik |
| **P3: Menengah** | Pengaruh pada Perencanaan | Tidak Real-Time (Batch) | 1–5 menit |
| **P4: Pendukung** | Dampak Minor/Audit | Batch atau Asinkron | > 1 jam |

### 3.3 Use Case Mapping

| Use Case | Priority | SLA Tier | Completeness | Timeliness |
|----------|----------|----------|-------------|------------|
| UC1 Predictive Failure | P2 | Tier 2 | ≥ 98% | < 60s |
| UC2 Capacity Optimization | P3 | Tier 4 | ≥ 95% | < 5 min |
| UC3 Energy / PUE Drift | P2 | Tier 3 | ≥ 99% | < 60s |
| UC4 NOC Monitoring | **P1** | **Tier 1** | ≥ 99% | < 5s |
| UC5 SIEM Correlation | **P1** | **Tier 1** | ≥ 99.9% | < 1s |
| UC6 Incident Response | P1 | Tier 2 | ≥ 98% | < 30s |
| UC7 Asset Lifecycle | P3 | Tier 3 | ≥ 95% | < 5 min |
| UC8 CMDB Sync | **P1** | Tier 2 | ≥ 99% | < 10s |
| UC9 Capacity Planning | P3 | Tier 4 | ≥ 95% | < 60 min |
| UC10 Energy Management | P3 | Tier 3 | ≥ 95% | < 5 min |
| UC11 Compliance | P4 | Tier 4 | ≥ 90% | < 60 min |
| UC12 Executive Dashboard | P3 | Tier 4 | ≥ 95% | < 60 min |
| UC13 Workforce Mgmt | P4 | Tier 4 | ≥ 90% | < 60 min |
| UC14 Audit Trail | P4 | Tier 5 | ≥ 90% | < 1 jam |

> **FIT041 Traceability:** Source system examples from FIT041 §2.4 (BMS=P1, EPMS=P1, VMware=P2, NMS=P2, CMDB=P1).

### 3.4 Source System Priority

| Sumber Data | Jenis Data | Status Integrasi | Prioritas |
|-------------|-----------|-----------------|-----------|
| Building Management System (BMS) | Suhu, Kelembaban, *Power* | Terintegrasi | **P1 (Kritis)** |
| Electrical Power Monitoring System (EPMS) | Daya (kW, kVA), Konsumsi | Terintegrasi | **P1 (Kritis)** |
| *Virtualization Platform* (VMware/Hyper-V) | *Compute* Performance, Kapasitas | Terintegrasi | P2 (Tinggi) |
| Configuration Management Database (CMDB) | Data Aset, Metadata | Real-time Sync | **P1 (Kritis)** |
| *Network Management System* (NMS) | *Network Latency*, *Utilization* | Terintegrasi | P2 (Tinggi) |

> **FIT041 Traceability:** Source coverage from FIT041 §2.4. CMDB priority upgraded from P3 (FIT041) to P1 (DCIM-Wiki) due to critical role in impact analysis.

---

## 4. Priority Assignment Logic

### 4.1 Auto-Assignment Rules

Event priority diassign otomatis oleh enrichment processor:

```yaml
# enrichment-rules.yaml (excerpt)
rules:
  - name: critical_alarm_priority
    condition:
      event_type: "*.alarm"
      payload.severity: "critical"
    action:
      set_priority: "P1"
      set_impact_score: 9

  - name: warning_alarm_priority
    condition:
      event_type: "*.alarm"
      payload.severity: "warning"
    action:
      set_priority: "P2"
      set_impact_score: 6
```

### 4.2 Python Logic

```python
def _assign_priority(self, event: dict) -> str:
    """Assign priority based on event rules."""
    event_type = event.get("event_type", "")
    severity = event.get("payload", {}).get("severity", "")

    if severity == "critical" or "alarm" in event_type:
        return "P1"
    elif severity == "warning":
        return "P2"
    elif "metrics" in event_type:
        return "P3"
    else:
        return "P4"
```

### 4.3 Priority Override

Source system dapat override priority via field `metadata.priority`. Jika tidak di-set, default = `P3`.

> **Source:** DCIM-Wiki §4. FIT041 does not define auto-assignment logic.

---

## 5. Impact Scoring

Impact score (0–10) digunakan untuk triage dan eskalasi:

```python
def _calculate_impact(self, event: dict) -> float:
    base = 5.0

    # Priority adjustment
    priority = event.get("metadata", {}).get("priority", "P3")
    priority_adj = {"P1": 4, "P2": 2, "P3": 0, "P4": -2}
    base += priority_adj.get(priority, 0)

    # CI criticality adjustment
    ci_criticality = event.get("enrichment", {}).get("ci_criticality", "medium")
    criticality_adj = {"critical": 2, "high": 1, "medium": 0, "low": -1}
    base += criticality_adj.get(ci_criticality, 0)

    return max(0, min(10, base))
```

### Impact Score Thresholds

| Score | Action |
|-------|--------|
| 8–10 | Immediate escalation, P1 ticket |
| 5–7 | Fast track, P2 ticket |
| 2–4 | Normal queue, P3 ticket |
| 0–1 | Low priority, background processing |

> **Source:** DCIM-Wiki §5. FIT041 does not define impact scoring.

---

## 6. Incident Severity & Response Times

### 6.1 Severity Classification

| Severity | Klasifikasi Insiden | Waktu Respons Target | Waktu Resolusi Target (MTTR) |
|----------|-------------------|---------------------|------------------------------|
| **S1 (Kritis)** | Kegagalan Total DI&I atau kegagalan *ingestion* dari Sumber P1 (misalnya, BMS/EPMS *down*). | **15 Menit** | **2 Jam** |
| **S2 (Tinggi)** | Kegagalan *ingestion* dari Sumber P2; *Throughput* di bawah 50% dari target (10.000 EPS). | **30 Menit** | **4 Jam** |
| **S3 (Menengah)** | Latensi NRT di atas 60 detik secara konsisten; Kegagalan *ingestion* dari Sumber P3/P4. | **1 Jam** | **1 Hari Kerja** |
| **S4 (Rendah)** | Masalah Akurasi Data minor (<0.1%), permintaan *ad-hoc* laporan *data quality*. | **2 Jam** | **3 Hari Kerja** |

> **FIT041 Traceability:** Response and resolution times adopted from FIT041 §2.5.

### 6.2 Escalation Matrix

| Severity | Jalur Eskalasi | Kontak Eskalasi |
|----------|---------------|-----------------|
| **S1 (Kritis)** | Tier 1 (DI&I Engineer) → Tier 2 (DCIM Architect) → **Project Owner & Vendor** | Project Owner |
| **S2 (Tinggi)** | Tier 1 (DI&I Engineer) → Tier 2 (DCIM Architect) | DCIM Architect |
| **S3/4** | Tier 1 (DI&I Engineer) | Operations Team Lead |

> **FIT041 Traceability:** Escalation paths from FIT041 §3.3.

### 6.3 SLA Breach → Ticket Routing

| Priority | Ticket Type | Assignment | Resolution SLA |
|----------|------------|------------|----------------|
| P1 | Incident | NOC Lead → On-Call | 1 jam |
| P2 | Problem | Data Engineer | 4 jam |
| P3 | Service Request | Data Engineer | 1 hari kerja |
| P4 | Task | Scheduled | Sprint berikutnya |

> **Source:** DCIM-Wiki §10.3.

---

## 7. Kafka Topic Priority

| Topic | Priority | Partition Key | Retention |
|-------|----------|---------------|-----------|
| `dcim.siem.alerts` | P1 | event_id | 30 hari |
| `dcim.noc.events` | P1 | device_id | 7 hari |
| `dcim.cmdb.updates` | P1 | ci_id | 90 hari |
| `dcim.analytics.anomalies` | P1 | device_id | 90 hari |
| `dcim.analytics.metrics` | P2 | device_id | 30 hari |
| `dcim.workflow.events` | P2 | entity_id | 90 hari |
| `dcim.asset.updates` | P2 | asset_id | 90 hari |
| `dcim.events.enriched` | P2 | event_id | 7 hari |
| `dcim.dlq` | P1 | event_id | 30 hari |
| `dcim.lineage` | P4 | event_id | 1 tahun |

> **Source:** DCIM-Wiki §7. FIT041 does not define Kafka topics.

---

## 8. Consumer Group Priority

Kafka consumer groups diprioritaskan via partition assignment:

| Consumer Group | Topic | Priority | Max Lag Before Alert |
|---------------|-------|----------|---------------------|
| `dii-siem-consumer` | `dcim.siem.alerts` | P1 | 100 msgs |
| `dii-noc-consumer` | `dcim.noc.events` | P1 | 100 msgs |
| `dii-cmdb-consumer` | `dcim.cmdb.updates` | P1 | 500 msgs |
| `dii-analytics-consumer` | `dcim.analytics.metrics` | P2 | 1,000 msgs |
| `dii-workflow-consumer` | `dcim.workflow.events` | P2 | 500 msgs |
| `dii-batch-consumer` | batch topics | P3–P4 | 5,000 msgs |

> **Source:** DCIM-Wiki §8. FIT041 does not define consumer groups.

---

## 9. SLA Monitoring & Alerting

### 9.1 KPIs (from FIT041)

| KPI | Definisi | Target Kepatuhan |
|-----|---------|-----------------|
| **Ketersediaan Layanan** | Persentase *uptime* *pipeline* DI&I. | > 99.95% |
| **MTTD (Mean Time to Detect)** | Waktu rata-rata dari kegagalan *ingestion* hingga *alert* terdeteksi. | < 5 Menit |
| **MTTR (Mean Time to Resolution)** | Waktu rata-rata untuk memperbaiki dan memulihkan kegagalan DI&I. | Harus sesuai dengan SLA §6.1 |
| **Latensi NRT Kepatuhan** | Persentase data P1 dan P2 yang diproses dalam waktu ≤ target tier. | > 99.5% |
| **Data Accuracy Kepatuhan** | Persentase data yang bebas dari kesalahan *pipeline*. | ≥ 99.9% |

> **FIT041 Traceability:** KPIs adopted from FIT041 §5.1.

### 9.2 Per-Stage Latency SLA

| Stage | SLA | Alert Threshold |
|-------|-----|----------------|
| Validation | p99 < 100ms | > 100ms |
| Enrichment | p99 < 50ms | > 50ms |
| Kafka publish | p99 < 10ms | > 10ms |
| Consumer lag | < 1,000 msgs | > 1,000 msgs |

> **Source:** DCIM-Wiki §9.1.

### 9.3 Prometheus Alert Rules

```yaml
groups:
  - name: dii_sla_alerts
    rules:
      - alert: ValidationLatencyHigh
        expr: histogram_quantile(0.99, rate(dii_validation_latency_seconds_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Validation p99 latency > 100ms"

      - alert: EnrichmentLatencyHigh
        expr: histogram_quantile(0.99, rate(dii_enrichment_latency_seconds_bucket[5m])) > 0.05
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Enrichment p99 latency > 50ms"

      - alert: KafkaConsumerLagHigh
        expr: kafka_consumer_group_lag > 1000
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Kafka consumer lag > 1000 msgs"
```

> **Source:** DCIM-Wiki §9.3. FIT041 does not define Prometheus alerts.

---

## 10. SLA Breach Handling

### 10.1 Breach Detection Flow

```
Metric Check → Threshold Breach → Alert Firing → Escalation
                                                      │
                                          ┌───────────┼───────────┐
                                          ▼           ▼           ▼
                                      S3: Auto    S2: Pager    S1: War
                                      Remediate   Alert        Room
```

### 10.2 Escalation Matrix

| SLA Tier | Breach → Auto Action | Breach → Escalation |
|----------|---------------------|---------------------|
| Tier 1 | Auto-retry + DLQ | PagerDuty P1, on-call < 5 min |
| Tier 2 | Auto-retry + DLQ | Slack alert, owner < 15 min |
| Tier 3 | Batch retry next cycle | Dashboard flag, owner < 1 hour |
| Tier 4 | Retry in next batch | Email report, next business day |
| Tier 5 | Log + archive | Monthly review |

> **Source:** DCIM-Wiki §10.2 + FIT041 §3.3 escalation paths.

### 10.3 Incident Escalation (from FIT041)

Eskalasi dilakukan jika Waktu Respons Target (§6.1) terlewati:

| Severity | Jalur Eskalasi (Jika Target Respons Terlewati 30 Menit) | Kontak |
|----------|--------------------------------------------------------|--------|
| **S1** | Tier 1 → Tier 2 → **Project Owner & Vendor** | Project Owner |
| **S2** | Tier 1 → Tier 2 | DCIM Architect |
| **S3/4** | Tier 1 | Operations Team Lead |

> **FIT041 Traceability:** Escalation paths from FIT041 §3.3.

---

## 11. Data Quality per Priority

| Priority | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| **P1** | ≥ 99% | **≥ 99.9%** | < 5s–30s | Strict | Schema + Referential |
| **P2** | ≥ 98% | ≥ 98% | < 1–60s | Cross-system | Schema + Business rules |
| **P3** | ≥ 95% | ≥ 95% | < 5–60 min | Batch-valid | Schema |
| **P4** | ≥ 90% | Best-effort | < 1–24 jam | Async-valid | Basic format |

> **FIT041 Traceability:** P1 accuracy 99.9% adopted from FIT041 §2.3. Tiered approach for P2-P4 from DCIM-Wiki.

---

## 12. Consumer SLA Matrix

| Consumer | Input Topics | Required SLA | Protocol |
|----------|-------------|-------------|----------|
| **CMDB** | `dcim.cmdb.updates` | Tier 2 (< 10s) | REST API |
| **Asset Repository** | `dcim.asset.updates` | Tier 3 (< 5 min) | REST API |
| **Time-Series DB** | `dcim.analytics.metrics` | Tier 2 (< 30s) | Direct write |
| **SIEM (ES)** | `dcim.siem.alerts` | Tier 1 (< 1s) | Bulk API |
| **Workflow Engine** | `dcim.workflow.events` | Tier 2 (< 30s) | REST API |
| **Dashboard** | `dcim.events.enriched` | Tier 1 (< 5s) | WebSocket |
| **BI Tools** | Batch exports | Tier 4 (< 60 min) | Export API |
| **AI Training** | `dcim.analytics.metrics` | Tier 5 (> 1 jam) | File export |

> **Source:** DCIM-Wiki §12. FIT041 does not define consumer SLA matrix.

---

## 13. Roles & Responsibilities

| Peran | Tanggung Jawab Utama terkait DI&I |
|-------|----------------------------------|
| **Project Owner (DCIM)** | Otoritas tertinggi untuk persetujuan SLA, memastikan DI&I mendukung tujuan DCIM, dan penerima laporan insiden kritis. |
| **Integration Team (DI&I Engineer)** | Pemeliharaan *pipeline* DI&I, pemantauan *throughput* (§2.2), *troubleshooting* insiden Severity 1 & 2, dan memastikan Akurasi Data (§2.3). |
| **Data Source Owners** | Memastikan ketersediaan *API/Gateway* Sumber Data, menyediakan kredensial akses, dan berkoordinasi dengan *Integration Team* untuk perubahan skema (*schema changes*). |
| **Operations Team** | Pemantauan *dashboard* DI&I harian, *triage* awal insiden Severity 3 & 4, dan implementasi *patch* atau *restart* jika diminta oleh *Integration Team*. |
| **Vendor (Jika Ada)** | Menyediakan *update* *middleware* DI&I, dukungan teknis untuk masalah platform, dan bantuan dalam kalibrasi kinerja. |

> **FIT041 Traceability:** Roles adopted from FIT041 §4.

---

## 14. Reporting Framework

### 14.1 Report Types

| Jenis Laporan | Frekuensi | Penerima | Fokus Konten |
|--------------|-----------|----------|-------------|
| **Laporan Harian** | Harian (Awal Hari Kerja) | Integration Team, Operations Team | Status *Ingestion* Sumber P1 & P2, daftar *backlog* data (jika ada), insiden terbuka Severity 1 & 2. |
| **Laporan Mingguan** | Setiap Hari Senin | Integration Team, DCIM Architect | Analisis tren *throughput*, ringkasan MTTR/MTTD, dan identifikasi sumber data yang rentan. |
| **Laporan Bulanan** | Tanggal [Date] Setiap Bulan | Project Owner, Vendor | Kepatuhan SLA (KPI §9.1), volume data total, dan rekomendasi peningkatan arsitektur. |

> **FIT041 Traceability:** Reporting framework adopted from FIT041 §5.2.

---

## 15. Review Process

**Periode Tinjauan:** Dokumen ini akan ditinjau secara formal **setiap 3 bulan (Quarterly)** atau segera setelah terjadi:
1. Penambahan/penghapusan Sumber Data P1/P2 baru
2. Perubahan signifikan pada arsitektur DI&I
3. Kegagalan SLA *Kritis* berulang

**Otoritas Revisi:** Setiap revisi harus disetujui oleh **Project Owner (DCIM)**.

> **FIT041 Traceability:** Review process adopted from FIT041 §6.

---

## 16. Maintenance Policy

| Parameter | Kebijakan |
|-----------|----------|
| **Jadwal Pemeliharaan** | Maksimal 1 jam/bulan |
| **Periode Dampak Terendah** | 02:00 - 03:00 WIB |
| **Pemberitahuan** | Minimal 72 jam sebelumnya kepada Data Source Owners |
| **Pemulihan Kegagalan** | Maksimal 5 menit (failover) |

> **FIT041 Traceability:** Maintenance policy adopted from FIT041 §2.1.

---

## 17. Glossary

| Istilah | Penjelasan |
|---------|-----------|
| **DI&I** | Data Ingestion & Integration. Komponen yang mengumpulkan dan memproses data dari sumber. |
| **NRT** | Near Real-Time. Data yang memiliki latensi sangat rendah (≤60 detik), penting untuk pemantauan fisik dan peringatan. |
| **Batch** | Proses data periodik yang tidak memerlukan latensi NRT, seperti data historis atau data konfigurasi. |
| **MTTR** | Mean Time to Resolution. Waktu rata-rata untuk memperbaiki dan memulihkan kegagalan layanan atau data. |
| **MTTD** | Mean Time to Detect. Waktu rata-rata dari kegagalan hingga alert terdeteksi. |
| **EPS** | Events per Second. Metrik *throughput* yang mengukur volume data yang dapat diproses per detik. |
| **DLQ** | Dead Letter Queue. Topic untuk event yang gagal diproses. |
| **RTO** | Recovery Time Objective. Waktu maksimal pemulihan setelah kegagalan. |
| **RPO** | Recovery Point Objective. Maksimal data loss yang dapat diterima. |
| **SLO** | Service Level Objective. Target kinerja yang terukur. |
| **SLA** | Service Level Agreement. Perjanjian tingkat layanan. |

> **FIT041 Traceability:** Glossary adopted from FIT041 §1.3 with additions from DCIM-Wiki.

---

## Related

- [[IF-SLA__Prioritization_Data_Ingestion-FIT041-20260126]] — FIT041 source document
- [[dii-sla-prioritization-framework]] — DCIM-Wiki SLA framework (superseded by this FINAL)
- [[priority-severity-model]] — Global priority & severity model
- [[dii-use-case-analysis-final]] — DI&I use case analysis (14 UCs)
- [[block2-data-ingestion-integration]] — DI&I reference design
- [[data-quality-framework]] — Data quality dimensions
- [[fit041-dii-sla-prioritization-komparasi]] — Comparison document
