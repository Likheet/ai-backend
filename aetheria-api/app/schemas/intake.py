"""Intake-related schemas for form and machine data."""

from datetime import datetime, date
from typing import Any, Dict, List, Optional
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.schemas.common import TimestampMixin, UUIDStr


class Gender(str, Enum):
    """Gender enumeration."""
    
    MALE = "male"
    FEMALE = "female" 
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"


class CustomerData(BaseModel):
    """Customer data for intake form."""
    
    full_name: str = Field(..., min_length=1, max_length=100)
    phone_e164: str = Field(..., pattern=r'^\+[1-9]\d{1,14}$')
    dob: Optional[date] = None
    gender: Optional[Gender] = None


class SessionData(BaseModel):
    """Session data for intake form."""
    
    tz: str = Field(default="Asia/Kolkata", max_length=50)
    location: Optional[str] = Field(None, max_length=200)


class IntakeFormRequest(BaseModel):
    """Request model for intake form submission."""
    
    customer: CustomerData
    session: SessionData
    answers: Dict[str, Any] = Field(..., description="Form answers as key-value pairs")
    raw: Optional[Dict[str, Any]] = Field(None, description="Raw form data")


class IntakeFormResponse(BaseModel):
    """Response model for intake form submission."""
    
    session_id: UUID


# Machine intake schemas
class MetricKey(str, Enum):
    """Valid metric keys for machine scans."""
    
    MOISTURE = "moisture"
    SEBUM = "sebum"
    TEXTURE = "texture"
    PIGMENTATION_UV = "pigmentation_uv"
    HYPEREMIA = "hyperemia"
    PORES = "pores"
    ACNE_UV = "acne_uv"
    UV_SPOT = "uv_spot"
    BROWN_AREA = "brown_area"
    SENSITIVITY = "sensitivity"


class MetricUnit(str, Enum):
    """Valid units for metrics."""
    
    PERCENT = "pct"
    SCORE = "score"
    COUNT = "count"
    MILLIMETER = "mm"


class SeverityLevel(str, Enum):
    """Severity level enumeration."""
    
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"


class CaptureMode(str, Enum):
    """Machine capture modes."""
    
    RGB = "RGB"
    POLARIZED = "PL"  
    UV = "UV"


class MachineMetric(BaseModel):
    """Individual machine metric measurement."""
    
    key: MetricKey
    value: float = Field(..., ge=0.0, le=100.0)
    unit: MetricUnit
    severity: Optional[SeverityLevel] = None
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    mode: Optional[CaptureMode] = None
    source_key: Optional[str] = Field(None, max_length=100)


class MachineIntakeRequest(BaseModel):
    """Request model for machine intake."""
    
    session_id: UUID
    device_id: Optional[str] = Field(None, max_length=100)
    capture_modes: List[str] = Field(..., min_items=1, max_items=5)
    metrics: List[MachineMetric] = Field(..., min_items=1, max_items=50)
    raw_report: Dict[str, Any] = Field(..., description="Raw machine report data")
    
    @field_validator('capture_modes')
    @classmethod
    def validate_capture_modes(cls, v):
        """Validate capture modes."""
        valid_modes = {mode.value for mode in CaptureMode}
        for mode in v:
            if mode not in valid_modes:
                raise ValueError(f"Invalid capture mode: {mode}")
        return v


class MachineIntakeResponse(BaseModel):
    """Response model for machine intake."""
    
    scan_id: UUID


# Legacy schemas for backward compatibility
class SkinType(str, Enum):
    """Skin type enumeration."""
    
    DRY = "dry"
    OILY = "oily"
    COMBINATION = "combination"
    SENSITIVE = "sensitive"
    NORMAL = "normal"


class HairType(str, Enum):
    """Hair type enumeration."""
    
    STRAIGHT = "straight"
    WAVY = "wavy"
    CURLY = "curly"
    COILY = "coily"


class IntakeRequest(BaseModel):
    """Legacy client intake request model."""
    
    client_name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., pattern=r'^\+?[1-9]\d{1,14}$')
    age: Optional[int] = Field(None, ge=13, le=120)
    skin_type: Optional[SkinType] = None
    hair_type: Optional[HairType] = None
    concerns: List[str] = Field(default_factory=list, max_items=10)
    previous_treatments: List[str] = Field(default_factory=list, max_items=5)
    allergies: List[str] = Field(default_factory=list, max_items=10)
    preferences: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = Field(None, max_length=1000)


class IntakeResponse(BaseModel):
    """Legacy client intake response model."""
    
    intake_id: UUIDStr
    client_id: UUIDStr
    status: str = "pending"
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    created_at: datetime
