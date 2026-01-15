from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, Index, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
import uuid
from app.database import Base


class BookingStatus(str, enum.Enum):
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    PENDING = "pending"


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id", ondelete="CASCADE"), nullable=False, index=True)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)
    status = Column(Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    version = Column(TIMESTAMP(timezone=True), nullable=False, default=datetime.utcnow)  # For optimistic locking

    # Composite indexes for efficient conflict detection
    __table_args__ = (
        Index('idx_booking_vehicle_time', 'vehicle_id', 'start_time', 'end_time'),
        Index('idx_booking_user_status', 'user_id', 'status'),
    )

    def __repr__(self):
        return f"<Booking(id={self.id}, vehicle_id={self.vehicle_id}, user_id={self.user_id}, status={self.status})>"
