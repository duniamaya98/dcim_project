"""
Root Cause Analysis (RCA) API Router

Endpoints:
- POST /api/v1/analytics/rca/analyze - Trigger RCA analysis
- GET  /api/v1/analytics/rca/{id} - Get RCA report
- GET  /api/v1/analytics/rca/history - RCA history

Reference: MT-023 §2.4, block7-analytics-ai-engine.md §5
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import sys
import os

# Add parent directory to path to import RCA engine
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ..dependencies import get_current_user, require_permission

# Lazy import for RCAEngine (heavy dependency chain)
def _get_rca_engine():
    from root_cause.rca_engine import RCAEngine
    return RCAEngine

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class RCAAnalyzeRequest(BaseModel):
    incident_id: str = Field(..., description="Incident ID to analyze")
    ci_id: str = Field(..., description="CI ID (Configuration Item)")
    timeframe_minutes: int = Field(default=60, ge=5, le=1440, description="Analysis timeframe in minutes")
    mode: str = Field(default="reactive", description="RCA mode: reactive, forward, or hybrid")


class RCAReportResponse(BaseModel):
    incident_id: str
    ci_id: str
    timestamp: str
    mode: str
    root_cause: str
    confidence: float
    causal_chain: List[str]
    explanation: str
    timeline: List[Dict[str, Any]]
    correlated_events: List[Dict[str, Any]]
    recommended_action: str
    analysis_duration_seconds: float


@router.post("/analyze", response_model=RCAReportResponse)
async def trigger_rca_analysis(
    request: RCAAnalyzeRequest,
    user=Depends(require_permission("analytics.write"))
):
    """
    Trigger Root Cause Analysis for an incident.

    Performs:
    1. Timeline reconstruction
    2. Event correlation
    3. Metric correlation
    4. Topology traversal
    5. Hypothesis generation
    6. Confidence scoring
    """
    try:
        start_time = datetime.utcnow()

        # Build incident dict for RCA engine
        incident = {
            "incident_id": request.incident_id,
            "ci_id": request.ci_id,
            "timestamp": datetime.utcnow(),
            "timeframe_minutes": request.timeframe_minutes,
            "mode": request.mode
        }

        # Run RCA analysis
        RCAEngine = _get_rca_engine()
        result = RCAEngine.analyze(incident)

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Build response
        return RCAReportResponse(
            incident_id=result.incident_id,
            ci_id=result.ci_id,
            timestamp=result.timestamp.isoformat() if hasattr(result.timestamp, 'isoformat') else str(result.timestamp),
            mode=result.mode,
            root_cause=result.root_cause,
            confidence=result.confidence,
            causal_chain=result.causal_chain,
            explanation=result.explanation,
            timeline=result.timeline if hasattr(result, 'timeline') else [],
            correlated_events=result.correlated_events if hasattr(result, 'correlated_events') else [],
            recommended_action=result.recommended_action if hasattr(result, 'recommended_action') else "Manual investigation required",
            analysis_duration_seconds=duration
        )

    except Exception as e:
        logger.error(f"RCA analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"RCA analysis failed: {str(e)}"
        )


@router.get("/{incident_id}", response_model=RCAReportResponse)
async def get_rca_report(
    incident_id: str,
    user=Depends(require_permission("analytics.read"))
):
    """
    Get RCA report by incident ID.

    TODO: Implement storage/retrieval from TimescaleDB or cache.
    For now, returns error if report not found.
    """
    raise HTTPException(
        status_code=501,
        detail="RCA report retrieval not yet implemented - reports are currently returned inline from /analyze"
    )


@router.get("/history")
async def get_rca_history(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(25, ge=1, le=100, description="Items per page"),
    ci_id: Optional[str] = Query(None, description="Filter by CI ID"),
    user=Depends(require_permission("analytics.read"))
):
    """
    Get RCA history with pagination.

    TODO: Implement retrieval from TimescaleDB.
    """
    raise HTTPException(
        status_code=501,
        detail="RCA history not yet implemented - requires TimescaleDB storage"
    )
