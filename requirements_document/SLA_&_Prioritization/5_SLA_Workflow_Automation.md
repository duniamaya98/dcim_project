# [cite_start]Kerangka Prioritas dan Perjanjian Tingkat Layanan (SLA) untuk Komponen Workflow Automation [cite: 386]

[cite_start]**Proyek:** Data Center Infrastructure Management (DCIM) [cite: 387]
[cite_start]**Nama Dokumen:** IF-SLA_&_Prioritization-FIT041-20260126-WorkflowAutomation [cite: 388]
[cite_start]**Versi:** 1.0 [cite: 389]
[cite_start]**Tanggal Revisi:** Date [cite: 390]

## [cite_start]1. Pendahuluan [cite: 391]
[cite_start]Dokumen ini menetapkan SLA untuk Komponen Workflow Automation, yang bertugas mengotomatisasi proses ITIL dan operasional DCIM (Incident, Change, Request)[cite: 392, 393].

### 1.1. [cite_start]Tujuan [cite: 394]
* [cite_start]Menetapkan SLO untuk ketersediaan mesin, kecepatan eksekusi, dan keandalan[cite: 395].
* [cite_start]Memprioritaskan Alur Kerja (Workflow) berdasarkan Dampak Bisnis[cite: 396].
* [cite_start]SLA berfokus pada Pengurangan Human Error dan Peningkatan Kecepatan (MTTE)[cite: 398].

## [cite_start]2. Definisi Layanan (SLA) [cite: 408]

### 2.1. [cite_start]Ketersediaan Mesin dan Keandalan [cite: 410]
| Parameter | Target SLA | Justifikasi |
| :--- | :--- | :--- |
| Ketersediaan Workflow Engine | 99.95% (Per Bulan) | [cite_start]Memastikan Alur Kerja P1 dapat dieksekusi saat insiden[cite: 411]. |
| Tingkat Keberhasilan Eksekusi | ≥ 99.0% | [cite_start]Persentase alur kerja berhasil tanpa kegagalan[cite: 411]. |
| Pemulihan Kegagalan | Maksimal 10 Menit | [cite_start]Waktu beralih ke node cadangan[cite: 411]. |

### 2.2. [cite_start]Kinerja dan Latensi [cite: 412]
| Parameter | Target SLA | Definisi |
| :--- | :--- | :--- |
| Latensi Step-to-Step | < 30 Detik | [cite_start]Waktu antara penyelesaian satu langkah ke langkah berikutnya (P1 & P2)[cite: 414]. |
| MTTE P1 (Critical Incident)| Maksimal 5 Menit | [cite_start]Waktu rata-rata menyelesaikan alur kerja kritis[cite: 414]. |
| Latensi Integrasi | < 60 Detik | [cite_start]Waktu komunikasi dengan API eksternal (Ticketing/CMDB)[cite: 414]. |

## [cite_start]3. Model Prioritas Alur Kerja [cite: 417]

### 3.1. [cite_start]Matriks Prioritas Alur Kerja (P1-P4) [cite: 423]
| Prioritas | Jenis Proses | Dampak Operasi | Target Kinerja Utama |
| :--- | :--- | :--- | :--- |
| P1: Kritis | Incident Response & Safety | Menghentikan Outage / Kerusakan Fisik | MTTE Maks. [cite_start]5 Menit [cite: 424] |
| P2: Tinggi | Standard Change & Non-Critical Incident| Degradasi Layanan | [cite_start]Success Rate ≥ 99.5% [cite: 424] |
| P3: Menengah| Access Request & Provisioning | Keterlambatan Layanan Pengguna | [cite_start]Latensi < 60 Detik [cite: 424] |
| P4: Pendukung| Reporting, Audit Trail | Dampak Minor | [cite_start]Audit Trail 100% [cite: 424] |

### 3.2. [cite_start]Proses Eskalasi Kegagalan [cite: 425]
| Tingkat | Jalur Eskalasi (Jika Gagal Diatasi Operasi) | Kontak Eskalasi |
| :--- | :--- | :--- |
| P1 (Kritis)| Operasi -> Automation Developer -> Process Owner | [cite_start]Person (Process Owner P1) [cite: 427] |
| P2 (Tinggi)| Operasi -> Automation Developer | [cite_start]Person (Lead Automation Developer) [cite: 427] |

## [cite_start]4. Peran dan Tanggung Jawab [cite: 428]
* [cite_start]**Process Owners:** Otoritas tertinggi persetujuan alur kerja[cite: 429].
* [cite_start]**Automation Developers:** Pengembangan dan troubleshooting mesin[cite: 429].
* [cite_start]**Operations Team:** Memantau harian dan melakukan manual override jika P1 gagal[cite: 429].

## [cite_start]5. Metrik dan Pelaporan [cite: 430]
| KPI | Definisi | Target Kepatuhan |
| :--- | :--- | :--- |
| Process Cycle Time Reduction | Pengurangan MTTE dibanding eksekusi manual | [cite_start]≥ 50% [cite: 433] |
| Manual Touchpoint Reduction | Langkah manual yang dihilangkan | [cite_start]≥ 80% [cite: 433] |
| Workflow Execution Success | Tingkat keberhasilan alur kerja | [cite_start]≥ 99.0% [cite: 433] |

## [cite_start]6. Tinjauan dan Revisi [cite: 436]
[cite_start]Tinjauan Formal dilakukan **Tahunan** (optimasi menyeluruh), dan Tinjauan Ad-Hoc segera setelah kegagalan SLA Kritis[cite: 439, 440].