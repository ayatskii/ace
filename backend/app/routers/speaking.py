from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.question import (
    SpeakingTaskCreate,
    SpeakingTaskUpdate,
    SpeakingTaskResponse
)
from app.models import User, SpeakingTask, TestSection
from app.core.security import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/tasks", response_model=SpeakingTaskResponse, status_code=status.HTTP_201_CREATED)
def create_speaking_task(
    task_data: SpeakingTaskCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a speaking task (Admin only)
    """
    # Verify section exists
    section = db.query(TestSection).filter(
        TestSection.id == task_data.section_id,
        TestSection.section_type == "speaking"
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaking section not found"
        )
    
    task = SpeakingTask(**task_data.model_dump())
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task

@router.get("/tasks", response_model=List[SpeakingTaskResponse])
def get_speaking_tasks(
    section_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all speaking tasks for a section
    """
    tasks = db.query(SpeakingTask).filter(
        SpeakingTask.section_id == section_id
    ).order_by(SpeakingTask.order).offset(skip).limit(limit).all()
    
    return tasks

@router.get("/tasks/{task_id}", response_model=SpeakingTaskResponse)
def get_speaking_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific speaking task
    """
    task = db.query(SpeakingTask).filter(SpeakingTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaking task not found"
        )
    
    return task

@router.put("/tasks/{task_id}", response_model=SpeakingTaskResponse)
def update_speaking_task(
    task_id: int,
    task_update: SpeakingTaskUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a speaking task (Admin only)
    """
    task = db.query(SpeakingTask).filter(SpeakingTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaking task not found"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_speaking_task(
    task_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a speaking task (Admin only)
    """
    task = db.query(SpeakingTask).filter(SpeakingTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaking task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return None
