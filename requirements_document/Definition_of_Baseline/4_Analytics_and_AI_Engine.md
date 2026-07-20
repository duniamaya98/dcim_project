# [cite_start]Definisi Baseline (Fungsional dan Non-Fungsional) - Analytics & AI Engine [cite: 87]

[cite_start]Dokumen ini mendefinisikan baseline fungsional dan non-fungsional untuk komponen Analytics & AI Engine dalam proyek Data Center Infrastructure Management (DCIM)[cite: 88].

## [cite_start]Persyaratan Proyek DCIM [cite: 89]
[cite_start]Proyek DCIM bertujuan untuk menyediakan visibilitas dan kontrol yang komprehensif atas infrastruktur pusat data[cite: 90]. [cite_start]Komponen Analytics & AI Engine sangat penting untuk mengubah data infrastruktur mentah menjadi wawasan yang dapat ditindaklanjuti, mendukung pengambilan keputusan, dan mengotomatisasi manajemen prediktif[cite: 91].

## [cite_start]Komponen: Analytics & AI Engine [cite: 92]

| Aspek | Deskripsi |
| :--- | :--- |
| **Tujuan** | [cite_start]Menganalisis data kinerja dan status dari Lapisan DI&I dan CMDB untuk menghasilkan wawasan, prediksi, dan anomali guna mendukung manajemen kapasitas, efisiensi energi, dan pemeliharaan prediktif. [cite: 93] |
| **Sumber Data** | [cite_start]Data Ingestion & Integration Layer (data time-series dan real-time), Configuration Management Database (data CI dan hubungan). [cite: 93] |
| **Penerima Data** | [cite_start]Workflow Automation, Modul Visualisasi & Pelaporan, Tim Operasi. [cite: 93] |

## [cite_start]Baseline Fungsional [cite: 94]
[cite_start]Baseline fungsional menjelaskan kemampuan yang harus dimiliki oleh Analytics & AI Engine untuk memenuhi persyaratan proyek[cite: 95].

### [cite_start]1. Analisis dan Pemrosesan Data [cite: 96]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pemrosesan Data Historis dan Real-time. | [cite_start]Mampu memproses volume data historis yang besar dari sistem pemantauan untuk tren jangka panjang dan mampu menganalisis data real-time untuk deteksi anomali segera. [cite: 97] |
| Analisis Tren dan Kapasitas. | [cite_start]Mampu memproyeksikan penggunaan sumber daya (misalnya, daya, ruang rak, pendingin) di masa depan berdasarkan tren historis dan laju pertumbuhan, menyediakan peringatan untuk potensi masalah kapasitas. [cite: 97] |
| Perhitungan Metrik Utama. | [cite_start]Mampu menghitung metrik DCIM standar dan kustom, seperti PUE (Power Usage Effectiveness), DCiE (Data Center Infrastructure Efficiency), dan utilisasi rak/server. [cite: 97] |

### [cite_start]2. Kemampuan Kecerdasan Buatan (AI) [cite: 98]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Deteksi Anomali. | [cite_start]Harus mampu secara otomatis mengidentifikasi pola data yang menyimpang dari perilaku normal (misalnya, peningkatan suhu yang tidak terduga, fluktuasi daya) dalam waktu 5 menit setelah kejadian. [cite: 99] |
| Pemeliharaan Prediktif (Predictive Maintenance). | [cite_start]Harus dapat menggunakan model Machine Learning untuk memprediksi kegagalan komponen infrastruktur (misalnya, UPS, CRAC) berdasarkan data kesehatan sensor dan log. [cite: 99] |
| Analisis Akar Masalah (Root Cause Analysis/RCA). | [cite_start]Mampu mengkorelasikan kejadian dan metrik kinerja dari berbagai CI yang terhubung (melalui CMDB) untuk mengidentifikasi akar masalah suatu insiden. [cite: 99] |

### [cite_start]3. Integrasi dan Output [cite: 100]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Integrasi dengan Workflow Automation. | [cite_start]Mampu memicu alur kerja otomatis di komponen Workflow Automation berdasarkan temuan analitik (misalnya, secara otomatis membuat tiket pemeliharaan, menyesuaikan setpoint pendingin). [cite: 101] |
| Output Data untuk Visualisasi. | [cite_start]Harus menyediakan API yang aman dan efisien untuk menyalurkan hasil analisis (misalnya, tren, prediksi, anomali) ke Modul Visualisasi & Pelaporan. [cite: 101] |
| Penjelasan Model (Explainability). | [cite_start]Hasil prediksi atau deteksi anomali yang dibuat oleh model AI harus disertai dengan penjelasan yang ringkas dan dapat dipahami oleh pengguna (misalnya, faktor apa yang menyebabkan anomali). [cite: 101] |

## [cite_start]Baseline Non-Fungsional [cite: 102]
[cite_start]Baseline non-fungsional menjelaskan kriteria kinerja, keandalan, dan keamanan Analytics & AI Engine[cite: 103].

### [cite_start]1. Kinerja dan Skalabilitas [cite: 104]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Waktu Intelejen (Time-to-Intelligence). | [cite_start]Waktu pemrosesan dari data real-time yang masuk hingga temuan analitik/anomali yang dapat digunakan tidak boleh melebihi 10 detik. [cite: 105] |
| Throughput Pemrosesan. | [cite_start]Mampu memproses peristiwa per detik untuk analisis real-time. [cite: 105] |
| Skalabilitas. | [cite_start]Harus mampu ditingkatkan secara horizontal untuk mendukung peningkatan volume data sebesar 40% per tahun. [cite: 105] |

### [cite_start]2. Keandalan dan Ketersediaan [cite: 106]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Ketersediaan. | [cite_start]Analytics & AI Engine harus memiliki ketersediaan 99.9%. [cite: 107] |
| Ketahanan Model. | [cite_start]Model AI harus teruji untuk keandalan dan harus secara otomatis dilatih ulang (re-train) secara terjadwal untuk menjaga akurasi. [cite: 107] |
| Pemulihan Bencana. | [cite_start]Harus mendukung replikasi data dan model ke lokasi Place dan mampu memulihkan layanan dalam RTO (Recovery Time Objective) 8 jam. [cite: 107] |

### [cite_start]3. Keamanan [cite: 108]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Kontrol Akses. | [cite_start]Harus menerapkan kontrol akses berbasis peran (RBAC) untuk membatasi siapa yang dapat melihat dan memanipulasi model, serta hasil analisis. [cite: 109] |
| Enkripsi Data. | [cite_start]Data sensitif yang digunakan untuk pelatihan model AI harus dienkripsi saat disimpan (Encryption at Rest). [cite: 109] |
| Audit Model. | [cite_start]Semua perubahan pada model (versi, parameter pelatihan, hasil) harus dicatat untuk keperluan audit. [cite: 109] |

### [cite_start]4. Kemudahan Pengelolaan (Manageability) [cite: 110]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pemantauan. | [cite_start]Harus menyediakan metrik kesehatan platform, penggunaan sumber daya (CPU/memori), dan status model AI (akurasi, latensi) ke alat pemantauan eksternal. [cite: 111] |
| Dokumentasi. | [cite_start]Metodologi analitik, daftar metrik yang dihitung, dan detail arsitektur model AI harus didokumentasikan dalam File. [cite: 111] |

---
[cite_start]Dokumen ini akan ditinjau dalam rapat Peninjauan Baseline yang akan diselenggarakan pada Calendar event, Date[cite: 112].

[cite_start]Dibuat oleh: Person [cite: 113]