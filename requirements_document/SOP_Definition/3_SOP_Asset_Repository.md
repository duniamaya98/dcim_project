# Prosedur Operasi Standar (SOP) - Asset Repository

## 1. Tujuan, Latar Belakang, dan Ruang Lingkup

### 1.1 Tujuan
* Menetapkan definisi dan fungsi Asset Repository sebagai Single Source of Truth untuk data finansial, kontraktual, dan kepemilikan aset.
* Menguraikan struktur data, atribut, dan klasifikasi aset.
* Menetapkan proses manajemen siklus hidup dan tata kelola data.

### 1.2 Latar Belakang
Asset Repository melengkapi CMDB dengan menyediakan konteks nilai, kepemilikan, dan kontrak untuk mendukung pengambilan keputusan perencanaan dan pengadaan.

### 1.3 Ruang Lingkup
Berlaku untuk perancangan, pengembangan, pengisian data, dan operasionalisasi, meliputi klasifikasi aset, spesifikasi atribut dari PO hingga Decommissioning, dan kebijakan kualitas data.

## 2. Definisi dan Peran Inti dalam DCIM

### 2.1 Definisi
Repositori terpusat yang berfokus pada manajemen aset (finansial, kontraktual, inventaris), melacak aset dari perencanaan hingga end-of-life.

### 2.2 Peran Kunci
Single Source of Truth (what we own), Dukungan Finansial (depresiasi, anggaran), Manajemen Kontrak (garansi), Verifikasi Data CMDB.

### 2.3 Hubungan dengan CMDB
Fokus Asset Repository adalah finansial/kontrak (Asset ID), sedangkan CMDB berfokus pada teknis/konfigurasi (CI ID). Memiliki relasi 1:1 atau 1:N wajib.

## 3. Jenis Aset yang Dikelola
Mencakup domain IT Computing (Server), Jaringan (Switch), Fasilitas & Lokasi, Daya (UPS), Mekanikal (Chiller), Keamanan (CCTV), Virtualisasi & Cloud, IoT & Sensor.

## 4. Struktur Data dan Atribut Kunci Aset

### 4.1 Klasifikasi Aset
Menggunakan standar taksonomi konsisten (Tipe, Sub-Tipe, Produsen, Model).

### 4.2 Atribut Kunci (Wajib)
`Asset_ID`, `CI_ID`, `Asset_Tag`, `Status`, `PO_Number`, `Purchase_Date`, `Cost/Value`, `Warranty_Expiry_Date`, `Owner/Department`, `Location_Tracking`, `Last_Audit_Date`.

## 5. Proses Siklus Hidup Aset
Tahapan meliputi: Planning & Budgeting (Planned), Procurement (Ordered), Registration & Receiving (In Stock, Asset Tag), Deployment & Use (In Use, update CMDB), Maintenance & Change (termasuk relocation), Decommissioning & Disposal (Retired/Disposed).

## 6. Sumber Data dan Mekanisme Pencatatan
* **ERP/Sistem Keuangan:** Integrasi API untuk data finansial (PO).
* **Data Ingestion/CMDB:** Sinkronisasi status dan lokasi fisik.
* **Manual Input:** Aset non-PO dengan form terstruktur.
* **Bulk Import:** Impor massal via CSV/Spreadsheet.
* **DMS:** Tautan ke dokumen pendukung (Invoice, Garansi).

## 7. Integrasi Asset Repository dengan Sistem Lain
Terintegrasi wajib dengan CMDB, ERP (depresiasi), ITSM (untuk manajemen insiden/perubahan), Sistem Fasilitas (BMS, NMS), dan Platform Pihak Ketiga (API vendor).

## 8. Manajemen Kualitas, Konsistensi, dan Audit

### 8.1 Kebijakan Kualitas Data
Accuracy (>99%), Completeness (atribut wajib terisi), Consistency (dengan ERP dan CMDB).

### 8.2 Audit Fisik dan Rekonsiliasi
Audit fisik (Kuartalan), Rekonsiliasi CMDB (Mingguan), Rekonsiliasi Finansial ERP (Bulanan).

## 9. Keamanan Data dan Kontrol Akses

### 9.1 Kontrol Akses
Role-Based Access Control (Read-Only dan Write khusus Asset Manager/Integration Engine).

### 9.2 Keamanan Data
Enkripsi (TLS/SSL) dan Audit Trail permanen untuk semua perubahan.

## 10. Pelaporan, Dashboard, dan KPI

### 10.1 KPI
Akurasi Inventaris Fisik (>99%), Kontrak Garansi Valid (>95%), Aset EOL (<5%), Keberhasilan Sinkronisasi (>99.9%).

### 10.2 Pelaporan Kunci
Laporan depresiasi, garansi mendekati kadaluarsa (<90 hari), inventaris fisik, discrepancy report CMDB.

## 11. Peran, Tanggung Jawab, dan RACI
(Rincian matriks RACI tersedia pada dokumen asli untuk DCIM Project Manager, Asset Manager, Finance/ERP Team, dsb).