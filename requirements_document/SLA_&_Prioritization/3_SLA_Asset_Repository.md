# [cite_start]Kerangka Prioritas dan Perjanjian Tingkat Layanan (SLA) untuk Komponen Asset Repository [cite: 281]

[cite_start]**Proyek:** Data Center Infrastructure Management (DCIM) [cite: 282]
[cite_start]**Nama Dokumen:** IF-SLA_&_Prioritization-FIT041-20260126-AssetRepository [cite: 283]
[cite_start]**Versi:** 1.0 [cite: 284]
[cite_start]**Tanggal Revisi:** Date [cite: 285]

## [cite_start]1. Pendahuluan [cite: 286]
[cite_start]Dokumen ini menetapkan Perjanjian Tingkat Layanan (SLA) dan Kerangka Prioritas Operasional untuk Komponen Asset Repository, sebagai sumber kebenaran tunggal (SSOT) data aset infrastruktur[cite: 287, 288].

### 1.1. [cite_start]Tujuan [cite: 289]
* [cite_start]Menetapkan Target Tingkat Layanan untuk akurasi inventaris fisik, integritas finansial, dan pembaruan[cite: 290].
* [cite_start]Memprioritaskan aset berdasarkan fase siklus hidup dan dampak operasional/finansial[cite: 291].
* [cite_start]Menentukan peran untuk pemeliharaan data dan audit fisik[cite: 292].

### 1.2. [cite_start]Ruang Lingkup [cite: 294]
[cite_start]Berlaku untuk seluruh manajemen data siklus hidup aset fisik (hardware IT, fasilitas) dan Data Pendukung (Garansi, Finansial, Kepemilikan)[cite: 295, 296, 297].

## [cite_start]2. Definisi Layanan (SLA) untuk Asset Repository [cite: 300]

### 2.1. [cite_start]Akurasi Inventaris dan Kepatuhan [cite: 302]
| Parameter | Target SLA | Justifikasi |
| :--- | :--- | :--- |
| Akurasi Inventaris | ≥ 98.0% (Per Triwulan) | [cite_start]Meminimalisir Audit Variance dan Ghost Assets[cite: 304]. |
| Frekuensi Rekonsiliasi | Triwulanan (Quarterly)| [cite_start]Audit fisik wajib empat kali setahun untuk aset P1[cite: 304]. |
| Keandalan Barcode/RFID | ≥ 99.5% Read Success | [cite_start]Mengurangi human error pada proses check-in/out[cite: 304]. |
| Kepatuhan Garansi | 100% Data Terisi | [cite_start]Aset P1/P2 Active harus memiliki data tanggal/garansi valid[cite: 304]. |

### 2.2. [cite_start]Kinerja dan Latensi Pembaruan [cite: 305]
| Parameter | Target SLA | Definisi |
| :--- | :--- | :--- |
| Update Latency (P1) | Maksimal 4 Jam Kerja | [cite_start]Waktu antara perubahan fisik aset hingga data diperbarui[cite: 307]. |
| Data Integrity Check | Harian | [cite_start]Sistem memeriksa integritas data otomatis untuk aset P1[cite: 307]. |
| Waktu Respon Laporan | Maksimal 1 Menit | [cite_start]Waktu penyajian laporan status real-time aset[cite: 307]. |

### 2.3. [cite_start]Waktu Respons dan Resolusi Dukungan [cite: 308]
| Tingkat Keparahan | Klasifikasi Insiden | Waktu Respons | Waktu Resolusi (MTTR) |
| :--- | :--- | :--- | :--- |
| Kritis (Severity 1) | Kegagalan Total Asset Repository; Inventory Accuracy > 5% selisih. | 15 Menit | [cite_start]2 Jam [cite: 310] |
| Tinggi (Severity 2) | Kegagalan sinkronisasi data dengan sistem Procurement/Finance. | 30 Menit | [cite_start]4 Jam [cite: 310] |
| Menengah (Severity 3)| Kesalahan data minor (salah Purchase Date). | 1 Jam | [cite_start]1 Hari Kerja [cite: 310] |
| Rendah (Severity 4) | Permintaan laporan ad-hoc. | 2 Jam | [cite_start]3 Hari Kerja [cite: 310] |

## [cite_start]3. Model Prioritas Aset dan Atribut Data [cite: 311]

### 3.1. [cite_start]Matriks Prioritas Aset (P1-P4) [cite: 313]
| Prioritas | Fase & Status | Dampak Finansial/Operasional | Contoh |
| :--- | :--- | :--- | :--- |
| P1: Kritis | Aset aktif di Production Rack. | Memicu Outage. Akurasi 100% wajib. | [cite_start]Server Database, Switch, PDU. [cite: 315] |
| P2: Tinggi | Aset garansi/kontrak & Cadangan. | Degradasi layanan; Cost avoidance. | [cite_start]Server Non-Kritis, Cold Spares. [cite: 315] |
| P3: Menengah| Aset Decommissioned / Arsip. | Pelaporan End-of-Life & depresiasi. | [cite_start]Aset di Storage Room. [cite: 315] |
| P4: Pendukung| Aset Retired (dijual/dibuang). | Audit historis & lingkungan. | [cite_start]Data aset historis. [cite: 315] |

### 3.2. [cite_start]Prioritas Atribut Data [cite: 316]
* [cite_start]**P1:** Serial Number, Lokasi Fisik, Status Operasional[cite: 318].
* [cite_start]**P2:** Owner, Garansi End Date, Purchase Date[cite: 318].

## [cite_start]4. Peran dan Tanggung Jawab [cite: 319]
* [cite_start]**Asset Manager (DCIM):** Pemilik SLA, memimpin audit[cite: 320].
* [cite_start]**Data Center Technicians:** Pelaksana check-in/out fisik[cite: 320].
* [cite_start]**Tim Procurement:** Memasukkan data Purchase Date/Warranty[cite: 320].
* [cite_start]**Tim Finance/Accounting:** Memberikan input Depreciation Value[cite: 320].

## [cite_start]5. Metrik dan Pelaporan [cite: 321]
| KPI | Definisi | Target Kepatuhan |
| :--- | :--- | :--- |
| Financial Accuracy Variance | Selisih nilai aset vs buku besar Finance | [cite_start]< 1.0% [cite: 324] |
| Audit Variance Rate | Persentase aset missing / ghost assets | [cite_start]< 2.0% [cite: 324] |
| Update Latency Kepatuhan | Persentase pembaruan P1/P2 dalam 4 jam kerja | [cite_start]≥ 95.0% [cite: 324] |

## [cite_start]6. Tinjauan dan Revisi [cite: 327]
[cite_start]Tinjauan formal dilakukan secara **Tahunan** selaras dengan audit finansial[cite: 329]. [cite_start]Revisi disetujui oleh **Project Owner (DCIM)** dan **Tim Finance**[cite: 330].