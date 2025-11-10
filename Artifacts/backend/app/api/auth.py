"""
Authentication API endpoints.

This module provides endpoints for user authentication:
- Login with email and password
- User session management
"""
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app import crud, schemas
from app.core import security
from app.db.session import get_db
from app.models import SystemRole

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)


class LoginRequest(BaseModel):
    """Login request payload."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with user data."""
    user: schemas.UserResponse
    message: str = "Login successful"


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate user with email and password",
)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate a user by email and password.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns user data if authentication is successful.
    Raises 401 if credentials are invalid.
    """
    # Look up user by email
    user = crud.get_user_by_email(db, email=credentials.email)
    
    if not user:
        logger.warning(f"Login attempt for non-existent email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Verify password
    if not security.verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed login attempt for user: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    # Check if user is active
    if not user.is_active:
        logger.warning(f"Login attempt for inactive user: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive. Contact your administrator.",
        )
    
    # Check if user has appropriate role for login
    if user.system_role == SystemRole.EMPLOYEE:
        logger.warning(f"Login attempt by employee: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Employee accounts are read-only. Request PM or Admin access.",
        )
    
    logger.info(f"Successful login for user: {credentials.email} (ID: {user.id})")
    
    return LoginResponse(user=user)

