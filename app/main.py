from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import auth_router, vehicle_router, booking_router, trip_router, analytics_router
import os


def create_app():
    """Create and configure the FastAPI application"""
    app = FastAPI(
        title="Fleet Management System",
        description="Production-grade backend for fleet and mobility operations",
        version="1.0.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json"
    )
    
    # Initialize database tables (non-blocking)
    try:
        init_db()
    except Exception as e:
        print(f"⚠️  Warning: Database initialization failed: {e}")
        # Continue anyway - app will still work for non-DB operations
    
    # Add CORS middleware
    origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(auth_router)
    app.include_router(vehicle_router)
    app.include_router(booking_router)
    app.include_router(trip_router)
    app.include_router(analytics_router)
    
    # Health check endpoint
    @app.get("/health")
    def health_check():
        return {
            "status": "healthy",
            "service": "Fleet Management API",
            "version": "1.0.0"
        }
    
    # Root endpoint
    @app.get("/")
    def root():
        return {
            "message": "Fleet Management System API",
            "version": "1.0.0",
            "docs_url": "/api/docs",
            "openapi_url": "/api/openapi.json"
        }
    
    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("RELOAD", "True").lower() == "true"
    )
