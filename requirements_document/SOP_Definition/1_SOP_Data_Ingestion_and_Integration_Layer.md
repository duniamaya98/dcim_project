# Prosedur Operasi Standar (SOP) - Data Ingestion & Integration Layer[cite: 3]

## 1. Tujuan, Latar Belakang, dan Ruang Lingkup

### 1.1 Tujuan
SOP ini bertujuan mendefinisikan komponen Data Ingestion & Integration Layer secara formal dan teknis dalam arsitektur DCIM, dengan tujuan spesifik:
* Menetapkan definisi dan fungsionalitas layer sebagai gerbang tunggal data operasional DCIM.
* Menguraikan arsitektur teknis penanganan berbagai sumber, format, dan protokol data (Real-Time, Near Real-Time, Batch).
* Menetapkan standar validasi, normalisasi, dan enrichment data.
* Menjadi referensi tunggal perancangan, implementasi pipeline data, dan operasionalisasi.

### 1.2 Latar Belakang
Kualitas dan ketersediaan data adalah fondasi platform DCIM, CMDB, dan Analytics & AI Engine. SOP ini memastikan proses ingest dan integrasi data dibangun dengan ketahanan, skalabilitas, dan kepatuhan keamanan.

### 1.3 Ruang Lingkup
SOP berlaku untuk semua aktivitas perancangan, pengembangan, implementasi, pemeliharaan, dan operasionalisasi pipeline data yang meliputi:
* Identifikasi dan klasifikasi sistem sumber data DCIM.
* Spesifikasi standar protokol, format, dan mekanisme integrasi (API, Message Broker, Streaming Engine).
* Manajemen kualitas data (validasi, normalisasi, transformasi, enrichment).
* Implementasi mekanisme ketahanan (Error Handling, Logging, Retry Mechanism).

## 2. Definisi dan Peran Inti Data Ingestion & Integration Layer

### 2.1 Definisi
Lapisan perantara untuk mengumpulkan, memproses, dan memuat data operasional dari source systems ke repositori inti DCIM (misal CMDB dan Data Lake), mengubah raw data menjadi clean data.

### 2.2 Peran Kunci
| Peran Kunci | Deskripsi Fungsional |
| :--- | :--- |
| Single Gateway | Titik masuk data resmi ke platform DCIM. |
| Data Cleansing | Validasi, pembersihan, dan normalisasi data. |
| Data Enrichment | Memperkaya data metrik dengan konteks CMDB (koordinat, Asset ID). |
| Protocol Translation| Mengubah format/protokol ke standar DCIM. |
| Buffer & Decoupling | Mekanisme buffering untuk ketahanan. |

## 3. Sumber Data dan Klasifikasi
| Kategori Sumber | Contoh Sistem Sumber | Jenis Data | Mekanisme Ingesti |
| :--- | :--- | :--- | :--- |
| Fasilitas | BMS, EPMS, EMS | Daya, Suhu, Status Peralatan | Near Real-Time, Streaming |
| IT Infrastructure| NMS, vCenter, Server OS | Utilisasi Port, Spesifikasi VM | Near Real-Time, Batch |
| IoT & Sensor | Sensor nirkabel, PDU Cerdas | Data Time-Series, Lokasi | Real-Time, Streaming |
| Sistem Eksternal | ITSM, ERP, Asset Repository | Data Finansial, Tiket Insiden | Batch, API Sync |

## 4. Mekanisme Ingesti dan Arsitektur Data Pipeline

### 4.1 Mode Ingesti Data
* **Real-Time Streaming:** Data berkelanjutan, diproses segera (< 5 Detik).
* **Near Real-Time:** Interval pendek (30 Detik – 5 Menit).
* **Batch Processing:** Berkala (Jam – Harian).

### 4.2 Arsitektur dan Komponen Kunci
* **Data Collector Agents:** Logstash, Telegraf, Klien API Kustom.
* **Message Broker:** Kafka, RabbitMQ.
* **Streaming Processor:** Kafka Streams, Spark Streaming.
* **Data Loader / Sink:** Konektor Database, API Loader.

## 5. Standar Protokol dan Mekanisme Integrasi
* **API Integration:** RESTful API (JSON/XML) dengan OAuth2/API Key dan HTTPS/TLS.
* **Message Queue / Broker:** MQTT, AMQP.
* **Database Connectors:** JDBC/ODBC, Change Data Capture (CDC).
* **Industrial Protocols:** SNMP (v3 wajib), Modbus TCP, BACnet/IP.
* **File Transfer:** SFTP/FTPS terstruktur dan divalidasi.

## 6. Manajemen Kualitas Data

### 6.1 Validasi dan Sanitasi
Schema Validation, Range Check, Format Consistency.

### 6.2 Normalisasi dan Transformasi
Normalization, Transformation (Filtering), Aggregation.

### 6.3 Data Enrichment
CI Context (CI_ID, Asset_ID), Location Context, Time/Weather Context.

## 7. Keamanan Data di Data Pipeline
* **Authentication & Authorization:** Service Account / API Key dengan Vault dan Least Privilege.
* **Data Encryption In Transit:** TLS/SSL (HTTPS) dan SNMPv3 wajib.
* **Data Masking:** Masking atau enkripsi informasi sensitif.
* **Audit Trail:** Pencatatan log transaksi untuk audit.

## 8. Monitoring, Logging, dan Mekanisme Ketahanan

### 8.1 Monitoring dan Alerting
Memantau Pipeline Health, Error Rate (< 0.01%), dan Data Freshness.

### 8.2 Error Handling dan Retry Mechanism
Menggunakan Dead Letter Queue (DLQ) dan kebijakan Exponential Backoff.

## 9. Tata Kelola dan Kepatuhan
* **Version Control:** Dikelola menggunakan Version Control System (File) melalui CI/CD.
* **Kepatuhan Standar DCIM:** Sesuai skema CMDB dan kebijakan retensi data.

## 10. Peran, Tanggung Jawab, dan RACI
(Rincian matriks RACI tersedia pada dokumen asli untuk DCIM Solution Architect, Integration Engineer, Data Owner, CMDB Administrator, MLOps Engineer).