from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import Trip, Booking, Vehicle
from app.schemas import BookingStatus
import uuid


class AnalyticsService:
    """Service for computing fleet utilization and operational metrics"""
    
    @staticmethod
    def get_vehicle_utilization(
        db: Session,
        vehicle_id: uuid.UUID,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """
        Calculate vehicle utilization metrics for a given time period.
        
        Metrics:
        - Utilization percentage (hours in use / total hours)
        - Total trips
        - Total distance traveled
        - Average trip duration
        """
        # Get completed trips
        trips = db.query(Trip).filter(
            Trip.vehicle_id == vehicle_id,
            Trip.start_time >= start_date,
            Trip.start_time <= end_date,
            Trip.end_time.isnot(None)
        ).all()
        
        total_hours = (end_date - start_date).total_seconds() / 3600.0
        
        if not trips:
            return {
                "vehicle_id": str(vehicle_id),
                "start_date": start_date,
                "end_date": end_date,
                "utilization_percentage": 0.0,
                "total_trips": 0,
                "total_distance_km": 0.0,
                "total_hours_in_use": 0.0,
                "average_trip_duration_hours": 0.0,
                "idle_hours": total_hours
            }
        
        total_distance = sum(trip.distance_traveled for trip in trips)
        total_hours_in_use = sum(trip.get_duration_hours() for trip in trips)
        
        return {
            "vehicle_id": str(vehicle_id),
            "start_date": start_date,
            "end_date": end_date,
            "utilization_percentage": round((total_hours_in_use / total_hours) * 100, 2) if total_hours > 0 else 0,
            "total_trips": len(trips),
            "total_distance_km": round(total_distance, 2),
            "total_hours_in_use": round(total_hours_in_use, 2),
            "average_trip_duration_hours": round(total_hours_in_use / len(trips), 2) if trips else 0,
            "idle_hours": round(total_hours - total_hours_in_use, 2)
        }
    
    @staticmethod
    def get_fleet_utilization(
        db: Session,
        start_date: datetime,
        end_date: datetime,
        location: Optional[str] = None
    ) -> Dict:
        """
        Calculate fleet-wide utilization metrics.
        
        Metrics:
        - Overall utilization percentage
        - Number of active vehicles
        - Peak usage hours
        - Fleet efficiency score
        """
        # Get vehicles (optionally filtered by location)
        vehicle_query = db.query(Vehicle).filter(Vehicle.is_active == True)
        if location:
            vehicle_query = vehicle_query.filter(Vehicle.location == location)
        
        vehicles = vehicle_query.all()
        
        if not vehicles:
            return {
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "total_vehicles": 0,
                "active_vehicles": 0,
                "fleet_utilization_percentage": 0.0,
                "total_trips": 0,
                "total_distance_km": 0.0,
                "peak_usage_hours": [],
                "fleet_efficiency_score": 0.0
            }
        
        total_hours = (end_date - start_date).total_seconds() / 3600.0
        available_vehicle_hours = len(vehicles) * total_hours
        
        # Get all trips
        trips = db.query(Trip).filter(
            Trip.start_time >= start_date,
            Trip.start_time <= end_date,
            Trip.end_time.isnot(None)
        ).all()
        
        total_distance = sum(trip.distance_traveled for trip in trips)
        total_hours_in_use = sum(trip.get_duration_hours() for trip in trips)
        
        utilization_percentage = (total_hours_in_use / available_vehicle_hours * 100) if available_vehicle_hours > 0 else 0
        
        # Calculate peak usage hours
        peak_hours = AnalyticsService._calculate_peak_hours(trips)
        
        # Fleet efficiency score (0-100)
        # Based on utilization and distance per hour
        distance_per_hour = (total_distance / total_hours_in_use) if total_hours_in_use > 0 else 0
        efficiency_score = min(100, (utilization_percentage * 0.6) + (min(distance_per_hour / 50, 1) * 40))
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "location": location,
            "total_vehicles": len(vehicles),
            "active_vehicles": len([v for v in vehicles if v.status.value == "in_use"]),
            "fleet_utilization_percentage": round(utilization_percentage, 2),
            "total_trips": len(trips),
            "total_distance_km": round(total_distance, 2),
            "peak_usage_hours": peak_hours,
            "fleet_efficiency_score": round(efficiency_score, 2)
        }
    
    @staticmethod
    def get_underutilized_vehicles(
        db: Session,
        start_date: datetime,
        end_date: datetime,
        threshold_percentage: float = 20.0
    ) -> List[Dict]:
        """
        Identify vehicles with utilization below threshold.
        Useful for optimization and asset reallocation decisions.
        """
        vehicles = db.query(Vehicle).filter(Vehicle.is_active == True).all()
        
        underutilized = []
        for vehicle in vehicles:
            metrics = AnalyticsService.get_vehicle_utilization(db, vehicle.id, start_date, end_date)
            if metrics["utilization_percentage"] < threshold_percentage:
                underutilized.append({
                    "vehicle_id": metrics["vehicle_id"],
                    "license_plate": vehicle.license_plate,
                    "utilization_percentage": metrics["utilization_percentage"],
                    "total_trips": metrics["total_trips"],
                    "health_score": vehicle.health_score
                })
        
        return sorted(underutilized, key=lambda x: x["utilization_percentage"])
    
    @staticmethod
    def _calculate_peak_hours(trips: List[Trip]) -> List[str]:
        """Calculate peak usage hours from trip data"""
        if not trips:
            return []
        
        hour_counts = {}
        for trip in trips:
            hour = trip.start_time.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Get top 3 peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        return [f"{hour:02d}:00-{hour+1:02d}:00" for hour, count in sorted_hours]
    
    @staticmethod
    def get_booking_statistics(
        db: Session,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Get booking statistics for a date range"""
        total_bookings = db.query(Booking).filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date
        ).count()
        
        completed_bookings = db.query(Booking).filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == BookingStatus.COMPLETED
        ).count()
        
        cancelled_bookings = db.query(Booking).filter(
            Booking.created_at >= start_date,
            Booking.created_at <= end_date,
            Booking.status == BookingStatus.CANCELLED
        ).count()
        
        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_bookings": total_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "completion_rate": round((completed_bookings / total_bookings * 100), 2) if total_bookings > 0 else 0
        }
