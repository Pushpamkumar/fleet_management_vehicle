from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app.models import User, Booking, Vehicle
from app.services import BookingService, BookingConflictError
from app.schemas import BookingCreate, BookingUpdate, BookingResponse, BookingStatus
from datetime import datetime
from typing import List, Optional
import uuid


router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    booking_data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new booking with concurrency-safe checks.
    
    Implements:
    - Time-window conflict detection
    - Row-level locking via SELECT FOR UPDATE
    - Idempotent booking creation
    """
    try:
        # Validate booking times
        if booking_data.start_time >= booking_data.end_time:
            raise ValueError("Start time must be before end time")
        
        if booking_data.start_time <= datetime.utcnow():
            raise ValueError("Booking start time must be in the future")
        
        # Create booking with concurrency-safe logic
        booking = BookingService.create_booking(
            db,
            user_id=current_user.id,
            vehicle_id=booking_data.vehicle_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time
        )
        
        db.commit()
        db.refresh(booking)
        
        return booking
    
    except BookingConflictError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get booking details"""
    try:
        bid = uuid.UUID(booking_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid booking ID")
    
    booking = db.query(Booking).filter(Booking.id == bid).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # User can only view their own bookings unless they're admin/fleet manager
    if current_user.id != booking.user_id and current_user.role.value not in ["admin", "fleet_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return booking


@router.get("", response_model=List[BookingResponse])
def list_bookings(
    status: Optional[BookingStatus] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List bookings for current user.
    Fleet Managers and Admins can see all bookings.
    """
    if current_user.role.value in ["admin", "fleet_manager"]:
        query = db.query(Booking)
        if status:
            query = query.filter(Booking.status == status)
        return query.order_by(Booking.start_time.desc()).all()
    else:
        # Regular users only see their own bookings
        return BookingService.get_user_bookings(db, current_user.id, status)


@router.put("/{booking_id}", response_model=BookingResponse)
def update_booking(
    booking_id: str,
    update_data: BookingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update booking status (cancel, etc.)"""
    try:
        bid = uuid.UUID(booking_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid booking ID")
    
    booking = db.query(Booking).filter(Booking.id == bid).first()
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    # Only booking owner or fleet manager can update
    if current_user.id != booking.user_id and current_user.role.value not in ["admin", "fleet_manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    try:
        if update_data.status == BookingStatus.CANCELLED:
            booking = BookingService.cancel_booking(db, bid)
        elif update_data.status == BookingStatus.COMPLETED:
            booking = BookingService.complete_booking(db, bid)
        
        db.commit()
        db.refresh(booking)
        
        return booking
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/vehicle/{vehicle_id}/availability", response_model=dict)
def check_availability(
    vehicle_id: str,
    start_time: str,  # ISO 8601 format
    end_time: str,    # ISO 8601 format
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if vehicle is available for given time range"""
    try:
        vid = uuid.UUID(vehicle_id)
        start = datetime.fromisoformat(start_time)
        end = datetime.fromisoformat(end_time)
    except (ValueError, AttributeError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid parameters")
    
    vehicle = db.query(Vehicle).filter(Vehicle.id == vid).first()
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    is_available = BookingService.check_availability(db, vid, start, end)
    conflicting = BookingService.get_conflicting_bookings(db, vid, start, end)
    
    return {
        "vehicle_id": str(vehicle_id),
        "is_available": is_available,
        "conflicting_bookings": len(conflicting),
        "start_time": start_time,
        "end_time": end_time
    }
