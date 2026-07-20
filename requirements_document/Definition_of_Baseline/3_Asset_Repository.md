# [cite_start]Definisi Baseline (Fungsional dan Non-Fungsional) - Asset Repository [cite: 59]

[cite_start]Dokumen ini mendefinisikan baseline fungsional dan non-fungsional untuk komponen Asset Repository dalam proyek Data Center Infrastructure Management (DCIM)[cite: 60].

## [cite_start]Persyaratan Proyek DCIM [cite: 61]
[cite_start]Proyek DCIM bertujuan untuk menyediakan visibilitas dan kontrol yang komprehensif atas infrastruktur pusat data[cite: 62]. [cite_start]Asset Repository berfungsi sebagai sistem pencatatan resmi (System of Record) untuk data aset fisik dan logis, memberikan fondasi data master yang akurat untuk CMDB dan komponen hilir lainnya[cite: 63].

## [cite_start]Komponen: Asset Repository [cite: 64]

| Aspek | Deskripsi |
| :--- | :--- |
| **Tujuan** | [cite_start]Berfungsi sebagai sumber kebenaran tunggal (Single Source of Truth) untuk data aset permanen (misalnya, nomor seri, tanggal pembelian, garansi, lokasi awal) dan menyediakan data master untuk CMDB. [cite: 65] |
| **Sumber Data** | [cite_start]Sistem Pembelian (Purchasing System), Pemasok (Vendor) Data, Informasi Inventaris Manual. [cite: 65] |
| **Penerima Data** | [cite_start]Configuration Management Database (CMDB), Modul Pengadaan, Modul Lisensi, Modul Pelaporan. [cite: 65] |

## [cite_start]Baseline Fungsional [cite: 66]
[cite_start]Baseline fungsional menjelaskan kemampuan yang harus dimiliki oleh Asset Repository untuk memenuhi persyaratan proyek[cite: 67].

### [cite_start]1. Pengelolaan Data Master Aset [cite: 68]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pengelolaan Siklus Hidup Aset. | Mampu melacak status aset dari pengadaan, instalasi, operasional, hingga dekomisioning. [cite_start]Harus mendukung status seperti Ordered, Staging, Deployed, Retired. [cite: 69] |
| Atribut Data Master. | [cite_start]Mampu menyimpan data master aset yang kritikal dan statis (misalnya, Produsen, Model, Nomor Seri, Informasi Garansi, Tanggal Pembelian, Nilai Awal) dan menyediakan validasi data master. [cite: 69] |
| Pengelolaan Lokasi Fisik. | [cite_start]Mampu mencatat lokasi fisik permanen atau lokasi stok (gudang) dari setiap aset. [cite: 69] |

### [cite_start]2. Integrasi Data dan Sinkronisasi [cite: 70]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Integrasi Data Pembelian. | [cite_start]Mampu mengimpor atau menerima data aset baru secara otomatis dari sistem pengadaan atau inventaris pihak ketiga. [cite: 71] |
| Integrasi dengan CMDB. | [cite_start]Menyediakan mekanisme ekspor data yang terjadwal dan berbasis perubahan untuk menyinkronkan data master aset ke CMDB. [cite: 71] |
| Pembaruan Massal dan Manual. | [cite_start]Harus menyediakan antarmuka yang efisien untuk pembaruan data massal (misalnya, melalui upload CSV) dan antarmuka web yang aman untuk pembaruan manual oleh pengguna yang berwenang. [cite: 71] |

### [cite_start]3. Query dan Pelaporan [cite: 72]

| Persyaratan Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pencarian dan Filter. | [cite_start]Harus menyediakan kemampuan pencarian dan penyaringan data aset berdasarkan berbagai kriteria (misalnya, model, vendor, tanggal garansi berakhir, status). [cite: 73] |
| Pelaporan Inventaris. | [cite_start]Mampu menghasilkan laporan inventaris yang telah ditentukan (misalnya, daftar aset berdasarkan lokasi, ringkasan garansi yang akan berakhir) dan laporan kustom. [cite: 73] |
| API Akses Data. | [cite_start]Harus mengekspos API yang aman untuk memungkinkan sistem lain (misalnya, modul Lisensi) mengambil data aset master. [cite: 73] |

## [cite_start]Baseline Non-Fungsional [cite: 74]
[cite_start]Baseline non-fungsional menjelaskan kriteria kinerja, keandalan, dan keamanan Asset Repository[cite: 75].

### [cite_start]1. Kinerja dan Skalabilitas [cite: 76]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Waktu Respons Query. | [cite_start]Waktu respons untuk query data master aset tunggal tidak boleh melebihi 1 detik. [cite: 77] |
| Throughput Impor Data. | [cite_start]Harus mampu memproses impor data master dari sistem pengadaan sebesar Person catatan per menit. [cite: 77] |
| Skalabilitas. | [cite_start]Harus mampu ditingkatkan untuk mengakomodasi peningkatan jumlah aset sebesar 30% per tahun selama 5 tahun ke depan. [cite: 77] |

### [cite_start]2. Keandalan dan Ketersediaan [cite: 78]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Ketersediaan. | [cite_start]Asset Repository harus memiliki ketersediaan 99.9%. [cite: 79] |
| Integritas Data Master. | [cite_start]Harus menerapkan aturan validasi untuk memastikan integritas data (misalnya, keunikan Nomor Seri, format tanggal yang benar) saat data dimasukkan atau diperbarui. [cite: 79] |
| Pemulihan Bencana. | [cite_start]Harus mendukung replikasi data ke lokasi Place dan mampu memulihkan layanan dalam RTO (Recovery Time Objective) 6 jam. [cite: 79] |

### [cite_start]3. Keamanan [cite: 80]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Kontrol Akses. | [cite_start]Harus menerapkan kontrol akses berbasis peran (Role-Based Access Control/RBAC) untuk membatasi akses melihat dan memodifikasi data master aset hanya kepada pengguna yang berwenang. [cite: 81] |
| Enkripsi Data. | [cite_start]Data master aset sensitif (misalnya, informasi keuangan, lokasi strategis) harus dienkripsi saat disimpan (Encryption at Rest). [cite: 81] |
| Audit Trail. | [cite_start]Semua penambahan, penghapusan, atau modifikasi pada data master aset harus dicatat dalam audit trail yang tidak dapat diubah (immutable log) dan disimpan selama minimal 5 tahun. [cite: 81] |

### [cite_start]4. Kemudahan Pengelolaan (Manageability) [cite: 82]

| Persyaratan Non-Fungsional | Detail Elaborasi untuk Proyek DCIM |
| :--- | :--- |
| Pemantauan. | [cite_start]Harus menyediakan metrik status sistem (misalnya, ruang disk, kesehatan basis data) ke alat pemantauan eksternal. [cite: 83] |
| Dokumentasi. | [cite_start]Semua struktur data, kamus data, dan prosedur pembaruan data harus didokumentasikan dalam File. [cite: 83] |

---
[cite_start]Dokumen ini akan ditinjau dalam rapat Peninjauan Baseline yang akan diselenggarakan pada Calendar event, Date[cite: 84].

[cite_start]Dibuat oleh: Person [cite: 85]