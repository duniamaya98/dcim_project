# [cite_start]Kerangka Prioritas dan Perjanjian Tingkat Layanan (SLA) untuk Komponen Configuration Management Database (CMDB) [cite: 229]

[cite_start]**Proyek:** Data Center Infrastructure Management (DCIM) [cite: 230]
[cite_start]**Nama Dokumen:** IF-SLA_&_Prioritization-FIT041-20260126-CMDB [cite: 231]
[cite_start]**Versi:** 1.0 [cite: 232]
[cite_start]**Tanggal Revisi:** Date [cite: 233]

## [cite_start]1. Pendahuluan [cite: 234]
[cite_start]Dokumen ini menetapkan Perjanjian Tingkat Layanan (SLA) dan Kerangka Prioritas Operasional untuk Komponen Configuration Management Database (CMDB) dalam Proyek DCIM[cite: 235]. [cite_start]CMDB berfungsi sebagai sumber kebenaran tunggal (SSOT) untuk semua aset konfigurasi[cite: 236].

### 1.1. [cite_start]Tujuan [cite: 237]
* [cite_start]Menetapkan Target Tingkat Layanan (SLO) untuk akurasi data (CI Accuracy) dan integritas keterkaitan antar CI[cite: 238].
* [cite_start]Menciptakan model terstruktur untuk memprioritaskan item konfigurasi (CI)[cite: 239].
* [cite_start]Menentukan peran dan tanggung jawab untuk pemeliharaan model CI dan pembaruan data[cite: 240].

### 1.2. [cite_start]Ruang Lingkup [cite: 242]
[cite_start]Berlaku untuk seluruh manajemen data dalam CMDB DCIM, mencakup Configuration Items (CIs) (Aset Fisik, Aplikasi Logis, Lokasi) dan Proses Data (Akuisisi data, Rekonsiliasi, Validasi)[cite: 243, 244, 245].

## [cite_start]2. Definisi Layanan (SLA) untuk Komponen CMDB [cite: 248]

### 2.1. [cite_start]Akurasi dan Integritas Data [cite: 250]
| Parameter | Target SLA | Justifikasi |
| :--- | :--- | :--- |
| Akurasi CI | ≥ 99.5% (untuk CI Kritis/P1) | [cite_start]Diperlukan untuk menghindari kesalahan fatal saat Incident atau Change[cite: 251]. |
| Integritas Keterkaitan | 100% (untuk Keterkaitan P1) | [cite_start]Keterkaitan harus lengkap untuk analisis dampak insiden yang akurat[cite: 251]. |
| Tingkat Duplikasi CI | Maksimal 0.1% | [cite_start]Duplikasi CI menyebabkan kebingungan operasional dan pelaporan yang salah[cite: 251]. |

### 2.2. [cite_start]Kinerja dan Ketersediaan [cite: 252]
| Parameter | Target SLA | Definisi |
| :--- | :--- | :--- |
| Ketersediaan API CMDB | 99.9% (Per Bulan) | [cite_start]API harus tersedia untuk dukungan otomatis dan aplikasi DCIM[cite: 253]. |
| Query Performance | Maksimal < 3 Detik | [cite_start]Waktu respons maksimum untuk kueri standar[cite: 253]. |
| Jadwal Pemeliharaan | Maksimal 1 Jam/Bulan | [cite_start]Harus dilakukan di luar jam operasional (misalnya, 02:00-03:00 WIB)[cite: 253]. |

### 2.3. [cite_start]Data Freshness (Ketepatan Waktu Pembaruan) [cite: 254]
| Parameter | Target SLA | Definisi |
| :--- | :--- | :--- |
| Freshness Data Otomatis (P1) | Maksimal 24 Jam | [cite_start]Waktu maksimum antara perubahan terdeteksi oleh Discovery Tool hingga diperbarui di CMDB[cite: 256]. |
| Freshness Data Manual (P2/P3) | Maksimal 2 Hari Kerja | [cite_start]Pembaruan data yang memerlukan input manual[cite: 256]. |
| Pembaruan Status Real-Time (P1)| Near Real-Time (NRT) | [cite_start]Untuk status operasional CI P1 diperbarui di bawah 5 menit[cite: 256]. |

### 2.4. [cite_start]Waktu Respons dan Resolusi Dukungan [cite: 257]
| Tingkat Keparahan | Klasifikasi Insiden | Waktu Respons | Waktu Resolusi (MTTR) |
| :--- | :--- | :--- | :--- |
| Severity 1 (Kritis) | Kegagalan Total API CMDB; Kesalahan Power Path. | 15 Menit | [cite_start]2 Jam [cite: 259] |
| Severity 2 (Tinggi) | Kegagalan Discovery Data P1; Akurasi CI P1 < 98.0%. | 30 Menit | [cite_start]4 Jam [cite: 259] |
| Severity 3 (Menengah) | Duplikasi CI > 0.1%; Kesalahan data minor. | 1 Jam | [cite_start]1 Hari Kerja [cite: 259] |
| Severity 4 (Rendah) | Permintaan laporan ad-hoc. | 2 Jam | [cite_start]3 Hari Kerja [cite: 259] |

## [cite_start]3. Model Prioritas Configuration Item (CI) [cite: 260]

### 3.1. [cite_start]Matriks Prioritas CI (P1-P4) [cite: 263]
| Prioritas | Deskripsi Dampak Operasional | Contoh CI | Prioritas Akurasi Data |
| :--- | :--- | :--- | :--- |
| P1: Kritis | Kegagalan data menyebabkan Kegagalan Layanan (Outage). | Perangkat Core Network, Firewall, UPS/PDU, Host. | [cite_start]≥ 99.5% [cite: 264] |
| P2: Tinggi | Kegagalan data menyebabkan Degradasi Layanan. | Server Non-Kritis, Switch, SAN Storage. | [cite_start]≥ 99.0% [cite: 264] |
| P3: Menengah| Kegagalan menyebabkan Kesalahan Perencanaan. | Data Lokasi, Kontrak/Garansi. | [cite_start]≥ 98.0% [cite: 264] |
| P4: Pendukung| Audit atau referensi historis. | Dokumen Lampiran, Retired Assets. | [cite_start]≥ 95.0% [cite: 264] |

### 3.2. [cite_start]Prioritas Sumber dan Metode Integrasi [cite: 265]
1. [cite_start]**Automated Discovery** (NRT - 24 Jam) [cite: 267]
2. [cite_start]**API Integration** (24 Jam) [cite: 267]
3. [cite_start]**Manual Import** (Sesuai kebutuhan) [cite: 267]

## [cite_start]4. Peran dan Tanggung Jawab [cite: 268]
* [cite_start]**CMDB Manager:** Pemilik Proses SLA, memastikan Akurasi CI[cite: 269].
* [cite_start]**DCIM/Operations Team:** Konsumen Data Utama, melaporkan insiden data[cite: 269].
* [cite_start]**Source System Owners:** Memastikan keandalan data sumber[cite: 269].
* [cite_start]**Automation Developers:** Memelihara Discovery Tools[cite: 269].

## [cite_start]5. Metrik dan Pelaporan [cite: 270]
| KPI | Definisi | Target Kepatuhan |
| :--- | :--- | :--- |
| CI Accuracy Rate (P1) | Persentase CI P1 yang tervalidasi akurat | > [cite_start]99.5% [cite: 273] |
| Data Freshness Score | Persentase data otomatis (P1) disinkronkan < 24 jam | > [cite_start]99.0% [cite: 273] |
| Discovery Success Rate| Persentase upaya discovery berhasil | > [cite_start]98.0% [cite: 273] |

## [cite_start]6. Tinjauan dan Revisi [cite: 276]
[cite_start]Dokumen ini akan ditinjau secara formal **Dua Tahunan (Bi-annual)**[cite: 278]. [cite_start]Revisi disetujui oleh **CMDB Manager** dan **Project Owner (DCIM)**[cite: 279].