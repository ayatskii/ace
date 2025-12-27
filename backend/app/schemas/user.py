from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Enums
class UserRoleEnum(str):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: str = Field(default="student", description="User role: student, teacher, or admin")

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class UserResponse(UserBase):
    id: int
    role: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class UserWithProfile(UserResponse):
    profile: Optional["UserProfileResponse"] = None

# User Profile Schemas
class UserProfileBase(BaseModel):
    date_of_birth: Optional[datetime] = None
    target_band_score: Optional[float] = Field(None, ge=0, le=9, description="Target IELTS band score (0-9)")
    preparation_level: Optional[str] = Field(None, description="Beginner, Intermediate, Advanced")
    preferred_test_type: Optional[str] = Field(None, description="academic or general_training")

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Authentication Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)

class PasswordReset(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
