"""Common schemas and types used across the application."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TimestampMixin(BaseModel):
    """Mixin for models with timestamp fields."""
    
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class BaseResponse(BaseModel):
    """Base response model."""
    
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    
    success: bool = False
    error: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str = "ok"
    timestamp: datetime
    version: str = "0.1.0"
    environment: str
    database: Optional[bool] = None


# Type aliases
UUIDStr = str  # UUID as string
Timestamp = datetime  # ISO timestamp
