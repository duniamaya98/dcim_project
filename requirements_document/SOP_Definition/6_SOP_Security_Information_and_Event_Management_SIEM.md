# Prosedur Operasi Standar (SOP) - Security Information & Event Management (SIEM)

## 1. Tujuan, Latar Belakang, dan Ruang Lingkup

### 1.1 Tujuan
* Menetapkan SIEM sebagai pusat intelijen keamanan terpadu (Single Pane of Glass) DCIM.
* Menguraikan arsitektur untuk pengumpulan, normalisasi, dan korelasi log IT dan Fasilitas.
* Menetapkan standar use case keamanan (aturan korelasi) dan mekanisme respons insiden.

### 1.2 Latar Belakang
SIEM berfungsi sebagai lapisan pertahanan yang menyediakan visibilitas holistik siber-fisik, memungkinkan deteksi ancaman cepat bagi SOC dan tim DCIM.

### 1.3 Ruang Lingkup
Meliputi spesifikasi arsitektur pengumpulan log, pengelolaan aturan korelasi, integrasi dengan ITSM/Workflow, kebijakan retensi log, dan keamanan data.

## 2. Definisi dan Peran Inti SIEM dalam DCIM

### 2.1 Definisi
Platform yang mengumpulkan dan menganalisis log keamanan (IT/OT) secara real-time untuk korelasi kejadian, manajemen insiden, dan pelaporan kepatuhan.

### 2.2 Peran Kunci
Pusat Intelijen Keamanan, Korelasi Siber-Fisik, Deteksi Anomalitas (UEBA), Manajemen Kepatuhan (Audit log), dan Pemicu Respon Otomatis via Workflow.

## 3. Hubungan dan Integrasi dengan Komponen DCIM Lain
SIEM berintegrasi dengan Data Ingestion Layer (sumber log), CMDB (konteks relasi CI), Analytics & AI Engine (UEBA), Workflow Automation (pemicu eksekusi quarantine), ITSM (tiket insiden), NOC/SOC, dan Threat Intelligence Platform.

## 4. Sumber Data Keamanan dan Klasifikasi Kejadian
Sumber mencakup IT Infrastructure (Server OS), Network Security (Firewall/IPS), Physical Security (Access Control, CCTV), Facility/OT (BMS/PDU), Cloud/API, dan Endpoint Security (Antivirus).

## 5. Arsitektur SIEM

### 5.1 Komponen Kunci
Log Collector (Syslog, Fluentd), Message Broker (Kafka), Parser & Normalizer (Logstash), Correlation Engine (Rule-based), UEBA (ML Engine), Storage & Retention Layer (Elasticsearch).

## 6. Proses Ingesti, Normalisasi, dan Korelasi

### 6.1 Ingesti Kejadian
Akuisisi (Push/Pull agen), Buffering (Message Broker), Throttling (membatasi rate).

### 6.2 Parsing dan Normalisasi
Parsing raw log, normalisasi field ke skema standar, Enrichment (Geo-IP, Threat Intelligence, CMDB Context).

### 6.3 Korelasi Kejadian
Menggunakan Rule-Based Correlation (logika kondisional), Time-Based Correlation (sliding window), Statistical Correlation (penyimpangan baseline), dan Grouping (mengurangi alert fatigue).

## 7. Use Cases Kunci SIEM (Konteks DCIM)
Mendeteksi Intrusi Siber-Fisik, Penyalahgunaan Akses Istimewa, Ancaman Fisik Internal, Data Exfiltration, dan Configuration Drift Security (konfigurasi tanpa tiket ITSM).

## 8. Integrasi Analytics & AI dan Rule Management
* **Integrasi AI:** Menggunakan modul UEBA untuk deteksi anomali perilaku dan threat prioritization.
* **Rule Management:** Dokumentasi aturan (MITRE ATT&CK) di File, tuning berkala, dan deployment melalui Change Management.

## 9. Alerting, Eskalasi, dan Respons Insiden
* **Alerting:** Prioritas (Low, Medium, High, Critical) berdasarkan kekritisan CI dari CMDB.
* **Eskalasi:** Alert Critical (<5 menit respons) dikirim otomatis ke Workflow Automation dan membuat tiket ITSM; High (<15 menit) ke Data Owner; Medium/Low diinvestigasi manual.
* **Integrasi ITSM:** SIEM membuat tiket dan memicu tindakan respons otomatis via Workflow.

## 10. Log Retention, Penyimpanan, dan Kepatuhan
* **Retensi Log:** Security Log (90 hari online / 5 Tahun Arsip), Facility Log (30 hari / 1 Tahun), Audit Trail (180 hari / 5 Tahun).
* **Keamanan Data:** Log dienkripsi (TLS & Disk), masking informasi sensitif, akses dibatasi (Need-to-Know).
* **Kepatuhan:** Bukti log untuk standar ISO 27001/PCI DSS.

## 11. Pemantauan Kinerja SIEM dan KPI
KPI: EPS Processed (99%), Parsing Success (>99.9%), False Positive Rate (<5%), MTTD (<15 Menit), MTTR (<60 Menit), Log Source Availability (>99.5%).

## 12. Peran, Tanggung Jawab, dan RACI
(Rincian matriks RACI tersedia pada dokumen asli untuk Security Officer, SOC Analyst, Security Engineer, dsb).