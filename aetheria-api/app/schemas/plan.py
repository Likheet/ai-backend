"""Treatment plan-related schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin, UUIDStr


class PlanStatus(str, Enum):
    """Plan status enumeration."""
    
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class TreatmentStep(BaseModel):
    """Individual treatment step model."""
    
    step_number: int = Field(..., ge=1)
    treatment_name: str = Field(..., min_length=1, max_length=100)
    machine_type: Optional[str] = Field(None, max_length=50)
    duration_minutes: int = Field(..., ge=5, le=480)
    settings: Dict[str, Any] = Field(default_factory=dict)
    instructions: Optional[str] = Field(None, max_length=500)
    precautions: List[str] = Field(default_factory=list)


class TreatmentPlanBase(BaseModel):
    """Base treatment plan model."""
    
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    target_concerns: List[str] = Field(..., min_items=1, max_items=10)
    estimated_sessions: int = Field(..., ge=1, le=20)
    session_interval_days: int = Field(..., ge=1, le=30)
    steps: List[TreatmentStep] = Field(..., min_items=1, max_items=15)


class TreatmentPlanCreate(TreatmentPlanBase):
    """Treatment plan creation model."""
    
    client_id: UUIDStr


class TreatmentPlanUpdate(BaseModel):
    """Treatment plan update model."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[PlanStatus] = None
    progress_notes: Optional[str] = Field(None, max_length=1000)
    steps: Optional[List[TreatmentStep]] = None


class TreatmentPlan(TreatmentPlanBase, TimestampMixin):
    """Treatment plan response model."""
    
    id: UUIDStr
    client_id: UUIDStr
    status: PlanStatus = PlanStatus.DRAFT
    current_session: int = 0
    progress_notes: Optional[str] = None
    estimated_completion: Optional[datetime] = None
