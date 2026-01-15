# Fleet Management System Tests

Test suite for the fleet management backend system.

## Running Tests

```bash
# Install test dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## Test Structure

- `test_auth.py` - Authentication and security tests
- `test_booking_service.py` - Booking service and concurrency tests
- `conftest.py` - Fixtures and test setup
