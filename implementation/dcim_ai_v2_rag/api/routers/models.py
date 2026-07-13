"""
Model Registry API Router

Endpoints:
- GET  /api/v1/analytics/models - List registered models
- GET  /api/v1/analytics/models/{id} - Get model details
- POST /api/v1/analytics/models - Register new model
- PUT  /api/v1/analytics/models/{id}/deploy - Deploy model
- GET  /api/v1/analytics/models/{id}/metrics - Get model performance

Reference: MT-023 §2.7, block7-analytics-ai-engine.md §8
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ..dependencies import get_current_user, require_permission

# Lazy imports for model registry (heavy dependency chain)
def _get_registry():
    from registry.model_registry import (
        register_model_v2,
        activate_model_v2,
        get_active_model_v2,
        list_models_by_type,
        list_models_by_domain,
    )
    return {
        "register_model_v2": register_model_v2,
        "activate_model_v2": activate_model_v2,
        "get_active_model_v2": get_active_model_v2,
        "list_models_by_type": list_models_by_type,
        "list_models_by_domain": list_models_by_domain,
    }

logger = logging.getLogger(__name__)
router = APIRouter()


# Request/Response Models
class ModelRegisterRequest(BaseModel):
    model_name: str = Field(..., description="Model name")
    model_type: str = Field(..., description="Model type: anomaly, forecast, clustering, etc.")
    version: str = Field(..., description="Semantic version (e.g., v1.2.3)")
    description: Optional[str] = Field(None, description="Model description")
    domain: Optional[str] = Field(None, description="Domain: server, network, storage, etc.")
    artifact_path: str = Field(..., description="Path to model artifact")
    metrics: Dict[str, float] = Field(..., description="Performance metrics (accuracy, precision, recall, f1)")
    hyperparameters: Optional[Dict[str, Any]] = Field(None, description="Model hyperparameters")


class ModelResponse(BaseModel):
    model_id: str
    model_name: str
    model_type: str
    version: str
    description: Optional[str]
    status: str
    trained_at: Optional[str]
    deployed_at: Optional[str]
    accuracy: Optional[float]
    precision_score: Optional[float]
    recall_score: Optional[float]
    f1_score: Optional[float]
    artifact_path: str


@router.get("", response_model=List[ModelResponse])
async def list_models(
    model_type: Optional[str] = Query(None, description="Filter by model type"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(25, ge=1, le=100, description="Items per page"),
    user=Depends(require_permission("analytics.read"))
):
    """
    List registered models with optional filtering.
    """
    try:
        reg = _get_registry()
        if model_type:
            models = reg["list_models_by_type"](model_type)
        elif domain:
            models = reg["list_models_by_domain"](domain)
        else:
            # TODO: Implement list_all_models in registry
            models = []

        # Convert to response format
        # TODO: Add actual model data from registry
        return []

    except Exception as e:
        logger.error(f"Failed to list models: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list models: {str(e)}"
        )


@router.get("/{model_name}", response_model=ModelResponse)
async def get_model_details(
    model_name: str,
    model_type: Optional[str] = Query(None, description="Model type (required for v2 API)"),
    user=Depends(require_permission("analytics.read"))
):
    """
    Get model details by name.
    """
    try:
        reg = _get_registry()
        if model_type:
            model = reg["get_active_model_v2"](model_name, model_type)
        else:
            # Try v1 API
            from registry.model_registry import get_active_model
            artifact_path = get_active_model(model_name)
            if not artifact_path:
                raise HTTPException(status_code=404, detail="Model not found")

            # Build minimal response
            return ModelResponse(
                model_id="unknown",
                model_name=model_name,
                model_type="unknown",
                version="unknown",
                description=None,
                status="production",
                trained_at=None,
                deployed_at=None,
                accuracy=None,
                precision_score=None,
                recall_score=None,
                f1_score=None,
                artifact_path=artifact_path
            )

        if not model:
            raise HTTPException(status_code=404, detail="Model not found")

        return ModelResponse(
            model_id=model.get("model_id", "unknown"),
            model_name=model.get("model_name"),
            model_type=model.get("model_type"),
            version=model.get("version"),
            description=model.get("description"),
            status=model.get("status", "registered"),
            trained_at=model.get("trained_at"),
            deployed_at=model.get("deployed_at"),
            accuracy=model.get("accuracy"),
            precision_score=model.get("precision_score"),
            recall_score=model.get("recall_score"),
            f1_score=model.get("f1_score"),
            artifact_path=model.get("artifact_path")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get model details: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get model details: {str(e)}"
        )


@router.post("", status_code=201)
async def register_model(
    request: ModelRegisterRequest,
    user=Depends(require_permission("analytics.admin"))
):
    """
    Register a new model in the registry.
    """
    try:
        reg = _get_registry()
        reg["register_model_v2"](
            model_name=request.model_name,
            model_type=request.model_type,
            version=request.version,
            artifact_path=request.artifact_path,
            metrics=request.metrics,
            description=request.description,
            domain=request.domain,
            hyperparameters=request.hyperparameters
        )

        return {
            "status": "registered",
            "model_name": request.model_name,
            "model_type": request.model_type,
            "version": request.version
        }

    except Exception as e:
        logger.error(f"Failed to register model: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register model: {str(e)}"
        )


@router.put("/{model_name}/deploy")
async def deploy_model(
    model_name: str,
    model_type: str = Query(..., description="Model type"),
    version: str = Query(..., description="Version to deploy"),
    user=Depends(require_permission("analytics.admin"))
):
    """
    Deploy (activate) a model version.
    """
    try:
        reg = _get_registry()
        reg["activate_model_v2"](model_name, model_type, version)

        return {
            "status": "deployed",
            "model_name": model_name,
            "model_type": model_type,
            "version": version,
            "deployed_at": datetime.utcnow().isoformat()
        }

    except Exception as e:
        logger.error(f"Failed to deploy model: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deploy model: {str(e)}"
        )
