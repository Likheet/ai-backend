"""Intake-related schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin, UUIDStr


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
    """Client intake request model."""
    
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
    """Client intake response model."""
    
    intake_id: UUIDStr
    client_id: UUIDStr
    status: str = "pending"
    recommendations: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)
    created_at: datetime
