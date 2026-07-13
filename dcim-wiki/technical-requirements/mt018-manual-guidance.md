# MT-018 Hardening — Manual Step-by-Step Guidance

> **Project path:** `/home/infra/dcim_project`
> **Virtual env:** `ragavenv`
> **Database:** PostgreSQL 16 + TimescaleDB (dcim_ai, user=infra, host=127.0.0.1)
> **Dedup method:** Opsi A (code-level DELETE before INSERT)
> **Date:** 2026-06-25

---

## Sebelum Mulai — Backup

```bash
cd /home/infra/dcim_project

# Backup seluruh project
cp -r . ../dcim_project_backup_$(date +%Y%m%d_%H%M%S)

# Backup models
cp -r models/ models_backup_$(date +%Y%m%d_%H%M%S)/

# Aktifkan venv
source ragavenv/bin/activate

# Install python-dotenv (dependency baru untuk Task 1)
pip install python-dotenv
```

---

# ═══════════════════════════════════════
# P1 — CRITICAL (Selesaikan ini dulu)
# ═══════════════════════════════════════

---

## Step 1: Buat File `.env`

```bash
cat > /home/infra/dcim_project/.env << 'EOF'
DCIM_DB_URL=postgresql+psycopg2://infra:YOUR_PASSWORD@127.0.0.1/dcim_ai
EOF
```

**Ganti `YOUR_PASSWORD`** dengan password PostgreSQL yang kamu tahu.

**Verifikasi:**
```bash
cat /home/infra/dcim_project/.env
# Harus menampilkan DCIM_DB_URL dengan password kamu (bukan "YOUR_PASSWORD")
```

---

## Step 2: Buat File `.env.example`

```bash
cat > /home/infra/dcim_project/.env.example << 'EOF'
# Database URL for DCIM AI Pipeline
# Copy this file to .env and fill in your actual password
DCIM_DB_URL=postgresql+psycopg2://infra:CHANGE_ME@127.0.0.1/dcim_ai
EOF
```

**Verifikasi:**
```bash
cat /home/infra/dcim_project/.env.example
# Harus menampilkan placeholder, bukan password asli
```

---

## Step 3: Buat/Update `.gitignore`

```bash
cat > /home/infra/dcim_project/.gitignore << 'EOF'
# Secrets
.env

# Model artifacts
models/*.pkl
models/archive/
models_backup_*/

# Python
__pycache__/
*.pyc
*.pyo
.venv/
ragavenv/

# Logs
logs/
*.log

# Backups
*_backup_*/
EOF
```

**Verifikasi:**
```bash
cat /home/infra/dcim_project/.gitignore
# Harus ada .env, models/*.pkl, ragavenv/
```

---

## Step 4: Fix `notebooks/dataset_preparation.py`

Buka file `notebooks/dataset_preparation.py` dan buat perubahan berikut:

### 4a. Tambah imports di baris paling atas

**SEBELUM (baris 1-7):**
```python
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
import numpy as np
import joblib
import os
```

**SESUDAH (ganti seluruh blok):**
```python
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import IsolationForest
import numpy as np
import joblib
import os
from dotenv import load_dotenv

load_dotenv()
```

### 4b. Ganti baris `engine = create_engine(...)`

**SEBELUM:**
```python
engine = create_engine(
"postgresql+psycopg2://infra:password@127.0.0.1/dcim_ai"
)
```

**SESUDAH (ganti dengan):**
```python
DB_URL = os.environ.get("DCIM_DB_URL")
if not DB_URL:
    raise EnvironmentError(
        "DCIM_DB_URL not set. Copy .env.example to .env and configure."
    )
engine = create_engine(DB_URL)
```

**Verifikasi:**
```bash
# Pastikan tidak ada hardcoded password
grep -n "infra:password" /home/infra/dcim_project/notebooks/dataset_preparation.py
# Expected: no output (kosong)

# Pastikan ada import dotenv
grep -n "dotenv" /home/infra/dcim_project/notebooks/dataset_preparation.py
# Expected: 2 baris (import + load_dotenv)
```

---

## Step 5: Fix `src/anomaly_inference.py`

Buka file `src/anomaly_inference.py` dan buat perubahan berikut:

### 5a. Tambah imports di baris paling atas

**SEBELUM (baris 1-3):**
```python
import pandas as pd
import joblib
from sqlalchemy import create_engine
```

**SESUDAH (ganti dengan):**
```python
import pandas as pd
import joblib
import time
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()
```

> **Catatan:** Tambah `time` (untuk monitoring latency) dan `text` (untuk raw SQL query dedup).

### 5b. Ganti baris `engine = create_engine(...)`

**SEBELUM:**
```python
engine = create_engine(
"postgresql+psycopg2://infra:password@127.0.0.1/dcim_ai"
)
```

**SESUDAH (ganti dengan):**
```python
DB_URL = os.environ.get("DCIM_DB_URL")
if not DB_URL:
    raise EnvironmentError(
        "DCIM_DB_URL not set. Copy .env.example to .env and configure."
    )
engine = create_engine(DB_URL)
```

### 5c. Ganti SELURUH bagian prediksi + write (dari baris `X = scaler.transform(df)` sampai akhir)

Cari baris:
```python
X = scaler.transform(df)

pred = model.predict(X)
```

Ganti **SEMUA** mulai dari baris `X = scaler.transform(df)` sampai **akhir file** dengan kode berikut:

```python
# === PREDICTION WITH MONITORING ===
start_time = time.time()

X = scaler.transform(df)
pred = model.predict(X)

latency_ms = (time.time() - start_time) * 1000

anomaly_flags = pred == -1
anomaly_count = int(anomaly_flags.sum())
total_rows = len(anomaly_flags)
ratio = anomaly_count / total_rows if total_rows > 0 else 0.0

# === DEDUP + WRITE ===
original_df = original_df.loc[df.index]
original_df["anomaly"] = anomaly_flags

output_df = original_df[
    ["time", "hostname", "cpu_usage", "memory_usage", "disk_io", "net_rx", "net_tx", "anomaly"]
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

    print(f"[INFERENCE] Wrote {len(output_df)} rows ({min_time} → {max_time})")
else:
    print("[INFERENCE] No data to write")

# === MONITORING ===
print(f"[MONITOR] inference_latency_ms={latency_ms:.1f} anomaly_ratio={ratio:.3f} anomaly_count={anomaly_count} total_rows={total_rows}")
```

> **Yang berubah:**
> 1. Tambah `time` import + `start_time` untuk ukur latency
> 2. `hostname` masuk ke output (sebelumnya tidak ada)
> 3. DELETE sebelum INSERT (dedup)
> 4. [MONITOR] logging

**Verifikasi:**
```bash
# Pastikan tidak ada hardcoded password
grep -n "infra:password" /home/infra/dcim_project/src/anomaly_inference.py
# Expected: no output

# Pastikan ada hostname di output columns
grep -n '"hostname"' /home/infra/dcim_project/src/anomaly_inference.py
# Expected: ada di output_df selection

# Pastikan ada DELETE query (dedup)
grep -n "DELETE FROM server_anomalies" /home/infra/dcim_project/src/anomaly_inference.py
# Expected: 1 match

# Pastikan ada [MONITOR] output
grep -n "MONITOR" /home/infra/dcim_project/src/anomaly_inference.py
# Expected: 1 match

# Pastikan ada import text
grep -n "from sqlalchemy import" /home/infra/dcim_project/src/anomaly_inference.py
# Expected: "from sqlalchemy import create_engine, text"
```

---

## Step 6: Fix `src/adaptive_retrain.py`

Buka file `src/adaptive_retrain.py` dan buat perubahan berikut:

### 6a. Tambah imports di baris paling atas

**SEBELUM (baris 1-5):**
```python
import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
```

**SESUDAH (ganti dengan):**
```python
import pandas as pd
import joblib
from sqlalchemy import create_engine
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import IsolationForest
import os
import shutil
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
```

### 6b. Ganti baris `engine = create_engine(...)`

**SEBELUM:**
```python
engine = create_engine(
"postgresql+psycopg2://infra:password@127.0.0.1/dcim_ai"
)
```

**SESUDAH (ganti dengan):**
```python
DB_URL = os.environ.get("DCIM_DB_URL")
if not DB_URL:
    raise EnvironmentError(
        "DCIM_DB_URL not set. Copy .env.example to .env and configure."
    )
engine = create_engine(DB_URL)
```

### 6c. Tambah model versioning SEBELUM baris `joblib.dump(model,...) pertama

Cari baris:
```python
joblib.dump(model,"models/isolation_forest_baseline.pkl")
joblib.dump(scaler,"models/scaler_baseline.pkl")
joblib.dump(df_clean.columns.tolist(),"models/feature_columns.pkl")
```

Tambahkan kode berikut **SEBELUM** baris `joblib.dump(model,...)` pertama:

```python
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
metadata = {
    "version": timestamp,
    "train_samples": int(len(X)),
    "contamination": 0.05,
    "feature_columns": df_clean.columns.tolist(),
    "data_window": "30 minutes"
}
metadata_path = f"{archive_dir}/metadata_{timestamp}.json"
with open(metadata_path, "w") as f:
    json.dump(metadata, f, indent=2)
print(f"[VERSION] Saved metadata → {metadata_path}")

# === LANJUT OVERWRITE ===
```

> **Catatan:** Baris `joblib.dump(...)` yang sudah ada tetap di bawah kode ini. Jadi urutannya jadi:
> 1. Kode versioning (backup + metadata)
> 2. `joblib.dump(model,...)` (overwrite)
> 3. `joblib.dump(scaler,...)` (overwrite)
> 4. `joblib.dump(feature_columns,...)` (overwrite)

**Verifikasi:**
```bash
# Pastikan tidak ada hardcoded password
grep -n "infra:password" /home/infra/dcim_project/src/adaptive_retrain.py
# Expected: no output

# Pastikan ada versioning code
grep -n "VERSION" /home/infra/dcim_project/src/adaptive_retrain.py
# Expected: 3+ matches (backup loop + metadata save)

# Pastikan ada archive dir creation
grep -n "archive_dir" /home/infra/dcim_project/src/adaptive_retrain.py
# Expected: 2+ matches
```

---

## P1 — Verifikasi Akhir

```bash
cd /home/infra/dcim_project
source ragavenv/bin/activate

# 1. Tidak ada hardcoded password di SEMUA script
echo "=== Check hardcoded credentials ==="
grep -rn "infra:password" notebooks/ src/
# Expected: no output

# 2. .env exists
echo "=== Check .env ==="
test -f .env && echo ".env EXISTS" || echo ".env MISSING"

# 3. dotenv bisa diimport
echo "=== Check dotenv import ==="
python -c "from dotenv import load_dotenv; print('dotenv OK')"

# 4. Script bisa diimport tanpa error
echo "=== Check script imports ==="
python -c "import sys; sys.path.insert(0,'notebooks'); exec(open('notebooks/dataset_preparation.py').read().split('engine')[0]); print('training imports OK')"
python -c "import sys; sys.path.insert(0,'src'); exec(open('src/anomaly_inference.py').read().split('engine')[0]); print('inference imports OK')"
python -c "import sys; sys.path.insert(0,'src'); exec(open('src/adaptive_retrain.py').read().split('engine')[0]); print('retrain imports OK')"
```

**Jika semua pass → P1 SELESAI. Lanjut ke P2.**

---

# ═══════════════════════════════════════
# P2 — HIGH (Setelah P1 selesai)
# ═══════════════════════════════════════

---

## Step 7: Update Database Schema — Tambah `hostname`

```bash
cd /home/infra/dcim_project
source ragavenv/bin/activate
```

Jalankan perintah SQL berikut via `psql`:

```bash
psql -U infra -d dcim_ai -h 127.0.0.1 << 'SQL'
-- Cek apakah column hostname sudah ada
SELECT column_name
FROM information_schema.columns
WHERE table_name = 'server_anomalies' AND column_name = 'hostname';
SQL
```

**Jika hasilnya kosong (belum ada):**
```bash
psql -U infra -d dcim_ai -h 127.0.0.1 << 'SQL'
-- Tambah hostname column
ALTER TABLE server_anomalies
    ADD COLUMN IF NOT EXISTS hostname TEXT;

-- Update existing rows: set hostname dari server_metrics yang paling dekat waktunya
UPDATE server_anomalies sa
SET hostname = (
    SELECT sm.hostname
    FROM server_metrics sm
    WHERE sm.time = sa.time
    LIMIT 1
)
WHERE sa.hostname IS NULL;

-- Tambah composite primary key
ALTER TABLE server_anomalies
    ADD CONSTRAINT server_anomalies_pkey PRIMARY KEY (time, hostname);
SQL
```

**Jika sudah ada (hasil query di atas menunjukkan hostname):**
```bash
psql -U infra -d dcim_ai -h 127.0.0.1 << 'SQL'
-- Pastikan primary key ada
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'server_anomalies_pkey'
    ) THEN
        ALTER TABLE server_anomalies
            ADD CONSTRAINT server_anomalies_pkey PRIMARY KEY (time, hostname);
    END IF;
END $$;
SQL
```

**Verifikasi:**
```bash
psql -U infra -d dcim_ai -h 127.0.0.1 -c "\d server_anomalies"
# Expected: hostname TEXT column visible, PRIMARY KEY (time, hostname)
```

---

## Step 8: Update Inference Script — Tambah Monitoring (sudah termasuk di Step 5)

> **Catatan:** Monitoring logging sudah ditambahkan di Step 5c. Tidak perlu perubahan tambahan.
> Cukup verifikasi:

```bash
grep -n "MONITOR" /home/infra/dcim_project/src/anomaly_inference.py
# Expected: "[MONITOR] inference_latency_ms=..."
```

---

## Step 9: Update MT-018 Document — Clarify Status

Buka file MT-018_Traditional_Machine_Learning_Model.md dan cari **Section 9: System Status**.

Ganti seluruh isi Section 9 dengan:

```markdown
# 9. System Status

## Completed (Baseline)
* Environment Setup
* Dataset Preparation (server_compute features)
* Baseline Model Development (Isolation Forest)
* Model Benchmarking
* Model Packaging (3 artifacts)
* Adaptive Retraining (30-min rolling window)
* Hardening (credentials externalized, dedup logic, hostname traceability, model versioning, monitoring logging)

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

**Verifikasi:**
```bash
grep -n "Completed (Baseline)" /home/infra/dcim_project/MT-018_Traditional_Machine_Learning_Model.md
# Expected: 1 match
```

---

## Step 10: Setup Cron Scheduling

```bash
cd /home/infra/dcim_project

# Buat log directory
mkdir -p logs

# Edit crontab
crontab -e
```

Tambahkan 2 baris berikut di akhir crontab:

```cron
# MT-018 Inference — setiap 5 menit
*/5 * * * * cd /home/infra/dcim_project && source ragavenv/bin/activate && python src/anomaly_inference.py >> logs/inference.log 2>&1

# MT-018 Adaptive Retraining — setiap 30 menit
*/30 * * * * cd /home/infra/dcim_project && source ragavenv/bin/activate && python src/adaptive_retrain.py >> logs/retrain.log 2>&1
```

> **Catatan:** Cron sudah terpasang tapi tidak akan jalan sampai data real ada. Script tetap bisa di-run manual.

**Verifikasi:**
```bash
crontab -l
# Expected: 2 entries terlihat

ls -la /home/infra/dcim_project/logs/
# Expected: logs/ directory exists
```

---

## P2 — Verifikasi Akhir

```bash
cd /home/infra/dcim_project
source ragavenv/bin/activate

# 1. Database schema check
echo "=== DB Schema ==="
psql -U infra -d dcim_ai -h 127.0.0.1 -c "\d server_anomalies"

# 2. Model versioning ready
echo "=== Archive dir ==="
mkdir -p models/archive
ls -la models/archive/

# 3. Cron check
echo "=== Cron ==="
crontab -l | grep -c "dcim_project"
# Expected: 2

# 4. Document status
echo "=== Doc Status ==="
grep "Completed (Baseline)" MT-018_Traditional_Machine_Learning_Model.md
```

**Jika semua pass → P2 SELESAI. Lanjut ke P3.**

---

# ═══════════════════════════════════════
# P3 — MEDIUM (Optional)
# ═══════════════════════════════════════

---

## Step 11: Fix Typo di Config Documentation

Buka file `MT-018_Traditional_ML_Model_Configuration_Documentation.md`.

### 11a. Fix "Congfiguration"

Cari (Ctrl+F):
```
Inference Congfiguration
```

Ganti dengan:
```
Inference Configuration
```

### 11b. Fix filename inconsistency

Cari (Ctrl+F):
```
adaptive_retraining.py
```

Ganti dengan:
```
adaptive_retrain.py
```

> **Hanya ganti di Section 12 (Configurasi Summary table).** Jangan ganti di Section 9 yang memang benar.

**Verifikasi:**
```bash
grep -n "Congfiguration" /home/infra/dcim_project/MT-018_Traditional_ML_Model_Configuration_Documentation.md
# Expected: no output (sudah diperbaiki)

grep -n "adaptive_retraining.py" /home/infra/dcim_project/MT-018_Traditional_ML_Model_Configuration_Documentation.md
# Expected: no output (sudah diganti ke adaptive_retrain.py)
```

---

## P3 — Verifikasi Akhir

```bash
echo "=== Typo check ==="
grep -rn "Congfiguration" /home/infra/dcim_project/
# Expected: no output

grep -rn "adaptive_retraining.py" /home/infra/dcim_project/
# Expected: no output
```

**Jika semua pass → P3 SELESAI. HARDENING SELESAI.**

---

# ═══════════════════════════════════════
# FINAL VERIFICATION — Semua Task
# ═══════════════════════════════════════

Jalankan checklist berikut:

```bash
cd /home/infra/dcim_project
source ragavenv/bin/activate

echo "========================================="
echo "MT-018 HARDENING — FINAL VERIFICATION"
echo "========================================="

# Task 1: Credentials externalized
echo ""
echo "[1/8] Credentials externalized"
RESULT=$(grep -rn "infra:password" notebooks/ src/ 2>/dev/null | wc -l)
if [ "$RESULT" -eq 0 ]; then
    echo "  ✅ PASS — No hardcoded credentials found"
else
    echo "  ❌ FAIL — Found $RESULT hardcoded credentials"
fi

# Task 2: .env exists
echo ""
echo "[2/8] .env file exists"
if [ -f .env ] && grep -q "DCIM_DB_URL" .env; then
    echo "  ✅ PASS — .env with DCIM_DB_URL"
else
    echo "  ❌ FAIL — .env missing or incomplete"
fi

# Task 3: dotenv importable
echo ""
echo "[3/8] python-dotenv installed"
python -c "from dotenv import load_dotenv" 2>/dev/null && echo "  ✅ PASS" || echo "  ❌ FAIL"

# Task 4: hostname in schema
echo ""
echo "[4/8] hostname column in server_anomalies"
psql -U infra -d dcim_ai -h 127.0.0.1 -t -c \
  "SELECT column_name FROM information_schema.columns WHERE table_name='server_anomalies' AND column_name='hostname'" 2>/dev/null | grep -q "hostname" && echo "  ✅ PASS" || echo "  ❌ FAIL"

# Task 5: dedup logic in inference
echo ""
echo "[5/8] Dedup logic (DELETE before INSERT)"
grep -q "DELETE FROM server_anomalies" src/anomaly_inference.py 2>/dev/null && echo "  ✅ PASS" || echo "  ❌ FAIL"

# Task 6: model versioning in retrain
echo ""
echo "[6/8] Model versioning in adaptive_retrain"
grep -q "archive_dir" src/adaptive_retrain.py 2>/dev/null && echo "  ✅ PASS" || echo "  ❌ FAIL"

# Task 7: monitoring logging
echo ""
echo "[7/8] Monitoring logging in inference"
grep -q "MONITOR" src/anomaly_inference.py 2>/dev/null && echo "  ✅ PASS" || echo "  ❌ FAIL"

# Task 8: doc status clarified
echo ""
echo "[8/8] MT-018 status clarified"
grep -q "Completed (Baseline)" MT-018_Traditional_Machine_Learning_Model.md 2>/dev/null && echo "  ✅ PASS" || echo "  ❌ FAIL"

echo ""
echo "========================================="
echo "VERIFICATION COMPLETE"
echo "========================================="
```

**Expected output:**
```
[1/8] Credentials externalized      ✅ PASS
[2/8] .env file exists              ✅ PASS
[3/8] python-dotenv installed        ✅ PASS
[4/8] hostname column               ✅ PASS
[5/8] Dedup logic                   ✅ PASS
[6/8] Model versioning              ✅ PASS
[7/8] Monitoring logging            ✅ PASS
[8/8] Doc status clarified          ✅ PASS
```

---

# ═══════════════════════════════════════
# ROLLBACK (Jika Ada Masalah)
# ═══════════════════════════════════════

```bash
cd /home/infra/dcim_project

# Restore dari backup
cp -r ../dcim_project_backup_*/notebooks/ notebooks/
cp -r ../dcim_project_backup_*/src/ src/
cp -r ../dcim_project_backup_*/models/ models/

# Hapus .env
rm -f .env

# Hapus cron
crontab -e  # hapus 2 entries

# Rollback database
psql -U infra -d dcim_ai -h 127.0.0.1 << 'SQL'
ALTER TABLE server_anomalies DROP CONSTRAINT IF EXISTS server_anomalies_pkey;
ALTER TABLE server_anomalies DROP COLUMN IF EXISTS hostname;
SQL
```

---

# ═══════════════════════════════════════
# REFERENSI CEPAT
# ═══════════════════════════════════════

| Step | File | Apa yang Diubah | Waktu Est. |
|------|------|-----------------|------------|
| 1 | `.env` | Buat baru — credentials | 1 menit |
| 2 | `.env.example` | Buat baru — template | 1 menit |
| 3 | `.gitignore` | Buat baru — proteksi | 1 menit |
| 4 | `notebooks/dataset_preparation.py` | Import + engine | 5 menit |
| 5 | `src/anomaly_inference.py` | Import + engine + dedup + hostname + monitoring | 15 menit |
| 6 | `src/adaptive_retrain.py` | Import + engine + versioning | 10 menit |
| 7 | Database | ALTER TABLE + PK | 5 menit |
| 8 | _(sudah di Step 5)_ | — | 0 menit |
| 9 | MT-018 doc | Update Section 9 | 5 menit |
| 10 | Crontab | 2 entries | 5 menit |
| 11 | Config doc | Fix typo | 2 menit |
| **Total** | | | **~50 menit** |
