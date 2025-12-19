from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.question import (
    WritingTaskCreate,
    WritingTaskUpdate,
    WritingTaskResponse
)
from app.models import User, WritingTask, TestSection
from app.core.security import get_current_user, get_current_admin_user

router = APIRouter()

@router.post("/tasks", response_model=WritingTaskResponse, status_code=status.HTTP_201_CREATED)
def create_writing_task(
    task_data: WritingTaskCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a writing task (Admin only)
    """
    # Verify section exists
    section = db.query(TestSection).filter(
        TestSection.id == task_data.section_id,
        TestSection.section_type == "writing"
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing section not found"
        )
    
    task = WritingTask(**task_data.model_dump())
    
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return task

@router.get("/tasks", response_model=List[WritingTaskResponse])
def get_writing_tasks(
    section_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all writing tasks for a section
    """
    tasks = db.query(WritingTask).filter(
        WritingTask.section_id == section_id
    ).order_by(WritingTask.task_number).offset(skip).limit(limit).all()
    
    return tasks

@router.get("/tasks/{task_id}", response_model=WritingTaskResponse)
def get_writing_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific writing task
    """
    task = db.query(WritingTask).filter(WritingTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing task not found"
        )
    
    return task

@router.put("/tasks/{task_id}", response_model=WritingTaskResponse)
def update_writing_task(
    task_id: int,
    task_update: WritingTaskUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a writing task (Admin only)
    """
    task = db.query(WritingTask).filter(WritingTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing task not found"
        )
    
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    db.commit()
    db.refresh(task)
    
    return task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_writing_task(
    task_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a writing task (Admin only)
    """
    task = db.query(WritingTask).filter(WritingTask.id == task_id).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing task not found"
        )
    
    db.delete(task)
    db.commit()
    
    return None
