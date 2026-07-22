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

import time
import json as _json

from ..dependencies import require_permission

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
    active_domains: List[str] = Field(
        default=["server", "network", "storage", "power", "cooling"],
        description="Active domains to analyze"
    )
    timeframe_minutes: int = Field(default=60, ge=5, le=1440, description="Analysis timeframe in minutes")
    mode: str = Field(default="reactive", description="RCA mode: reactive, forward, or hybrid")
    domain_scores: Optional[Dict[str, float]] = Field(default=None, description="Domain severity scores")


class RCAReportResponse(BaseModel):
    incident_id: str
    ci_id: str
    timestamp: str
    mode: str
    root_cause: str
    confidence: float
    causal_chain: List[str]
    explanation: str
    ranked_domains: List[str]
    impact_domains: List[str]
    domain_probabilities: Dict[str, float]
    analysis_duration_seconds: float


@router.post("/analyze", response_model=RCAReportResponse)
async def trigger_rca_analysis(
    request: RCAAnalyzeRequest,
    user=Depends(require_permission("analytics.write"))
):
    """
    Trigger Root Cause Analysis for an incident.

    Performs:
    1. Topology traversal
    2. Domain strength scoring
    3. Causal chain reconstruction
    4. Confidence scoring (softmax)
    5. Explanation generation
    """
    try:
        req_start = time.time()
        start_time = datetime.utcnow()

        # Build incident dict for RCA engine
        # RCAEngine expects: incident_id, timestamp, active_domains, domain_scores
        incident = {
            "incident_id": request.incident_id,
            "timestamp": datetime.utcnow(),
            "active_domains": request.active_domains,
            "domain_scores": request.domain_scores or {d: 1.0 for d in request.active_domains},
        }

        # Run RCA analysis
        RCAEngine = _get_rca_engine()
        result = RCAEngine.analyze(incident)

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Build response from RootCauseResult
        response = RCAReportResponse(
            incident_id=result.incident_id,
            ci_id=request.ci_id,
            timestamp=result.timestamp.isoformat() if hasattr(result.timestamp, 'isoformat') else str(result.timestamp),
            mode=result.mode,
            root_cause=result.root_domain,
            confidence=result.confidence,
            causal_chain=result.causal_chain,
            explanation=result.explanation,
            ranked_domains=result.ranked_domains,
            impact_domains=result.impact_domains,
            domain_probabilities=result.domain_probabilities,
            analysis_duration_seconds=duration
        )

        # RAG LLM Explanation Generation
        try:
            from .llm import _call_llama
            from ...rag.pipeline import RAGPipeline
            rag = RAGPipeline()
            query_str = f"Incident {result.incident_id} root cause in {result.root_domain} affecting {', '.join(result.active_domains)}"
            docs = rag.vector_store.search(query_str, n_results=2)
            context = "\n".join([f"- {d['document']}" for d in docs])
            
            prompt = rag.templates["rca_explanation"].format(
                incident_id=result.incident_id,
                root_domain=result.root_domain,
                confidence=f"{result.confidence:.2f}",
                causal_chain=_json.dumps(result.causal_chain),
                context=context
            )
            llm_explanation = _call_llama(prompt)
            if llm_explanation:
                result.explanation = llm_explanation
        except Exception as e:
            logger.warning(f"Failed to generate LLM explanation with RAG: {e}")

        # Auto-save to TimescaleDB (best-effort, non-blocking)
        try:
            from ..dependencies import get_db_connection
            import json as _json
            conn = get_db_connection()
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO rca_reports (
                        incident_id, ci_id, timestamp, mode,
                        root_cause, confidence, causal_chain, explanation,
                        timeline, correlated_events, recommended_action,
                        analysis_duration_seconds
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (incident_id) DO UPDATE SET
                        root_cause = EXCLUDED.root_cause,
                        confidence = EXCLUDED.confidence,
                        causal_chain = EXCLUDED.causal_chain,
                        explanation = EXCLUDED.explanation,
                        analysis_duration_seconds = EXCLUDED.analysis_duration_seconds
                    """,
                    (
                        result.incident_id,
                        request.ci_id,
                        result.timestamp,
                        result.mode,
                        result.root_domain,
                        result.confidence,
                        _json.dumps(result.causal_chain),
                        result.explanation,
                        _json.dumps([]),   # timeline
                        _json.dumps([]),   # correlated_events
                        None,              # recommended_action
                        duration,
                    ),
                )
                conn.commit()
                logger.info(f"RCA report saved: {result.incident_id}")
            finally:
                conn.close()
        except Exception as save_err:
            logger.warning(f"RCA save to DB failed (non-blocking): {save_err}")

        # Record metrics
        rca_duration = time.time() - req_start
        from ..main import METRICS_RCA_LATENCY
        if METRICS_RCA_LATENCY:
            METRICS_RCA_LATENCY.observe(rca_duration)

        return response

    except Exception as e:
        logger.error(f"RCA analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"RCA analysis failed: {str(e)}"
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

    Retrieves from rca_reports table in TimescaleDB.
    """
    try:
        from ..dependencies import get_db_connection
        conn = get_db_connection()
        try:
            cur = conn.cursor()

            # Build query with optional CI filter
            where_clause = ""
            params = []
            if ci_id:
                where_clause = "WHERE ci_id = %s"
                params.append(ci_id)

            # Count total
            cur.execute(f"SELECT COUNT(*) as cnt FROM rca_reports {where_clause}", params)
            total = cur.fetchone()["cnt"]

            # Fetch page
            offset = (page - 1) * per_page
            cur.execute(
                f"""
                SELECT rca_id, incident_id, ci_id, timestamp, mode,
                       root_cause, confidence, causal_chain,
                       analysis_duration_seconds, created_at
                FROM rca_reports {where_clause}
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
                """,
                params + [per_page, offset],
            )
            rows = cur.fetchall()
        finally:
            conn.close()

        items = []
        for row in rows:
            items.append({
                "incident_id": row["incident_id"],
                "ci_id": str(row["ci_id"]) if row["ci_id"] else "",
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else "",
                "mode": row["mode"],
                "root_cause": row["root_cause"],
                "confidence": float(row["confidence"]) if row["confidence"] else 0.0,
                "analysis_duration_seconds": float(row["analysis_duration_seconds"] or 0),
            })

        return {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": max(1, (total + per_page - 1) // per_page),
            "items": items,
        }

    except Exception as e:
        logger.warning(f"Could not retrieve from DB (table may not exist yet): {e}")
        raise HTTPException(
            status_code=503,
            detail="RCA storage not available. Run database migration 002 first."
        )


@router.get("/{incident_id}")
async def get_rca_report(
    incident_id: str,
    user=Depends(require_permission("analytics.read"))
):
    """
    Get RCA report by incident ID.

    Retrieves from rca_reports table in TimescaleDB.
    Falls back to a generic response if not found.
    """
    try:
        from ..dependencies import get_db_connection
        conn = get_db_connection()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT rca_id, incident_id, ci_id, timestamp, mode,
                       root_cause, confidence, causal_chain, explanation,
                       timeline, correlated_events, recommended_action,
                       analysis_duration_seconds, created_at
                FROM rca_reports
                WHERE incident_id = %s
                """,
                (incident_id,),
            )
            row = cur.fetchone()
        finally:
            conn.close()

        if row:
            causal_chain = row["causal_chain"]
            if isinstance(causal_chain, str):
                import json
                causal_chain = json.loads(causal_chain)

            return {
                "incident_id": row["incident_id"],
                "ci_id": str(row["ci_id"]) if row["ci_id"] else "",
                "timestamp": row["timestamp"].isoformat() if row["timestamp"] else "",
                "mode": row["mode"],
                "root_cause": row["root_cause"],
                "confidence": float(row["confidence"]) if row["confidence"] else 0.0,
                "causal_chain": causal_chain or [],
                "explanation": row["explanation"] or "",
                "ranked_domains": [],
                "impact_domains": [],
                "domain_probabilities": {},
                "analysis_duration_seconds": float(row["analysis_duration_seconds"] or 0),
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"RCA report not found for incident '{incident_id}'. "
                        f"Run POST /api/v1/analytics/rca/analyze first."
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Could not retrieve from DB (table may not exist yet): {e}")
        raise HTTPException(
            status_code=503,
            detail="RCA storage not available. Run database migration 002 first."
        )
