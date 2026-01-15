from app.routes.auth import router as auth_router
from app.routes.vehicle import router as vehicle_router
from app.routes.booking import router as booking_router
from app.routes.trip import router as trip_router
from app.routes.analytics import router as analytics_router

__all__ = [
    "auth_router",
    "vehicle_router",
    "booking_router",
    "trip_router",
    "analytics_router",
]
