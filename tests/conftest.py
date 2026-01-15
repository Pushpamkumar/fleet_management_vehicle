import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def db():
    """Create test database"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="module")
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def user_token(client):
    """Get user token for testing"""
    # Register user
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
            "role": "user"
        }
    )
    
    # Login and get token
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "password123"
        }
    )
    
    return response.json()["access_token"]
