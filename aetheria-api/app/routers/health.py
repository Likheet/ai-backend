"""Health check router."""

from datetime import datetime

from fastapi import APIRouter, Depends
from fastapi import status

from app.core.config import get_settings, Settings
from app.core.db import check_db_connection, check_existing_tables
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])


@router.get(
    "/healthz",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the API and its dependencies."
)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Health check endpoint."""
    
    # Check database connection
    db_healthy = await check_db_connection()
    
    # Check existing tables (for debugging)
    existing_tables = await check_existing_tables() if db_healthy else {}
    
    return HealthResponse(
        status="ok",
        timestamp=datetime.utcnow(),
        version="0.1.0",
        environment=settings.app_env,
        database=db_healthy
    )
