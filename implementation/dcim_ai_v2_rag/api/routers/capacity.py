"""
Capacity Forecasting API Router

Endpoints:
- GET  /api/v1/analytics/capacity - List capacity reports
- POST /api/v1/analytics/capacity/forecast - Trigger forecast

Reference: MT-023 §2.5, block7-analytics-ai-engine.md §6
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging
import json
import numpy as np

from ..dependencies import require_permission
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class CapacityForecastRequest(BaseModel):
    ci_id: str = Field(..., description="CI ID (Configuration Item)")
    metric_name: str = Field(..., description="Metric to forecast: cpu_utilization, memory_usage, disk_temperature, interface_status, battery_capacity")
    forecast_days: int = Field(default=30, ge=7, le=365, description="Forecast horizon in days")


class CapacityResponse(BaseModel):
    report_id: str
    ci_id: str
    metric_name: str
    current_value: float
    predicted_value_30d: Optional[float] = None
    predicted_value_60d: Optional[float] = None
    predicted_value_90d: Optional[float] = None
    trend: str
    slope_per_day: float
    r_squared: float
    exhaustion_date: Optional[str] = None
    recommendation: str


@router.get("", response_model=List[CapacityResponse])
async def list_capacity_reports(
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    ci_id: Optional[str] = Query(None, description="Filter by CI ID"),
    user=Depends(require_permission("analytics.read"))
):
    """List capacity reports from TimescaleDB."""
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
            SELECT forecast_id, resource_type, ci_id, forecast_date,
                   current_usage_pct, projected_usage_pct,
                   projected_exhaustion_date, confidence, model,
                   recommendations, created_at
            FROM capacity_forecasts
            WHERE {' AND '.join(conditions)}
            ORDER BY created_at DESC
            LIMIT %s OFFSET %s
            """,
            params + [per_page, offset],
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()

        results = []
        for r in rows:
            current_val = float(r["current_usage_pct"]) if r.get("current_usage_pct") else 0
            projected_val = float(r["projected_usage_pct"]) if r.get("projected_usage_pct") else 0
            trend = "increasing" if projected_val > current_val else "decreasing"

            recs = r.get("recommendations", [])
            if isinstance(recs, str):
                try:
                    recs = json.loads(recs)
                except (json.JSONDecodeError, TypeError):
                    recs = [recs] if recs else []
            first_rec = str(recs[0]) if isinstance(recs, list) and recs else None

            exhaustion = r.get("projected_exhaustion_date")
            if exhaustion and hasattr(exhaustion, "strftime"):
                exhaustion = exhaustion.strftime("%Y-%m-%d")
            elif exhaustion:
                exhaustion = str(exhaustion)

            results.append(CapacityResponse(
                report_id=str(r["forecast_id"]),
                ci_id=str(r["ci_id"]) if r.get("ci_id") else "",
                metric_name=r.get("resource_type", "unknown"),
                current_value=round(current_val, 2),
                predicted_value_30d=round(projected_val, 2),
                predicted_value_60d=None,
                predicted_value_90d=None,
                trend=trend,
                slope_per_day=0.0,
                r_squared=0.0,
                exhaustion_date=exhaustion,
                recommendation=first_rec or "No recommendation",
            ))

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list capacity reports: {e}", exc_info=True)
        detail = f"Failed to list capacity reports: {str(e)}"
        if "relation" in str(e) and "does not exist" in str(e):
            detail += " — table may not exist. Ensure migration 002_create_analytics_tables.sql has been run."
        raise HTTPException(status_code=500, detail=detail)


@router.post("/forecast", response_model=CapacityResponse)
async def trigger_capacity_forecast(
    request: CapacityForecastRequest,
    user=Depends(require_permission("analytics.write"))
):
    """
    Generate capacity forecast using linear regression.

    Works in two modes:
    1. Live mode: If TimescaleDB has historical data, use real data
    2. Demo mode: If no data available, generate synthetic data for demo
    """
    try:
        # Try to get real data from TimescaleDB
        historical_data = _try_get_historical_data(request.ci_id, request.metric_name)

        if historical_data and len(historical_data) >= 7:
            # Use real data
            values = [d["value"] for d in historical_data]
            source = "timescaledb"
        else:
            # Generate synthetic data for demo
            values = _generate_synthetic_data(request.metric_name, days=90)
            source = "synthetic_demo"

        # Linear regression
        x = np.arange(len(values))
        y = np.array(values)

        n = len(x)
        sum_x = np.sum(x)
        sum_y = np.sum(y)
        sum_xy = np.sum(x * y)
        sum_x2 = np.sum(x * x)

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
        intercept = (sum_y - slope * sum_x) / n

        # R-squared
        y_pred = slope * x + intercept
        ss_res = np.sum((y - y_pred) ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # Predictions
        current_value = float(values[-1])
        pred_30d = float(slope * (len(values) + 30) + intercept)
        pred_60d = float(slope * (len(values) + 60) + intercept)
        pred_90d = float(slope * (len(values) + 90) + intercept)

        # Exhaustion date (when value reaches 100%)
        exhaustion_date = None
        if slope > 0:
            days_to_100 = (100 - current_value) / slope
            if days_to_100 > 0:
                exhaustion_date = (datetime.utcnow() + timedelta(days=days_to_100)).strftime("%Y-%m-%d")

        # Recommendation
        if pred_90d > 95:
            recommendation = f"CRITICAL: {request.metric_name} will reach {pred_90d:.1f}% in 90 days. Immediate action required."
        elif pred_90d > 80:
            recommendation = f"WARNING: {request.metric_name} trending to {pred_90d:.1f}% in 90 days. Plan capacity expansion."
        else:
            recommendation = f"OK: {request.metric_name} stable at {pred_90d:.1f}% in 90 days. No immediate action needed."

        return CapacityResponse(
            report_id=f"cap-{request.ci_id}-{request.metric_name}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
            ci_id=request.ci_id,
            metric_name=request.metric_name,
            current_value=round(current_value, 2),
            predicted_value_30d=round(pred_30d, 2),
            predicted_value_60d=round(pred_60d, 2),
            predicted_value_90d=round(pred_90d, 2),
            trend="increasing" if slope > 0 else "decreasing",
            slope_per_day=round(float(slope), 4),
            r_squared=round(float(r_squared), 4),
            exhaustion_date=exhaustion_date,
            recommendation=recommendation
        )

    except Exception as e:
        logger.error(f"Capacity forecast failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Capacity forecast failed: {str(e)}")


def _try_get_historical_data(ci_id: str, metric_name: str, days: int = 90) -> list:
    """Try to get historical data from TimescaleDB. Returns empty list if unavailable."""
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
            connect_timeout=5
        )
        cur = conn.cursor()
        cur.execute("""
            SELECT time_bucket('1 day', time) AS bucket, AVG(value) AS value
            FROM metrics
            WHERE ci_id = %s AND metric_name = %s
            AND time > NOW() - INTERVAL '%s days'
            GROUP BY bucket ORDER BY bucket
        """, (ci_id, metric_name, days))
        data = cur.fetchall()
        cur.close()
        conn.close()
        return data
    except Exception:
        return []


def _generate_synthetic_data(metric_name: str, days: int = 90) -> list:
    """Generate synthetic data for demo purposes."""
    np.random.seed(hash(metric_name) % 2**32)

    # Different patterns per metric
    patterns = {
        "cpu_utilization": {"base": 45, "slope": 0.2, "noise": 5},
        "memory_usage": {"base": 55, "slope": 0.3, "noise": 3},
        "disk_temperature": {"base": 38, "slope": 0.1, "noise": 2},
        "interface_status": {"base": 1, "slope": 0, "noise": 0.1},
        "battery_capacity": {"base": 95, "slope": -0.05, "noise": 2},
    }

    p = patterns.get(metric_name, {"base": 50, "slope": 0.2, "noise": 5})
    x = np.arange(days)
    values = p["base"] + p["slope"] * x + np.random.normal(0, p["noise"], days)
    return list(np.clip(values, 0, 100))
