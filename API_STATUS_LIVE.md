# 🚀 Fleet Management System - API Status: LIVE ✅

**Server Status**: ✅ **RUNNING**  
**Base URL**: `http://localhost:8000`  
**API Docs**: `http://localhost:8000/api/docs`  
**Last Updated**: January 15, 2026

---

## 📊 All Running Endpoints

### 🔐 Authentication Routes (`/api/auth`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/auth/register` | Register new user | ✅ LIVE |
| POST | `/api/auth/login` | Login and get JWT token | ✅ LIVE |
| POST | `/api/auth/refresh` | Refresh access token | ✅ LIVE |
| GET | `/api/auth/me` | Get current user profile | ✅ LIVE |
| PUT | `/api/auth/me` | Update user profile | ✅ LIVE |

**Example: Register User**
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "role": "user"
  }'
```

---

### 🚗 Vehicle Routes (`/api/vehicles`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/vehicles` | List all vehicles | ✅ LIVE |
| GET | `/api/vehicles/{id}` | Get vehicle details | ✅ LIVE |
| POST | `/api/vehicles` | Create new vehicle | ✅ LIVE |
| PUT | `/api/vehicles/{id}` | Update vehicle | ✅ LIVE |
| DELETE | `/api/vehicles/{id}` | Delete vehicle (soft-delete) | ✅ LIVE |
| GET | `/api/vehicles/status/{status}` | Filter by status | ✅ LIVE |
| POST | `/api/vehicles/{id}/start-trip` | Start vehicle trip | ✅ LIVE |
| POST | `/api/vehicles/{id}/end-trip` | End vehicle trip | ✅ LIVE |
| GET | `/api/vehicles/maintenance/list` | Get maintenance alerts | ✅ LIVE |

**Example: Create Vehicle**
```bash
curl -X POST "http://localhost:8000/api/vehicles" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "license_plate": "ABC123XYZ",
    "make": "Toyota",
    "model": "Camry",
    "year": 2024,
    "location": "Warehouse A"
  }'
```

---

### 📅 Booking Routes (`/api/bookings`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/bookings` | Create booking (concurrency-safe) | ✅ LIVE |
| GET | `/api/bookings` | List user bookings | ✅ LIVE |
| GET | `/api/bookings/{id}` | Get booking details | ✅ LIVE |
| PUT | `/api/bookings/{id}` | Update booking | ✅ LIVE |
| DELETE | `/api/bookings/{id}` | Cancel booking | ✅ LIVE |
| POST | `/api/bookings/{id}/confirm` | Confirm booking | ✅ LIVE |
| GET | `/api/bookings/check-availability` | Check vehicle availability | ✅ LIVE |

**Example: Check Availability (Double-Booking Prevention)**
```bash
curl -X GET "http://localhost:8000/api/bookings/check-availability" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "vehicle-uuid",
    "start_time": "2026-01-20T10:00:00Z",
    "end_time": "2026-01-20T18:00:00Z"
  }'
```

---

### 🛣️ Trip Routes (`/api/trips`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| POST | `/api/trips/start` | Start trip | ✅ LIVE |
| POST | `/api/trips/{id}/end` | End trip (auto-calculate distance) | ✅ LIVE |
| GET | `/api/trips` | List trips | ✅ LIVE |
| GET | `/api/trips/{id}` | Get trip details | ✅ LIVE |
| GET | `/api/trips/vehicle/{vehicle_id}` | Trips by vehicle | ✅ LIVE |
| GET | `/api/trips/user/{user_id}` | Trips by user | ✅ LIVE |

**Example: Start Trip**
```bash
curl -X POST "http://localhost:8000/api/trips/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "booking-uuid",
    "vehicle_id": "vehicle-uuid",
    "start_location": "Start Point",
    "mileage_start": 15000
  }'
```

---

### 📈 Analytics Routes (`/api/analytics`)

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/api/analytics/vehicle-utilization` | Vehicle utilization % | ✅ LIVE |
| GET | `/api/analytics/fleet-utilization` | Fleet-wide utilization | ✅ LIVE |
| GET | `/api/analytics/underutilized-vehicles` | Find underutilized vehicles | ✅ LIVE |
| GET | `/api/analytics/booking-statistics` | Booking stats | ✅ LIVE |
| GET | `/api/analytics/peak-hours` | Peak booking hours | ✅ LIVE |

**Example: Fleet Utilization**
```bash
curl -X GET "http://localhost:8000/api/analytics/fleet-utilization?start_date=2026-01-01&end_date=2026-01-31" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 🏥 System Routes

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| GET | `/health` | Health check | ✅ LIVE |
| GET | `/` | Root/welcome | ✅ LIVE |

---

## 🔒 Authentication

All protected endpoints require JWT token in the `Authorization` header:

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

**Get token:**
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "SecurePass123!"
  }'
```

Response will include:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

---

## 📋 Role-Based Access Control

- **Admin**: Full access to all endpoints
- **Fleet Manager**: Can manage vehicles and view analytics
- **User**: Can create bookings and view own trips

---

## 🌐 Interactive API Testing

### Swagger UI (Best for testing)
- **URL**: `http://localhost:8000/api/docs`
- **Features**: Try endpoints, see responses, auto-generated docs

### ReDoc (Read-only docs)
- **URL**: `http://localhost:8000/api/redoc`
- **Features**: Beautiful API documentation

---

## 💾 Database Status

- **Type**: SQLite (Development) / PostgreSQL (Production)
- **Tables**: Users, Vehicles, Bookings, Trips
- **Status**: ✅ Initialized and ready

---

## 🚀 Key Features Working

✅ **Double-Booking Prevention** - Row-level locking prevents concurrent bookings  
✅ **JWT Authentication** - Secure token-based auth with refresh tokens  
✅ **Role-Based Access** - Admin, Fleet Manager, User roles  
✅ **Vehicle Lifecycle** - Status tracking (available, in_use, maintenance)  
✅ **Analytics** - Fleet utilization, vehicle metrics, peak hours  
✅ **Trip Tracking** - Auto-distance calculation, mileage tracking  
✅ **Concurrency Safe** - SELECT FOR UPDATE for booking conflicts  

---

## 📝 Example Workflow

1. **Register User**
   ```bash
   POST /api/auth/register
   ```

2. **Login & Get Token**
   ```bash
   POST /api/auth/login
   ```

3. **Create Vehicle** (Admin/Fleet Manager)
   ```bash
   POST /api/vehicles
   ```

4. **Check Availability**
   ```bash
   GET /api/bookings/check-availability
   ```

5. **Create Booking**
   ```bash
   POST /api/bookings
   ```

6. **Start Trip**
   ```bash
   POST /api/trips/start
   ```

7. **End Trip**
   ```bash
   POST /api/trips/{id}/end
   ```

8. **View Analytics**
   ```bash
   GET /api/analytics/fleet-utilization
   ```

---

## 🛠️ Tech Stack

- **Framework**: FastAPI (Python)
- **Database**: SQLite / PostgreSQL
- **Authentication**: JWT (PyJWT)
- **ORM**: SQLAlchemy 2.0
- **Validation**: Pydantic
- **Server**: Uvicorn

---

## 📦 Dependencies

All installed and ready:
- fastapi
- uvicorn
- sqlalchemy
- pydantic
- pydantic-settings
- python-jose
- passlib
- PyJWT
- python-dotenv
- psycopg2-binary (PostgreSQL driver)
- email-validator
- redis

---

**Status**: 🟢 **FULLY OPERATIONAL**  
**All 26+ Endpoints**: ✅ Running  
**Authentication**: ✅ Enabled  
**Database**: ✅ Connected  
**Documentation**: ✅ Available
