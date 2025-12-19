from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.schemas.question import (
    ListeningQuestionCreate,
    ListeningQuestionUpdate,
    ListeningQuestionResponse,
    ListeningQuestionWithAnswer,
    ListeningQuestionWithAnswerCreate,
    ListeningPartCreate,
    ListeningPartResponse,
    ListeningPartUpdate
)
from app.models import User, ListeningQuestion, ListeningAnswer, TestSection, ListeningPart
from app.core.security import get_current_user, get_current_admin_user

router = APIRouter()

# --- Listening Parts ---

@router.post("/parts", response_model=ListeningPartResponse, status_code=status.HTTP_201_CREATED)
def create_listening_part(
    part_data: ListeningPartCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Create a listening part (audio + transcript)"""
    section = db.query(TestSection).filter(
        TestSection.id == part_data.section_id,
        TestSection.section_type == "listening"
    ).first()
    
    if not section:
        raise HTTPException(status_code=404, detail="Listening section not found")
        
    part = ListeningPart(**part_data.model_dump())
    db.add(part)
    db.commit()
    db.refresh(part)
    return part

@router.get("/parts", response_model=List[ListeningPartResponse])
def get_listening_parts(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all parts for a section"""
    parts = db.query(ListeningPart).filter(
        ListeningPart.section_id == section_id
    ).order_by(ListeningPart.part_number).all()
    return parts

@router.delete("/parts/{part_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listening_part(
    part_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a listening part and its questions"""
    part = db.query(ListeningPart).filter(ListeningPart.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Part not found")
        
    db.delete(part)
    db.commit()
    return None

# --- Listening Questions ---

@router.post("/questions", response_model=ListeningQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_listening_question(
    question_data: ListeningQuestionWithAnswerCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a listening question with answer (Admin only)
    """
    # Verify section exists
    section = db.query(TestSection).filter(
        TestSection.id == question_data.question.section_id,
        TestSection.section_type == "listening"
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Listening section not found"
        )
        
    # Verify part exists
    part = db.query(ListeningPart).filter(ListeningPart.id == question_data.question.part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Listening part not found")
    
    # Create question
    question = ListeningQuestion(
        **question_data.question.model_dump(exclude={'options'}),
        options=[opt.model_dump() for opt in question_data.question.options] if question_data.question.options else None
    )
    
    db.add(question)
    db.flush()
    
    # Create answer
    answer = ListeningAnswer(
        question_id=question.id,
        **question_data.answer.model_dump()
    )
    
    db.add(answer)
    db.commit()
    db.refresh(question)
    
    return question

@router.get("/questions", response_model=List[ListeningQuestionResponse])
def get_listening_questions(
    section_id: int,
    part_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all listening questions for a section, optionally filtered by part
    """
    query = db.query(ListeningQuestion).filter(ListeningQuestion.section_id == section_id)
    
    if part_id:
        query = query.filter(ListeningQuestion.part_id == part_id)
        
    questions = query.order_by(ListeningQuestion.order).offset(skip).limit(limit).all()
    
    return questions

@router.get("/questions/{question_id}", response_model=ListeningQuestionWithAnswer)
def get_listening_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific listening question with answer (answer only visible to admin/teacher)
    """
    question = db.query(ListeningQuestion).filter(
        ListeningQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question

@router.put("/questions/{question_id}", response_model=ListeningQuestionResponse)
def update_listening_question(
    question_id: int,
    question_update: ListeningQuestionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a listening question (Admin only)
    """
    question = db.query(ListeningQuestion).filter(
        ListeningQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    update_data = question_update.model_dump(exclude_unset=True, exclude={'options'})
    for field, value in update_data.items():
        setattr(question, field, value)
    
    # Update options if provided
    if question_update.options is not None:
        question.options = [opt.model_dump() for opt in question_update.options]
    
    db.commit()
    db.refresh(question)
    
    return question

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_listening_question(
    question_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a listening question (Admin only)
    """
    question = db.query(ListeningQuestion).filter(
        ListeningQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    db.delete(question)
    db.commit()
    
    return None
