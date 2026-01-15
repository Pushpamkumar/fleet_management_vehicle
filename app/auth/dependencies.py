from fastapi import Depends, HTTPException, status, Header
from typing import Optional
from app.auth.security import verify_token, TokenData
from app.database import get_db
from app.models import User
from sqlalchemy.orm import Session


async def get_current_user(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Extract and validate the current user from JWT token"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    token_data = verify_token(token)
    
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify token is access token
    if token_data.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Fetch user from database
    user = db.query(User).filter(User.id == token_data["user_id"]).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user


async def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Admin role required."
        )
    return current_user


async def get_current_fleet_manager(current_user: User = Depends(get_current_user)) -> User:
    """Require fleet manager or admin role"""
    allowed_roles = ["fleet_manager", "admin"]
    if current_user.role.value not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions. Fleet Manager role required."
        )
    return current_user


def get_current_user_optional(
    authorization: str = Header(None)
) -> Optional[TokenData]:
    """Optionally extract user from token (may be None)"""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    
    try:
        token = authorization.split(" ")[1]
        token_data = verify_token(token)
        return token_data
    except Exception:
        return None
