"""Machine-related schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field

from app.schemas.common import TimestampMixin, UUIDStr


class MachineType(str, Enum):
    """Machine type enumeration."""
    
    FACIAL_STEAMER = "facial_steamer"
    MICRODERMABRASION = "microdermabrasion"
    LASER_THERAPY = "laser_therapy"
    ULTRASONIC_CLEANER = "ultrasonic_cleaner"
    LED_THERAPY = "led_therapy"
    RADIO_FREQUENCY = "radio_frequency"


class MachineStatus(str, Enum):
    """Machine status enumeration."""
    
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_ORDER = "out_of_order"


class MachineBase(BaseModel):
    """Base machine model."""
    
    name: str = Field(..., min_length=1, max_length=100)
    machine_type: MachineType
    model: Optional[str] = Field(None, max_length=50)
    manufacturer: Optional[str] = Field(None, max_length=50)
    specifications: Dict[str, Any] = Field(default_factory=dict)


class MachineCreate(MachineBase):
    """Machine creation model."""
    pass


class MachineUpdate(BaseModel):
    """Machine update model."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    status: Optional[MachineStatus] = None
    specifications: Optional[Dict[str, Any]] = None
    maintenance_notes: Optional[str] = Field(None, max_length=500)


class Machine(MachineBase, TimestampMixin):
    """Machine response model."""
    
    id: UUIDStr
    status: MachineStatus = MachineStatus.AVAILABLE
    last_maintenance: Optional[datetime] = None
    usage_hours: int = 0
    maintenance_notes: Optional[str] = None
