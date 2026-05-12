# (MT-018) Traditional Machine Learning Model

# 1. Overview

## Objective 

Membangun sistem anomaly detection berbasis Traditional Machine Learning untuk:

* Monitoring server metrics real-time
* Mendeteksi abnormal behavior
* Menyimpan hasil anomaly ke database
* Menyediakan fondasi AI DCIM adaptif

***

# 2. System Architecture

```scss
Telemetry Collector
        ↓
PostgreSQL + TimescaleDB
        ↓
Dataset Preparation
        ↓
Baseline Model Training
        ↓
Model Artifacts (pkl bundle)
        ↓
Inference Engine
        ↓
server_anomalies table
```



***

# 3. ML Environment Setup

## Infrastructure

* OS : Ubuntu 24.04 LTS
* Python venv: ragavenv
* Database: PostgreSQL 16 + TimescaleDB
* GPU: 2x RTX 3070 TI (not used for baseline ML)

## Python Dependencies

```nginx
pandas
numpy
scikit-learn
sqlalchemy
psycopg2
joblib
```

***

# 4. Dataset Preparation

## Data Source

Table : `server_metrics`

Columns:

* time
* hostname
* cpu\_usage
* memory\_usage
* disk\_io
* temperature
* gpu\_util
* gpu\_mem\_used
* gpu\_mem\_total
* net\_rx
* net\_tx

## Cleaning Pipeline

Steps:

* Drop NULL values
* Remove non-feature columns
* Variance analysis
* Remove low-variance features (<1e-3)
* StandardScaler normalization
* Train-test split (80/20)

## Feature Selection Result

Initial feature set:

```css
['cpu_usage', 'memory_usage', 'disk_io', 'net_rx', 'net_tx']
```

Adaptive retrain feature set:

```css
['cpu_usage', 'memory_usage', 'net_rx', 'net_tx']
```

Dengan penjelasan:

* cpu\_usage (%)
  * Persentase utilisasi cpu.
  * Indikator beban komputasi server.
  * Spike mendadak → indikasi runaway process / overload.
  * Variance tinggi → kandidat utama anomaly detection.
* memory\_usage (%)
  * Persentase penggunaan RAM.
  * Drift baseline sering terjadi akibat perubahan workload.
  * Penting untuk mendeteksi memory leak.
* disk\_io (bytes/sec atau cumulative IO)
  * Aktivitas read/write disk.
  * Burst tinggi → backup, indexing, database write strom.
  * Variance rendah → di-drop oleh variance filter.
* net\_rx (MB)
  * Network receive throughput.
  * Mendeteksi traffic spike.
  * Digunakan untuk mendeteksi DDoS / traffice anomaly.
* net\_tx (MB)
  * Network transmit throughput.
  * Indikator outgoing brust (backup sync, upload, replication).

***

# 5. Baseline Model Development

## Algorithm

Isolation Forest

Parameters:

```ini
n_estimators = 200  
#jumlah decision trees.
#Lebih banyak tree → boundary lebih stabil.
#Tradeoff: waktu training vs robustness.
contamination = 0.05
#Perkiraan proporsi anomaly.
#Mengatur threshold decision.
#Tidak memaksa output 5%, hanya mengatur cut-off saat training
random_state = 42
#Repoducibility.
#Menjamin hasil konsisten saat retraining.
```

## Validation

✔ CPU Spike Injection Test

Manual spike → anomaly detected

✔ Training Anomaly Ratio

≈ 5% (as configured)



***

# 6. Model Benchmarking

| Contamination | Train Time | Inference Time | Test Ratio |
| ------------- | ---------- | -------------- | ---------- |
| 0.01          | \~0.13s    | \~0.008s       | \~1%       |
| 0.05          | \~0.13s    | \~0.008s       | \~5%       |
| 0.10          | \~0.13s    | \~0.008s       | \~13%      |

Inference latency < 10ms

Suitable for real-time DCIM.

Penjelasan metrics:

* Train Time (\~0.13s)
  * Mengukur computational overhead.
  * Indikator kelayakan retraining frequent.
* Inference Time (\~0.008s)
  * Latency per batch.
  * <10ms → cocok real-time monitoring.



***

# 7. Model Packaging

## Artifact Structure

```
models/
  isolation_forest_baseline.pkl
  scaler_baseline.pkl
  feature_columns.pkl
```

## Inference Pipeline

File:

```shellscript
src/anomaly_inference.py
```

Flow

* Load model
* Load scaler
* Load feature list
* Fetch data from DB
* Transform
* Predict
* Insert into server\_anomalies

## Output Table

`server_anomalies`

Columns:

* time
* cpu\_usage
* memory\_usage
* disk\_io
* net\_rx
* net\_tx
* anomaly (boolean)



***

# 8. Adaptive Model Lifecycle Management

## Problem Encountered

Data drift:



Memory baseline:

23% → 16%

Anomaly ratio:

5% → 45%

## Solution Implemented

Rolling retraining (30-minute window)

File

```shellscript
src/adaptive_retrain.py
```

Mechanism:

* Fetch last 30 minutes
* Full retrain
* Overwrite artifact
* Maintain contamination=0.05

Training anomaly ratio stabilized ≈ 5%

## Key Insights Learned

* Static models fail in dynamic environments
* Isolation Forest sensitive to low variance
* Snapshot-based detection unstable for highly stable servers
* Distribution shift drastically impacts threshold

# 9. System Status

## Completed

* Environment Setup
* Dataset Preparation
* Baseline Model Development
* Model Benchmarking
* Model Packaging
* Adaptive Retraining

## Limitations

* Snapshot detection too sensitive
* No trend-based detection
* No drift scoring metric
* No model versioning
* No rollback mechanism

# 10. Phase Completion Summary

Traditional ML Phase Status:

✔ Functional

✔ Drift-aware (basic)

✔ Production-testable

⚠ Needs intelligence upgrade





| Date       | Versi | Auth   | Note                                  |
| ---------- | ----- | ------ | ------------------------------------- |
| 13/02/2026 | 1     | Fakhri | -                                     |
| 02/03/2026 | 1.1.2 | Fakhri | Perubahan tambahan penjelasan metrics |

