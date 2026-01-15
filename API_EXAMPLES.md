# API Examples & Use Cases

This document provides practical examples for common fleet management scenarios.

## Table of Contents

1. [User Registration & Login](#user-registration--login)
2. [Creating Vehicles](#creating-vehicles)
3. [Booking Workflow](#booking-workflow)
4. [Handling Conflicts](#handling-conflicts)
5. [Analytics Queries](#analytics-queries)

---

## User Registration & Login

### Step 1: Register a New User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_driver",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "role": "user"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "username": "john_driver",
  "email": "john@example.com",
  "role": "user",
  "is_active": true,
  "created_at": "2026-01-15T10:00:00"
}
```

### Step 2: Login to Get Tokens

```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_driver",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Save the `access_token` - you'll use it for all API requests.

### Step 3: Refresh Access Token (After Expiration)

```bash
curl -X POST http://localhost:8000/api/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

---

## Creating Vehicles

### Fleet Manager: Add New Vehicle

```bash
# Register fleet manager first
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "fleet_ops",
    "email": "fleet@ridecell.com",
    "password": "FleetPass123!",
    "role": "fleet_manager"
  }'
```

Login to get fleet_manager token, then add vehicles:

```bash
FLEET_TOKEN="<fleet_manager_access_token>"

curl -X POST http://localhost:8000/api/vehicles \
  -H "Authorization: Bearer $FLEET_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "license_plate": "SF-2023-001",
    "make": "Tesla",
    "model": "Model 3",
    "year": 2023,
    "location": "San Francisco Downtown",
    "mileage": 15000.0
  }'
```

Response:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440111",
  "license_plate": "SF-2023-001",
  "make": "Tesla",
  "model": "Model 3",
  "year": 2023,
  "status": "available",
  "location": "San Francisco Downtown",
  "mileage": 15000.0,
  "health_score": 100.0,
  "is_active": true,
  "created_at": "2026-01-15T10:00:00"
}
```

### List All Available Vehicles

```bash
USER_TOKEN="<user_access_token>"

curl -X GET "http://localhost:8000/api/vehicles?status=available&location=San Francisco" \
  -H "Authorization: Bearer $USER_TOKEN"
```

---

## Booking Workflow

### Scenario: User Books a Vehicle

**Timeline**:
- Jan 20, 10:00 AM - 2:00 PM (4-hour booking)

#### Step 1: Check Availability

```bash
USER_TOKEN="<user_access_token>"
VEHICLE_ID="660e8400-e29b-41d4-a716-446655440111"

curl -X GET "http://localhost:8000/api/bookings/vehicle/$VEHICLE_ID/availability" \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d "start_time=2026-01-20T10:00:00&end_time=2026-01-20T14:00:00"
```

Response:
```json
{
  "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
  "is_available": true,
  "conflicting_bookings": 0,
  "start_time": "2026-01-20T10:00:00",
  "end_time": "2026-01-20T14:00:00"
}
```

#### Step 2: Create Booking

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
    "start_time": "2026-01-20T10:00:00",
    "end_time": "2026-01-20T14:00:00"
  }'
```

Response:
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440222",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
  "start_time": "2026-01-20T10:00:00",
  "end_time": "2026-01-20T14:00:00",
  "status": "confirmed",
  "created_at": "2026-01-15T10:00:00",
  "updated_at": "2026-01-15T10:00:00"
}
```

#### Step 3: Start Trip

When the user picks up the vehicle:

```bash
BOOKING_ID="770e8400-e29b-41d4-a716-446655440222"

curl -X POST http://localhost:8000/api/trips \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "booking_id": "'$BOOKING_ID'",
    "start_location": "50 Market St, San Francisco",
    "mileage_start": 15000.0
  }'
```

Response:
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440333",
  "booking_id": "770e8400-e29b-41d4-a716-446655440222",
  "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "start_time": "2026-01-20T10:05:30",
  "end_time": null,
  "start_location": "50 Market St, San Francisco",
  "distance_traveled": 0.0,
  "mileage_start": 15000.0,
  "mileage_end": null,
  "created_at": "2026-01-15T10:00:00"
}
```

#### Step 4: End Trip

When the user returns the vehicle:

```bash
TRIP_ID="880e8400-e29b-41d4-a716-446655440333"

curl -X PUT http://localhost:8000/api/trips/$TRIP_ID \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "end_location": "SFO Airport, Terminal 1",
    "mileage_end": 15045.5
  }'
```

Response:
```json
{
  "id": "880e8400-e29b-41d4-a716-446655440333",
  "end_time": "2026-01-20T13:55:00",
  "end_location": "SFO Airport, Terminal 1",
  "distance_traveled": 45.5,
  "mileage_end": 15045.5,
  "...": "..."
}
```

---

## Handling Conflicts

### Scenario: Booking Conflict

Two users try to book the same vehicle for overlapping times.

#### User A Books 10:00-14:00

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer $TOKEN_A" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
    "start_time": "2026-01-20T10:00:00",
    "end_time": "2026-01-20T14:00:00"
  }'
```

✅ Success: 201 Created

#### User B Tries to Book 12:00-16:00 (Overlaps!)

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
    "start_time": "2026-01-20T12:00:00",
    "end_time": "2026-01-20T16:00:00"
  }'
```

❌ Error: 409 Conflict
```json
{
  "detail": "Vehicle has 1 conflicting booking(s) in the requested time window"
}
```

#### User B Books Non-Overlapping Time (14:00-18:00) ✅

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer $TOKEN_B" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
    "start_time": "2026-01-20T14:00:00",
    "end_time": "2026-01-20T18:00:00"
  }'
```

✅ Success: 201 Created

---

## Analytics Queries

### Fleet Manager: Vehicle Utilization

```bash
FLEET_TOKEN="<fleet_manager_token>"
VEHICLE_ID="660e8400-e29b-41d4-a716-446655440111"

curl -X GET "http://localhost:8000/api/analytics/vehicle/$VEHICLE_ID/utilization" \
  -H "Authorization: Bearer $FLEET_TOKEN" \
  -d "start_date=2026-01-01T00:00:00&end_date=2026-01-31T23:59:59"
```

Response:
```json
{
  "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-01-31T23:59:59",
  "utilization_percentage": 62.5,
  "total_trips": 18,
  "total_distance_km": 1450.75,
  "total_hours_in_use": 180.5,
  "idle_hours": 499.5,
  "average_trip_duration_hours": 10.03
}
```

**Interpretation**:
- Vehicle is in use 62.5% of the time (good utilization)
- 18 trips, averaging 10 hours each
- 1450.75 km traveled, ~80.6 km per trip

### Fleet Analytics

```bash
curl -X GET "http://localhost:8000/api/analytics/fleet/utilization" \
  -H "Authorization: Bearer $FLEET_TOKEN" \
  -d "start_date=2026-01-01T00:00:00&end_date=2026-01-31T23:59:59&location=San Francisco"
```

Response:
```json
{
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-01-31T23:59:59",
  "location": "San Francisco",
  "total_vehicles": 45,
  "active_vehicles": 38,
  "fleet_utilization_percentage": 68.3,
  "total_trips": 892,
  "total_distance_km": 35400.0,
  "peak_usage_hours": ["09:00-10:00", "12:00-13:00", "17:00-18:00"],
  "fleet_efficiency_score": 82.1
}
```

**Decision Making**:
- Fleet efficiency is 82.1/100 - good but room for improvement
- Peak hours are 9-10 AM, 12-1 PM, 5-6 PM - plan maintenance outside these times
- 7 vehicles not in use (45-38) - consider fleet right-sizing

### Identify Underutilized Vehicles

```bash
curl -X GET "http://localhost:8000/api/analytics/fleet/underutilized-vehicles" \
  -H "Authorization: Bearer $FLEET_TOKEN" \
  -d "start_date=2026-01-01&end_date=2026-01-31&threshold_percentage=25"
```

Response:
```json
[
  {
    "vehicle_id": "660e8400-e29b-41d4-a716-446655440111",
    "license_plate": "SF-OLD-005",
    "utilization_percentage": 12.3,
    "total_trips": 2,
    "health_score": 65.0
  },
  {
    "vehicle_id": "660e8400-e29b-41d4-a716-446655440222",
    "license_plate": "SF-OLD-006",
    "utilization_percentage": 18.5,
    "total_trips": 5,
    "health_score": 45.0
  }
]
```

**Action Items**:
1. Relocate underutilized vehicles to high-demand areas
2. Schedule maintenance for low health scores
3. Consider retiring vehicles SF-OLD-005 and SF-OLD-006

### Booking Statistics

```bash
curl -X GET "http://localhost:8000/api/analytics/bookings/statistics" \
  -H "Authorization: Bearer $FLEET_TOKEN" \
  -d "start_date=2026-01-01&end_date=2026-01-31"
```

Response:
```json
{
  "start_date": "2026-01-01T00:00:00",
  "end_date": "2026-01-31T23:59:59",
  "total_bookings": 950,
  "completed_bookings": 902,
  "cancelled_bookings": 48,
  "completion_rate": 94.95
}
```

---

## Advanced Use Cases

### Case Study 1: Peak Hour Capacity Planning

**Question**: How many vehicles do we need in the 9-10 AM slot?

```bash
# Step 1: Get peak hours from fleet analytics
GET /api/analytics/fleet/utilization
# Returns: "peak_usage_hours": ["09:00-10:00", "12:00-13:00", "17:00-18:00"]

# Step 2: Query bookings for 9-10 AM slot across multiple days
GET /api/bookings?status=confirmed
# Filter for start_time in [09:00-10:00] range

# Step 3: Calculate demand vs supply
demand = count(bookings in 9-10 AM) / days_in_period
current_vehicles = total_active_vehicles
utilization = demand / current_vehicles * 100

# If utilization > 85%, need more vehicles
# If utilization < 40%, can reduce fleet
```

### Case Study 2: Predictive Maintenance

```bash
# Get vehicles needing maintenance (health_score < 30%)
GET /api/vehicles/maintenance/needed

# Schedule maintenance outside peak hours
peak_hours = ["09:00-10:00", "12:00-13:00", "17:00-18:00"]
suggested_maintenance = "08:00-09:00 or 14:00-15:00"

# Mark vehicle as MAINTENANCE
PUT /api/vehicles/{vehicle_id}
{
  "status": "maintenance"
}
```

### Case Study 3: Dynamic Pricing

```bash
# Analyze peak vs off-peak demand
peak_utilization = 75%     # 9-10 AM
offpeak_utilization = 30%  # 3-4 AM

pricing_strategy = {
  "peak_hours": "1.5x base price",
  "standard_hours": "1.0x base price",
  "offpeak_hours": "0.5x base price"
}

# Implement via separate pricing engine (not in this API)
```

---

## Error Handling Examples

### Case 1: Invalid Token

```bash
curl -X GET http://localhost:8000/api/vehicles \
  -H "Authorization: Bearer invalid_token"
```

Response: 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### Case 2: Unauthorized Access

```bash
# Regular user tries to delete a vehicle (Admin only)
curl -X DELETE http://localhost:8000/api/vehicles/{vehicle_id} \
  -H "Authorization: Bearer $USER_TOKEN"
```

Response: 403 Forbidden
```json
{
  "detail": "Insufficient permissions. Admin role required."
}
```

### Case 3: Not Found

```bash
curl -X GET http://localhost:8000/api/bookings/invalid-id \
  -H "Authorization: Bearer $USER_TOKEN"
```

Response: 404 Not Found
```json
{
  "detail": "Booking not found"
}
```

### Case 4: Invalid Request

```bash
curl -X POST http://localhost:8000/api/bookings \
  -H "Authorization: Bearer $USER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vehicle_id": "invalid-uuid",
    "start_time": "2026-01-20",
    "end_time": "2026-01-19"  # End before start!
  }'
```

Response: 400 Bad Request
```json
{
  "detail": "Start time must be before end time"
}
```

---

## Python Client Example

```python
import requests
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8000/api"
ACCESS_TOKEN = None


def login(username: str, password: str):
    global ACCESS_TOKEN
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": username, "password": password}
    )
    ACCESS_TOKEN = response.json()["access_token"]
    return ACCESS_TOKEN


def book_vehicle(vehicle_id: str, start_time: datetime, end_time: datetime):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    response = requests.post(
        f"{BASE_URL}/bookings",
        headers=headers,
        json={
            "vehicle_id": vehicle_id,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat()
        }
    )
    return response.json()


# Usage
login("john_driver", "SecurePass123!")

# Book vehicle for tomorrow 10-14:00
tomorrow_10am = datetime.now() + timedelta(days=1, hours=10)
tomorrow_2pm = datetime.now() + timedelta(days=1, hours=14)

booking = book_vehicle(
    vehicle_id="660e8400-e29b-41d4-a716-446655440111",
    start_time=tomorrow_10am,
    end_time=tomorrow_2pm
)

print(f"Booking confirmed: {booking['id']}")
```

---

**More examples and code snippets available in the repository.**
