from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, get_current_fleet_manager
from app.models import User
from app.services import AnalyticsService
from datetime import datetime
from typing import Optional
import uuid


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/vehicle/{vehicle_id}/utilization", response_model=dict)
def get_vehicle_utilization(
    vehicle_id: str,
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_fleet_manager)
):
    """
    Get vehicle utilization metrics for a date range.
    
    Metrics:
    - Utilization percentage
    - Total trips
    - Total distance
    - Hours in use
    - Idle hours
    - Average trip duration
    """
    try:
        vid = uuid.UUID(vehicle_id)
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parameters")
    
    if start >= end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date must be before end date")
    
    metrics = AnalyticsService.get_vehicle_utilization(db, vid, start, end)
    return metrics


@router.get("/fleet/utilization", response_model=dict)
def get_fleet_utilization(
    start_date: str,
    end_date: str,
    location: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_fleet_manager)
):
    """
    Get fleet-wide utilization metrics.
    
    Metrics:
    - Fleet utilization percentage
    - Number of active vehicles
    - Peak usage hours
    - Fleet efficiency score
    - Total trips and distance
    """
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parameters")
    
    if start >= end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date must be before end date")
    
    metrics = AnalyticsService.get_fleet_utilization(db, start, end, location)
    return metrics


@router.get("/fleet/underutilized-vehicles", response_model=list)
def get_underutilized_vehicles(
    start_date: str,
    end_date: str,
    threshold_percentage: float = 20.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_fleet_manager)
):
    """
    Identify underutilized vehicles for optimization.
    
    Returns vehicles with utilization below threshold percentage.
    Useful for asset reallocation and operational decisions.
    """
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parameters")
    
    if start >= end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date must be before end date")
    
    if not (0 <= threshold_percentage <= 100):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Threshold must be between 0-100")
    
    vehicles = AnalyticsService.get_underutilized_vehicles(db, start, end, threshold_percentage)
    return vehicles


@router.get("/bookings/statistics", response_model=dict)
def get_booking_statistics(
    start_date: str,
    end_date: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_fleet_manager)
):
    """
    Get booking statistics for a date range.
    
    Metrics:
    - Total bookings
    - Completed bookings
    - Cancelled bookings
    - Completion rate
    """
    try:
        start = datetime.fromisoformat(start_date)
        end = datetime.fromisoformat(end_date)
    except (ValueError, AttributeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parameters")
    
    if start >= end:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Start date must be before end date")
    
    stats = AnalyticsService.get_booking_statistics(db, start, end)
    return stats
