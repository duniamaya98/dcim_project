# [cite_start]Definisi Baseline (Fungsional dan Non-Fungsional) - Workflow Automation [cite: 115]

[cite_start]Dokumen ini mendefinisikan baseline fungsional dan non-fungsional untuk komponen Workflow Automation dalam proyek Data Center Infrastructure Management (DCIM)[cite: 116].

## [cite_start]Persyaratan Proyek DCIM [cite: 117]
[cite_start]Proyek DCIM bertujuan untuk menyediakan visibilitas dan kontrol yang komprehensif atas infrastruktur pusat data[cite: 118]. [cite_start]Komponen Workflow Automation sangat penting untuk mengubah wawasan dan peringatan dari komponen lain (DI&I, CMDB, Analytics) menjadi tindakan otomatis yang konsisten dan cepat, seperti respons insiden, manajemen perubahan, dan tindakan remediasi[cite: 119].

## [cite_start]Komponen: Workflow Automation [cite: 120]

| Aspek | Deskripsi |
| :--- | :--- |
| **Tujuan** | [cite_start]Mengotomatisasi alur kerja operasional yang berulang, berbasis aturan, dan kompleks (misalnya, respons insiden, manajemen perubahan, tindakan remediasi, provisi) untuk mengurangi intervensi manual dan mempercepat waktu respons. [cite: 121] |
| **Sumber Pemicu** | [cite_start]Security Information & Event Management (SIEM), Analytics & AI Engine (hasil anomali/prediksi), Data Ingestion & Integration Layer (alarm), Manajer. [cite: 121] |
| **Penerima Data** | [cite_start]Perangkat Infrastruktur Pusat Data (misalnya, Server, CRAC, UPS), Configuration Management Database (CMDB), Modul Visualisasi & Pelaporan. [cite: 121] |

## [cite_start]Baseline Fungsional [cite: 122]
[cite_start]Baseline fungsional menjelaskan kemampuan yang harus dimiliki oleh Workflow Automation untuk memenuhi persyaratan proyek[cite: 123].

### [cite_start]1. Desain dan Pengelolaan Alur Kerja [cite: 124]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Mesin Alur Kerja Berbasis Aturan. | [cite_start]Harus memiliki mesin yang kuat untuk mengeksekusi alur kerja berdasarkan aturan bersyarat (misalnya, IF [Peristiwa] AND [Kondisi CMDB] THEN [Tindakan Otomatis]). [cite: 125] |
| Antarmuka Desain Grafis (Low-Code). | [cite_start]Menyediakan antarmuka visual/grafis (drag-and-drop) untuk mendesain, menguji, dan memelihara alur kerja tanpa memerlukan pengkodean yang ekstensif, untuk digunakan oleh Person. [cite: 125] |
| Pengelolaan Versi dan Audit Alur Kerja. | [cite_start]Mampu menyimpan riwayat versi alur kerja yang diaudit dan menyediakan mekanisme persetujuan sebelum alur kerja baru diaktifkan. [cite: 125] |

### [cite_start]2. Integrasi dan Aksi [cite: 126]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Integrasi Dua Arah. | [cite_start]Mampu menerima pemicu (trigger) dari sistem eksternal (misalnya, SIEM, Analytics Engine) dan mampu mengirim perintah (aksi) ke perangkat infrastruktur atau sistem manajemen (misalnya, membuat tiket di sistem Ticketing, me-reboot server). [cite: 127] |
| Konektor Infrastruktur. | [cite_start]Menyediakan konektor yang siap pakai (out-of-the-box) atau mudah dikonfigurasi untuk berinteraksi dengan berbagai perangkat DCIM (misalnya, SNMP, REST API, SSH/Telnet) dan sistem lain (misalnya, CMDB, SIEM). [cite: 127] |
| Dukungan Logika Kompleks. | [cite_start]Mampu menjalankan logika kompleks yang melibatkan urutan tindakan, jeda waktu, perulangan, dan intervensi manusia (misalnya, mengirim permintaan persetujuan kepada Person). [cite: 127] |

### [cite_start]3. Eksekusi dan Pelaporan [cite: 128]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pemrosesan Real-time. | [cite_start]Harus mampu memproses pemicu kritis (misalnya, alarm kebakaran, kegagalan daya) dan memulai alur kerja yang relevan dalam waktu 1 detik setelah menerima pemicu. [cite: 129] |
| Pemantauan Eksekusi. | [cite_start]Menyediakan dasbor untuk memantau status eksekusi alur kerja yang sedang berjalan, riwayat eksekusi, dan metrik kinerja (misalnya, waktu rata-rata eksekusi). [cite: 129] |
| Pemberitahuan dan Pelaporan. | [cite_start]Mampu mengirimkan pemberitahuan status alur kerja (berhasil/gagal) melalui berbagai saluran (misalnya, Email, SMS, Slack) dan menghasilkan laporan audit eksekusi. [cite: 129] |

## [cite_start]Baseline Non-Fungsional [cite: 130]
[cite_start]Baseline non-fungsional menjelaskan kriteria kinerja, keandalan, dan keamanan komponen Workflow Automation[cite: 131].

### [cite_start]1. Kinerja dan Skalabilitas [cite: 132]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Latensi Eksekusi. | [cite_start]Latensi rata-rata dari pemicu hingga dimulainya tindakan pertama tidak boleh melebihi 2 detik. [cite: 133] |
| Throughput. | [cite_start]Mampu memproses Person alur kerja serentak per menit pada jam sibuk. [cite: 133] |
| Skalabilitas. | [cite_start]Harus mampu ditingkatkan secara horizontal untuk mendukung peningkatan jumlah alur kerja dan perangkat yang dikelola sebesar 35% per tahun. [cite: 133] |

### [cite_start]2. Keandalan dan Ketersediaan [cite: 134]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Ketersediaan. | [cite_start]Mesin Workflow Automation harus memiliki ketersediaan 99.99%. [cite: 135] |
| Ketahanan Eksekusi. | [cite_start]Harus memiliki mekanisme untuk melanjutkan eksekusi alur kerja (workflow persistence) setelah kegagalan node dan menyediakan mekanisme rollback untuk tindakan yang gagal. [cite: 135] |
| Pemulihan Bencana. | [cite_start]Harus mendukung replikasi data alur kerja ke lokasi Place dan mampu memulihkan layanan dalam RTO (Recovery Time Objective) 2 jam. [cite: 135] |

### [cite_start]3. Keamanan [cite: 136]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Kontrol Akses. | [cite_start]Harus menerapkan kontrol akses berbasis peran (RBAC) untuk menentukan pengguna atau sistem mana yang diizinkan untuk membuat, memodifikasi, dan memicu alur kerja tertentu. [cite: 137] |
| Manajemen Kredensial Aman. | [cite_start]Semua kredensial yang digunakan oleh alur kerja untuk berinteraksi dengan perangkat atau sistem eksternal harus dienkripsi saat disimpan (Encryption at Rest) dan dikelola dalam brankas kredensial yang aman. [cite: 137] |
| Audit Trail Eksekusi. | [cite_start]Setiap langkah dan tindakan dalam eksekusi alur kerja harus dicatat dalam audit trail yang tidak dapat diubah (immutable log) dan disimpan selama minimal 3 tahun. [cite: 137] |

### [cite_start]4. Kemudahan Pengelolaan (Manageability) [cite: 138]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pemantauan. | [cite_start]Harus menyediakan metrik kinerja dan kesehatan mesin alur kerja ke alat pemantauan eksternal untuk melacak latensi, tingkat kegagalan, dan utilisasi. [cite: 139] |
| Dokumentasi. | [cite_start]Semua alur kerja yang disetujui, definisi logika, dan prosedur pemulihan harus didokumentasikan dalam File. [cite: 139] |

---
[cite_start]Dokumen ini akan ditinjau dalam rapat Peninjauan Baseline yang akan diselenggarakan pada Calendar event, Date[cite: 140].

[cite_start]Dibuat oleh: Person [cite: 141]