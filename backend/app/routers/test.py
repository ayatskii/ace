from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import os
import shutil

from app.database import get_db
from app.schemas.test import (
    TestTemplateCreate, 
    TestTemplateResponse, 
    TestTemplateUpdate, 
    TestTemplateWithSections,
    TestSectionCreate, 
    TestSectionResponse,
    TestSectionUpdate,
    TestAttemptCreate, 
    TestAttemptResponse, 
    TestAttemptResponse, 
    TestAttemptWithDetails,
    TestStructureResponse,
    TestSubmission
)
from app.models import User, TestTemplate, TestSection, TestAttempt
from app.core.security import get_current_user, get_current_admin_user
from app.services.question_grading import grade_question
import json

router = APIRouter()

# ==================== Test Template Endpoints ====================

@router.post("/templates", response_model=TestTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_test_template(
    test_data: TestTemplateCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a new test template (Admin only)
    """
    test_template = TestTemplate(
        **test_data.model_dump(),
        created_by=current_user.id
    )
    
    db.add(test_template)
    db.commit()
    db.refresh(test_template)
    
    # Auto-create standard sections
    sections = [
        TestSection(
            test_template_id=test_template.id,
            section_type="listening",
            order=1,
            total_questions=40,
            duration_minutes=30
        ),
        TestSection(
            test_template_id=test_template.id,
            section_type="reading",
            order=2,
            total_questions=40,
            duration_minutes=60
        ),
        TestSection(
            test_template_id=test_template.id,
            section_type="writing",
            order=3,
            total_questions=2,
            duration_minutes=60
        ),
        TestSection(
            test_template_id=test_template.id,
            section_type="speaking",
            order=4,
            total_questions=3,
            duration_minutes=14
        )
    ]
    
    db.add_all(sections)
    db.commit()
    db.refresh(test_template)
    
    return test_template

@router.get("/templates", response_model=List[TestTemplateResponse])
def get_test_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    test_type: Optional[str] = Query(None, description="academic or general_training"),
    is_published: Optional[bool] = Query(None),
    difficulty_level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all test templates
    
    Students can only see published tests.
    Teachers and admins can see all tests.
    """
    query = db.query(TestTemplate)
    
    # Students can only see published tests
    if current_user.role == "student":
        query = query.filter(TestTemplate.is_published == True)
    
    if test_type:
        query = query.filter(TestTemplate.test_type == test_type)
    
    if is_published is not None:
        query = query.filter(TestTemplate.is_published == is_published)
    
    if difficulty_level:
        query = query.filter(TestTemplate.difficulty_level == difficulty_level)
    
    tests = query.order_by(TestTemplate.created_at.desc()).offset(skip).limit(limit).all()
    return tests

@router.get("/templates/{test_id}", response_model=TestTemplateWithSections)
def get_test_template(
    test_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get test template by ID with all sections
    """
    test = db.query(TestTemplate).filter(TestTemplate.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test template not found"
        )
    
    # Students can only see published tests
    if current_user.role == "student" and not test.is_published:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Test not available"
        )
    
    return test

@router.put("/templates/{test_id}", response_model=TestTemplateResponse)
def update_test_template(
    test_id: int,
    test_update: TestTemplateUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update test template (Admin only)
    """
    test = db.query(TestTemplate).filter(TestTemplate.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test template not found"
        )
    
    update_data = test_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(test, field, value)
    
    db.commit()
    db.refresh(test)
    
    return test

@router.delete("/templates/{test_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_template(
    test_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete test template (Admin only)
    
    Warning: This will cascade delete all sections and questions
    """
    test = db.query(TestTemplate).filter(TestTemplate.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test template not found"
        )
    
    # Check for related test attempts
    attempt_count = db.query(TestAttempt).filter(TestAttempt.test_template_id == test_id).count()
    if attempt_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete test: {attempt_count} student attempt(s) exist. Delete attempts first or archive the test."
        )
    
    db.delete(test)
    db.commit()
    
    return None

@router.post("/templates/{test_id}/publish", response_model=TestTemplateResponse)
def publish_test_template(
    test_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Publish a test template (Admin only)
    """
    test = db.query(TestTemplate).filter(TestTemplate.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test template not found"
        )
    
    test.is_published = True
    db.commit()
    db.refresh(test)
    
    return test

@router.post("/templates/{test_id}/unpublish", response_model=TestTemplateResponse)
def unpublish_test_template(
    test_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Unpublish a test template (Admin only)
    """
    test = db.query(TestTemplate).filter(TestTemplate.id == test_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test template not found"
        )
    
    test.is_published = False
    db.commit()
    db.refresh(test)
    
    return test

# ==================== Test Section Endpoints ====================

@router.post("/sections", response_model=TestSectionResponse, status_code=status.HTTP_201_CREATED)
def create_test_section(
    section_data: TestSectionCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Create a test section (Admin only)
    """
    # Verify test template exists
    test = db.query(TestTemplate).filter(TestTemplate.id == section_data.test_template_id).first()
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test template not found"
        )
    
    section = TestSection(**section_data.model_dump())
    
    db.add(section)
    db.commit()
    db.refresh(section)
    
    return section

@router.get("/sections/{section_id}", response_model=TestSectionResponse)
def get_test_section(
    section_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific test section
    """
    section = db.query(TestSection).filter(TestSection.id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    return section

@router.put("/sections/{section_id}", response_model=TestSectionResponse)
def update_test_section(
    section_id: int,
    section_update: TestSectionUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Update a test section (Admin only)
    """
    section = db.query(TestSection).filter(TestSection.id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    update_data = section_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(section, field, value)
    
    db.commit()
    db.refresh(section)
    
    return section

@router.delete("/sections/{section_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_section(
    section_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a test section (Admin only)
    """
    section = db.query(TestSection).filter(TestSection.id == section_id).first()
    if not section:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Section not found"
        )
    
    db.delete(section)
    db.commit()
    
    return None

# ==================== Test Attempt Endpoints ====================

@router.post("/attempts", response_model=TestAttemptResponse, status_code=status.HTTP_201_CREATED)
def start_test_attempt(
    attempt_data: TestAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new test attempt
    """
    # Check if test exists and is published
    test = db.query(TestTemplate).filter(
        TestTemplate.id == attempt_data.test_template_id,
        TestTemplate.is_published == True
    ).first()
    
    if not test:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found or not available"
        )
    
    # Check for existing attempt
    existing_attempt = db.query(TestAttempt).filter(
        TestAttempt.user_id == current_user.id,
        TestAttempt.test_template_id == attempt_data.test_template_id
    ).first()

    if existing_attempt:
        if existing_attempt.status == "in_progress":
            return existing_attempt
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already completed this test"
            )
    
    # Create test attempt
    attempt = TestAttempt(
        user_id=current_user.id,
        test_template_id=attempt_data.test_template_id,
        status="in_progress"
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt

@router.get("/attempts/me", response_model=List[TestAttemptResponse])
def get_my_test_attempts(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user's test attempts
    """
    from sqlalchemy.orm import joinedload
    
    query = db.query(TestAttempt).filter(TestAttempt.user_id == current_user.id)
    
    if status:
        query = query.filter(TestAttempt.status == status)
    
    attempts = query.options(
        joinedload(TestAttempt.test_template),
        joinedload(TestAttempt.result)
    ).order_by(TestAttempt.created_at.desc()).offset(skip).limit(limit).all()
            
    return attempts

@router.get("/attempts/{attempt_id}", response_model=TestAttemptWithDetails)
def get_test_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get test attempt by ID with details
    """
    attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test attempt not found"
        )
    
    # Check access permissions
    if attempt.user_id != current_user.id and current_user.role not in ["teacher", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this test attempt"
        )
    
    # Populate test structure
    test_template = attempt.test_template
    structure = {
        "listening_parts": [],
        "listening_questions": [],
        "reading_passages": [],
        "reading_questions": [],
        "writing_tasks": [],
        "speaking_tasks": []
    }
    
    for section in test_template.sections:
        if section.section_type == "listening":
            structure["listening_parts"].extend(section.listening_parts)
            structure["listening_questions"].extend(section.listening_questions)
        elif section.section_type == "reading":
            structure["reading_passages"].extend(section.reading_passages)
            # Questions are linked to passages, but we might want them flat list too or nested
            # For now, let's collect them from passages
            for passage in section.reading_passages:
                structure["reading_questions"].extend(passage.questions)
        elif section.section_type == "writing":
            structure["writing_tasks"].extend(section.writing_tasks)
        elif section.section_type == "speaking":
            structure["speaking_tasks"].extend(section.speaking_tasks)
            
    # Create response with structure
    response = TestAttemptWithDetails.model_validate(attempt)
    response.test_structure = TestStructureResponse(**structure)
    
    return response

@router.put("/attempts/{attempt_id}/submit", response_model=TestAttemptResponse)
def submit_test_attempt(
    attempt_id: int,
    submission_data: TestSubmission = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a test attempt
    
    This marks the test as submitted and records the end time.
    It also saves any writing answers provided in the body.
    """
    from app.models import WritingSubmission
    
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test attempt not found"
        )
    
    if attempt.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test already submitted"
        )
    
    # Save writing answers if provided
    if submission_data:
        # Process Writing Answers
        from app.models import WritingTask
        
        # Get all writing tasks for this test
        writing_tasks = db.query(WritingTask).join(TestSection).filter(
            TestSection.test_template_id == attempt.test_template_id,
            TestSection.section_type == "writing"
        ).all()
        
        # Create submissions for all writing tasks (even if empty)
        for task in writing_tasks:
            # Check if submission already exists
            existing_sub = db.query(WritingSubmission).filter(
                WritingSubmission.test_attempt_id == attempt_id,
                WritingSubmission.task_id == task.id
            ).first()
            
            # Find the answer for this task (if provided)
            task_answer = None
            if submission_data.writing_answers:
                for answer in submission_data.writing_answers:
                    if answer.task_id == task.id:
                        task_answer = answer
                        break
            
            response_text = task_answer.response_text if task_answer else ""
            word_count = len(response_text.split()) if response_text else 0
            
            if existing_sub:
                existing_sub.response_text = response_text
                existing_sub.word_count = word_count
                existing_sub.submitted_at = datetime.now(timezone.utc)
            else:
                new_sub = WritingSubmission(
                    test_attempt_id=attempt_id,
                    task_id=task.id,
                    response_text=response_text,
                    word_count=word_count,
                    status="pending",
                    assigned_teacher_id=None
                )
                db.add(new_sub)
        
        # Process Listening Answers
        if submission_data.listening_answers:
            from app.models import ListeningSubmission, ListeningQuestion
            for answer in submission_data.listening_answers:
                # Get question to check correctness
                question = db.query(ListeningQuestion).get(answer.question_id)
                is_correct = False
                
                if question:
                    # Try grading with new service (for complex types)
                    if question.answer_data is not None:
                        user_val = answer.user_answer
                        try:
                            user_val = json.loads(answer.user_answer)
                        except:
                            pass
                            
                        grading_result = grade_question(
                            question_type=question.question_type,
                            user_answer=user_val,
                            answer_data=question.answer_data,
                            type_specific_data=question.type_specific_data
                        )
                        is_correct = grading_result["is_correct"]
                    
                    # Fallback to legacy logic if no answer_data or if we want to double check (though answer_data should take precedence)
                    elif question.answers:
                        # Check against all possible correct answers
                        for correct_ans in question.answers:
                            user_ans = answer.user_answer.strip()
                            correct_ans_text = correct_ans.correct_answer.strip()
                            
                            # Respect case sensitivity setting
                            if correct_ans.case_sensitive:
                                if user_ans == correct_ans_text:
                                    is_correct = True
                                    break
                            else:
                                if user_ans.lower() == correct_ans_text.lower():
                                    is_correct = True
                                    break
                            
                            # Check alternative answers if any
                            if correct_ans.alternative_answers:
                                for alt in correct_ans.alternative_answers:
                                    alt_text = alt.strip()
                                    if correct_ans.case_sensitive:
                                        if user_ans == alt_text:
                                            is_correct = True
                                            break
                                    else:
                                        if user_ans.lower() == alt_text.lower():
                                            is_correct = True
                                            break
                            if is_correct: break
                
                existing_sub = db.query(ListeningSubmission).filter(
                    ListeningSubmission.test_attempt_id == attempt_id,
                    ListeningSubmission.question_id == answer.question_id
                ).first()
                
                if existing_sub:
                    existing_sub.user_answer = answer.user_answer
                    existing_sub.is_correct = is_correct
                    existing_sub.submitted_at = datetime.now(timezone.utc)
                else:
                    new_sub = ListeningSubmission(
                        test_attempt_id=attempt_id,
                        question_id=answer.question_id,
                        user_answer=answer.user_answer,
                        is_correct=is_correct
                    )
                    db.add(new_sub)

        # Process Reading Answers
        if submission_data.reading_answers:
            from app.models import ReadingSubmission, ReadingQuestion
            for answer in submission_data.reading_answers:
                # Get question to check correctness
                question = db.query(ReadingQuestion).get(answer.question_id)
                is_correct = False
                
                if question:
                    # Try grading with new service (for complex types)
                    if question.answer_data is not None:
                        user_val = answer.user_answer
                        try:
                            user_val = json.loads(answer.user_answer)
                        except:
                            pass
                            
                        grading_result = grade_question(
                            question_type=question.question_type,
                            user_answer=user_val,
                            answer_data=question.answer_data,
                            type_specific_data=question.type_specific_data
                        )
                        is_correct = grading_result["is_correct"]
                    
                    # Fallback to legacy logic
                    elif question.answers:
                        for correct_ans in question.answers:
                            user_ans = answer.user_answer.strip()
                            correct_ans_text = correct_ans.correct_answer.strip()
                            
                            # Respect case sensitivity setting
                            if correct_ans.case_sensitive:
                                if user_ans == correct_ans_text:
                                    is_correct = True
                                    break
                            else:
                                if user_ans.lower() == correct_ans_text.lower():
                                    is_correct = True
                                    break
                            
                            # Check alternative answers if any
                            if correct_ans.alternative_answers:
                                for alt in correct_ans.alternative_answers:
                                    alt_text = alt.strip()
                                    if correct_ans.case_sensitive:
                                        if user_ans == alt_text:
                                            is_correct = True
                                            break
                                    else:
                                        if user_ans.lower() == alt_text.lower():
                                            is_correct = True
                                            break
                            if is_correct: break
                
                existing_sub = db.query(ReadingSubmission).filter(
                    ReadingSubmission.test_attempt_id == attempt_id,
                    ReadingSubmission.question_id == answer.question_id
                ).first()
                
                if existing_sub:
                    existing_sub.user_answer = answer.user_answer
                    existing_sub.is_correct = is_correct
                    existing_sub.submitted_at = datetime.now(timezone.utc)
                else:
                    new_sub = ReadingSubmission(
                        test_attempt_id=attempt_id,
                        question_id=answer.question_id,
                        user_answer=answer.user_answer,
                        is_correct=is_correct
                    )
                    db.add(new_sub)
    
    attempt.status = "submitted"
    attempt.end_time = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(attempt)
    
    # Calculate initial results (Listening & Reading)
    try:
        calculate_initial_results(attempt.id, db)
    except Exception as e:
        print(f"Error calculating results: {e}")
    
    return attempt

def calculate_initial_results(attempt_id: int, db: Session):
    """
    Calculate scores for auto-graded sections (Listening & Reading)
    and create the initial TestResult record.
    
    Scores are calculated based on the sum of marks for correctly answered questions.
    """
    from app.models import ListeningSubmission, ReadingSubmission, TestResult, ListeningQuestion, ReadingQuestion
    from sqlalchemy import func
    
    # Calculate Listening Score - sum of marks for correct answers
    listening_score_result = db.query(func.coalesce(func.sum(ListeningQuestion.marks), 0)).join(
        ListeningSubmission,
        ListeningSubmission.question_id == ListeningQuestion.id
    ).filter(
        ListeningSubmission.test_attempt_id == attempt_id,
        ListeningSubmission.is_correct == True
    ).scalar()
    listening_correct = int(listening_score_result or 0)
    
    # Get total possible listening marks
    listening_total = db.query(func.coalesce(func.sum(ListeningQuestion.marks), 40)).join(
        ListeningSubmission,
        ListeningSubmission.question_id == ListeningQuestion.id
    ).filter(
        ListeningSubmission.test_attempt_id == attempt_id
    ).scalar()
    listening_total = int(listening_total or 40)
    
    # Simple band score mapping (approximate)
    listening_score = min(9.0, round((listening_correct / max(listening_total, 1)) * 9 * 2) / 2) if listening_correct > 0 else 0.0
    
    # Calculate Reading Score - sum of marks for correct answers
    reading_score_result = db.query(func.coalesce(func.sum(ReadingQuestion.marks), 0)).join(
        ReadingSubmission,
        ReadingSubmission.question_id == ReadingQuestion.id
    ).filter(
        ReadingSubmission.test_attempt_id == attempt_id,
        ReadingSubmission.is_correct == True
    ).scalar()
    reading_correct = int(reading_score_result or 0)
    
    # Get total possible reading marks
    reading_total = db.query(func.coalesce(func.sum(ReadingQuestion.marks), 40)).join(
        ReadingSubmission,
        ReadingSubmission.question_id == ReadingQuestion.id
    ).filter(
        ReadingSubmission.test_attempt_id == attempt_id
    ).scalar()
    reading_total = int(reading_total or 40)
    
    reading_score = min(9.0, round((reading_correct / max(reading_total, 1)) * 9 * 2) / 2) if reading_correct > 0 else 0.0
    
    # Create or Update TestResult
    result = db.query(TestResult).filter(TestResult.test_attempt_id == attempt_id).first()
    
    if not result:
        result = TestResult(
            test_attempt_id=attempt_id,
            listening_score=listening_score,
            reading_score=reading_score,
            writing_score=None, # Pending grading
            speaking_score=None, # Pending grading
            overall_band_score=0.0 # Will be calculated when all components are ready
        )
        db.add(result)
    else:
        result.listening_score = listening_score
        result.reading_score = reading_score
        
    db.commit()


@router.delete("/attempts/{attempt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a test attempt
    
    Users can only delete their own attempts if in_progress
    Admins can delete any attempt
    """
    attempt = db.query(TestAttempt).filter(TestAttempt.id == attempt_id).first()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test attempt not found"
        )
    
    # Check permissions
    if current_user.role != "admin":
        if attempt.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this attempt"
            )
        if attempt.status != "in_progress":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete submitted test"
            )
    
    db.delete(attempt)
    db.commit()
    
    return None

@router.post("/attempts/{attempt_id}/speaking/{task_id}/upload", status_code=status.HTTP_200_OK)
async def upload_speaking_audio(
    attempt_id: int,
    task_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload audio recording for a speaking task
    """
    attempt = db.query(TestAttempt).filter(
        TestAttempt.id == attempt_id,
        TestAttempt.user_id == current_user.id
    ).first()
    
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test attempt not found"
        )
        
    if attempt.status != "in_progress":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test is not in progress"
        )

    # Create uploads directory if it doesn't exist
    upload_dir = "uploads/speaking"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"{attempt_id}_{task_id}_{timestamp}.webm"
    file_path = os.path.join(upload_dir, filename)
    
    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Create or update SpeakingSubmission
    from app.models import SpeakingSubmission
    
    # Mock duration for now since we don't extract it from audio yet
    # In real app, use ffmpeg or similar to get duration
    duration = 0 
    
    existing_sub = db.query(SpeakingSubmission).filter(
        SpeakingSubmission.test_attempt_id == attempt_id,
        SpeakingSubmission.task_id == task_id
    ).first()
    
    # Construct URL (assuming static file serving is set up or will be)
    # For local dev, we might need a route to serve these
    audio_url = f"/uploads/speaking/{filename}"
    
    if existing_sub:
        existing_sub.audio_url = audio_url
        existing_sub.submitted_at = datetime.now(timezone.utc)
    else:
        new_sub = SpeakingSubmission(
            test_attempt_id=attempt_id,
            task_id=task_id,
            audio_url=audio_url,
            duration_seconds=duration, # Placeholder
            status="pending"
        )
        db.add(new_sub)
        
    db.commit()
    
    return {"filename": filename, "status": "uploaded", "audio_url": audio_url}
