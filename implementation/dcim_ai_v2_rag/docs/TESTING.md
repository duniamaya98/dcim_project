# Block 7 Analytics & AI Engine - Testing & Sample Data Guide

**Last Updated:** 2026-07-13  
**Status:** All endpoints verified working  
**API Server:** http://localhost:8000  
**Swagger UI:** http://localhost:8000/api/v1/docs

---

## 📋 Daftar Isi

1. [Quick Start (3 Langkah)](#quick-start-3-langkah)
2. [Sample Data Generator](#sample-data-generator)
3. [API Test Script](#api-test-script)
4. [Cara Test Per Endpoint](#cara-test-per-endpoint)
5. [Full Pipeline Test](#full-pipeline-test)
6. [Swagger UI (Interactive)](#swagger-ui-interactive)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Quick Start (3 Langkah)

### Langkah 1: Start API Server

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Langkah 2: Run Test Script

```bash
python3 scripts/test_api_with_sample_data.py
```

### Langkah 3: Buka Swagger UI

```
http://localhost:8000/api/v1/docs
```

---

## 🎰 Sample Data Generator

Lokasi: `scripts/generate_sample_data.py`

### Apa yang Di-generate

| Komponen | Detail |
|----------|--------|
| Servers | 8 server (srv-web-001, srv-app-001, srv-db-001, dll) |
| Metrics | 9 jenis (cpu, memory, disk, network, power, temperature, fan) |
| Time Range | 7 hari (configurable) |
| Interval | Per jam (configurable) |
| Anomaly Points | 5 injection points (spike & gradual) |
| Total Metrics | ~12,096 (7 hari × 24 jam × 8 server × 9 metrics) |

### Data yang Di-generate

```
Server Types:
  - web: srv-web-001, srv-web-002
  - app: srv-app-001, srv-app-002
  - database: srv-db-001, srv-db-002
  - cache: srv-cache-001
  - ml: srv-ml-001

Metric Types:
  - cpu_usage: % (range: 5-95)
  - memory_usage: % (range: 20-98)
  - disk_usage: % (range: 30-95)
  - disk_iops: iops (range: 100-10000)
  - network_rx_bytes: bytes/s (range: 1M-1B)
  - network_tx_bytes: bytes/s (range: 1M-500M)
  - power_consumption: watts (range: 50-500)
  - temperature: celsius (range: 18-45)
  - fan_speed: rpm (range: 1000-8000)

Anomaly Injections:
  - srv-web-001 / cpu_usage: Spike 2x pada hari ke-5
  - srv-db-001 / disk_usage: Gradual increase pada hari ke-7
  - srv-app-002 / memory_usage: Spike 1.8x pada hari ke-10
  - srv-cache-001 / temperature: Spike 1.6x pada hari ke-3
  - srv-ml-001 / power_consumption: Spike 1.7x pada hari ke-8
```

### Cara Pakai

#### Option A: Dry Run (Preview aja)

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag

# Preview data yang akan di-generate
python3 scripts/generate_sample_data.py --target dry

# Custom parameters
python3 scripts/generate_sample_data.py --target dry --days 3 --servers 2
```

**Output:**
```
Generating sample data...
  Target: dry
  Days: 3
  Servers: 2

Total metrics: 1296
Servers: srv-web-001, srv-web-002
Anomaly injections: 5 points

[DRY RUN] No data sent.
```

#### Option B: Kirim ke Kafka (Realistic Pipeline)

```bash
# Kirim ke Kafka (butuh Kafka running di 10.70.0.56:9092)
python3 scripts/generate_sample_data.py --target kafka --days 7

# Output:
# Sending 12096 metrics to Kafka topic 'dcim.analytics.metrics'...
#   Sent 100/12096 metrics...
#   Sent 200/12096 metrics...
#   ...
# ✅ Successfully sent 12096 metrics to Kafka
```

#### Option C: Insert Langsung ke TimescaleDB (Paling Cepat)

```bash
# Insert langsung ke DB (butuh TimescaleDB running di 10.70.0.56:5433)
python3 scripts/generate_sample_data.py --target timescaledb --days 7

# Output:
# Inserting 12096 metrics into TimescaleDB...
#   Inserted 100/12096 metrics...
#   Inserted 200/12096 metrics...
#   ...
# ✅ Successfully inserted 12096 metrics into TimescaleDB
```

### Parameter Lengkap

| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `--target` | `dry` | Target: `kafka`, `timescaledb`, `dry` |
| `--days` | `7` | Berapa hari data |
| `--interval` | `1` | Interval per jam |
| `--servers` | `8` | Berapa server |

---

## 🧪 API Test Script

Lokasi: `scripts/test_api_with_sample_data.py`

### Apa yang Di-test

Script ini test **semua endpoint** yang sudah work:

1. Health Check
2. Root Cause Analysis (3 skenario berbeda)
3. Capacity Forecasting (cpu, disk, memory)
4. PUE Calculation
5. Energy Optimization
6. List Anomalies
7. List Predictions
8. List Models

### Cara Pakai

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag

# Pastikan API server running dulu
uvicorn api.main:app --host 0.0.0.0 --port 8000 &

# Run test script
python3 scripts/test_api_with_sample_data.py
```

### Contoh Output

```
============================================================
  DCIM Analytics API - Sample Data Test
============================================================

Target: http://localhost:8000
Time: 2026-07-13T13:47:51.121361

============================================================
  1. Health Check
============================================================

Status: 200
{
  "status": "healthy",
  "version": "1.0.0",
  "service": "analytics-ai-engine"
}

============================================================
  2. Root Cause Analysis
============================================================

--- Server CPU Issue ---
Status: 200
Root Cause: power
Confidence: 23.35%
Domains: ['power', 'cooling', 'storage', 'server', 'network']

--- Network Latency Issue ---
Status: 200
Root Cause: storage
Confidence: 34.54%
Domains: ['storage', 'network', 'server']

--- Storage Full Issue ---
Status: 200
Root Cause: storage
Confidence: 51.35%
Domains: ['storage', 'server']

============================================================
  3. Capacity Forecasting
============================================================

--- srv-web-001 / cpu_usage ---
Status: 200
Current: 61.5%
30d: 67.42
60d: 72.7
90d: 77.98
Exhaustion: 2027-02-17
R²: 0.485
Rec: OK: cpu_usage stable at 78.0% in 90 days.

--- srv-db-001 / disk_usage ---
Status: 200
Current: 84.0%
30d: 89.15
60d: 96.35
90d: 103.56
Exhaustion: 2026-09-18
R²: 0.912
Rec: CRITICAL: disk_usage will reach 103.6% in 90 days.

--- srv-app-001 / memory_usage ---
Status: 200
Current: 85.7%
30d: 90.97
60d: 99.91
90d: 108.86
Exhaustion: 2026-08-30
R²: 0.883
Rec: CRITICAL: memory_usage will reach 108.9% in 90 days.

============================================================
  4. Energy Optimization
============================================================

--- PUE Calculation ---
Status: 200
PUE: 1.5
Rating: good
Total Power: 150.0 kW
IT Power: 100.0 kW
Cooling: 50.0 kW
Recommendations:
  • Good PUE. Fine-tune cooling schedules...
  • Consider LED lighting and occupancy sensors...

--- Optimization Recommendations ---
Status: 200
Current PUE: 1.5
Target PUE: 1.3
Savings: 13.3%
Monthly Savings: 14400 kWh
Actions:
  [HIGH] Raise cooling set points by 2°C
  [HIGH] Implement hot aisle containment
  [MEDIUM] Install variable speed drives on cooling fans

============================================================
  5. Anomalies & Predictions
============================================================

Anomalies: 200 → []
Predictions: 200 → []

============================================================
  6. Model Registry
============================================================

Models: 200 → []

============================================================
  Test Complete!
============================================================
```

---

## 🔍 Cara Test Per Endpoint

### 1. Health Check

```bash
curl http://localhost:8000/health
```

```json
{
  "status": "healthy",
  "timestamp": "2026-07-13T06:38:24.075991",
  "version": "1.0.0",
  "service": "analytics-ai-engine"
}
```

---

### 2. Root Cause Analysis

```bash
# Skenario 1: Server CPU Issue
curl -X POST http://localhost:8000/api/v1/analytics/rca/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "incident_id": "INC-001",
    "ci_id": "srv-web-001",
    "active_domains": ["server", "network", "storage", "power", "cooling"],
    "mode": "reactive"
  }'
```

```json
{
  "incident_id": "INC-001",
  "ci_id": "srv-web-001",
  "root_cause": "power",
  "confidence": 0.2335,
  "causal_chain": ["power"],
  "explanation": "power identified as primary root cause...",
  "ranked_domains": ["power", "cooling", "storage", "server", "network"],
  "domain_probabilities": {
    "power": 0.23,
    "cooling": 0.21,
    "storage": 0.20,
    "server": 0.18,
    "network": 0.18
  },
  "analysis_duration_seconds": 0.049
}
```

**Parameter:**
- `incident_id`: ID insiden (bebas)
- `ci_id`: ID server/perangkat
- `active_domains`: Domain yang dianalisis
- `mode`: "reactive", "forward", atau "hybrid"

---

### 3. Capacity Forecast

```bash
# CPU forecast
curl -X POST http://localhost:8000/api/v1/analytics/capacity/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "ci_id": "srv-web-001",
    "metric_name": "cpu_usage",
    "forecast_days": 30
  }'
```

```json
{
  "ci_id": "srv-web-001",
  "metric_name": "cpu_usage",
  "current_value": 61.5,
  "predicted_value_30d": 67.42,
  "predicted_value_60d": 72.7,
  "predicted_value_90d": 77.98,
  "trend": "increasing",
  "slope_per_day": 0.2401,
  "r_squared": 0.485,
  "exhaustion_date": "2027-02-17",
  "recommendation": "OK: cpu_usage stable at 78.0% in 90 days."
}
```

**Metric names:**
- `cpu_usage` - CPU utilization
- `memory_usage` - Memory utilization
- `disk_usage` - Disk space
- `network_bandwidth` - Network bandwidth
- `power_consumption` - Power consumption

---

### 4. PUE Calculation

```bash
curl "http://localhost:8000/api/v1/analytics/energy/pue?datacenter_id=dc-001"
```

```json
{
  "datacenter_id": "dc-001",
  "pue": 1.5,
  "total_power_kw": 150.0,
  "it_power_kw": 100.0,
  "cooling_power_kw": 50.0,
  "cooling_efficiency": 2.0,
  "rating": "good",
  "recommendations": [
    "Good PUE. Fine-tune cooling schedules to match load patterns.",
    "Consider LED lighting and occupancy sensors to reduce ancillary load."
  ]
}
```

**PUE Rating:**
| PUE | Rating |
|-----|--------|
| ≤ 1.2 | excellent |
| 1.2 - 1.5 | good |
| 1.5 - 2.0 | average |
| > 2.0 | inefficient |

---

### 5. Energy Optimization

```bash
curl -X POST "http://localhost:8000/api/v1/analytics/energy/optimize?datacenter_id=dc-001&target_pue=1.3"
```

```json
{
  "current_pue": 1.5,
  "target_pue": 1.3,
  "potential_savings_pct": 13.33,
  "actions": [
    {
      "action": "Raise cooling set points by 2°C",
      "category": "cooling",
      "estimated_pue_impact": 0.06,
      "priority": "high"
    },
    {
      "action": "Implement hot aisle containment",
      "category": "airflow",
      "estimated_pue_impact": 0.08,
      "priority": "high"
    }
  ],
  "estimated_monthly_savings_kwh": 14400.0
}
```

---

## 🔄 Full Pipeline Test

Test end-to-end: Kafka → Consumer → TimescaleDB → API

### Step 1: Run Database Migrations

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/migrations
python3 run_migrations.py --host 10.70.0.56 --port 5433
```

### Step 2: Generate Sample Data ke Kafka

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
python3 scripts/generate_sample_data.py --target kafka --days 7
```

### Step 3: Start Kafka Consumer (Terminal 2)

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
python3 -m stream.metrics_consumer
```

### Step 4: Start Anomaly Detector (Terminal 3)

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
python3 -m stream.anomaly_detector
```

### Step 5: Start API Server (Terminal 4)

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Step 6: Verify Data Flow

```bash
# Check anomalies (should have data now)
curl http://localhost:8000/api/v1/analytics/anomalies

# Check predictions
curl http://localhost:8000/api/v1/analytics/predictions

# Test capacity with real data
curl -X POST http://localhost:8000/api/v1/analytics/capacity/forecast \
  -H "Content-Type: application/json" \
  -d '{"ci_id": "srv-web-001", "metric_name": "cpu_usage", "forecast_days": 30}'
```

---

## 🌐 Swagger UI (Interactive)

Buka browser ke:

```
http://localhost:8000/api/v1/docs
```

**Fitur Swagger UI:**
1. Lihat semua endpoints
2. Klik "Try it out" pada endpoint manapun
3. Isi parameter langsung di browser
4. Klik "Execute"
5. Lihat response real-time
6. Lihat request/response schema

---

## 🔧 Troubleshooting

### Problem: API tidak bisa start

```bash
# Cek port sudah dipakai
lsof -i :8000

# Kill process lama
pkill -f "uvicorn api.main"

# Start ulang
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Problem: ModuleNotFoundError

```bash
# Install semua dependencies
pip3 install --break-system-packages \
  fastapi uvicorn pydantic-settings \
  psycopg2-binary kafka-python \
  numpy scikit-learn pandas sqlalchemy redis
```

### Problem: Kafka connection refused

```bash
# Cek Kafka running
kafka-topics --bootstrap-server 10.70.0.56:9092 --list

# Jika tidak ada Kafka, gunakan TimescaleDB langsung
python3 scripts/generate_sample_data.py --target timescaledb
```

### Problem: TimescaleDB connection refused

```bash
# Cek connectivity
psql -h 10.70.0.56 -p 5433 -U ai_user -d timescale_db

# Jika tidak ada TimescaleDB, gunakan demo mode
# (API akan gunakan synthetic data otomatis)
```

### Problem: Capacity/Energy return synthetic data

Ini **normal**! Endpoint ini punya 2 mode:
1. **Demo mode**: Jika DB tidak tersedia → return synthetic data
2. **Live mode**: Jika DB punya data real → return data real

Untuk switch ke live mode:
```bash
# 1. Run migrations
python3 migrations/run_migrations.py --host 10.70.0.56 --port 5433

# 2. Generate sample data ke DB
python3 scripts/generate_sample_data.py --target timescaledb

# 3. Restart API
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

## 📁 File Locations

```
implementation/dcim_ai_v2_rag/
├── scripts/
│   ├── generate_sample_data.py        # ← Sample data generator
│   └── test_api_with_sample_data.py   # ← API test script
├── docs/
│   ├── TESTING.md                     # ← FILE INI
│   └── ARCHITECTURE.md                # ← Arsitektur & cara kerja
├── api/
│   ├── main.py                        # FastAPI entry point
│   ├── config.py                      # Configuration
│   ├── dependencies.py                # Auth & DB
│   └── routers/
│       ├── anomalies.py               # Anomaly endpoints
│       ├── predictions.py             # Prediction endpoints
│       ├── rca.py                     # RCA endpoints
│       ├── capacity.py                # Capacity endpoints
│       ├── energy.py                  # Energy endpoints
│       ├── models.py                  # Model registry
│       └── llm.py                     # LLM endpoints
├── migrations/
│   ├── 001_create_timescaledb_schema.sql
│   └── run_migrations.py
├── stream/
│   ├── base_consumer.py               # Base Kafka consumer
│   ├── metrics_consumer.py            # Metrics ingestion
│   └── anomaly_detector.py            # Anomaly detection
├── services/
│   ├── capacity_forecasting.py        # Capacity service
│   └── energy_optimization.py         # Energy service
└── QUICKSTART.md                      # Quick start guide
```

---

## 📞 Support

**Dokumentasi:**
- `docs/ARCHITECTURE.md` - Arsitektur lengkap & data flow
- `QUICKSTART.md` - Quick start guide
- `task/MT-023_BLOCK7_FINAL_SUMMARY.md` - Progress report

**Infrastructure:**
- TimescaleDB: `10.70.0.56:5433`
- Kafka: `10.70.0.56:9092`
- API Server: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/api/v1/docs`

---

**Generated:** 2026-07-13  
**By:** Hermes (DCIM AI Assistant)
