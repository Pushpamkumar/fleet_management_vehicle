from sqlalchemy import Column, String, Float, Integer, Enum, DateTime, Boolean, Index
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import enum
import uuid
from app.database import Base


class VehicleStatus(str, enum.Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_plate = Column(String(50), unique=True, nullable=False, index=True)
    make = Column(String(100), nullable=False)
    model = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(Enum(VehicleStatus), default=VehicleStatus.AVAILABLE, nullable=False, index=True)
    location = Column(String(255), nullable=True)
    mileage = Column(Float, default=0.0, nullable=False)
    health_score = Column(Float, default=100.0, nullable=False)  # 0-100 score for predictive maintenance
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Composite index for querying available vehicles by location
    __table_args__ = (
        Index('idx_vehicle_status_active', 'status', 'is_active'),
    )

    def __repr__(self):
        return f"<Vehicle(id={self.id}, license_plate={self.license_plate}, status={self.status})>"
