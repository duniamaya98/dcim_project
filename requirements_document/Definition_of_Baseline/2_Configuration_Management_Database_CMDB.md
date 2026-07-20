# [cite_start]Definisi Baseline (Fungsional dan Non-Fungsional) - Configuration Management Database (CMDB) [cite: 30]

[cite_start]Dokumen ini mendefinisikan baseline fungsional dan non-fungsional untuk komponen Configuration Management Database (CMDB) dalam proyek Data Center Infrastructure Management (DCIM)[cite: 31].

## [cite_start]Persyaratan Proyek DCIM [cite: 32]
[cite_start]Proyek DCIM bertujuan untuk menyediakan visibilitas dan kontrol yang komprehensif atas infrastruktur pusat data[cite: 33]. [cite_start]CMDB adalah jantung dari sistem ini, bertindak sebagai repositori terpusat untuk semua informasi konfigurasi aset dan hubungan[cite: 34].

## [cite_start]Komponen: Configuration Management Database (CMDB) [cite: 35]

| Aspek | Deskripsi |
| :--- | :--- |
| **Tujuan** | [cite_start]Menyediakan pandangan terpusat dan terperinci mengenai semua Configuration Item (CI) dalam pusat data, statusnya, dan hubungannya untuk mendukung manajemen aset, insiden, dan perubahan. [cite: 36] |
| **Sumber Data** | [cite_start]Data Ingestion & Integration Layer, Asset Repository, Sumber Data Manual (misalnya, tim Operasi). [cite: 36] |
| **Penerima Data** | [cite_start]Analytics & AI Engine, Workflow Automation, Security Information & Event Management (SIEM), Modul Visualisasi & Pelaporan. [cite: 36] |

## [cite_start]Baseline Fungsional [cite: 37]
[cite_start]Baseline fungsional menjelaskan kemampuan yang harus dimiliki oleh CMDB untuk memenuhi persyaratan proyek DCIM[cite: 38].

### [cite_start]1. Model Data dan CI (Configuration Item) [cite: 39]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Mendukung model data CMDB standar. | [cite_start]Harus mampu merepresentasikan hierarki aset data center (misalnya, Gedung, Lantai, Ruang, Rak, Perangkat) dan mendukung model data yang fleksibel untuk CI kustom. [cite: 40] |
| Pengelolaan Atribut CI. | [cite_start]Mampu menyimpan atribut kritis untuk setiap CI, termasuk spesifikasi teknis, status operasional (misalnya, In Use, Reserved, Decommissioned), data kepemilikan, dan lokasi fisik yang tepat (misalnya, Rack U Position). [cite: 40] |
| Definisi Hubungan CI. | [cite_start]Harus memungkinkan definisi hubungan antar-CI yang kompleks dan multi-level (misalnya, Server A terhubung ke Port X Switch Y; Aplikasi Z berjalan di Server A). [cite: 40] |

### [cite_start]2. Pengambilan Data dan Sinkronisasi [cite: 41]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Integrasi dengan Data Ingestion Layer. | [cite_start]Mampu menerima pembaruan data real-time dan massal (bulk load) dari Data Ingestion & Integration Layer untuk menjaga CI status operasional, metrik kinerja, dan kejadian alarm tetap up-to-date. [cite: 42] |
| Mekanisme Sinkronisasi. | [cite_start]Mendukung sinkronisasi data yang terjadwal dan berbasis peristiwa dari Asset Repository untuk memastikan konsistensi data master aset. [cite: 42] |
| Pembaruan Manual. | [cite_start]Harus menyediakan antarmuka yang aman dan mudah digunakan untuk pembaruan manual informasi CI oleh tim Operasi yang terdokumentasi dalam File. [cite: 42] |

### [cite_start]3. Query dan Akses Data [cite: 43]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pencarian dan Filter. | [cite_start]Harus menyediakan kemampuan pencarian yang kuat (full-text search) dan kemampuan untuk memfilter CI berdasarkan atribut, status, dan hubungan (misalnya, "Tampilkan semua server yang menjalankan aplikasi kritis di lantai 3 dengan status alert"). [cite: 44] |
| API Akses Data. | [cite_start]Harus mengekspos API yang aman dan terstruktur (misalnya, RESTful API) untuk memungkinkan sistem hilir (Analytics Engine, Workflow Automation) mengakses dan memanipulasi data CMDB. [cite: 44] |
| Visualisasi Hubungan. | [cite_start]Mampu menampilkan peta topologi atau diagram visual yang menunjukkan hubungan antar-CI untuk analisis dampak perubahan dan insiden. [cite: 44] |

## [cite_start]Baseline Non-Fungsional [cite: 45]
[cite_start]Baseline non-fungsional menjelaskan kriteria kinerja, keandalan, dan keamanan CMDB[cite: 46].

### [cite_start]1. Kinerja dan Skalabilitas [cite: 47]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Waktu Respons Query. | [cite_start]Waktu respons untuk query tunggal CI/relationship kritis tidak boleh melebihi 2 detik. [cite: 48] |
| Throughput Pembaruan. | [cite_start]Harus mampu memproses pembaruan massal (bulk updates) dari Lapisan Data Ingestion sebesar CI per menit. [cite: 48] |
| Skalabilitas. | [cite_start]Harus mampu ditingkatkan untuk mengakomodasi peningkatan jumlah CI sebesar 50% dalam 3 tahun ke depan tanpa penurunan kinerja yang signifikan. [cite: 48] |

### [cite_start]2. Keandalan dan Ketersediaan [cite: 49]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Ketersediaan. | [cite_start]CMDB harus memiliki ketersediaan 99.99%. [cite: 50] |
| Integritas Data. | [cite_start]Harus menerapkan mekanisme validasi dan integritas data untuk mencegah CI yang duplikat, tidak valid, atau memiliki hubungan yang rusak (orphan). [cite: 50] |
| Pemulihan Bencana. | [cite_start]Harus mendukung replikasi data ke lokasi Place dan mampu memulihkan layanan dalam RTO (Recovery Time Objective) 1 jam untuk data CI kritis. [cite: 50] |

### [cite_start]3. Keamanan [cite: 51]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Kontrol Akses. | [cite_start]Harus menerapkan kontrol akses berbasis peran (Role-Based Access Control/RBAC) untuk menentukan siapa yang dapat melihat, membuat, atau memodifikasi CI dan hubungannya. [cite: 52] |
| Enkripsi Data. | [cite_start]Data CI sensitif (misalnya, kredensial manajemen) harus dienkripsi saat disimpan (Encryption at Rest). [cite: 52] |
| Audit Trail. | [cite_start]Semua perubahan pada CI (termasuk siapa, kapan, dan apa yang diubah) harus dicatat dalam audit trail yang tidak dapat diubah (immutable log) dan disimpan selama minimal 1 tahun. [cite: 52] |

### [cite_start]4. Kemudahan Pengelolaan (Manageability) [cite: 53]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pemantauan. | [cite_start]Harus menyediakan metrik kesehatan basis data, kinerja query, dan status integrasi ke alat pemantauan eksternal. [cite: 54] |
| Backup dan Restore. | [cite_start]Harus mendukung jadwal backup harian secara otomatis dengan periode retensi 30 hari. [cite: 54] |
| Dokumentasi. | [cite_start]Skema CMDB dan model data CI harus didokumentasikan dalam File. [cite: 54] |

---
[cite_start]Dokumen ini akan ditinjau dalam rapat Peninjauan Baseline yang akan diselenggarakan pada Calendar event, Date[cite: 55].

[cite_start]Dibuat oleh: Person [cite: 56]