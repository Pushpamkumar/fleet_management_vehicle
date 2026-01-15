from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum
import uuid


class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    PENDING = "pending"


class BookingCreate(BaseModel):
    vehicle_id: uuid.UUID
    start_time: datetime = Field(..., description="Start time for booking (ISO 8601 format)")
    end_time: datetime = Field(..., description="End time for booking (ISO 8601 format)")

    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_id": "550e8400-e29b-41d4-a716-446655440000",
                "start_time": "2026-01-20T10:00:00",
                "end_time": "2026-01-20T14:00:00"
            }
        }


class BookingUpdate(BaseModel):
    status: Optional[BookingStatus] = None


class BookingResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    vehicle_id: uuid.UUID
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookingDetail(BookingResponse):
    """Extended booking details with vehicle info"""
    vehicle_license_plate: Optional[str] = None
    vehicle_make: Optional[str] = None
    vehicle_model: Optional[str] = None
