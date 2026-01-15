# Quick Start Guide

Get the Fleet Management System up and running in 5 minutes!

## Option 1: Docker (Recommended)

**Requirements**: Docker & Docker Compose

```bash
# 1. Clone/navigate to project
cd fleet-management

# 2. Start all services (PostgreSQL + Redis + API)
docker-compose up -d

# 3. Verify services are running
docker-compose ps

# 4. API is ready at: http://localhost:8000
# Docs at: http://localhost:8000/api/docs
```

**Stopping**:
```bash
docker-compose down
```

---

## Option 2: Local Installation

**Requirements**: Python 3.11+, PostgreSQL 13+, Redis 7+

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Set Up Database

```bash
# Create PostgreSQL database
createdb fleet_management

# Set database credentials in .env
cat > .env << EOF
DATABASE_URL=postgresql://postgres:password@localhost:5432/fleet_management
SECRET_KEY=your-secret-key-change-in-production
REDIS_URL=redis://localhost:6379/0
RELOAD=True
EOF
```

### Step 3: Start Redis

```bash
# On macOS (using Homebrew)
redis-server

# On Linux
sudo systemctl start redis

# Or using Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Step 4: Run Application

```bash
python -m uvicorn app.main:app --reload
```

API is ready at: `http://localhost:8000`

---

## Testing the API

### 1. Check Health

```bash
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "service": "Fleet Management API",
  "version": "1.0.0"
}
```

### 2. Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "role": "user"
  }'
```

### 3. Login to Get Token

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'

# Response
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Save the `access_token` to a variable:

```bash
export TOKEN="<access_token_from_above>"
```

### 4. List Vehicles

```bash
curl -X GET http://localhost:8000/api/vehicles \
  -H "Authorization: Bearer $TOKEN"

# Response: Empty array (no vehicles yet)
[]
```

### 5. Create a Vehicle (Fleet Manager Only)

First, create a fleet manager account:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "fleet_ops",
    "email": "fleet@example.com",
    "password": "SecurePass123!",
    "role": "fleet_manager"
  }'

# Login as fleet manager
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "fleet_ops",
    "password": "SecurePass123!"
  }'

# Save fleet manager token
export FLEET_TOKEN="<fleet_manager_token>"
```

Now create a vehicle:

```bash
curl -X POST http://localhost:8000/api/vehicles \
  -H "Authorization: Bearer $FLEET_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "license_plate": "SF-2023-001",
    "make": "Tesla",
    "model": "Model 3",
    "year": 2023,
    "location": "San Francisco",
    "mileage": 15000.0
  }'

# Response
{
  "id": "660e8400-e29b-41d4-a716-446655440111",
  "license_plate": "SF-2023-001",
  "status": "available",
  "health_score": 100.0,
  ...
}
```

Save the vehicle ID:

```bash
export VEHICLE_ID="660e8400-e29b-41d4-a716-446655440111"
```

### 6. Book a Vehicle

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "'$VEHICLE_ID'",
    "start_time": "2026-01-20T10:00:00",
    "end_time": "2026-01-20T14:00:00"
  }'

# Response
{
  "id": "770e8400-e29b-41d4-a716-446655440222",
  "status": "confirmed",
  ...
}
```

### 7. Check Availability

```bash
curl -X GET "http://localhost:8000/api/bookings/vehicle/$VEHICLE_ID/availability?start_time=2026-01-20T14:00:00&end_time=2026-01-20T18:00:00" \
  -H "Authorization: Bearer $TOKEN"

# Response
{
  "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
  "is_available": true,
  "conflicting_bookings": 0
}
```

---

## Using the Interactive API Docs

FastAPI provides interactive documentation:

### Swagger UI
```
http://localhost:8000/api/docs
```

### ReDoc
```
http://localhost:8000/api/redoc
```

You can:
- See all endpoints
- Test endpoints directly in the browser
- View request/response schemas
- View error codes

---

## Project Structure

```
fleet-management/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── auth/                # JWT & security
│   │   ├── security.py
│   │   ├── dependencies.py
│   │   └── __init__.py
│   ├── models/              # SQLAlchemy models
│   │   ├── user.py
│   │   ├── vehicle.py
│   │   ├── booking.py
│   │   ├── trip.py
│   │   └── __init__.py
│   ├── schemas/             # Pydantic schemas
│   │   ├── user.py
│   │   ├── vehicle.py
│   │   ├── booking.py
│   │   ├── trip.py
│   │   ├── common.py
│   │   └── __init__.py
│   ├── services/            # Business logic
│   │   ├── booking_service.py
│   │   ├── vehicle_service.py
│   │   ├── trip_service.py
│   │   ├── analytics_service.py
│   │   └── __init__.py
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── vehicle.py
│   │   ├── booking.py
│   │   ├── trip.py
│   │   ├── analytics.py
│   │   └── __init__.py
│   └── middleware/          # Custom middleware
├── tests/                   # Test suite
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_booking_service.py
│   └── __init__.py
├── migrations/              # Database migrations (Alembic)
├── docker-compose.yml       # Docker services
├── Dockerfile               # API container
├── requirements.txt         # Dependencies
├── requirements-dev.txt     # Dev dependencies
├── .env                     # Environment variables
├── .env.example             # Example env file
├── README.md                # Full documentation
├── ARCHITECTURE.md          # Design decisions
├── API_EXAMPLES.md          # API usage examples
└── QUICKSTART.md            # This file
```

---

## Common Tasks

### Run Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_booking_service.py
```

### View API Logs

```bash
# Docker logs
docker-compose logs app

# With live follow
docker-compose logs -f app
```

### Access Database

```bash
# Connect to PostgreSQL
psql -U postgres -d fleet_management

# Common queries
SELECT * FROM users;
SELECT * FROM vehicles WHERE status = 'available';
SELECT * FROM bookings WHERE status = 'confirmed';
SELECT COUNT(*) FROM trips;
```

### Generate Sample Data

```python
# Create a Python script: seed_data.py
from app.database import SessionLocal
from app.models import User, Vehicle
from app.auth import hash_password
from app.schemas import UserRole, VehicleStatus
import uuid

db = SessionLocal()

# Create users
admin = User(
    id=uuid.uuid4(),
    username="admin",
    email="admin@example.com",
    hashed_password=hash_password("admin123"),
    role=UserRole.ADMIN
)
db.add(admin)

# Create fleet manager
fleet_mgr = User(
    id=uuid.uuid4(),
    username="fleet_manager",
    email="fleet@example.com",
    hashed_password=hash_password("fleet123"),
    role=UserRole.FLEET_MANAGER
)
db.add(fleet_mgr)

# Create vehicles
for i in range(10):
    vehicle = Vehicle(
        id=uuid.uuid4(),
        license_plate=f"SF-2023-{i:03d}",
        make="Toyota",
        model="Camry",
        year=2023,
        location="San Francisco",
        mileage=10000.0 + (i * 1000),
        status=VehicleStatus.AVAILABLE
    )
    db.add(vehicle)

db.commit()
print("✅ Sample data created!")
```

Run it:
```bash
python seed_data.py
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use different port
python -m uvicorn app.main:app --port 8001
```

### Database Connection Error

```bash
# Check PostgreSQL is running
psql --version

# Test connection
psql -U postgres -d fleet_management

# Check .env DATABASE_URL is correct
cat .env | grep DATABASE_URL
```

### Redis Connection Error

```bash
# Check Redis is running
redis-cli ping

# If using Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### JWT Token Errors

- **"Invalid or expired token"**: Token may have expired (30 min). Use refresh token.
- **"Invalid token type"**: Using refresh token instead of access token.
- **"User not found or inactive"**: User was deleted or deactivated.

---

## Performance Tips

1. **Use Database Indexes**: Already configured for common queries
2. **Cache Vehicle Availability**: Redis caching reduces DB hits
3. **Batch Operations**: Instead of 100 create calls, batch them
4. **Pagination**: Use limit/offset for large result sets
5. **Connection Pooling**: Already configured (pool_size=20)

---

## Next Steps

1. **Read Full Documentation**:
   - [README.md](README.md) - Complete API reference
   - [ARCHITECTURE.md](ARCHITECTURE.md) - Design decisions
   - [API_EXAMPLES.md](API_EXAMPLES.md) - Real-world examples

2. **Explore Features**:
   - Create users with different roles
   - Test booking conflict detection
   - Generate analytics reports
   - Try token refresh flow

3. **Deploy**:
   - Use docker-compose for development
   - Deploy to AWS ECS/Kubernetes for production
   - Set up monitoring and alerting

---

## Getting Help

- Check [README.md](README.md) for detailed API docs
- See [API_EXAMPLES.md](API_EXAMPLES.md) for code samples
- Review error messages in responses
- Check logs: `docker-compose logs -f app`

---

**Happy coding! 🚀**
