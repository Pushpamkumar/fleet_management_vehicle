# Architecture & Design Decisions

This document explains the architectural choices and technical decisions made in the Fleet Management System.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Database Design](#database-design)
3. [Concurrency Handling](#concurrency-handling)
4. [API Design Principles](#api-design-principles)
5. [Security](#security)
6. [Scalability](#scalability)

---

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│              (Web / Mobile / Third-party APIs)               │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS
                         ↓
┌─────────────────────────────────────────────────────────────┐
│                     API Gateway                              │
│            (Rate limiting, Load balancing)                   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ↓
┌──────────────────────────────────────────────────────────────┐
│                  FastAPI Application                         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Middleware & Dependency                 │  │
│  │         Injection (Auth, Logging, CORS)              │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            API Routes / Handlers                     │  │
│  │  • Auth Router      • Vehicle Router                 │  │
│  │  • Booking Router   • Trip Router                    │  │
│  │  • Analytics Router                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Service Layer (Business Logic)              │  │
│  │  • BookingService      • VehicleService              │  │
│  │  • TripService         • AnalyticsService            │  │
│  └──────────────────────────────────────────────────────┘  │
│                         ↓                                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       Data Access Layer (SQLAlchemy ORM)             │  │
│  │         • Database Session Management                │  │
│  │         • Query Building & Optimization              │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────┬──────────────────────┬───────────────────┬─────┘
             │                      │                   │
             ↓                      ↓                   ↓
       ┌──────────────────────────────────┐   ┌──────────────────┐
       │     PostgreSQL Database          │   │  Redis Cache     │
       │                                  │   │                  │
       │  ✓ ACID Transactions             │   │  ✓ Session Store │
       │  ✓ Row-level Locking             │   │  ✓ Distributed   │
       │  ✓ Composite Indexes             │   │    Locks         │
       │  ✓ Constraint Validation         │   │  ✓ Rate Limiting │
       │                                  │   │                  │
       └──────────────────────────────────┘   └──────────────────┘
```

### Why This Architecture?

**Separation of Concerns**
- Routes handle HTTP contract
- Services contain business logic
- Models define data structure
- Auth/Middleware are cross-cutting

**Testability**
- Services can be tested independently
- Mock database for unit tests
- Integration tests with test database

**Maintainability**
- Clear responsibility boundaries
- Easy to locate code by function
- Minimal coupling between layers

---

## Database Design

### Entity Relationship Diagram

```
┌─────────────┐
│    Users    │
├─────────────┤
│ id (PK)     │
│ username    │ (unique, indexed)
│ email       │ (unique, indexed)
│ hashed_pwd  │
│ role        │ (enum: admin, fleet_manager, user)
│ is_active   │
│ created_at  │
│ updated_at  │
└─────────────┘
       │
       │ (1:N)
       │
       └─────────────────────────┐
                                 │
                    ┌────────────┴──────────┐
                    ↓                       ↓
            ┌──────────────┐       ┌──────────────┐
            │  Bookings    │       │   Trips      │
            ├──────────────┤       ├──────────────┤
            │ id (PK)      │       │ id (PK)      │
            │ user_id (FK) │       │ booking_id   │
            │ vehicle_id   │       │ vehicle_id   │
            │ start_time   │       │ user_id      │
            │ end_time     │       │ start_time   │
            │ status       │       │ end_time     │
            │ created_at   │       │ distance_km  │
            │ version      │       │ mileage_*    │
            │ (Indexes:    │       │ created_at   │
            │  vehicle_id, │       │ (Indexes:    │
            │  start_time) │       │  vehicle_id, │
            └──────────────┘       │  start_time) │
                    ↑              └──────────────┘
                    │
                    │ (1:N)
                    │
            ┌───────────────┐
            │   Vehicles    │
            ├───────────────┤
            │ id (PK)       │
            │ license_plate │ (unique, indexed)
            │ make, model   │
            │ year          │
            │ status        │ (enum, indexed)
            │ location      │
            │ mileage       │
            │ health_score  │
            │ is_active     │
            │ created_at    │
            │ updated_at    │
            │ (Indexes:     │
            │  status,      │
            │  is_active)   │
            └───────────────┘
```

### Index Strategy

**High-Performance Indexes**:

```sql
-- Booking conflict detection (critical path)
CREATE INDEX idx_booking_vehicle_time 
ON bookings(vehicle_id, start_time, end_time) 
WHERE status IN ('confirmed', 'pending');

-- User bookings lookup
CREATE INDEX idx_booking_user_status 
ON bookings(user_id, status);

-- Vehicle availability queries
CREATE INDEX idx_vehicle_status_active 
ON vehicles(status, is_active);

-- Trip time-based queries
CREATE INDEX idx_trip_vehicle_date 
ON trips(vehicle_id, start_time);

-- License plate lookup (unique)
CREATE UNIQUE INDEX idx_vehicle_license_plate 
ON vehicles(license_plate);

-- Username/email lookup (unique)
CREATE UNIQUE INDEX idx_user_username 
ON users(username);

CREATE UNIQUE INDEX idx_user_email 
ON users(email);
```

**Why These Indexes?**
- Booking queries run on (vehicle_id, time) - composite index is optimal
- Vehicle availability filtered by status - helps WHERE clause
- Trip analytics need date range queries - prefix index on vehicle_id

### Schema Constraints

**Foreign Keys with Cascades**:
```sql
ALTER TABLE bookings 
ADD CONSTRAINT fk_booking_vehicle 
FOREIGN KEY (vehicle_id) 
REFERENCES vehicles(id) ON DELETE CASCADE;

ALTER TABLE bookings 
ADD CONSTRAINT fk_booking_user 
FOREIGN KEY (user_id) 
REFERENCES users(id) ON DELETE CASCADE;

ALTER TABLE trips 
ADD CONSTRAINT fk_trip_booking 
FOREIGN KEY (booking_id) 
REFERENCES bookings(id) ON DELETE CASCADE;
```

**Check Constraints**:
```sql
-- Ensure valid status values
ALTER TABLE vehicles 
ADD CONSTRAINT check_vehicle_status 
CHECK (status IN ('available', 'in_use', 'maintenance', 'inactive'));

-- Ensure end_time > start_time
ALTER TABLE bookings 
ADD CONSTRAINT check_booking_time 
CHECK (end_time > start_time);

-- Health score 0-100
ALTER TABLE vehicles 
ADD CONSTRAINT check_health_score 
CHECK (health_score >= 0 AND health_score <= 100);
```

---

## Concurrency Handling

### The Double-Booking Problem

**Scenario**: Two users simultaneously book the same vehicle for overlapping times.

```
Timeline:
T1: User A queries availability for Jan 20, 10:00-14:00 → Available
T2: User B queries availability for Jan 20, 12:00-16:00 → Available
T3: User A creates booking 10:00-14:00 → ✅ Success
T4: User B creates booking 12:00-16:00 → ❌ Should fail!

Without proper locking, both would succeed (race condition).
```

### Solution: Row-Level Locking + Transactions

```python
def create_booking(db, user_id, vehicle_id, start_time, end_time):
    # 1. Lock vehicle row (SELECT FOR UPDATE)
    vehicle = db.query(Vehicle)\
        .filter(Vehicle.id == vehicle_id)\
        .with_for_update()\  # ← Row-level exclusive lock
        .first()
    
    # 2. Check availability within the transaction
    # No new bookings can be created between check and insert
    conflicts = db.query(Booking).filter(
        Booking.vehicle_id == vehicle_id,
        Booking.start_time < end_time,
        Booking.end_time > start_time,
        Booking.status.in_(['confirmed', 'pending'])
    ).count()
    
    if conflicts > 0:
        raise BookingConflictError()
    
    # 3. Create booking
    booking = Booking(...)
    db.add(booking)
    
    # 4. Commit atomically
    db.commit()  # Lock released here
```

### Lock Sequence

```
User A Timeline          User B Timeline
├─ Begin Txn             ├─ Begin Txn
├─ Lock Vehicle Row      ├─ Wait for lock... (blocked)
├─ Check availability    │
├─ Create booking        │
├─ Commit (Release lock) │
                         ├─ Acquire lock
                         ├─ Check availability → CONFLICT!
                         ├─ Rollback
                         └─ Return 409
```

### Optimistic Locking (Alternative)

For cases where row-level locking is too heavy:

```python
# Booking model includes version field
class Booking(Base):
    version = Column(TIMESTAMP, default=datetime.utcnow)

# Update only if version matches
def update_booking(db, booking_id, expected_version):
    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.version == expected_version
    ).update({
        Booking.status: BookingStatus.CANCELLED,
        Booking.version: datetime.utcnow()
    })
    
    if booking == 0:
        # Someone else modified it
        raise ConcurrentModificationError()
```

---

## API Design Principles

### RESTful Resource Modeling

```
Resources        CRUD Operations      Status Codes

/vehicles        GET (list)           200 OK
                 POST (create)        201 Created
                 GET (detail)         400 Bad Request
                 PUT (update)         404 Not Found
                 DELETE (soft)        409 Conflict

/bookings        GET (list)           500 Server Error
                 POST (create)
                 GET (detail)
                 PUT (update)
```

### Idempotent Design

**Problem**: Network failures may cause duplicate requests.

**Solution**: Idempotent operations for critical workflows.

```python
# Booking creation is idempotent
# Client can safely retry if network fails

# Request 1: User creates booking X
POST /api/bookings
{
  "vehicle_id": "123",
  "start_time": "2026-01-20T10:00:00",
  "end_time": "2026-01-20T14:00:00"
}
# Network failure → retry

# Request 2 (retry): Same data
# Database UNIQUE constraint on (vehicle_id, start_time, end_time, user_id)
# ensures no duplicate booking created
```

### Error Response Standardization

```json
{
  "detail": "Human-readable error message",
  "status_code": 400,
  "type": "validation_error"  // (optional)
}
```

### Pagination (for future expansion)

```python
# Example for listing bookings
GET /api/bookings?page=1&page_size=50&sort=-created_at

# Response includes metadata
{
  "items": [...],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total": 250,
    "pages": 5
  }
}
```

---

## Security

### JWT Authentication Flow

```
1. User Login
   ├─ Validate credentials (password hash)
   ├─ Generate JWT payload
   │  ├─ sub: user_id
   │  ├─ role: user_role
   │  ├─ exp: exp_time (30 min)
   │  └─ type: "access"
   └─ Return access_token + refresh_token

2. API Request
   ├─ Client includes: Authorization: Bearer {token}
   ├─ Server verifies JWT signature
   ├─ Check token not expired
   ├─ Extract user_id and role
   └─ Check role-based permissions

3. Token Expiration
   ├─ Access token expires after 30 minutes
   ├─ Client uses refresh_token to get new access_token
   ├─ Refresh token valid for 7 days
   └─ User must re-login after 7 days
```

### Password Security

```python
# Use bcrypt (industry standard)
hashed = bcrypt.hash(password, rounds=12)

# Verify password
verified = bcrypt.verify(plain_password, hashed)
```

**Never store plain passwords!**

### CORS Configuration

```python
# Only allow trusted origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://app.example.com",
        "https://admin.example.com"
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"]
)
```

### Input Validation

All inputs validated at API boundary using Pydantic:

```python
class BookingCreate(BaseModel):
    vehicle_id: UUID  # Type validation
    start_time: datetime  # Format validation
    end_time: datetime
    
    @field_validator('start_time')
    def validate_future(cls, v):
        if v <= datetime.utcnow():
            raise ValueError('Must be future time')
        return v
```

---

## Scalability

### Horizontal Scaling

```
┌────────────────────────────────────────────┐
│            Load Balancer                   │
│          (nginx / ALB)                     │
└─────────┬──────────────────────────────────┘
          │
    ┌─────┼─────┬─────────┐
    ↓     ↓     ↓         ↓
  ┌──┐  ┌──┐  ┌──┐      ┌──┐
  │ 1│  │ 2│  │ 3│  ... │ N│  API Instances
  │  │  │  │  │  │      │  │  (Stateless)
  └──┘  └──┘  └──┘      └──┘
    │     │     │         │
    └─────┼─────┴─────────┘
          │
      ┌───┴────────────┐
      ↓                ↓
┌─────────────┐  ┌──────────┐
│ PostgreSQL  │  │  Redis   │
│ (Primary)   │  │ (Cache)  │
└─────────────┘  └──────────┘
```

**Why Stateless?**
- API instances share no local state
- Requests can go to any instance
- Easy to add/remove instances
- Failures don't impact other instances

### Database Optimization

**Connection Pooling**:
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,          # 20 connections in pool
    max_overflow=0,        # Don't create extra connections
    pool_pre_ping=True     # Verify connections before use
)
```

**Query Optimization**:
- Use composite indexes for common queries
- Eager load relationships when needed
- Avoid N+1 queries (use joins)

**Caching Strategy**:
```python
# Redis caching for vehicle availability
# Instead of: SELECT ... FROM bookings WHERE vehicle_id = ?
# Cache: available:{vehicle_id}:{date} → True/False

# Invalidate cache when booking created/cancelled
def create_booking(...):
    booking = BookingService.create_booking(...)
    redis.delete(f"available:{booking.vehicle_id}:{booking.start_time.date()}")
    db.commit()
```

### Rate Limiting

```python
# Prevent abuse of booking API
# Max 10 bookings per user per day

@app.post("/api/bookings")
@rate_limit(max_calls=10, time_window=timedelta(hours=24))
def create_booking(...):
    ...
```

### Monitoring & Observability

```
├─ Metrics
│  ├─ Request latency (p50, p95, p99)
│  ├─ Error rates by endpoint
│  ├─ Database query times
│  └─ Cache hit rates
│
├─ Logging
│  ├─ Request/response logging
│  ├─ Booking conflict logs (for analysis)
│  └─ Database transaction logs
│
└─ Alerting
   ├─ High error rate (>5%)
   ├─ Booking conflicts spike
   └─ Database connection pool exhaustion
```

---

## Summary of Design Choices

| Aspect | Choice | Reason |
|--------|--------|--------|
| Framework | FastAPI | Async, built-in validation, auto docs |
| Database | PostgreSQL | ACID, row-level locking, indexes |
| Auth | JWT | Stateless, scalable, industry standard |
| Concurrency | Row-level locks | Prevents race conditions atomically |
| Caching | Redis | Fast, distributed, versatile |
| ORM | SQLAlchemy | Explicit control, good for locking |
| API Style | REST | Intuitive, standardized, cacheable |

---

**Last Updated**: January 2026
