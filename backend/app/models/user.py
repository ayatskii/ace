from sqlalchemy import Column, Integer, String, Boolean, Enum, DateTime,  ForeignKey, Float
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime, timezone
import enum

class UserRole(str, enum.Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT)
    phone = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    test_attempts = relationship("TestAttempt", back_populates="user")
    created_tests = relationship("TestTemplate", back_populates="creator")

class UserProfile(Base):
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    date_of_birth = Column(DateTime, nullable=True)
    target_band_score = Column(Float, nullable=True)
    preferred_test_type = Column(String, nullable=True)
    
    user = relationship("User", back_populates="profile")