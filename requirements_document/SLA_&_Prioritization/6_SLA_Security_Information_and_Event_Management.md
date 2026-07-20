# [cite_start]Kerangka Prioritas dan Perjanjian Tingkat Layanan (SLA) untuk Komponen SIEM (Security Information & Event Management) [cite: 443]

[cite_start]**Proyek:** Data Center Infrastructure Management (DCIM) [cite: 444]
[cite_start]**Nama Dokumen:** IF-SLA_&_Prioritization-FIT041-20260126 [cite: 445]
[cite_start]**Versi:** 1.0 [cite: 446]
[cite_start]**Tanggal Revisi:** Date [cite: 447]

## [cite_start]1. Pendahuluan [cite: 448]
[cite_start]Dokumen ini mendefinisikan SLA dan Kerangka Prioritas Operasional untuk layanan SIEM yang terintegrasi di DCIM[cite: 449].

### 1.1. [cite_start]Tujuan [cite: 450]
* [cite_start]Menetapkan parameter kinerja (SLO) untuk ketersediaan dan performa SIEM[cite: 451].
* [cite_start]Memprioritaskan insiden keamanan berdasarkan risiko dan dampak bisnis[cite: 452].

### 1.2. [cite_start]Ruang Lingkup [cite: 454]
[cite_start]Mencakup operasional pengumpulan log hingga respons insiden keamanan yang berdampak pada DCIM kritis (server, jaringan, penyimpanan, kontrol akses fisik)[cite: 455].

## [cite_start]2. Definisi Layanan (SLA) untuk SIEM [cite: 456]

### 2.1. [cite_start]Ketersediaan Layanan (Service Availability) [cite: 458]
| Parameter | Target SLA | Penjelasan |
| :--- | :--- | :--- |
| Target Uptime | 99.9% (Per Bulan) | [cite_start]Waktu henti maks 43 menit 12 detik[cite: 459]. |
| Jadwal Pemeliharaan | Maks 2 jam/bulan | [cite_start]Dilakukan di luar jam kerja (Misal: Minggu pukul 01:00)[cite: 459]. |
| Ketersediaan Agen Log| 100% | [cite_start]Semua agen pada DCIM kritis harus selalu aktif[cite: 459]. |

### 2.2. [cite_start]Kinerja dan Latensi [cite: 460]
| Parameter | Target SLA | Definisi |
| :--- | :--- | :--- |
| Latensi Koleksi Log (LCL) | Maksimal 60 detik | [cite_start]Waktu pencatatan oleh sumber hingga diterima SIEM[cite: 461]. |
| Waktu Pemrosesan (EPP) | Maksimal 120 detik | [cite_start]Waktu dari penerimaan log hingga hasil korelasi tersedia[cite: 461]. |
| Alert Delivery Time | Maksimal 5 menit | [cite_start]Waktu peringatan dikirim hingga diterima tim respons[cite: 461]. |

### 2.3. [cite_start]Kapasitas [cite: 462]
* [cite_start]**Periode Retensi (Hot Storage):** 90 Hari[cite: 463].
* [cite_start]**Periode Retensi (Cold Storage):** 1 Tahun[cite: 463].
* [cite_start]**Volume EPS Didukung:** 15.000 EPS[cite: 463].

### 2.4. [cite_start]Waktu Respons dan Resolusi Dukungan [cite: 470]
| Tingkat Keparahan | Klasifikasi Insiden | Waktu Respons | Waktu Resolusi |
| :--- | :--- | :--- | :--- |
| Severity 1 (Kritis) | Ancaman langsung DCIM (misal: ransomware aktif). | 15 Menit | [cite_start]2 Jam [cite: 472] |
| Severity 2 (Tinggi) | Potensi dampak serius (misal: malware server non-kritis). | 30 Menit | [cite_start]4 Jam [cite: 472] |
| Severity 3 (Menengah)| Perlu perhatian tanpa dampak operasional langsung. | 1 Jam | [cite_start]1 Hari Kerja [cite: 472] |

## [cite_start]3. Model Prioritas Insiden Keamanan [cite: 473]

### 3.1. [cite_start]Matriks Prioritas [cite: 488]
[cite_start]Menggabungkan Risk Level (Ancaman) dan Impact (Dampak Bisnis)[cite: 489]. [cite_start]Jika ada Pelanggaran Regulasi (Regulatory Violation), prioritas dinaikkan[cite: 490].

| Tingkat Risiko | Dampak Kritis | Dampak Tinggi | Dampak Menengah |
| :--- | :--- | :--- | :--- |
| Tinggi | Kritis | Kritis | [cite_start]Tinggi [cite: 491] |
| Sedang | Kritis | Tinggi | [cite_start]Menengah [cite: 491] |
| Rendah | Tinggi | Menengah| [cite_start]Rutin (Low) [cite: 491] |

**Target Penanganan:**
* [cite_start]**Kritis:** Ditangani segera tanpa batasan jam kerja[cite: 493].
* [cite_start]**Tinggi:** Dalam 1 Jam[cite: 493].

## [cite_start]4. Peran dan Tanggung Jawab [cite: 497]
* [cite_start]**DCIM Owner:** Otoritas kebijakan dan penerima laporan insiden Kritis[cite: 498].
* [cite_start]**Tim Keamanan:** Pemantauan 24/7 dan penanganan insiden[cite: 498].
* [cite_start]**Tim Operasi:** Memastikan ketersediaan agen log dan melakukan mitigasi[cite: 498].

## [cite_start]5. Metrik dan Pelaporan [cite: 499]
| KPI | Definisi | Target Kepatuhan |
| :--- | :--- | :--- |
| MTTD | Waktu rata-rata pencatatan hingga peringatan | [cite_start]< 15 Menit [cite: 502] |
| MTTR (Respond)| Waktu rata-rata memulai investigasi awal | [cite_start]< 30 Menit [cite: 502] |
| Kepatuhan Waktu Respons| Insiden yang direspons sesuai target SLA | > [cite_start]95% [cite: 502] |

## [cite_start]6. Tinjauan dan Revisi [cite: 505]
[cite_start]Dokumen ini ditinjau secara formal **setiap 6 bulan**[cite: 507]. [cite_start]Setiap revisi harus disetujui oleh **DCIM Owner** dan **Security Manager**[cite: 508].