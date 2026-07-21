"""
LLM/RAG Explanation Layer API Router

Endpoints:
- POST /api/v1/analytics/llm/query - Ask natural language question
- POST /api/v1/analytics/llm/explain - Explain anomaly in natural language

Modes:
  1. llama-server HTTP (Gema 4 12B on port 8080) — real LLM
  2. Template fallback — rule-based when model unavailable

Reference: MT-023 §2.8, block7-analytics-ai-engine.md §9
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import logging
import os
import json as _json

import time

from ..dependencies import require_permission
from ..main import METRICS_LLM_LATENCY, METRICS_LLM_ERRORS

logger = logging.getLogger(__name__)
router = APIRouter()


class LLMQueryRequest(BaseModel):
    query: str = Field(..., description="Natural language query")
    context_ci_id: Optional[str] = Field(None, description="CI ID for context scoping")
    n_results: int = Field(5, ge=1, le=20, description="Num context docs (future RAG use)")


class LLMQueryResponse(BaseModel):
    query: str
    answer: str
    citations: List[Dict[str, Any]] = []
    context_used: int = 0
    model: str = "template-fallback"


class AnomalyExplainRequest(BaseModel):
    metric_name: str = Field(..., description="Metric name")
    current_value: float = Field(..., description="Current value")
    expected_min: float = Field(None, description="Expected minimum")
    expected_max: float = Field(None, description="Expected maximum")
    severity: str = Field("medium", description="Severity level")
    detection_method: str = Field("z_score", description="Detection method used")


# ─── Llama-server HTTP caller ─────────────────────────

LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://localhost:8080/v1/chat/completions")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT_SECONDS", "25"))


def _call_llama(prompt: str, max_tokens: int = 400, temperature: float = 0.5) -> Optional[str]:
    """Call Gemma 4 12B via llama-server. Returns None if unavailable."""
    try:
        import urllib.request

        payload = _json.dumps({
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a DCIM data center infrastructure management assistant. "
                        "You help operators understand anomalies, metrics, and infrastructure conditions. "
                        "Answer concisely in 2-4 sentences. Be specific and actionable. "
                        "If you don't know, say so honestly."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }).encode("utf-8")

        req = urllib.request.Request(
            LLAMA_SERVER_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        req.add_header("User-Agent", "DCIM-LLM-Router/1.0")

        with urllib.request.urlopen(req, timeout=LLM_TIMEOUT) as resp:
            data = _json.loads(resp.read().decode("utf-8"))

        content = data.get("choices", [{}])[0].get("message", {})
        text = content.get("content", "") or content.get("reasoning_content", "")
        if isinstance(text, str) and text.strip():
            return text.strip()
        return None

    except Exception as e:
        logger.warning(f"llama-server unavailable: {e}")
        return None


# ─── POST /query ─────────────────────────────────────

@router.post("/query", response_model=LLMQueryResponse)
async def llm_query(
    request: LLMQueryRequest,
    user=Depends(require_permission("analytics.read")),
):
    """Ask natural language question. Uses Gemma 4 12B, falls back to templates."""
    start_time = time.time()
    model_name = "template-fallback"
    answer = None

    # Try real LLM first
    real_answer = _call_llama(request.query)
    if real_answer:
        answer = real_answer
        model_name = os.getenv("LLM_MODEL", "gemma-4-12b-it")
        logger.info(f"LLM response from {model_name} ({len(answer)} chars)")
    else:
        METRICS_LLM_ERRORS.inc()
        logger.warning("LLM response failed/empty. Triggering template fallback.")

    if not answer:
        answer = _template_answer(request.query)
        logger.info("Using template fallback")

    # Record metrics
    duration = time.time() - start_time
    if METRICS_LLM_LATENCY:
        METRICS_LLM_LATENCY.observe(duration)

    return LLMQueryResponse(
        query=request.query,
        answer=answer,
        citations=[],
        context_used=0,
        model=model_name,
    )


# ─── POST /explain ───────────────────────────────────

@router.post("/explain")
async def explain_anomaly(
    request: AnomalyExplainRequest,
    user=Depends(require_permission("analytics.read")),
):
    """Explain anomaly in natural language."""
    prompt = (
        f"Explain this DCIM anomaly:\n"
        f"- Metric: {request.metric_name}\n"
        f"- Value: {request.current_value}\n"
        f"- Expected range: {request.expected_min} to {request.expected_max}\n"
        f"- Severity: {request.severity}\n"
        f"- Detection: {request.detection_method}\n\n"
        f"Provide: 1) What happened, 2) Why it matters, 3) Recommended action."
    )

    model_name = "template-fallback"
    explanation = None

    real_answer = _call_llama(prompt)
    if real_answer:
        explanation = real_answer
        model_name = os.getenv("LLM_MODEL", "gemma-4-12b-it")

    if not explanation:
        explanation = _template_explain(
            request.metric_name, request.current_value,
            request.expected_min, request.expected_max, request.severity,
        )

    return {
        "anomaly": {
            "metric_name": request.metric_name,
            "current_value": request.current_value,
            "expected_range": f"{request.expected_min}-{request.expected_max}",
            "severity": request.severity,
            "detection_method": request.detection_method,
        },
        "explanation": explanation,
        "citations": [],
        "model": model_name,
    }


# ─── Template fallbacks ──────────────────────────────

def _template_answer(query: str) -> str:
    ql = query.lower()
    if "cpu" in ql and ("spike" in ql or "high" in ql):
        return (
            "CPU spike detected. This indicates a sudden increase in processing load, "
            "likely caused by a runaway process, batch job, or resource contention. "
            "Immediate action: identify the top CPU-consuming process using 'top' or 'htop'. "
            "Confidence: Medium."
        )
    elif "temperature" in ql:
        return (
            "Temperature alert. Normal range is 18-28°C. Check cooling unit status, "
            "verify airflow paths, and inspect for equipment hotspots. "
            "If above 35°C, consider emergency load shedding. Confidence: High."
        )
    elif "pue" in ql:
        return (
            "PUE = Total facility power / IT equipment power. Ideal: 1.1-1.5. "
            "High PUE indicates cooling or power distribution inefficiency. "
            "Check CRAC set points, UPS efficiency, and airflow management. Confidence: High."
        )
    elif "memory" in ql or "ram" in ql:
        return (
            "Memory utilization alert. Check for memory leaks using process monitoring. "
            "Identify top consumers and growth patterns. If gradual increase, suspect "
            "a memory leak. Temporary fix: restart affected service. Confidence: Medium."
        )
    elif "disk" in ql:
        return (
            "Disk usage concern. Identify large files, check log rotation, clean temp files. "
            "If >=95% used, submit storage expansion request immediately. Confidence: High."
        )
    return (
        "I analyzed your query against the available DCIM knowledge. "
        "Please provide more specifics (metric name, CI ID, severity) for "
        "a more targeted analysis. Confidence: Low."
    )


def _template_explain(metric_name: str, value: float, exp_min: float, exp_max: float, severity: str) -> str:
    normal_range = f"{exp_min}-{exp_max}" if exp_min and exp_max else "normal operating range"
    return (
        f"Anomaly detected in {metric_name}: current value {value} is outside the "
        f"{normal_range}. This is classified as {severity} severity. "
        f"Recommendation: investigate the {metric_name} trend for the last hour "
        f"and correlate with other metrics on the same CI."
    )
