"""
Core utilities for the IELTS Mock Test System.

This package contains:
- config: Application configuration and settings
- security: Authentication, authorization, and password management
"""

from .config import settings
from .security import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    get_current_user,
    get_current_admin_user,
    get_current_teacher_user,
    oauth2_scheme,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

__all__ = [
    # Config
    "settings",
    
    # Security - Password
    "get_password_hash",
    "verify_password",
    
    # Security - JWT
    "create_access_token",
    "decode_access_token",
    "ACCESS_TOKEN_EXPIRE_MINUTES",
    
    # Security - Dependencies
    "get_current_user",
    "get_current_admin_user",
    "get_current_teacher_user",
    "oauth2_scheme",
]
