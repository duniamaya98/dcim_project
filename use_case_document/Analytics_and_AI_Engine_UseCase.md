# Analytics & AI Engine

## Use Case Analysis: Analytics & AI Engine

### Introduction
Dokumen ini menyediakan studi kasus terkait komponen Analytics & AI Engine di dalam Proyek Data Center Infrastructure Management (DCIM). Bagian ini adalah lapisan intelligence dari platform DCIM, bertanggung jawab untuk memproses sejumlah data operasional (metrik, log, konfigurasi) dari Data Ingestion & Integration Layer untuk mendapatkan wawasan yang dapat ditindaklanjuti, memprediksi kegagalan, dan merekomendasikan optimasi untuk kapasitas dan konsumsi energi.

### Analytics & AI Engine Component Overview
Analytics & AI Engine menyediakan kemampuan penting untuk melangkah lebih jauh dari sekedar simple monitoring menuju operasi prediktif dan preskriptif, dengan memanfaatkan model statistik dan pembelajaran mesin untuk memaksimalkan efisiensi dan keandalan.

| Fungsi Utama | Deskripsi |
| :--- | :--- |
| **Predictive Maintenance** | Menggunakan machine learning untuk memprediksi kegagalan sebelum terjadi. |
| **Anomaly Detection** | Mengidentifikasi pola yang tidak biasa dalam kinerja, suhu, atau konsumsi daya yang menandakan potensi masalah. |
| **Capacity Optimization** | Merekomendasikan penempatan beban kerja dan konsolidasi perangkat keras berdasarkan data pemanfaatan. |
| **Energy/PUE Optimization** | Menganalisis data environment dan energi untuk menyarankan perubahan guna meningkatkan Power Usage Effectiveness (PUE). |

### Use Case 1: Predictive Failure Alerting for Critical Assets
**Goal:** Memberikan peringatan dini kepada operator infrastruktur mengenai probabilitas tinggi kegagalan aset kritikal (server, storage, cooling, power) sebelum kegagalan fisik benar-benar terjadi.

| Detail | Description |
| :--- | :--- |
| **Actor(s)** | AI & LLM Intelligence Engine, Data Ingestion Layer, NetBox, Monitoring Dashboard. |
| **Trigger** | Streaming real-time data operasional (temperature, power draw, SMART disk, fan speed, utilization). |
| **Pre-conditions** | Model telah dilatih menggunakan data historis kegagalan dan kondisi normal |
| **Success Criteria** | Sistem mengeluarkan High Probability of Failure Alert minimal 24–48 jam sebelum kegagalan aktual. |
| **Flow** | 1. Data Ingestion: AI Engine menerima telemetry dan metadata aset dari NetBox dan monitoring system.<br>2. Feature Engineering: Sistem menghitung statistical features seperti moving average, variance, trend deviation.<br>3. Model Scoring: Model prediktif (LSTM / Gradient Boosting / Random Forest) menghitung probabilitas kegagalan.<br>4. LLMReasoning Layer: LLM mengkorelasikan hasil model dengan konteks aset (lokasi, criticality, maintenance history).<br>5. Alert Generation: Jika threshold terlampaui, alert dikirim ke dashboard dan sistem incident management.<br>6. Output: Alert tersebut dialihkan ke Monitoring Dashboard DCIM dan Incident Management System. |
| **Priority** | High |

### Use Case 2: Capacity Optimization Recommendation
**Goal:** Mengidentifikasi underutilized resources dan memberikan rekomendasi konsolidasi atau redistribusi workload untuk meningkatkan efisiensi kapasitas infrastruktur.

| Detail | Description |
| :--- | :--- |
| **Actor(s)** | Capacity Planning Tool, AI & LLM Engine, NetBox |
| **Trigger** | Analisis terjadwal (mingguan) atau permintaan ad-hoc(mendadak). |
| **Pre-conditions** | Data kapasitas dan utilisasi tersedia minimal 90 hari. |
| **Success Criteria** | Rekomendasi menghasilkan penghematan kapasitas ≥10% dalam satu kuartal. |
| **Flow** | 1. Data Retrieval: Mengambil data CPU, RAM, Storage dan rack occupancy dari NetBox & metrics store.<br>2. Clustering Analysis: Sistem mengelompokkan workload dengan pola pemanfaatan rendah atau saling melengkapi.<br>3. Optimization Modeling: AI mensimulasikan skenario konsolidasi dan dampaknya terhadap performa dan power.<br>4. LLM Recommendation Layer: LLM menyajikan rekomendasi dalam bentuk narasi teknis yang mudah dipahami.<br>5. Output: Laporan rekomendasi kapasitas, target aset, dan estimasi efisiensi. |
| **Priority** | High |

### Use Case 3: Energy Anomaly Detection and PUE Drift
**Goal:** Mendeteksi anomali konsumsi energi dan penyimpangan PUE secara real-time untuk mencegah pemborosan energi dan kegagalan sistem kelistrikan.

| Detail | Description |
| :--- | :--- |
| **Actor(s)** | Power Monitoring System, AI & LLM Engine, DCIM Operator |
| **Trigger** | Streaming data power, suhu, dan environment. |
| **Pre-conditions** | Baseline PUE dan pola konsumsi energi telah ditentukan |
| **Success Criteria** | Anomali >5% terdeteksi dalam ≤15 menit. |
| **Flow** | 1. Real-Time Data Ingestion: Mengambil data power dari PDU, UPS, dan sensor lingkungan.<br>2. Baseline Comparison: Menggunakan model statistik atau ML (Z-score, Isolation Forest).<br>3. PUE Calculation: PUE dihitung secara kontinu berdasarkan power facility vs IT load.<br>4. Anomaly Alert: Sistem mendeteksi spike atau drift di luar batas toleransi.<br>5. Contextual Alerting: Alert menyertakan lokasi, perangkat terdampak, dan estimasi dampak energi.<br>6. Output: Alert tersebut mencakup besarnya penyimpangan dan perangkat atau area yang terpengaruh (misalnya, “Baris C, PDU-05: Konsumsi daya 8% lebih tinggi dari standar normal"). |
| **Priority** | Medium |

### Requirements Checklist
Berikut ini adalah daftar persyaratan teknis dan non-fungsional untuk Analytics & AI Engine, yang selaras dengan kasus penggunaan di atas.

| Requirement Type | Requirement | Status |
| :--- | :--- | :--- |
| **Technical** | Integrasi dengan NetBox API & metrics store. | To be determined |
| **Technical** | Support ML framework (PyTorch, TensorFlow). | To be determined |
| **Technical** | LLM inference via Ollama / Local LLM. | To be determined |
| **Performance** | Pemrosesan real-time telemetry data. | To be determined |
| **Scalability** | Support multiple concurrent models. | To be determined |
| **Data Quality** | Deteksi & penanganan noisy / incomplete data. | To be determined |
| **Availability** | Uptime AI Services ≥ 99%. | To be determined |
