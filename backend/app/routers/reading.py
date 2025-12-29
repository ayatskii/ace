from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.question import (
    ReadingPassageCreate,
    ReadingPassageUpdate,
    ReadingPassageResponse,
    ReadingPassageWithQuestions,
    ReadingQuestionCreate,
    ReadingQuestionUpdate,
    ReadingQuestionResponse,
    ReadingQuestionWithAnswerCreate
)
from app.models import User, ReadingPassage, ReadingQuestion, ReadingAnswer, TestSection
from app.core.security import get_current_user, get_current_admin_user

router = APIRouter()

# Reading Passage Endpoints
@router.post("/passages", response_model=ReadingPassageResponse, status_code=status.HTTP_201_CREATED)
def create_reading_passage(
    passage_data: ReadingPassageCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a reading passage (Admin only)
    """
    # Verify section exists
    section = db.query(TestSection).filter(
        TestSection.id == passage_data.section_id,
        TestSection.section_type == "reading"
    ).first()
    
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading section not found"
        )
    
    # Calculate word count
    word_count = len(passage_data.content.split())
    
    passage = ReadingPassage(
        **passage_data.model_dump(),
        word_count=word_count
    )
    
    db.add(passage)
    db.commit()
    db.refresh(passage)
    
    return passage

@router.get("/passages", response_model=List[ReadingPassageResponse])
def get_reading_passages(
    section_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all reading passages for a section
    """
    passages = db.query(ReadingPassage).filter(
        ReadingPassage.section_id == section_id
    ).order_by(ReadingPassage.order).offset(skip).limit(limit).all()
    
    return passages

@router.get("/passages/{passage_id}", response_model=ReadingPassageWithQuestions)
def get_reading_passage(
    passage_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific reading passage with questions
    """
    passage = db.query(ReadingPassage).filter(
        ReadingPassage.id == passage_id
    ).first()
    
    if not passage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passage not found"
        )
    
    return passage

@router.put("/passages/{passage_id}", response_model=ReadingPassageResponse)
def update_reading_passage(
    passage_id: int,
    passage_update: ReadingPassageUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a reading passage (Admin only)
    """
    passage = db.query(ReadingPassage).filter(
        ReadingPassage.id == passage_id
    ).first()
    
    if not passage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passage not found"
        )
    
    update_data = passage_update.model_dump(exclude_unset=True)
    
    # Recalculate word count if content changed
    if 'content' in update_data:
        update_data['word_count'] = len(update_data['content'].split())
    
    for field, value in update_data.items():
        setattr(passage, field, value)
    
    db.commit()
    db.refresh(passage)
    
    return passage

@router.delete("/passages/{passage_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reading_passage(
    passage_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a reading passage (Admin only)
    """
    passage = db.query(ReadingPassage).filter(
        ReadingPassage.id == passage_id
    ).first()
    
    if not passage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Passage not found"
        )
    
    db.delete(passage)
    db.commit()
    
    return None

# Reading Question Endpoints
@router.post("/questions", response_model=ReadingQuestionResponse, status_code=status.HTTP_201_CREATED)
def create_reading_question(
    question_data: ReadingQuestionWithAnswerCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a reading question with answer (Admin only)
    """
    # Verify passage exists
    passage = db.query(ReadingPassage).filter(
        ReadingPassage.id == question_data.question.passage_id
    ).first()
    
    if not passage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reading passage not found"
        )
    
    # Create question
    question = ReadingQuestion(
        **question_data.question.model_dump(exclude={'options'}),
        options=[opt.model_dump() for opt in question_data.question.options] if question_data.question.options else None
    )
    
    db.add(question)
    db.flush()
    
    # Create answer
    answer = ReadingAnswer(
        question_id=question.id,
        **question_data.answer.model_dump()
    )
    
    db.add(answer)
    db.commit()
    db.refresh(question)
    
    return question

@router.get("/questions/{question_id}", response_model=ReadingQuestionResponse)
def get_reading_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific reading question
    """
    question = db.query(ReadingQuestion).filter(
        ReadingQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    return question

@router.put("/questions/{question_id}", response_model=ReadingQuestionResponse)
def update_reading_question(
    question_id: int,
    question_update: ReadingQuestionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a reading question (Admin only)
    """
    question = db.query(ReadingQuestion).filter(
        ReadingQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    # Exclude passage_id and question_number to avoid unique constraint issues
    update_data = question_update.model_dump(exclude_unset=True, exclude={'options', 'passage_id', 'question_number'})
    for field, value in update_data.items():
        setattr(question, field, value)
    
    # Update options if provided
    if question_update.options is not None:
        question.options = [opt.model_dump() for opt in question_update.options]
    
    db.commit()
    db.refresh(question)
    
    return question

@router.delete("/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reading_question(
    question_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a reading question (Admin only)
    """
    question = db.query(ReadingQuestion).filter(
        ReadingQuestion.id == question_id
    ).first()
    
    if not question:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    db.delete(question)
    db.commit()
    
    return None
