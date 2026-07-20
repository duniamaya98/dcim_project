---
title: Product Description — DCIM Core Platform
created: 2026-07-06
updated: 2026-07-06
type: summary
tags: [requirement, architecture, implementation, deployment, performance, security, ha-dr, dashboard, dii, cmdb, asset-repository, analytics-ai, workflow-automation, siem-soc]
sources:
  - README.md
  - concepts/dcim-core-platform.md
  - entities/infrastructure-provisioning.md
  - entities/data-ingestion-integration.md
  - entities/asset-repository.md
  - entities/cmdb.md
  - entities/web-dashboard.md
  - entities/analytics-ai-engine.md
  - entities/workflow-automation.md
  - entities/siem-soc.md
  - reference-designs/block1-infrastructure-provisioning.md
  - reference-designs/block2-data-ingestion-integration.md
  - reference-designs/block3-asset-repository.md
  - reference-designs/block4-cmdb.md
  - reference-designs/block5-web-dashboard.md
  - reference-designs/block6-siem-soc.md
  - reference-designs/block7-analytics-ai-engine.md
  - reference-designs/block8-workflow-automation.md
  - plans/implementation-plan.md
  - FIT041 source documents: Technical Requirements, Use Case Analysis, SLA & Prioritization, Baseline, SOP Definition
confidence: high
---

# Product Description — DCIM Core Platform

## Ringkasan Dokumen

Dokumen ini menjelaskan **DCIM Core Platform** sebagai produk internal untuk mengelola infrastruktur pusat data secara terpadu. Isi dokumen disusun untuk dua kelompok pembaca:

1. **Stakeholders bisnis dan operasional** — memahami manfaat, fitur, kemampuan, dan roadmap produk.
2. **Engineers dan implementer** — memahami komponen teknis, kebutuhan hardware, dependency, setup, konfigurasi, dan acceptance checklist.

Dokumen ini dibuat berdasarkan knowledge base repo **DCIM-Wiki** serta source documents FIT041 yang mencakup technical requirements, use case analysis, SLA/prioritization, baseline, dan SOP definition.

---

## 1. Product Description

### 1.1 Definisi Produk

**DCIM Core Platform** adalah platform **Data Center Infrastructure Management** yang memberikan visibilitas, kontrol, analitik, otomatisasi, dan audit terhadap infrastruktur pusat data. Produk ini menghubungkan data dari domain fasilitas, IT infrastructure, security, workflow, dan enterprise systems ke dalam satu platform operasional yang dapat digunakan oleh NOC, SOC, Facilities, IT Operations, Capacity Planning, Security, dan Management.

Tujuan utama produk adalah membuat kondisi pusat data dapat dilihat, dianalisis, dan ditindaklanjuti dari satu ekosistem yang konsisten. Platform ini tidak hanya menampilkan data monitoring, tetapi juga menghubungkan data aset, konfigurasi, hubungan antar-komponen, log keamanan, insight AI, dan workflow operasional.

### 1.2 Masalah yang Diselesaikan

Banyak operasi data center masih menghadapi masalah berikut:

- Data perangkat tersebar di BMS, EPMS, EMS, NMS, monitoring server, virtualization platform, access control, ITSM, ERP, dan DMS.
- Tim operasi sulit mengetahui dampak insiden karena data aset, konfigurasi, dan dependensi layanan tidak selalu terhubung.
- Inventaris aset, lokasi rack/U-position, garansi, kontrak, dan status lifecycle sering tidak sinkron.
- Alert keamanan dan operasional sulit diprioritaskan tanpa konteks aset dan criticality.
- Analisis kapasitas, energi, dan prediksi kegagalan sulit dilakukan karena data historis dan real-time belum dinormalisasi.
- Prosedur remediasi masih manual, tidak konsisten, dan sulit diaudit.

DCIM Core Platform menyelesaikan masalah tersebut dengan membangun **single gateway for data ingestion**, **core data stores**, **intelligence layer**, **automation layer**, dan **presentation layer**.

### 1.3 Value Proposition

Produk ini memberikan nilai utama berikut:

| Nilai | Penjelasan Stakeholder |
|---|---|
| Visibility | Menampilkan kondisi real-time infrastruktur data center: power, cooling, network, compute, storage, security, dan workflow. |
| Control | Memberikan kontrol akses, konfigurasi, status aset, dan perubahan melalui API, RBAC, dan audit trail. |
| Automation | Mengubah alert dan insight menjadi workflow, ticket, approval, runbook, remediation, dan escalation. |
| Analytics | Menghasilkan anomaly detection, predictive maintenance, RCA, capacity forecasting, dan energy optimization. |
| Audit & Compliance | Menyimpan log, riwayat perubahan, audit trail, dan data kepatuhan untuk investigasi dan pelaporan. |

### 1.4 Target Users

| User Group | Kebutuhan Utama | Modul yang Digunakan |
|---|---|---|
| NOC Operators | Monitoring kesehatan infrastruktur, alert, kapasitas, dan availability. | Web Dashboard, CMDB, DI&I, Analytics |
| SOC Analysts | Deteksi ancaman, korelasi event, investigasi, dan compliance. | SIEM/SOC, Workflow, Dashboard SOC |
| Facilities Team | Monitoring power, cooling, environmental sensors, dan incident response fasilitas. | DI&I, Web Dashboard Facilities, Analytics |
| IT Operations | Manajemen CI, impact analysis, service mapping, workflow incident/change. | CMDB, Workflow Automation, Dashboard |
| Asset Manager | Inventaris aset, lokasi, garansi, kontrak, depresiasi, audit fisik. | Asset Repository, CMDB Reconciliation |
| Capacity Planner | Forecast kapasitas rack, daya, cooling, compute, storage, network. | Analytics & AI Engine, Dashboard KPI |
| Management | SLA, KPI, risk, cost, compliance, roadmap execution. | Management View, SLA/KPI Dashboard |
| Engineers | Implementasi, konfigurasi, observability, security, deployment. | Infrastructure, API, CI/CD, Monitoring |

### 1.5 Arsitektur Produk Secara Sederhana

```text
Source Systems
  BMS / EPMS / EMS / NMS / Server / Storage / Virtualization / Access Control / ITSM / ERP / DMS
        ↓
Data Ingestion & Integration Layer
  NiFi + Kafka + Validation + Normalization + Enrichment + DLQ + Lineage
        ↓
Core Data Stores
  CMDB + Asset Repository + Time-Series Store + SIEM/Logging Store
        ↓
Intelligence Layer
  Analytics & AI Engine: anomaly, prediction, RCA, capacity, energy, LLM/RAG explanation
        ↓
Automation Layer
  Workflow Automation: ITSM ticketing, approval, runbook, remediation, escalation
        ↓
Presentation Layer
  Web Dashboard: NOC, SOC, Facilities, CMDB Explorer, SLA/KPI, Logs, Task Board
```

### 1.6 Product Boundary

**Termasuk dalam produk:**

- Infrastructure foundation: PostgreSQL, Redis, Kafka, NiFi, Elasticsearch/OpenSearch, Prometheus, Grafana, Vault, Docker/Kubernetes.
- Data Ingestion & Integration Layer.
- Asset Repository.
- Configuration Management Database.
- Web Dashboard.
- SIEM/SOC integration.
- Analytics & AI Engine.
- Workflow Automation.
- External integrations via adapter pattern.

**Tidak diasumsikan sebagai fitur siap pakai dalam dokumen ini:**

- Native mobile application terpisah, kecuali sebagai presentation channel yang disebut di high-level design.
- Full SOAR enterprise implementation di luar SIEM/SOC dan Workflow Automation baseline.
- Integrasi vendor spesifik yang belum didefinisikan connector-nya.
- AI model yang belum memiliki data training, acceptance criteria, dan operational owner.

---

## 2. Detail Specifications

### 2.1 Layer dan Komponen Utama

| Layer | Komponen | Fungsi Utama | Technology Baseline |
|---|---|---|---|
| Infrastructure Foundation | PostgreSQL, Redis, Kafka, NiFi, Elasticsearch/OpenSearch, Prometheus, Grafana, Vault | Runtime, storage, messaging, monitoring, secret management, deployment foundation. | PostgreSQL 16, Redis 7, Kafka 3.x KRaft, NiFi 1.x, Elasticsearch 8.x/OpenSearch 2.x, Prometheus, Grafana, HashiCorp Vault, Docker/Kubernetes |
| Data Ingestion & Integration | DI&I Gateway | Mengambil data dari source systems, validasi, cleansing, normalization, enrichment, routing, DLQ, lineage. | Apache NiFi, Kafka, optional Flink/Python processors |
| Core Data Stores | Asset Repository | SSOT untuk data aset fisik, finansial, kontrak, garansi, lifecycle, dan lokasi. | PostgreSQL, Redis cache, REST API |
| Core Data Stores | CMDB | SSOT untuk CI, relationship, topology, impact analysis, service mapping, reconciliation. | PostgreSQL, Redis cache, REST API, optional graph/search layer |
| Security | SIEM/SOC | Security event ingestion, correlation, alerting, incident response, compliance reporting. | Wazuh, Syslog, Kafka, Elasticsearch/OpenSearch |
| Intelligence | Analytics & AI Engine | Time-series processing, anomaly detection, predictive maintenance, RCA, capacity forecasting, energy optimization, LLM/RAG explanation. | Kafka, Python/Flink, TimescaleDB/InfluxDB, ML framework, Grafana |
| Automation | Workflow Automation | Workflow state machine, ITSM ticketing, approvals, runbook execution, auto-remediation, escalation. | n8n/Temporal, REST/Webhook, PostgreSQL |
| Presentation | Web Dashboard | NOC/SOC/Facilities views, CMDB Explorer, SLA/KPI, Log Viewer, Task Board. | Vue 3/React, API Gateway, REST/GraphQL, RBAC/SSO |
| External Integration | Adapter Layer | Integrasi dengan ITSM, ERP, DMS, NMS, cloud, virtualization, dan vendor systems. | Adapter pattern, REST/SOAP/JDBC/SFTP/Webhook |

### 2.2 Source Systems

DCIM Core Platform menerima data dari sumber berikut:

| Domain | Contoh Source | Jenis Data |
|---|---|---|
| Facilities | BMS, EPMS, EMS | Power, cooling, temperature, humidity, UPS, PDU, CRAC/CRAH, genset, chiller |
| IT Infrastructure | NMS, server monitoring, storage monitoring | Network utilization, server health, storage capacity, device status |
| Virtualization & Cloud | VMware, Hyper-V, Proxmox, cloud platforms | VM inventory, hypervisor capacity, workload placement |
| Security & Access | Access control, surveillance, firewall, IDS/IPS, EDR | Badge events, CCTV/NVR metadata, access logs, security alerts |
| Enterprise Systems | ITSM, ERP, DMS | Tickets, changes, purchase order, asset finance, documents |
| Manual/Operational Input | Web forms, bulk import, approval input | Asset updates, CI corrections, workflow approvals |

### 2.3 Supported Protocols dan Integration Methods

| Method | Penggunaan |
|---|---|
| REST API / Webhook | Integrasi modern dengan ITSM, ERP, dashboard, CMDB, workflow, cloud, virtualization. |
| SNMP v2/v3 | PDU, UPS, network devices, environmental sensors. SNMPv3 direkomendasikan untuk keamanan. |
| Modbus/TCP, BACnet/IP | Perangkat fasilitas/OT seperti BMS, EPMS, UPS, cooling. |
| Syslog TCP/UDP/TLS | Security logs, OS logs, network logs, SIEM ingestion. |
| SSH / Remote command | Discovery script, server health checks, controlled operational commands. |
| JDBC/ODBC | Legacy database polling dan enterprise data source. |
| SFTP/FTPS | Batch file ingestion, CSV/XLSX/JSON historical load. |
| Kafka topics | Event streaming, decoupling, replay, DLQ, downstream routing. |

### 2.4 Data Flow Detail

```text
1. Source system menghasilkan event, metric, log, atau configuration snapshot.
2. NiFi connector mengambil data melalui REST, SNMP, Syslog, SSH, JDBC, atau SFTP.
3. Data masuk ke Kafka raw topic.
4. Validation Processor memeriksa schema, mandatory fields, type, range, format, dan referential integrity.
5. Data valid masuk ke validated topic; data gagal masuk ke DLQ dengan metadata error.
6. Enrichment Processor menambahkan CI_ID, Asset_ID, lokasi, owner, priority, criticality, SLA, dan context.
7. Router mengirim data ke target:
   - CMDB untuk CI dan relationship update.
   - Asset Repository untuk asset update.
   - Time-Series Store untuk metrics dan analytics.
   - SIEM/Logging Store untuk security/log events.
8. Analytics menghasilkan anomaly, prediction, RCA, capacity insight, dan energy recommendation.
9. Workflow Automation menerima trigger dan menjalankan ticketing, approval, runbook, remediation, atau escalation.
10. Dashboard menyajikan NOC/SOC/Facilities/Management view.
```

### 2.5 Core Data Models

#### 2.5.1 Event Schema

Event yang masuk ke platform harus memiliki field minimum berikut:

| Field | Keterangan |
|---|---|
| event_id | Unique identifier event, direkomendasikan UUID. |
| timestamp | Timestamp standar ISO 8601. |
| source_system | Identitas sumber seperti bms, epms, nms, server_monitor, vmware, itsm, erp, dms, api. |
| event_type | Namespace event seperti power.pdu.load, network.switch.port_down, security.login.failed. |
| payload | Data spesifik event. |
| metadata.priority | P1/P2/P3/P4. |
| metadata.category | power, cooling, environment, network, compute, storage, security, compliance, capacity, performance, availability. |
| correlation_id | ID untuk korelasi lintas event. |
| enrichment | CI, asset, location, owner, criticality, enrichment_status. |

#### 2.5.2 Asset Repository Model

| Data Area | Field Utama |
|---|---|
| Identifikasi | asset_id, serial_number, asset_tag, manufacturer, model, name |
| Lokasi | site_name, building, floor, room, rack, position_u, latitude, longitude |
| Finansial | po_number, purchase_date, purchase_cost, depreciation_method, book_value |
| Kontrak | contract_id, vendor, contract_type, SLA terms, warranty_start, warranty_end, renewal_date |
| Lifecycle | On Order, Received, Deployed, In Storage, Maintenance, Retired, Disposed |
| Audit | created_at, updated_at, changed_by, old_value, new_value, reason |

#### 2.5.3 CMDB Model

| Data Area | Field Utama |
|---|---|
| CI Core | ci_id, name, ci_type, status, owner, location_id, serial_number, ip_address, vendor, model |
| CI Types | Server, NetworkDevice, Storage, VM, Application, Service, Rack, PatchPanel, UPS, PDU |
| Relationship Types | contains, depends_on, connected_to, runs_on, part_of, managed_by, impacts |
| Lifecycle | Planned, Active, Maintenance, In Use, Retired, Disposed |
| Operations | topology, impact analysis, reconciliation, service mapping, health dashboard |

#### 2.5.4 Time-Series / Analytics Model

| Field | Keterangan |
|---|---|
| time | Timestamp metric. |
| metric_name | Nama metric seperti temperature, power_kw, cpu_usage, pue. |
| ci_id / asset_id | Konteks konfigurasi dan aset. |
| source | Source system. |
| value / unit | Nilai dan satuan. |
| tags | Metadata tambahan untuk filtering dan analytics. |

#### 2.5.5 Workflow Model

State workflow minimum:

```text
pending → in_progress → waiting_approval → approved → executing → completed
                                      ↘ rejected / cancelled
executing → failed → rollback → completed/failed
```

Workflow harus menyimpan execution_id, workflow_id, trigger_source, state, approver, actor, start_time, end_time, input/output data, error message, dan audit trail.

### 2.6 API Specification Summary

| API Group | Endpoint Pattern | Fungsi |
|---|---|---|
| CMDB API | /api/v1/cmdb/ci | CRUD CI. |
| CMDB Relationship API | /api/v1/cmdb/ci/{id}/relationships | Create/read relationship. |
| CMDB Topology API | /api/v1/cmdb/topology/{ci_id} | Topology traversal. |
| CMDB Impact API | /api/v1/cmdb/impact/{ci_id} | Impact analysis. |
| Asset API | /api/v1/assets | CRUD assets. |
| Asset Bulk API | /api/v1/assets/bulk | Bulk import CSV/JSON. |
| Asset Enrichment API | /api/v1/assets/enrich/{ci_id} | Read-optimized enrichment lookup. |
| Analytics API | /api/v1/analytics/* | Query metrics, anomaly, prediction, RCA, capacity, energy. |
| SIEM API | /api/v1/siem/* | Query security events, incidents, reports. |
| Workflow API | /api/v1/workflows/* | Create workflow, transition state, approve, execute, retry, rollback. |
| Dashboard API Gateway | /api/* or GraphQL | Central frontend entry point with auth, RBAC, rate limit, cache. |

### 2.7 Performance dan SLA Baseline

| Area | Baseline Target |
|---|---|
| DI&I uptime | 99.95% per bulan untuk critical ingestion. |
| DI&I NRT latency | ≤ 60 detik untuk P1/P2; desain streaming internal menargetkan < 1 detik untuk critical alerts. |
| DI&I throughput | Baseline FIT041: 10.000 EPS; technical baseline minimum: 5.000 records/sec sustained; Kafka design dapat ditingkatkan dengan partition/consumer scaling. |
| Data accuracy | ≥ 99.9% untuk pipeline DI&I; schema integrity 100% untuk data yang diterima target store. |
| CMDB availability | ≥ 99.9%; beberapa baseline menyebut target lebih tinggi untuk CI kritikal. |
| CMDB topology traversal | Target p99 < 200 ms untuk traversal topology. |
| CMDB impact analysis | Target p99 < 500 ms. |
| Asset Repository availability | ≥ 99.9%. |
| Asset enrichment API | Target p99 < 50 ms dengan Redis cache. |
| SIEM event ingestion | < 5 detik latency. |
| SIEM alerting | < 30 detik dari deteksi ke alert. |
| SIEM event storage | Retensi hot minimal 90 hari; cold/archive mengikuti kebijakan compliance. |
| Analytics anomaly scoring | < 500 ms per event. |
| Analytics RCA | < 30 detik per incident. |
| LLM/RAG explanation | < 5 detik per query. |
| Workflow ticket creation | < 30 detik dari trigger. |
| Workflow auto-remediation | < 2 menit untuk aksi yang memenuhi safety guard. |
| Dashboard refresh | NOC 5 detik, SOC 10 detik, Facilities 30 detik, SLA/KPI 5 menit, Task Board 30 detik. |

### 2.8 Security Specification

| Area | Requirement |
|---|---|
| Data in transit | TLS 1.2+ untuk semua API/internal traffic; Syslog TLS untuk security log bila tersedia. |
| Data at rest | Enkripsi database, log store, secrets, model registry, dan data finansial/sensitif. |
| Credential management | HashiCorp Vault atau Kubernetes Secrets; tidak menyimpan plaintext password di config file. |
| Access control | RBAC granular untuk CMDB, Asset, SIEM, Workflow, Dashboard, dan API Gateway. |
| API security | Token-based authentication, API key/OAuth2/OIDC sesuai integrasi. |
| Least privilege | Service account per connector dengan izin minimum. |
| Audit trail | Semua perubahan CI, asset, workflow, security rule, model, dan konfigurasi penting harus tercatat. |
| Network segmentation | Management VLAN, Data VLAN, DMZ VLAN, firewall default deny, allow required ports only. |

### 2.9 Observability Specification

| Area | Metric/Log |
|---|---|
| Ingestion | throughput, latency, success/failure rate, Kafka lag, DLQ count, data freshness. |
| CMDB | API latency, query latency, relationship integrity, stale CI, reconciliation success. |
| Asset | lookup latency, import success, duplicate rate, warranty/contract completeness. |
| SIEM | EPS, parsing success, correlation latency, alert count, false positive rate, log source availability. |
| Analytics | inference latency, model accuracy, model drift, feature completeness, resource utilization. |
| Workflow | workflow success rate, execution latency, backlog, failed workflow count, manual intervention rate. |
| Platform | CPU, RAM, disk, network, database health, Kafka broker health, ES cluster health, Vault status. |

---

## 3. List Features

Catatan: fitur di bawah ini adalah fitur yang sudah tercakup dalam baseline produk dan knowledge base. Dokumen ini tidak menambahkan fitur spekulatif di luar source.

### 3.1 Data Ingestion & Integration Features

- Connector untuk REST API, SNMP, Syslog, SSH, JDBC/ODBC, SFTP/FTPS, dan protokol fasilitas seperti Modbus/TCP.
- NiFi flows untuk BMS/EPMS, NMS, server/storage monitoring, virtualization/cloud, access control/surveillance.
- Kafka topics untuk raw, validated, enriched, DLQ, CMDB updates, asset updates, SIEM events, analytics metrics, workflow events.
- Unified event schema.
- Schema validation, type validation, range validation, format validation, mandatory field validation.
- Data cleansing untuk missing value, invalid format, duplicate event, dan unit normalization.
- Data enrichment dengan CI_ID, Asset_ID, location, owner, criticality, SLA, dan priority.
- Routing data ke CMDB, Asset Repository, Time-Series Store, dan SIEM.
- Dead Letter Queue untuk data gagal.
- Retry mechanism dengan backoff.
- Data lineage tracking source → validation → enrichment → store.
- Monitoring ingestion throughput, latency, Kafka lag, error rate, dan freshness.

### 3.2 Asset Repository Features

- Asset CRUD API.
- Bulk import CSV/JSON.
- Asset lifecycle tracking: On Order, Received, Deployed, In Storage, Maintenance, Retired, Disposed.
- Asset location tracking: site, building, floor, room, rack, U-position.
- Financial tracking: purchase cost, depreciation, book value, PO number.
- Warranty and contract tracking.
- Enrichment API untuk CMDB dan Analytics.
- Redis cache untuk low-latency lookup.
- Reconciliation dengan CMDB dan discovery data.
- Immutable audit trail untuk perubahan aset.
- Inventory and contract reporting.
- Duplicate prevention melalui serial number + manufacturer / asset tag.

### 3.3 CMDB Features

- CI CRUD API.
- CI data model untuk Server, NetworkDevice, Storage, VM, Application, Service, Rack, PatchPanel, UPS, PDU.
- Relationship modeling: contains, depends_on, connected_to, runs_on, part_of, managed_by, impacts.
- Topology engine untuk traversal relationship.
- Impact analysis: menjawab “what breaks if this CI fails?”
- Service mapping untuk melihat dependency end-to-end.
- Reconciliation dengan Asset Repository dan discovery data.
- CI lifecycle management.
- Data quality validation: mandatory attributes, referential integrity, orphan detection, duplicate prevention.
- Health dashboard untuk status CI dan kualitas data.
- Audit trail perubahan CI dan relationship.

### 3.4 Web Dashboard Features

- NOC View untuk infrastructure health, alerts, dan capacity.
- SOC View untuk security events, incidents, dan compliance.
- Facilities View untuk power, cooling, environmental monitoring.
- Management View untuk KPI, SLA, cost, dan capacity planning.
- CMDB Explorer dengan topology graph, CI search/filter, relationship visualization, impact view.
- SLA/KPI Dashboard.
- Log Viewer dengan filter source, severity, time range, dan export.
- Task Board untuk workflow status, assignment, priority, dan SLA countdown.
- API Gateway dengan authentication, RBAC, rate limiting, request transformation, cache.
- Responsive UI untuk desktop/tablet/mobile browser.

### 3.5 SIEM/SOC Features

- Wazuh agent-based security event ingestion.
- Syslog ingestion pipeline.
- Security event normalization ke schema terstruktur.
- Kafka topic `dcim.siem.events`.
- Elasticsearch/OpenSearch security event store.
- Rule-based correlation.
- Threshold alerting.
- Cross-source correlation.
- Incident response workflow integration.
- Severity classification.
- Forensics data collection support.
- CIS benchmark compliance checks.
- Compliance reporting.
- SOC API untuk query events, incident status, update incident, dan export reports.

### 3.6 Analytics & AI Engine Features

- Time-series ingestion dari Kafka ke TimescaleDB/InfluxDB.
- Metrics processing untuk infrastructure, power, cooling, environment, compute, storage, network.
- Anomaly detection menggunakan statistical/rule-based/ML approach seperti Z-score dan Isolation Forest.
- Predictive maintenance menggunakan time-series forecasting dan failure probability scoring.
- Root Cause Analysis berdasarkan event, metric, dan CMDB topology.
- Capacity forecasting untuk CPU, memory, storage, network, rack, power, dan cooling.
- Energy optimization termasuk PUE calculation, cooling optimization, dan power load balancing.
- Model training pipeline: data collection, feature engineering, training, registry, deployment, monitoring.
- LLM/RAG explanation layer untuk penjelasan natural language terhadap anomaly dan recommendation.
- Alert generation ke Workflow Automation.

### 3.7 Workflow Automation Features

- Workflow state machine.
- Manual, event-driven, schedule-based, webhook/API, dan AI insight triggers.
- ITSM ticketing integration.
- Multi-level approval workflows.
- Runbook engine.
- Auto-remediation dengan safety guards.
- Rollback capability.
- Escalation rules berbasis severity dan waktu.
- Notification channels: email, SMS, Slack, Teams, webhook, PagerDuty.
- Integration dengan CMDB untuk impact assessment.
- Integration dengan SIEM dan Analytics untuk incident/anomaly workflows.
- Execution log dan audit trail.

### 3.8 Infrastructure & Operations Features

- PostgreSQL primary/replica dan PgBouncer.
- Redis primary/replica dan Sentinel.
- Kafka 3.x cluster dengan KRaft, 3 brokers, replication factor 3, min.insync.replicas 2.
- NiFi data flow orchestration.
- Elasticsearch/OpenSearch untuk logging dan SIEM data store.
- Prometheus untuk metrics collection.
- Grafana untuk dashboards.
- HashiCorp Vault untuk secrets.
- Docker Compose untuk dev/staging dan Kubernetes manifests untuk production.
- Network segmentation dan firewall rules.
- Base monitoring and alerting.
- Backup/recovery baseline.

---

## 4. Functional & Non-Functional

### 4.1 Functional Requirements

Functional requirements menjelaskan apa yang harus dilakukan produk.

| Functional Area | Requirement | Outcome untuk Stakeholder |
|---|---|---|
| Data Collection | Platform harus mampu mengumpulkan data dari BMS, EPMS, EMS, NMS, server/storage, virtualization, access control, ITSM, ERP, DMS. | Data center dapat dimonitor dari satu platform. |
| Data Normalization | Platform harus menyatukan data berbeda ke schema DCIM yang konsisten. | Data dari sistem berbeda dapat dibandingkan dan dianalisis. |
| Data Quality | Platform harus memvalidasi schema, type, range, mandatory fields, referential integrity, dan duplicate. | Data yang masuk ke dashboard dan analitik dapat dipercaya. |
| Asset Management | Platform harus menyimpan data aset, lokasi, lifecycle, kontrak, garansi, dan finansial. | Asset Manager dapat melakukan audit dan planning. |
| Configuration Management | Platform harus menyimpan CI dan relationship, serta mendukung topology dan impact analysis. | Tim operasi dapat mengetahui dampak insiden/perubahan. |
| Security Monitoring | Platform harus mengumpulkan security logs, melakukan korelasi, dan menghasilkan alert. | SOC dapat melakukan investigasi dan response. |
| Analytics | Platform harus mendeteksi anomali, memprediksi kegagalan, melakukan RCA, capacity forecast, dan energy optimization. | Operasi menjadi prediktif, bukan hanya reaktif. |
| Workflow | Platform harus menjalankan ticketing, approval, runbook, remediation, escalation. | Tindakan operasional lebih cepat, konsisten, dan auditable. |
| Dashboard | Platform harus menyediakan NOC, SOC, Facilities, CMDB, SLA/KPI, Logs, dan Task views. | Stakeholders mendapat tampilan sesuai peran. |
| API & Integration | Platform harus mengekspos API aman untuk sistem internal dan eksternal. | Sistem enterprise dapat terhubung tanpa integrasi manual. |

### 4.2 Non-Functional Requirements

Non-functional requirements menjelaskan kualitas produk: cepat, aman, andal, mudah dikelola, dan siap berkembang.

| Quality Attribute | Requirement | Penjelasan Praktis |
|---|---|---|
| Performance | Latency ingestion dan query harus memenuhi target SLA per modul. | Alert kritis tidak terlambat; dashboard tetap responsif. |
| Scalability | Komponen harus dapat diskalakan horizontal: Kafka partitions, consumers, app pods, ES nodes, DB replicas. | Platform dapat mengikuti pertumbuhan perangkat dan data. |
| Reliability | Tidak boleh ada single point of failure pada komponen kritikal. | Gangguan satu node tidak menghentikan layanan utama. |
| Availability | Target availability modul kritikal berkisar 99.9%–99.95% sesuai komponen dan prioritas. | Operasi data center tetap berjalan. |
| Data Integrity | Idempotency, upsert, referential integrity, schema validation, audit trail. | Retry tidak menyebabkan duplicate dan data tidak rusak. |
| Security | TLS 1.2+, RBAC, Vault, least privilege, encryption at rest, no plaintext credentials. | Risiko security dan compliance menurun. |
| Observability | Semua komponen harus expose metrics/logs/traces dan dashboard kesehatan. | Engineers dapat melakukan troubleshooting cepat. |
| Maintainability | Konfigurasi, schema, connector, dan workflow harus versioned dan terdokumentasi. | Perubahan dapat dikontrol dan di-review. |
| Auditability | Semua perubahan penting harus tercatat immutable. | Audit dan investigasi dapat dilakukan dengan bukti lengkap. |
| Disaster Recovery | Backup, replication, RTO/RPO, dan restore test wajib tersedia. | Platform dapat dipulihkan saat insiden besar. |
| Data Governance | Ownership, data quality rule, retention, lineage, dan review process harus jelas. | Data tidak menjadi tidak terkendali seiring waktu. |

### 4.3 Prioritas dan Severity

| Priority | Definisi | Contoh |
|---|---|---|
| P1 Critical | Berdampak outage/safety atau wajib real-time. | Power failure, fire/safety alarm, critical security incident, PDU/UPS critical telemetry. |
| P2 High | Berdampak degradasi signifikan atau perlu near-real-time. | Network degradation, hypervisor capacity alert, failed sync P2. |
| P3 Medium | Berdampak planning, reporting, audit, atau batch acceptable. | Capacity reports, warranty sync, historical logs. |
| P4 Supporting | Referensi/historis/asynchronous. | Archive records, retired asset documentation, ad-hoc report. |

---

## 5. Hardware Requirements

### 5.1 Minimum Platform Sizing

Baseline minimum untuk foundation DCIM Core Platform:

| Component | Quantity | vCPU | RAM | Storage | Network |
|---|---:|---:|---:|---:|---:|
| PostgreSQL Primary | 1 | 2 | 8 GB | 100 GB SSD | 1 Gbps |
| PostgreSQL Replica | 1 | 2 | 8 GB | 100 GB SSD | 1 Gbps |
| Redis Primary | 1 | 1 | 4 GB | 20 GB SSD | 1 Gbps |
| Redis Replica | 1 | 1 | 4 GB | 20 GB SSD | 1 Gbps |
| Kafka Brokers | 3 | 2 each | 8 GB each | 200 GB SSD each | 1 Gbps |
| NiFi | 1 | 2 | 4 GB | 50 GB SSD | 1 Gbps |
| Elasticsearch/OpenSearch Nodes | 3 | 2 each | 8 GB each | 200 GB SSD each | 1 Gbps |
| Prometheus | 1 | 1 | 4 GB | 50 GB SSD | 1 Gbps |
| Grafana | 1 | 1 | 2 GB | 10 GB SSD | 1 Gbps |
| Vault | 1 | 1 | 2 GB | 20 GB SSD | 1 Gbps |
| **Total Minimum** | — | **±22 vCPU** | **±80 GB RAM** | **±1 TB SSD** | **1 Gbps minimum** |

Catatan: storage NVR/video surveillance tidak termasuk sizing DCIM core. Baseline NVR di reference design menyebut 4 TB per NVR head unit dan harus dipisahkan dari storage aplikasi DCIM.

### 5.2 Recommended Production Sizing

Untuk production HA, engineer sebaiknya merancang minimal sebagai berikut:

| Area | Recommended Production Pattern |
|---|---|
| Application Services | 2–3 app instances per service untuk HA dan rolling deployment. |
| PostgreSQL | 1 primary + 1 replica minimum; production critical dapat memakai 3-node cluster/managed HA. |
| Redis | Primary + replica + Sentinel atau managed Redis HA. |
| Kafka | 3 brokers minimum, replication factor 3, min.insync.replicas 2. |
| Elasticsearch/OpenSearch | 3 nodes minimum, ILM hot/warm/cold sesuai retensi. |
| NiFi | 1 node untuk dev/staging; production dapat menggunakan NiFi cluster bila throughput/availability menuntut. |
| CMDB | 3+ application nodes, DB HA, cache, dan search/topology optimization. |
| Asset Repository | Stateless API nodes, PostgreSQL HA, Redis cache. |
| SIEM | Wazuh Manager cluster, OpenSearch multi-node, dashboard behind load balancer bila production. |
| Analytics | CPU/RAM menyesuaikan volume metrics; GPU opsional untuk training/inference model berat. |
| Workflow | n8n/Temporal runtime dengan PostgreSQL persistent storage; high availability tergantung edition/platform. |
| Dashboard | 2 frontend/API gateway instances behind reverse proxy/load balancer. |

### 5.3 Hardware Profile by Environment

| Environment | Tujuan | Minimum Saran |
|---|---|---|
| Development | Local integration, unit testing, connector prototyping. | 8–12 vCPU, 32–48 GB RAM, 500 GB SSD; boleh single-node non-HA. |
| Staging/UAT | End-to-end testing, performance baseline, security validation. | Mendekati production kecil: 16–24 vCPU, 64–96 GB RAM, 1–2 TB SSD. |
| Production Minimum | Operasional awal dengan HA dasar. | Mengikuti minimum platform sizing: ±22 vCPU, ±80 GB RAM, ±1 TB SSD + backup storage. |
| Production Scale | Volume besar, SIEM EPS tinggi, retention panjang, analytics intensif. | Scale Kafka/ES/PostgreSQL/Analytics sesuai EPS, retention, query load, dan jumlah perangkat. |

### 5.4 Network Requirements

| Requirement | Detail |
|---|---|
| Network bandwidth | 1 Gbps minimum antar komponen core; 10 Gbps direkomendasikan untuk SIEM/log volume tinggi atau data center besar. |
| Segmentation | Management VLAN, Data VLAN, DMZ VLAN, optional NVR/OT VLAN. |
| Default policy | Firewall default deny; buka hanya port yang diperlukan. |
| TLS | TLS 1.2+ untuk API, dashboard, database connection, internal service traffic, dan log forwarding bila tersedia. |
| DNS/NTP | DNS internal stabil dan NTP/time sync wajib karena event correlation tergantung timestamp. |
| Load balancer | Dibutuhkan untuk Dashboard/API Gateway, Wazuh/OpenSearch dashboard, dan app services production. |

### 5.5 Storage & Retention Requirements

| Data Type | Storage | Retention Baseline |
|---|---|---|
| Raw/validated/enriched Kafka events | Kafka broker disks | Raw 7 hari, validated 30 hari, enriched 90 hari sesuai topic baseline. |
| DLQ | Kafka compacted topic / database error store | 30 hari minimum atau sampai reprocess selesai. |
| CMDB/Asset data | PostgreSQL | Retained sesuai lifecycle dan audit policy. |
| Audit trail | PostgreSQL/append-only store/log index | Minimal 1 tahun untuk CMDB; lebih panjang untuk asset/security sesuai compliance. |
| Time-series metrics | TimescaleDB/InfluxDB | 90 hari raw baseline; aggregate hourly/daily dapat lebih lama. |
| SIEM security logs | Elasticsearch/OpenSearch + cold storage | 90 hari hot baseline; archive dapat 1–5 tahun sesuai compliance. |
| Backup | Backup repository/object storage | Daily full/incremental + WAL/PITR sesuai RTO/RPO. |

---

## 6. Installation & Configuration Setup

### 6.1 Pre-Implementation Checklist

Sebelum implementasi, engineer harus memastikan:

- Environment target sudah jelas: dev, staging, production.
- Sizing dan kapasitas sudah disetujui.
- VLAN dan firewall policy sudah disiapkan.
- DNS, NTP, TLS certificate, dan internal CA tersedia.
- Secrets management diputuskan: Vault atau Kubernetes Secrets.
- Naming convention CI, asset, Kafka topics, database schema, dan API path disetujui.
- Source system owner sudah memberikan akses API/SNMP/Syslog/JDBC/SFTP.
- Data classification dan RBAC role matrix tersedia.
- Backup location, retention, dan restore test plan tersedia.

### 6.2 Repository dan Project Structure

Recommended structure:

```text
dcim-core/
  docker-compose.yml
  .env.example
  Makefile
  README.md
  postgres/
    init.sql
    replication.conf
  redis/
    redis.conf
    sentinel.conf
  kafka/
    kraft-config.sh
    topics.sh
  nifi/
    flows/
  elasticsearch/
    elasticsearch.yml
    ilm-policy.json
  prometheus/
    prometheus.yml
  grafana/
    dashboards/
    provisioning/
  vault/
    config.hcl
    policies/
  k8s/
    namespace.yml
    deployments/
    services/
    ingress.yml
  schemas/
    event-schema.json
    ci-schema.json
    asset-schema.json
  services/
    cmdb/
    asset-repository/
    analytics/
    workflow/
    siem/
    api-gateway/
    frontend/
```

### 6.3 Base Infrastructure Setup

#### Step 1 — Configure environment

- Copy `.env.example` ke `.env`.
- Isi database user, Kafka bootstrap servers, Redis URL, Vault address, TLS paths, and API secrets.
- Jangan menyimpan password plaintext di git.

#### Step 2 — Deploy PostgreSQL

- Deploy PostgreSQL primary dan replica.
- Aktifkan streaming replication.
- Konfigurasikan PgBouncer untuk connection pooling.
- Aktifkan SSL, SCRAM-SHA-256, logging slow query, WAL archiving, backup.
- Jalankan schema migration untuk CMDB, Asset Repository, Workflow, lineage, audit.
- Verifikasi dengan `SELECT version();`, replication status, dan backup test.

#### Step 3 — Deploy Redis

- Deploy Redis primary/replica.
- Aktifkan Sentinel untuk failover.
- Konfigurasikan persistence RDB/AOF sesuai kebutuhan.
- Verifikasi dengan `redis-cli ping` dan Sentinel status.

#### Step 4 — Deploy Kafka

- Deploy Kafka 3.x dengan KRaft mode dan 3 brokers.
- Set `default.replication.factor=3` dan `min.insync.replicas=2`.
- Buat topics:

```text
dcim.events.raw
dcim.events.validated
dcim.events.enriched
dcim.events.dlq
dcim.cmdb.updates
dcim.asset.updates
dcim.siem.events
dcim.analytics.metrics
dcim.workflow.events
```

- Verifikasi broker health, topic list, under-replicated partitions, producer/consumer test.

#### Step 5 — Deploy NiFi

- Deploy NiFi untuk data flow orchestration.
- Konfigurasikan keystore/truststore dan sensitive properties.
- Buat processor group untuk BMS/EPMS, NMS, server/storage, virtualization/cloud, access control/surveillance, ITSM/ERP/DMS.
- Set flow pattern: ingest → transform → validate → route pass/fail → publish Kafka / DLQ.
- Aktifkan provenance repository untuk lineage.

#### Step 6 — Deploy Elasticsearch/OpenSearch

- Deploy 3-node cluster untuk logging dan SIEM store.
- Configure TLS, authentication, index lifecycle management.
- Buat index pattern untuk logs, SIEM events, audit trail.
- Verifikasi cluster health.

#### Step 7 — Deploy Prometheus + Grafana

- Configure Prometheus scrape targets: Kafka, NiFi, PostgreSQL, Redis, ES/OpenSearch, app services, node exporters.
- Configure Alertmanager routes.
- Configure Grafana data sources: Prometheus, Elasticsearch/OpenSearch, PostgreSQL.
- Import base dashboard untuk infrastructure health, ingestion health, Kafka lag, database health, SIEM health.

#### Step 8 — Deploy Vault

- Deploy Vault.
- Enable audit logging.
- Buat policy dan secret paths untuk DCIM services.
- Integrasikan services dengan Vault token/role.
- Rotate credentials sesuai policy.

### 6.4 Application Services Setup

#### Step 9 — Asset Repository

- Deploy stateless API service.
- Jalankan migration tabel asset, asset_location, asset_financial, asset_contract, audit.
- Configure Redis cache TTL untuk enrichment lookup.
- Configure bulk import validation.
- Configure reconciliation job dengan CMDB/discovery.
- Acceptance checks:
  - CRUD asset berhasil.
  - Bulk import valid dan invalid file ditolak.
  - Enrichment API p99 memenuhi target.
  - Audit trail tercatat.

#### Step 10 — CMDB

- Deploy CMDB API service.
- Jalankan migration tabel ci, ci_attribute, ci_relationship, ci_lifecycle, ci_service.
- Configure CI types dan mandatory fields.
- Configure relationship rules: no self-relationship, no containment cycle, orphan detection.
- Configure topology cache dan impact cache.
- Configure reconciliation job dengan Asset Repository dan discovery.
- Acceptance checks:
  - CI CRUD berhasil.
  - Relationship create/read berhasil.
  - Topology traversal berjalan.
  - Impact analysis menghasilkan daftar CI/service terdampak.
  - Data quality checks berjalan.

#### Step 11 — DI&I Pipelines

- Load event schema.
- Configure validation rule per source.
- Configure enrichment lookup ke Asset Repository/CMDB.
- Configure routing ke CMDB, Asset Repository, Time-Series, SIEM.
- Configure DLQ and reprocessing procedure.
- Acceptance checks:
  - Source sample event masuk raw topic.
  - Data valid masuk validated/enriched topic.
  - Data invalid masuk DLQ dengan error metadata.
  - Downstream store menerima data.

#### Step 12 — SIEM/SOC

- Deploy Wazuh components/agent integration.
- Configure Syslog collector.
- Configure Kafka → Elasticsearch/OpenSearch pipeline.
- Configure normalization/parsing.
- Configure initial correlation rules.
- Configure incident trigger ke Workflow Automation.
- Acceptance checks:
  - Wazuh agent mengirim event.
  - Syslog event masuk SIEM index.
  - Failed login sample memicu alert sesuai rule.
  - Incident ticket/workflow dibuat.

#### Step 13 — Analytics & AI Engine

- Deploy time-series ingestion processor.
- Deploy TimescaleDB/InfluxDB if separate from core PostgreSQL.
- Configure metrics schema, hypertable/retention/aggregation.
- Deploy anomaly scoring service.
- Configure predictive/RCA/capacity/energy services sesuai available data.
- Configure model registry and monitoring.
- Acceptance checks:
  - Metrics masuk time-series store.
  - Anomaly detector memproses sample event.
  - RCA dapat mengambil topology context dari CMDB.
  - Insight tampil di dashboard atau memicu workflow.

#### Step 14 — Workflow Automation

- Deploy n8n/Temporal/workflow engine.
- Configure workflow state machine.
- Configure ITSM connector.
- Configure approval chains.
- Configure runbook library.
- Configure auto-remediation safety guards.
- Configure notification channels.
- Acceptance checks:
  - Workflow dibuat dari alert/manual trigger.
  - State transition valid.
  - Approval timeout dan escalation berjalan.
  - Runbook execution tercatat audit.
  - Failed action dapat retry/rollback.

#### Step 15 — Web Dashboard & API Gateway

- Deploy frontend dan API gateway.
- Configure auth, RBAC/SSO, rate limit, caching.
- Configure backend service routes: CMDB, Asset, Analytics, SIEM, Workflow.
- Configure view refresh intervals.
- Acceptance checks:
  - NOC, SOC, Facilities, CMDB Explorer, SLA/KPI, Log Viewer, Task Board dapat dibuka sesuai role.
  - API gateway menolak akses tanpa token/role.
  - Dashboard menampilkan data live dari backend.

### 6.5 Post-Install Configuration

| Area | Checklist |
|---|---|
| Security | TLS enabled, Vault integrated, RBAC roles applied, default passwords removed, audit enabled. |
| Backup | DB backup, WAL/PITR, ES snapshots, Vault backup/unseal procedure, restore test. |
| Observability | Prometheus targets UP, Grafana dashboards imported, alerts routed. |
| Data Quality | Validation rules active, DLQ monitored, lineage visible. |
| HA | Failover test PostgreSQL, Redis, Kafka broker failure, ES node failure. |
| Retention | Kafka retention, time-series retention, SIEM ILM, audit retention configured. |
| Documentation | Runbooks, integration mapping, schema docs, API docs, workflow docs updated. |

### 6.6 Delivery Acceptance Checklist

Product delivery dianggap siap UAT jika:

- Semua core services running dan health check green.
- Source connector minimal untuk BMS/EPMS atau NMS sample berhasil.
- Kafka topics dibuat dengan replication factor sesuai baseline.
- Valid data mengalir ke target store.
- Invalid data masuk DLQ.
- Asset Repository CRUD dan enrichment API berjalan.
- CMDB CI CRUD, relationship, topology, impact analysis berjalan.
- Dashboard menampilkan minimal NOC, CMDB, log, task, KPI views.
- SIEM menerima event dan menghasilkan alert sample.
- Workflow dapat membuat ticket/runbook dari alert sample.
- Analytics minimal anomaly detection baseline berjalan untuk sample metric.
- RBAC, TLS, audit trail, backup, monitoring, dan alerting aktif.

---

## 7. Roadmap

### 7.1 Prinsip Roadmap

Roadmap produk disusun dalam dua phase besar sesuai implementation plan DCIM-Wiki:

- **Phase 1 — Infrastructure & Core Foundation:** membangun platform dasar, data gateway, asset repository, dan CMDB.
- **Phase 2 — Intelligence, Automation & Presentation:** membangun dashboard, SIEM/SOC, analytics AI, workflow automation, dan external integrations.

Critical path baseline: sekitar **27.5 hari single-threaded** atau **15–18 hari dengan dua tim paralel**, bergantung ketersediaan engineer, akses source systems, dan readiness environment.

### 7.2 Roadmap Detail

| Phase | Block | Fokus | Deliverable Utama | Value untuk Stakeholders |
|---|---|---|---|---|
| Phase 0 | Product Baseline & Readiness | Finalisasi requirement, data source inventory, owner, akses, environment, security policy. | Product description, scope, RACI, source matrix, risk register. | Semua pihak memahami produk dan batas implementasi. |
| Phase 1 | Block 1 — Infrastructure Provisioning | Menyiapkan runtime dan platform foundation. | Docker/K8s, PostgreSQL, Redis, Kafka, NiFi, ES/OpenSearch, Prometheus, Grafana, Vault, network segmentation. | Fondasi teknis tersedia untuk semua modul. |
| Phase 1 | Block 2 — Data Ingestion & Integration | Membangun single gateway data. | Event schema, Kafka topics, NiFi flows, validation, enrichment, DLQ, lineage, connectors. | Data dari berbagai sistem mulai terkonsolidasi. |
| Phase 1 | Block 3 — Asset Repository | Membangun SSOT aset. | Asset data model, CRUD API, bulk import, reconciliation, audit trail, enrichment API. | Aset fisik/finansial/kontrak dapat dikelola. |
| Phase 1 | Block 4 — CMDB | Membangun SSOT CI dan relationship. | CI model, relationship, topology engine, impact analysis, reconciliation, service mapping. | Impact insiden/perubahan dapat diketahui. |
| Phase 2 | Block 5 — Web Dashboard | Membangun presentation layer. | NOC, SOC, Facilities, CMDB Explorer, SLA/KPI, Log Viewer, Task Board, RBAC/SSO. | User mendapat single pane of glass. |
| Phase 2 | Block 6 — SIEM/SOC | Membangun security monitoring dan compliance baseline. | Wazuh/Syslog ingestion, correlation engine, incident response workflow, compliance reporting, SOC API. | SOC dapat mendeteksi dan merespons insiden. |
| Phase 2 | Block 7 — Analytics & AI Engine | Membangun intelligence layer. | Time-series pipeline, anomaly detection, predictive maintenance, RCA, capacity forecasting, energy optimization, LLM/RAG. | Operasi menjadi prediktif dan berbasis insight. |
| Phase 2 | Block 8 — Workflow Automation | Membangun execution layer. | State machine, ITSM integration, approvals, runbook, auto-remediation, escalation. | Alert dapat berubah menjadi tindakan terkontrol. |
| Phase 2 | Block 9 — External Integrations | Membangun adapter ke sistem enterprise. | ITSM, ERP, DMS, NMS, cloud, virtualization adapters, health monitoring. | DCIM terhubung ke proses enterprise. |
| Phase 3 | Hardening, UAT, Production Readiness | Menguji end-to-end, security, performance, DR, observability. | UAT evidence, performance baseline, DR test, security sign-off, operations handover. | Produk siap operasi production. |
| Phase 4 | Continuous Improvement | Optimasi model, SLA, connector, automation, reporting. | Model retraining, new integrations, SLA tuning, automation expansion. | Platform berkembang sesuai kebutuhan operasi. |

### 7.3 Milestone Prioritas

| Milestone | Kriteria Selesai |
|---|---|
| M1 — Foundation Ready | Core infrastructure running, monitoring active, secrets managed, network segmented. |
| M2 — Data Gateway Ready | Minimal source connector berjalan, validation/enrichment/DLQ active, event routed to target. |
| M3 — Core Data Ready | Asset Repository dan CMDB dapat CRUD, reconcile, search, topology, impact. |
| M4 — Dashboard Ready | NOC/SOC/Facilities/CMDB/SLA/Logs/Tasks visible sesuai role. |
| M5 — Security Ready | SIEM receives logs, correlation rule active, incident workflow triggered. |
| M6 — Intelligence Ready | Time-series data processed, anomaly/prediction/RCA baseline working. |
| M7 — Automation Ready | Workflow state machine, ticketing, approval, runbook, escalation active. |
| M8 — Production Ready | HA, backup, restore, performance, security, UAT, documentation signed off. |

### 7.4 Roadmap Risiko dan Dependency

| Risk/Dependency | Dampak | Mitigasi |
|---|---|---|
| Akses source system terlambat | Connector dan testing mundur. | Tetapkan data source owner dan credential readiness sebelum sprint integrasi. |
| Data quality buruk | Dashboard/analytics tidak dipercaya. | Terapkan schema validation, DLQ, lineage, data owner sign-off. |
| CMDB relationship tidak lengkap | Impact analysis dan RCA tidak akurat. | Mulai dari critical CI P1/P2, lakukan reconciliation dan audit berkala. |
| SIEM EPS lebih besar dari sizing | ES/OpenSearch overload. | Lakukan EPS sizing, ILM, hot/warm/cold, scale indexer. |
| Workflow automation tanpa safety guard | Risiko aksi otomatis salah target. | Approval, blast-radius check, rollback, dry-run, CMDB impact check. |
| Model AI belum cukup data | Prediction tidak akurat. | Mulai dengan statistical/rule-based anomaly baseline, lalu ML setelah data historis cukup. |
| Security hardening tertunda | Risiko compliance dan exposure. | TLS, Vault, RBAC, audit trail, network segmentation sejak Phase 1. |

---

## Source Mapping Ringkas

| Section Dokumen | Source Utama |
|---|---|
| Product Description | `concepts/dcim-core-platform.md`, README, high-level design source. |
| Detail Specifications | Reference designs Block 1–8, entity pages, FIT041 Technical Requirements. |
| List Features | Entity pages dan reference designs untuk DI&I, Asset, CMDB, Dashboard, SIEM, Analytics, Workflow. |
| Functional & Non-Functional | FIT041 Baseline, Technical Requirements, SLA & Prioritization, SOP Definition. |
| Hardware Requirements | Block 1 Infrastructure Provisioning, FIT041 Technical Requirements component sizing. |
| Installation & Configuration Setup | Implementation Plan, Block 1 reference design, component reference designs. |
| Roadmap | `plans/implementation-plan.md`, `concepts/dcim-core-platform.md`. |

---

## Related Wiki Links

- [[dcim-core-platform]]
- [[infrastructure-provisioning]]
- [[data-ingestion-integration]]
- [[asset-repository]]
- [[cmdb]]
- [[web-dashboard]]
- [[siem-soc]]
- [[analytics-ai-engine]]
- [[workflow-automation]]
- [[external-integration]]
- [[service-level-objectives]]
- [[priority-severity-model]]
- [[dcim-implementation-checklist]]
- [[roadmap-strategy]]
