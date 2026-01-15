import pytest
from app.auth import hash_password, verify_password, create_access_token, verify_token


def test_hash_password():
    """Test password hashing"""
    password = "test_password_123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_token_creation_and_verification():
    """Test JWT token creation and verification"""
    user_id = "test-user-id"
    username = "testuser"
    role = "user"
    
    token = create_access_token(user_id, username, role)
    assert token is not None
    
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded["user_id"] == user_id
    assert decoded["username"] == username
    assert decoded["role"] == role
    assert decoded["type"] == "access"
