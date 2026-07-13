-- ============================================================================
-- DCIM Analytics & AI Engine - TimescaleDB Schema
-- Migration: 001_create_timescaledb_schema.sql
-- Reference: block7-analytics-ai-engine-technical-requirements.md §5.1
-- ============================================================================

-- Enable TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. TIME-SERIES METRICS TABLE (Hypertable)
-- ============================================================================

CREATE TABLE IF NOT EXISTS metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    ci_id UUID,
    asset_id UUID,
    source VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    tags JSONB DEFAULT '{}'::jsonb,
    CONSTRAINT metrics_value_not_null CHECK (value IS NOT NULL)
);

-- Convert to hypertable
SELECT create_hypertable(
    'metrics',
    'time',
    if_not_exists => TRUE,
    chunk_time_interval => INTERVAL '1 day'
);

-- Indexes for query performance
CREATE INDEX IF NOT EXISTS idx_metrics_metric_name ON metrics (metric_name, time DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_ci_id ON metrics (ci_id, time DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_source ON metrics (source, time DESC);
CREATE INDEX IF NOT EXISTS idx_metrics_tags_gin ON metrics USING GIN (tags);

-- Compression policy (compress after 7 days)
SELECT add_compression_policy(
    'metrics',
    INTERVAL '7 days',
    if_not_exists => TRUE
);

-- Retention policy (drop after 90 days)
SELECT add_retention_policy(
    'metrics',
    INTERVAL '90 days',
    if_not_exists => TRUE
);

-- ============================================================================
-- 2. CONTINUOUS AGGREGATES (Pre-computed hourly/daily)
-- ============================================================================

CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    metric_name,
    ci_id,
    source,
    COUNT(*) AS sample_count,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value
FROM metrics
GROUP BY bucket, metric_name, ci_id, source
WITH NO DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS metrics_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    metric_name,
    ci_id,
    source,
    COUNT(*) AS sample_count,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value
FROM metrics
GROUP BY bucket, metric_name, ci_id, source
WITH NO DATA;

-- Refresh policies
SELECT add_continuous_aggregate_policy(
    'metrics_hourly',
    start_offset => INTERVAL '3 hours',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE
);

SELECT add_continuous_aggregate_policy(
    'metrics_daily',
    start_offset => INTERVAL '3 days',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day',
    if_not_exists => TRUE
);

-- ============================================================================
-- 3. ANOMALY EVENTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS anomaly_events (
    anomaly_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    ci_id UUID,
    asset_id UUID,
    detection_method VARCHAR(50) NOT NULL,
    current_value DOUBLE PRECISION NOT NULL,
    expected_min DOUBLE PRECISION,
    expected_max DOUBLE PRECISION,
    anomaly_score DECIMAL(5,4) NOT NULL CHECK (anomaly_score >= 0 AND anomaly_score <= 1),
    severity VARCHAR(20) NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    description TEXT,
    possible_causes JSONB DEFAULT '[]'::jsonb,
    recommended_actions JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(20) DEFAULT 'open' CHECK (status IN ('open', 'acknowledged', 'resolved', 'false_positive')),
    acknowledged_by VARCHAR(100),
    acknowledged_at TIMESTAMPTZ,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_anomaly_timestamp ON anomaly_events (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_ci_id ON anomaly_events (ci_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_severity ON anomaly_events (severity, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_status ON anomaly_events (status, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_anomaly_metric_name ON anomaly_events (metric_name, timestamp DESC);

-- ============================================================================
-- 4. PREDICTIONS TABLE (Predictive Maintenance)
-- ============================================================================

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    ci_id UUID NOT NULL,
    asset_id UUID,
    prediction_type VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    model_version VARCHAR(20),
    predicted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    prediction_window VARCHAR(20) NOT NULL,
    failure_probability DECIMAL(5,4) CHECK (failure_probability >= 0 AND failure_probability <= 1),
    confidence DECIMAL(5,4) CHECK (confidence >= 0 AND confidence <= 1),
    risk_level VARCHAR(20) CHECK (risk_level IN ('low', 'medium', 'high', 'critical')),
    contributing_factors JSONB DEFAULT '[]'::jsonb,
    recommended_actions JSONB DEFAULT '[]'::jsonb,
    maintenance_window JSONB,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'scheduled', 'completed', 'cancelled')),
    scheduled_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_predictions_ci_id ON predictions (ci_id, predicted_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_risk ON predictions (risk_level, predicted_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_status ON predictions (status, predicted_at DESC);
CREATE INDEX IF NOT EXISTS idx_predictions_model ON predictions (model, model_version, predicted_at DESC);

-- ============================================================================
-- 5. ML MODELS REGISTRY TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS ml_models (
    model_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    domain VARCHAR(50),
    trained_at TIMESTAMPTZ,
    training_data_size INTEGER,
    training_duration_seconds INTEGER,
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc_roc DECIMAL(5,4),
    status VARCHAR(20) DEFAULT 'registered' CHECK (status IN ('registered', 'staging', 'production', 'archived')),
    deployed_at TIMESTAMPTZ,
    artifact_path VARCHAR(500) NOT NULL,
    artifact_size_bytes BIGINT,
    artifact_checksum VARCHAR(64),
    hyperparameters JSONB,
    features_used JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(model_name, model_type, version)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_models_name_type ON ml_models (model_name, model_type);
CREATE INDEX IF NOT EXISTS idx_models_status ON ml_models (status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_models_type ON ml_models (model_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_models_domain ON ml_models (domain, created_at DESC);

-- ============================================================================
-- 6. RCA REPORTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS rca_reports (
    rca_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id VARCHAR(100) NOT NULL,
    ci_id UUID NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    mode VARCHAR(20) NOT NULL CHECK (mode IN ('reactive', 'forward', 'hybrid')),
    root_cause VARCHAR(200) NOT NULL,
    confidence DECIMAL(5,4) NOT NULL,
    causal_chain JSONB DEFAULT '[]'::jsonb,
    explanation TEXT,
    timeline JSONB DEFAULT '[]'::jsonb,
    correlated_events JSONB DEFAULT '[]'::jsonb,
    recommended_action TEXT,
    analysis_duration_seconds DECIMAL(8,2),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(incident_id)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_rca_incident ON rca_reports (incident_id);
CREATE INDEX IF NOT EXISTS idx_rca_ci_id ON rca_reports (ci_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_rca_timestamp ON rca_reports (timestamp DESC);

-- ============================================================================
-- 7. CAPACITY FORECASTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS capacity_forecasts (
    forecast_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    resource_type VARCHAR(50) NOT NULL,
    ci_id UUID,
    forecast_date DATE NOT NULL,
    current_usage_pct DECIMAL(5,2),
    projected_usage_pct DECIMAL(5,2),
    projected_exhaustion_date DATE,
    confidence DECIMAL(5,4),
    model VARCHAR(50) NOT NULL,
    recommendations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_capacity_resource ON capacity_forecasts (resource_type, forecast_date DESC);
CREATE INDEX IF NOT EXISTS idx_capacity_ci_id ON capacity_forecasts (ci_id, forecast_date DESC);
CREATE INDEX IF NOT EXISTS idx_capacity_exhaustion ON capacity_forecasts (projected_exhaustion_date);

-- ============================================================================
-- 8. ENERGY REPORTS TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS energy_reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_date DATE NOT NULL,
    pue DECIMAL(5,3),
    total_power_kw DECIMAL(10,2),
    it_power_kw DECIMAL(10,2),
    cooling_power_kw DECIMAL(10,2),
    cooling_efficiency DECIMAL(5,4),
    power_load_balance DECIMAL(5,4),
    carbon_intensity_gco2_kwh DECIMAL(8,2),
    recommendations JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_energy_date ON energy_reports (report_date DESC);
CREATE INDEX IF NOT EXISTS idx_energy_pue ON energy_reports (pue, report_date DESC);

-- ============================================================================
-- 9. MODEL DRIFT TRACKING TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS model_drift_tracking (
    drift_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID REFERENCES ml_models(model_id),
    check_date TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    drift_score DECIMAL(5,4) NOT NULL,
    metric_drifts JSONB DEFAULT '{}'::jsonb,
    threshold DECIMAL(5,4) DEFAULT 0.15,
    status VARCHAR(20) CHECK (status IN ('ok', 'warning', 'critical')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_drift_model ON model_drift_tracking (model_id, check_date DESC);
CREATE INDEX IF NOT EXISTS idx_drift_status ON model_drift_tracking (status, check_date DESC);

-- ============================================================================
-- 10. AUDIT LOG TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS audit_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    user_id VARCHAR(100),
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50) NOT NULL,
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}'::jsonb,
    ip_address INET,
    user_agent TEXT
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log (user_id, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_resource ON audit_log (resource_type, resource_id, timestamp DESC);

-- ============================================================================
-- SUMMARY
-- ============================================================================

COMMENT ON TABLE metrics IS 'Time-series metrics hypertable with compression and retention';
COMMENT ON TABLE anomaly_events IS 'Anomaly detection events with severity classification';
COMMENT ON TABLE predictions IS 'Predictive maintenance forecasts and failure predictions';
COMMENT ON TABLE ml_models IS 'ML model registry with versioning and performance tracking';
COMMENT ON TABLE rca_reports IS 'Root cause analysis reports with causal chains';
COMMENT ON TABLE capacity_forecasts IS 'Capacity forecasting reports for resource planning';
COMMENT ON TABLE energy_reports IS 'Energy optimization reports (PUE, cooling, power)';
COMMENT ON TABLE model_drift_tracking IS 'Model drift monitoring over time';
COMMENT ON TABLE audit_log IS 'Audit trail for all analytics operations';

-- Grant permissions (adjust based on your IAM setup)
-- GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO ai_team;
-- GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO ai_team;
