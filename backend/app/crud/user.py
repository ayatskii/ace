from typing import Optional
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models import User, UserProfile
from app.schemas.user import UserCreate, UserUpdate, UserProfileCreate, UserProfileUpdate
from app.core.security import get_password_hash, verify_password


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User"""
    
    def get_by_email(self, db: Session, *, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """Create user with hashed password"""
        db_obj = User(
            email=obj_in.email,
            full_name=obj_in.full_name,
            phone=obj_in.phone,
            role=obj_in.role,
            password_hash=get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def authenticate(self, db: Session, *, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    def update_password(self, db: Session, *, db_obj: User, new_password: str) -> User:
        """Update user password"""
        db_obj.password_hash = get_password_hash(new_password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_role(self, db: Session, *, role: str, skip: int = 0, limit: int = 100):
        """Get users by role"""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()


class CRUDUserProfile(CRUDBase[UserProfile, UserProfileCreate, UserProfileUpdate]):
    """CRUD operations for UserProfile"""
    
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[UserProfile]:
        """Get profile by user ID"""
        return db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
    
    def create_for_user(self, db: Session, *, obj_in: UserProfileCreate, user_id: int) -> UserProfile:
        """Create profile for a specific user"""
        db_obj = UserProfile(
            user_id=user_id,
            **obj_in.model_dump()
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


# Create instances
user = CRUDUser(User)
user_profile = CRUDUserProfile(UserProfile)
