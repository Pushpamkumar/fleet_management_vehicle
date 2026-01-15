from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import Booking, Vehicle
from app.schemas import BookingStatus, VehicleStatus
import uuid


class BookingConflictError(Exception):
    """Raised when booking conflicts with existing bookings"""
    pass


class BookingService:
    """Service for managing bookings with concurrency-safe operations"""
    
    @staticmethod
    def check_availability(
        db: Session,
        vehicle_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: Optional[uuid.UUID] = None
    ) -> bool:
        """
        Check if vehicle is available for the given time range.
        Uses database indexes for efficient queries.
        
        Time-window conflict detection: A booking conflicts if it overlaps
        with the requested time window.
        """
        query = db.query(Booking).filter(
            Booking.vehicle_id == vehicle_id,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
            # Overlap condition: booking_start < requested_end AND booking_end > requested_start
            and_(
                Booking.start_time < end_time,
                Booking.end_time > start_time
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        conflicting_count = query.count()
        return conflicting_count == 0
    
    @staticmethod
    def get_conflicting_bookings(
        db: Session,
        vehicle_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime
    ) -> List[Booking]:
        """Get all bookings that conflict with the given time range"""
        return db.query(Booking).filter(
            Booking.vehicle_id == vehicle_id,
            Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING]),
            and_(
                Booking.start_time < end_time,
                Booking.end_time > start_time
            )
        ).all()
    
    @staticmethod
    def create_booking(
        db: Session,
        user_id: uuid.UUID,
        vehicle_id: uuid.UUID,
        start_time: datetime,
        end_time: datetime
    ) -> Booking:
        """
        Create a booking with concurrency-safe checks.
        
        Strategy:
        1. Verify vehicle exists and is available
        2. Check availability using transaction-safe query
        3. Create booking in confirmed state
        4. Commit transaction atomically
        """
        # Verify vehicle exists and is available
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).with_for_update().first()
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise ValueError(f"Vehicle is not available (status: {vehicle.status})")
        
        # Check availability with row-level locking
        if not BookingService.check_availability(db, vehicle_id, start_time, end_time):
            conflicting = BookingService.get_conflicting_bookings(db, vehicle_id, start_time, end_time)
            raise BookingConflictError(
                f"Vehicle has {len(conflicting)} conflicting booking(s) in the requested time window"
            )
        
        # Create booking
        booking = Booking(
            id=uuid.uuid4(),
            user_id=user_id,
            vehicle_id=vehicle_id,
            start_time=start_time,
            end_time=end_time,
            status=BookingStatus.CONFIRMED
        )
        
        db.add(booking)
        db.flush()  # Flush to get the ID without committing
        
        return booking
    
    @staticmethod
    def cancel_booking(db: Session, booking_id: uuid.UUID) -> Booking:
        """Cancel an existing booking"""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        if booking.status == BookingStatus.COMPLETED:
            raise ValueError("Cannot cancel a completed booking")
        
        if booking.status == BookingStatus.CANCELLED:
            raise ValueError("Booking is already cancelled")
        
        booking.status = BookingStatus.CANCELLED
        return booking
    
    @staticmethod
    def complete_booking(db: Session, booking_id: uuid.UUID) -> Booking:
        """Mark a booking as completed"""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if not booking:
            raise ValueError(f"Booking {booking_id} not found")
        
        if booking.status != BookingStatus.CONFIRMED:
            raise ValueError(f"Cannot complete booking with status {booking.status}")
        
        booking.status = BookingStatus.COMPLETED
        return booking
    
    @staticmethod
    def get_user_bookings(
        db: Session,
        user_id: uuid.UUID,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """Get all bookings for a user, optionally filtered by status"""
        query = db.query(Booking).filter(Booking.user_id == user_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.order_by(Booking.start_time.desc()).all()
    
    @staticmethod
    def get_vehicle_bookings(
        db: Session,
        vehicle_id: uuid.UUID,
        status: Optional[BookingStatus] = None
    ) -> List[Booking]:
        """Get all bookings for a vehicle, optionally filtered by status"""
        query = db.query(Booking).filter(Booking.vehicle_id == vehicle_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.order_by(Booking.start_time.desc()).all()
