"""
Predictive Maintenance API Router

Endpoints:
- GET  /api/v1/analytics/predictions - List predictions
- POST /api/v1/analytics/predictions/forecast - Trigger failure probability forecast

Reference: MT-023 §2.3, block7-analytics-ai-engine.md §4
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid
import json
import os
import sys

import numpy as np

from ..dependencies import require_permission
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class ForecastRequest(BaseModel):
    ci_id: str = Field(..., description="CI ID (Configuration Item)")
    metric_names: Optional[List[str]] = Field(
        default=["cpu_utilization", "memory_usage", "disk_temperature", "interface_status", "battery_capacity"],
        description="Metrics to forecast"
    )


class PredictionResponse(BaseModel):
    prediction_id: str
    ci_id: str
    prediction_type: str
    failure_probability: float
    confidence: float
    model_version: Optional[str] = None
    severity: Optional[str] = None
    contributing_factors: List[str] = []
    recommendation: Optional[str] = None
    timestamp: str


# ─── Model loader ────────────────────────────────────────

_model_cache: Optional[Dict[str, Any]] = None


def _load_model_ensemble() -> Dict[str, Any]:
    """Load IF/LOF/OCSVM ensemble with hot-reload awareness."""
    global _model_cache
    if _model_cache is not None:
        return _model_cache

    try:
        # Try ModelManager path first
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
        from inference.model_manager import ModelManager

        mgr = ModelManager()
        models, pipeline, baseline_stats, version, corr_config = mgr.get()
        _model_cache = {
            "models": models,
            "pipeline": pipeline,
            "baseline_stats": baseline_stats,
            "version": version,
            "loaded": True,
        }
        return _model_cache

    except Exception as e1:
        logger.warning(f"ModelManager failed: {e1}. Trying direct load...")

    try:
        import joblib
        from pathlib import Path

        models_dir = Path("/home/infra/dcim_project/implementation/dcim_ai_v2_rag/artifacts/models")
        registry_path = Path("/home/infra/dcim_project/implementation/dcim_ai_v2_rag/registry/registry.json")

        if registry_path.exists():
            registry = json.loads(registry_path.read_text())
            version = registry.get("current_production", "v1.4")
        else:
            version = "v1.4"

        version_dir = models_dir / version
        models_path = version_dir / "models.pkl"
        pipeline_path = version_dir / "pipeline.pkl"
        baseline_path = version_dir / "baseline_stats.json"

        if models_path.exists():
            models = joblib.load(str(models_path))
            pipeline = joblib.load(str(pipeline_path))
            baseline = json.loads(baseline_path.read_text())
            _model_cache = {
                "models": models, "pipeline": pipeline,
                "baseline_stats": baseline, "version": version,
                "loaded": True,
            }
            return _model_cache
    except Exception as e2:
        logger.warning(f"Direct model load failed: {e2}")

    return {"loaded": False}


def _compute_failure_probability(metrics: Dict[str, float], model_data: Dict) -> Dict[str, Any]:
    """Run IF/LOF/OCSVM ensemble voting on provided metrics."""
    if not model_data.get("loaded"):
        return _fallback_forecast(metrics)

    try:
        import pandas as pd

        models = model_data["models"]
        pipeline = model_data["pipeline"]
        baseline = model_data["baseline_stats"]

        df = pd.DataFrame([metrics])
        df = df[pipeline.feature_columns]

        X = pipeline.transform(df)

        iso_pred = models["isolation_forest"].predict(X)[0]
        lof_pred = models["local_outlier_factor"].predict(X)[0]
        svm_pred = models["one_class_svm"].predict(X)[0]

        iso_score = float(models["isolation_forest"].decision_function(X)[0])
        lof_score = float(models["local_outlier_factor"].decision_function(X)[0])
        svm_score = float(models["one_class_svm"].decision_function(X)[0])

        votes = sum(1 for p in [iso_pred, lof_pred, svm_pred] if p == -1)
        is_anomaly = votes >= 2

        avg_score = (iso_score + lof_score + svm_score) / 3
        failure_probability = 1.0 / (1.0 + np.exp(avg_score / 0.5))

        # Drift check
        raw = df[pipeline.feature_columns].values[0]
        z_scores = []
        for i, feat in enumerate(pipeline.feature_columns):
            b_mean = baseline["mean"][i]
            b_std = baseline["std"][i]
            z = abs((raw[i] - b_mean) / b_std) if b_std > 0 else 0
            z_scores.append((feat, z))

        drift_score = float(np.mean([z for _, z in z_scores]))
        top_contributors = sorted(z_scores, key=lambda x: x[1], reverse=True)[:3]

        if votes == 3:
            severity = "critical"
        elif votes == 2:
            severity = "warning"
        elif votes == 1:
            severity = "weak_signal"
        else:
            severity = "normal"

        return {
            "is_anomaly": is_anomaly,
            "failure_probability": round(failure_probability, 4),
            "confidence": max(0.3, 1.0 - abs(avg_score) / 2),
            "severity": severity,
            "model_votes": {
                "isolation_forest": int(iso_pred),
                "local_outlier_factor": int(lof_pred),
                "one_class_svm": int(svm_pred),
                "anomaly_votes": votes,
            },
            "drift_score": round(drift_score, 4),
            "contributing_factors": [
                f"{feat} (z={z:.2f})" for feat, z in top_contributors
            ],
            "model_version": model_data.get("version", "unknown"),
        }
    except Exception as e:
        logger.error(f"Ensemble forecast failed: {e}", exc_info=True)
        return _fallback_forecast(metrics)


def _fallback_forecast(metrics: Dict[str, float]) -> Dict[str, Any]:
    """Simple heuristic when model is unavailable."""
    risk = 0.0
    factors = []

    if metrics.get("cpu_utilization", 0) > 90:
        risk += 0.3
        factors.append("cpu_utilization (>90%)")
    if metrics.get("memory_usage", 0) > 90:
        risk += 0.3
        factors.append("memory_usage (>90%)")
    if metrics.get("disk_temperature", 0) > 800000:
        risk += 0.2
        factors.append("disk_temperature high")
    if metrics.get("interface_status", 0) < 100:
        risk += 0.1
        factors.append("interface_status low (possible network issue)")

    risk = min(risk, 0.95)
    return {
        "is_anomaly": risk > 0.3,
        "failure_probability": round(risk, 4),
        "confidence": 0.4,
        "severity": "critical" if risk > 0.7 else ("warning" if risk > 0.3 else "normal"),
        "model_votes": {},
        "drift_score": 0,
        "contributing_factors": factors,
        "model_version": "fallback-heuristic",
    }


# ─── GET /predictions ────────────────────────────────────

@router.get("", response_model=List[PredictionResponse])
async def list_predictions(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    ci_id: Optional[str] = Query(None),
    user=Depends(require_permission("analytics.read")),
):
    """List predictions from database."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(
            host=settings.TIMESCALEDB_HOST,
            port=settings.TIMESCALEDB_PORT,
            database=settings.TIMESCALEDB_DATABASE,
            user=settings.TIMESCALEDB_USER,
            password=settings.TIMESCALEDB_PASSWORD,
            cursor_factory=RealDictCursor,
            connect_timeout=5,
        )
        cur = conn.cursor()

        conditions = ["1=1"]
        params = []
        if ci_id:
            conditions.append("ci_id = %s")
            params.append(ci_id)

        offset = (page - 1) * per_page
        cur.execute(
            f"""
            SELECT prediction_id, ci_id, prediction_type, failure_probability,
                   confidence, model_version, risk_level, contributing_factors,
                   recommended_actions, predicted_at
            FROM predictions
            WHERE {' AND '.join(conditions)}
            ORDER BY predicted_at DESC
            LIMIT %s OFFSET %s
            """,
            params + [per_page, offset],
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        return [
            PredictionResponse(
                prediction_id=str(r["prediction_id"]),
                ci_id=str(r["ci_id"]) if r.get("ci_id") else "",
                prediction_type=r.get("prediction_type", "failure_probability"),
                failure_probability=float(r["failure_probability"]),
                confidence=float(r["confidence"]),
                model_version=r.get("model_version"),
                severity=r.get("risk_level"),
                contributing_factors=r.get("contributing_factors", []),
                recommendation=_extract_first_action(r.get("recommended_actions")),
                timestamp=r["predicted_at"].isoformat() if hasattr(r["predicted_at"], "isoformat") else str(r["predicted_at"]),
            )
            for r in rows
        ]
    except Exception as e:
        logger.error(f"Failed to list predictions: {e}", exc_info=True)
        detail = f"Failed to list predictions: {str(e)}"
        if "relation" in str(e) and "does not exist" in str(e):
            detail += " — table may not exist. Ensure migration 002_create_analytics_tables.sql has been run."
        raise HTTPException(status_code=500, detail=detail)


# ─── POST /predictions/forecast ──────────────────────────

@router.post("/forecast")
async def trigger_forecast(
    request: ForecastRequest,
    user=Depends(require_permission("analytics.write")),
):
    """
    Trigger predictive maintenance forecast.

    Uses IF/LOF/OCSVM ensemble to compute failure probability.
    Falls back to heuristic scoring if model is unavailable.
    Stores result in predictions table.
    """
    try:
        # Try to fetch live metrics from TimescaleDB
        metrics = _fetch_live_metrics(request.ci_id, request.metric_names)

        if not metrics:
            # Generate synthetic for demo
            metrics = _generate_synthetic_metrics(request.ci_id, request.metric_names)
            source = "synthetic"
        else:
            source = "timescaledb"

        # Run ensemble
        model_data = _load_model_ensemble()
        result = _compute_failure_probability(metrics, model_data)

        # Build response
        now = datetime.utcnow()
        prediction_id = str(uuid.uuid4())

        recommendation = _build_recommendation(result["severity"], result["contributing_factors"])

        # Store in DB
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor

            conn = psycopg2.connect(
                host=settings.TIMESCALEDB_HOST,
                port=settings.TIMESCALEDB_PORT,
                database=settings.TIMESCALEDB_DATABASE,
                user=settings.TIMESCALEDB_USER,
                password=settings.TIMESCALEDB_PASSWORD,
                connect_timeout=5,
            )
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO predictions (
                    prediction_id, ci_id, prediction_type,
                    model, model_version, predicted_at, prediction_window,
                    failure_probability, confidence, risk_level,
                    contributing_factors, recommended_actions
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    prediction_id, request.ci_id, "failure_probability",
                    "if_lof_ocsvm_ensemble", result.get("model_version", "unknown"),
                    now, "24h",
                    result["failure_probability"], result["confidence"],
                    result["severity"],
                    json.dumps(result["contributing_factors"]),
                    json.dumps([recommendation]),
                ),
            )
            conn.commit()
            cur.close()
            conn.close()
            stored = True
        except Exception as store_err:
            logger.warning(f"Failed to store prediction: {store_err}")
            stored = False

        return {
            "prediction_id": prediction_id,
            "ci_id": request.ci_id,
            "timestamp": now.isoformat(),
            "source": source,
            "stored": stored,
            **result,
            "recommendation": recommendation,
            "input_metrics": metrics,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Forecast failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Forecast failed: {str(e)}")


# ─── Helpers ─────────────────────────────────────────────

def _extract_first_action(recommended_actions) -> Optional[str]:
    """Extract first action from JSONB recommended_actions array."""
    if not recommended_actions:
        return None
    if isinstance(recommended_actions, str):
        try:
            recommended_actions = json.loads(recommended_actions)
        except (json.JSONDecodeError, TypeError):
            return recommended_actions
    if isinstance(recommended_actions, list) and len(recommended_actions) > 0:
        return str(recommended_actions[0])
    return str(recommended_actions) if recommended_actions else None


def _fetch_live_metrics(ci_id: str, metric_names: List[str]) -> Optional[Dict[str, float]]:
    """Fetch latest metric values from TimescaleDB."""
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor

        conn = psycopg2.connect(
            host=settings.TIMESCALEDB_HOST,
            port=settings.TIMESCALEDB_PORT,
            database=settings.TIMESCALEDB_DATABASE,
            user=settings.TIMESCALEDB_USER,
            password=settings.TIMESCALEDB_PASSWORD,
            cursor_factory=RealDictCursor,
            connect_timeout=5,
        )
        cur = conn.cursor()

        metrics = {}
        for m in metric_names:
            cur.execute(
                """
                SELECT value FROM metrics
                WHERE ci_id = %s AND metric_name = %s
                  AND time > NOW() - INTERVAL '6 hours'
                ORDER BY time DESC LIMIT 1
                """,
                (ci_id, m),
            )
            row = cur.fetchone()
            if row:
                metrics[m] = float(row["value"])

        cur.close()
        conn.close()

        return metrics if metrics else None
    except Exception:
        return None


def _generate_synthetic_metrics(ci_id: str, metric_names: List[str]) -> Dict[str, float]:
    """Generate synthetic metrics for demo."""
    import hashlib
    seed = int(hashlib.md5(ci_id.encode()).hexdigest()[:8], 16)
    rng = np.random.RandomState(seed % (2**31))

    patterns = {
        "cpu_utilization": (45, 20),
        "memory_usage": (55, 15),
        "disk_temperature": (500000, 200000),
        "interface_status": (200000, 80000),
        "battery_capacity": (90, 10),
    }

    result = {}
    for m in metric_names:
        base, spread = patterns.get(m, (50, 20))
        result[m] = round(float(base + rng.normal(0, spread / 3)), 2)
    return result


def _build_recommendation(severity: str, factors: List[str]) -> str:
    if severity == "critical":
        return (
            f"CRITICAL: Multiple models agree on anomaly ({', '.join(factors)}). "
            "Immediate investigation required. Check affected CI and correlate with "
            "recent changes, load patterns, and environmental conditions."
        )
    elif severity == "warning":
        return (
            f"WARNING: Anomaly indicators detected ({', '.join(factors)}). "
            "Schedule inspection within 24 hours. Monitor trend for escalation."
        )
    elif severity == "weak_signal":
        return (
            "WEAK SIGNAL: One model flagged potential issue. "
            "Continue monitoring. No immediate action required."
        )
    return "NORMAL: No failure indicators detected. Routine monitoring sufficient."
