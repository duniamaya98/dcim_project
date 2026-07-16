# DCIM Analytics & AI Engine — Deployment & Usage Guide

> **Last Updated:** 15 Juli 2026
> **Status:** ✅ Database ready, code patched, ready to deploy

---

## Ringkasan Pekerjaan

### Background
Tim AI (Syauqi) deploy API Block 7 dan melaporkan endpoint Anomalies & Predictions mengembalikan array kosong `[]`. Setelah investigasi, akar masalahnya adalah tabel-tabel analytics belum dibuat di TimescaleDB — bukan pipeline ingestion yang bermasalah (metrics table punya 1.76 juta baris).

### Yang Sudah Dikerjakan

| # | Item | Status |
|---|------|--------|
| 1 | **Migrasi database** — 9 tabel analytics dibuat | ✅ Selesai (Syauqi/DBA) |
| 2 | **Silent error handling** — `return []` diganti `raise HTTPException(500)` | ✅ Selesai |
| 3 | **Column mismatch predictions** — 5 mismatch query vs schema | ✅ Selesai |
| 4 | **Capacity GET** — dari TODO hardcoded `[]` jadi query penuh | ✅ Selesai |
| 5 | **Dokumentasi Syauqi** — 3 file diupdate dengan gap analysis | ✅ Selesai |
| 6 | **Metric name alignment** — semua router diselaraskan ke standar pipeline Syauqi | ✅ Selesai |
| 7 | **Query window adjustment** — diperlonggar ke 6 jam (temporary, menunggu poller real-time) | ✅ Selesai |
| 8 | **Stream processor reconnect** — fix `connection already closed` (by Syauqi) | ✅ Selesai |

### File yang Dipatch

```
implementation/dcim_ai_v2_rag/api/routers/anomalies.py    — silent error fix + metric names + window 6h
implementation/dcim_ai_v2_rag/api/routers/predictions.py   — silent error + column mismatch + metric names + window 6h
implementation/dcim_ai_v2_rag/api/routers/capacity.py      — full GET implementation + metric names
implementation/dcim_ai_v2_rag/api/routers/energy.py        — sudah proper error handling dari awal
reference_docs/Syauqi/gap-analysis-for-syauqi.md           — gap analysis doc
```

### Metric Name Mapping (API → Pipeline Syauqi)

| API (sebelum) | Pipeline Syauqi (sekarang) | Ada di DB? |
|---|---|---|
| `cpu_usage` | `cpu_utilization` | ⏳ belum muncul di pipeline |
| `disk_io` / `disk_usage` | `disk_temperature` | ✅ 979K baris (value 21–43°C) |
| `net_rx` / `net_tx` / `network_bandwidth` | `interface_status` | ✅ 5.2M baris (value 1–6) |
| — (baru) | `battery_capacity` | ✅ 15K baris (value 100%) |
| — (baru) | `inventory_snapshot` | ✅ 4.3K baris |
| `memory_usage` | `memory_usage` | ❌ belum ada di pipeline |
| `total_facility_power` | — | ❌ belum ada di pipeline (energy.py) |
| `it_equipment_power` | — | ❌ belum ada di pipeline (energy.py) |

---

## Prasyarat Deploy

### Environment Variables

```bash
export TIMESCALEDB_HOST=10.70.0.56
export TIMESCALEDB_PORT=5433
export TIMESCALEDB_DATABASE=dcim_analytics
export TIMESCALEDB_USER=ai_team
export TIMESCALEDB_PASSWORD=Inovasi@0918              # ⚠️ pastikan sinkron dengan dokumen Syauqi
export LLAMA_SERVER_URL=http://localhost:8080/v1/chat/completions  # LLM (opsional)
```

### Database — Tabel yang Tersedia

| Tabel | Baris | Fungsi |
|-------|-------|--------|
| `metrics` | 27,680,000+ | Raw time-series (hypertable) |
| `metrics_hourly` | — | Hourly aggregate (continuous) |
| `metrics_daily` | — | Daily aggregate (continuous) |
| `anomaly_events` | 0 | Hasil deteksi anomali |
| `predictions` | 0 | Hasil prediksi kegagalan |
| `rca_reports` | 0 | Laporan Root Cause Analysis |
| `capacity_forecasts` | 0 | Laporan forecasting kapasitas |
| `energy_reports` | 0 | Laporan optimasi energi |
| `ml_models` | 0 | Registri model ML |
| `model_drift_tracking` | 0 | Monitoring drift model |
| `audit_log` | 0 | Audit trail |

> Kolom `anomaly_events` dan `predictions` sudah diverifikasi 1:1 cocok dengan query di API router.

---

## Cara Menjalankan API

### 1. Aktivasi Virtual Environment

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
source /home/infra/dcim_project/ragavenv/bin/activate
```

### 2. Set Environment

```bash
export TIMESCALEDB_HOST=10.70.0.56
export TIMESCALEDB_PORT=5433
export TIMESCALEDB_DATABASE=dcim_analytics
export TIMESCALEDB_USER=ai_team
export TIMESCALEDB_PASSWORD=Inovasi@0918
```

### 3. Jalankan Server

```bash
python -m api.main
# atau:
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### 4. Verifikasi

```bash
curl http://localhost:8000/health
# {"status":"healthy","timestamp":"...","version":"1.0.0","service":"analytics-ai-engine"}

curl http://localhost:8000/api/v1/health
# {"status":"healthy","components":{"database":"healthy","api":"healthy"}}
```

### 5. Swagger UI

Buka browser ke:
```
http://<server-ip>:8000/api/v1/docs
```

---

## Panduan Penggunaan — Per Endpoint

### 1. Anomaly Detection

**Prefix:** `/api/v1/analytics/anomalies`

| Method | Path | Fungsi | Kapan Dipakai |
|--------|------|--------|---------------|
| `POST` | `/detect` | Deteksi anomali real-time dengan Z-score | Setiap kali mau cek apakah suatu metric lagi abnormal |
| `GET` | `` | List semua anomali yang pernah terdeteksi | Dashboard monitoring, lihat history anomali |
| `GET` | `/{anomaly_id}` | Detail satu anomali | Investigasi insiden spesifik |
| `GET` | `/seasonal` | Dekomposisi seasonal (STL-like) | Analisis pola musiman metric |

**Contoh: Trigger Deteksi**

```bash
curl -X POST http://localhost:8000/api/v1/analytics/anomalies/detect \
  -H "Content-Type: application/json" \
  -d '{"metric_name": "cpu_utilization", "ci_id": "550e8400-e29b-41d4-a716-446655440000", "zscore_threshold": 3.0}'
```

**Response (jika normal):**
```json
{
  "metric_name": "cpu_utilization",
  "is_anomaly": false,
  "zscore": 1.23,
  "severity": "low",
  "anomaly_score": 0.12,
  "source": "timescaledb",
  "expected_range": [30.5, 75.2],
  "sample_size": 100
}
```

**Response (jika anomali):**
```json
{
  "anomaly_id": "abc-123-def",
  "metric_name": "cpu_utilization",
  "is_anomaly": true,
  "zscore": 5.67,
  "severity": "critical",
  "stored": true
}
```

### 2. Predictive Maintenance

**Prefix:** `/api/v1/analytics/predictions`

| Method | Path | Fungsi | Kapan Dipakai |
|--------|------|--------|---------------|
| `POST` | `/forecast` | Forecast probabilitas kegagalan (IF/LOF/OCSVM ensemble) | Maintenance prediktif, cek kesehatan CI |
| `GET` | `` | List semua prediksi yang pernah dibuat | Dashboard, trend analysis |

**Contoh: Trigger Forecast**

```bash
curl -X POST http://localhost:8000/api/v1/analytics/predictions/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "ci_id": "550e8400-e29b-41d4-a716-446655440000",
    "metric_names": ["cpu_utilization", "memory_usage", "disk_temperature", "interface_status", "battery_capacity"]
  }'
```

**Response:**
```json
{
  "prediction_id": "def-456-ghi",
  "failure_probability": 0.12,
  "confidence": 0.78,
  "severity": "normal",
  "model_votes": {
    "isolation_forest": 1,
    "local_outlier_factor": 1,
    "one_class_svm": 1,
    "anomaly_votes": 0
  },
  "contributing_factors": [],
  "recommendation": "NORMAL: No failure indicators detected. Routine monitoring sufficient."
}
```

### 3. Root Cause Analysis

**Prefix:** `/api/v1/analytics/rca`

| Method | Path | Fungsi | Kapan Dipakai |
|--------|------|--------|---------------|
| `POST` | `/analyze` | Trigger RCA analysis | Setelah anomali terdeteksi, cari akar penyebab |
| `GET` | `/{incident_id}` | Detail laporan RCA | Investigasi insiden |
| `GET` | `/history` | Riwayat RCA | Audit, pattern analysis |

**Contoh: Trigger RCA**

```bash
curl -X POST http://localhost:8000/api/v1/analytics/rca/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC-20260715-001",
    "ci_id": "550e8400-e29b-41d4-a716-446655440000",
    "active_domains": ["server", "network", "storage", "power", "cooling"],
    "timeframe_minutes": 60,
    "mode": "reactive"
  }'
```

**Response:**
```json
{
  "incident_id": "INC-20260715-001",
  "root_cause": "server.cpu_utilization",
  "confidence": 0.68,
  "causal_chain": ["high_cpu -> thermal_throttle -> performance_degradation"],
  "ranked_domains": ["server", "cooling", "power"],
  "domain_probabilities": {"server": 0.68, "cooling": 0.22, "power": 0.10}
}
```

### 4. Capacity Forecasting

**Prefix:** `/api/v1/analytics/capacity`

| Method | Path | Fungsi | Kapan Dipakai |
|--------|------|--------|---------------|
| `POST` | `/forecast` | Forecast kapasitas dengan linear regression | Perencanaan kapasitas, budgeting |
| `GET` | `` | List laporan kapasitas | Dashboard, trend analysis |

**Contoh: Trigger Forecast**

```bash
curl -X POST http://localhost:8000/api/v1/analytics/capacity/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "ci_id": "550e8400-e29b-41d4-a716-446655440000",
    "metric_name": "cpu_utilization",
    "forecast_days": 90
  }'
```

**Response:**
```json
{
  "report_id": "cap-550e8400-cpu_utilization-20260715140000",
  "current_value": 52.30,
  "predicted_value_30d": 58.30,
  "predicted_value_60d": 64.30,
  "predicted_value_90d": 70.30,
  "trend": "increasing",
  "exhaustion_date": "2026-11-20",
  "recommendation": "OK: cpu_utilization stable at 70.3% in 90 days."
}
```

### 5. Energy Optimization

**Prefix:** `/api/v1/analytics/energy`

| Method | Path | Fungsi | Kapan Dipakai |
|--------|------|--------|---------------|
| `GET` | `/pue` | Hitung PUE (Power Usage Effectiveness) | Monitoring efisiensi energi |
| `POST` | `/optimize` | Rekomendasi optimasi energi | Menekan biaya listrik, target PUE |

**Contoh: Cek PUE**

```bash
curl "http://localhost:8000/api/v1/analytics/energy/pue?datacenter_id=dc-001"
```

**Response:**
```json
{
  "datacenter_id": "dc-001",
  "pue": 1.50,
  "total_power_kw": 150.00,
  "it_power_kw": 100.00,
  "cooling_power_kw": 50.00,
  "rating": "good",
  "recommendations": ["Good PUE. Fine-tune cooling schedules..."],
  "estimated_monthly_cost_usd": 10800.00
}
```

### 6. Model Registry

**Prefix:** `/api/v1/analytics/models`

| Method | Path | Fungsi | Kapan Dipakai |
|--------|------|--------|---------------|
| `GET` | `` | List model terdaftar | Cek model apa saja yang available |
| `POST` | `` | Register model baru | Setelah training model baru |
| `GET` | `/{model_name}` | Detail model | Cek metrik, versi, status |
| `PUT` | `/{model_name}/deploy` | Deploy model ke production | Aktivasi model setelah staging |

### 7. LLM/RAG

**Prefix:** `/api/v1/analytics/llm`

| Method | Path | Fungsi | Kapan Dipakai |
|--------|------|--------|---------------|
| `POST` | `/query` | Tanya natural language ke LLM | Debugging, eksplorasi data |
| `POST` | `/explain` | Jelaskan anomali dalam bahasa natural | Investigasi insiden |

**Contoh: Tanya LLM**

```bash
curl -X POST http://localhost:8000/api/v1/analytics/llm/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Apa penyebab paling umum CPU usage tinggi di server?"}'
```

> LLM menggunakan Gemma 4 12B via llama-server di port 8080. Jika llama-server tidak tersedia, fallback ke template response.

---

## Cara Testing Cepat

### Menggunakan Test Script Bawaan

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
source /home/infra/dcim_project/ragavenv/bin/activate

# Test semua endpoint
python scripts/test_api_endpoints.py

# Test group spesifik
python scripts/test_api_endpoints.py --group anomalies
python scripts/test_api_endpoints.py --group rca

# Custom base URL
python scripts/test_api_endpoints.py --base-url http://192.168.100.35:8000
```

### Smoke Test Manual (5 endpoint utama)

```bash
BASE="http://localhost:8000"

# 1. Health check
curl -s "$BASE/health" | python -m json.tool

# 2. Anomaly detection
curl -s -X POST "$BASE/api/v1/analytics/anomalies/detect" \
  -H "Content-Type: application/json" \
  -d '{"metric_name":"cpu_utilization"}' | python -m json.tool

# 3. Predictive forecast
curl -s -X POST "$BASE/api/v1/analytics/predictions/forecast" \
  -H "Content-Type: application/json" \
  -d '{"ci_id":"550e8400-e29b-41d4-a716-446655440000"}' | python -m json.tool

# 4. RCA analysis
curl -s -X POST "$BASE/api/v1/analytics/rca/analyze" \
  -H "Content-Type: application/json" \
  -d '{"incident_id":"SMOKE-001","ci_id":"550e8400-e29b-41d4-a716-446655440000"}' | python -m json.tool

# 5. PUE check
curl -s "$BASE/api/v1/analytics/energy/pue?datacenter_id=dc-001" | python -m json.tool
```

---

## Verifikasi Database

```bash
PGPASSWORD=Inovasi@0918 psql -h 10.70.0.56 -p 5433 -U ai_team -d dcim_analytics

# Cek semua tabel
\dt

# Cek data metrics
SELECT COUNT(*) FROM metrics;
SELECT metric_name, COUNT(*) FROM metrics GROUP BY metric_name ORDER BY 2 DESC LIMIT 10;

# Cek tabel analytics (harus 0 — belum ada data hasil API)
SELECT COUNT(*) FROM anomaly_events;
SELECT COUNT(*) FROM predictions;
SELECT COUNT(*) FROM rca_reports;
SELECT COUNT(*) FROM capacity_forecasts;

# Cek permission ai_team
SELECT table_schema, table_name, privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'ai_team' AND table_schema = 'public'
ORDER BY table_name, privilege_type;
```

---

## Arsitektur

```
Sources (Server/CCTV/NAS/UPS/Network)
    │
    ▼
NiFi (Ingestion Pollers)
    │
    ▼
Kafka (dcim.analytics.metrics — JSON, port 9094 SSL)
    │
    ▼
Stream Processor + Analytics Bridge
    │
    ▼
TimescaleDB: metrics (1.76M baris)
    │
    ▼
┌─────────────────────────────────────────────┐
│  API Analytics (FastAPI, port 8000)         │
│                                             │
│  /anomalies  ──▶ anomaly_events             │
│  /predictions ─▶ predictions                │
│  /rca        ──▶ rca_reports                │
│  /capacity   ──▶ capacity_forecasts         │
│  /energy     ──▶ energy_reports             │
│  /models     ──▶ ml_models                  │
│  /llm        ──▶ Gemma 4 12B (port 8080)    │
│                                             │
│  Tim AI consume hasil dari tabel output     │
└─────────────────────────────────────────────┘
```

---

## Troubleshooting

### API return 500 — "relation does not exist"

Penyebab: tabel analytics belum dibuat. Verifikasi:
```bash
PGPASSWORD=Inovasi@0918 psql -h 10.70.0.56 -p 5433 -U ai_team -d dcim_analytics -c "\dt"
```
Seharusnya muncul 9 tabel. Jika kurang, jalankan migration `002_create_analytics_tables.sql` oleh `analytics_user`.

### API return `source: synthetic` padahal data ada di DB

Penyebab: data di TimescaleDB ada (27M+ baris) tapi lebih dari X jam yang lalu — window query API tidak menjangkau. Atau metric name mismatch.
Solusi:
1. Cek metric name yang digunakan sudah sesuai pipeline: `cpu_utilization`, `disk_temperature`, `interface_status`, `battery_capacity`
2. Cek data terbaru: `SELECT metric_name, MAX(time) FROM metrics WHERE metric_name = '<name>' GROUP BY metric_name;`
3. Saat ini window query di-set ke 6 jam sebagai temporary measure. Begitu poller real-time stabil, akan dikembalikan ke 5 menit.

> **Status terkini (16 Juli 2026):** Stream processor reconnect sudah fix, tapi poller upstream belum push data P1 secara konsisten. API window di 6 jam — akan auto-switch ke `source: timescaledb` begitu data fresh masuk.

### API return 503 — "Database connection failed"

Penyebab: salah environment variables. Cek:
```bash
echo $TIMESCALEDB_HOST $TIMESCALEDB_PORT $TIMESCALEDB_DATABASE $TIMESCALEDB_USER
```
Pastikan semua terisi. Password terbaru: `Inovasi@0918`.

### LLM query fallback ke template

Penyebab: llama-server tidak running. Cek:
```bash
curl http://localhost:8080/v1/chat/completions
```
Jika gagal, LLM akan otomatis fallback ke template response — API tetap berfungsi.

---

## Referensi

| Dokumen | Path |
|---------|------|
| API Main | `implementation/dcim_ai_v2_rag/api/main.py` |
| Config | `implementation/dcim_ai_v2_rag/api/config.py` |
| Migration SQL | `implementation/dcim_ai_v2_rag/migrations/002_create_analytics_tables.sql` |
| Test Script | `implementation/dcim_ai_v2_rag/scripts/test_api_endpoints.py` |
| Gap Analysis | `reference_docs/Syauqi/gap-analysis-for-syauqi.md` |
| Dokumen Syauqi | `reference_docs/Syauqi/ai-team-access.md` |
| Dokumen Syauqi | `reference_docs/Syauqi/ai-pipeline-architecture.md` |
