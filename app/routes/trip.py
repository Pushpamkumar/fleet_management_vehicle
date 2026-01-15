from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Trip, Booking
from app.services import TripService, BookingService
from app.schemas import TripCreate, TripUpdate, TripResponse, BookingStatus
from datetime import datetime
from typing import List, Optional
import uuid


router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def start_trip(
    trip_data: TripCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start a trip from a confirmed booking.
    Captures initial mileage for distance tracking.
    """
    try:
        booking_id = uuid.UUID(str(trip_data.booking_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid booking ID")
    
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Verify booking belongs to current user or user is admin
    if current_user.id != booking.user_id and current_user.role.value not in ["admin", "fleet_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    if booking.status != BookingStatus.CONFIRMED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Booking must be confirmed to start trip (current status: {booking.status})"
        )
    
    try:
        trip = TripService.create_trip(
            db,
            booking_id=booking_id,
            vehicle_id=booking.vehicle_id,
            user_id=booking.user_id,
            start_location=trip_data.start_location,
            mileage_start=trip_data.mileage_start
        )
        
        db.commit()
        db.refresh(trip)
        
        return trip
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(
    trip_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get trip details"""
    try:
        tid = uuid.UUID(trip_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid trip ID")
    
    trip = TripService.get_trip_by_id(db, tid)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    # User can only view their own trips unless admin/fleet manager
    if current_user.id != trip.user_id and current_user.role.value not in ["admin", "fleet_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return trip


@router.put("/{trip_id}", response_model=TripResponse)
def end_trip(
    trip_id: str,
    trip_data: TripUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    End a trip with final mileage and location.
    Automatically calculates distance traveled.
    """
    try:
        tid = uuid.UUID(trip_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid trip ID")
    
    trip = TripService.get_trip_by_id(db, tid)
    if not trip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    
    # User can only update their own trips unless admin/fleet manager
    if current_user.id != trip.user_id and current_user.role.value not in ["admin", "fleet_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    if trip.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trip has already been ended"
        )
    
    try:
        trip = TripService.end_trip(
            db,
            tid,
            end_location=trip_data.end_location,
            mileage_end=trip_data.mileage_end
        )
        
        # Also mark the associated booking as completed
        booking = db.query(Booking).filter(Booking.id == trip.booking_id).first()
        if booking:
            BookingService.complete_booking(db, booking.id)
        
        db.commit()
        db.refresh(trip)
        
        return trip
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/user/{user_id}", response_model=List[TripResponse])
def get_user_trips(
    user_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all trips for a user within date range"""
    try:
        uid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid user ID")
    
    # Users can only view their own trips unless admin
    if current_user.id != uid and current_user.role.value not in ["admin", "fleet_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")
    
    trips = TripService.get_user_trips(db, uid, start, end)
    return trips


@router.get("/vehicle/{vehicle_id}", response_model=List[TripResponse])
def get_vehicle_trips(
    vehicle_id: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all trips for a vehicle within date range (Fleet Manager only)"""
    try:
        vid = uuid.UUID(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vehicle ID")
    
    if current_user.role.value not in ["admin", "fleet_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Fleet Manager role required")
    
    try:
        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid date format")
    
    trips = TripService.get_vehicle_trips(db, vid, start, end)
    return trips
