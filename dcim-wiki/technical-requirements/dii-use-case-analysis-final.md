---
title: "Use Case Analysis — Data Ingestion & Integration Layer (Final)"
created: 2026-06-25
updated: 2026-06-25
type: use-case-analysis
block: 2
phase: 1
status: final
confidence: high
tags: [use-case, data-ingestion, requirements-mapping, source-systems, pipeline, sla, merged]
sources:
  - IF-Use_Case_Analysis_Data_Ingestion-FIT041-20260121.md
  - dii-use-case-analysis.md
  - fit041-dii-use-case-komparasi.md
  - block2-data-ingestion-integration
  - fit041-data-ingestion-komparasi
  - data-ingestion-architecture-comparison
  - data-ingestion-integration
  - analytics-ai-engine (UC1/UC2/UC3)
purpose: >
  Final Use Case Analysis untuk DI&I Layer.
  Merged dari FIT041 Use Case Analysis (3 UCs) + DCIM-Wiki Use Case Analysis (14 UCs).
  Setiap UC dilengkapi: actors, pre-conditions, flow, source systems, data types,
  Kafka topics, SLA, data quality, consumers, acceptance criteria.
---

# Use Case Analysis — Data Ingestion & Integration Layer (Final)

> **Purpose:** Use Case Analysis komprehensif untuk DI&I Layer — merged dari FIT041 Requirements + DCIM-Wiki Implementation.
> **Cara pakai:** Review per use case untuk memahami data apa yang harus diingest, dari mana, dengan SLA berapa, dan ke mana data dikirim.
> **Depends on:** Block 2 Reference Design, FIT041 Requirements, Analytics & AI Addendum v1.2.0
> **Merge Source:** FIT041 Use Case Analysis (Jan 2026) + DCIM-Wiki Use Case Analysis (Jun 2026)
> **Traceability:** UC4, UC5, UC8 dilengkapi dari FIT041 actors/pre-conditions/flow

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Use Case Taxonomy](#2-use-case-taxonomy)
3. [Analytics & AI Use Cases (UC1–UC3)](#3-analytics--ai-use-cases-uc1uc3)
4. [Operational Use Cases (UC4–UC10)](#4-operational-use-cases-uc4uc10)
5. [Compliance & Reporting Use Cases (UC11–UC14)](#5-compliance--reporting-use-cases-uc11uc14)
6. [Source System → Use Case Matrix](#6-source-system--use-case-matrix)
7. [Data Type → Use Case Mapping](#7-data-type--use-case-mapping)
8. [Pipeline Requirements per Use Case](#8-pipeline-requirements-per-use-case)
9. [SLA & Latency Requirements](#9-sla--latency-requirements)
10. [Data Quality Requirements per Use Case](#10-data-quality-requirements-per-use-case)
11. [Downstream Consumer Mapping](#11-downstream-consumer-mapping)
12. [FIT041 Requirements Checklist](#12-fit041-requirements-checklist)
13. [Gaps & Recommendations](#13-gaps--recommendations)
14. [Acceptance Criteria](#14-acceptance-criteria)
15. [Traceability Matrix](#15-traceability-matrix)

---

## 1. Executive Summary

### Scope

DCIM Core Platform memiliki **3 kategori use case** yang membutuhkan Data Ingestion & Integration:

| Kategori | Jumlah | Prioritas Rata-rata |
|----------|--------|-------------------|
| **Analytics & AI** | 3 use case (UC1–UC3) | P1–P2 |
| **Operational** | 7 use case (UC4–UC10) | P1–P3 |
| **Compliance & Reporting** | 4 use case (UC11–UC14) | P2–P4 |
| **Total** | **14 use case** | — |

### Merge Summary

| Aspek | FIT041 | DCIM-Wiki | Merged |
|-------|--------|-----------|--------|
| Use Cases | 3 | 14 | **14** (FIT041 UCs absorbed) |
| Actors per UC | ✅ Listed | ⚠️ Implicit | **✅** (UC4/UC5/UC8 dari FIT041) |
| Pre-conditions | ✅ Listed | ⚠️ Implicit | **✅** (UC4/UC5/UC8 dari FIT041) |
| Flow Steps | ✅ 5-step | ✅ Architecture | **✅** (merged) |
| Source Systems | 7 | 13 | **13** |
| SLA Tiers | 1 (<5s) | 5 tiers | **5 tiers** |
| Data Quality | — | 5 dimensions | **5 dimensions** |
| Kafka Topics | — | 13 topics | **13 topics** |
| Acceptance Criteria | 3 | 25+ | **25+** |

### Key Findings

1. **14 source systems** harus terhubung ke DI&I layer
2. **3 processing modes** dibutuhkan: real-time (<1s), near-RT (1–30s), batch (1–60 min)
3. **13 Kafka topics** diperlukan untuk routing semua use case
4. **5 data quality dimensions** harus terpenuhi: completeness, accuracy, timeliness, consistency, validity
5. **5 SLA tiers**: Tier 1 real-time (<1s), Tier 2 near-RT (1–30s), Tier 3 near-RT (1–5min), Tier 4 batch (15–60min), Tier 5 async (>1h)
6. **FIT041 actors/pre-conditions** diadopsi untuk UC4, UC5, UC8 sebagai traceability baseline

### Quick Architecture View

```
┌─────────────────────────────────────────────────────────────────────────┐
│                     USE CASES REQUIRING DI&I                            │
│                                                                         │
│  UC1 Predictive Failure  UC2 Capacity     UC3 Energy/PUE               │
│  UC4 NOC Monitoring      UC5 SOC Events   UC6 Incident Response       │
│  UC7 Asset Lifecycle     UC8 CMDB Sync    UC9 Capacity Planning       │
│  UC10 Energy Mgmt        UC11 Compliance  UC12 Executive Reports      │
│  UC13 Workforce Mgmt     UC14 Audit Trail                              │
└─────────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     DI&I GATEWAY                                        │
│                                                                         │
│  Source Systems ──→ NiFi ──→ Kafka ──→ Validation ──→ Enrichment       │
│                        │                              │                 │
│                        ▼                              ▼                 │
│                    DLQ + Retry              Router (by event_type)      │
│                                                                         │
│  ┌──────────┬──────────┬──────────┬──────────┬──────────┐              │
│  │ CMDB     │Asset Repo│TimeSeries│  SIEM    │ AI/ML    │              │
│  └──────────┴──────────┴──────────┴──────────┴──────────┘              │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Use Case Taxonomy

### 2.1 Classification

| ID | Use Case Name | Kategori | Prioritas | Processing Mode | FIT041 Traceability |
|----|--------------|----------|-----------|-----------------|---------------------|
| UC1 | Predictive Failure Alerting | Analytics & AI | **P1** | Near-RT (5–30s) | DCIM-Wiki original |
| UC2 | Capacity Optimization | Analytics & AI | **P2** | Batch (15–60 min) | DCIM-Wiki original |
| UC3 | Energy/PUE Drift Detection | Analytics & AI | **P2** | Near-RT (1–5 min) | DCIM-Wiki original |
| UC4 | NOC Real-Time Monitoring | Operational | **P1** | Real-time (<1s) | **FIT041 UC1** |
| UC5 | Security Event Correlation (SIEM) | Operational | **P1** | Real-time (<1s) | **FIT041 UC3** |
| UC6 | Incident Response Automation | Operational | **P1** | Near-RT (5–30s) | DCIM-Wiki original |
| UC7 | Asset Lifecycle Tracking | Operational | **P2** | Near-RT (1–5 min) | DCIM-Wiki original |
| UC8 | CMDB Real-Time Sync | Operational | **P1** | Near-RT (1–10s) | **FIT041 UC2** |
| UC9 | Capacity Planning | Operational | **P3** | Batch (daily) | DCIM-Wiki original |
| UC10 | Energy Management | Operational | **P2** | Near-RT (1–5 min) | DCIM-Wiki original |
| UC11 | Regulatory Compliance Reporting | Compliance | **P2** | Batch (daily/weekly) | DCIM-Wiki original |
| UC12 | Executive Dashboard | Compliance | **P3** | Batch (hourly) | DCIM-Wiki original |
| UC13 | Workforce/Shift Management | Compliance | **P4** | Batch (daily) | DCIM-Wiki original |
| UC14 | Audit Trail | Compliance | **P3** | Async (real-time logging) | DCIM-Wiki original |

### 2.2 Priority Distribution

| Prioritas | Jumlah | Use Cases |
|-----------|--------|-----------|
| **P1 Critical** | 5 | UC1, UC4, UC5, UC6, UC8 |
| **P2 High** | 5 | UC2, UC3, UC7, UC10, UC11 |
| **P3 Medium** | 3 | UC9, UC12, UC14 |
| **P4 Supporting** | 1 | UC13 |

---

## 3. Analytics & AI Use Cases (UC1–UC3)

> Source: Addendum v1.2.0 (20 May 2026) + Block 7 Reference Design
> Traceability: DCIM-Wiki original (no FIT041 equivalent)

### 3.1 UC1 — Predictive Failure Alerting

**Objective:** Deteksi potensi kegagalan server 24–48 jam sebelum terjadi.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 30s end-to-end |
| **Model** | Isolation Forest (baseline) + LSTM/TFT (advanced) |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| IPMI/Redfish | REST | temperature, fan_speed, voltage, power | 30s |
| SNMP v2c/v3 | SNMP GET/WALK | CPU, memory, disk I/O, network | 30s |
| SMART (HDD/SSD) | SSH/SFTP | smart_*, temperature, power_on_hours | 15 min |
| OS Monitoring (Telegraf) | REST/JSON | load_avg, process_count, swap_usage | 15s |
| Failure Events (manual/system) | REST API | failure_type, component, severity | Event-driven |

#### Required Fields (Payload)

```json
{
  "hostname": "string (required)",
  "serial": "string (required)",
  "timestamp": "ISO 8601 (required)",
  "metrics": {
    "temperature_cpu": "float (°C)",
    "fan_speed": "array of int (RPM)",
    "voltage": "array of float (V)",
    "power_w": "float (W)",
    "smart_raw": "object (SMART attributes)",
    "cpu_usage": "float (%)",
    "memory_usage": "float (%)",
    "disk_io": "float (MB/s)"
  },
  "labels": {
    "failure_event": "bool",
    "failure_type": "string (enum: disk, memory, psu, fan, thermal, network)"
  }
}
```

#### Kafka Topics

| Topic | Purpose |
|-------|---------|
| `dcim.raw.server_health` | Raw telemetry dari IPMI/SNMP/SMART |
| `dcim.normalized.events` | Normalized server metrics |
| `dcim.analytics.metrics` | Enriched metrics untuk AI inference |
| `dcim.analytics.anomalies` | Anomaly scores dari model |

#### Downstream Consumers

- **AI Engine (MT-018/MT-019):** Anomaly detection + forecasting
- **Workflow Automation:** Alert creation + escalation
- **Dashboard:** Real-time anomaly visualization

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 98% (no missing hostname/serial) |
| Accuracy | ±0.5°C temperature, ±1% CPU/memory |
| Timeliness | Data age < 60s |
| Consistency | Unit standardization (°C, %, W, RPM) |
| Validity | Schema validation (event-v1.json) |

---

### 3.2 UC2 — Capacity Optimization

**Objective:** Optimasi utilisasi resource (CPU, memory, storage, network) untuk mengurangi waste.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | 15–60 min (batch acceptable) |
| **Model** | Time-series forecasting + optimization |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| Server Monitoring | REST/SNMP | CPU, memory, disk usage | 5 min |
| VMware/KVM | REST API | VM allocation, host utilization | 5 min |
| NetBox | REST API (read-only) | Asset inventory, rack capacity | 15 min |
| Storage Arrays | REST/SNMP | Volume usage, IOPS, latency | 5 min |
| Cloud (AWS/GCP/Azure) | Cloud API | Instance types, usage, cost | 1 hour |

#### Kafka Topics

| Topic | Purpose |
|-------|---------|
| `dcim.raw.capacity_metrics` | Raw utilization data |
| `dcim.normalized.events` | Normalized capacity data |
| `dcim.analytics.metrics` | Enriched untuk forecasting |

#### Downstream Consumers

- **AI Engine:** Capacity forecasting + recommendation
- **Dashboard:** Utilization heatmaps
- **ITSM:** Auto-ticket for over/under-utilized resources

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 95% (tolerance untuk VM sporadic) |
| Accuracy | ±2% utilization |
| Timeliness | Data age < 5 min |
| Consistency | Cross-reference dengan NetBox asset |
| Validity | Referential integrity (hostname → CI_ID) |

---

### 3.3 UC3 — Energy/PUE Drift Detection

**Objective:** Deteksi drift energi dan PUE (Power Usage Effectiveness) untuk optimalisasi cooling/power.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | 1–5 min (near-RT) |
| **Model** | Statistical process control + anomaly |

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| PDU (Power Distribution) | SNMP v3/REST | power_w, voltage, current, energy_kwh | 30s |
| UPS | SNMP/Modbus | input_power, output_power, battery_status | 30s |
| CRAC/CRAH | BACnet/SNMP | temperature_setpoint, fan_speed, cooling_load | 1 min |
| Environmental Sensors | MQTT/REST | temperature_inlet, temperature_outlet, humidity | 30s |
| Metering (STS/ATS) | Modbus TCP | voltage, current, frequency | 30s |
| BMS | REST API | building_temp, ambient_condition | 5 min |

#### Kafka Topics

| Topic | Purpose |
|-------|---------|
| `dcim.raw.power_metrics` | Raw power data dari PDU/UPS |
| `dcim.raw.environment_metrics` | Raw sensor environment |
| `dcim.normalized.events` | Normalized power/env data |
| `dcim.analytics.metrics` | Enriched untuk PUE calculation |

#### Downstream Consumers

- **AI Engine (UC3):** PUE drift detection + anomaly
- **Dashboard:** Real-time power/cooling visualization
- **Facilities Operations:** Alert untuk PUE deviation
- **Compliance:** Energy reporting untuk audit

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99% (P1 for power monitoring) |
| Accuracy | ±1% power, ±0.1°C temperature |
| Timeliness | Data age < 60s |
| Consistency | Unit standardization (W, V, A, °C, %) |
| Validity | No negative power values, sensor range validation |

---

## 4. Operational Use Cases (UC4–UC10)

### 4.1 UC4 — NOC Real-Time Monitoring

> **FIT041 Traceability:** Merged dari FIT041 Use Case 1 (Real-time Operational Monitoring)

**Objective:** Dashboard real-time untuk NOC operator memonitor kesehatan infrastruktur.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 1s (real-time) |
| **Source** | Semua monitoring sources |

#### Actors (from FIT041)

Power Distribution Units (PDUs), Cooling Units, Sensor Rak, Perangkat Keras Server, Perangkat Jaringan, DCIM Monitoring Dashboard

#### Pre-conditions (from FIT041)

- Data Sources telah dikonfigurasi dan dapat diakses melalui protokol yang ditentukan (SNMP, Modbus, API)
- Kafka cluster operational
- NiFi flows running

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Ingestion Data:** Mengumpulkan data time-series mentah dari semua perangkat fisik
2. **Transformasi:** Menstandarisasi unit pengukuran (mengonversi berbagai skala suhu ke Celsius), menerapkan pengidentifikasi aset umum
3. **Validasi:** Memeriksa poin data yang hilang dan values yang di luar jangkauan
4. **Integrasi:** Menggabungkan data sensor dengan data konfigurasi aset dari CMDB
5. **Output:** Mendorong data terintegrasi ke Dashboard untuk visualisasi dan alerting

#### Data Requirements

| Data Type | Source | Protocol | Frequency |
|-----------|--------|----------|-----------|
| Server Health | IPMI/SNMP | REST/SNMP | 15s |
| Network Status | NMS (Telegraf/Zabbix) | SNMP/REST | 15s |
| Power Status | PDU/UPS | SNMP | 30s |
| Environment | Sensors | MQTT | 30s |
| Storage Health | Storage Array | REST | 1 min |
| VM Status | VMware/KVM | REST | 1 min |

#### Success Criteria (from FIT041)

Data yang dinormalisasi tersedia di Asset Repository dan CMDB dalam waktu 5 detik setelah pengumpulan.

#### Processing Mode

- **Real-time** via Kafka → Flink/Stream processor
- Dashboard refresh: 5–15s interval
- Alert trigger: < 5s from event generation

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99% |
| Timeliness | < 5s |
| Validity | Schema validation |

---

### 4.2 UC5 — Security Event Correlation (SIEM)

> **FIT041 Traceability:** Merged dari FIT041 Use Case 3 (Log Data Unification for SIEM)

**Objective:** Ingest security events untuk korelasi, deteksi ancaman, dan respons.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | < 1s (real-time) |
| **Target** | SIEM/SOC (Wazuh + Elasticsearch) |

#### Actors (from FIT041)

Log Sistem Operasi (Windows Event Log, Syslog), Log Aplikasi, Log Firewall, Sistem SIEM

#### Pre-conditions (from FIT041)

- Mekanisme pengiriman log (Logstash, Filebeat) telah terinstal dan dikonfigurasi pada source systems
- Wazuh agents deployed
- Kafka topics `dcim.siem.*` created

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Data Ingestion:** Menerima pesan log melalui berbagai protokol (TCP/UDP, Syslog, CEF)
2. **Transformation:** Menerapkan aturan parsing (Grok patterns, CEF parsing) untuk mengekstrak bidang utama (timestamp, source IP, event type, severity)
3. **Filtering:** Membuang log noise yang tidak relevan dengan keamanan/operasional
4. **Enrichment:** Menambahkan konteks geografis, jaringan, dan CMDB CI mapping
5. **Output:** Meneruskan log event stream yang telah distandarisasi ke sistem SIEM

#### Source Systems

| Source | Protocol | Data Type | Frequency |
|--------|----------|-----------|-----------|
| Wazuh Agent | Syslog/CEF | Security alerts, compliance | Event-driven |
| Firewall | Syslog | Traffic logs, block events | Event-driven |
| Access Control | REST/Syslog | Badge in/out, door events | Event-driven |
| Surveillance (NVR) | ONVIF/SNIF | Motion detection, anomaly | Event-driven |
| OS Audit | Syslog | Login, sudo, cron events | Event-driven |

#### Success Criteria (from FIT041)

Log terkait keamanan yang telah difilter dan dinormalisasi tersedia di sistem SIEM untuk dianalisis.

#### Processing Mode

- **Real-time** via Kafka → Elasticsearch
- Correlation window: 5 min sliding
- Alert SLA: < 5s detection, < 30s case creation

#### Data Quality Requirements

| Dimension | Requirement |
|-----------|-------------|
| Completeness | ≥ 99.9% |
| Timeliness | < 1s |
| Consistency | MITRE ATT&CK mapping |
| Validity | CEF format validation |

---

### 4.3 UC6 — Incident Response Automation

**Objective:** Auto-response untuk incident berdasarkan severity dan playbook.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | 5–30s |
| **Target** | Workflow Automation (n8n/Temporal) |

#### Trigger Sources

| Trigger | Source | Event Type |
|---------|--------|------------|
| Anomaly Alert | AI Engine | anomaly.score > threshold |
| Security Alert | SIEM | alert.severity == S1/S2 |
| Power Alert | BMS/PDU | power_loss, overload |
| Hardware Alert | IPMI/SNMP | disk failure, fan failure |

---

### 4.4 UC7 — Asset Lifecycle Tracking

**Objective:** Track perubahan status asset dari deployment hingga decommission.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | 1–5 min |
| **Target** | Asset Repository |

#### Source Systems

| Source | Protocol | Data Type |
|--------|----------|-----------|
| Manual Entry | REST API | Status change, location move |
| Discovery (Nmap/Zabbix) | REST/SNMP | Device presence, IP assignment |
| ITSM (iTop) | REST API | Ticket status, change request |

---

### 4.5 UC8 — CMDB Real-Time Sync

> **FIT041 Traceability:** Merged dari FIT041 Use Case 2 (CMDB Configuration Updates)

**Objective:** Sinkronisasi CMDB dengan source of truth untuk CI relationships.

| Aspect | Detail |
|--------|--------|
| **Priority** | P1 Critical |
| **Latency** | 1–10s |
| **Target** | CMDB (PostgreSQL) |

#### Actors (from FIT041)

Server Provisioning System, Virtualization Management Platform, Network Discovery Tools, CMDB

#### Pre-conditions (from FIT041)

- Integration Layer memiliki kredensial dan akses ke API/basis data alat penemuan (discovery tool)
- CMDB schema deployed
- Kafka topic `dcim.cmdb.updates` created

#### Flow (merged FIT041 + DCIM-Wiki)

1. **Data Ingestion:** Mengambil snapshot konfigurasi atau log perubahan dari source
2. **Transformation:** Memetakan source atribut (Serial No, Location Tag) ke CMDB schema fields
3. **Validation:** Memverifikasi bahwa mandatory fields telah terisi dan pengidentifikasi unik konsisten
4. **Integration:** Membandingkan data baru/terbarui dengan CMDB records yang ada untuk mengidentifikasi perubahan (deltas)
5. **Output:** Memperbarui entri CMDB untuk aset yang terdampak

#### Success Criteria (from FIT041)

CMDB records diperbarui dengan konfigurasi terbaru dalam waktu 1 jam setelah perubahan pada sistem sumber.

#### Data Flow

```
Discovery/Asset Changes → DI&I Gateway → dcim.cmdb.updates → CMDB Consumer
                                                                ↓
                                                          CI Upsert/Reconcile
```

---

### 4.6 UC9 — Capacity Planning

**Objective:** Long-term capacity planning berdasarkan trend analysis.

| Aspect | Detail |
|--------|--------|
| **Priority** | P3 Medium |
| **Latency** | Batch (daily) |
| **Target** | AI Engine + BI Tools |

---

### 4.7 UC10 — Energy Management

**Objective:** Monitoring dan optimisasi konsumsi energi data center.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | 1–5 min |
| **Target** | Dashboard + Facilities |

---

## 5. Compliance & Reporting Use Cases (UC11–UC14)

### 5.1 UC11 — Regulatory Compliance Reporting

**Objective:** Generate laporan compliance untuk audit dan regulasi.

| Aspect | Detail |
|--------|--------|
| **Priority** | P2 High |
| **Latency** | Batch (daily/weekly) |
| **Target** | BI Tools + Document Management |

### 5.2 UC12 — Executive Dashboard

**Objective:** Ringkasan KPI untuk management.

| KPI | Data Source | Frequency |
|-----|------------|-----------|
| Overall PUE | Power + IT Load | Hourly |
| Uptime % | Availability logs | Daily |
| Incident Count | ITSM tickets | Daily |
| Cost/Compute | Cloud + on-prem | Weekly |

### 5.3 UC13 — Workforce/Shift Management

**Objective:** Jadwal dan efisiensi tenaga kerja operasional.

| Data | Source | Frequency |
|------|--------|-----------|
| Shift Schedule | DMS/Manual | Daily |
| Task Completion | ITSM/Workflow | Real-time |
| Personnel Location | Access Control | Event-driven |

### 5.4 UC14 — Audit Trail

**Objective:** Track semua perubahan untuk audit compliance.

| Data | Source | Retention |
|------|--------|-----------|
| CI Changes | CMDB | 7 years |
| Access Logs | Access Control | 1 year |
| Config Changes | Git/Vault | 7 years |
| Data Lineage | DI&I Layer | 1 year |

---

## 6. Source System → Use Case Matrix

| Source System | UC1 | UC2 | UC3 | UC4 | UC5 | UC6 | UC7 | UC8 | UC9 | UC10 | UC11 | UC12 | UC13 | UC14 |
|--------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|------|------|------|------|------|
| **IPMI/Redfish** | ✅ | — | — | ✅ | — | ✅ | — | — | — | — | — | — | — | — |
| **SNMP (NMS)** | ✅ | ✅ | ✅ | ✅ | — | — | — | ✅ | ✅ | ✅ | — | — | — | — |
| **SMART** | ✅ | — | — | — | — | — | — | — | — | — | — | — | — | — |
| **PDU/UPS** | — | — | ✅ | ✅ | — | ✅ | — | — | — | ✅ | ✅ | ✅ | — | — |
| **Sensors (Env)** | — | — | ✅ | ✅ | — | — | — | — | — | ✅ | ✅ | ✅ | — | — |
| **Wazuh/Firewall** | — | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | ✅ |
| **Access Control** | — | — | — | ✅ | ✅ | — | — | — | — | — | ✅ | — | ✅ | ✅ |
| **VMware/KVM** | — | ✅ | — | ✅ | — | — | — | ✅ | ✅ | — | — | — | — | — |
| **Cloud APIs** | — | ✅ | — | — | — | — | — | — | ✅ | — | — | ✅ | — | — |
| **NetBox** | — | ✅ | — | — | — | — | ✅ | ✅ | ✅ | — | — | — | — | — |
| **ITSM (iTop)** | — | — | — | — | — | ✅ | ✅ | — | — | — | ✅ | — | — | ✅ |
| **Storage Arrays** | — | ✅ | — | ✅ | — | — | — | — | ✅ | — | — | — | — | — |
| **BMS** | — | — | ✅ | ✅ | — | — | — | — | — | ✅ | ✅ | ✅ | — | — |
| **NVR (CCTV)** | — | — | — | ✅ | ✅ | — | — | — | — | — | — | — | — | — |

**Legend:** ✅ = source digunakan, — = tidak digunakan

---

## 7. Data Type → Use Case Mapping

### 7.1 Server Telemetry

| Data Field | UC1 | UC2 | UC4 | UC8 |
|-----------|-----|-----|-----|-----|
| hostname | ✅ | ✅ | ✅ | ✅ |
| serial | ✅ | — | — | ✅ |
| cpu_usage | ✅ | ✅ | ✅ | — |
| memory_usage | ✅ | ✅ | ✅ | — |
| temperature_cpu | ✅ | — | ✅ | — |
| fan_speed | ✅ | — | ✅ | — |
| disk_io | ✅ | ✅ | — | — |
| smart_raw | ✅ | — | — | — |

### 7.2 Power Metrics

| Data Field | UC3 | UC4 | UC6 | UC10 | UC11 | UC12 |
|-----------|-----|-----|-----|------|------|------|
| power_w | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| voltage | ✅ | ✅ | — | ✅ | ✅ | — |
| energy_kwh | ✅ | — | — | ✅ | ✅ | ✅ |
| pue | ✅ | — | — | ✅ | ✅ | ✅ |

### 7.3 Environment Metrics

| Data Field | UC3 | UC4 | UC10 | UC11 | UC12 |
|-----------|-----|-----|------|------|------|
| temp_inlet | ✅ | ✅ | ✅ | — | — |
| temp_outlet | ✅ | — | ✅ | — | — |
| humidity | ✅ | ✅ | ✅ | — | — |
| cooling_load | ✅ | — | ✅ | — | — |

---

## 8. Pipeline Requirements per Use Case

### 8.1 Processing Mode Summary

| Use Case | Mode | Kafka Topics (read) | Kafka Topics (write) |
|----------|------|--------------------|--------------------|
| UC1 | Near-RT | `dcim.raw.*` | `dcim.analytics.metrics`, `dcim.analytics.anomalies` |
| UC2 | Batch | `dcim.normalized.events` | `dcim.analytics.metrics` |
| UC3 | Near-RT | `dcim.raw.power_*`, `dcim.raw.env_*` | `dcim.analytics.metrics` |
| UC4 | Real-time | `dcim.events.enriched` | Dashboard (WebSocket) |
| UC5 | Real-time | Wazuh Syslog → Kafka | `dcim.siem.alerts` |
| UC6 | Near-RT | `dcim.analytics.anomalies`, `dcim.siem.alerts` | `dcim.workflow.events` |
| UC7 | Near-RT | `dcim.asset.updates` | `dcim.cmdb.updates` |
| UC8 | Near-RT | `dcim.cmdb.updates` | CMDB (PostgreSQL) |
| UC9 | Batch | `dcim.analytics.metrics` | BI Tools |
| UC10 | Near-RT | `dcim.analytics.metrics` | Dashboard |
| UC11 | Batch | Various | Reports (PDF/Excel) |
| UC12 | Batch | `dcim.analytics.metrics` | Dashboard |
| UC13 | Batch | Access Control logs | DMS |
| UC14 | Async | All topics (audit) | PostgreSQL (lineage) |

### 8.2 Resource Requirements per Use Case

| Use Case | CPU (vCPU) | Memory (GB) | Storage (GB) | Network (Mbps) |
|----------|-----------|-------------|--------------|----------------|
| UC1 | 4 | 8 | 20 | 100 |
| UC2 | 2 | 4 | 10 | 50 |
| UC3 | 2 | 4 | 10 | 50 |
| UC4 | 4 | 8 | 5 | 200 |
| UC5 | 4 | 8 | 30 | 200 |
| UC6 | 2 | 4 | 5 | 50 |
| UC7 | 1 | 2 | 2 | 20 |
| UC8 | 2 | 4 | 5 | 50 |
| UC9–14 | 2 | 4 | 10 | 50 |
| **Total** | **23** | **46** | **97** | **770** |

---

## 9. SLA & Latency Requirements

### 9.1 End-to-End Latency SLA

| Tier | Latency | Use Cases | Processing Mode |
|------|---------|-----------|-----------------|
| **Tier 1 (Real-time)** | < 1s | UC4 (NOC), UC5 (SIEM) | Kafka → Stream Processor |
| **Tier 2 (Near-RT)** | 1–30s | UC1 (Predictive), UC6 (Incident), UC8 (CMDB) | Kafka → Consumer |
| **Tier 3 (Near-RT)** | 1–5 min | UC3 (Energy), UC7 (Asset), UC10 (Energy Mgmt) | Kafka → Batch Consumer |
| **Tier 4 (Batch)** | 15–60 min | UC2 (Capacity), UC9–13 | NiFi Scheduled |
| **Tier 5 (Async)** | > 1 hour | UC14 (Audit Trail) | Background Jobs |

### 9.2 Throughput Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Total EPS | ≥ 5,000 | Events per second aggregate |
| Kafka Throughput | ≥ 100,000 msg/s | Per broker cluster |
| Batch Records | ≥ 5,000 rec/s | Per batch job |
| API Response | < 200ms p99 | Enrichment API |

### 9.3 Availability Targets

| Component | SLA | RTO | RPO |
|-----------|-----|-----|-----|
| DI&I Gateway | 99.9% | 5 min | 0 (Kafka replay) |
| Kafka Cluster | 99.95% | 30s | 0 (RF=3) |
| NiFi Cluster | 99.9% | 2 min | 1 min |
| Enrichment API | 99.9% | 1 min | N/A |

---

## 10. Data Quality Requirements per Use Case

### 10.1 Quality Dimensions by Priority

| Use Case | Completeness | Accuracy | Timeliness | Consistency | Validity |
|----------|-------------|----------|------------|-------------|----------|
| UC1 (P1) | ≥ 98% | ±0.5°C | < 60s | ✅ Unit std | ✅ Schema |
| UC2 (P2) | ≥ 95% | ±2% | < 5 min | ✅ NetBox ref | ✅ Referential |
| UC3 (P2) | ≥ 99% | ±1% | < 60s | ✅ Unit std | ✅ Range check |
| UC4 (P1) | ≥ 99% | — | < 5s | — | ✅ Schema |
| UC5 (P1) | ≥ 99.9% | — | < 1s | ✅ MITRE mapping | ✅ CEF format |
| UC6 (P1) | ≥ 98% | — | < 30s | — | ✅ Schema |
| UC8 (P1) | ≥ 99% | — | < 10s | ✅ CI_ID unique | ✅ Referential |

### 10.2 Validation Rules per Data Type

| Data Type | Mandatory Fields | Range Check | Format Check |
|-----------|-----------------|-------------|--------------|
| Server Telemetry | hostname, serial, timestamp | CPU 0–100%, temp -20–120°C | ISO 8601 timestamp |
| Power Metrics | asset_id, timestamp, power_w | power ≥ 0, voltage 0–500V | UUID format |
| Environment | asset_id, timestamp | temp -40–80°C, humidity 0–100% | ISO 8601 timestamp |
| Security Events | event_id, timestamp, severity | severity 1–4 | CEF format |
| CI Updates | ci_id, ci_type | — | UUID format |

---

## 11. Downstream Consumer Mapping

### 11.1 Consumer → Data Requirements

| Consumer | Input Topics | Required Fields | Output |
|----------|-------------|-----------------|--------|
| **CMDB** | `dcim.cmdb.updates` | ci_id, ci_type, relationships, status | CI record |
| **Asset Repository** | `dcim.asset.updates` | asset_id, serial, warranty, location | Asset record |
| **Time-Series DB** | `dcim.analytics.metrics` | timestamp, metrics.*, labels | Time-series data |
| **SIEM (Elasticsearch)** | `dcim.siem.alerts` | event_id, severity, source, timestamp | Alert index |
| **Workflow Engine** | `dcim.workflow.events` | trigger, playbook, priority | Ticket/case |
| **Dashboard** | `dcim.events.enriched` | all fields | WebSocket stream |
| **BI Tools** | Batch exports | aggregated metrics | Reports |
| **AI Training** | `dcim.analytics.metrics` | labeled data | Training dataset |

### 11.2 Kafka Topic → Consumer Group Mapping

| Topic | Consumer Groups | Parallelism |
|-------|----------------|-------------|
| `dcim.events.raw` | validation-processor | 3 |
| `dcim.events.validated` | enrichment-processor | 3 |
| `dcim.events.enriched` | router | 6 |
| `dcim.events.dlq` | dlq-handler | 1 |
| `dcim.cmdb.updates` | cmdb-consumer | 2 |
| `dcim.asset.updates` | asset-consumer | 2 |
| `dcim.analytics.metrics` | timeseries-writer, ai-consumer | 4 |
| `dcim.siem.alerts` | siem-consumer, alert-handler | 3 |
| `dcim.workflow.events` | workflow-executor | 2 |

---

## 12. FIT041 Requirements Checklist

> Source: IF-Use_Case_Analysis_Data_Ingestion-FIT041-20260121.md

Berikut adalah technical dan non-functional requirements dari FIT041 yang telah di-align dengan use case di atas:

| Requirement Type | Requirement | Aligned UCs | Status |
|-----------------|-------------|-------------|--------|
| **Technical** | Mendukung protokol SNMP v2/v3, Modbus/TCP, REST APIs, dan Syslog | UC1–UC8 | ✅ Covered |
| **Technical** | Data normalization engine yang mendukung format JSON, XML, dan format proprietary | UC1–UC8 | ✅ Covered |
| **Performance** | Latensi untuk data pemantauan real-time harus kurang dari 5 detik | UC4, UC5 | ✅ Covered (Tier 1: <1s) |
| **Performance** | Kapasitas untuk memproses peak load peristiwa/detik | All UCs | ✅ Covered (≥5,000 EPS) |
| **Security** | Transmisi data terenkripsi (TLS/SSL) untuk semua aliran data sensitif | UC5, UC14 | ✅ Covered (TLS 1.2+) |
| **Scalability** | Harus dapat diskalakan secara horizontal untuk menangani pertumbuhan data center | All UCs | ✅ Covered (HPA rules) |

---

## 13. Gaps & Recommendations

### 13.1 Identified Gaps

| # | Gap | Impact | Priority | Recommendation |
|---|-----|--------|----------|----------------|
| 1 | UC5 (SIEM) membutuhkan dedicated Kafka topics (`dcim.siem.*`) yang belum ada | P1 — SIEM tidak bisa terima data real-time | **P1** | Buat 3 topik: `dcim.siem.alerts`, `dcim.siem.cases`, `dcim.siem.actions` |
| 2 | UC1 membutuhkan `failure_events` table untuk supervised learning | P1 — Model training terhambat | **P1** | Implementasi failure_events schema + REST API |
| 3 | UC3 membutuhkan data imputation untuk noisy sensors | P2 — Data quality rendah | **P2** | Implementasi forward-fill + linear interpolation |
| 4 | Time-based enrichment (shift kerja, maintenance window) belum ada | P2 — Operational context kurang | **P2** | Tambah enrichment rules untuk shift/maintenance |
| 5 | Topology enrichment (Server→Rack→Room) belum lengkap | P2 — Impact analysis terhambat | **P2** | Extend enrichment dengan CI→Asset→Location lookup |
| 6 | ELK Stack untuk centralized logging belum ada di Block 2 | P2 — Troubleshooting sulit | **P2** | Tambah logging section atau integrasi dengan SIEM |
| 7 | Auto-scaling belum terdefinisi | P3 — Scaling manual | **P3** | Definisikan HPA rules untuk NiFi/Kafka consumers |
| 8 | Cloud provider connectors (AWS/GCP/Azure) belum ada | P3 — UC2 incomplete | **P3** | Implementasi NiFi cloud connectors untuk UC2 |

### 13.2 Recommendations

| # | Recommendation | Rationale | Effort |
|---|---------------|-----------|--------|
| 1 | Prioritaskan SIEM topics sebelum UC5 dijalankan | P1 dependency | 1 sprint |
| 2 | Implementasi failure_events untuk UC1 supervised learning | P1 untuk model accuracy | 1 sprint |
| 3 | Tambah data imputation untuk UC3 | Sensor noise unavoidable | 2 days |
| 4 | Tambah time-based enrichment | Operational context critical | 3 days |
| 5 | Extend topology enrichment | Impact analysis foundation | 1 sprint |
| 6 | ELK/logging integration | Observability gap | 1 sprint |

---

## 14. Acceptance Criteria

### 14.1 Per Use Case

| Use Case | Acceptance Criteria |
|----------|-------------------|
| **UC1** | ✅ Server metrics teringest < 30s dari source<br>✅ Anomaly score tersedia di `dcim.analytics.anomalies`<br>✅ ≥ 98% data completeness<br>✅ Model training data tersedia (≥ 30 hari) |
| **UC2** | ✅ Capacity data teringest setiap 15 menit<br>✅ Utilization heatmap tersedia di dashboard<br>✅ ≥ 95% data completeness<br>✅ NetBox asset cross-reference valid |
| **UC3** | ✅ Power/environment data teringest < 5 menit<br>✅ PUE calculation akurat ±0.01<br>✅ Sensor imputation mengurangi missing data < 2%<br>✅ Alert trigger saat PUE drift > threshold |
| **UC4** | ✅ NOC dashboard refresh < 15s<br>✅ ≥ 99% data completeness<br>✅ Real-time alert < 5s dari event<br>✅ Cover semua source systems<br>✅ Data tersedia di Asset Repository & CMDB dalam 5 detik (FIT041) |
| **UC5** | ✅ Security events teringest < 1s<br>✅ ≥ 99.9% data completeness<br>✅ Alert correlation window 5 min<br>✅ Case creation < 30s<br>✅ Log filtered & normalized tersedia di SIEM (FIT041) |
| **UC8** | ✅ CMDB records terupdate dalam 10s<br>✅ ≥ 99% data completeness<br>✅ CI_ID unique constraint valid<br>✅ Delta detection akurat<br>✅ CMDB terupdate dalam 1 jam setelah perubahan (FIT041) |

### 14.2 Cross-Cutting

| Criteria | Target |
|----------|--------|
| Total EPS | ≥ 5,000 |
| End-to-end latency (P1) | < 30s |
| Data completeness (P1) | ≥ 98% |
| DLQ rate | < 1% |
| Enrichment success rate | ≥ 95% |
| Kafka consumer lag | < 1000 msgs |
| Lineage coverage | 100% (every event tracked) |

---

## 15. Traceability Matrix

| DCIM-Wiki UC | FIT041 Equivalent | Merge Type | Enhanced With |
|-------------|-------------------|------------|---------------|
| UC1 Predictive Failure | — | DCIM-Wiki original | — |
| UC2 Capacity Optimization | — | DCIM-Wiki original | — |
| UC3 Energy/PUE Drift | — | DCIM-Wiki original | — |
| UC4 NOC Monitoring | FIT041 UC1: Real-time Operational Monitoring | **Merged** | Actors, pre-conditions, flow, success criteria |
| UC5 SIEM Correlation | FIT041 UC3: Log Data Unification for SIEM | **Merged** | Actors, pre-conditions, flow, success criteria |
| UC6 Incident Response | — | DCIM-Wiki original | — |
| UC7 Asset Lifecycle | — | DCIM-Wiki original | — |
| UC8 CMDB Sync | FIT041 UC2: CMDB Configuration Updates | **Merged** | Actors, pre-conditions, flow, success criteria |
| UC9 Capacity Planning | — | DCIM-Wiki original | — |
| UC10 Energy Management | — | DCIM-Wiki original | — |
| UC11 Compliance | — | DCIM-Wiki original | — |
| UC12 Executive Dashboard | — | DCIM-Wiki original | — |
| UC13 Workforce Mgmt | — | DCIM-Wiki original | — |
| UC14 Audit Trail | — | DCIM-Wiki original | — |

---

## References

- [[IF-Use_Case_Analysis_Data_Ingestion-FIT041-20260121]] — FIT041 Use Case Analysis (source)
- [[dii-use-case-analysis]] — DCIM-Wiki Use Case Analysis (source)
- [[fit041-dii-use-case-komparasi]] — Comparison document
- [[block2-data-ingestion-integration]] — Reference design spec
- [[fit041-data-ingestion-komparasi]] — FIT041 alignment
- [[data-ingestion-architecture-comparison]] — Architecture comparison
- [[data-ingestion-integration]] — Entity page
- Analytics & AI Addendum v1.2.0 — UC1/UC2/UC3 requirements
- Block 7 Reference Design — AI Engine implementation

---

> **Status:** Final — Merged dari FIT041 + DCIM-Wiki
> **Date:** 2026-06-25
> **Purpose:** Use Case Analysis final untuk DI&I Layer — 14 use cases, merged actors/pre-conditions/flow dari FIT041
> **Method:** MCP Sequential Thinking (4 steps) + dcim-comparison skill + document alignment
> **Merge:** FIT041 UCs absorbed into UC4/UC5/UC8 with enhanced actors, pre-conditions, flow, success criteria
> **Constraint:** Tidak mengubah dokumen existing ✅
