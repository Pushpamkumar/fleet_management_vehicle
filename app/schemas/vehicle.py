from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class VehicleCreate(BaseModel):
    license_plate: str = Field(..., min_length=1, max_length=50)
    make: str = Field(..., min_length=1, max_length=100)
    model: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    location: Optional[str] = None
    mileage: float = Field(default=0.0, ge=0)


class VehicleUpdate(BaseModel):
    status: Optional[VehicleStatus] = None
    location: Optional[str] = None
    mileage: Optional[float] = Field(None, ge=0)
    health_score: Optional[float] = Field(None, ge=0, le=100)
    is_active: Optional[bool] = None


class VehicleResponse(BaseModel):
    id: uuid.UUID
    license_plate: str
    make: str
    model: str
    year: int
    status: VehicleStatus
    location: Optional[str]
    mileage: float
    health_score: float
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
