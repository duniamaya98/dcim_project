# Prosedur Operasi Standar (SOP) - Configuration Management Database (CMDB)

## 1. Tujuan, Latar Belakang, dan Ruang Lingkup

### 1.1 Tujuan
SOP ini mendefinisikan komponen CMDB secara formal dan teknis, dengan tujuan spesifik:
* Menetapkan definisi dan fungsi CMDB sebagai pusat kebenaran (Single Source of Truth).
* Menguraikan standar model data, atribut CI, dan mekanisme hubungan.
* Menetapkan proses siklus hidup CI dan kebijakan tata kelola data.
* Menjadi referensi tunggal untuk perancangan, implementasi, dan operasionalisasi.

### 1.2 Latar Belakang
CMDB adalah fondasi kritikal untuk manajemen infrastruktur, penting untuk manajemen insiden, perubahan, kapasitas, dan otomatisasi.

### 1.3 Ruang Lingkup
Meliputi definisi arsitektural, identifikasi CI, mekanisme integrasi, dan proses manajemen siklus hidup CI.

## 2. Definisi dan Peran Inti CMDB dalam DCIM

### 2.1 Definisi
Repositori terpusat untuk menyimpan informasi detail (CI) seluruh infrastruktur IT dan Fasilitas, berfokus pada data statis/semi-statis.

### 2.2 Peran Kunci
* **Single Source of Truth:** Pandangan konsisten infrastruktur.
* **Penyedia Konteks:** Konteks untuk data metrik.
* **Aset Dasar Operasi:** Dukungan manajemen insiden dan perubahan.
* **Dasar Analitik:** Data dasar untuk Analytics & AI Engine.

## 3. Hubungan CMDB dengan Komponen Lain
CMDB terintegrasi dengan Data Ingestion Layer (update otomatis), Asset Repository (data teknis & relasional vs finansial), Sistem Fasilitas (BMS, NMS), ITSM (dasar data insiden/perubahan), ERP (data akuntansi), dan Workflow Automation (pemicu otomatisasi).

## 4. Klasifikasi Configuration Item (CI)
Kategori mencakup Fasilitas & Lokasi (Room, Rack), Daya (UPS, PDU), Mekanikal (Chiller, CRAC), IT Computing (Server, Storage), Jaringan (Switch, Router), Virtualisasi & Cloud (VM), IoT & Sensor (Sensor Suhu).

## 5. Model Data CMDB

### 5.1 Atribut Kunci CI
Atribut minimum meliputi `CI_ID`, `Asset_ID`, `CI_Type`, `Status`, `Location`, `Owner/Support Group`, `Configuration Data`, dan `Last_Update_Date`.

### 5.2 Hubungan CI
Memodelkan topologi infrastruktur melalui tipe hubungan: Dependency, Containment, Connectivity, Services.

## 6. Sumber Data CI dan Mekanisme Populasi Data
* **Automatic Discovery:** Penemuan otomatis CI/pembaruan konfigurasi.
* **System Integration:** Integrasi API/Database dengan sistem sumber.
* **Manual Input:** CI yang tidak dapat ditemukan secara otomatis.
* **Bulk Import:** Implementasi awal atau migrasi.

## 7. Proses Siklus Hidup CI
Proses terdefinisi dari CI Creation (In Stock), Update/Change, Verification (Audit), Audit Kepatuhan, hingga Retirement (setelah masa retensi).

## 8. Tata Kelola Data dan Kebijakan Kualitas

### 8.1 Kebijakan Kualitas
Accuracy (> 98%), Completeness, Consistency, Timeliness.

### 8.2 Tata Kelola dan Pemilik Data
Penunjukan Data Owner dan Schema Management via Change Control Board (didokumentasikan di File).

## 9. Integrasi CMDB dengan Proses Operasional (ITIL)
* **Change Management:** Analisis dampak dan verifikasi pasca-perubahan.
* **Incident/Problem Management:** Identifikasi dampak dan analisis akar masalah.
* **Capacity/Risk Management:** Data dasar kapasitas dan pemodelan risiko.

## 10. Pemantauan, Pelaporan, dan KPI
KPI mencakup Akurasi Data (>98%), Relasi Kunci (>95%), CI Stale (<1%), Keberhasilan Integrasi Otomatis (>99.5%).

## 11. Keamanan Data dan Kontrol Akses
* **Kontrol Akses:** Role-Based Access (Read-Only dan Write).
* **Audit Trail:** Transaksi dicatat selama Date.
* **Enkripsi:** Data sensitif dienkripsi at rest dan in transit.

## 12. Peran, Tanggung Jawab, dan RACI
(Rincian matriks RACI tersedia pada dokumen asli untuk DCIM Solution Architect, CMDB Administrator, dsb).