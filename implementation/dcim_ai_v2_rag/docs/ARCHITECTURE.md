# Block 7 Analytics & AI Engine - Arsitektur & Cara Kerja

**Last Updated:** 2026-07-10  
**Status:** Production-Ready Foundation

---

## 📋 Daftar Isi

1. [Arsitektur Overview](#arsitektur-overview)
2. [Data Flow](#data-flow)
3. [Komponen-Komponen](#komponen-komponen)
4. [Cara Kerja Per Komponen](#cara-kerja-per-komponen)
5. [Contoh Penggunaan](#contoh-penggunaan)
6. [Troubleshooting](#troubleshooting)

---

## 🏗️ Arsitektur Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    DCIM Analytics & AI Engine                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐ │
│  │  Kafka   │───▶│ Stream   │───▶│Timescale │───▶│  API     │ │
│  │  Topics  │    │Consumer  │    │   DB     │    │ Layer    │ │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘ │
│       │              │               │               │         │
│       │              ▼               │               ▼         │
│       │        ┌──────────┐          │         ┌──────────┐   │
│       │        │ Anomaly  │──────────┼────────▶│ Clients  │   │
│       │        │ Detector │          │         │ (curl,   │   │
│       │        └──────────┘          │         │  apps)   │   │
│       │                              │         └──────────┘   │
│       │                              ▼                         │
│       │                        ┌──────────┐                    │
│       │                        │ Services │                    │
│       │                        │ (Capacity│                    │
│       │                        │  Energy) │                    │
│       │                        └──────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Flow 1: Metrics Ingestion (Real-time)

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   External   │     │    Kafka     │     │  TimescaleDB │
│   Systems    │────▶│   Consumer   │────▶│   (metrics)  │
│  (Prometheus,│     │              │     │              │
│   SNMP, etc) │     └──────────────┘     └──────────────┘
└──────────────┘            │
                           ▼
                    ┌──────────────┐
                    │   Anomaly    │
                    │  Detector    │
                    │  (Z-score)   │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    Kafka     │
                    │  (anomalies) │
                    └──────────────┘
```

### Flow 2: API Request/Response

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │     │   FastAPI    │     │  TimescaleDB │
│  (Browser,   │────▶│   Server     │────▶│   (query)    │
│   curl, etc) │     │              │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  Services    │
                    │ (Analytics)  │
                    └──────────────┘
```

---

## 🧩 Komponen-Komponen

### 1. **API Layer** (`api/`)

| File | Fungsi |
|------|--------|
| `main.py` | Entry point FastAPI, register semua router |
| `config.py` | Konfigurasi (env vars, defaults) |
| `dependencies.py` | Auth, DB connection, permission checks |
| `routers/` | Endpoint definitions per fitur |

### 2. **Stream Processing** (`stream/`)

| File | Fungsi |
|------|--------|
| `base_consumer.py` | Base class Kafka consumer dengan error handling |
| `metrics_consumer.py` | Baca metrics dari Kafka → simpan ke TimescaleDB |
| `anomaly_detector.py` | Deteksi anomaly pakai Z-score secara real-time |

### 3. **Analytics Services** (`services/`)

| File | Fungsi |
|------|--------|
| `capacity_forecasting.py` | Prediksi kapan resource habis (CPU, RAM, disk) |
| `energy_optimization.py` | Hitung PUE, efisiensi cooling, rekomendasi |

### 4. **Database** (`migrations/`)

| File | Fungsi |
|------|--------|
| `001_create_timescaledb_schema.sql` | Schema: 9 tables, hypertables, continuous aggregates |
| `run_migrations.py` | Script untuk jalankan migrations |

---

## 🔍 Cara Kerja Per Komponen

### 1. FastAPI API Server

```python
# api/main.py - Entry point

from fastapi import FastAPI
from .routers import anomalies, predictions, rca, capacity, energy, models, llm

app = FastAPI(title="DCIM Analytics & AI Engine")

# Register semua router
app.include_router(anomalies.router, prefix="/api/v1/analytics/anomalies")
app.include_router(predictions.router, prefix="/api/v1/analytics/predictions")
app.include_router(rca.router, prefix="/api/v1/analytics/rca")
# ... dst

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

**Cara kerja:**
1. Client kirim HTTP request ke endpoint
2. FastAPI route ke handler function yang sesuai
3. Handler ambil data dari DB atau service
4. Return JSON response

**Contoh:**
```bash
# List anomalies
curl http://localhost:8000/api/v1/analytics/anomalies

# Response:
[
  {
    "anomaly_id": "ano-001",
    "timestamp": "2026-07-10T04:00:00Z",
    "metric_name": "cpu_usage",
    "ci_id": "server-001",
    "detection_method": "zscore",
    "current_value": 95.5,
    "anomaly_score": 3.2,
    "severity": "high"
  }
]
```

---

### 2. Kafka Metrics Consumer

```python
# stream/metrics_consumer.py

class MetricsConsumer(BaseConsumer):
    def __init__(self):
        super().__init__(
            topics=["dcim.analytics.metrics"],
            group_id="dcim-metrics-consumer"
        )
    
    def process_message(self, message):
        # 1. Parse message dari Kafka
        metric = {
            "ci_id": message["ci_id"],
            "metric_name": message["metric_name"],
            "value": message["value"],
            "timestamp": message["timestamp"]
        }
        
        # 2. Insert ke TimescaleDB
        self.db.execute("""
            INSERT INTO metrics (time, ci_id, metric_name, value, source)
            VALUES (%s, %s, %s, %s, %s)
        """, (metric["timestamp"], metric["ci_id"], 
              metric["metric_name"], metric["value"], "kafka"))
```

**Cara kerja:**
1. Consumer subscribe ke Kafka topic `dcim.analytics.metrics`
2. Terima message dari producer (external systems)
3. Parse message (JSON → dict)
4. Insert ke TimescaleDB table `metrics`
5. Commit offset ke Kafka

**Data format:**
```json
{
  "ci_id": "server-001",
  "metric_name": "cpu_usage",
  "value": 75.5,
  "timestamp": "2026-07-10T04:00:00Z",
  "source": "prometheus",
  "tags": {"environment": "production", "datacenter": "dc1"}
}
```

---

### 3. Anomaly Detector (Z-score)

```python
# stream/anomaly_detector.py

class AnomalyDetector:
    def __init__(self, threshold=3.0, window_size=100):
        self.threshold = threshold  # Z-score threshold
        self.window_size = window_size  # Sliding window size
    
    def detect(self, current_value, historical_values):
        # 1. Hitung mean dari window
        mean = sum(historical_values) / len(historical_values)
        
        # 2. Hitung standard deviation
        variance = sum((x - mean) ** 2 for x in historical_values) / len(historical_values)
        std_dev = variance ** 0.5
        
        # 3. Hitung Z-score
        if std_dev == 0:
            z_score = 0
        else:
            z_score = (current_value - mean) / std_dev
        
        # 4. Deteksi anomaly
        is_anomaly = abs(z_score) > self.threshold
        
        return {
            "is_anomaly": is_anomaly,
            "z_score": z_score,
            "mean": mean,
            "std_dev": std_dev,
            "threshold": self.threshold
        }
```

**Cara kerja:**
1. Baca metrics terbaru dari TimescaleDB (sliding window)
2. Hitung mean dan standard deviation dari window
3. Hitung Z-score untuk value terbaru
4. Jika `|Z-score| > threshold` → anomaly!
5. Publish anomaly ke Kafka topic `dcim.analytics.anomalies`

**Visualisasi Z-score:**
```
Value: 95 (anomaly!)
         ↑
    ─────┼───────────────────── threshold (Z=3)
         │
    ─────┼───────────────────── mean
         │
    ─────┼───────────────────── threshold (Z=-3)
         ↓
Normal range: mean ± (3 × std_dev)
```

---

### 4. Capacity Forecasting

```python
# services/capacity_forecasting.py

class CapacityForecastingService:
    async def generate_forecast(self, ci_id, metric_name, forecast_days=30):
        # 1. Ambil historical data dari TimescaleDB
        data = await self._get_historical_data(ci_id, metric_name, days=90)
        
        # 2. Fit linear regression
        # y = mx + b (trend line)
        x = range(len(data))  # time
        y = [d["value"] for d in data]  # values
        
        slope = self._calculate_slope(x, y)  # m
        intercept = self._calculate_intercept(x, y)  # b
        
        # 3. Prediksi ke depan
        future_x = len(data) + forecast_days
        predicted_value = slope * future_x + intercept
        
        # 4. Hitung kapan resource habis (100%)
        if slope > 0:  # Increasing trend
            days_to_exhaustion = (100 - y[-1]) / slope
            exhaustion_date = datetime.now() + timedelta(days=days_to_exhaustion)
        else:
            exhaustion_date = None  # Tidak akan habis
        
        return {
            "ci_id": ci_id,
            "metric_name": metric_name,
            "current_value": y[-1],
            "predicted_value": predicted_value,
            "trend": "increasing" if slope > 0 else "decreasing",
            "slope": slope,
            "exhaustion_date": exhaustion_date,
            "confidence": self._calculate_r_squared(x, y, slope, intercept)
        }
```

**Cara kerja:**
1. Ambil historical data (90 hari) dari TimescaleDB
2. Fit linear regression ke data
3. Extrapolate ke depan (30/60/90 hari)
4. Hitung kapan resource mencapai 100%
5. Return forecast dengan confidence score

**Contoh output:**
```json
{
  "ci_id": "server-001",
  "metric_name": "disk_usage",
  "current_value": 75.2,
  "predicted_value_30d": 82.1,
  "predicted_value_60d": 89.0,
  "predicted_value_90d": 95.9,
  "exhaustion_date": "2026-10-15",
  "trend": "increasing",
  "slope": 0.23,
  "confidence": 0.89,
  "recommendation": "Add 50GB storage before 2026-10-15"
}
```

---

### 5. Energy Optimization (PUE)

```python
# services/energy_optimization.py

class EnergyOptimizationService:
    async def calculate_pue(self, datacenter_id):
        # 1. Ambil data power dari TimescaleDB
        total_power = await self._get_total_power(datacenter_id)
        it_power = await self._get_it_power(datacenter_id)
        
        # 2. Hitung PUE
        # PUE = Total Facility Power / IT Equipment Power
        pue = total_power / it_power
        
        # 3. Tentukan rating
        if pue <= 1.2:
            rating = "excellent"
        elif pue <= 1.5:
            rating = "good"
        elif pue <= 2.0:
            rating = "average"
        else:
            rating = "inefficient"
        
        # 4. Hitung cooling efficiency
        cooling_power = total_power - it_power
        cooling_efficiency = it_power / cooling_power if cooling_power > 0 else 0
        
        return {
            "datacenter_id": datacenter_id,
            "pue": round(pue, 2),
            "total_power_kw": total_power,
            "it_power_kw": it_power,
            "cooling_power_kw": cooling_power,
            "cooling_efficiency": round(cooling_efficiency, 2),
            "rating": rating,
            "recommendations": self._get_recommendations(pue, rating)
        }
```

**Cara kerja:**
1. Ambil data power dari TimescaleDB
2. Hitung PUE = Total Power / IT Power
3. Tentukan rating (excellent/good/average/inefficient)
4. Hitung cooling efficiency
5. Generate rekomendasi optimasi

**PUE Explained:**
```
PUE = 1.0 → Perfect (all power goes to IT)
PUE = 1.2 → Excellent (20% overhead for cooling/lighting)
PUE = 1.5 → Good (50% overhead)
PUE = 2.0 → Average (100% overhead - same power for IT and cooling)
PUE > 2.0 → Inefficient (more power for cooling than IT!)
```

---

### 6. TimescaleDB Schema

```sql
-- Table: metrics (Hypertable - time-series optimized)
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    ci_id TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    source TEXT,
    tags JSONB
);

-- Convert to hypertable (TimescaleDB magic)
SELECT create_hypertable('metrics', 'time');

-- Continuous aggregate (auto-rollup)
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    ci_id,
    metric_name,
    AVG(value) as avg_value,
    MAX(value) as max_value,
    MIN(value) as min_value,
    COUNT(*) as sample_count
FROM metrics
GROUP BY bucket, ci_id, metric_name;
```

**Cara kerja:**
1. Data time-series disimpan di hypertable (partitioned by time)
2. TimescaleDB otomatis partition per hari
3. Continuous aggregates pre-compute rollups (hourly, daily)
4. Retention policy auto-delete data > 90 hari
5. Indexes untuk query cepat

---

## 🧪 Contoh Penggunaan

### Contoh 1: Kirim Metrics ke Kafka

```python
# examples/send_metrics.py

from kafka import KafkaProducer
import json
from datetime import datetime, timezone

producer = KafkaProducer(
    bootstrap_servers='10.70.0.56:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Kirim CPU usage metric
metric = {
    "ci_id": "server-001",
    "metric_name": "cpu_usage",
    "value": 85.5,
    "timestamp": datetime.now(timezone.utc).isoformat(),
    "source": "prometheus",
    "tags": {"environment": "production"}
}

producer.send('dcim.analytics.metrics', value=metric)
producer.flush()
print(f"Sent: {metric}")
```

### Contoh 2: Query Anomalies via API

```bash
# List semua anomalies
curl http://localhost:8000/api/v1/analytics/anomalies

# Filter by CI ID
curl "http://localhost:8000/api/v1/analytics/anomalies?ci_id=server-001"

# Get anomaly details
curl http://localhost:8000/api/v1/analytics/anomalies/ano-001
```

### Contoh 3: Trigger Capacity Forecast

```bash
curl -X POST http://localhost:8000/api/v1/analytics/capacity/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "ci_id": "server-001",
    "metric_name": "disk_usage",
    "forecast_days": 30
  }'
```

### Contoh 4: Calculate PUE

```bash
curl http://localhost:8000/api/v1/analytics/energy/pue?datacenter_id=dc-001
```

---

## 🔧 Troubleshooting

### Problem: API tidak bisa start

```bash
# Cek log
uvicorn api.main:app --log-level debug

# Cek dependencies
pip list | grep -E "fastapi|uvicorn|pydantic"

# Cek port
lsof -i :8000
```

### Problem: Kafka consumer tidak terima message

```bash
# Cek topic exists
kafka-topics --bootstrap-server 10.70.0.56:9092 --list

# Cek consumer group
kafka-consumer-groups --bootstrap-server 10.70.0.56:9092 \
  --describe --group dcim-metrics-consumer

# Cek message di topic
kafka-console-consumer --bootstrap-server 10.70.0.56:9092 \
  --topic dcim.analytics.metrics --from-beginning
```

### Problem: TimescaleDB connection refused

```bash
# Cek connectivity
psql -h 10.70.0.56 -p 5433 -U ai_user -d timescale_db

# Cek firewall
telnet 10.70.0.56 5433

# Cek credentials
echo $TIMESCALEDB_HOST $TIMESCALEDB_PORT $TIMESCALEDB_USER
```

---

## 📊 Monitoring

### Health Check

```bash
# API health
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "timestamp": "2026-07-10T04:00:00Z",
  "version": "1.0.0",
  "service": "analytics-ai-engine"
}
```

### Metrics Endpoint (Prometheus)

```bash
curl http://localhost:8000/metrics

# Output:
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/health"} 150
http_requests_total{method="POST",endpoint="/api/v1/analytics/rca/analyze"} 23
```

---

## 🎯 Summary

| Komponen | Input | Output | Fungsi |
|----------|-------|--------|--------|
| API Layer | HTTP Request | JSON Response | Serve data ke client |
| Metrics Consumer | Kafka messages | TimescaleDB rows | Ingest metrics |
| Anomaly Detector | Metrics | Anomalies | Deteksi masalah real-time |
| Capacity Service | Historical data | Forecasts | Prediksi resource exhaustion |
| Energy Service | Power data | PUE & recommendations | Optimasi energi |

**Data Flow:**
```
External Systems → Kafka → Consumer → TimescaleDB → API → Clients
                                    ↓
                              Anomaly Detector → Kafka (anomalies)
```

---

**Generated:** 2026-07-10  
**By:** Hermes (DCIM AI Assistant)
