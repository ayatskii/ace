"""
Admin router for managing admin-only operations.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, TestTemplate
from app.schemas import UserResponse, TestTemplateResponse
from app.core.security import get_current_admin_user

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get all users in the system. Admin only.
    """
    users = db.query(User).all()
    return users

@router.get("/tests", response_model=List[TestTemplateResponse])
async def get_all_tests(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get all tests in the system. Admin only.
    """
    tests = db.query(TestTemplate).all()
    return tests

@router.get("/stats")
def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get platform statistics for admin dashboard  
    """
    from app.schemas.stats import AdminStatsResponse
    from app.models import TestAttempt
    
    # Count users by role
    total_users = db.query(User).count()
    total_students = db.query(User).filter(User.role == "student").count()
    total_teachers = db.query(User).filter(User.role == "teacher").count()
    
    # Count tests
    total_tests = db.query(TestTemplate).count()
    active_tests = db.query(TestTemplate).filter(TestTemplate.is_published == True).count()
    
    # Count test attempts
    completed_attempts = db.query(TestAttempt).count()
    
    return AdminStatsResponse(
        total_users=total_users,
        total_students=total_students,
        total_teachers=total_teachers,
        total_tests=total_tests,
        active_tests=active_tests,
        completed_attempts=completed_attempts
    ).model_dump()

@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update a user's role. Admin only.
    """
    # Validate role
    if role not in ["student", "teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role. Must be: student, teacher, or admin"
        )
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-demotion
    if user_id == current_user.id and role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change your own admin role"
        )
    
    # Update role
    user.role = role
    db.commit()
    db.refresh(user)
    
    return user
