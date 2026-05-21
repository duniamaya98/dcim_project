-- =====================================================================
-- Migration: 2026-05-20 — Multi-Model Registry & Schema UC1/UC3
-- Versi paket addendum: v1.2.0
--
-- Mengikuti:
--   MT-018 §11.5  : tabel failure_events (UC1 supervised labeling)
--   MT-018 §11.2  : tabel power_metrics & environment_metrics (UC3)
--   MT-019 §6.2   : kolom multi-model di model_registry
--   MT-019 §6.4   : tabel inference_results (output streaming)
--
-- Catatan:
--   - Semua perubahan IDEMPOTENT (IF NOT EXISTS).
--   - Tidak ada kolom yang dihapus / di-rename.
--   - Aman dijalankan ulang.
--   - Asumsi extension TimescaleDB tersedia. Bila tidak, baris
--     `SELECT create_hypertable(...)` akan gagal — comment-out bila perlu.
--
-- Cara jalankan:
--   psql -U infra -d dcim_ai \
--     -f dcim_ai/registry/sql/migrations/2026_05_20_v1_2_0_multi_model.sql
-- =====================================================================

BEGIN;

-- =====================================================================
-- 1. model_registry — kolom multi-model (MT-019 §6.2)
-- =====================================================================

ALTER TABLE IF EXISTS model_registry
    ADD COLUMN IF NOT EXISTS model_type            TEXT,
    ADD COLUMN IF NOT EXISTS domain                TEXT,
    ADD COLUMN IF NOT EXISTS inference_mode        TEXT,
    ADD COLUMN IF NOT EXISTS data_contract_version TEXT;

-- Backfill: record lama dianggap anomaly model — sesuai perilaku
-- registry sebelum v1.2.0.
UPDATE model_registry
   SET model_type = 'anomaly'
 WHERE model_type IS NULL;

UPDATE model_registry
   SET inference_mode = 'batch'
 WHERE inference_mode IS NULL;

UPDATE model_registry
   SET data_contract_version = '1.0.0'
 WHERE data_contract_version IS NULL;

-- Constraint domain values (soft — pakai CHECK supaya tetap bisa di-extend).
ALTER TABLE IF EXISTS model_registry
    DROP CONSTRAINT IF EXISTS model_registry_model_type_chk;

ALTER TABLE IF EXISTS model_registry
    ADD CONSTRAINT model_registry_model_type_chk
    CHECK (model_type IN (
        'anomaly', 'forecast', 'clustering',
        'energy_anomaly', 'capacity_optimizer'
    ));

ALTER TABLE IF EXISTS model_registry
    DROP CONSTRAINT IF EXISTS model_registry_inference_mode_chk;

ALTER TABLE IF EXISTS model_registry
    ADD CONSTRAINT model_registry_inference_mode_chk
    CHECK (inference_mode IN ('batch', 'streaming', 'scheduled'));

CREATE INDEX IF NOT EXISTS idx_model_registry_type_active
    ON model_registry (model_type, is_active);

CREATE INDEX IF NOT EXISTS idx_model_registry_domain
    ON model_registry (domain);


-- =====================================================================
-- 2. inference_results — output standar (MT-019 §6.3, §6.4)
-- =====================================================================

CREATE TABLE IF NOT EXISTS inference_results (
    id              BIGSERIAL PRIMARY KEY,
    time            TIMESTAMPTZ NOT NULL,
    model_id        TEXT        NOT NULL,
    model_type      TEXT        NOT NULL,
    asset_id        TEXT        NOT NULL,
    score           DOUBLE PRECISION,
    severity        TEXT        NOT NULL,
    confidence      DOUBLE PRECISION,
    domain          TEXT,
    forecast_horizon_h INT,
    payload         JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_inference_results_time
    ON inference_results (time DESC);

CREATE INDEX IF NOT EXISTS idx_inference_results_asset_time
    ON inference_results (asset_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_inference_results_model
    ON inference_results (model_id, time DESC);

CREATE INDEX IF NOT EXISTS idx_inference_results_severity
    ON inference_results (severity, time DESC)
    WHERE severity IN ('warning', 'critical');

-- TimescaleDB hypertable — abaikan bila extension tidak ada.
-- Aman dijalankan ulang karena create_hypertable menerima if_not_exists.
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable(
            'inference_results', 'time',
            if_not_exists => TRUE,
            migrate_data  => TRUE
        );
    END IF;
END $$;


-- =====================================================================
-- 3. failure_events — supervised labels untuk UC1 (MT-018 §11.5)
-- =====================================================================

CREATE TABLE IF NOT EXISTS failure_events (
    event_id     UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    asset_id     TEXT        NOT NULL,
    event_time   TIMESTAMPTZ NOT NULL,
    failure_type TEXT        NOT NULL
        CHECK (failure_type IN ('disk', 'fan', 'thermal', 'memory', 'power', 'other')),
    severity     TEXT        NOT NULL
        CHECK (severity IN ('minor', 'major', 'critical')),
    source       TEXT        NOT NULL
        CHECK (source IN ('manual', 'incident_ticket', 'sensor_threshold')),
    evidence     JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_failure_events_asset_time
    ON failure_events (asset_id, event_time DESC);

CREATE INDEX IF NOT EXISTS idx_failure_events_type
    ON failure_events (failure_type, event_time DESC);


-- =====================================================================
-- 4. power_metrics — UC3 (MT-018 §11.2)
-- =====================================================================

CREATE TABLE IF NOT EXISTS power_metrics (
    time        TIMESTAMPTZ NOT NULL,
    device_id   TEXT        NOT NULL,
    device_type TEXT        NOT NULL
        CHECK (device_type IN ('pdu', 'ups', 'meter', 'other')),
    location    TEXT,
    power_w     DOUBLE PRECISION,
    voltage     DOUBLE PRECISION,
    current     DOUBLE PRECISION,
    energy_kwh  DOUBLE PRECISION,
    pue         DOUBLE PRECISION,
    extra       JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_power_metrics_device_time
    ON power_metrics (device_id, time DESC);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable(
            'power_metrics', 'time',
            if_not_exists => TRUE,
            migrate_data  => TRUE
        );
    END IF;
END $$;


-- =====================================================================
-- 5. environment_metrics — UC3 (MT-018 §11.2)
-- =====================================================================

CREATE TABLE IF NOT EXISTS environment_metrics (
    time        TIMESTAMPTZ NOT NULL,
    device_id   TEXT        NOT NULL,
    location    TEXT,
    temp_inlet  DOUBLE PRECISION,
    temp_outlet DOUBLE PRECISION,
    humidity    DOUBLE PRECISION,
    dewpoint    DOUBLE PRECISION,
    extra       JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_environment_metrics_device_time
    ON environment_metrics (device_id, time DESC);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable(
            'environment_metrics', 'time',
            if_not_exists => TRUE,
            migrate_data  => TRUE
        );
    END IF;
END $$;


-- =====================================================================
-- 6. server_health — UC1 (MT-018 §11.2)
-- =====================================================================

CREATE TABLE IF NOT EXISTS server_health (
    time                       TIMESTAMPTZ NOT NULL,
    hostname                   TEXT        NOT NULL,
    smart_reallocated_sectors  INT,
    smart_pending_sectors      INT,
    smart_temp                 DOUBLE PRECISION,
    fan_speed                  DOUBLE PRECISION,
    hwmon_temp                 DOUBLE PRECISION,
    extra                      JSONB       NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_server_health_host_time
    ON server_health (hostname, time DESC);

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable(
            'server_health', 'time',
            if_not_exists => TRUE,
            migrate_data  => TRUE
        );
    END IF;
END $$;


COMMIT;

-- =====================================================================
-- Verifikasi singkat — jalankan manual setelah migration:
--
--   \d model_registry
--   \d inference_results
--   \d failure_events
--   \d power_metrics
--   \d environment_metrics
--   \d server_health
--
--   SELECT model_type, COUNT(*) FROM model_registry GROUP BY 1;
-- =====================================================================
