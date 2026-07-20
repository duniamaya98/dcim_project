# [cite_start]Technical Requirements - Asset Repository (AR) [cite: 370]

## [cite_start]1. Pendahuluan [cite: 371]
[cite_start]Dokumen ini menetapkan persyaratan teknis untuk komponen Asset Repository (AR) dalam Proyek Manajemen Infrastruktur Pusat Data (DCIM) Core Platform. [cite: 372] [cite_start]Asset Repository berfungsi sebagai sistem pencatatan inventaris utama untuk aset fisik dan non-fisik, yang menyimpan informasi non-operasional (misalnya, finansial, kontrak, garansi, kepemilikan) yang akan digunakan untuk memperkaya (enrichment) data Configuration Item (CI) di Configuration Management Database (CMDB) dan mendukung fungsi DCIM lainnya. [cite: 373]

### 1.1. [cite_start]Konteks Proyek [cite: 374]
| Field | Description |
|---|---|
| Nama Proyek | [cite_start]Data Center Infrastructure Management (DCIM) Core Platform [cite: 375] |
| Komponen | [cite_start]Asset Repository (AR) [cite: 375] |
| Versi Dokumen | [cite_start]1.0 [cite: 375] |
| Tanggal Pembuatan | [cite_start]Jan 20, 2026 [cite: 375] |
| Disiapkan Oleh | [cite_start]Shuffahaq Gilang Zhesa [cite: 375] |

## [cite_start]2. Kebutuhan Fungsional [cite: 376]
[cite_start]Asset Repository harus memenuhi fungsi inti berikut: [cite: 377]

### 2.1. [cite_start]Asset Inventory Management [cite: 378]
**2.1.1. [cite_start]Asset Data Model** [cite: 379]
[cite_start]Asset Repository harus mendukung model data yang fleksibel untuk merekam berbagai atribut aset. [cite: 380]
* [cite_start]**Requirement 2.1.1.1 (Atribut Fisik):** Harus menyimpan data teknis dasar, termasuk Asset ID, Serial Number, Model, Manufacturer, Part Number, dan status fisik. [cite: 381]
* **Requirement 2.1.1.2 (Atribut Finansial):** Harus menyimpan informasi biaya aset, seperti Purchase Date, Acquisition Cost, Depreciation Status, dan Purchase Order (PO) Number. [cite: 382]
* [cite_start]**Requirement 2.1.1.3 (Atribut Non-Teknis):** Harus menyimpan informasi terkait kontrak, garansi, dan kepemilikan, seperti Warranty Expiration Date, Vendor/Supplier, Maintenance Contract ID, dan Business Owner. [cite: 383]

[cite_start]Contoh Atribut Aset: [cite: 384]
| Kategori | Atribut Wajib | Atribut Opsional |
|---|---|---|
| Identifikasi | [cite_start]Asset ID, Serial Number, Manufacturer, Model [cite: 385] | [cite_start]Part Number, Tag DCIM [cite: 385] |
| Finansial | [cite_start]Purchase Date, Acquisition Cost [cite: 385] | [cite_start]Depreciation Status, Lease/Owned [cite: 385] |
| Kontrak/Legal | [cite_start]Warranty Expiration Date, Vendor Contact [cite: 385] | [cite_start]Maintenance Contract ID, SLA Level [cite: 385] |
| Operasional | [cite_start]Current Status (Active/Retired), Location (Logical) [cite: 385] | [cite_start]Last Audit Date, User/Department [cite: 385] |

**2.1.2. [cite_start]Asset Status Tracking (Lifecycle Management)** [cite: 386]
[cite_start]Sistem harus mampu melacak status siklus hidup aset. [cite: 387]
* [cite_start]**Requirement 2.1.2.1 (Status Tracking):** Harus mendukung status aset yang membedakan tahap kehidupan aset (e.g., Procured, In Stock, Deployed, Under Repair, Retired, Disposed). [cite: 388]
* [cite_start]**Requirement 2.1.2.2 (Riwayat Status):** Harus menyimpan riwayat lengkap perubahan status aset, mencakup tanggal, pengguna yang mengubah, dan alasan perubahan. [cite: 389]

**2.1.3. [cite_start]Audit and Inventory** [cite: 390]
* **Requirement 2.1.3.1 (Audit Trail):** Harus menyediakan log audit yang lengkap dan tidak dapat diubah (immutable) untuk semua data yang dimasukkan, dimodifikasi, atau dihapus. [cite: 391]
* [cite_start]**Requirement 2.1.3.2 (Reporting Inventaris):** Harus mampu menghasilkan laporan inventarisasi aset berdasarkan filter kompleks (misalnya, aset yang akan berakhir garansi dalam 90 hari, aset yang terdepresiasi penuh). [cite: 392]

### 2.2. [cite_start]Data Integration and API [cite: 393]
**2.2.1. [cite_start]Data Ingestion** [cite: 394]
[cite_start]Asset Repository harus menyediakan mekanisme yang aman untuk menerima data dari sistem eksternal (misalnya, sistem Purchase Order/ERP). [cite: 395]
* [cite_start]**Requirement 2.2.1.1 (API Ingestion):** Harus menyediakan REST API yang aman dan terstruktur untuk operasi Read dan Write data aset. [cite: 396]
* [cite_start]**Requirement 2.2.1.2 (File Ingestion):** Harus mendukung upload data aset secara massal melalui format file standar (CSV, XLSX, JSON) dengan validasi skema yang ketat. [cite: 397]

**2.2.2. [cite_start]Data Export (Enrichment API)** [cite: 398]
[cite_start]Asset Repository bertindak sebagai sumber data enrichment untuk CMDB dan sistem lain. [cite: 399]
* [cite_start]**Requirement 2.2.2.1 (Enrichment API):** Harus menyediakan API yang dioptimalkan untuk read-only lookup data aset berdasarkan kunci unik (e.g., Serial Number, Asset ID). [cite: 400]
* **Requirement 2.2.2.2 (Filter dan Query):** API harus mendukung filter dan kueri yang efisien untuk mengambil subset data (e.g., hanya mengambil owner dan warranty date dari suatu aset). [cite: 401]

## 3. Kebutuhan Non-Fungsional [cite: 402]
### 3.1. Performance and Scalability [cite: 403]
* [cite_start]**Requirement 3.1.1 (Kapasitas Aset):** Harus mampu menyimpan dan mengelola minimal 100.000 record aset. [cite: 404]
* [cite_start]**Requirement 3.1.2 (API Latency):** Latency untuk operasi Lookup/Read API (digunakan untuk CMDB Enrichment) harus konsisten di bawah 200 ms. [cite: 405]
* **Requirement 3.1.3 (Skalabilitas Database):** Arsitektur database harus mendukung skalabilitas vertikal maupun horizontal untuk mengantisipasi pertumbuhan volume aset dan frekuensi kueri. [cite: 406]

### 3.2. Reliability and Availability [cite: 407]
* [cite_start]**Requirement 3.2.1 (Uptime):** Target ketersediaan (Uptime) sistem minimal 99.9%. [cite: 408]
* [cite_start]**Requirement 3.2.2 (High Availability - HA):** Harus diimplementasikan dalam konfigurasi HA dengan redundansi dan failover otomatis untuk server aplikasi dan database. [cite: 409]
* **Requirement 3.2.3 (Backup and Recovery):** Harus mendukung daily backup data dan point-in-time recovery dengan Recovery Time Objective (RTO) kurang dari 4 jam. [cite: 410]

### 3.3. Security [cite: 411]
* [cite_start]**Requirement 3.3.1 (Akses Kontrol):** Harus menerapkan Role-Based Access Control (RBAC) yang granular untuk memisahkan hak akses Inventory/Finance/Auditor. [cite: 412]
* [cite_start]**Requirement 3.3.2 (API Security):** Semua akses API harus diamankan menggunakan TLS 1.2+ dan skema otentikasi berbasis token (e.g., API Key atau OAuth 2.0). [cite: 413]
* **Requirement 3.3.3 (Data Encryption):** Data sensitif (misalnya, detail finansial atau kontrak) harus dienkripsi saat transit (TLS) dan saat disimpan (Encryption at Rest). [cite: 414]

## 4. Spesifikasi Teknis [cite: 415]
### 4.1. Architecture [cite: 416]
Asset Repository harus dirancang sebagai aplikasi web berbasis REST API, dengan pemisahan yang jelas antara lapisan aplikasi dan lapisan database/storage. [cite: 417]

| Layer | Komponen Utama | Tujuan |
|---|---|---|
| Application Layer | Web/API Server (Stateless) [cite: 418] | Menangani permintaan API, otentikasi, dan validasi data. [cite: 418] |
| Database Layer | Relational Database (HA Cluster) [cite: 418] | Penyimpanan data aset yang terstruktur, audit log, dan riwayat status. [cite: 418] |
| Cache Layer | In-Memory Cache [cite: 418] | Mengurangi latency untuk Enrichment Lookup yang berfrekuensi tinggi. [cite: 418] |
| Deployment | Containerization / Orchestration [cite: 418] | Menjamin skalabilitas horizontal dan HA. [cite: 418] |

### 4.2. Technology Stack [cite: 419]
Pemilihan teknologi harus mempertimbangkan kompatibilitas dengan ekosistem DCIM yang sudah ada. [cite: 420]

| Category | Requirement | Preferred Technology/Platform | Notes |
|---|---|---|---|
| Database Core | Penyimpanan data terstruktur dan integritas transaksi | PostgreSQL | Stabilitas, performa untuk data relasional, dan dukungan HA. [cite: 421] |
| Application Framework | Robust dan skalabel (API-first) | Python/Django atau Go/Fiber | Pilihan yang modern dan mendukung pengembangan REST API yang cepat. [cite: 421] |
| Cache Enrichment | Low-latency lookup untuk CMDB | Redis | Wajib untuk menjaga latency API di bawah 200ms. [cite: 421] |
| Deployment | Containerization dan Orchestration | Docker/Kubernetes | Untuk deployment yang fleksibel, skalabel, dan otomatis. [cite: 421] |
| Authentication/Security | Manajemen kredensial dan API Key | Kubernetes Secrets atau HashiCorp Vault | Kredensial tidak boleh disimpan dalam konfigurasi statis. [cite: 421] |

## 5. External Integration [cite: 422]
Asset Repository adalah sumber data utama (master data) yang akan dibaca oleh komponen DCIM lainnya. [cite: 423]

### 5.1. Integration Matrix [cite: 424]
| Sistem/Layanan | Interface Type | Data Flow Direction | Tujuan Integrasi |
|---|---|---|---|
| Configuration Management Database (CMDB) | API (REST) | Uni-directional (Read) | Enrichment data CI dengan informasi Finansial/Garansi. [cite: 425] |
| Data Ingestion & Integration Layer | API (REST) | Bi-directional (Read/Write) | Ingest data aset dari sumber eksternal (e.g., ERP/PO System). [cite: 425] |
| Workflow Automation | API (REST) | Uni-directional (Read) | Mengambil Warranty Date untuk memicu workflow End-of-Life Notification. [cite: 425] |
| Reporting System & Dashboard | API (REST) / DB Access | Uni-directional (Read) | Menghasilkan laporan total biaya kepemilikan (TCO) aset. [cite: 425] |

### 5.2. API Specifications [cite: 426]
* [cite_start]**Requirement 5.2.1 (Lookup API):** Harus memiliki endpoint API yang terdedikasi, dioptimalkan untuk kueri cepat berdasarkan Serial Number atau Asset ID. [cite: 427] [cite_start]Contoh Endpoint: `/api/v1/assets/lookup?serial_number={sn}` [cite: 428]
* [cite_start]**Requirement 5.2.2 (Write API):** Harus memiliki endpoint dengan validasi ketat untuk create dan update data aset. [cite: 429] [cite_start]Operasi Update harus mengimplementasikan partial update (PATCH) jika memungkinkan. [cite: 430]

## [cite_start]Appendix: Change Log [cite: 431]
| Version | Date | Author | Description of Change |
|---|---|---|---|
| 1.0 | Jan 20, 2026 | Shuffahaq Gilang Zhesa | [cite_start]Initial draft of Asset Repository Technical Requirements. [cite: 432] |