import pytest
from datetime import datetime, timedelta
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Vehicle, Booking, User
from app.services import BookingService, BookingConflictError
from app.schemas import VehicleStatus, BookingStatus, UserRole


@pytest.fixture
def test_db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    return SessionLocal()


def test_check_availability_no_conflicts(test_db):
    """Test availability check with no conflicts"""
    vehicle_id = uuid.uuid4()
    start_time = datetime.utcnow() + timedelta(hours=1)
    end_time = start_time + timedelta(hours=2)
    
    is_available = BookingService.check_availability(test_db, vehicle_id, start_time, end_time)
    assert is_available is True


def test_booking_conflict_detection(test_db):
    """Test that booking conflicts are detected"""
    vehicle_id = uuid.uuid4()
    user_id = uuid.uuid4()
    
    # Create user and vehicle
    user = User(
        id=user_id,
        username="testuser",
        email="test@example.com",
        hashed_password="hashed",
        role=UserRole.USER
    )
    test_db.add(user)
    
    vehicle = Vehicle(
        id=vehicle_id,
        license_plate="ABC123",
        make="Toyota",
        model="Camry",
        year=2023,
        status=VehicleStatus.AVAILABLE
    )
    test_db.add(vehicle)
    test_db.commit()
    
    # Create first booking
    start1 = datetime.utcnow() + timedelta(hours=1)
    end1 = start1 + timedelta(hours=2)
    
    booking1 = Booking(
        id=uuid.uuid4(),
        user_id=user_id,
        vehicle_id=vehicle_id,
        start_time=start1,
        end_time=end1,
        status=BookingStatus.CONFIRMED
    )
    test_db.add(booking1)
    test_db.commit()
    
    # Check availability for overlapping time
    start2 = start1 + timedelta(minutes=30)
    end2 = start2 + timedelta(hours=1)
    
    is_available = BookingService.check_availability(test_db, vehicle_id, start2, end2)
    assert is_available is False
    
    # Check availability for non-overlapping time
    start3 = end1 + timedelta(hours=1)
    end3 = start3 + timedelta(hours=2)
    
    is_available = BookingService.check_availability(test_db, vehicle_id, start3, end3)
    assert is_available is True
