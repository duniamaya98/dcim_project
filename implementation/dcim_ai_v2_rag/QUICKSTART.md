# Block 7 Analytics & AI Engine - Quick Start

**Last Updated:** 2026-07-09 05:08 WIB

## 🚀 Option 1: Run API Directly (No Docker)

Paling cepat untuk testing.

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag

# 1. Install dependencies
cd api
pip install -r requirements.txt
cd ..

# 2. Set environment variables
export TIMESCALEDB_HOST=10.70.0.56
export TIMESCALEDB_PORT=5433
export TIMESCALEDB_DATABASE=timescale_db
export TIMESCALEDB_USER=ai_user
export TIMESCALEDB_PASSWORD=<your-local-password>
export KAFKA_BOOTSTRAP_SERVERS=10.70.0.56:9092

# 3. Run API
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Test
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/docs  # OpenAPI docs
```

---

## 🐳 Option 2: Docker Compose (Simplified)

Uses external infrastructure (TimescaleDB & Kafka dari Syauqi).

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag

# Build images (first time only)
docker-compose -f docker-compose.simple.yml build

# Start services
docker-compose -f docker-compose.simple.yml up -d

# Check logs
docker-compose -f docker-compose.simple.yml logs -f api

# Test API
curl http://localhost:8000/health
open http://localhost:8000/api/v1/docs

# Stop services
docker-compose -f docker-compose.simple.yml down
```

---

## 📊 Option 3: Run Database Migrations

Setup TimescaleDB schema sebelum run API.

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag/migrations

# Run migrations
python run_migrations.py \
  --host 10.70.0.56 \
  --port 5433 \
  --database timescale_db \
  --user ai_user \
  --password <your-local-password>

# Output:
# ✅ Connected to TimescaleDB
# ✅ Running migration: 001_create_timescaledb_schema.sql
# ✅ Created 9 tables, 2 hypertables, 2 continuous aggregates
```

---

## 🧪 Option 4: Test Individual Components

### Test Kafka Consumer

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag

export TIMESCALEDB_HOST=10.70.0.56
export TIMESCALEDB_PORT=5433
export KAFKA_BOOTSTRAP_SERVERS=10.70.0.56:9092

python -m stream.metrics_consumer
```

### Test Anomaly Detector

```bash
python -m stream.anomaly_detector
```

### Test Capacity Forecasting Service

```bash
python -c "
from services.capacity_forecasting import CapacityForecastingService
import asyncio

async def test():
    service = CapacityForecastingService()
    forecast = await service.generate_forecast(
        ci_id='server-001',
        metric_name='cpu_usage',
        forecast_days=30
    )
    print(forecast)

asyncio.run(test())
"
```

---

## 📋 Verification Checklist

### 1. Database Connection

```bash
psql -h 10.70.0.56 -p 5433 -U ai_user -d timescale_db -c "\dt"
# Should show 9 tables
```

### 2. Kafka Topics

```bash
# List topics
kafka-topics --bootstrap-server 10.70.0.56:9092 --list | grep dcim

# Expected:
# dcim.analytics.metrics
# dcim.analytics.anomalies
# dcim.analytics.rca
# dcim.analytics.capacity
# dcim.analytics.energy
```

### 3. API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List anomalies
curl http://localhost:8000/api/v1/analytics/anomalies

# RCA analyze
curl -X POST http://localhost:8000/api/v1/analytics/rca/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ci_id": "server-001",
    "metric_name": "cpu_usage",
    "timestamp": "2026-07-09T05:00:00Z"
  }'

# Capacity forecast
curl -X POST http://localhost:8000/api/v1/analytics/capacity/forecast \
  -H "Content-Type: application/json" \
  -d '{
    "ci_id": "server-001",
    "metric_name": "disk_usage",
    "forecast_days": 30
  }'
```

---

## 🔧 Troubleshooting

### Problem: ModuleNotFoundError

```bash
# Solution: Install dependencies
cd api
pip install -r requirements.txt
```

### Problem: Connection refused (TimescaleDB)

```bash
# Solution: Check network connectivity
telnet 10.70.0.56 5433

# Or check firewall
sudo ufw status
```

### Problem: Kafka consumer not receiving messages

```bash
# Solution: Check topic exists
kafka-topics --bootstrap-server 10.70.0.56:9092 --describe --topic dcim.analytics.metrics

# Check consumer group
kafka-consumer-groups --bootstrap-server 10.70.0.56:9092 --describe --group dcim-metrics-consumer
```

### Problem: Docker build timeout

```bash
# Solution: Use simplified compose (no local DB/Kafka)
docker-compose -f docker-compose.simple.yml up -d

# Or run directly without Docker (Option 1)
```

---

## 📊 Sample Data Generator

Generate test metrics untuk testing pipeline.

```bash
cd /home/infra/dcim_project/implementation/dcim_ai_v2_rag

# Create sample data generator
cat > scripts/generate_sample_metrics.py << 'EOF'
#!/usr/bin/env python3
"""Generate sample metrics to Kafka for testing"""
import json
import time
import random
from kafka import KafkaProducer
from datetime import datetime, timezone

producer = KafkaProducer(
    bootstrap_servers='10.70.0.56:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

metrics = [
    ('server-001', 'cpu_usage', 10, 90),
    ('server-001', 'memory_usage', 20, 85),
    ('server-001', 'disk_usage', 30, 80),
    ('server-002', 'cpu_usage', 15, 75),
    ('server-002', 'network_rx', 1000000, 9000000),
]

print("Sending sample metrics to dcim.analytics.metrics...")

for i in range(100):
    for ci_id, metric_name, min_val, max_val in metrics:
        message = {
            'ci_id': ci_id,
            'metric_name': metric_name,
            'value': random.uniform(min_val, max_val),
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'source': 'sample_generator',
            'tags': {'environment': 'dev', 'datacenter': 'dc1'}
        }
        producer.send('dcim.analytics.metrics', value=message)
        print(f"Sent: {ci_id} - {metric_name} = {message['value']:.2f}")

    time.sleep(1)

producer.flush()
print("Done!")
EOF

chmod +x scripts/generate_sample_metrics.py
python scripts/generate_sample_metrics.py
```

---

## 🎯 Next Steps

1. **Run migrations** (Option 3) - Setup database schema
2. **Start API** (Option 1 or 2) - Test endpoints
3. **Generate sample data** - Test full pipeline
4. **Check anomaly detection** - Verify real-time processing
5. **Test capacity forecasting** - Verify analytics services

---

**Support:** Hermes AI Assistant
**Documentation:** See README.md for full implementation details
**Report:** task/MT-023_BLOCK7_IMPLEMENTATION_REPORT.md
