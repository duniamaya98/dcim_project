---
title: "Block 7 — Analytics & AI Engine: Reference Design Spec"
created: 2026-06-23
updated: 2026-06-23
type: reference-design
block: 7
phase: 2
status: generated
confidence: high
tags: [analytics, ai, anomaly-detection, predictive-maintenance, rca, capacity, energy, llm-rag, timeseries]
wiki_pages:
  - analytics-ai-engine
  - cmdb
  - data-ingestion-integration
  - web-dashboard
  - workflow-automation
  - time-series-db-comparison
  - ml-framework-comparison
  - llm-rag-explanation-layer
  - capacity-planning-runbook
  - energy-optimization-strategy
purpose: >
  Reference design spec untuk Block 7 Analytics & AI Engine.
  Tim gunakan untuk komparasi dengan implementasi aktual.
  Gap = connection dots.
---

# Block 7 — Analytics & AI Engine: Reference Design Spec

> **Purpose:** Dokumen referensi lengkap untuk Analytics & AI — anomaly detection, predictive maintenance, RCA, capacity forecasting, energy optimization, LLM/RAG.
> **Cara pakai:** Tim komparasi side-by-side dengan implementasi. Setiap gap = connection point.
> **Architecture Diagram:** `diagrams/block7-analytics-ai-architecture.html`
> **Depends on:** Block 2 (DI&I), Block 4 (CMDB)

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Time-Series Pipeline](#2-time-series-pipeline)
3. [Anomaly Detection](#3-anomaly-detection)
4. [Predictive Maintenance](#4-predictive-maintenance)
5. [Root Cause Analysis (RCA)](#5-root-cause-analysis-rca)
6. [Capacity Forecasting](#6-capacity-forecasting)
7. [Energy Optimization](#7-energy-optimization)
8. [Model Training Pipeline](#8-model-training-pipeline)
9. [LLM/RAG Explanation Layer](#9-llmrag-explanation-layer)
10. [Performance & Sizing](#10-performance--sizing)
11. [Security](#11-security)
12. [Monitoring & Alerting](#12-monitoring--alerting)
13. [Acceptance Criteria](#13-acceptance-criteria)
14. [Gap Comparison Template](#14-gap-comparison-template)

---

## 1. Architecture Overview

### 1.1 System Context

```
┌─────────────────────────────────────────────────────────────────┐
│                   Analytics & AI Engine                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Time-Series Pipeline                         │  │
│  │  Kafka (dcim.analytics.metrics) → Flink/Python            │  │
│  │  → TimescaleDB/InfluxDB → Grafana                        │  │
│  └────────────────────────┬─────────────────────────────────┘  │
│                           │                                     │
│  ┌────────────────────────┴─────────────────────────────────┐  │
│  │              Intelligence Layer                          │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │  │
│  │  │ Anomaly  │ │Predictive│ │   RCA    │ │ Capacity │   │  │
│  │  │Detection │ │Maintenan.│ │ Engine   │ │Forecast. │   │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │  │
│  │  ┌──────────┐ ┌──────────┐                              │  │
│  │  │ Energy   │ │ LLM/RAG  │                              │  │
│  │  │Optimiz.  │ │Layer     │                              │  │
│  │  └──────────┘ └──────────┘                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Model Training Pipeline                     │  │
│  │  Data Collection → Feature Eng → Training → Registry     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
         │                 │                │
         ▼                 ▼                ▼
  ┌──────────┐    ┌──────────┐    ┌──────────────┐
  │   CMDB   │    │Workflow  │    │   Dashboard  │
  │(topology)│    │Automation│    │  (Grafana)   │
  └──────────┘    └──────────┘    └──────────────┘
```

### 1.2 Data Flow

```
DI&I Gateway → Kafka (dcim.analytics.metrics)
  → Flink/Python Processor
    → TimescaleDB/InfluxDB (time-series store)
      → Analytics Services (anomaly, predictive, RCA, capacity, energy)
        → Alerts → Workflow Automation
        → Insights → LLM/RAG → Dashboard
        → Models → Model Registry → Scoring Service
```

### 1.3 Core Responsibilities

| Responsibility | Description | SLA |
|---------------|-------------|-----|
| Time-Series Ingestion | Process 430+ metrics/sec | < 1s latency |
| Anomaly Detection | Real-time anomaly scoring | < 500ms per event |
| Predictive Maintenance | Failure probability scoring | Daily batch + real-time |
| RCA | Root cause identification | < 30s per incident |
| Capacity Forecasting | Trend analysis + projection | Daily batch |
| Energy Optimization | PUE, cooling, power | Hourly calculation |
| LLM/RAG | Natural language explanations | < 5s per query |
| Model Training | Offline model development | Weekly batch |

---

## 2. Time-Series Pipeline

### 2.1 Pipeline Architecture

```
Kafka (dcim.analytics.metrics)
  → Flink/Python Stream Processor
    → TimescaleDB (primary time-series)
    → InfluxDB (optional, for specific use cases)
    → Grafana (visualization)
```

### 2.2 Kafka Topic

| Topic | Partitions | Retention | Purpose |
|-------|------------|-----------|---------|
| `dcim.analytics.metrics` | 6 | 7 days | Raw metrics from DI&I |
| `dcim.analytics.anomalies` | 3 | 30 days | Anomaly alerts |
| `dcim.analytics.predictions` | 3 | 30 days | Prediction results |

### 2.3 TimescaleDB Schema

```sql
-- Metrics table (hypertable)
CREATE TABLE metrics (
    time TIMESTAMPTZ NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    ci_id UUID,
    asset_id UUID,
    source VARCHAR(50) NOT NULL,
    value DOUBLE PRECISION NOT NULL,
    unit VARCHAR(20),
    tags JSONB DEFAULT '{}'
);

-- Convert to hypertable
SELECT create_hypertable('metrics', 'time');

-- Compression policy (compress after 7 days)
ALTER TABLE metrics SET (
    timescaledb.compress,
    timescaledb.compress_segmentby = 'metric_name, source',
    timescaledb.compress_orderby = 'time DESC'
);

SELECT add_compression_policy('metrics', INTERVAL '7 days');

-- Retention policy (drop after 90 days)
SELECT add_retention_policy('metrics', INTERVAL '90 days');

-- Continuous aggregates for common queries
CREATE MATERIALIZED VIEW metrics_hourly
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 hour', time) AS bucket,
    metric_name,
    source,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    COUNT(*) AS sample_count
FROM metrics
GROUP BY bucket, metric_name, source;

CREATE MATERIALIZED VIEW metrics_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', time) AS bucket,
    metric_name,
    source,
    AVG(value) AS avg_value,
    MIN(value) AS min_value,
    MAX(value) AS max_value,
    STDDEV(value) AS stddev_value
FROM metrics
GROUP BY bucket, metric_name, source;
```

### 2.4 Stream Processor

```python
# analytics/timeseries_pipeline.py

from datetime import datetime
import json

class TimeSeriesProcessor:
    def __init__(self, kafka_consumer, tsdb_client):
        self.kafka = kafka_consumer
        self.tsdb = tsdb_client

    async def process_metrics(self, event: dict):
        """Process metric event and store in TimescaleDB."""

        # Parse metric
        metric = {
            "time": event["timestamp"],
            "metric_name": event["metric_name"],
            "ci_id": event.get("ci_id"),
            "asset_id": event.get("asset_id"),
            "source": event["source_system"],
            "value": float(event["payload"]["value"]),
            "unit": event["payload"].get("unit"),
            "tags": event.get("metadata", {}).get("tags", {})
        }

        # Insert into TimescaleDB
        await self.tsdb.execute("""
            INSERT INTO metrics (time, metric_name, ci_id, asset_id, source, value, unit, tags)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """, metric["time"], metric["metric_name"], metric["ci_id"],
             metric["asset_id"], metric["source"], metric["value"],
             metric["unit"], json.dumps(metric["tags"]))

        # Trigger anomaly detection (async)
        await self._check_anomaly(metric)

    async def _check_anomaly(self, metric: dict):
        """Check metric for anomalies."""
        # Query recent values for this metric
        recent = await self.tsdb.fetch("""
            SELECT value FROM metrics
            WHERE metric_name = $1 AND source = $2
            AND time > NOW() - INTERVAL '1 hour'
            ORDER BY time DESC LIMIT 100
        """, metric["metric_name"], metric["source"])

        values = [r["value"] for r in recent]
        values.append(metric["value"])

        # Z-score check
        if len(values) >= 20:
            import statistics
            mean = statistics.mean(values[:-1])
            stdev = statistics.stdev(values[:-1])
            if stdev > 0:
                z_score = abs(metric["value"] - mean) / stdev
                if z_score > 3.0:
                    await self._emit_anomaly(metric, z_score, mean, stdev)
```

---

## 3. Anomaly Detection

### 3.1 Detection Methods

| Method | Type | Use Case | Latency |
|--------|------|----------|---------|
| Z-score | Univariate | Single metric threshold | Real-time |
| Isolation Forest | Multivariate | Multi-metric pattern | Near real-time |
| Moving Average | Trend | Slow drift detection | Batch (5min) |
| Seasonal Decomposition | Pattern | Daily/weekly patterns | Batch (hourly) |

### 3.2 Z-score Implementation

```python
# analytics/anomaly_detection.py

import numpy as np
from typing import Tuple

class ZScoreDetector:
    def __init__(self, window_size: int = 100, threshold: float = 3.0):
        self.window_size = window_size
        self.threshold = threshold

    def detect(self, values: list, current: float) -> Tuple[bool, float]:
        """Detect anomaly using Z-score."""
        if len(values) < 20:
            return False, 0.0

        recent = values[-self.window_size:]
        mean = np.mean(recent)
        std = np.std(recent)

        if std == 0:
            return False, 0.0

        z_score = abs(current - mean) / std
        is_anomaly = z_score > self.threshold

        return is_anomaly, z_score
```

### 3.3 Isolation Forest Implementation

```python
from sklearn.ensemble import IsolationForest
import numpy as np

class IsolationForestDetector:
    def __init__(self, contamination: float = 0.01):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.is_trained = False

    def train(self, X: np.ndarray):
        """Train on historical data."""
        self.model.fit(X)
        self.is_trained = True

    def predict(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Predict anomalies. Returns (labels, scores)."""
        if not self.is_trained:
            raise ValueError("Model not trained")

        labels = self.model.predict(X)  # -1 = anomaly, 1 = normal
        scores = self.model.decision_function(X)  # Lower = more anomalous

        return labels, scores
```

### 3.4 Anomaly Alert Schema

```json
{
  "anomaly_id": "uuid",
  "timestamp": "2026-06-23T14:30:00Z",
  "metric_name": "cpu_usage_percent",
  "ci_id": "CI-SERVER-001",
  "asset_id": "AST-001",
  "detection_method": "z_score",
  "current_value": 95.5,
  "expected_range": [20.0, 60.0],
  "z_score": 4.2,
  "anomaly_score": 0.95,
  "severity": "high",
  "description": "CPU usage spike detected: 95.5% (normal: 20-60%)",
  "possible_causes": ["process runaway", "ddos attack", "resource contention"],
  "recommended_actions": ["check running processes", "review network traffic"]
}
```

---

## 4. Predictive Maintenance

### 4.1 Prediction Models

| Model | Use Case | Input | Output | Training |
|-------|----------|-------|--------|----------|
| Prophet | Trend forecasting | Time-series | Future values | Weekly |
| LSTM | Sequential pattern | Time-series sequence | Failure probability | Monthly |
| Survival Analysis | Time-to-failure | Event history | Remaining life | Quarterly |
| Random Forest | Multi-factor | Features | Risk score | Monthly |

### 4.2 Failure Prediction Schema

```json
{
  "prediction_id": "uuid",
  "ci_id": "CI-SERVER-001",
  "asset_id": "AST-001",
  "prediction_type": "failure_probability",
  "model": "lstm_v2.1",
  "predicted_at": "2026-06-23T14:30:00Z",
  "prediction_window": "30_days",
  "failure_probability": 0.72,
  "confidence": 0.85,
  "risk_level": "high",
  "contributing_factors": [
    {"factor": "disk_health_declining", "weight": 0.35},
    {"factor": "age_above_threshold", "weight": 0.25},
    {"factor": "recent_errors", "weight": 0.20},
    {"factor": "temperature_trend", "weight": 0.20}
  ],
  "recommended_actions": [
    "Schedule disk replacement within 2 weeks",
    "Monitor temperature closely",
    "Run diagnostic tests"
  ],
  "maintenance_window": {
    "earliest": "2026-06-30",
    "latest": "2026-07-07",
    "estimated_duration_hours": 4
  }
}
```

### 4.3 Maintenance Optimization

```python
class MaintenanceOptimizer:
    def optimize_schedule(self, predictions: list, constraints: dict) -> list:
        """Optimize maintenance schedule based on predictions."""

        # Sort by urgency (failure probability / time)
        urgent = sorted(predictions, key=lambda p: p["failure_probability"], reverse=True)

        schedule = []
        current_date = datetime.now()

        for pred in urgent:
            if pred["failure_probability"] > 0.7:
                # Critical: schedule within 7 days
                schedule.append({
                    "ci_id": pred["ci_id"],
                    "priority": "critical",
                    "scheduled_date": current_date + timedelta(days=1),
                    "reason": f"High failure probability: {pred['failure_probability']:.0%}"
                })
            elif pred["failure_probability"] > 0.4:
                # Warning: schedule within 30 days
                schedule.append({
                    "ci_id": pred["ci_id"],
                    "priority": "high",
                    "scheduled_date": current_date + timedelta(days=14),
                    "reason": f"Moderate failure probability: {pred['failure_probability']:.0%}"
                })

        return schedule
```

---

## 5. Root Cause Analysis (RCA)

### 5.1 RCA Pipeline

```
Incident/Anomaly Detected
  → Timeline Reconstruction (what happened when)
  → Event Correlation (related events)
  → Metric Correlation (related metrics)
  → Topology Traversal (what's connected)
  → Root Cause Hypothesis Generation
  → Confidence Scoring
  → Recommended Remediation
```

### 5.2 RCA Implementation

```python
# analytics/rca_engine.py

class RCAEngine:
    def __init__(self, es_client, tsdb_client, cmdb_client, kafka_producer):
        self.es = es_client
        self.tsdb = tsdb_client
        self.cmdb = cmdb_client
        self.kafka = kafka_producer

    async def analyze(self, incident_id: str, ci_id: str, timeframe_minutes: int = 60) -> dict:
        """Perform root cause analysis for an incident."""

        # 1. Timeline reconstruction
        timeline = await self._reconstruct_timeline(ci_id, timeframe_minutes)

        # 2. Event correlation
        correlated_events = await self._correlate_events(ci_id, timeframe_minutes)

        # 3. Metric correlation
        correlated_metrics = await self._correlate_metrics(ci_id, timeframe_minutes)

        # 4. Topology traversal
        dependencies = await self._traverse_topology(ci_id, depth=3)

        # 5. Generate hypotheses
        hypotheses = self._generate_hypotheses(
            timeline, correlated_events, correlated_metrics, dependencies
        )

        # 6. Score confidence
        scored_hypotheses = self._score_hypotheses(hypotheses)

        return {
            "incident_id": incident_id,
            "ci_id": ci_id,
            "timeline": timeline,
            "correlated_events": correlated_events,
            "correlated_metrics": correlated_metrics,
            "dependencies": dependencies,
            "hypotheses": scored_hypotheses,
            "top_hypothesis": scored_hypotheses[0] if scored_hypotheses else None,
            "recommended_action": self._get_remediation(scored_hypotheses[0]) if scored_hypotheses else "Manual investigation required"
        }

    async def _reconstruct_timeline(self, ci_id: str, minutes: int) -> list:
        """Reconstruct event timeline for CI."""

        events = await self.es.search(
            index="dcim-siem-*,dcim-events-*",
            query={
                "bool": {
                    "must": [
                        {"term": {"ci_id": ci_id}},
                        {"range": {"timestamp": {"gte": f"now-{minutes}m"}}}
                    ]
                }
            },
            sort=[{"timestamp": {"order": "asc"}}],
            size=100
        )

        return [hit["_source"] for hit in events["hits"]["hits"]]

    async def _traverse_topology(self, ci_id: str, depth: int) -> dict:
        """Traverse CMDB topology to find dependencies."""

        topology = await self.cmdb.get_topology(ci_id, depth=depth)

        # Focus on upstream dependencies (what this CI depends on)
        upstream = [n for n in topology["nodes"] if n["depth"] > 0]

        return {
            "upstream_dependencies": upstream,
            "total_dependencies": len(upstream),
            "critical_dependencies": [n for n in upstream if n.get("criticality") == "critical"]
        }

    def _generate_hypotheses(self, timeline, events, metrics, dependencies) -> list:
        """Generate root cause hypotheses."""

        hypotheses = []

        # Check for upstream failures
        for dep in dependencies.get("critical_dependencies", []):
            hypotheses.append({
                "cause": f"Upstream dependency failure: {dep['name']}",
                "confidence": 0.7,
                "evidence": f"CI depends on {dep['name']} which may be failing",
                "type": "dependency_failure"
            })

        # Check for metric anomalies
        for metric in metrics:
            if metric.get("anomaly"):
                hypotheses.append({
                    "cause": f"Metric anomaly: {metric['name']} = {metric['value']}",
                    "confidence": 0.6,
                    "evidence": f"{metric['name']} deviated from normal range",
                    "type": "metric_anomaly"
            })

        # Check for security events
        security_events = [e for e in events if e.get("category") in ("authentication", "malware")]
        for event in security_events:
            hypotheses.append({
                "cause": f"Security event: {event['title']}",
                "confidence": 0.5,
                "evidence": event.get("description", ""),
                "type": "security_event"
            })

        # Sort by confidence
        return sorted(hypotheses, key=lambda h: h["confidence"], reverse=True)
```

---

## 6. Capacity Forecasting

### 6.1 Metrics Monitored

| Metric | Source | Forecast Horizon | Alert Threshold |
|--------|--------|-----------------|-----------------|
| CPU usage | Prometheus | 30 days | > 80% projected |
| Memory usage | Prometheus | 30 days | > 85% projected |
| Disk usage | Prometheus | 90 days | > 90% projected |
| Network bandwidth | Prometheus | 30 days | > 80% projected |
| Power consumption | BMS/EPMS | 30 days | > 90% capacity |
| Cooling capacity | BMS | 30 days | > 85% capacity |
| Rack space | CMDB | 365 days | > 90% utilized |

### 6.2 Forecasting Models

| Model | Use Case | Accuracy | Speed |
|-------|----------|----------|-------|
| Linear Regression | Simple trend | Medium | Fast |
| Exponential Smoothing | Trend + seasonality | High | Fast |
| Prophet | Complex seasonality | High | Medium |
| ARIMA | Stationary time-series | High | Medium |

### 6.3 Capacity Report Schema

```json
{
  "report_id": "uuid",
  "generated_at": "2026-06-23T14:30:00Z",
  "resource_type": "storage",
  "scope": "datacenter-wide",
  "current_usage": {
    "total_tb": 100,
    "used_tb": 65,
    "utilization_pct": 65.0
  },
  "forecast": {
    "model": "exponential_smoothing",
    "horizon_days": 90,
    "projections": [
      {"date": "2026-07-23", "projected_tb": 72, "confidence_low": 68, "confidence_high": 76},
      {"date": "2026-08-23", "projected_tb": 79, "confidence_low": 73, "confidence_high": 85},
      {"date": "2026-09-23", "projected_tb": 87, "confidence_low": 79, "confidence_high": 95}
    ],
    "exhaustion_date": "2026-11-15",
    "days_until_90pct": 143
  },
  "alerts": [
    {"threshold": 90, "projected_date": "2026-11-15", "severity": "warning"}
  ],
  "recommendations": [
    "Add 20TB storage by October 2026",
    "Implement data archival for cold data",
    "Review retention policies"
  ]
}
```

---

## 7. Energy Optimization

### 7.1 Key Metrics

| Metric | Formula | Target | Alert |
|--------|---------|--------|-------|
| PUE | Total Facility Power / IT Equipment Power | < 1.4 | > 1.6 |
| Cooling Efficiency | Cooling Power / IT Equipment Power | < 0.4 | > 0.6 |
| Power Load Balance | Max(PDU) / Avg(PDU) | < 1.2 | > 1.5 |
| Carbon Intensity | CO2 (kg) / IT Power (kWh) | < 0.5 | > 0.7 |

### 7.2 PUE Calculation

```python
class EnergyOptimizer:
    def calculate_pue(self, total_power: float, it_power: float) -> dict:
        """Calculate Power Usage Effectiveness."""

        pue = total_power / it_power if it_power > 0 else 0
        overhead = total_power - it_power

        return {
            "pue": round(pue, 2),
            "total_power_kw": total_power,
            "it_power_kw": it_power,
            "overhead_power_kw": overhead,
            "overhead_pct": round((overhead / total_power) * 100, 1),
            "rating": self._rate_pue(pue),
            "annual_cost_impact": self._calculate_cost_impact(pue, it_power)
        }

    def _rate_pue(self, pue: float) -> str:
        if pue < 1.2:
            return "exceptional"
        elif pue < 1.4:
            return "good"
        elif pue < 1.6:
            return "average"
        elif pue < 2.0:
            return "poor"
        return "critical"

    def optimize_cooling(self, temperature_map: dict) -> dict:
        """Recommend cooling optimization."""

        recommendations = []

        for zone, temp in temperature_map.items():
            if temp > 27:
                recommendations.append({
                    "zone": zone,
                    "action": "increase_cooling",
                    "current_temp": temp,
                    "target_temp": 22,
                    "estimated_savings_kw": 2.5
                })
            elif temp < 18:
                recommendations.append({
                    "zone": zone,
                    "action": "reduce_cooling",
                    "current_temp": temp,
                    "target_temp": 22,
                    "estimated_savings_kw": 1.5
                })

        return {
            "recommendations": recommendations,
            "total_estimated_savings_kw": sum(r["estimated_savings_kw"] for r in recommendations)
        }
```

---

## 8. Model Training Pipeline

### 8.1 Pipeline Stages

```
1. Data Collection → TimescaleDB query (historical metrics)
2. Feature Engineering → Transform raw metrics to features
3. Data Splitting → Train/Validation/Test (70/15/15)
4. Model Training → Offline training (GPU optional)
5. Evaluation → Accuracy, precision, recall, F1
6. Model Registry → Version control + metadata
7. Deployment → Load model to scoring service
8. A/B Testing → Compare model versions
9. Monitoring → Track model drift
```

### 8.2 Model Registry Schema

```sql
CREATE TABLE ml_models (
    model_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,  -- 'isolation_forest', 'lstm', 'prophet', 'xgboost'
    version VARCHAR(20) NOT NULL,
    description TEXT,

    -- Training metadata
    trained_at TIMESTAMPTZ,
    training_data_size INTEGER,
    training_duration_seconds INTEGER,

    -- Performance metrics
    accuracy DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    auc_roc DECIMAL(5,4),

    -- Deployment
    status VARCHAR(20) DEFAULT 'registered'
        CHECK (status IN ('registered', 'staging', 'production', 'archived')),
    deployed_at TIMESTAMPTZ,

    -- Model artifact
    artifact_path VARCHAR(500),
    artifact_size_bytes BIGINT,

    -- Configuration
    hyperparameters JSONB,
    features_used JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 9. LLM/RAG Explanation Layer

### 9.1 Architecture

```
User Query
  → Intent Classification
    → RAG Retrieval (CMDB + Logs + Runbooks + Historical)
      → Context Assembly
        → LLM Generation (GPT-4 / Claude / Local LLM)
          → Response + Citations
```

### 9.2 RAG Knowledge Sources

| Source | Content | Update Frequency |
|--------|---------|-----------------|
| CMDB | CI data, relationships, topology | Real-time |
| Logs | Elasticsearch (dcim-logs-*) | Real-time |
| Runbooks | Markdown files in wiki | On change |
| Historical Incidents | Past incidents + resolutions | Daily |
| Metrics | TimescaleDB (recent + trends) | Real-time |
| Documentation | Wiki pages, API docs | Weekly |

### 9.3 Query Examples

```
Operator: "Why is web-server-01 showing high CPU?"

RAG Process:
1. Retrieve CI info from CMDB
2. Retrieve recent metrics from TimescaleDB
3. Retrieve recent incidents from Elasticsearch
4. Retrieve relevant runbooks
5. Assemble context
6. Generate explanation

Response: "web-server-01 (CI-SERVER-001) is experiencing high CPU (95.5% vs normal 40%).
Timeline: CPU started rising at 14:00. Correlated events: 3 OOM kills in the last hour.
Root cause hypothesis: Java application memory leak causing garbage collection storms.
Recommended action: Restart the application service and review memory allocation.
Reference: Runbook 'Java Memory Troubleshooting' (Section 3.2)."
```

### 9.4 API Design

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analytics/llm/query` | Ask natural language question |
| POST | `/api/v1/analytics/llm/explain` | Explain anomaly/prediction |
| GET | `/api/v1/analytics/llm/context/{ci_id}` | Get context for CI |
| GET | `/api/v1/analytics/llm/history` | Query history |

---

## 10. Performance & Sizing

### 10.1 Processing Capacity

| Component | Throughput | Latency p99 | Resource |
|-----------|------------|-------------|----------|
| Time-series ingestion | 1000 metrics/sec | < 100ms | 2 vCPU, 4GB |
| Z-score detection | 5000 checks/sec | < 10ms | 1 vCPU, 2GB |
| Isolation Forest | 100 predictions/sec | < 500ms | 2 vCPU, 4GB |
| Prophet forecast | 100 forecasts/min | < 10s | 2 vCPU, 4GB |
| RCA analysis | 10 analyses/min | < 30s | 2 vCPU, 4GB |
| LLM/RAG query | 20 queries/min | < 5s | 4 vCPU, 8GB + GPU |

### 10.2 Resource Allocation

| Component | vCPU | RAM | Storage | Instances |
|-----------|------|-----|---------|-----------|
| Time-series processor | 2 | 4 GB | — | 2 |
| Anomaly detection | 2 | 4 GB | — | 2 |
| Predictive maintenance | 2 | 4 GB | 10 GB (models) | 1 |
| RCA engine | 2 | 4 GB | — | 1 |
| Capacity forecasting | 1 | 2 GB | — | 1 |
| Energy optimization | 1 | 2 GB | — | 1 |
| Model training (offline) | 4 | 16 GB | 50 GB | 1 |
| LLM/RAG service | 4 | 8 GB | 20 GB (embeddings) | 1 |
| **Total** | **~20** | **~44 GB** | **~80 GB** | **~10** |

---

## 11. Security

| Control | Implementation |
|---------|---------------|
| Model artifacts | Encrypted at rest, access-controlled |
| Training data | Anonymized, no PII |
| LLM queries | Audit logged, no secrets in prompts |
| API access | RBAC (analytics.read, analytics.write, analytics.admin) |
| Secrets | Vault for API keys, model registry credentials |

---

## 12. Monitoring & Alerting

### 12.1 Key Metrics

| Metric | Type | Description |
|--------|------|-------------|
| `analytics_metrics_ingested_total` | Counter | Metrics processed |
| `analytics_anomalies_detected_total` | Counter | Anomalies detected |
| `analytics_predictions_generated_total` | Counter | Predictions made |
| `analytics_rca_analyses_total` | Counter | RCA analyses |
| `analytics_model_accuracy` | Gauge | Current model accuracy |
| `analytics_model_drift_score` | Gauge | Model drift indicator |
| `analytics_llm_query_latency_seconds` | Histogram | LLM response time |
| `analytics_timeseries_query_latency_seconds` | Histogram | TS query time |

### 12.2 Alert Rules

```yaml
groups:
  - name: analytics-ai
    rules:
      - alert: AnalyticsAnomalyRateHigh
        expr: rate(analytics_anomalies_detected_total[1h]) > 50
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "High anomaly detection rate: {{ $value }}/hour"

      - alert: AnalyticsModelAccuracyLow
        expr: analytics_model_accuracy < 0.8
        for: 7d
        labels:
          severity: warning
        annotations:
          summary: "Model accuracy dropped below 80%"

      - alert: AnalyticsModelDrift
        expr: analytics_model_drift_score > 0.15
        for: 7d
        labels:
          severity: warning
        annotations:
          summary: "Model drift detected, retraining recommended"

      - alert: AnalyticsLLMLatencyHigh
        expr: histogram_quantile(0.99, rate(analytics_llm_query_latency_seconds_bucket[5m])) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "LLM query p99 latency > 10s"
```

---

## 13. Acceptance Criteria — Block 7 Complete

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | Time-series pipeline working | Kafka → TimescaleDB flow tested | ⬜ |
| 2 | TimescaleDB hypertable created | Metrics stored, compressed | ⬜ |
| 3 | Continuous aggregates working | Hourly/daily views populated | ⬜ |
| 4 | Z-score anomaly detection | Detects threshold violations | ⬜ |
| 5 | Isolation Forest working | Trained model detects anomalies | ⬜ |
| 6 | Real-time anomaly scoring | Kafka → scoring → alert flow | ⬜ |
| 7 | Predictive maintenance (Prophet) | 30-day forecast generated | ⬜ |
| 8 | Predictive maintenance (LSTM) | Failure probability scored | ⬜ |
| 9 | RCA engine working | Incident → root cause identified | ⬜ |
| 10 | Capacity forecasting working | 30/90-day projections | ⬜ |
| 11 | Energy optimization working | PUE calculated, recommendations | ⬜ |
| 12 | Model training pipeline | End-to-end training flow | ⬜ |
| 13 | Model registry working | Version control + deployment | ⬜ |
| 14 | LLM/RAG working | NL query returns contextual answer | ⬜ |
| 15 | Monitoring dashboards | Grafana analytics views | ⬜ |
| 16 | Alert rules active | Test alert fires | ⬜ |

---

## 14. Gap Comparison Template

### Gap: [Component Name]

| Aspect | Reference Design | Actual Implementation | Gap | Priority |
|--------|-----------------|----------------------|-----|----------|
| Time-series | [spec DB] | [aktual DB] | [match/mismatch] | P1-P4 |
| Anomaly detection | [spec methods] | [aktual methods] | [gap detail] | P1-P4 |
| Predictive maint. | [spec models] | [aktual models] | [gap detail] | P1-P4 |
| RCA | [spec pipeline] | [aktual pipeline] | [gap detail] | P1-P4 |
| Capacity | [spec metrics] | [aktual metrics] | [gap detail] | P1-P4 |
| Energy | [spec formulas] | [aktual formulas] | [gap detail] | P1-P4 |
| Model training | [spec pipeline] | [aktual pipeline] | [gap detail] | P1-P4 |
| LLM/RAG | [spec architecture] | [aktual architecture] | [gap detail] | P1-P4 |
| Performance | [spec targets] | [aktual metrics] | [gap detail] | P1-P4 |

**Decision:** [adopt spec / keep actual / hybrid]
**Rationale:** [why]
**Action items:** [what to do]

---

## References

- [[analytics-ai-engine]]
- [[cmdb]] — topology for RCA
- [[data-ingestion-integration]] — metric streams
- [[web-dashboard]] — visualization
- [[workflow-automation]] — alert workflows
- [[time-series-db-comparison]]
- [[ml-framework-comparison]]
- [[llm-rag-explanation-layer]]
- [[capacity-planning-runbook]]
- [[energy-optimization-strategy]]
- [[dcim-core-platform]]

---

> **Status:** Generated by Hermes DCIM Orchestrator
> **Date:** 2026-06-23
> **Purpose:** Reference for team comparison → gap identification → connection dots
> **Phase 2 Progress:** B5 ✅ → B6 ✅ → B7 ✅ → B8 ⬜ → B9 ⬜
