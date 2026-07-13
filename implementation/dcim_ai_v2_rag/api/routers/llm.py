"""
LLM/RAG Explanation Layer API Router

Endpoints:
- POST /api/v1/analytics/llm/query - Ask natural language question
- POST /api/v1/analytics/llm/explain - Explain anomaly

Reference: MT-023 §2.8, block7-analytics-ai-engine.md §9
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List
import logging

from ..dependencies import require_permission

logger = logging.getLogger(__name__)
router = APIRouter()


class LLMQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    context_ci_id: Optional[str] = Field(None, description="CI ID for context")


class LLMQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[str]
    confidence: float


@router.post("/query", response_model=LLMQueryResponse)
async def llm_query(
    request: LLMQueryRequest,
    user=Depends(require_permission("analytics.read"))
):
    """Ask natural language question about metrics/anomalies"""
    raise HTTPException(status_code=501, detail="LLM/RAG not yet implemented")


@router.post("/explain")
async def explain_anomaly(
    anomaly_id: str,
    user=Depends(require_permission("analytics.read"))
):
    """Explain an anomaly in natural language"""
    raise HTTPException(status_code=501, detail="LLM/RAG not yet implemented")
