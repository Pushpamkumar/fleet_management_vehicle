from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid


class TripCreate(BaseModel):
    booking_id: uuid.UUID
    start_location: Optional[str] = None
    mileage_start: float = Field(..., ge=0)


class TripUpdate(BaseModel):
    end_location: Optional[str] = None
    mileage_end: Optional[float] = Field(None, ge=0)


class TripResponse(BaseModel):
    id: uuid.UUID
    booking_id: uuid.UUID
    vehicle_id: uuid.UUID
    user_id: uuid.UUID
    start_time: datetime
    end_time: Optional[datetime]
    start_location: Optional[str]
    end_location: Optional[str]
    distance_traveled: float
    mileage_start: float
    mileage_end: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
