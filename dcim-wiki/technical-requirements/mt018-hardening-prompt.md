# MT-018 Hardening Prompt — AI Agent Task Specification

> **Purpose:** Prompt ini dirancang untuk AI coding agent (Claude Code, Codex, Copilot, atau Hermes Dev agent) agar bisa memperbaiki semua issue yang teridentifikasi dalam review MT-018 Traditional ML Model.
>
> **Cara pakai:** Copy seluruh isi file ini sebagai prompt/task description ke agent yang kamu pakai di host.
>
> **Reviewed by:** Hermes DCIM Orchestrator, 2026-06-25

---

## 1. Project Context

MT-018 adalah sistem anomaly detection berbasis Isolation Forest untuk monitoring server metrics di DCIM Core Platform. Pipeline:

```
Telemetry Collector → PostgreSQL/TimescaleDB → Dataset Preparation → Isolation Forest Training → Model Artifacts (.pkl) → Inference Engine → server_anomalies table
```

Baseline sudah berfungsi. Tugas ini memperbaiki **security, data integrity, dan operational gaps** agar siap production.

---

## 2. Environment

| Component | Value |
|-----------|-------|
| OS | Ubuntu 24.04 LTS |
| Python venv | `ragavenv` |
| Activate | `source ragavenv/bin/activate` |
| Database | PostgreSQL 16 + TimescaleDB |
| DB Name | `dcim_ai` |
| DB User | `infra` |
| DB Host | `127.0.0.1` |

**Working directory assumption:** Semua path relatif dari project root (dimana `notebooks/`, `src/`, `models/` berada). Adjust jika beda.

---

## 3. File Inventory

| File | Purpose |
|------|---------|
| `notebooks/dataset_preparation.py` | Training script — load data, clean, train IF, save artifacts |
| `src/anomaly_inference.py` | Inference script — load model, predict, write anomalies |
| `src/adaptive_retrain.py` | Retraining script — rolling window retrain |
| `models/isolation_forest_baseline.pkl` | Isolation Forest model artifact |
| `models/scaler_baseline.pkl` | StandardScaler artifact |
| `models/feature_columns.pkl` | Feature column list artifact |
| `.env` | **BARU — Buat file ini** untuk credentials |

---

## 4. Tasks — P1 CRITICAL

### Task 1: Fix Hardcoded Credentials

**Files:** `notebooks/dataset_preparation.py`, `src/anomaly_inference.py`, `src/adaptive_retrain.py`

**Problem:** Password `password` hardcode di `create_engine()` di semua 3 script.

**Fix:**

**Step 1 — Buat `.env` di project root:**
```bash
# .env — jangan commit ke git
DCIM_DB_URL=postgresql+psycopg2://infra:YOUR_ACTUAL_PASSWORD@127.0.0.1/dcim_ai
```

**Step 2 — Buat `.env.example` (untuk reference, tanpa password):**
```bash
# .env.example — safe to commit
DCIM_DB_URL=postgresql+psycopg2://infra:CHANGE_ME@127.0.0.1/dcim_ai
```

**Step 3 — Buat `.gitignore` entry (jika belum ada):**
```
.env
models/*.pkl
models/archive/
__pycache__/
```

**Step 4 — Update KETIGA script, ganti:**

```python
# LAMA (HAPUS):
engine = create_engine(
    "postgresql+psycopg2://infra:password@127.0.0.1/dcim_ai"
)

# BARU (GANTI DENGAN):
import os
from dotenv import load_dotenv

load_dotenv()  # load .env file

DB_URL = os.environ.get("DCIM_DB_URL")
if not DB_URL:
    raise EnvironmentError("DCIM_DB_URL not set. Copy .env.example to .env and configure.")

engine = create_engine(DB_URL)
```

**Step 5 — Install dependency:**
```bash
source ragavenv/bin/activate
pip install python-dotenv
```

**Verification:**
```bash
# Pastikan .env ada
cat .env | grep DCIM_DB_URL

# Pastikan script tidak punya hardcoded password lagi
grep -rn "infra:password" notebooks/ src/
# Expected: no output

# Test import
python -c "from dotenv import load_dotenv; print('dotenv OK')"
```

---

### Task 2: Fix Duplicate Anomaly Writes

**File:** `src/anomaly_inference.py`

**Problem:** `if_exists="append"` tanpa dedup. Jika inference run >1x dalam 30 menit → data duplicate.

**Fix — Opsi A (Recommended): Hapus data lama sebelum write**

Ganti bagian write di `src/anomaly_inference.py`:

```python
# LAMA:
original_df[
    ["time","cpu_usage","memory_usage","disk_io","net_rx","net_tx","anomaly"]
].to_sql(
    "server_anomalies",
    engine,
    if_exists="append",
    index=False
)

# BARU:
from sqlalchemy import text

output_df = original_df[
    ["time","hostname","cpu_usage","memory_usage","disk_io","net_rx","net_tx","anomaly"]
]

if not output_df.empty:
    min_time = output_df["time"].min()
    max_time = output_df["time"].max()

    with engine.begin() as conn:
        # Hapus data yang overlap (dedup)
        conn.execute(text(
            "DELETE FROM server_anomalies WHERE time >= :min_t AND time <= :max_t"
        ), {"min_t": min_time, "max_t": max_time})

        # Insert data baru
        output_df.to_sql(
            "server_anomalies",
            conn,
            if_exists="append",
            index=False
        )

    print(f"[INFERENCE] Wrote {len(output_df)} rows ({min_time} → {max_t})")
else:
    print("[INFERENCE] No data to write")
```

**Fix — Opsi B (Alternative): Primary Key constraint**

Jika ingin hard guarantee di database level, jalankan SQL ini satu kali:

```sql
-- Jalankan sekali di psql
-- WARNING: Hapus data duplicate yang mungkin sudah ada

-- 1. Cek duplicate
SELECT time, hostname, COUNT(*)
FROM server_anomalies
GROUP BY time, hostname
HAVING COUNT(*) > 1;

-- 2. Hapus duplicate (keep first)
DELETE FROM server_anomalies
WHERE ctid NOT IN (
    SELECT MIN(ctid)
    FROM server_anomalies
    GROUP BY time, hostname
);

-- 3. Tambahkan primary key
ALTER TABLE server_anomalies
    ADD COLUMN IF NOT EXISTS hostname TEXT;

ALTER TABLE server_anomalies
    ADD PRIMARY KEY (time, hostname);
```

> **Pilih Opsi A atau B, jangan keduanya.** Opsi A lebih fleksibel, Opsi B lebih robust.

**Verification:**
```bash
# Cek tidak ada lagi if_exists="append" tanpa dedup logic
grep -n "if_exists" src/anomaly_inference.py
# Expected: ada tapi dalam context block yang sudah di-update dengan DELETE sebelum INSERT

# Test inference
source ragavenv/bin/activate
python src/anomaly_inference.py

# Jalankan lagi — cek tidak duplicate
python src/anomaly_inference.py

# Cek database
psql -U infra -d dcim_ai -c "SELECT COUNT(*), COUNT(DISTINCT time || hostname) FROM server_anomalies;"
# Expected: COUNT(*) == COUNT(DISTINCT ...) (no duplicates)
```

---

## 5. Tasks — P2 HIGH

### Task 3: Add `hostname` ke Output Table

**Files:** `src/anomaly_inference.py`, database schema

**Problem:** `server_anomalies` tidak punya `hostname`. Anomaly tidak traceable ke server.

**Fix:**

**Step 1 — Update database schema:**
```sql
-- Jalankan sekali
ALTER TABLE server_anomalies
    ADD COLUMN IF NOT EXISTS hostname TEXT;

-- Update primary key jika sudah ada (dari Task 2 Opsi B)
-- atau tambahkan jika belum
ALTER TABLE server_anomalies
    DROP CONSTRAINT IF EXISTS server_anomalies_pkey;

ALTER TABLE server_anomalies
    ADD PRIMARY KEY (time, hostname);
```

**Step 2 — Update inference script (sudah termasuk di Task 2):**

Pastikan output_df include `hostname`:
```python
output_df = original_df[
    ["time","hostname","cpu_usage","memory_usage","disk_io","net_rx","net_tx","anomaly"]
]
```

**Verification:**
```bash
# Cek schema
psql -U infra -d dcim_ai -c "\d server_anomalies"
# Expected: hostname TEXT column exists

# Jalankan inference
python src/anomaly_inference.py

# Cek data
psql -U infra -d dcim_ai -c "SELECT time, hostname, anomaly FROM server_anomalies LIMIT 5;"
# Expected: hostname column populated
```

---

### Task 4: Add Model Versioning

**Files:** `src/adaptive_retrain.py`

**Problem:** Setiap retraining overwrite `.pkl` files. Tidak ada version history. Tidak bisa rollback.

**Fix:**

Tambahkan di `src/adaptive_retrain.py`, **sebelum** baris `joblib.dump(...)`:

```python
import shutil
import json
from datetime import datetime

# === MODEL VERSIONING ===
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
archive_dir = "models/archive"
os.makedirs(archive_dir, exist_ok=True)

# Backup model lama (jika ada)
for f in ["isolation_forest_baseline.pkl", "scaler_baseline.pkl", "feature_columns.pkl"]:
    src = f"models/{f}"
    if os.path.exists(src):
        dst = f"{archive_dir}/{f.replace('.pkl', f'_{timestamp}.pkl')}"
        shutil.copy2(src, dst)
        print(f"[VERSION] Backed up {f} → {dst}")

# Simpan training metadata
anomaly_ratio = float((pred == -1).sum()) / len(pred) if len(pred) > 0 else 0
metadata = {
    "version": timestamp,
    "train_samples": int(len(X)),
    "contamination": 0.05,
    "feature_columns": df_clean.columns.tolist(),
    "training_anomaly_ratio": round(anomaly_ratio, 4),
    "data_window": "30 minutes"
}
metadata_path = f"{archive_dir}/metadata_{timestamp}.json"
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"[VERSION] Saved metadata → {metadata_path}")

# === SELESAI VERSIONING, LANJUT KE OVERWRITE ===
joblib.dump(model, "models/isolation_forest_baseline.pkl")
joblib.dump(scaler, "models/scaler_baseline.pkl")
joblib.dump(df_clean.columns.tolist(), "models/feature_columns.pkl")
```

**Verification:**
```bash
# Jalankan retraining
source ragavenv/bin/activate
python src/adaptive_retrain.py

# Cek archive
ls -la models/archive/
# Expected: isolation_forest_baseline_*.pkl, scaler_baseline_*.pkl, feature_columns_*.pkl, metadata_*.json

# Cek metadata
cat models/archive/metadata_*.json | python -m json.tool
# Expected: valid JSON with version, train_samples, anomaly_ratio

# Jalankan lagi — cek ada 2 versi
python src/adaptive_retrain.py
ls models/archive/*.pkl | wc -l
# Expected: 6 (3 files × 2 runs)
```

---

### Task 5: Add Monitoring Logging

**Files:** `src/anomaly_inference.py`, `src/adaptive_retrain.py`

**Problem:** Monitoring metrics (anomaly ratio, latency, count) tidak diimplementasi.

**Fix di `src/anomaly_inference.py` — bungkus prediction dengan timing:**

```python
import time

# ... (sebelum prediksi) ...
start_time = time.time()

X = scaler.transform(df)
pred = model.predict(X)

latency_ms = (time.time() - start_time) * 1000
anomaly_flags = pred == -1
anomaly_count = int(anomaly_flags.sum())
total_rows = len(anomaly_flags)
ratio = anomaly_count / total_rows if total_rows > 0 else 0.0

print(f"[MONITOR] inference_latency_ms={latency_ms:.1f} anomaly_ratio={ratio:.3f} anomaly_count={anomaly_count} total_rows={total_rows}")
```

**Fix di `src/adaptive_retrain.py` — log training metrics:**

```python
# ... (setelah model.fit(X)) ...
import time

# Training info
print(f"[MONITOR] retrain_samples={len(X)} features={df_clean.columns.tolist()} contamination=0.05")
```

**Verification:**
```bash
# Jalankan inference
python src/anomaly_inference.py
# Expected output: [MONITOR] inference_latency_ms=XX.X anomaly_ratio=X.XXX ...

# Jalankan retraining
python src/adaptive_retrain.py
# Expected output: [MONITOR] retrain_samples=XXX ...
```

---

### Task 6: Clarify Addendum Status

**File:** Dokumen MT-018 (Markdown)

**Problem:** Section 9 "System Status" menyatakan "COMPLETED" tapi Addendum v1.2.0 belum diimplementasi. Status misleading.

**Fix — Update Section 9 di MT-018 Main Spec:**

Ganti Section 9 menjadi:

```markdown
# 9. System Status

## Completed (Baseline)
* Environment Setup
* Dataset Preparation (server_compute features)
* Baseline Model Development (Isolation Forest)
* Model Benchmarking
* Model Packaging (3 artifacts)
* Adaptive Retraining (30-min rolling window)
* Hardening (credentials, dedup, hostname, versioning, monitoring)

## In Progress / Planned (per Addendum v1.2.0)
* [ ] Feature group expansion: server_health, power_metrics, environment_metrics, capacity_metrics
* [ ] MetricSource abstract loader (Section 11.3)
* [ ] Forecasting pipeline: Prophet / XGBoost / LSTM (Section 11.4)
* [ ] Supervised labeling: failure_events table (Section 11.5)
* [ ] Imputation & noise handling per-feature (Section 11.6)
* [ ] Model registry (MLflow / DVC)
* [ ] Alerting integration (Telegram / email)
* [ ] Dashboard integration (Grafana)
```

**Verification:**
```bash
# Cek tidak ada "COMPLETED" tanpa context
grep -n "COMPLETED" path/to/MT-018_Traditional_Machine_Learning_Model.md
# Expected: "Completed (Baseline)" saja, bukan "COMPLETED" bare
```

---

### Task 7: Add Basic Cron Scheduling

**Files:** Crontab entry

**Problem:** Semua script di-run manual. Tidak ada automation.

**Fix:**

```bash
# Edit crontab
crontab -e

# Tambahkan entries:
# Inference setiap 5 menit
*/5 * * * * cd /path/to/project && source ragavenv/bin/activate && python src/anomaly_inference.py >> logs/inference.log 2>&1

# Adaptive retraining setiap 30 menit
*/30 * * * * cd /path/to/project && source ragavenv/bin/activate && python src/adaptive_retrain.py >> logs/retrain.log 2>&1

# Buat log directory
mkdir -p /path/to/project/logs
```

> **Ganti `/path/to/project`** dengan path aktual project root.

**Verification:**
```bash
crontab -l
# Expected: 2 entries visible

# Cek log directory
ls -la logs/
```

---

## 6. Tasks — P3 MEDIUM (Optional, bisa dikerjakan nanti)

### Task 8: Fix Typo

**File:** Config Documentation (markdown)

- Section 8: "Congfiguration" → "Configuration"
- Section 12: `adaptive_retraining.py` → `adaptive_retrain.py`

### Task 9: Add `.gitignore`

**File:** `.gitignore` (buatan baru jika belum ada)

```
.env
models/*.pkl
models/archive/
__pycache__/
*.pyc
logs/
.venv/
ragavenv/
```

---

## 7. Execution Order

```
1. Task 1  (credentials)     ← Fix dulu, semua script dependent
2. Task 9  (.gitignore)      ← Proteksi secrets
3. Task 3  (hostname)        ← Schema change dulu
4. Task 2  (dedup)           ← Setelah schema ready
5. Task 4  (versioning)      ← Retraining script
6. Task 5  (monitoring)      ← Logging di inference + retrain
7. Task 6  (status clarify)  ← Documentation update
8. Task 7  (cron)            ← Terakhir, after semua script fixed
9. Task 8  (typo)            ← Optional
```

---

## 8. Success Criteria

Semua task selesai jika:

- [ ] `grep -rn "infra:password" notebooks/ src/` → **no output**
- [ ] `.env` exists with `DCIM_DB_URL`
- [ ] `python -c "from dotenv import load_dotenv"` → **OK**
- [ ] `psql -U infra -d dcim_ai -c "\d server_anomalies"` → **hostname column exists**
- [ ] `python src/anomaly_inference.py` runs → **[MONITOR] output visible**
- [ ] `python src/anomaly_inference.py` run 2x → **no duplicate rows**
- [ ] `python src/adaptive_retrain.py` → **archive files created**
- [ ] `ls models/archive/metadata_*.json` → **valid JSON**
- [ ] `crontab -l` → **2 entries visible**
- [ ] MT-018 Section 9 → **"Completed (Baseline)" not bare "COMPLETED"**

---

## 9. Rollback Plan

Jika ada masalah setelah perubahan:

```python
# Rollback credentials: kembalikan hardcoded engine di semua script
# Rollback dedup: hapus DELETE logic, kembalikan if_exists="append"
# Rollback versioning: hapus shutil + metadata logic
# Rollback hostname: ALTER TABLE server_anomalies DROP COLUMN hostname
# Rollback cron: crontab -e, hapus 2 entries
```

**Database rollback (jika perlu):**
```sql
-- Hapus primary key constraint
ALTER TABLE server_anomalies DROP CONSTRAINT IF EXISTS server_anomalies_pkey;

-- Hapus hostname column
ALTER TABLE server_anomalies DROP COLUMN IF EXISTS hostname;
```

---

## 10. Notes

- **Path adjustment:** Ganti `/path/to/project` di cron entries dengan path aktual.
- **Password:** Ganti `YOUR_ACTUAL_PASSWORD` di `.env` dengan password database yang benar.
- **Python version:** Pastikan `ragavenv` sudah aktif sebelum jalankan script.
- **Dependencies:** `python-dotenv` harus install di venv.
- **Backup:** Sebelum mulai, backup `models/` directory: `cp -r models/ models_backup_$(date +%Y%m%d)/`
