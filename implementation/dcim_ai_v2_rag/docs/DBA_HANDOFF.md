# Block 7 DBA Handoff — Analytics Tables Setup

## Background
Block 7 Analytics & AI Engine needs 8 new tables in TimescaleDB (`dcim_analytics` database).
User `ai_team` has only USAGE on public schema — cannot CREATE TABLE.
Tables must be created by `analytics_user` (or any user with CREATE privilege).

## Connection
```
Host: 10.70.0.56
Port: 5433
Database: dcim_analytics
Run as: analytics_user (or superuser)
```

## SQL to Run
```bash
PGPASSWORD=<analytics_user_password> psql \
  -h 10.70.0.56 -p 5433 -U analytics_user -d dcim_analytics \
  -f /home/infra/dcim_project/implementation/dcim_ai_v2_rag/migrations/002_create_analytics_tables.sql
```

## Tables Created (8 tables, ~45 indexes)
| Table | Purpose | Retention |
|-------|---------|-----------|
| anomaly_events | Anomaly detection results | Permanent |
| predictions | Predictive maintenance forecasts | Permanent |
| ml_models | ML model registry | Permanent |
| rca_reports | Root cause analysis reports | Permanent |
| capacity_forecasts | Capacity projections | Permanent |
| energy_reports | PUE/energy optimization | Permanent |
| model_drift_tracking | Model drift monitoring | Permanent |
| audit_log | Audit trail | 90 days |

## Continuous Aggregates
These should already exist from migration 001 (skip-on-error):
- metrics_hourly (1-hour aggregate)
- metrics_daily (1-day aggregate)

If missing, the SQL also attempts to recreate them (skip-on-error).

## Permissions
The SQL includes GRANT statements for `ai_team`:
- SELECT, INSERT, UPDATE, DELETE on all tables
- USAGE on all sequences
- Default privileges for future objects

## Verification After Running
```sql
\dt anomaly_events predictions ml_models rca_reports capacity_forecasts energy_reports model_drift_tracking audit_log

SELECT grantee, privilege_type FROM information_schema.table_privileges
WHERE table_schema='public' AND table_name IN ('anomaly_events','rca_reports')
AND grantee='ai_team';
```

## Contact
Analytics & AI Team — Block 7
