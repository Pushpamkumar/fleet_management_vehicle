from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.database import Base


class Trip(Base):
    __tablename__ = "trips"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    start_location = Column(String(255), nullable=True)
    end_location = Column(String(255), nullable=True)
    distance_traveled = Column(Float, default=0.0, nullable=False)  # in km
    mileage_start = Column(Float, nullable=False)
    mileage_end = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_trip_vehicle_date', 'vehicle_id', 'start_time'),
        Index('idx_trip_user_date', 'user_id', 'start_time'),
    )

    def get_duration_hours(self) -> float:
        """Calculate trip duration in hours"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds() / 3600.0
        return 0.0

    def __repr__(self):
        return f"<Trip(id={self.id}, booking_id={self.booking_id}, vehicle_id={self.vehicle_id})>"
