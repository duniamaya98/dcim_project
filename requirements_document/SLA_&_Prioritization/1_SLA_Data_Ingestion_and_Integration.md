# [cite_start]Kerangka Prioritas dan Perjanjian Tingkat Layanan (SLA) untuk Komponen Data Ingestion & Integration [cite: 170, 171]

[cite_start]**Proyek:** Data Center Infrastructure Management (DCIM) [cite: 172]
[cite_start]**Nama Dokumen:** IF-SLA_&_Prioritization-FIT041-20260126-DataIngestion [cite: 173]
[cite_start]**Versi:** 1.0 [cite: 174]
[cite_start]**Tanggal Revisi:** Date [cite: 175]

## [cite_start]1. Pendahuluan [cite: 176]
[cite_start]Dokumen ini menetapkan Perjanjian Tingkat Layanan (SLA) dan Kerangka Prioritas Operasional untuk Komponen Data Ingestion & Integration (DI&I) dalam Proyek DCIM[cite: 177]. [cite_start]Komponen DI&I bertanggung jawab untuk mengumpulkan, menormalisasi, dan mengintegrasikan data real-time dari berbagai sistem operasional dan lingkungan pusat data ke dalam platform DCIM[cite: 178].

### 1.1. [cite_start]Tujuan [cite: 179]
* [cite_start]Menetapkan Target Tingkat Layanan (Service Level Objectives/SLO) yang terukur untuk ketersediaan, kinerja, dan akurasi data[cite: 180].
* [cite_start]Menciptakan model terstruktur untuk memprioritaskan sumber data (data source) dan insiden integrasi berdasarkan dampak bisnis dan kebutuhan real-time[cite: 181].
* [cite_start]Menentukan peran dan tanggung jawab yang jelas untuk pemeliharaan dan respons terhadap masalah integrasi data[cite: 182].

### 1.2. [cite_start]Ruang Lingkup [cite: 183]
[cite_start]Dokumen ini berlaku untuk seluruh proses end-to-end Komponen DI&I, mencakup koneksi ke sistem sumber (misalnya, BMS, EPMS, CMDB, Virtualization Platform), mekanisme transmisi data, pipeline normalisasi, dan pengiriman data ke repositori utama DCIM[cite: 184].

### 1.3. [cite_start]Glosarium Istilah Utama [cite: 185]
| Istilah | Penjelasan |
| :--- | :--- |
| **DI&I** | Data Ingestion & Integration. [cite_start]Komponen yang mengumpulkan dan memproses data dari sumber[cite: 186]. |
| **NRT** | Near Real-Time. [cite_start]Data yang memiliki latensi sangat rendah (≤60 detik), penting untuk pemantauan fisik dan peringatan[cite: 186]. |
| **Batch** | [cite_start]Proses data periodik yang tidak memerlukan latensi NRT, seperti data historis atau data konfigurasi[cite: 186]. |
| **MTTR** | Mean Time to Resolution. [cite_start]Waktu rata-rata untuk memperbaiki dan memulihkan kegagalan layanan atau data[cite: 186]. |
| **EPS** | Events per Second. [cite_start]Metrik throughput yang mengukur volume data yang dapat diproses per detik[cite: 186]. |

## [cite_start]2. Definisi Layanan (SLA) untuk Komponen DI&I [cite: 187]
[cite_start]Bagian ini merinci parameter kinerja minimum yang disepakati untuk menjamin integritas dan ketepatan waktu data DCIM[cite: 188].

### 2.1. [cite_start]Ketersediaan Layanan (Service Availability) [cite: 189]
| Parameter | Target SLA | Justifikasi |
| :--- | :--- | :--- |
| Target Uptime | 99.95% (Per Bulan) | Target ini setara dengan waktu henti (downtime) maksimum 21 menit 53 detik per bulan. [cite_start]Waktu henti dihitung sebagai kegagalan dalam memproses data dari sumber kritis[cite: 190]. |
| Jadwal Pemeliharaan Terjadwal | Maksimal 1 jam/bulan | [cite_start]Dilakukan pada periode dampak terendah (low-impact period, misalnya, 02:00 - 03:00 WIB), dengan pemberitahuan minimal 72 jam sebelumnya kepada Data Source Owners[cite: 190]. |
| Pemulihan Kegagalan (Failover Time) | Maksimal 5 Menit | [cite_start]Waktu yang dibutuhkan sistem untuk beralih ke komponen cadangan setelah terdeteksi kegagalan pada primary processing node[cite: 190]. |

### 2.2. [cite_start]Kinerja dan Latensi (Performance and Latency) [cite: 191]
[cite_start]Kinerja DI&I diukur berdasarkan kecepatan pemrosesan data (latensi) dan volume yang ditangani (throughput)[cite: 192].

| Parameter | Target SLA | Definisi |
| :--- | :--- | :--- |
| Latensi NRT (Near Real-Time) | ≤ 60 Detik | Waktu maksimum antara pencatatan peristiwa di sumber (misalnya, sensor suhu) dan ketersediaannya di platform DCIM. [cite_start]Berlaku untuk P1 dan P2[cite: 193]. |
| Latensi Batch | ≤ 2 Jam | Waktu maksimum untuk pemrosesan data non-kritis dan data snapshot (misalnya, data kapasitas bulanan dari SAN). [cite_start]Berlaku untuk P3 dan P4[cite: 193]. |
| Throughput (Events per Second/EPS) | 10.000 EPS | [cite_start]Kapasitas minimum DI&I untuk memproses Events per Second tanpa mengalami backlog atau degradasi Latensi NRT/Batch[cite: 193]. |

### 2.3. [cite_start]Akurasi dan Integritas Data [cite: 194]
| Parameter | Target SLA | Penjelasan |
| :--- | :--- | :--- |
| Akurasi Data (Data Accuracy) | ≥ 99.9% | [cite_start]Persentase data yang dikumpulkan, dinormalisasi, dan disimpan di DCIM tanpa kesalahan format, duplikasi, atau missing value yang disebabkan oleh pipeline DI&I[cite: 195]. |
| Integritas Skema | 100% | Skema data yang dikirim oleh DI&I harus selalu konsisten dengan skema yang dibutuhkan oleh DCIM. [cite_start]Penyimpangan wajib memicu alert Kritis[cite: 195]. |

### 2.4. [cite_start]Cakupan Sumber Data (Data Source Coverage) [cite: 196]
[cite_start]Layanan DI&I WAJIB terintegrasi dan memproses data dari semua sistem DCIM kritis[cite: 197].

| Sumber Data (Contoh) | Jenis Data | Status Integrasi | Prioritas |
| :--- | :--- | :--- | :--- |
| Building Management System (BMS) | Suhu, Kelembaban, Power | Terintegrasi | [cite_start]P1 (Kritis) [cite: 199] |
| Electrical Power Monitoring System (EPMS) | Daya (kW, kVA), Konsumsi | Terintegrasi | [cite_start]P1 (Kritis) [cite: 199] |
| Virtualization Platform (VMware/Hyper-V) | Compute Performance, Kapasitas | Terintegrasi | [cite_start]P2 (Tinggi) [cite: 199] |
| Configuration Management Database (CMDB) | Data Aset, Metadata | Batch | [cite_start]P3 (Menengah) [cite: 199] |
| Network Management System (NMS) | Network Latency, Utilization | Terintegrasi | [cite_start]P2 (Tinggi) [cite: 199] |

### 2.5. [cite_start]Waktu Respons dan Resolusi Dukungan [cite: 200]
[cite_start]Target waktu respons dan resolusi untuk insiden yang memengaruhi pipeline DI&I, berdasarkan prioritas insiden[cite: 201].

| Tingkat Keparahan | Klasifikasi Insiden | Waktu Respons Target | Waktu Resolusi Target (MTTR) |
| :--- | :--- | :--- | :--- |
| Kritis (Severity 1) | Kegagalan Total DI&I atau kegagalan ingestion dari Sumber P1 (misalnya, BMS/EPMS down). | 15 Menit | [cite_start]2 Jam [cite: 202] |
| Tinggi (Severity 2) | Kegagalan ingestion dari Sumber P2; Throughput di bawah 50% dari target (10.000 EPS). | 30 Menit | [cite_start]4 Jam [cite: 202] |
| Menengah (Severity 3) | Latensi NRT di atas 60 detik secara konsisten; Kegagalan ingestion dari Sumber P3/P4. | 1 Jam | [cite_start]1 Hari Kerja [cite: 202] |
| Rendah (Severity 4) | Masalah Akurasi Data minor (<0.1%), permintaan ad-hoc laporan data quality. | 2 Jam | [cite_start]3 Hari Kerja [cite: 202] |

## [cite_start]3. Model Prioritas Data dan Insiden [cite: 203]
### 3.1. [cite_start]Kriteria Penilaian Prioritas Data (P1-P4) [cite: 206]
* [cite_start]**Dampak pada Operasi DCIM:** Konsekuensi dari missing data[cite: 208].
* [cite_start]**Kebutuhan Real-Time:** Apakah data digunakan untuk peringatan/kontrol otomatis[cite: 209].
* [cite_start]**Kompleksitas Integrasi:** Tingkat kesulitan pemeliharaan dan normalisasi data[cite: 210].

### 3.2. [cite_start]Matriks Prioritas Data [cite: 211]
| Prioritas | Dampak Operasi | Kebutuhan Real-Time | Contoh Data Sumber | Target Latensi |
| :--- | :--- | :--- | :--- | :--- |
| P1: Kritis | Kegagalan Total (Outage) | WAJIB Real-Time (NRT) | BMS (Suhu, Daya), EPMS. | [cite_start]≤ 60 Detik [cite: 212] |
| P2: Tinggi | Degradasi Layanan Signifikan | Real-Time atau NRT | Virtualization Platform, NMS. | [cite_start]≤ 60 Detik [cite: 212] |
| P3: Menengah | Pengaruh pada Perencanaan | Tidak Real-Time (Batch) | CMDB (Metadata Aset), Data Histori Log. | [cite_start]≤ 2 Jam [cite: 212] |
| P4: Pendukung | Dampak Minor/Audit | Batch atau Asinkron | Data Audit Kepatuhan, Laporan Eksternal. | [cite_start]≤ 2 Jam [cite: 212] |

### 3.3. [cite_start]Proses Eskalasi Insiden DI&I [cite: 213]
| Tingkat Keparahan Insiden | Jalur Eskalasi (Jika Terlewati 30 Menit) | Kontak Eskalasi |
| :--- | :--- | :--- |
| Severity 1 (Kritis) | Tier 1 (DI&I Engineer) -> Tier 2 (DCIM Architect) -> Project Owner & Vendor | [cite_start]Person (Project Owner) [cite: 215] |
| Severity 2 (Tinggi) | Tier 1 (DI&I Engineer) -> Tier 2 (DCIM Architect) | [cite_start]Person (DCIM Architect) [cite: 215] |
| Severity 3/4 | Tier 1 (DI&I Engineer) | [cite_start]Person (Operations Team Lead) [cite: 215] |

## [cite_start]4. Peran dan Tanggung Jawab [cite: 216]
* [cite_start]**Project Owner (DCIM):** Otoritas tertinggi SLA, penerima laporan insiden kritis[cite: 217].
* [cite_start]**Integration Team (DI&I Engineer):** Pemeliharaan pipeline, troubleshooting insiden[cite: 217].
* [cite_start]**Data Source Owners:** Memastikan ketersediaan API/Gateway Sumber Data[cite: 217].
* [cite_start]**Operations Team:** Pemantauan dashboard DI&I harian, triage awal[cite: 217].
* [cite_start]**Vendor (Jika Ada):** Dukungan teknis dan middleware update[cite: 217].

## [cite_start]5. Metrik dan Pelaporan [cite: 218]
| KPI | Definisi | Target Kepatuhan |
| :--- | :--- | :--- |
| Ketersediaan Layanan | Persentase uptime pipeline DI&I | > [cite_start]99.95% [cite: 221] |
| MTTD | Waktu rata-rata kegagalan hingga alert terdeteksi | [cite_start]< 5 Menit [cite: 221] |
| MTTR | Waktu rata-rata perbaikan kegagalan | [cite_start]Sesuai SLA 2.5 [cite: 221] |
| Latensi NRT Kepatuhan | Persentase data P1 dan P2 diproses ≤ 60 detik | > [cite_start]99.5% [cite: 221] |
| Data Accuracy Kepatuhan | Persentase data bebas dari kesalahan pipeline | [cite_start]≥ 99.9% [cite: 221] |

## [cite_start]6. Tinjauan dan Revisi [cite: 224]
[cite_start]Dokumen SLA akan ditinjau secara formal **setiap 3 bulan (Quarterly)**[cite: 226]. [cite_start]Setiap revisi harus disetujui oleh **Project Owner (DCIM)**[cite: 227].