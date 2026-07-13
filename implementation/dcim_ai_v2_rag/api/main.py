"""
Block 7 Analytics & AI Engine - FastAPI Main Application

Provides REST API for:
- Anomaly Detection
- Predictive Maintenance
- Root Cause Analysis (RCA)
- Capacity Forecasting
- Energy Optimization
- Model Registry
- LLM/RAG Explanation Layer

Reference:
- dcim-wiki/reference-designs/block7-analytics-ai-engine.md
- dcim-wiki/reference-designs/block7-analytics-ai-engine-technical-requirements.md
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import logging
from datetime import datetime

from .routers import (
    anomalies,
    predictions,
    rca,
    capacity,
    energy,
    models,
    llm,
)
from .dependencies import get_current_user, get_db_connection
from .config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="DCIM Analytics & AI Engine",
    description="Block 7 - Analytics & AI Engine API for anomaly detection, predictive maintenance, RCA, capacity forecasting, energy optimization, and LLM/RAG",
    version="1.0.0",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    anomalies.router,
    prefix="/api/v1/analytics/anomalies",
    tags=["Anomaly Detection"]
)
app.include_router(
    predictions.router,
    prefix="/api/v1/analytics/predictions",
    tags=["Predictive Maintenance"]
)
app.include_router(
    rca.router,
    prefix="/api/v1/analytics/rca",
    tags=["Root Cause Analysis"]
)
app.include_router(
    capacity.router,
    prefix="/api/v1/analytics/capacity",
    tags=["Capacity Forecasting"]
)
app.include_router(
    energy.router,
    prefix="/api/v1/analytics/energy",
    tags=["Energy Optimization"]
)
app.include_router(
    models.router,
    prefix="/api/v1/analytics/models",
    tags=["Model Registry"]
)
app.include_router(
    llm.router,
    prefix="/api/v1/analytics/llm",
    tags=["LLM/RAG"]
)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "service": "analytics-ai-engine"
    }


@app.get("/api/v1/health", tags=["Health"])
async def api_health_check():
    """API health check with component status"""
    try:
        # Check database connection
        db = get_db_connection()
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_status = "unhealthy"

    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0",
        "components": {
            "database": db_status,
            "api": "healthy"
        }
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": f"HTTP_{exc.status_code}",
                "message": exc.detail,
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """General exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "timestamp": datetime.utcnow().isoformat()
            }
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
