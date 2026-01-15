from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user, get_current_fleet_manager, get_current_admin
from app.models import User, Vehicle
from app.services import VehicleService
from app.schemas import VehicleCreate, VehicleUpdate, VehicleResponse, VehicleStatus
from datetime import datetime
from typing import List, Optional
import uuid


router = APIRouter(prefix="/api/vehicles", tags=["vehicles"])


@router.get("", response_model=List[VehicleResponse])
def list_vehicles(
    status: Optional[VehicleStatus] = Query(None),
    location: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all vehicles, optionally filtered by status or location"""
    if status:
        vehicles = db.query(Vehicle).filter(
            Vehicle.is_active == True,
            Vehicle.status == status
        ).all()
    else:
        vehicles = VehicleService.get_all_vehicles(db)
    
    if location:
        vehicles = [v for v in vehicles if v.location == location]
    
    return vehicles


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    vehicle_data: VehicleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_fleet_manager)
):
    """Create a new vehicle (Fleet Manager only)"""
    # Check if vehicle with same license plate exists
    existing = db.query(Vehicle).filter(Vehicle.license_plate == vehicle_data.license_plate).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle with this license plate already exists"
        )
    
    vehicle = VehicleService.create_vehicle(
        db,
        license_plate=vehicle_data.license_plate,
        make=vehicle_data.make,
        model=vehicle_data.model,
        year=vehicle_data.year,
        location=vehicle_data.location,
        mileage=vehicle_data.mileage
    )
    
    db.commit()
    db.refresh(vehicle)
    
    return vehicle


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get vehicle details"""
    try:
        vid = uuid.UUID(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vehicle ID")
    
    vehicle = VehicleService.get_vehicle_by_id(db, vid)
    if not vehicle or not vehicle.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    return vehicle


@router.put("/{vehicle_id}", response_model=VehicleResponse)
def update_vehicle(
    vehicle_id: str,
    update_data: VehicleUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_fleet_manager)
):
    """Update vehicle details (Fleet Manager only)"""
    try:
        vid = uuid.UUID(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vehicle ID")
    
    vehicle = VehicleService.get_vehicle_by_id(db, vid)
    if not vehicle or not vehicle.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    try:
        if update_data.status:
            vehicle = VehicleService.update_vehicle_status(db, vid, update_data.status)
        
        if update_data.location:
            vehicle = VehicleService.update_vehicle_location(db, vid, update_data.location)
        
        if update_data.mileage is not None:
            vehicle = VehicleService.update_vehicle_mileage(db, vid, update_data.mileage)
        
        if update_data.health_score is not None:
            vehicle.health_score = update_data.health_score
        
        db.commit()
        db.refresh(vehicle)
        
        return vehicle
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Soft-delete a vehicle (Admin only)"""
    try:
        vid = uuid.UUID(vehicle_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid vehicle ID")
    
    vehicle = VehicleService.get_vehicle_by_id(db, vid)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    
    VehicleService.soft_delete_vehicle(db, vid)
    db.commit()


@router.get("/maintenance/needed", response_model=List[VehicleResponse])
def get_vehicles_needing_maintenance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_fleet_manager)
):
    """Get vehicles that need maintenance (Fleet Manager only)"""
    vehicles = VehicleService.get_vehicles_needing_maintenance(db)
    return vehicles
