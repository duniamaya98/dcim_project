# Database Migrations

Database schema migrations untuk TimescaleDB Analytics & AI Engine.

## Prerequisites

- TimescaleDB 2.15+
- PostgreSQL 16+
- User dengan CREATE privileges

## Connection Details

```bash
Host: 10.70.0.56
Port: 5433
Database: dcim_analytics
User: ai_team
Password: [from vault]
```

## Running Migrations

### Manual Execution

```bash
psql -h 10.70.0.56 -p 5433 -U ai_team -d dcim_analytics -f 001_create_timescaledb_schema.sql
```

### Via Python Script

```python
python run_migrations.py
```

## Migration Files

| # | File | Description |
|---|------|-------------|
| 001 | `001_create_timescaledb_schema.sql` | Initial schema: metrics, anomalies, predictions, models, RCA, capacity, energy |

## Schema Overview

### Hypertables
- `metrics` - Time-series metrics (compressed after 7d, retained for 90d)

### Continuous Aggregates
- `metrics_hourly` - Hourly rollups
- `metrics_daily` - Daily rollups

### Regular Tables
- `anomaly_events` - Anomaly detection results
- `predictions` - Predictive maintenance forecasts
- `ml_models` - Model registry
- `rca_reports` - Root cause analysis
- `capacity_forecasts` - Capacity planning
- `energy_reports` - Energy optimization
- `model_drift_tracking` - Model drift monitoring
- `audit_log` - Audit trail

## Verification

```sql
-- Check hypertable
SELECT * FROM timescaledb_information.hypertables;

-- Check continuous aggregates
SELECT * FROM timescaledb_information.continuous_aggregates;

-- Check compression policy
SELECT * FROM timescaledb_information.compression_settings;

-- Check retention policy
SELECT * FROM timescaledb_information.jobs WHERE proc_name LIKE 'policy_retention%';
```

## Rollback

```sql
-- Drop all tables (DANGEROUS - data loss!)
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS model_drift_tracking CASCADE;
DROP TABLE IF EXISTS energy_reports CASCADE;
DROP TABLE IF EXISTS capacity_forecasts CASCADE;
DROP TABLE IF EXISTS rca_reports CASCADE;
DROP TABLE IF EXISTS ml_models CASCADE;
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS anomaly_events CASCADE;
DROP MATERIALIZED VIEW IF EXISTS metrics_daily CASCADE;
DROP MATERIALIZED VIEW IF EXISTS metrics_hourly CASCADE;
DROP TABLE IF EXISTS metrics CASCADE;
```
