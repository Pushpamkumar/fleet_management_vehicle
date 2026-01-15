# Complete Directory Structure

Fleet Management System - Production-Grade Backend

```
fleet-management and vehicle/
│
├── 📁 app/                              # Main application code
│   ├── __init__.py                      # Package initialization
│   ├── main.py                          # FastAPI app factory
│   ├── config.py                        # Configuration from environment
│   ├── database.py                      # SQLAlchemy setup
│   │
│   ├── 📁 auth/                         # Authentication & Security
│   │   ├── __init__.py
│   │   ├── security.py                  # JWT tokens, password hashing
│   │   └── dependencies.py              # FastAPI dependency injection
│   │
│   ├── 📁 models/                       # SQLAlchemy ORM Models
│   │   ├── __init__.py
│   │   ├── user.py                      # User model with role enum
│   │   ├── vehicle.py                   # Vehicle lifecycle model
│   │   ├── booking.py                   # Booking with concurrency control
│   │   └── trip.py                      # Trip tracking model
│   │
│   ├── 📁 schemas/                      # Pydantic validation schemas
│   │   ├── __init__.py
│   │   ├── user.py                      # User request/response schemas
│   │   ├── vehicle.py                   # Vehicle schemas
│   │   ├── booking.py                   # Booking schemas
│   │   ├── trip.py                      # Trip schemas
│   │   └── common.py                    # Shared schemas
│   │
│   ├── 📁 services/                     # Business logic layer
│   │   ├── __init__.py
│   │   ├── booking_service.py           # Concurrency-safe bookings
│   │   ├── vehicle_service.py           # Vehicle operations
│   │   ├── trip_service.py              # Trip management
│   │   └── analytics_service.py         # Fleet analytics
│   │
│   ├── 📁 routes/                       # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py                      # Auth endpoints
│   │   ├── vehicle.py                   # Vehicle CRUD endpoints
│   │   ├── booking.py                   # Booking endpoints
│   │   ├── trip.py                      # Trip endpoints
│   │   └── analytics.py                 # Analytics endpoints
│   │
│   └── 📁 middleware/                   # Custom middleware
│       └── __init__.py
│
├── 📁 tests/                            # Test suite
│   ├── __init__.py
│   ├── conftest.py                      # Pytest fixtures
│   ├── test_auth.py                     # Authentication tests
│   ├── test_booking_service.py           # Concurrency tests
│   └── README.md                        # Testing guide
│
├── 📁 migrations/                       # Database migrations (Alembic)
│   └── (placeholder directory)
│
├── 📄 docker-compose.yml                # Multi-container setup
├── 📄 Dockerfile                        # API container definition
├── 📄 .env                              # Environment variables
├── 📄 requirements.txt                  # Production dependencies
├── 📄 requirements-dev.txt              # Development dependencies
│
└── 📚 Documentation Files
    ├── 📄 README.md                     # Complete API reference
    ├── 📄 QUICKSTART.md                 # 5-minute setup guide
    ├── 📄 ARCHITECTURE.md               # Design & system architecture
    ├── 📄 API_EXAMPLES.md               # Real-world examples
    ├── 📄 PROJECT_SUMMARY.md            # Project overview
    └── 📄 FILE_MANIFEST.md              # File listing
```

---

## 📊 Directory Breakdown

### app/ - Main Application (7 subdirectories, 30+ files)

**Purpose**: Contains all production application code

#### auth/ (3 files)
- JWT token creation and verification
- Password hashing with bcrypt
- Role-based access control dependencies

#### models/ (5 files)
- SQLAlchemy ORM definitions
- User, Vehicle, Booking, Trip entities
- Database constraints and indexes
- Relationship definitions

#### schemas/ (6 files)
- Pydantic validation models
- Request/response schemas
- Input validation with type checking
- Serialization/deserialization

#### services/ (5 files)
- Business logic layer
- Booking conflict detection (concurrency-safe)
- Vehicle lifecycle management
- Trip tracking calculations
- Analytics computations

#### routes/ (6 files)
- FastAPI endpoint definitions
- HTTP request handlers
- Role-based authorization
- Error handling and responses

### tests/ (5 files)

**Purpose**: Test suite and testing utilities

- Pytest fixtures for test setup
- Authentication tests
- Booking service concurrency tests
- Testing documentation

### Deployment Files

**Purpose**: Configuration for running the application

- `docker-compose.yml` - Orchestrates PostgreSQL, Redis, and API
- `Dockerfile` - Containerizes the API
- `.env` - Environment variables
- `requirements.txt` - Python dependencies
- `requirements-dev.txt` - Development tools

### Documentation (6 files)

**Purpose**: Guides and references for using the system

| File | Purpose |
|------|---------|
| README.md | Complete API documentation |
| QUICKSTART.md | Get started in 5 minutes |
| ARCHITECTURE.md | Design decisions and patterns |
| API_EXAMPLES.md | Real-world use cases |
| PROJECT_SUMMARY.md | Project overview |
| FILE_MANIFEST.md | File listing |

---

## 📈 Code Organization Pattern

```
Request Flow:
┌─────────────────────────────────────┐
│  Client Request (HTTP)              │
└──────────────────┬──────────────────┘
                   ↓
        ┌──────────────────────┐
        │  routes/*.py         │
        │  (Endpoint handlers) │
        └──────────┬───────────┘
                   ↓
        ┌──────────────────────┐
        │  schemas/*.py        │
        │  (Validation)        │
        └──────────┬───────────┘
                   ↓
        ┌──────────────────────┐
        │  services/*.py       │
        │  (Business logic)    │
        └──────────┬───────────┘
                   ↓
        ┌──────────────────────┐
        │  models/*.py         │
        │  (Data access)       │
        └──────────┬───────────┘
                   ↓
        ┌──────────────────────┐
        │  PostgreSQL + Redis  │
        │  (Persistence)       │
        └──────────┬───────────┘
                   ↓
┌─────────────────────────────────────┐
│  Response (JSON)                    │
└─────────────────────────────────────┘
```

---

## 🎯 Module Responsibilities

### auth/
- Generate JWT tokens (access + refresh)
- Verify and decode tokens
- Hash passwords with bcrypt
- Dependency injection for routes

### models/
- Define database schema
- Implement validations
- Track relationships
- Support indexing for performance

### schemas/
- Validate incoming requests
- Transform database models to JSON
- Type checking and coercion
- API documentation generation

### services/
- **BookingService**: Conflict detection, concurrency-safe operations
- **VehicleService**: Lifecycle management, state transitions
- **TripService**: Recording usage, calculating metrics
- **AnalyticsService**: Fleet metrics, utilization reports

### routes/
- **auth.py**: Register, login, token refresh
- **vehicle.py**: CRUD operations, maintenance queries
- **booking.py**: Create, list, update bookings, check availability
- **trip.py**: Start/end trips, trip history
- **analytics.py**: Utilization, efficiency, underutilized vehicles

---

## 📦 Dependency Flow

```
routes/
    ↓ depends on ↓
schemas/ + auth/ + services/
    ↓ depends on ↓
models/ + database/
    ↓ depends on ↓
PostgreSQL + Redis
```

---

## 🔧 Configuration Files Explained

### .env (Environment Variables)
```env
DATABASE_URL          # PostgreSQL connection string
SECRET_KEY           # JWT signing key
REDIS_URL            # Redis cache connection
CORS_ORIGINS         # Allowed origins
ACCESS_TOKEN_EXPIRE_MINUTES  # Token TTL
```

### docker-compose.yml
```yaml
services:
  postgres:    # PostgreSQL database
  redis:       # Redis cache
  app:         # FastAPI application
```

### requirements.txt
```
fastapi              # Web framework
uvicorn              # ASGI server
sqlalchemy           # ORM
psycopg2-binary      # PostgreSQL driver
pydantic             # Validation
python-jose          # JWT
passlib              # Password hashing
redis                # Cache client
```

---

## 📝 File Size Reference

| Category | Count | Est. Lines |
|----------|-------|------------|
| App code (models, services, routes) | 20+ | 2000+ |
| Auth, schemas, middleware | 10+ | 500+ |
| Tests | 5 | 200+ |
| Configuration | 3 | 100+ |
| Documentation | 6 | 3000+ |
| **Total** | **44+** | **5800+** |

---

## 🚀 How Files Work Together

### Example: Creating a Booking

1. **Client** sends POST request with booking data
2. **routes/booking.py** receives request
3. **schemas/booking.py** validates input
4. **auth/dependencies.py** checks user authorization
5. **services/booking_service.py** checks conflicts (with row-level locking)
6. **models/booking.py** saves to database
7. Response returned as JSON

### Example: Getting Analytics

1. Client requests `/api/analytics/fleet/utilization`
2. **routes/analytics.py** handles request
3. **auth/dependencies.py** verifies fleet manager role
4. **services/analytics_service.py** computes metrics:
   - Queries **models/trip.py** for trip data
   - Queries **models/vehicle.py** for vehicle data
   - Queries **models/booking.py** for booking stats
   - Calculates utilization percentage, efficiency score, peak hours
5. Returns metrics as JSON

---

## 🔐 Security File Organization

- **auth/security.py**: Token generation, password hashing
- **auth/dependencies.py**: Route-level authorization
- **routes/***: Role-based endpoint protection
- **models/***: Database constraints

---

## 🗄️ Database File Organization

- **models/user.py**: Users table schema
- **models/vehicle.py**: Vehicles table + indexes
- **models/booking.py**: Bookings table + composite indexes
- **models/trip.py**: Trips table + time-based indexes
- **database.py**: Connection management

---

## 📚 Documentation Organization

### Getting Started
1. Start: **QUICKSTART.md** (5 min)
2. Understand: **README.md** (API reference)

### Deep Dive
3. Architecture: **ARCHITECTURE.md** (design decisions)
4. Examples: **API_EXAMPLES.md** (real-world code)

### Reference
5. Summary: **PROJECT_SUMMARY.md** (overview)
6. Files: **FILE_MANIFEST.md** (this document)

---

## 🎓 Learning Path

**Beginner**:
1. Read QUICKSTART.md
2. Run docker-compose up -d
3. Test endpoints in /api/docs

**Intermediate**:
1. Read README.md API reference
2. Study API_EXAMPLES.md
3. Explore routes/ and models/

**Advanced**:
1. Study ARCHITECTURE.md
2. Review services/ for business logic
3. Understand booking concurrency in booking_service.py

---

## 🔄 Development Workflow

```
1. Modify models/         ← Database schema changes
2. Update schemas/        ← API contract changes
3. Implement services/    ← Business logic
4. Add routes/            ← Expose as API
5. Test with tests/       ← Verify functionality
6. Document in docs/      ← Keep examples updated
7. Deploy with docker/    ← Run in containers
```

---

## 📊 Module Dependencies

```
┌─ auth/security.py ─────────────────┐
│  (JWT & passwords)                 │
└──────────┬────────────────────────┘
           ↓
      auth/dependencies.py
      (Inject into routes)
           ↓
      ┌─ routes/*.py ─────────────┐
      │ (API endpoints)           │
      └──────┬────────────────────┘
             ↓
      ┌─ schemas/*.py ─────────────┐
      │ (Validation)               │
      └──────┬────────────────────┘
             ↓
      ┌─ services/*.py ────────────┐
      │ (Business logic)           │
      └──────┬────────────────────┘
             ↓
      ┌─ models/*.py ──────────────┐
      │ (Database)                 │
      └────────────────────────────┘
```

---

## 🎯 Key Architectural Decisions

**Why This Structure?**

1. **Separation of Concerns**: Routes → Schemas → Services → Models
2. **Testability**: Each layer can be tested independently
3. **Reusability**: Services used by different routes
4. **Maintainability**: Changes isolated to specific modules
5. **Scalability**: Easy to add features without refactoring

---

**Project Structure Completed**
**Total Files**: 44+
**Total Lines**: 5800+
**Status**: Production-Ready
