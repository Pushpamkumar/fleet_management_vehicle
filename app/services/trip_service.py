from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Trip, Booking
from app.schemas import BookingStatus
import uuid


class TripService:
    """Service for managing trips and vehicle usage tracking"""
    
    @staticmethod
    def create_trip(
        db: Session,
        booking_id: uuid.UUID,
        vehicle_id: uuid.UUID,
        user_id: uuid.UUID,
        start_location: Optional[str] = None,
        mileage_start: float = 0.0
    ) -> Trip:
        """Create a new trip from a confirmed booking"""
        trip = Trip(
            id=uuid.uuid4(),
            booking_id=booking_id,
            vehicle_id=vehicle_id,
            user_id=user_id,
            start_time=datetime.utcnow(),
            start_location=start_location,
            mileage_start=mileage_start
        )
        
        db.add(trip)
        return trip
    
    @staticmethod
    def end_trip(
        db: Session,
        trip_id: uuid.UUID,
        end_location: Optional[str] = None,
        mileage_end: float = 0.0
    ) -> Trip:
        """End an active trip"""
        trip = db.query(Trip).filter(Trip.id == trip_id).first()
        if not trip:
            raise ValueError(f"Trip {trip_id} not found")
        
        if trip.end_time:
            raise ValueError("Trip has already been ended")
        
        trip.end_time = datetime.utcnow()
        trip.end_location = end_location
        trip.mileage_end = mileage_end
        
        # Calculate distance traveled
        if mileage_end >= trip.mileage_start:
            trip.distance_traveled = mileage_end - trip.mileage_start
        
        return trip
    
    @staticmethod
    def get_trip_by_id(db: Session, trip_id: uuid.UUID) -> Optional[Trip]:
        """Get a trip by ID"""
        return db.query(Trip).filter(Trip.id == trip_id).first()
    
    @staticmethod
    def get_trips_by_booking(db: Session, booking_id: uuid.UUID) -> List[Trip]:
        """Get all trips associated with a booking"""
        return db.query(Trip).filter(Trip.booking_id == booking_id).all()
    
    @staticmethod
    def get_vehicle_trips(
        db: Session,
        vehicle_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Trip]:
        """Get all trips for a vehicle within a date range"""
        query = db.query(Trip).filter(Trip.vehicle_id == vehicle_id)
        
        if start_date:
            query = query.filter(Trip.start_time >= start_date)
        
        if end_date:
            query = query.filter(Trip.start_time <= end_date)
        
        return query.order_by(Trip.start_time.desc()).all()
    
    @staticmethod
    def get_user_trips(
        db: Session,
        user_id: uuid.UUID,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Trip]:
        """Get all trips for a user within a date range"""
        query = db.query(Trip).filter(Trip.user_id == user_id)
        
        if start_date:
            query = query.filter(Trip.start_time >= start_date)
        
        if end_date:
            query = query.filter(Trip.start_time <= end_date)
        
        return query.order_by(Trip.start_time.desc()).all()
    
    @staticmethod
    def get_completed_trips(
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Trip]:
        """Get all completed trips within a date range"""
        query = db.query(Trip).filter(Trip.end_time.isnot(None))
        
        if start_date:
            query = query.filter(Trip.start_time >= start_date)
        
        if end_date:
            query = query.filter(Trip.start_time <= end_date)
        
        return query.order_by(Trip.start_time.desc()).all()
