# Definisi Baseline (Fungsional dan Non-Fungsional) - Data Ingestion & Integration Layer  2]

Dokumen ini mendefinisikan baseline fungsional dan non-fungsional untuk komponen Data Ingestion & Integration Layer dalam proyek Data Center Infrastructure Management (DCIM)

## Persyaratan Proyek DCIM 
Proyek DCIM bertujuan untuk menyediakan visibilitas dan kontrol yang komprehensif atas infrastruktur pusat data 5]. Lapisan Data Ingestion & Integration (DI&I) sangat penting untuk mengumpulkan dan mengintegrasikan data dari berbagai sumber infrastruktur

## Komponen: Data Ingestion & Integration Layer 

| Aspek | Deskripsi |
| :--- | :--- |
| **Tujuan** | Mengumpulkan, memproses, dan mengintegrasikan data dari berbagai sumber (misalnya, Building Management System/BMS, peralatan IT, sensor) untuk analisis dan manajemen.  |
| **Sumber Data** | Sistem Pemantauan Infrastruktur, Jaringan, Server, Peralatan Daya dan Pendingin, Sensor Lingkungan.  |
| **Penerima Data** | CMDB, Asset Repository, Analytics & AI Engine, Workflow Automation, SIEM.  |

## Baseline Fungsional 
Baseline fungsional menjelaskan kemampuan yang harus dimiliki oleh Lapisan DI&I untuk memenuhi persyaratan proyek.

### 1. Pengumpulan Data (Data Ingestion) 

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Mendukung berbagai protokol konektivitas. | Mampu mengumpulkan data melalui protokol standar (misalnya, SNMP, Modbus, REST API, MQTT, Syslog) dari perangkat IT dan Operasional (OT) yang berbeda (misalnya, UPS, PDU, CRAC, Server, Switch).  |
| Mendukung berbagai format data. | Mampu memproses data terstruktur (misalnya, JSON, XML, CSV) dan semi-terstruktur, serta data time-series.  |
| Mekanisme polling dan berbasis peristiwa (event-driven). | Mampu melakukan polling berkala untuk data status dan kinerja, serta menerima notifikasi dan peristiwa secara real-time dari sumber data (misalnya, alarm).  |

### 2. Transformasi dan Pemrosesan Data 

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Data Normalization. | Menyatukan skema data dari berbagai sumber ke dalam format standar yang konsisten untuk digunakan oleh komponen hilir (CMDB, Analytics).  |
| Data Cleansing and Validating. | Mengidentifikasi dan menangani data yang hilang, outlier, atau tidak valid sebelum diintegrasikan (misalnya, memfilter pembacaan sensor yang tidak realistis).  |
| Agregasi dan Komputasi. | Mampu melakukan perhitungan dasar (misalnya, rata-rata, total daya) dan agregasi data historis untuk mengurangi beban penyimpanan dan analisis.  |

### 3. Integrasi Data 

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Integrasi Data Real-time. | Memastikan data kritis seperti peristiwa dan alarm disalurkan ke Security Information & Event Management (SIEM) dan Workflow Automation dalam hitungan detik. |
| Integrasi Data Massal. | Mendukung pemuatan data historis dalam jumlah besar ke dalam CMDB dan Asset Repository.  |
| Sinkronisasi Data Master. | Memastikan sinkronisasi data aset dan konfigurasi secara teratur antara sumber dan Asset Repository/CMDB.  |

## Baseline Non-Fungsional 
Baseline non-fungsional menjelaskan kriteria kinerja, keandalan, dan keamanan Lapisan DI&I.

### 1. Kinerja dan Skalabilitas 

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Latensi. | Latensi pemrosesan data (dari sumber hingga lapisan integrasi) untuk data real-time tidak boleh melebihi 5 detik.  |
| Throughput. | Mampu menangani throughput data puncak sebesar [placeholder] peristiwa per detik.  |
| Skalabilitas. | Harus mampu ditingkatkan secara horizontal untuk mengakomodasi pertumbuhan jumlah perangkat dan volume data sebesar 25% per tahun.  |

### 2. Keandalan dan Ketersediaan 

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Ketersediaan. | Lapisan DI&I harus memiliki ketersediaan 99.9% (Tier III).  |
| Toleransi Kegagalan. | Harus memiliki mekanisme failover otomatis jika terjadi kegagalan node dan mencegah kehilangan data selama transit.  |
| Pemulihan Bencana. | Harus mendukung replikasi data asinkron ke lokasi DR Place dan mampu memulihkan layanan dalam RTO (Recovery Time Objective) 4 jam.  |

### 3. Keamanan 

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Enkripsi saat Transit. | Semua komunikasi Lapisan DI&I dengan sumber data dan sistem hilir harus dienkripsi (misalnya, TLS 1.2+).  |
| Otentikasi dan Otorisasi. | Harus menerapkan mekanisme otentikasi yang kuat untuk mengakses sumber data dan API.  |
| Audit Trail. | Semua operasi pemrosesan data harus dicatat untuk keperluan audit dan kepatuhan (disimpan selama 6 bulan).  |

### 4. Kemudahan Pengelolaan (Manageability) 

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pemantauan. | Harus menyediakan metrik kinerja dan status kesehatan Lapisan DI&I ke alat pemantauan eksternal.  |
| Konfigurasi. | Semua alur (pipeline) integrasi harus dikelola melalui konfigurasi terpusat (Infrastructure as Code) yang terdokumentasi dalam File.  |

---
Dokumen ini akan ditinjau dalam rapat Peninjauan Baseline yang akan diselenggarakan pada Calendar event, Date.

Dibuat oleh: Person 