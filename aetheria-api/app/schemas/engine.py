"""Engine and plan generation schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin, UUIDStr


class PlanGenerationRequest(BaseModel):
    """Request model for generating treatment plans."""
    
    session_id: UUID
    max_steps: Optional[int] = Field(None, ge=1, le=15, description="Maximum steps per routine")
    max_serums: Optional[int] = Field(None, ge=1, le=5, description="Maximum serums per routine")


class RoutineStep(BaseModel):
    """Individual step in a routine."""
    
    step_order: int = Field(..., ge=1)
    instructions: str = Field(..., min_length=1, max_length=500)


class WeeklyStep(BaseModel):
    """Weekly routine step with specific timing."""
    
    day_of_week: int = Field(..., ge=0, le=6, description="0=Sunday, 6=Saturday")
    when: str = Field(..., pattern="^(AM|PM)$")
    instructions: str = Field(..., min_length=1, max_length=500)


class RoutineSchedule(BaseModel):
    """Complete routine schedule."""
    
    am: List[RoutineStep] = Field(default_factory=list)
    pm: List[RoutineStep] = Field(default_factory=list)
    weekly: List[WeeklyStep] = Field(default_factory=list)


class PlanGenerationResponse(BaseModel):
    """Response model for plan generation."""
    
    plan_id: UUID
    skin_profile: Dict[str, Any] = Field(..., description="Analyzed skin profile")
    routine: RoutineSchedule
    explainability: Dict[str, Any] = Field(..., description="AI reasoning and recommendations")


class SessionSummary(BaseModel):
    """Summary of an assessment session."""
    
    session_id: UUID
    created_at: datetime
    tz: str
    location: Optional[str] = None


class CustomerSessionsResponse(BaseModel):
    """Response model for customer sessions list."""
    
    sessions: List[SessionSummary]


class MetricComparison(BaseModel):
    """Comparison of a single metric between two sessions."""
    
    key: str
    previous: Optional[float] = None
    latest: Optional[float] = None
    delta: Optional[float] = None


class ProfileComparison(BaseModel):
    """Comparison of skin profile between sessions."""
    
    skin_type: Dict[str, Optional[str]] = Field(
        default_factory=lambda: {"previous": None, "latest": None}
    )
    main_concerns: Dict[str, Optional[List[str]]] = Field(
        default_factory=lambda: {"previous": None, "latest": None}
    )


class SessionComparisonResponse(BaseModel):
    """Response model for session comparison."""
    
    metrics: List[MetricComparison]
    profile: ProfileComparison
    notes: List[str] = Field(default_factory=list, description="Analysis notes and insights")
