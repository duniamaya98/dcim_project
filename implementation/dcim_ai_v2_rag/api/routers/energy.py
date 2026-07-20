"""
Energy Optimization API Router

Endpoints:
- GET  /api/v1/analytics/energy/pue - Get PUE calculation
- POST /api/v1/analytics/energy/optimize - Trigger optimization

Reference: MT-023 §2.6, block7-analytics-ai-engine.md §7
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from ..dependencies import require_permission
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


class PUEResponse(BaseModel):
    datacenter_id: str
    pue: float
    total_power_kw: float
    it_power_kw: float
    cooling_power_kw: float
    cooling_efficiency: float
    rating: str
    recommendations: List[str]
    carbon_intensity_kg_per_kwh: float = 0.85
    estimated_monthly_cost_usd: float = 0.0
    calculated_at: str


class OptimizationResponse(BaseModel):
    datacenter_id: str
    current_pue: float
    target_pue: float
    potential_savings_pct: float
    potential_savings_usd_per_month: float = 0.0
    carbon_reduction_kg_per_month: float = 0.0
    actions: List[Dict[str, Any]]
    estimated_monthly_savings_kwh: float


@router.get("/pue", response_model=PUEResponse)
async def get_pue(
    datacenter_id: str = Query(default="dc-001", description="Datacenter ID"),
    user=Depends(require_permission("analytics.read"))
):
    """
    Calculate PUE (Power Usage Effectiveness).

    Works in two modes:
    1. Live mode: If TimescaleDB has power metrics, calculate real PUE
    2. Demo mode: If no data available, use synthetic data for demo
    """
    try:
        # Try to get real data
        power_data = _try_get_power_metrics(datacenter_id)

        if power_data and power_data.get("total_power_kw", 0) > 0:
            total_power = power_data["total_power_kw"] / 1000.0  # Convert W to kW
            it_power = power_data["it_power_kw"] / 1000.0        # Convert W to kW
            source = "timescaledb"
        else:
            # Demo data
            total_power = 150.0  # kW total facility
            it_power = 100.0    # kW IT equipment
            source = "synthetic_demo"

        # Calculate PUE
        cooling_power = total_power - it_power
        pue = total_power / it_power if it_power > 0 else 999.0
        cooling_efficiency = it_power / cooling_power if cooling_power > 0 else 0

        # Rating
        if pue <= 1.2:
            rating = "excellent"
        elif pue <= 1.5:
            rating = "good"
        elif pue <= 2.0:
            rating = "average"
        else:
            rating = "inefficient"

        # Recommendations
        recommendations = _get_pue_recommendations(pue, rating, cooling_efficiency)

        # Carbon intensity (Indonesia grid average ~0.85 kg CO2/kWh)
        carbon_intensity = 0.85  # kg CO2/kWh
        electricity_rate_usd_per_kwh = 0.10  # Indonesia industrial rate ~$0.10/kWh
        monthly_cost = total_power * 24 * 30 * electricity_rate_usd_per_kwh

        return PUEResponse(
            datacenter_id=datacenter_id,
            pue=round(pue, 2),
            total_power_kw=round(total_power, 2),
            it_power_kw=round(it_power, 2),
            cooling_power_kw=round(cooling_power, 2),
            cooling_efficiency=round(cooling_efficiency, 2),
            rating=rating,
            recommendations=recommendations,
            carbon_intensity_kg_per_kwh=carbon_intensity,
            estimated_monthly_cost_usd=round(monthly_cost, 2),
            calculated_at=datetime.utcnow().isoformat()
        )

    except Exception as e:
        logger.error(f"PUE calculation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"PUE calculation failed: {str(e)}")


@router.post("/optimize", response_model=OptimizationResponse)
async def trigger_optimization(
    datacenter_id: str = Query(default="dc-001", description="Datacenter ID"),
    target_pue: float = Query(default=1.3, ge=1.0, le=3.0, description="Target PUE"),
    user=Depends(require_permission("analytics.write"))
):
    """
    Generate energy optimization recommendations.

    Analyzes current PUE and provides actionable steps to reach target PUE.
    """
    try:
        # Get current PUE
        power_data = _try_get_power_metrics(datacenter_id)

        if power_data and power_data.get("total_power_kw", 0) > 0:
            total_power = power_data["total_power_kw"] / 1000.0  # Convert W to kW
            it_power = power_data["it_power_kw"] / 1000.0        # Convert W to kW
        else:
            total_power = 150.0
            it_power = 100.0

        current_pue = total_power / it_power if it_power > 0 else 999.0
        cooling_power = total_power - it_power

        # Calculate savings
        if current_pue > target_pue:
            target_total = target_pue * it_power
            savings_kw = total_power - target_total
            savings_pct = (savings_kw / total_power) * 100
            monthly_savings_kwh = savings_kw * 24 * 30
        else:
            savings_kw = 0
            savings_pct = 0
            monthly_savings_kwh = 0

        electricity_rate = 0.10  # USD/kWh
        carbon_rate = 0.85  # kg CO2/kWh
        savings_usd = monthly_savings_kwh * electricity_rate
        carbon_reduction = monthly_savings_kwh * carbon_rate

        # Generate actions
        actions = _generate_optimization_actions(current_pue, target_pue, cooling_power, it_power)

        return OptimizationResponse(
            datacenter_id=datacenter_id,
            current_pue=round(current_pue, 2),
            target_pue=target_pue,
            potential_savings_pct=round(savings_pct, 2),
            potential_savings_usd_per_month=round(savings_usd, 2),
            carbon_reduction_kg_per_month=round(carbon_reduction, 2),
            actions=actions,
            estimated_monthly_savings_kwh=round(monthly_savings_kwh, 2)
        )

    except Exception as e:
        logger.error(f"Energy optimization failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Energy optimization failed: {str(e)}")


def _try_get_power_metrics(datacenter_id: str) -> dict:
    """Try to get power metrics from TimescaleDB. Returns empty dict if unavailable."""
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

        # Total facility power
        cur.execute("""
            SELECT AVG(value) as avg_value FROM metrics
            WHERE metric_name = 'total_facility_power'
            AND time > NOW() - INTERVAL '24 hours'
        """)
        total_row = cur.fetchone()
        total_power = float(total_row['avg_value']) if total_row and total_row['avg_value'] else 0

        # IT equipment power
        cur.execute("""
            SELECT AVG(value) as avg_value FROM metrics
            WHERE metric_name = 'it_equipment_power'
            AND time > NOW() - INTERVAL '24 hours'
        """)
        it_row = cur.fetchone()
        it_power = float(it_row['avg_value']) if it_row and it_row['avg_value'] else 0

        cur.close()
        conn.close()

        return {"total_power_kw": total_power, "it_power_kw": it_power}
    except Exception:
        return {}


def _get_pue_recommendations(pue: float, rating: str, cooling_efficiency: float) -> list:
    """Generate PUE improvement recommendations."""
    recs = []

    if rating == "inefficient":
        recs.append("URGENT: PUE > 2.0 indicates major inefficiency. Conduct full facility audit.")
        recs.append("Consider hot/cold aisle containment to improve airflow management.")
        recs.append("Evaluate free cooling options (outside air economizers).")
    elif rating == "average":
        recs.append("PUE can be improved. Review cooling set points (raise by 1-2°C).")
        recs.append("Implement variable speed drives on cooling fans and pumps.")
        recs.append("Consider in-row cooling units for high-density racks.")
    elif rating == "good":
        recs.append("Good PUE. Fine-tune cooling schedules to match load patterns.")
        recs.append("Consider LED lighting and occupancy sensors to reduce ancillary load.")
    else:
        recs.append("Excellent PUE. Maintain current practices and monitor for drift.")

    if cooling_efficiency < 1.0:
        recs.append("Cooling power exceeds IT load. Review cooling system efficiency.")

    return recs


def _generate_optimization_actions(current_pue: float, target_pue: float, cooling_kw: float, it_kw: float) -> list:
    """Generate specific optimization actions with estimated impact."""
    actions = []

    if current_pue <= target_pue:
        actions.append({
            "action": "No optimization needed",
            "category": "maintain",
            "estimated_pue_impact": 0,
            "priority": "low",
            "description": f"Current PUE ({current_pue:.2f}) already meets target ({target_pue:.2f})"
        })
        return actions

    # Action 1: Raise temperature set points
    temp_impact = min(0.1, (current_pue - target_pue) * 0.3)
    actions.append({
        "action": "Raise cooling set points by 2°C",
        "category": "cooling",
        "estimated_pue_impact": round(temp_impact, 2),
        "priority": "high",
        "description": "Increasing server inlet temperature from 20°C to 22°C reduces cooling load"
    })

    # Action 2: Implement hot/cold aisle containment
    containment_impact = min(0.15, (current_pue - target_pue) * 0.4)
    actions.append({
        "action": "Implement hot aisle containment",
        "category": "airflow",
        "estimated_pue_impact": round(containment_impact, 2),
        "priority": "high",
        "description": "Physical barriers prevent hot exhaust air from mixing with cold supply air"
    })

    # Action 3: Variable speed drives
    vsd_impact = min(0.08, (current_pue - target_pue) * 0.2)
    actions.append({
        "action": "Install variable speed drives on cooling fans",
        "category": "cooling",
        "estimated_pue_impact": round(vsd_impact, 2),
        "priority": "medium",
        "description": "VSD fans adjust speed based on actual cooling demand instead of running at full speed"
    })

    # Action 4: Free cooling
    if cooling_kw > it_kw * 0.5:
        free_cooling_impact = min(0.2, (current_pue - target_pue) * 0.5)
        actions.append({
            "action": "Implement free cooling (economizer mode)",
            "category": "cooling",
            "estimated_pue_impact": round(free_cooling_impact, 2),
            "priority": "medium",
            "description": "Use outside air for cooling when ambient temperature is below 18°C"
        })

    return actions
