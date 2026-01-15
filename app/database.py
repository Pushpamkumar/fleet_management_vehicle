from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL from environment or use default PostgreSQL
#DATABASE_URL = os.getenv("postgresql://postgres:Pushp%40m009@localhost:5432/fleet_management")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Pushp%40m009@localhost:5432/fleet_management"
)



engine = create_engine(
    DATABASE_URL,
    echo=os.getenv("SQL_ECHO", "False").lower() == "true",
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,  # Verify connections before using
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to provide database sessions"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    from app.models import User, Vehicle, Booking, Trip
    Base.metadata.create_all(bind=engine)
