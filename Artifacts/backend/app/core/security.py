"""
Security utilities for password hashing and JWT token management.

This module provides functions for securely hashing passwords using bcrypt
and creating/verifying JWT tokens for authentication.
"""
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from .config import settings

# Configure password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain-text password matches a hashed password.
    
    Args:
        plain_password: The password to verify (plain text)
        hashed_password: The hashed password to compare against
        
    Returns:
        True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a plain-text password using bcrypt.
    
    Args:
        password: The plain-text password to hash
        
    Returns:
        The hashed password string
    """
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token with the provided data.
    
    Args:
        data: The data to encode in the token (typically includes 'sub' with user ID)
        expires_delta: Optional custom expiration time. If not provided, uses default from settings
        
    Returns:
        The encoded JWT token as a string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Create a JWT refresh token with the provided data.
    
    Refresh tokens have a longer expiration time than access tokens.
    
    Args:
        data: The data to encode in the token (typically includes 'sub' with user ID)
        
    Returns:
        The encoded JWT refresh token as a string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Decode and verify a JWT token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        The decoded token payload as a dictionary, or None if invalid
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

