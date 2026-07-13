"""
FastAPI dependencies for authentication, database connections, etc.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import logging

from .config import settings

logger = logging.getLogger(__name__)

# Security
security = HTTPBearer(auto_error=False)


def get_db_connection():
    """Get TimescaleDB connection"""
    try:
        conn = psycopg2.connect(
            host=settings.TIMESCALEDB_HOST,
            port=settings.TIMESCALEDB_PORT,
            database=settings.TIMESCALEDB_DATABASE,
            user=settings.TIMESCALEDB_USER,
            password=settings.TIMESCALEDB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection failed"
        )


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
):
    """
    Get current authenticated user.

    For now, returns a mock user if AUTH_ENABLED=false.
    In production, this should validate JWT token from IAM service.
    """
    if not settings.AUTH_ENABLED:
        # Development mode - return mock user
        return {
            "user_id": "dev-user",
            "username": "developer",
            "roles": ["analytics.read", "analytics.write", "analytics.admin"]
        }

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Validate JWT token with IAM service
    # For now, raise error if auth is enabled but not implemented
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented"
    )


def require_permission(permission: str):
    """
    Dependency factory to require specific permission.

    Usage:
        @router.post("/endpoint", dependencies=[Depends(require_permission("analytics.write"))])
    """
    async def check_permission(user=Depends(get_current_user)):
        if permission not in user.get("roles", []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        return user

    return check_permission
