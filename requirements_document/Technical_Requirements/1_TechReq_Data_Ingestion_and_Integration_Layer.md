# [cite_start]Technical Requirements - Data Ingestion & Integration Layer [cite: 2]

## [cite_start]1. Pendahuluan [cite: 3]
[cite_start]Dokumen ini menetapkan persyaratan teknis untuk komponen Data Ingestion & Integration Layer dalam Proyek Manajemen Infrastruktur Pusat Data (DCIM). [cite: 4] [cite_start]Layer ini bertanggung jawab untuk mengumpulkan, memproses, menormalkan, dan mengirimkan data Configuration Item (CI), monitoring, dan operasional dari berbagai sumber ke Configuration Management Database (CMDB) dan komponen DCIM inti lainnya. [cite: 5]

### 1.1. [cite_start]Konteks Proyek [cite: 6]
| Field | Description |
|---|---|
| Nama Proyek | [cite_start]Data Center Infrastructure Management (DCIM) Core Platform [cite: 7] |
| Komponen | [cite_start]Data Ingestion & Integration Layer [cite: 7] |
| Versi Dokumen | [cite_start]1.0 [cite: 7] |
| Tanggal Pembuatan | [cite_start]20 Jan 2026 [cite: 7] |
| Disiapkan Oleh | [cite_start]Imam Syauqi Achmad [cite: 7] |

## [cite_start]2. Kebutuhan Fungsional [cite: 8]
[cite_start]The Data Ingestion & Integration Layer must fulfill the following core functions: [cite: 9]

### 2.1. [cite_start]Data Source Connectivity [cite: 10]
[cite_start]**Requirement 2.1.1 (Protocol Support):** [cite: 11]
[cite_start]Harus support berbagai macam protokol agar lebih fleksible saat ada penambahan protokol baru: [cite: 12]
* [cite_start]REST API - Polling/Webhook - Apache Nifi, Kafka Connect HTTP [cite: 13]
* [cite_start]SNMP - Polling device - Telegraf, snmp_exporter [cite: 14]
* [cite_start]SSH - Remote Command / Script - Ansible, Custom Python script [cite: 15]
* [cite_start]JDBC/ODBC - Database polling - Kafka connect JDBC [cite: 16]
* [cite_start]Syslog - Real-time log - Filebeat / Logstash [cite: 17]
* [cite_start]SFTP/FTPS - File-based ingestion - Nifi, Filebeat [cite: 18]

[cite_start]**Requirement 2.1.2 (Connectors):** [cite: 19]
* [cite_start]REST API + NiFi untuk NMS (Zabbix/Prometheus/Grafana) [cite: 20]
* [cite_start]SNMP + Telegraf untuk PDU, UPS, atau sensor lingkungan [cite: 21]
* [cite_start]REST API untuk VMWare / Hyper-V / Proxmox [cite: 22]
* [cite_start]JDBC / REST untuk Legacy asset management [cite: 23]

### 2.2. [cite_start]Data Transformation & Normalization [cite: 24]
[cite_start]**Requirement 2.2.1 (Mapping):** [cite: 25]
[cite_start]Gunakan DCIM Common Data Model (CDM) [cite: 26]
[cite_start]CI Type - Mandatory Fields: [cite: 27]
* [cite_start]Server: hostname, serial, rack, power_state [cite: 28]
* [cite_start]Network: hostname, ip, model [cite: 29]
* [cite_start]PDU: outlet, load, capacity [cite: 30]
* [cite_start]Sensor: metric, value, unit [cite: 31]

[cite_start]Tentukan CDM schema CMDB [cite: 32]
[cite_start]Buat mapping table: source.hostname → cmdb.ci_name [cite: 33][cite_start], source.ip → cmdb.primary_ip [cite: 34][cite_start], source.rack → cmdb.location.rack [cite: 35]
[cite_start]Tools: Apache NiFi (Record Processor) [cite: 36, 37][cite_start], StreamSets [cite: 38]

[cite_start]**Requirement 2.2.2 (Data Cleansing):** Must include capabilities for data cleansing, error handling (e.g., missing values, incorrect format), and standardization (e.g., unit conversion, case transformation) before insertion into the CMDB. [cite: 39]

[cite_start]Validasi schema [cite: 40]
| Jenis Validasi | Contoh DCIM |
|---|---|
| [cite_start]Mandatory field | ci_id , hostname , location [cite: 41] |
| [cite_start]Data type | power_kw harus numeric [cite: 41] |
| [cite_start]Range | suhu 0–60°C [cite: 41] |
| Format | [cite_start]IP address, MAC [cite: 41] |
| [cite_start]Referential | rack_id harus ada [cite: 41] |

[cite_start]Tools: Apache NiFi (ValidateRecord, ValidateXml, ValidateJson) [cite: 42, 43][cite_start], Python (pydantic, jsonschema) [cite: 44]
[cite_start]Error Handling: Default value untuk missing field [cite: 45, 46][cite_start], Konversi unit (W → kW, °C → Kelvin jika perlu) [cite: 47]

| Error | Contoh |
|---|---|
| [cite_start]Missing value | rack_id kosong [cite: 48] |
| Invalid format | [cite_start]IP salah [cite: 48] |
| [cite_start]Mapping gagal | field tidak dikenal [cite: 48] |
| [cite_start]Lookup gagal | owner tidak ditemukan [cite: 48] |

[cite_start]Cara menangani: Tag error [cite: 49, 50][cite_start], Kirim ke DLQ [cite: 51][cite_start], Alert ke ops [cite: 52]
[cite_start]Fungsi - Tools: DLQ - Kafka topic [cite: 53, 54][cite_start], Error store - PostgreSQL [cite: 55][cite_start], Alert - Alertmanager (Prometheus) [cite: 56]
[cite_start]Normalisasi string [cite: 57][cite_start], Unit Conversion [cite: 58]

| Source | DCIM Standard |
|---|---|
| 12000 W | [cite_start]12 kW [cite: 59] |
| 35 °C | [cite_start]308.15 K (jika perlu) [cite: 59] |
| 80 % | [cite_start]0.8 [cite: 59] |

[cite_start]Naming Convention [cite: 60]
| Source | Standard |
|---|---|
| Rack-01 | [cite_start]RACK_01 [cite: 61] |
| srv-01.dc.local | [cite_start]SRV-01 [cite: 61] |

[cite_start]Boolean & Status [cite: 62]
| Source | Standard |
|---|---|
[cite_start]| yes/no | true/false [cite: 63] |
| UP/DOWN | [cite_start]1 / 0 [cite: 63] |

[cite_start]Tools: NiFi (Update Record, ReplaceText, ExecuteScript) [cite: 64, 65][cite_start], Flink (Map & Filler) [cite: 66]

[cite_start]**Requirement 2.2.3 (Enrichment):** Must be able to enrich ingested data with contextual information (e.g., location, owner from Asset Repository) using lookup tables or external services. [cite: 67]
[cite_start]Enrichment tidak boleh overwrite source data. [cite: 68]
[cite_start]Reference / Lookup Enrichment, menambahkan atribut dari master data. [cite: 69]

| Field Baru | Diambil Dari |
|---|---|
| location.site | [cite_start]Site master [cite: 70] |
| rack.row | [cite_start]Rack DB [cite: 70] |
| owner | [cite_start]Asset Repository [cite: 70] |
| business_unit | [cite_start]CMDB master [cite: 70] |

[cite_start]Gunakan lookup key (hostname, asset_id, serial number). [cite: 71] [cite_start]Join ke tabel referensi. [cite: 72]
[cite_start]Tools: Apache NiFi (LookupRecord) [cite: 73, 74][cite_start], Redis (Cache lookup) [cite: 75][cite_start], PostgreSQL (Reference DB) [cite: 76][cite_start], REST API (External CMDB) [cite: 77]

[cite_start]Topology & Relationship Enrichment, membangun relasi antar CI. [cite: 81]
| CI | Relasi |
|---|---|
| Server | [cite_start]Mounted in Rack [cite: 82] |
| Rack | [cite_start]Located in Room [cite: 82] |
| Server | [cite_start]Powered by PDU [cite: 82] |
| VM | [cite_start]Runs on Host [cite: 82] |

[cite_start]Identifikasi foreign key [cite: 83][cite_start], Bentuk relationship object [cite: 84][cite_start], Simpan ke CMDB [cite: 85]
[cite_start]Tools: NiFi (ExecuteScript) [cite: 86, 87][cite_start], Python grahp logic [cite: 88][cite_start], CMDB Relationship API [cite: 89]

[cite_start]Contextual Enrichment (Environment & Business), menambahkan makna operasional dan bisnis. [cite: 97]
| Atribut | Sumber |
|---|---|
| environment | [cite_start]Dev / Prod [cite: 98] |
| criticality | [cite_start]High / Medium [cite: 98] |
| SLA | [cite_start]SLA DB [cite: 98] |
| compliance | [cite_start]Policy engine [cite: 98] |

[cite_start]Rule-based mapping [cite: 99][cite_start], Lookup ke CMDB atau policy service [cite: 100]
[cite_start]Tools: NiFi Rules [cite: 101, 102][cite_start], Python decision logic [cite: 103][cite_start], Config YAML [cite: 104]
[cite_start]Time-Based Enrichment, menambah konteks waktu [cite: 105] [cite_start](Shift Kerja [cite: 107], Jam Operasional [cite: 108], Maintenance Window [cite: 109])
[cite_start]Geo & Location Enrichment [cite: 115] [cite_start]Mendukung: Heat map [cite: 116, 117][cite_start], Capacity planning [cite: 118][cite_start], Disaster Impact [cite: 119]

| Field | Nilai |
|---|---|
| latitude | [cite_start]-6.2 [cite: 120] |
| longitude | [cite_start]106.8 [cite: 120] |
| region | [cite_start]APAC [cite: 120] |

[cite_start]Error Handling [cite: 121][cite_start]: Enrichment gagal data tidak di drop [cite: 122][cite_start], Field diberi status enrichment_status [cite: 123]
[cite_start]Strategi: [cite: 130]
| Kasus | Tindakan |
|---|---|
| Lookup gagal | [cite_start]Cache retry [cite: 131] |
| API down | [cite_start]Skip + flag [cite: 131] |
| Data tidak ada | [cite_start]Default / UNKNOWN [cite: 131] |

[cite_start]Caching Strategy [cite: 132][cite_start]: Lookup bisa ribuan per detik [cite: 133][cite_start], Jangan Query DB terus [cite: 134]
[cite_start]Tools: Redis - Lookup cepat [cite: 135, 136][cite_start], In-memory - Local microservice [cite: 137][cite_start], TTL - Auto refresh [cite: 138]

### 2.3. [cite_start]Data Flow Management [cite: 139]
[cite_start]**Requirement 2.3.1 (Batch and Streaming):** [cite: 140]
[cite_start]Streaming → Kafka topic [cite: 141][cite_start], Batch → Scheduler + Kafka [cite: 142]
[cite_start]Tools: Streaming -> Kafka + Flink [cite: 143, 144][cite_start], Batch -> NiFi Scheduler / Airflow [cite: 145]

[cite_start]Batch Processing - Sumber Data Batch [cite: 146, 147]
| Source | Metode |
|---|---|
| Asset DB | [cite_start]JDBC polling [cite: 148] |
| VMware | [cite_start]Scheduled REST [cite: 148] |
| File inventory | [cite_start]SFTP [cite: 148] |
| Discovery script | [cite_start]SSH [cite: 148] |

[cite_start]Scheduling [cite: 149]
| Tool | Fungsi |
|---|---|
| Apache NiFi | [cite_start]Native scheduler [cite: 150] |
| Apache Airflow | [cite_start]Complex dependency [cite: 150] |
| Cron + Script | [cite_start]Simple batch [cite: 150] |

[cite_start]Batch Optimization [cite: 151]
| Teknik | Manfaat |
|---|---|
| Incremental load | [cite_start]Kurangi beban [cite: 152] |
| Checkpoint | [cite_start]Resume aman [cite: 152] |
| Parallel batch | [cite_start]Throughput [cite: 152] |

[cite_start]Streaming Processing - Sumber Data Streaming [cite: 153, 154]
| Source | Metode |
|---|---|
| Syslog | [cite_start]Filebeat [cite: 155] |
| SNMP Trap | [cite_start]Telegraf [cite: 155] |
| Event API | [cite_start]Webhook [cite: 155] |
| Sensor | [cite_start]MQTT [cite: 155] |

[cite_start]Failure & Retry Strategy [cite: 156]
| Mode | Penanganan |
|---|---|
| Batch gagal | [cite_start]Retry + checkpoint [cite: 157] |
| Streaming gagal | [cite_start]Replay Kafka [cite: 157] |
| Partial batch | [cite_start]Resume [cite: 157] |

[cite_start]Performance Target [cite: 158]
| Mode | Target |
|---|---|
| Batch | [cite_start]5k+ records/sec [cite: 159] |
| Streaming | [cite_start]<500 ms latency [cite: 159] |
| Kafka | [cite_start]100k msg/sec [cite: 159] |

[cite_start]Monitoring Batch & Streaming [cite: 160]
| Metric | Mode |
|---|---|
| Throughput | [cite_start]Batch & Streaming [cite: 161] |
| Latency | [cite_start]Streaming [cite: 161] |
| Lag | [cite_start]Streaming [cite: 161] |
| Job duration | [cite_start]Batch [cite: 161] |

[cite_start]Tools: Prometheus [cite: 162, 163][cite_start], Grafana [cite: 164][cite_start], Kafka Exporter [cite: 165]

[cite_start]**Requirement 2.3.2 (Error Handling):** [cite: 166]
[cite_start]Cara menangani: Record gagal → kirim ke Dead Letter Queue (DLQ) [cite: 167, 168][cite_start], Jangan drop data [cite: 169][cite_start], DLQ berbasis Kafka topic / DB table [cite: 170][cite_start], Metadata lengkap [cite: 171]
[cite_start]Tools: Kafka DLQ topic [cite: 172, 173][cite_start], PostgreSQL (error table) [cite: 174][cite_start], Alert via Alertmanager (Prometheus) [cite: 175]

[cite_start]**Requirement 2.3.3 (Data Lineage):** Must track and log the source, timestamp, and transformation steps for every ingested record for auditing and troubleshooting purposes. [cite: 176]
[cite_start]Simpan metadata: Source [cite: 177, 178][cite_start], Timestamp [cite: 179][cite_start], Pipeline ID [cite: 180][cite_start], Transformation version [cite: 181]
[cite_start]Tools: NiFi Provenance [cite: 182, 183][cite_start], OpenLineage [cite: 184][cite_start], Custom Metadata DB [cite: 185]

## [cite_start]3. Kebutuhan Non-Fungsional [cite: 186]
### 3.1. [cite_start]Performance & Scalability [cite: 187]
[cite_start]**Requirement 3.1.1 (Throughput):** Must be capable of processing and transforming a sustained load of 5,000 data records per second during peak hours. [cite: 188]
[cite_start]Sistem mampu memproses ≥ 5k msg/s end-to-end [cite: 189]
[cite_start]Sudah termasuk: Ingest [cite: 190, 191][cite_start], Transform [cite: 192][cite_start], Enrich [cite: 193][cite_start], Deliver [cite: 194]
[cite_start]Decoupling dengan Message Broker [cite: 195][cite_start]: Gunakan Kafka sebagai buffer [cite: 196][cite_start], Producer ≠ Consumer [cite: 197][cite_start], Producer → Kafka → Consumer [cite: 198]
[cite_start]Parallel Processing [cite: 199][cite_start]: Partition Kafka [cite: 200][cite_start], Consumer group [cite: 201]

| Komponen | Konfigurasi |
|---|---|
| Kafka | [cite_start]≥ 6 partition [cite: 202] |
| Consumer | [cite_start]≥ 3 instance [cite: 202] |
| NiFi | [cite_start]Concurrent tasks [cite: 202] |

[cite_start]Stateless Processing [cite: 203][cite_start]: Jangan simpan state di memory lokal [cite: 204][cite_start], State → external store [cite: 205]
[cite_start]Tools: Apache Kafka [cite: 206, 207][cite_start], Apache NiFi / Flink [cite: 208][cite_start], Kubernetes HPA [cite: 209]

[cite_start]**Kebutuhan 3.1.2 (Latency):** Latency for critical streaming data pipelines (e.g., alerts) must be consistently under 500 milliseconds from source detection to target delivery. [cite: 210]
[cite_start]Streaming-first Design [cite: 211][cite_start]: Hindari batch untuk data kritikal [cite: 212][cite_start], Event-driven ingestion [cite: 213]
[cite_start]Lightweight Processing [cite: 214][cite_start]: Rule sederhana [cite: 215][cite_start], Hindari lookup berlebihan [cite: 216][cite_start], Gunakan cache [cite: 217]
[cite_start]Async & Non-blocking I/O [cite: 218][cite_start]: REST async [cite: 219][cite_start], Kafka async producer [cite: 220]
[cite_start]Tools: Kafka (low-latency config) [cite: 221, 222][cite_start], Apache Flink [cite: 223][cite_start], Redis cache [cite: 224]

[cite_start]**Kebutuhan 3.1.3 (Scaling):** The layer must be designed as a distributed system that can scale horizontally to handle increased data volume and velocity by adding resources. [cite: 231]
[cite_start]Microservices Architeture [cite: 232][cite_start]: Ingestor [cite: 233][cite_start], Processor [cite: 234][cite_start], Enricher [cite: 235][cite_start], Sink [cite: 236]
[cite_start]Containerization & Orchestration [cite: 237][cite_start]: Docker [cite: 238][cite_start], Kubernetes [cite: 239]
[cite_start]Auto Scaling [cite: 240] [cite_start](Scale Berdasarkan: CPU [cite: 241, 242], Kafka lag [cite: 243], Throughput [cite: 244])
[cite_start]Tools: Kubernetes HPA [cite: 245, 246][cite_start], Kafka Exporter [cite: 247][cite_start], Prometheus [cite: 248]

### 3.2. [cite_start]Reliability & Availability [cite: 249]
[cite_start]**Requirement 3.2.1 (HA):** The ingestion pipeline must be highly available with no single point of failure (SPOF) and provide automatic failover capabilities. [cite: 250]

| Komponen | Solusi |
|---|---|
| Kafka | [cite_start]3+ broker [cite: 251] |
| NiFi | [cite_start]Cluster mode [cite: 251] |
| DB | [cite_start]PostgreSQL HA [cite: 251] |

[cite_start]**Requirement 3.2.2 (Idempotency):** The ingestion process must be idempotent to prevent duplicate data insertion or processing when re-running a job or recovering from a failure. [cite: 252]
[cite_start]Cara menangani: Gunakan unique key (CI_ID) [cite: 253, 254][cite_start], Upsert, bukan insert [cite: 255]
[cite_start]Tools: CMDB API idempotent endpoint [cite: 256, 257][cite_start], Kafka message key [cite: 258]

### 3.3. [cite_start]Security [cite: 259]
[cite_start]**Requirement 3.3.1 (Credential Management):** Must securely store and manage credentials (e.g., API keys, SSH keys, passwords) required for connecting to source systems, preferably via integration with an enterprise vault/key management system. [cite: 260]
[cite_start]Jangan simpan password di config file [cite: 261]
[cite_start]Tools: Hashicorp Vault [cite: 262, 263][cite_start], Kubernetes Secrets [cite: 264][cite_start], Ansible Vault [cite: 265]

[cite_start]**Requirement 3.3.2 (Data in Transit):** All data transfer between the ingestion layer and external sources/targets must utilize encrypted channels (e.g., TLS 1.2+). [cite: 266]
[cite_start]TLS di semua channel [cite: 267]
[cite_start]Tools: HTTPS [cite: 268, 269][cite_start], Kafka SSL [cite: 270][cite_start], mTLS (internal service) [cite: 271]

## [cite_start]4. Spesifikasi Teknis [cite: 272]
### 4.1. [cite_start]Architecture [cite: 273]
[cite_start]Data Ingestion & Integration Layer harus dibangun menggunakan arsitektur modular berbasis microservices, dengan tujuan: [cite: 274]
* [cite_start]Memisahkan tanggung jawab tiap komponen (decoupled) [cite: 275]
* [cite_start]Mudah diskalakan secara horizontal [cite: 276]
* [cite_start]Fault-tolerant dan mudah diobservasi [cite: 277]
* [cite_start]Mendukung batch dan streaming secara bersamaan [cite: 278]

### 4.2. [cite_start]Technology Stack [cite: 279]
| Category | Requirement | Preferred Technology/Platform | Notes |
|---|---|---|---|
| Ingestion Framework | Mendukung pemrosesan batch dan streaming | [cite_start]Apache Kafka, Kafka Connect, Filebeat [cite: 280] | Kafka digunakan sebagai backbone event-driven untuk throughput tinggi dan buffering lonjakan data. [cite_start]Filebeat digunakan untuk ingestion log dan syslog secara real-time. [cite: 280] |
| Processing Engine | Transformasi, normalisasi, dan pemetaan data ke Common Data Model (CDM) | [cite_start]Apache NiFi, Apache Flink (opsional), microservice Python [cite: 280] | NiFi digunakan untuk visual flow, data provenance, dan audit. [cite_start]Flink digunakan untuk kebutuhan streaming dengan latency sangat rendah [cite: 280] |
| Message Broker | Penyangga data dan decoupling antar komponen | [cite_start]Apache Kafka [cite: 280] | [cite_start]Menyediakan mekanisme replay, partitioning, dan fault tolerance untuk ingestion DCIM. [cite: 280] |
| Database/Storage | Penyimpanan metadata pipeline, error queue, dan audit data | [cite_start]PostgreSQL, MongoDB [cite: 280] | PostgreSQL untuk data terstruktur (DLQ, metadata). [cite_start]MongoDB opsional untuk data semi-terstruktur. [cite: 280] |
| Cache Enrichment | Lookup data referensi berfrekuensi tinggi | [cite_start]Redis [cite: 280] | [cite_start]Digunakan untuk mengurangi latency enrichment dan beban ke database utama. [cite: 280] |
| Containerization | For deployment and scaling | [cite_start]Docker/Kubernetes [cite: 280] | [cite_start]Mendukung skalabilitas horizontal, high availability, dan rolling update tanpa downtime. [cite: 280] |
| Monitoring & Metrics | Monitoring performa ingestion dan pipeline | [cite_start]Prometheus, Grafana [cite: 280] | [cite_start]Digunakan untuk memonitor throughput, latency, error rate, dan Kafka lag. [cite: 280] |
| Logging Terpusat | Logging terpusat dan audit trail | [cite_start]ELK Stack (Filebeat, Logstash, Elasticsearch, Kibana) [cite: 280] | [cite_start]Digunakan untuk troubleshooting, audit, dan integrasi dengan sistem logging DCIM. [cite: 280] |
| Security & Credential Management | Manajemen kredensial dan secret | [cite_start]Kubernetes Secrets, HashiCorp Vault (opsional) [cite: 280] | [cite_start]Kredensial tidak disimpan di konfigurasi statis atau source code. [cite: 280] |
| CI/CD (Opsional) | Otomatisasi deployment dan konfigurasi | [cite_start]GitLab CI / GitHub Actions [cite: 280] | [cite_start]Mendukung versioning pipeline dan deployment yang konsisten. [cite: 280] |

### 4.3. [cite_start]Monitoring and Logging [cite: 281]
[cite_start]**Requirement 4.3.1:** Must expose ingestion metrics (e.g., throughput, success/fail rate, latency per pipeline) via standard protocols (e.g., Prometheus/JMX). [cite: 282]
[cite_start]Metric yang wajib disediakan [cite: 283]
| Metric | Deskripsi |
|---|---|
| Throughput | [cite_start]Jumlah record / detik [cite: 284] |
| Success rate | [cite_start]Data berhasil diproses [cite: 284] |
| Failure rate | [cite_start]Data gagal [cite: 284] |
| Latency per pipeline | [cite_start]End-to-end latency [cite: 284] |
| Kafka lag | [cite_start]Backlog processing [cite: 284] |

[cite_start]Tools Monitoring: Prometheus [cite: 285, 286][cite_start], Grafana [cite: 287][cite_start], JMX exporter [cite: 288][cite_start], Kafka exporter [cite: 289]

[cite_start]**Requirement 4.3.2:** Must log all processing steps, errors, and data flow events centrally and be integrated with the DCIM logging system. [cite: 290]
[cite_start]Jenis Log [cite: 291]
| Log Type | Isi |
|---|---|
| Ingestion log | [cite_start]Data masuk [cite: 292] |
| Processing log | [cite_start]Transform & enrichment [cite: 292] |
| Error log | [cite_start]Validation & DLQ [cite: 292] |
| Audit log | [cite_start]Lineage & trace [cite: 292] |

[cite_start]Tools Logging: Filebeat [cite: 293, 294][cite_start], Logstash [cite: 295][cite_start], Elasticsearch [cite: 296][cite_start], Kibana [cite: 297]

## [cite_start]5. Integration Targets [cite: 298]
[cite_start]Fungsi utama lapisan ini adalah untuk memasok data ke komponen inti DCIM berikutnya: [cite: 299]

| Target Component | Data Type | Communication Protocol | Target CMDB Section |
|---|---|---|---|
| Configuration Management Database (CMDB) | [cite_start]CI data, relationships, attributes [cite: 300] | [cite_start]REST API CMDB, Database Write (Upsert) [cite: 300] | [cite_start]Repository CI dan Relationship CMDB [cite: 300] |
| Monitoring System | [cite_start]Data sensor real-time, event operasional, alert [cite: 300] | [cite_start]Apache Kafka (Message Queue), REST API [cite: 300] | [cite_start]Dashboard Operasional / NOC View [cite: 300] |
| Analytics & AI Engine | [cite_start]Historical data for trend analysis [cite: 300] | [cite_start]Apache Kafka, Database Write [cite: 300] | [cite_start]Data Lake/Warehouse [cite: 300] |
| Centralized Logging | [cite_start]Log ingestion, error, audit, dan data lineage [cite: 300] | [cite_start]ELK Stack (Filebeat, Logstash, Elasticsearch) [cite: 300] | [cite_start]Centralized Logging DCIM [cite: 300] |
| Reporting System & Dashboard | [cite_start]Data ringkasan operasional dan performa [cite: 300] | [cite_start]REST API / Query Database [cite: 300] | [cite_start]Dashboard Manajemen & Operasional [cite: 300] |

## [cite_start]Appendix: Change Log [cite: 301]
| Version | Date | Author | Description of Change |
|---|---|---|---|
| 1.0 | [cite_start]20 Jan 2026 | shuffahaqgzz@gmail.com [cite: 302] | [cite_start]Initial draft of Data Ingestion & Integration Layer Technical Requirements. [cite: 302] |
| 2.0 | 21 Jan 2026 | [cite_start]Imam Syauqi Achmad [cite: 302] |  |