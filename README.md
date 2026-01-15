# Fleet Management System - Backend API Documentation

Production-grade backend system for fleet and mobility operations, simulating real-world challenges similar to Ridecell's platform.

## 🌐 **LIVE API - Now Online!**

### **Production URLs:**
- 🚀 **Live API Base**: https://fleetmanagementvehicle-production-9176.up.railway.app/
- 📖 **Interactive Docs (Swagger UI)**: https://fleetmanagementvehicle-production-9176.up.railway.app/api/docs
- 📚 **API Documentation (ReDoc)**: https://fleetmanagementvehicle-production-9176.up.railway.app/api/redoc
- 🏥 **Health Check**: https://fleetmanagementvehicle-production-9176.up.railway.app/health

**Status**: ✅ **LIVE & OPERATIONAL**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Getting Started](#getting-started)
4. [API Endpoints](#api-endpoints)
5. [Authentication](#authentication)
6. [Key Features](#key-features)
7. [Concurrency & Locking](#concurrency--locking)
8. [Analytics](#analytics)

---

## Overview

This system models real fleet-management operations with:

- **Multi-role authentication** (Admin, Fleet Manager, User)
- **Vehicle lifecycle management** with state-machine validation
- **Concurrency-safe booking engine** preventing double-bookings
- **Trip tracking** for vehicle utilization analytics
- **Fleet-wide analytics** for operational insights
- **ACID compliance** with row-level locking

### Key Challenges Solved

✅ **Double Booking Prevention** - Time-window conflict detection with database transactions
✅ **Vehicle Utilization Tracking** - Capture trip data for analytics
✅ **Real-time Availability** - Optimized queries with PostgreSQL indexes and Redis caching
✅ **State Validation** - State-machine logic for vehicle status transitions
✅ **Multi-tenant Support** - Role-based access control for different operational roles

---

## Architecture

```
Client (Web / Mobile)
        ↓
   API Gateway
        ↓
Backend Service (FastAPI)
        ├── Auth Module
        ├── Vehicle Module
        ├── Booking Module (Concurrency-Safe)
        ├── Trip Module
        ├── Analytics Module
        ↓
PostgreSQL (Primary DB)
        ↓
Redis (Caching + Distributed Locks)
```

### Technology Stack

- **Framework**: FastAPI (async Python)
- **Database**: SQLite (development) / PostgreSQL (production)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with role-based access
- **Caching**: Redis (optional)
- **Server**: Uvicorn
- **Testing**: pytest with async support
- **Deployment**: Docker + Railway.app

---

## 🚀 Quick Access

### **Try the Live API Right Now!**

No installation needed - just use the live URLs:

1. **View API Docs**: https://fleetmanagementvehicle-production-9176.up.railway.app/api/docs
   - Try endpoints directly in your browser
   - See request/response examples

2. **Check Health Status**: https://fleetmanagementvehicle-production-9176.up.railway.app/
   - Verify the API is running

3. **Use with Postman/cURL**:
   ```bash
   # Health check
   curl https://fleetmanagementvehicle-production-9176.up.railway.app/health
   
   # Register user
   curl -X POST https://fleetmanagementvehicle-production-9176.up.railway.app/api/auth/register \
     -H "Content-Type: application/json" \
     -d '{"username":"user","email":"user@example.com","password":"Pass123!"}'
   ```

---

## Getting Started

### Prerequisites (for local development)

- Python 3.9+
- PostgreSQL 13+ (optional, SQLite works)
- Redis 7+ (optional for caching)
- Docker & Docker Compose (optional)

### Installation

#### Option 1: Use Live API (No Setup Needed!)

Just visit: https://fleetmanagementvehicle-production-9176.up.railway.app/api/docs

#### Option 2: Docker (Recommended for Local)

```bash
# Clone repository
git clone https://github.com/Pushpamkumar/fleet_management_vehicle.git
cd fleet-management-vehicle

# Start all services
docker-compose up -d

# API available at http://localhost:8000
```

#### Option 3: Local Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Start server (uses SQLite by default)
python -m uvicorn app.main:app --reload

# API available at http://localhost:8000
```

### Configuration

Key environment variables (see `.env`):

```env
# Use SQLite (default)
DATABASE_URL=sqlite:///./fleet_management.db

# Or use PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/fleet_management

SECRET_KEY=your-secret-key-for-jwt
REDIS_URL=redis://localhost:6379/0
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## API Endpoints

### Live API

All endpoints available at: **https://fleetmanagementvehicle-production-9176.up.railway.app**

### Authentication

#### Register User
```
POST /api/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password_123",
  "role": "user"  // "user", "fleet_manager", "admin"
}

Response: 201
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-01-15T10:00:00"
}
```

#### Login
```
POST /api/auth/login
Content-Type: application/json

{
  "username": "john_doe",
  "password": "secure_password_123"
}

Response: 200
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
```
POST /api/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGc..."
}

Response: 200
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Get Current User
```
GET /api/auth/me
Authorization: Bearer {access_token}

Response: 200
{
  "id": "uuid",
  "username": "john_doe",
  "email": "john@example.com",
  "role": "user",
  "is_active": true
}
```

---

### Vehicles

#### Create Vehicle (Fleet Manager only)
```
POST /api/vehicles
Authorization: Bearer {fleet_manager_token}
Content-Type: application/json

{
  "license_plate": "ABC-123",
  "make": "Toyota",
  "model": "Camry",
  "year": 2023,
  "location": "San Francisco",
  "mileage": 5000.0
}

Response: 201
{
  "id": "uuid",
  "license_plate": "ABC-123",
  "make": "Toyota",
  "model": "Camry",
  "year": 2023,
  "status": "available",
  "location": "San Francisco",
  "mileage": 5000.0,
  "health_score": 100.0,
  "is_active": true,
  "created_at": "2026-01-15T10:00:00",
  "updated_at": "2026-01-15T10:00:00"
}
```

#### List Vehicles
```
GET /api/vehicles?status=available&location=San Francisco
Authorization: Bearer {access_token}

Response: 200
[
  {
    "id": "uuid",
    "license_plate": "ABC-123",
    "status": "available",
    ...
  }
]
```

#### Get Vehicle Details
```
GET /api/vehicles/{vehicle_id}
Authorization: Bearer {access_token}

Response: 200
{
  "id": "uuid",
  "license_plate": "ABC-123",
  ...
}
```

#### Update Vehicle
```
PUT /api/vehicles/{vehicle_id}
Authorization: Bearer {fleet_manager_token}
Content-Type: application/json

{
  "status": "maintenance",
  "location": "San Jose",
  "mileage": 6000.0,
  "health_score": 95.0
}

Response: 200
{
  "id": "uuid",
  "status": "maintenance",
  "location": "San Jose",
  "mileage": 6000.0,
  "health_score": 95.0,
  ...
}
```

#### Get Vehicles Needing Maintenance
```
GET /api/vehicles/maintenance/needed
Authorization: Bearer {fleet_manager_token}

Response: 200
[
  {
    "id": "uuid",
    "license_plate": "ABC-123",
    "health_score": 25.0,
    ...
  }
]
```

---

### Bookings

#### Create Booking (Core Feature - Concurrency-Safe)
```
POST /api/bookings
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "vehicle_id": "uuid",
  "start_time": "2026-01-20T10:00:00",
  "end_time": "2026-01-20T14:00:00"
}

Response: 201
{
  "id": "uuid",
  "user_id": "uuid",
  "vehicle_id": "uuid",
  "start_time": "2026-01-20T10:00:00",
  "end_time": "2026-01-20T14:00:00",
  "status": "confirmed",
  "created_at": "2026-01-15T10:00:00",
  "updated_at": "2026-01-15T10:00:00"
}
```

**Error Cases:**

```
409 Conflict - Vehicle has conflicting bookings
{
  "detail": "Vehicle has 1 conflicting booking(s) in the requested time window"
}

400 Bad Request - Invalid vehicle status
{
  "detail": "Vehicle is not available (status: maintenance)"
}
```

#### Check Vehicle Availability
```
GET /api/bookings/vehicle/{vehicle_id}/availability?start_time=2026-01-20T10:00:00&end_time=2026-01-20T14:00:00
Authorization: Bearer {access_token}

Response: 200
{
  "vehicle_id": "uuid",
  "is_available": true,
  "conflicting_bookings": 0,
  "start_time": "2026-01-20T10:00:00",
  "end_time": "2026-01-20T14:00:00"
}
```

#### List Bookings
```
GET /api/bookings?status=confirmed
Authorization: Bearer {access_token}

Response: 200
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "vehicle_id": "uuid",
    "status": "confirmed",
    ...
  }
]
```

#### Get Booking Details
```
GET /api/bookings/{booking_id}
Authorization: Bearer {access_token}

Response: 200
{
  "id": "uuid",
  ...
}
```

#### Update Booking Status
```
PUT /api/bookings/{booking_id}
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "status": "cancelled"
}

Response: 200
{
  "id": "uuid",
  "status": "cancelled",
  ...
}
```

---

### Trips

#### Start Trip
```
POST /api/trips
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "booking_id": "uuid",
  "start_location": "San Francisco Downtown",
  "mileage_start": 5000.0
}

Response: 201
{
  "id": "uuid",
  "booking_id": "uuid",
  "vehicle_id": "uuid",
  "user_id": "uuid",
  "start_time": "2026-01-20T10:05:00",
  "end_time": null,
  "start_location": "San Francisco Downtown",
  "distance_traveled": 0.0,
  "mileage_start": 5000.0,
  "mileage_end": null,
  ...
}
```

#### End Trip
```
PUT /api/trips/{trip_id}
Authorization: Bearer {user_token}
Content-Type: application/json

{
  "end_location": "San Francisco Airport",
  "mileage_end": 5045.0
}

Response: 200
{
  "id": "uuid",
  "end_time": "2026-01-20T14:00:00",
  "end_location": "San Francisco Airport",
  "distance_traveled": 45.0,
  "mileage_end": 5045.0,
  ...
}
```

#### Get Trip Details
```
GET /api/trips/{trip_id}
Authorization: Bearer {user_token}

Response: 200
{
  "id": "uuid",
  ...
}
```

#### Get Vehicle Trips
```
GET /api/trips/vehicle/{vehicle_id}?start_date=2026-01-01&end_date=2026-01-31
Authorization: Bearer {fleet_manager_token}

Response: 200
[
  {
    "id": "uuid",
    "distance_traveled": 45.0,
    ...
  }
]
```

---

### Analytics

#### Vehicle Utilization
```
GET /api/analytics/vehicle/{vehicle_id}/utilization?start_date=2026-01-01&end_date=2026-01-31
Authorization: Bearer {fleet_manager_token}

Response: 200
{
  "vehicle_id": "uuid",
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-01-31T23:59:59",
  "utilization_percentage": 45.5,
  "total_trips": 12,
  "total_distance_km": 450.25,
  "total_hours_in_use": 48.5,
  "idle_hours": 671.5,
  "average_trip_duration_hours": 4.04
}
```

#### Fleet Utilization
```
GET /api/analytics/fleet/utilization?start_date=2026-01-01&end_date=2026-01-31&location=San Francisco
Authorization: Bearer {fleet_manager_token}

Response: 200
{
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-01-31T23:59:59",
  "location": "San Francisco",
  "total_vehicles": 25,
  "active_vehicles": 18,
  "fleet_utilization_percentage": 52.3,
  "total_trips": 250,
  "total_distance_km": 12500.0,
  "peak_usage_hours": ["10:00-11:00", "14:00-15:00", "18:00-19:00"],
  "fleet_efficiency_score": 78.5
}
```

#### Underutilized Vehicles
```
GET /api/analytics/fleet/underutilized-vehicles?start_date=2026-01-01&end_date=2026-01-31&threshold_percentage=20
Authorization: Bearer {fleet_manager_token}

Response: 200
[
  {
    "vehicle_id": "uuid",
    "license_plate": "XYZ-789",
    "utilization_percentage": 15.2,
    "total_trips": 2,
    "health_score": 98.5
  }
]
```

#### Booking Statistics
```
GET /api/analytics/bookings/statistics?start_date=2026-01-01&end_date=2026-01-31
Authorization: Bearer {fleet_manager_token}

Response: 200
{
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-01-31T23:59:59",
  "total_bookings": 500,
  "completed_bookings": 475,
  "cancelled_bookings": 25,
  "completion_rate": 95.0
}
```

---

## Authentication

### JWT Token Flow

1. **User Registration** → Account created with hashed password
2. **Login** → Server issues access + refresh tokens
3. **Access Token** → Short-lived (30 min), used for API requests
4. **Refresh Token** → Long-lived (7 days), used to get new access token
5. **Authorization** → Include access token in `Authorization: Bearer {token}` header

### Roles & Permissions

| Role | Permissions |
|------|-------------|
| **Admin** | Full system access, user management, delete vehicles |
| **Fleet Manager** | Vehicle CRUD, booking management, analytics, trip tracking |
| **User** | Create/view own bookings, view vehicles, track own trips |

### Token Refresh

Access tokens expire after 30 minutes. Use refresh tokens to get new ones:

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "..."}'
```

---

## Key Features

### 1. Concurrency-Safe Booking Engine

**Problem**: Multiple users booking the same vehicle at the same time.

**Solution**:

```python
# Time-window conflict detection
def check_availability(db, vehicle_id, start_time, end_time):
    # Finds overlapping bookings efficiently using indexes
    conflicts = db.query(Booking).filter(
        Booking.vehicle_id == vehicle_id,
        Booking.start_time < end_time,  # Booking starts before requested end
        Booking.end_time > start_time   # Booking ends after requested start
    ).count()
    return conflicts == 0

# Row-level locking via SELECT FOR UPDATE
vehicle = db.query(Vehicle).filter(...).with_for_update().first()

# Atomic transaction ensures data consistency
db.add(booking)
db.commit()  # All-or-nothing
```

**Benefits**:
- Prevents race conditions
- ACID compliance
- Idempotent API design

### 2. Vehicle Lifecycle Management

**States**: AVAILABLE → IN_USE / MAINTENANCE → AVAILABLE

**State Machine Validation**:

```python
valid_transitions = {
    AVAILABLE: [IN_USE, MAINTENANCE, INACTIVE],
    IN_USE: [AVAILABLE, MAINTENANCE],
    MAINTENANCE: [AVAILABLE],
    INACTIVE: [AVAILABLE]
}
```

**Predictive Maintenance**: Health score decreases with mileage.

### 3. Trip Tracking & Analytics

**Automatic Calculations**:
- Distance = mileage_end - mileage_start
- Duration = end_time - start_time
- Vehicle utilization % = (hours_in_use / total_hours) × 100

**Fleet Efficiency Score**: Combines utilization + distance_per_hour

### 4. Real-time Availability

**Optimization**:
- PostgreSQL composite indexes on (vehicle_id, start_time, end_time)
- Redis caching for frequently queried vehicles
- Efficient query plans with EXPLAIN ANALYZE

### 5. Multi-tenant Role-Based Access

**Example**: Users can only view their own bookings; Fleet Managers see all.

---

## Concurrency & Locking

### Database-Level Protection

1. **Row-Level Locking** (SELECT FOR UPDATE)
   - Locks vehicle row during booking creation
   - Prevents race conditions atomically

2. **Optimistic Locking** (Version Field)
   - Booking model includes version timestamp
   - Detects concurrent modifications

3. **Composite Indexes**
   - idx_booking_vehicle_time on (vehicle_id, start_time, end_time)
   - Enables efficient conflict detection

### Example: Double-Booking Prevention

```
Thread 1: Check availability for Jan 20, 10:00-14:00 → ✅ Available
Thread 2: Check availability for Jan 20, 11:00-15:00 → ✅ Available
Thread 1: Lock vehicle, create booking → ✅ Success
Thread 2: Lock vehicle (waits for Thread 1)
Thread 1: Commit, release lock
Thread 2: Acquire lock, check availability → ❌ CONFLICT DETECTED
Thread 2: Rollback, return 409 Conflict
```

---

## Analytics

### Key Metrics

| Metric | Calculation | Use Case |
|--------|------------|----------|
| **Utilization %** | (hours_in_use / total_hours) × 100 | Resource efficiency |
| **Efficiency Score** | Weighted avg of utilization + distance/hour | Overall fleet health |
| **Peak Hours** | Hour with most trips | Capacity planning |
| **Idle Time** | Total hours - hours_in_use | Cost optimization |

### Decision-Making Examples

1. **Underutilized Vehicles** → Relocate or retire
2. **Low Health Scores** → Schedule maintenance
3. **Peak Hours** → Adjust pricing/availability
4. **Cancellation Rate** → Improve booking flow

---

## Error Handling

### HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Booking created |
| 201 | Created | New vehicle added |
| 400 | Bad Request | Invalid date format |
| 401 | Unauthorized | Expired token |
| 403 | Forbidden | User not authorized |
| 404 | Not Found | Vehicle doesn't exist |
| 409 | Conflict | Double booking |
| 500 | Server Error | Database failure |

### Error Response Format

```json
{
  "detail": "Vehicle has 1 conflicting booking(s) in the requested time window"
}
```

---

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# With coverage report
pytest --cov=app --cov-report=html

# Run specific test
pytest tests/test_booking_service.py::test_booking_conflict_detection
```

---

## Deployment

### Docker Deployment

```bash
docker-compose up -d
```

Services:
- API: http://localhost:8000
- PostgreSQL: localhost:5432
- Redis: localhost:6379
- Docs: http://localhost:8000/api/docs

### Production Checklist

- [ ] Change SECRET_KEY
- [ ] Set strong database password
- [ ] Use HTTPS (TLS)
- [ ] Configure CORS properly
- [ ] Set up log aggregation
- [ ] Configure monitoring/alerting
- [ ] Regular backups
- [ ] Load testing

---

## Architecture Highlights

### Why This Design?

✅ **FastAPI**: Async-first, built-in validation, auto docs
✅ **PostgreSQL**: ACID transactions, row-level locking, indexes
✅ **SQLAlchemy**: ORM with explicit locking primitives
✅ **Redis**: Distributed locking, caching, session storage
✅ **JWT**: Stateless, scalable authentication

### Scalability Considerations

- Stateless API (horizontal scaling via load balancer)
- Connection pooling (pool_size=20)
- Database indexes on hot paths
- Redis for caching frequently-accessed data
- Composite indexes for conflict detection

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run full test suite
5. Submit pull request

---

## License

MIT License - See LICENSE file for details

---

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Last Updated**: January 2026
**Version**: 1.0.0
