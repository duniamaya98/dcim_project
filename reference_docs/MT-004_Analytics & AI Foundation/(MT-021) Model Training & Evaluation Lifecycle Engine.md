# (MT-021) Model Training & Evaluation Lifecycle Engine

# 1. Unified Training & Artifact Management Engine

## Objective

Membangun sistem training yang version-controlled, reproducible, dan lifecycle-aware untuk memastikan setiap model anomaly:

* Dapat dilacak versinya
* Memiliki baseline statistik drift
* Tersimpan dalam struktur artifact yang konsisten
* Tidak langsung aktif ke production

Fase ini menyelesaikan keterbatasan pada fase sebelumnya yang belum memiliki full version lifecycle governance [(MT-018) Traditional Machine Learning Model](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/I44pKpyLLU9mmFHCLBRgw).

## Architectural Concept

```
Monitoring Dataset
        ↓
Training Orchestrator
        ↓
Feature Pipeline
        ↓
Ensemble Model Training
        ↓
Artifact Packaging
        ↓
Model Registry (Candidate)
```

## Implementation

Training Orchestrator

File:

```
dcim_ai/training/training_orchestrator.py
```

Fungsi:

* Load dataset berdasarkan time-window
* Train / validation split
* Ensemble training:
  * Isolation Forest
  * Local Outlier Factor
  * One-Class SVM
* Validation anomaly ratio check


* Drift baseline calculation
* Artifact packaging
* Candidate auto-registration (optional)

## Artifact Structure (Per Version)

```
dcim_ai/artifacts/models/vX.Y/
    isolation_forest.pkl
    lof.pkl
    ocsvm.pkl
    scaler.pkl
    feature_columns.json
    metadata.json
```

Metadata menyimpan:

* version
* training\_window

  Parameter yang menentukan rentang waktu dataset training (misal: last\_30\_minutes, all).

  Berfungsi untuk:
  * Mengontrol adaptasi model terhadap data terbaru
  * Membedakan full historical retrain vs rolling retrain
  * Menghindari contamination akibat data lama
* validation anomaly ratio

  Menunjukan proporsi data pada validation set yang diklasifikasikan sebagai anomaly.

  Rumus umum:

```
validation_anomaly_ratio = anomaly_count / total_validation_samples
```



&#x20;   Digunakan untuk:

* Memastikan model tidak terlalu agresif
* Mendeteksi anomaly explosion saat retraining
* Membandingkan stabilitas antar versi model

&#x20;   Jika terlalu tinggi → model ove-sensitive

&#x20;   Jika terlalu rendah → model terlalu tumpul

* drift baseline mean

  Rata-rata nilai setiap fitur pada dataset training.

  Disimpan sebagai baseline refrensi untuk evaluasi drift pada fase inference dan drift robustness testing.

  Digunakan untuk:
  * Perhitungan Z-score
  * Drift simulation
  * Distribution comparison antar versi
* drift baseline std

  Standar deviasi setiap fitur pada datashet training.

  Digunakan untuk:
  * Mengukur deviasi distribusi
  * Simulasi drift berbasis sigma ((0.5σ, 1σ, 2σ)
  Nilai ini menjadi dasar dalam mengukur ketahanan model terhadap distribution shift.
* timestamp

## Outcome

* Model training kini reproducible
* Artifact terstruktur
* Tidak ada overwrite manual
* Version governance siap untuk promotion control



***

# 2. Cross-Version Benchmark & Evaluation Engine

## Objective

Mencegah regression dengan membandingkan model candidate terhadap model production aktif. Fase ini memperluas model registry dan lifecycle management yang telah dibangun sebelumnya [(MT-019) Anomaly Detection Framework](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/jLnCyJBpKVVWT18Ci96Ep).

## Architectural Concept

```
Candidate Model
        +
Production Model
        ↓
Evaluation Engine
        ↓
Regression Metrics
```

## Evaluation Metrics

* anomaly\_ratio\_candidate

  Proporsi anomaly yang dihasilkan model candidate pada dataset evaluasi.

  Digunakan untuk:
  * Mengukur agresivitas model baru
  * Membandingkan perubahan perilaku terhadap production
* anomaly\_ratio\_production

  Proporsi anomaly yang dihasilkan model production aktif.

  Menjadi baseline pembanding untuk regression analysis.
* anomaly\_delta

  Selisih antara anomaly\_ratio\_candidate dan anomaly\_ratio\_production.

  Rumus:
  ```
  anomaly_delta = candidate_ratio - production_ratio
  ```
  Digunakan untuk:
  * Medeteksi regression
  * Mengidentifikasi anomaly explosion
  * Menentukan anomaly\_safe flag
  Semakin besar delta → semakin berisiko model baru.
* agreement\_rate

  Presentase kesamaan prediksi antara model candidate dan production.

  Rumus umum:
  ```
  agreement_rate = same_prediction / total_samples
  ```
  Digunakan untuk:
  * Mengukur stabilitas antar versi
  * Mendeteksi perubahan boundary decision
  * Menilai consistency model behavior
* dataset\_size

  Jumlah sampel yang digunakan dalam evaluasi.

  Berfungsi untuk:
  * Memberikan konteks statistik
  * Menghadiri evaluasi pada dataset terlalu kecil
  * Menentukan reliabilitas hasil perbandingan

## Safety Rule

* anomaly\_delta harus dalam threshold aman
* agreement\_rate tinggi
* Tidak terjadi anomaly explosion atau anomaly saturation

## Output

```
evaluation_report.json
```

## Outcome

* Regression terdeteksi sebelum deployment
* Model baru tidak langsung dipercaya
* Production stability terjaga



***

# 3. Correlation & Incident Impact Validation

## Objective

Mengukur dampak perubahan model terhadap sistem incident & domain correlation. Fase ini terintegrasi langsung dengan arsitektur correlation engine [(MT-020) Cross-Domain Correlation Engine](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/dnYp6l89De). Evaluasi tidak berhenti pada anomaly detection, tetapi dilanjutkan hingga pembentukan incident yang bersifat operasional.

## Architectural Concept

```
Anomaly Prediction
        ↓
Domain Engine
        ↓
Correlation Engine
        ↓
Incident Simulation
        ↓
Impact Comparison
```

## Evaluated Metrics

* incident\_delta

  Selisih jumlah incident antara model candidate dan production.

  Digunakan untuk:
  * Mengukur dampak operasional
  * Mendeteksi escalation tidak terkontrol
  * Menghindari incident explosion di production
* candidate\_incident\_count / production\_incident\_count

  Jumlah total incident yang dihasilkan oleh masing-masing model.

  Menjadi indikator utama perubahan perilaku sistem monitoring.
* multi\_domain\_ratio

  Proporsi incident yang melibatkan lebih dari satu domain aktif.

  Rumus umum:
  ```
  multi_domain_ratio = multi_domain_incidents / total_incidents
  ```
  Digunakan untuk:
  * Mendeteksi interaksi lintas domain
  * Mengidentifikasi kompleksitas gangguan
  * Menilai perubahan correlation behavior
* severity\_distribution

  Distribusi tingkat severity (normal, warning, critical).

  Digunakan untuk:
  * Mengukur perubahan eskalasi
  * Mendeteksi peningkatan severity profile
  * Menilai potensi alert fatigue
* average\_confidence

  Rata-rata confidence score dari incident.

  Confidence dihitung dari kombinasi:
  * anomaly\_ratio
  * drift\_ratio
  * domain persistence
  Digunakan untuk:
  * Mengukur keyakinan sistem terhadap incident
  * Menilai reliability output
* domain\_activation\_intensity

  Rata-rata jumlah domain aktif per incident.

  Digunakan untuk:
  * Mengukur kompleksitas gangguan
  * Mendeteksi perubahan domain behavior
  * Menganalisis interaksi lintas domain
* correlation\_safe flag

  Boolean indicator yang menyatakan apakah perubahan correlation behavior masih dalam batas aman.

  True → perubahan terkendali

  False → perubahan signifikan, perlu review

## Insight Layer

Sistem kini mampu:

* Mendeteksi perubahan severity profile
* Mengidentifikasi pergeseran multi-domain interaction
* Mengukur intensitas aktivasi domain
* Menghitung potensi escalation

## Outcome

* Model tidak hanya dievaluasi dari anomaly
* Dampak operasional dianalisis
* Incident stability terjaga



***

# 4. Drift Robustness & Ensemble Optimization

## Objective

Menguji ketahanan model terhadap distribution shift. 

Mengatasi keterbatasan drift sensitivity yang teridentifikasi pada fase awal [(MT-018) Traditional Machine Learning Model](assets://./workspace/0712d6e7-fc27-4d65-b0fa-2e8581ad87c2/I44pKpyLLU9mmFHCLBRgw).

## Drift Simulation Strategy

Partial Feature Drift:

* Drift hanya pada sebagian fitur (realistic simulation)
* Level:
  * 0σ
  * 0.5σ
  * 1σ
  * 2σ

## Evaluation Metrics

* drift\_level\_0

  Anomaly ratio pada dataset tanpa drift.

  Menjadi baseline stabilitas model.
* drift\_level\_0.5

  Anomaly ratio saat sebagian fitur digeser 0.5σ.

  Digunakan untuk:
  * Mengukur toleransi terhadap mild shift
  * Mendeteksi over-sensitivity
* drift\_level\_1

  Anomaly ratio saat sebagian fitur digeser 1σ.

  Mewakili modorete distribution shift.

  Jika terlalu tinggi → model terlalu sensitif.
* drift\_level\_2

  Anomaly ratio saat sebagian fitur digeser 2σ.

  Mewakili severe distribution shift.

  Seharusnya meningkat signifikan dibanding drift\_level\_0.
* drift\_sensitivity

  Perbedaan antara drift\_level\_2 dan drift\_level\_0.

  Rumus:
  ```
  drift_sensivity = drift_level_2 - drift_level_0
  ```
  Digunakan untuk:
  * Mengukur respons model terhadap shift besar
  * Menilai ketahanan model

## Ensemble Optimization

* Voting threshold diperketat (≥2/3 model)

  Parameter ensemble decision rule.

  Minimal dua dari tiga model harus menyetujui anomaly agar dianggap valid.

  Digunakan untuk:
  * Mengurangi false positive
  * Meningkatkan robustness
  * Menjaga konsistensi prediksi
* contamination / nu tuning

  Parameter pada model anomaly detection yang menentukan estimasi proporsi anomaly dalam data training.

  Digunakan untuk:
  * Mengontrol boundary decision
  * Menghindari model terlalu agresif
  * Menyesuaikan sensivitas terhadap distribusi data 
* Progressive drift response validation

## Outcome

* Tidak terjadi anomaly saturation
* Respons drift menjadi gradual
* Model lebih tahan terhadap noise
* Robust terhadap severe shift



***

# 5. Promotion Gatekeeper & Simulation Framework

## Objective

Menyatukan seluruh layer evaluasi menjadi sistem keputusan semi-automatic sebelum activation.

Mengatasi keterbatasan "manual promotion tanpa evaluasi terstruktur".

## Architectural Concept

```
Anomaly Evaluation
        +
Correlation Impact
        +
Drift Robustness
        ↓
Promotion Gatekeeper
        ↓
APPROVE / REVIEW / REJECT
```

## Decision Inputs

* anomaly\_safe

  True jika anomaly\_delta dalam batas aman dan agreement\_rate tinggi.

  Menandakan tidak terjadi regression signifikan.
* correlation\_safe

  True jika incident behavior dan severity profile masih dalam batas toleransi.

  Menandakan dampak operasional terkendali.
* drift\_safe

  True jika drift\_level\_0.5 dan drift\_level\_1 tidak menunjukan over-sensitivity.

  Menandakan model stabil terhadap mild shift.

## Decision Output

```
{
  candidate_version,
  promotion_recommendation,
  risk_level
}
```

## Decision Categories

* APPROVE → aman di semua layer
* REVIEW → ada perubahan signifikan tapi terkendali
* REJECT → risiko tinggi atau regression terdeteksi

## Governance Result

* Model tidak lagi self-activate
* Lifecycle terkontrol
* Promotion berbasis evaluasi multi-layer
* Risk-aware AI deployment



***

# 6. System Evolution Summary

Sistem sudah berevolusi dari: 

Feature-level anomaly detection

menjadi 

Lifecycle-Governed Monitoring Intelligence Platform



***

