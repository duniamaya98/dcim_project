# [cite_start]Definisi Baseline (Fungsional dan Non-Fungsional) - Security Information & Event Management (SIEM) [cite: 143]

[cite_start]Dokumen ini mendefinisikan baseline fungsional dan non-fungsional untuk komponen Security Information & Event Management (SIEM) dalam proyek Data Center Infrastructure Management (DCIM)[cite: 144].

## [cite_start]Persyaratan Proyek DCIM [cite: 145]
[cite_start]Proyek DCIM bertujuan untuk menyediakan visibilitas dan kontrol yang komprehensif atas infrastruktur pusat data[cite: 146]. [cite_start]Komponen SIEM sangat penting untuk mengonsolidasikan data keamanan dan peristiwa operasional dari seluruh infrastruktur DCIM guna mendeteksi ancaman, anomali, dan memastikan kepatuhan[cite: 147].

## [cite_start]Komponen: Security Information & Event Management (SIEM) [cite: 148]

| Aspek | Deskripsi |
| :--- | :--- |
| **Tujuan** | [cite_start]Mengumpulkan, menganalisis, dan mengelola log keamanan dan peristiwa operasional dari semua komponen DCIM dan infrastruktur pusat data untuk deteksi ancaman dan respons insiden secara real-time. [cite: 149] |
| **Sumber Data** | [cite_start]Data Ingestion & Integration Layer (Alarm, Events), Perangkat Jaringan & Keamanan (Firewall, IDS/IPS), Server & Sistem Operasi, Aplikasi DCIM. [cite: 149] |
| **Penerima Data** | [cite_start]Workflow Automation, Tim Keamanan, Tim Operasi, Modul Pelaporan Kepatuhan. [cite: 149] |

## [cite_start]Baseline Fungsional [cite: 150]
[cite_start]Baseline fungsional menjelaskan kemampuan yang harus dimiliki oleh SIEM untuk memenuhi persyaratan proyek DCIM[cite: 151].

### [cite_start]1. Pengumpulan dan Normalisasi Data [cite: 152]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Dukungan Pengumpulan Log. | [cite_start]Mampu mengumpulkan log dan peristiwa dari semua komponen DCIM (DI&I, CMDB, Analytics) dan infrastruktur (misalnya, Syslog, SNMP, log Windows Event, log aplikasi kustom). [cite: 153] |
| Normalisasi Data. | [cite_start]Harus mampu menstandardisasi format data log dan peristiwa yang berbeda dari berbagai sumber ke dalam skema umum yang konsisten untuk analisis yang seragam. [cite: 153] |
| Pengayaan Data. | [cite_start]Mampu memperkaya data peristiwa dengan konteks yang relevan (misalnya, data aset dari CMDB, data pengguna, geolokasi) untuk meningkatkan akurasi deteksi dan respons. [cite: 153] |

### [cite_start]2. Deteksi Ancaman dan Korelasi Peristiwa [cite: 154]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Korelasi Peristiwa Real-time. | [cite_start]Mampu mengkorelasikan peristiwa dari berbagai sumber secara real-time untuk mengidentifikasi pola serangan atau anomali yang kompleks (misalnya, multiple failed logins diikuti oleh unauthorized configuration change). [cite: 155] |
| Mesin Aturan yang Fleksibel. | [cite_start]Menyediakan mesin aturan yang memungkinkan pembuatan, modifikasi, dan penerapan aturan deteksi kustom untuk ancaman spesifik pusat data (misalnya, unauthorized access attempt ke perangkat daya). [cite: 155] |
| Deteksi Anomali. | [cite_start]Harus menerapkan kemampuan analitik perilaku (misalnya, User and Entity Behavior Analytics/UEBA) untuk mendeteksi penyimpangan dari perilaku dasar operasional dan keamanan yang normal. [cite: 155] |

### [cite_start]3. Manajemen Insiden dan Respons [cite: 156]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Peringatan (Alerting). | [cite_start]Mampu menghasilkan peringatan yang dapat ditindaklanjuti berdasarkan korelasi dan deteksi anomali, dengan tingkat keparahan yang diklasifikasikan (Kritis, Tinggi, Sedang, Rendah). [cite: 157] |
| Integrasi Respons Otomatis. | [cite_start]Harus mampu memicu alur kerja otomatis di komponen Workflow Automation sebagai respons terhadap insiden kritis (misalnya, memicu isolasi jaringan atau mengirim notifikasi ke Person). [cite: 157] |
| Investigasi Log. | [cite_start]Harus menyediakan antarmuka pencarian dan filter log yang cepat dan intuitif untuk mendukung investigasi insiden oleh tim keamanan. [cite: 157] |

## [cite_start]Baseline Non-Fungsional [cite: 158]
[cite_start]Baseline non-fungsional menjelaskan kriteria kinerja, keandalan, dan keamanan SIEM[cite: 159].

### [cite_start]1. Kinerja dan Skalabilitas [cite: 160]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Latensi Pemrosesan. | [cite_start]Latensi dari peristiwa diterima hingga peringatan yang dihasilkan untuk peristiwa kritis tidak boleh melebihi 3 detik. [cite: 161] |
| Throughput Ingesti. | [cite_start]Harus mampu menangani throughput ingesti data log puncak sebesar Person peristiwa per detik. [cite: 161] |
| Skalabilitas. | [cite_start]Harus mampu ditingkatkan secara horizontal untuk mengakomodasi peningkatan volume log sebesar 30% per tahun selama 5 tahun ke depan. [cite: 161] |

### [cite_start]2. Keandalan dan Ketersediaan [cite: 162]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Ketersediaan. | [cite_start]Sistem SIEM harus memiliki ketersediaan 99.9%. [cite: 163] |
| Ketahanan Data. | [cite_start]Harus memiliki mekanisme replikasi dan failover untuk mencegah kehilangan data peristiwa selama ingesti dan penyimpanan. [cite: 163] |
| Pemulihan Bencana. | [cite_start]Harus mendukung replikasi data dan konfigurasi ke lokasi Place dan mampu memulihkan layanan dalam RTO (Recovery Time Objective) 4 jam. [cite: 163] |

### [cite_start]3. Keamanan dan Kepatuhan [cite: 164]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Kontrol Akses. | [cite_start]Harus menerapkan kontrol akses berbasis peran (RBAC) yang ketat untuk mengakses log dan konfigurasi SIEM, hanya mengizinkan personel yang berwenang. [cite: 165] |
| Enkripsi Log. | [cite_start]Semua log yang disimpan (Encryption at Rest) dan yang sedang dikirim (Encryption in Transit) harus dienkripsi. [cite: 165] |
| Retensi Log. | [cite_start]Log mentah dan log yang dinormalisasi harus disimpan selama minimal 1 tahun untuk memenuhi persyaratan audit dan kepatuhan. [cite: 165] |
| Pelaporan Kepatuhan. | [cite_start]Harus mampu menghasilkan laporan kepatuhan yang telah ditentukan (misalnya, laporan akses, laporan perubahan konfigurasi) untuk regulasi standar. [cite: 165] |

### [cite_start]4. Kemudahan Pengelolaan (Manageability) [cite: 166]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pemantauan. | [cite_start]Harus menyediakan metrik kinerja sistem, ingestion rate, dan status kesehatan mesin korelasi ke alat pemantauan eksternal. [cite: 167] |
| Dokumentasi. | [cite_start]Semua aturan korelasi, prosedur respons insiden (Playbook), dan arsitektur SIEM harus didokumentasikan dalam File. [cite: 167] |

---
[cite_start]Dokumen ini akan ditinjau dalam rapat Peninjauan Baseline yang akan diselenggarakan pada Calendar event, Date[cite: 168].

[cite_start]Dibuat oleh: Person [cite: 169]