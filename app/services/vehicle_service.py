from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models import Vehicle
from app.schemas import VehicleStatus
import uuid


class VehicleService:
    """Service for managing vehicle lifecycle and operations"""
    
    @staticmethod
    def create_vehicle(
        db: Session,
        license_plate: str,
        make: str,
        model: str,
        year: int,
        location: Optional[str] = None,
        mileage: float = 0.0
    ) -> Vehicle:
        """Create a new vehicle"""
        vehicle = Vehicle(
            id=uuid.uuid4(),
            license_plate=license_plate,
            make=make,
            model=model,
            year=year,
            location=location,
            mileage=mileage,
            status=VehicleStatus.AVAILABLE,
            health_score=100.0
        )
        
        db.add(vehicle)
        return vehicle
    
    @staticmethod
    def get_vehicle_by_id(db: Session, vehicle_id: uuid.UUID) -> Optional[Vehicle]:
        """Get a vehicle by ID"""
        return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    
    @staticmethod
    def get_all_vehicles(db: Session, status: Optional[VehicleStatus] = None) -> List[Vehicle]:
        """Get all active vehicles, optionally filtered by status"""
        query = db.query(Vehicle).filter(Vehicle.is_active == True)
        
        if status:
            query = query.filter(Vehicle.status == status)
        
        return query.order_by(Vehicle.created_at.desc()).all()
    
    @staticmethod
    def get_available_vehicles(
        db: Session,
        location: Optional[str] = None
    ) -> List[Vehicle]:
        """Get all available vehicles, optionally filtered by location"""
        query = db.query(Vehicle).filter(
            Vehicle.is_active == True,
            Vehicle.status == VehicleStatus.AVAILABLE
        )
        
        if location:
            query = query.filter(Vehicle.location == location)
        
        return query.order_by(Vehicle.created_at.desc()).all()
    
    @staticmethod
    def update_vehicle_status(
        db: Session,
        vehicle_id: uuid.UUID,
        new_status: VehicleStatus
    ) -> Vehicle:
        """Update vehicle status with validation"""
        vehicle = VehicleService.get_vehicle_by_id(db, vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        # Validate state transitions
        valid_transitions = {
            VehicleStatus.AVAILABLE: [VehicleStatus.IN_USE, VehicleStatus.MAINTENANCE, VehicleStatus.INACTIVE],
            VehicleStatus.IN_USE: [VehicleStatus.AVAILABLE, VehicleStatus.MAINTENANCE],
            VehicleStatus.MAINTENANCE: [VehicleStatus.AVAILABLE],
            VehicleStatus.INACTIVE: [VehicleStatus.AVAILABLE]
        }
        
        if new_status not in valid_transitions.get(vehicle.status, []):
            raise ValueError(
                f"Invalid state transition from {vehicle.status} to {new_status}"
            )
        
        vehicle.status = new_status
        return vehicle
    
    @staticmethod
    def update_vehicle_mileage(
        db: Session,
        vehicle_id: uuid.UUID,
        new_mileage: float
    ) -> Vehicle:
        """Update vehicle mileage"""
        vehicle = VehicleService.get_vehicle_by_id(db, vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        if new_mileage < vehicle.mileage:
            raise ValueError("Mileage cannot decrease")
        
        vehicle.mileage = new_mileage
        
        # Update health score based on mileage (predictive maintenance)
        # Health decreases gradually with mileage
        max_mileage = 500000  # Assume vehicle lifecycle ends at 500k km
        health_percentage = max(0, 100 * (1 - (new_mileage / max_mileage)))
        vehicle.health_score = round(health_percentage, 2)
        
        return vehicle
    
    @staticmethod
    def update_vehicle_location(
        db: Session,
        vehicle_id: uuid.UUID,
        location: str
    ) -> Vehicle:
        """Update vehicle location"""
        vehicle = VehicleService.get_vehicle_by_id(db, vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        vehicle.location = location
        return vehicle
    
    @staticmethod
    def soft_delete_vehicle(db: Session, vehicle_id: uuid.UUID) -> Vehicle:
        """Soft-delete a vehicle (mark as inactive)"""
        vehicle = VehicleService.get_vehicle_by_id(db, vehicle_id)
        if not vehicle:
            raise ValueError(f"Vehicle {vehicle_id} not found")
        
        vehicle.is_active = False
        vehicle.status = VehicleStatus.INACTIVE
        return vehicle
    
    @staticmethod
    def get_vehicles_needing_maintenance(db: Session) -> List[Vehicle]:
        """Get vehicles with health score below threshold"""
        MAINTENANCE_THRESHOLD = 30.0  # Percentage
        
        return db.query(Vehicle).filter(
            Vehicle.is_active == True,
            Vehicle.health_score < MAINTENANCE_THRESHOLD
        ).order_by(Vehicle.health_score.asc()).all()
