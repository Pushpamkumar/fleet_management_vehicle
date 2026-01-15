from pydantic import BaseModel
from typing import Optional


class AvailabilityCheckRequest(BaseModel):
    """Request to check vehicle availability for a time range"""
    vehicle_id: str
    start_time: str  # ISO 8601 format
    end_time: str    # ISO 8601 format


class AvailabilityCheckResponse(BaseModel):
    """Response indicating vehicle availability"""
    vehicle_id: str
    is_available: bool
    conflicting_bookings: int = 0


class FleetUtilizationRequest(BaseModel):
    """Request for fleet utilization metrics"""
    start_date: str  # ISO 8601 format
    end_date: str    # ISO 8601 format
    location: Optional[str] = None
