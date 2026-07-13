# MT-018 Traditional ML Model — Review Report

**Reviewer:** Hermes DCIM Orchestrator
**Date:** 2026-06-25
**Documents Reviewed:**
- MT-018_Traditional_Machine_Learning_Model.md (Main Spec, v1.2.0)
- MT-018_Traditional_ML_Model_Configuration_Documentation.md (Config Doc)

---

## Executive Summary

| Aspek | Status |
|-------|--------|
| Functional baseline | ✅ WORKING |
| Security posture | ❌ CRITICAL GAPS |
| Data integrity | ⚠️ RISK OF DUPLICATES |
| Production readiness | ⚠️ BASELINE ONLY |
| Addendum v1.2.0 implementation | ❌ NOT IMPLEMENTED |
| Monitoring implementation | ❌ NOT IMPLEMENTED |

**Kesimpulan:** Baseline anomaly detection **berfungsi** untuk proof-of-concept. Tapi ada **2 isu P1 (critical)** dan **5 isu P2** yang harus diperbaiki sebelum production deployment.

---

## P1 — CRITICAL (Harus diperbaiki sekarang)

### 1. Hardcoded Database Credentials

**Lokasi:** Ketiga script (training, inference, retraining)

```python
engine = create_engine(
    "postgresql+psycopg2://infra:password@127.0.0.1/dcim_ai"
)
```

**Masalah:**
- Password `password` dalam plain text
- Ter-expose di code, documentation, dan version control
- Siapapun yang akses repo bisa lihat credentials
- Violates DCIM Security requirement (SOUL.md §7.4)

**Fix:**
```python
import os
engine = create_engine(
    os.environ.get(
        "DCIM_DB_URL",
        "postgresql+psycopg2://infra:${DCIM_DB_PASSWORD}@127.0.0.1/dcim_ai"
    )
)
```

Atau pakai `.env` + `python-dotenv`:
```python
from dotenv import load_dotenv
load_dotenv()
engine = create_engine(os.environ["DCIM_DB_URL"])
```

**Ref:** Vault/Kubernetes Secrets/Ansible Vault — sesuai SOUL.md §7.4

---

### 2. Duplicate Anomaly Writes (Data Integrity)

**Lokasi:** `src/anomaly_inference.py`, Section 8 config doc

```python
original_df[...].to_sql(
    "server_anomalies",
    engine,
    if_exists="append",  # ← MASALAH
    index=False
)
```

**Masalah:**
- Inference query: `WHERE time > NOW() - INTERVAL '30 minutes'`
- Training query: `WHERE time > NOW() - INTERVAL '30 minutes'`
- Jika inference run 2x dalam 30 menit → **data duplicate**
- Tidak ada deduplication mechanism
- `server_anomalies` table tidak punya UNIQUE constraint

**Fix (opsi):**

**Opsi A — Time-based dedup:**
```python
# Sebelum write, hapus existing data untuk window yang sama
max_time = original_df['time'].max()
min_time = original_df['time'].min()
engine.execute(
    f"DELETE FROM server_anomalies WHERE time >= '{min_time}' AND time <= '{max_time}'"
)
original_df.to_sql("server_anomalies", engine, if_exists="append", index=False)
```

**Opsi B — INSERT ON CONFLICT (recommended):**
```sql
CREATE TABLE server_anomalies (
    time TIMESTAMPTZ NOT NULL,
    hostname TEXT,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_io FLOAT,
    net_rx FLOAT,
    net_tx FLOAT,
    anomaly BOOLEAN,
    PRIMARY KEY (time, hostname)  -- composite key
);
```

```python
# pakai SQLAlchemy execute
from sqlalchemy import text
with engine.begin() as conn:
    conn.execute(text("""
        INSERT INTO server_anomalies (time, hostname, cpu_usage, memory_usage, disk_io, net_rx, net_tx, anomaly)
        VALUES (:time, :hostname, :cpu, :mem, :disk, :rx, :tx, :anomaly)
        ON CONFLICT (time, hostname) DO UPDATE SET
            cpu_usage = EXCLUDED.cpu_usage,
            anomaly = EXCLUDED.anomaly
    """), records)
```

---

## P2 — HIGH (Perlu diperbaiki sebelum production)

### 3. Missing `hostname` di Output Table

**Masalah:**
- `server_metrics` punya `hostname` column
- `server_anomalies` TIDAK punya `hostname`
- Inference code drop `hostname` sebelum predict
- Anomaly output tidak bisa di-trace ke server tertentu

**Dampak:** Untuk DCIM, anomaly tanpa hostname = tidak actionable. NOC/SOC tidak tahu server mana yang bermasalah.

**Fix:**
```sql
CREATE TABLE server_anomalies (
    time TIMESTAMPTZ NOT NULL,
    hostname TEXT,          -- TAMBAH INI
    cpu_usage FLOAT,
    memory_usage FLOAT,
    disk_io FLOAT,
    net_rx FLOAT,
    net_tx FLOAT,
    anomaly BOOLEAN,
    PRIMARY KEY (time, hostname)
);
```

```python
# inference script — simpan hostname
original_df[
    ["time", "hostname", "cpu_usage", "memory_usage", "disk_io", "net_rx", "net_tx", "anomaly"]
].to_sql(...)
```

---

### 4. No Model Versioning / Rollback

**Masalah:**
- Setiap retraining overwrite `isolation_forest_baseline.pkl`
- Tidak ada version history
- Tidak ada performance comparison sebelum deploy
- Jika model baru lebih buruk → tidak bisa rollback

**Dampak:** Production ML tanpa versioning = operasional risk tinggi.

**Fix (minimum):**
```python
import shutil
from datetime import datetime

# Backup sebelum overwrite
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copy("models/isolation_forest_baseline.pkl", f"models/archive/isolation_forest_{timestamp}.pkl")

# Simpan metadata
import json
metadata = {
    "version": timestamp,
    "train_samples": len(X_train),
    "contamination": 0.05,
    "feature_columns": feature_columns,
    "training_anomaly_ratio": float(anomaly_ratio)
}
with open(f"models/archive/metadata_{timestamp}.json", "w") as f:
    json.dump(metadata, f)
```

**Ideal:** MLflow / DVC untuk model registry.

---

### 5. Monitoring Tidak Diimplementasi

**Masalah:**
- Section 11 MT-018 menyebutkan: anomaly ratio, inference latency, retraining count
- Config doc Section 11 juga menyebutkan monitoring
- **Tidak ada kode monitoring di script manapun**

**Fix (minimum):**
```python
# Tambahan di inference script
import time

start = time.time()
# ... prediction code ...
latency = time.time() - start

anomaly_count = anomaly_flags.sum()
total = len(anomaly_flags)
ratio = anomaly_count / total if total > 0 else 0

print(f"[MONITOR] inference_latency_ms={latency*1000:.1f} anomaly_ratio={ratio:.3f} total_rows={total}")

# Untuk Prometheus integration:
# from prometheus_client import Histogram, Gauge
# INFERENCE_LATENCY = Histogram('ml_inference_latency_seconds', 'Inference latency')
# ANOMALY_RATIO = Gauge('ml_anomaly_ratio', 'Anomaly ratio')
```

---

### 6. Feature Groups Addendum v1.2.0 Belum Diimplementasi

**Masalah:**
- Addendum mendefinisikan 5 feature groups: `server_compute`, `server_health`, `power_metrics`, `environment_metrics`, `capacity_metrics`
- Implementasi saat ini: hanya `server_compute` (baseline)
- `MetricSource` abstract class belum diimplementasi

**Status:** Addendum v1.2.0 = forward plan, bukan completed work. Harus dinyatakan explicit di dokumen.

**Rekomendasi:** Update MT-018 Section 9 (System Status) untuk clarify:
```markdown
## System Status

### Completed
- Baseline anomaly detection (server_compute only)
- Environment Setup, Dataset Preparation, Benchmarking, Packaging
- Adaptive Retraining (basic drift handling)

### In Progress / Planned (per Addendum v1.2.0)
- [ ] Feature group expansion (server_health, power, environment, capacity)
- [ ] MetricSource abstract loader
- [ ] Forecasting pipeline (Prophet/XGBoost/LSTM)
- [ ] Supervised labeling (failure_events table)
- [ ] Imputation & noise handling
- [ ] Model versioning & rollback
```

---

### 7. No Scheduling Mechanism

**Masalah:**
- Script di-run manual: `python src/anomaly_inference.py`
- Tidak ada cron/scheduler untuk automated inference
- Tidak ada health check / watchdog

**Fix:**
```bash
# Crontab untuk inference (setiap 5 menit)
*/5 * * * * cd /path/to/project && source ragavenv/bin/activate && python src/anomaly_inference.py >> logs/inference.log 2>&1

# Crontab untuk adaptive retraining (setiap 30 menit)
*/30 * * * * cd /path/to/project && source ragavenv/bin/activate && python src/adaptive_retrain.py >> logs/retrain.log 2>&1
```

---

## P3 — MEDIUM (Fix saat ada waktu)

### 8. Typo & Inconsistency

- Config doc Section 8: "Congfiguration" → "Configuration"
- Config doc Section 12: filename `adaptive_retraining.py` vs actual `adaptive_retrain.py`

### 9. Missing Data Quality Logging

- Addendum §11.6 mendefinisikan imputation strategies dan `data_quality_log`
- Implementasi saat ini hanya `dropna()` — no logging, no imputation flags

### 10. No Alerting Integration

- Anomaly terdeteksi → tidak ada alert ke NOC/SOC
- Perlu integrasi dengan Telegram Alerting (L9.2) atau email

---

## Konsistensi Antar Dokumen

| Aspek | MT-018 Main Spec | Config Doc | Status |
|-------|-------------------|------------|--------|
| Feature columns | `cpu_usage, memory_usage, disk_io, net_rx, net_tx` | Same | ✅ Consistent |
| Model params | IF, n_est=200, cont=0.05, rs=42 | Same | ✅ Consistent |
| Query window | 30 minutes | Same | ✅ Consistent |
| DB credentials | `infra:password` | Same | ⚠️ Consistent but insecure |
| Artifact names | `isolation_forest_baseline.pkl` etc | Same | ✅ Consistent |
| File paths | `notebooks/`, `src/`, `models/` | Same | ✅ Consistent |
| Addendum v1.2.0 | Referenced | Not reflected | ⚠️ Config doc = baseline only |

---

## Mapping ke DCIM Block 7 (Analytics & AI)

| Block 7 Requirement | MT-018 Status | Gap |
|---------------------|---------------|-----|
| Anomaly Detection | ✅ Baseline IF | No LOF/OCSVM comparison |
| Predictive Maintenance | ❌ Not started | Addendum §11.4 plan exists |
| Capacity Forecasting | ❌ Not started | Addendum §11.2 capacity_metrics plan |
| Energy/PUE Analysis | ❌ Not started | Addendum §11.2 power_metrics plan |
| RCA Engine | ❌ Not started | Separate component |
| Model Training Pipeline | ⚠️ Basic | No versioning, no registry |
| LLM/RAG Explanation | ❌ Not started | Separate component |

---

## Rekomendasi Prioritas

| Priority | Action | Effort |
|----------|--------|--------|
| **P1** | Fix credentials → env vars / Vault | 1 jam |
| **P1** | Fix duplicate writes → dedup or PK constraint | 2 jam |
| **P2** | Add hostname ke output table | 30 menit |
| **P2** | Add model versioning (minimum: archive + metadata) | 2 jam |
| **P2** | Add monitoring logging (latency, ratio, count) | 1 jam |
| **P2** | Clarify addendum status di Section 9 | 15 menit |
| **P2** | Add cron scheduling | 30 menit |
| **P3** | Fix typos | 5 menit |
| **P3** | Add data quality logging | 2 jam |
| **P3** | Add alerting integration | 4 jam |

**Total effort untuk P1+P2:** ~7 jam
**Total effort untuk full P1+P2+P3:** ~19 jam

---

## Quality Gate Checklist

- [x] Pipeline berfungsi (training → inference → output)
- [x] Model benchmark terdokumentasi
- [x] Feature selection rationale dijelaskan
- [x] Adaptive retraining bekerja
- [ ] ❌ Credentials tidak di-expose
- [ ] ❌ Data integrity terjaga (no duplicates)
- [ ] ❌ Output traceable ke server (hostname)
- [ ] ❌ Model versioned & rollback-able
- [ ] ❌ Monitoring diimplementasi
- [ ] ❌ Scheduling automated
- [ ] ❌ Alerting integrated
- [ ] ❌ Addendum v1.2.0 status clarified

**Current score: 5/12 (42%)**

---

## Kesimpulan

MT-018 baseline **berhasil dibangun** dan **berfungsi** untuk anomaly detection sederhana. Isolation Forest dengan 30-minute rolling window adalah pilihan yang reasonable untuk proof-of-concept.

Tapi untuk **production DCIM deployment**, ada 2 critical issues (credentials + data integrity) yang harus fix dulu. Tanpa hostname di output, anomaly tidak actionable untuk NOC/SOC. Tanpa model versioning, operasional risk tinggi.

Addendum v1.2.0 adalah **forward plan yang bagus** — tapi harus dinyatakan explicit bahwa itu belum diimplementasi, bukan "completed".

**Status aktual: COMPLETED (baseline only) — needs 7 hours of hardening before production.**
