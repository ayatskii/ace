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
    TestAttemptWithDetails,
    TestStructureResponse
)
from app.models import User, TestTemplate, TestSection, TestAttempt
from app.core.security import get_current_user, get_current_admin_user

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
    query = db.query(TestAttempt).filter(TestAttempt.user_id == current_user.id)
    
    if status:
        query = query.filter(TestAttempt.status == status)
    
    attempts = query.order_by(TestAttempt.created_at.desc()).offset(skip).limit(limit).all()
    
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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a test attempt
    
    This marks the test as submitted and records the end time
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
            detail="Test already submitted"
        )
    
    attempt.status = "submitted"
    attempt.end_time = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(attempt)
    
    return attempt

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
        
    # In a real app, we would save the URL/path to a SpeakingSubmission record here
    # For now, we just return success
    
    return {"filename": filename, "status": "uploaded"}
