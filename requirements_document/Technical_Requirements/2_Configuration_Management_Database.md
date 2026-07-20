# [cite_start]Technical Requirements - Configuration Management Database (CMDB) [cite: 304]

## [cite_start]1. Pendahuluan [cite: 305]
[cite_start]Dokumen ini menetapkan persyaratan teknis untuk komponen Configuration Management Database (CMDB) dalam Proyek Manajemen Infrastruktur Pusat Data (DCIM). [cite: 306] [cite_start]CMDB akan berfungsi sebagai sumber kebenaran tunggal (Single Source of Truth) untuk semua Configuration Item (CI) dan relasinya, yang mendukung fungsi utama DCIM, termasuk monitoring, otomatisasi, dan analitik. [cite: 307]

### 1.1. [cite_start]Konteks Proyek [cite: 308]
| Field | Description |
|---|---|
| Nama Proyek | [cite_start]Data Center Infrastructure Management (DCIM) Core Platform [cite: 309] |
| Komponen | [cite_start]Configuration Management Database (CMDB) [cite: 309] |
| Versi Dokumen | [cite_start]1.0 [cite: 309] |
| Tanggal Pembuatan | [cite_start]Jan 19, 2026 12:15 AM GMT+7 [cite: 309] |
| Disiapkan Oleh | [cite_start]Shuffahaq Gilang Zhesa [cite: 309] |

## [cite_start]2. Kebutuhan Fungsional [cite: 310]
[cite_start]CMDB harus memenuhi fungsi inti berikut: [cite: 311]

### 2.1. [cite_start]Configuration Item (CI) Management [cite: 312]
**2.1.1. [cite_start]CI Data Model** [cite: 313]
* **Requirement 2.1.1.1 (Fleksibilitas Skema):** Harus mendukung model data yang fleksibel dan terstruktur untuk mendefinisikan berbagai tipe CI (e.g., Server, Network Device, Rack, PDU, Aplikasi, Layanan). [cite: 314]
* [cite_start]**Requirement 2.1.1.2 (CI Hierarki):** Harus mendukung struktur hierarki dan pewarisan (inheritance) antar CI (e.g., Server mewarisi dari Hardware, VM mewarisi dari Host). [cite: 315]
* [cite_start]**Requirement 2.1.1.3 (Mandatory Attributes):** Harus memungkinkan penetapan atribut wajib (mandatory fields) untuk setiap tipe CI (e.g., serial number, location, owner). [cite: 316]

[cite_start]Contoh Tipe CI Utama: [cite: 317]
| CI Type | Mandatory Attributes |
|---|---|
| Hardware | [cite_start]Serial Number, Model, Manufacturer, Status [cite: 318] |
| Physical Location | [cite_start]Site, Building, Room, Rack (Nama/ID) [cite: 318] |
| Virtual | [cite_start]Host Reference, Guest OS, vCPU/vRAM [cite: 318] |
| Logic/Services | [cite_start]Service Owner, Business Criticality, SLA [cite: 318] |

**2.1.2. [cite_start]CI Lifecycle Management** [cite: 319]
* **Requirement 2.1.2.1 (Status Tracking):** Harus melacak siklus hidup CI, mencakup status seperti: Planned, Operational, Maintenance, Retired, Decommissioned. [cite: 320]
* [cite_start]**Requirement 2.1.2.2 (Audit Trail):** Harus menyimpan audit log lengkap dari semua perubahan pada atribut CI (Siapa, Kapan, Perubahan Lama, Perubahan Baru). [cite: 321]

### 2.2. [cite_start]Relationship Management [cite: 322]
**2.2.1. [cite_start]Relationship Model** [cite: 323]
* [cite_start]**Requirement 2.2.1.1 (Relationship Types):** Harus mendukung hubungan biner (two-way) dan terdefinisi dengan jelas (e.g., Connects to, Runs on, Contained in, Powers). [cite: 324]
* **Requirement 2.2.1.2 (Relationship Visualization):** Harus menyediakan antarmuka untuk memvisualisasikan peta topologi (topology map) yang menunjukkan semua relasi CI yang dipilih. [cite: 325]

Contoh Relationship Model: [cite: 326]
| CI A | Relationship Type | CI B |
|---|---|---|
| Server | Is Connected to | Switch Port [cite: 327] |
| VM | Runs on | Hypervisor Host [cite: 327] |
| Rack | Contains | PDU [cite: 327] |
| Service | Depends on | Database Server [cite: 327] |

**2.2.2. [cite_start]Impact Analysis** [cite: 328]
* **Requirement 2.2.2.1 (Impact Calculation):** Harus mampu melakukan analisis dampak (impact analysis) secara real-time, yaitu mengidentifikasi layanan dan CI yang terpengaruh jika suatu CI gagal (misalnya, Jika Rack R-10 down, layanan apa saja yang terpengaruh?). [cite: 329]
* [cite_start]**Requirement 2.2.2.2 (Path Tracing):** Harus dapat melacak semua jalur koneksi (path) dari layanan ke infrastruktur fisik pendukungnya. [cite: 330]

### 2.3. [cite_start]Data Ingestion & Update [cite: 331]
**2.3.1. [cite_start]Data Integration (Ingestion)** [cite: 332]
* [cite_start]**Requirement 2.3.1.1 (API Ingestion):** Harus menyediakan REST API yang aman dan terdokumentasi untuk menerima data CI dan relasi dari Data Ingestion & Integration Layer. [cite: 333]
* [cite_start]**Requirement 2.3.1.2 (Idempotency):** Operasi write/update (upsert) harus bersifat idempotent untuk mencegah duplikasi data saat terjadi retry atau re-run data ingestion. [cite: 334]
* **Requirement 2.3.1.3 (Data Validation):** Harus menerapkan validasi skema saat ingestion untuk memastikan integritas data (e.g., tipe data, mandatory fields). [cite: 335]

**2.3.2. [cite_start]Data Maintenance** [cite: 336]
* **Requirement 2.3.2.1 (Reconciliation):** Harus memiliki mesin rekonsiliasi untuk menggabungkan (merge) data dari berbagai sumber (e.g., Discovery Tool, Asset Repository) berdasarkan aturan yang dikonfigurasi (e.g., Serial Number sebagai Unique Key). [cite: 337]
* [cite_start]**Requirement 2.3.2.2 (Discrepancy Reporting):** Harus melaporkan anomali atau ketidaksesuaian data (data discrepancy) antara data yang ada di CMDB dan data yang masuk dari sumber eksternal. [cite: 338]

## [cite_start]3. Kebutuhan Non-Fungsional [cite: 339]
### 3.1. [cite_start]Performance and Scalability [cite: 340]
* [cite_start]**Requirement 3.1.1 (Kapasitas CI):** Harus mampu menyimpan dan mengelola minimal 150.000 Configuration Item (CI) dan 500.000 Relationship. [cite: 341]
* **Requirement 3.1.2 (API Latency):** Latency untuk operasi Read (Query) CI dan Relationship API harus konsisten di bawah 500 ms untuk query dengan 5+ filter/join. [cite: 342]
* [cite_start]**Requirement 3.1.3 (Scalability):** Arsitektur harus mendukung skalabilitas horizontal (penambahan node aplikasi dan database) untuk menangani lonjakan data ingestion. [cite: 343]

### 3.2. [cite_start]Reliability and Availability [cite: 344]
* **Requirement 3.2.1 (Uptime):** Target ketersediaan (Uptime) sistem minimal 99.9% (Tier 3-4 data center). [cite: 345]
* [cite_start]**Requirement 3.2.2 (High Availability - HA):** Harus diimplementasikan dalam mode cluster HA dengan failover otomatis untuk mencegah Single Point of Failure (SPOF) pada database dan server aplikasi. [cite: 346]
* [cite_start]**Requirement 3.2.3 (Backup and Recovery):** Harus mendukung daily full backup dan point-in-time recovery dengan Recovery Time Objective (RTO) kurang dari 4 jam. [cite: 347]

### 3.3. [cite_start]Security [cite: 348]
* [cite_start]**Requirement 3.3.1 (Akses Kontrol):** Harus menerapkan Role-Based Access Control (RBAC) yang granular, memisahkan akses Read/Write berdasarkan Tipe CI, Lokasi, dan Role pengguna (e.g., Network Team hanya boleh mengedit CI Network Device). [cite: 349]
* **Requirement 3.3.2 (API Security):** Semua akses API harus diamankan menggunakan TLS 1.2+ dan skema otentikasi berbasis token (e.g., OAuth 2.0 atau API Key). [cite: 350]
* [cite_start]**Requirement 3.3.3 (Data Classification):** Harus mendukung klasifikasi data (e.g., Public, Internal, Confidential) dan membatasi akses ke atribut sensitif. [cite: 351]

## [cite_start]4. Integration & Interface [cite: 352]
[cite_start]CMDB berfungsi sebagai hub sentral dan harus berintegrasi dengan komponen DCIM lainnya. [cite: 353]

### 4.1. [cite_start]Integration Matrix [cite: 354]
| Sistem/Layanan | Interface Type | Data Flow Direction | Tujuan Integrasi |
|---|---|---|---|
| Data Ingestion & Integration Layer | API (REST) | Bi-directional (Read/Write) | [cite_start]Ingest data CI, relasi, dan update status. [cite: 355] |
| Asset Repository (AR) | API (REST) | Uni-directional (Read) | [cite_start]Menambah data non-CI (Finansial, Kontrak, Garansi) sebagai Enrichment. [cite: 355] |
| Monitoring System | API (REST) | Uni-directional (Read) | [cite_start]Mengambil konteks CI dan relasi untuk Event Correlation dan Alert Enrichment. [cite: 355] |
| Analytics & AI Engine | API (REST) / DB | Uni-directional (Read) | [cite_start]Menyediakan data topologi dan relasi untuk Impact Analysis dan Failure Prediction. [cite: 355] |
| Workflow Automation | API (REST) | Bi-directional (Read/Write) | [cite_start]Mengambil CI data untuk otomatisasi dan mengupdate CI status (e.g., Maintenance). [cite: 355] |
| IT Service Management (ITSM) | API (REST) | Bi-directional (Read/Write) | [cite_start]Sinkronisasi CI dan relasi dengan tiket (Incident, Change, Problem). [cite: 355] |

### 4.2. [cite_start]API Requirements [cite: 356]
[cite_start]**Requirement 4.2.1 (REST API):** Harus menyediakan REST API yang memadai untuk: [cite: 357]
* CRUD (Create, Read, Update, Delete) CI dan Relationship. [cite: 358]
* [cite_start]Query data dengan filter kompleks. [cite: 359]
* [cite_start]Melakukan Impact Analysis via API. [cite: 360]

[cite_start]**Requirement 4.2.2 (Query Language):** Harus mendukung bahasa kueri yang fleksibel dan efisien (misalnya, GraphQL, SQL-like, atau kueri khusus graph database). [cite: 361]

## [cite_start]5. Spesifikasi Teknis [cite: 362]
### 5.1. [cite_start]Technology Stack [cite: 363]
| Category | Requirement | Preferred Technology/Platform | Notes |
|---|---|---|---|
| Database Core | High-performance for relationships and topology | Neo4j (Graph DB) / PostgreSQL (Relational) | Preferensi kuat untuk Graph Database seperti Neo4j untuk model relasi yang kompleks dan performa Impact Analysis. [cite_start]PostgreSQL sebagai alternatif atau untuk penyimpanan atribut non-relasi. [cite: 364] |
| Application Framework | Robust dan scalable | Python/Django atau Go/Fiber | [cite_start]Framework modern dengan dukungan REST API dan skalabilitas tinggi. [cite: 364] |
| Deployment | Containerization dan Orchestration | Docker/Kubernetes | [cite_start]Wajib untuk High Availability, Scalability, dan rolling update. [cite: 364] |
| Search Engine | Fast full-text search dan indexing | Elasticsearch / OpenSearch | [cite_start]Diperlukan untuk pencarian CI yang cepat dan kompleks (e.g., mencari berdasarkan deskripsi, tag, atau log). [cite: 364] |
| Cache | Low-latency lookup | Redis | [cite_start]Caching metadata dan hasil Impact Analysis yang sering diakses. [cite: 364] |

### 5.2. [cite_start]Platform Requirements [cite: 365]
| Component Type | Quantity (Rec) | CPU (Cores) | RAM (GB) | Storage (GB) | Network (Gbps) |
|---|---|---|---|---|---|
| CMDB Application Server (VM/Pod) | [cite_start]3+ (Active-Active) [cite: 366] | [cite_start]4 [cite: 366] | [cite_start]16 [cite: 366] | [cite_start]100 (OS + App) [cite: 366] | [cite_start]1 [cite: 366] |
| CMDB Database (Graph/Relational) | [cite_start]3 (Cluster) [cite: 366] | [cite_start]8 [cite: 366] | [cite_start]32 [cite: 366] | [cite_start]1000 (Data + Index) [cite: 366] | [cite_start]10 [cite: 366] |
| Search Engine (Cluster) | [cite_start]3 (Cluster) [cite: 366] | [cite_start]4 [cite: 366] | [cite_start]8 [cite: 366] | [cite_start]500 (Data + Index) [cite: 366] | [cite_start]1 [cite: 366] |

## [cite_start]Appendix: Change Log [cite: 367]
| Version | Date | Author | Description of Change |
|---|---|---|---|
| 1.0 | Jan 20, 2026 | Shuffahaq Gilang Zhesa | [cite_start]Initial draft of Configuration Management Database Technical Requirements. [cite: 368] |