from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.database import get_db
from app.schemas.grade import (
    WritingGradeCreate,
    WritingGradeResponse,
    SpeakingGradeCreate,
    SpeakingGradeResponse,
    TeacherWorkload
)
from app.schemas.submission import (
    WritingSubmissionResponse,
    SpeakingSubmissionResponse
)
from app.models import (
    User,
    WritingSubmission,
    SpeakingSubmission,
    WritingGrade,
    SpeakingGrade,
    TestAttempt
)
from app.core.security import get_current_teacher_user

router = APIRouter()

# Helper function to calculate band score
def calculate_band_score(*scores: float) -> float:
    """Calculate average band score rounded to nearest 0.5"""
    avg = sum(scores) / len(scores)
    return round(avg * 2) / 2

# Writing Grading
@router.get("/writing/pending", response_model=List[WritingSubmissionResponse])
def get_pending_writing_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get pending writing submissions for grading (Teacher only)
    """
    from sqlalchemy.orm import joinedload
    
    submissions = db.query(WritingSubmission).options(
        joinedload(WritingSubmission.test_attempt).joinedload(TestAttempt.user)
    ).filter(
        WritingSubmission.status.in_(["pending", "under_review"])
    ).offset(skip).limit(limit).all()
    
    # Manually populate student info  
    result = []
    for sub in submissions:
        data = WritingSubmissionResponse.model_validate(sub).model_dump()
        if sub.test_attempt and sub.test_attempt.user:
            data['student_name'] = sub.test_attempt.user.full_name
            data['student_email'] = sub.test_attempt.user.email
        result.append(data)
    
    return result

@router.post("/writing/{submission_id}", response_model=WritingGradeResponse, status_code=status.HTTP_201_CREATED)
def grade_writing_submission(
    submission_id: int,
    grade_data: WritingGradeCreate,
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Grade a writing submission (Teacher only)
    """
    # Get submission
    submission = db.query(WritingSubmission).filter(
        WritingSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Writing submission not found"
        )
    
    # Check if already graded
    existing_grade = db.query(WritingGrade).filter(
        WritingGrade.submission_id == submission_id
    ).first()
    
    if existing_grade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission already graded"
        )
    
    # Calculate overall band score
    overall_score = calculate_band_score(
        grade_data.task_achievement_score,
        grade_data.coherence_cohesion_score,
        grade_data.lexical_resource_score,
        grade_data.grammatical_range_score
    )
    
    # Create grade
    grade = WritingGrade(
        submission_id=submission_id,
        teacher_id=current_user.id,
        task_achievement_score=grade_data.task_achievement_score,
        coherence_cohesion_score=grade_data.coherence_cohesion_score,
        lexical_resource_score=grade_data.lexical_resource_score,
        grammatical_range_score=grade_data.grammatical_range_score,
        overall_band_score=overall_score,
        feedback_text=grade_data.feedback_text
    )
    
    db.add(grade)
    
    # Update submission status
    submission.status = "graded"
    submission.graded_at = datetime.now(timezone.utc)
    submission.assigned_teacher_id = current_user.id
    
    db.commit()
    db.refresh(grade)
    
    # Update Test Result
    try:
        update_test_result(submission.test_attempt_id, db)
    except Exception as e:
        print(f"Error updating test result: {e}")
    
    return grade

# Speaking Grading
@router.get("/speaking/pending", response_model=List[SpeakingSubmissionResponse])
def get_pending_speaking_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get pending speaking submissions for grading (Teacher only)
    """
    from sqlalchemy.orm import joinedload
    
    submissions = db.query(SpeakingSubmission).options(
        joinedload(SpeakingSubmission.test_attempt).joinedload(TestAttempt.user)
    ).filter(
        SpeakingSubmission.status.in_(["pending", "under_review"])
    ).offset(skip).limit(limit).all()
    
     # Manually populate student info  
    result = []
    for sub in submissions:
        data = SpeakingSubmissionResponse.model_validate(sub).model_dump()
        if sub.test_attempt and sub.test_attempt.user:
            data['student_name'] = sub.test_attempt.user.full_name
            data['student_email'] = sub.test_attempt.user.email
        result.append(data)
    
    return result

@router.post("/speaking/{submission_id}", response_model=SpeakingGradeResponse, status_code=status.HTTP_201_CREATED)
def grade_speaking_submission(
    submission_id: int,
    grade_data: SpeakingGradeCreate,
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Grade a speaking submission (Teacher only)
    """
    # Get submission
    submission = db.query(SpeakingSubmission).filter(
        SpeakingSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Speaking submission not found"
        )
    
    # Check if already graded
    existing_grade = db.query(SpeakingGrade).filter(
        SpeakingGrade.submission_id == submission_id
    ).first()
    
    if existing_grade:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission already graded"
        )
    
    # Calculate overall band score
    overall_score = calculate_band_score(
        grade_data.fluency_coherence_score,
        grade_data.lexical_resource_score,
        grade_data.grammatical_range_score,
        grade_data.pronunciation_score
    )
    
    # Create grade
    grade = SpeakingGrade(
        submission_id=submission_id,
        teacher_id=current_user.id,
        fluency_coherence_score=grade_data.fluency_coherence_score,
        lexical_resource_score=grade_data.lexical_resource_score,
        grammatical_range_score=grade_data.grammatical_range_score,
        pronunciation_score=grade_data.pronunciation_score,
        overall_band_score=overall_score,
        feedback_text=grade_data.feedback_text
    )
    
    db.add(grade)
    
    # Update submission status
    submission.status = "graded"
    submission.graded_at = datetime.now(timezone.utc)
    submission.assigned_teacher_id = current_user.id
    
    db.commit()
    db.refresh(grade)
    
    # Update Test Result
    try:
        update_test_result(submission.test_attempt_id, db)
    except Exception as e:
        print(f"Error updating test result: {e}")
    
    return grade

@router.get("/workload", response_model=TeacherWorkload)
def get_teacher_workload(
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get teacher's current workload
    """
    pending_writing = db.query(WritingSubmission).filter(
        WritingSubmission.status.in_(["pending", "under_review"])
    ).count()
    
    pending_speaking = db.query(SpeakingSubmission).filter(
        SpeakingSubmission.status.in_(["pending", "under_review"])
    ).count()
    
    # Count completed today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    completed_today = (
        db.query(WritingGrade).filter(
            WritingGrade.teacher_id == current_user.id,
            WritingGrade.graded_at >= today_start
        ).count() +
        db.query(SpeakingGrade).filter(
            SpeakingGrade.teacher_id == current_user.id,
            SpeakingGrade.graded_at >= today_start
        ).count()
    )
    
    return {
        "teacher_id": current_user.id,
        "teacher_name": current_user.full_name,
        "pending_writing": pending_writing,
        "pending_speaking": pending_speaking,
        "completed_today": completed_today,
        "total_pending": pending_writing + pending_speaking
    }

@router.get("/queue")
def get_grading_queue(
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get pending submissions queue for teacher dashboard
    """
    from sqlalchemy import or_
    from app.schemas.stats import TeacherStatsResponse, RecentSubmissionResponse
    
    # Count pending submissions (assigned to this teacher OR unassigned)
    pending_writing = db.query(WritingSubmission).filter(
        or_(
            WritingSubmission.assigned_teacher_id == current_user.id,
            WritingSubmission.assigned_teacher_id == None
        ),
        WritingSubmission.status.in_(["pending", "under_review"])
    ).count()
    
    pending_speaking = db.query(SpeakingSubmission).filter(
        or_(
            SpeakingSubmission.assigned_teacher_id == current_user.id,
            SpeakingSubmission.assigned_teacher_id == None
        ),
        SpeakingSubmission.status.in_(["pending", "under_review"])
    ).count()
    
    # Get recent submissions (last 3)
    from sqlalchemy.orm import joinedload
    
    recent_writing = db.query(WritingSubmission).options(
        joinedload(WritingSubmission.test_attempt).joinedload(TestAttempt.user)
    ).filter(
        or_(
            WritingSubmission.assigned_teacher_id == current_user.id,
            WritingSubmission.assigned_teacher_id == None
        ),
        WritingSubmission.status.in_(["pending", "under_review"])
    ).order_by(WritingSubmission.submitted_at.desc()).limit(2).all()
    
    recent_speaking = db.query(SpeakingSubmission).options(
        joinedload(SpeakingSubmission.test_attempt).joinedload(TestAttempt.user)
    ).filter(
        or_(
            SpeakingSubmission.assigned_teacher_id == current_user.id,
            SpeakingSubmission.assigned_teacher_id == None
        ),
        SpeakingSubmission.status.in_(["pending", "under_review"])
    ).order_by(SpeakingSubmission.submitted_at.desc()).limit(1).all()
    
    # Format recent submissions
    recent_submissions = []
    
    for sub in recent_writing:
        test_attempt = sub.test_attempt  
        student_name = test_attempt.user.full_name if test_attempt and test_attempt.user else "Unknown"
        
        # Ensure submitted_at is timezone-aware
        submitted_at = sub.submitted_at
        if submitted_at.tzinfo is None:
            submitted_at = submitted_at.replace(tzinfo=timezone.utc)
        
        time_diff = datetime.now(timezone.utc) - submitted_at
        hours_ago = int(time_diff.total_seconds() / 3600)
        if hours_ago < 1:
            minutes_ago = int(time_diff.total_seconds() / 60)
            submitted_text = f"{minutes_ago} mins ago"
        else:
            submitted_text = f"{hours_ago} hours ago"
        
        recent_submissions.append({
            "id": sub.id,
            "student": student_name,
            "type": "Writing",
            "task": f"Task {sub.task_id}",
            "submitted": submitted_text
        })
    
    for sub in recent_speaking:
        test_attempt = sub.test_attempt
        student_name = test_attempt.user.full_name if test_attempt and test_attempt.user else "Unknown"
        
        # Ensure submitted_at is timezone-aware
        submitted_at = sub.submitted_at
        if submitted_at.tzinfo is None:
            submitted_at = submitted_at.replace(tzinfo=timezone.utc)
        
        time_diff = datetime.now(timezone.utc) - submitted_at
        hours_ago = int(time_diff.total_seconds() / 3600)
        if hours_ago < 1:
            minutes_ago = int(time_diff.total_seconds() / 60)
            submitted_text = f"{minutes_ago} mins ago"
        else:
            submitted_text = f"{hours_ago} hours ago"
        
        recent_submissions.append({
            "id": sub.id,
            "student": student_name,
            "type": "Speaking",
            "task": f"Task {sub.task_id}",
            "submitted": submitted_text
        })
    
    return {
        "pending_writing": pending_writing,
        "pending_speaking": pending_speaking,
        "recent_submissions": recent_submissions
    }


@router.get("/stats")
def get_grading_stats(
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get grading statistics for teacher dashboard
    """
    from app.schemas.stats import TeacherStatsResponse
    
    # Count graded today
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    graded_writing_today = db.query(WritingSubmission).filter(
        WritingSubmission.assigned_teacher_id == current_user.id,
        WritingSubmission.status == "graded",
        WritingSubmission.graded_at >= today_start
    ).count()
    
    graded_speaking_today = db.query(SpeakingSubmission).filter(
        SpeakingSubmission.assigned_teacher_id == current_user.id,
        SpeakingSubmission.status == "graded",
        SpeakingSubmission.graded_at >= today_start
    ).count()
    
    graded_today = graded_writing_today + graded_speaking_today
    
    # Average grading time (simplified)
    avg_grading_time = "15 min"
    
    return TeacherStatsResponse(
        pending_writing=0,  # Set by queue endpoint
        pending_speaking=0,  # Set by queue endpoint
        graded_today=graded_today,
        avg_grading_time=avg_grading_time
    ).model_dump()


@router.get("/history")
def get_grading_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_teacher_user),
    db: Session = Depends(get_db)
):
    """
    Get history of graded submissions by the current teacher
    """
    # Get graded writing submissions
    writing_grades = db.query(WritingGrade).filter(
        WritingGrade.teacher_id == current_user.id
    ).order_by(WritingGrade.graded_at.desc()).offset(skip).limit(limit).all()
    
    # Get graded speaking submissions
    speaking_grades = db.query(SpeakingGrade).filter(
        SpeakingGrade.teacher_id == current_user.id
    ).order_by(SpeakingGrade.graded_at.desc()).offset(skip).limit(limit).all()
    
    # Combine and sort (simplified approach, ideally we'd query a union or handle pagination better)
    # For now, we'll just return a mixed list sorted by date
    
    history = []
    
    for grade in writing_grades:
        submission = db.query(WritingSubmission).get(grade.submission_id)
        student_name = submission.test_attempt.user.full_name if submission and submission.test_attempt and submission.test_attempt.user else "Unknown"
        
        history.append({
            "id": grade.id,
            "submission_id": grade.submission_id,
            "student": student_name,
            "type": "Writing",
            "task": f"Task {submission.task_id}" if submission else "Unknown",
            "score": grade.overall_band_score,
            "graded_at": grade.graded_at,
            "feedback": grade.feedback_text
        })
        
    for grade in speaking_grades:
        submission = db.query(SpeakingSubmission).get(grade.submission_id)
        student_name = submission.test_attempt.user.full_name if submission and submission.test_attempt and submission.test_attempt.user else "Unknown"
        
        history.append({
            "id": grade.id,
            "submission_id": grade.submission_id,
            "student": student_name,
            "type": "Speaking",
            "task": f"Part {submission.task_id}" if submission else "Unknown",
            "score": grade.overall_band_score,
            "graded_at": grade.graded_at,
            "feedback": grade.feedback_text
        })
    
    # Sort by graded_at desc
    history.sort(key=lambda x: x["graded_at"], reverse=True)
    
    return history[:limit]

def update_test_result(attempt_id: int, db: Session):
    """
    Update TestResult with latest grades and calculate overall band score
    """
    from app.models import TestResult, WritingSubmission, SpeakingSubmission, WritingGrade, SpeakingGrade
    
    result = db.query(TestResult).filter(TestResult.test_attempt_id == attempt_id).first()
    
    if not result:
        # Should have been created at submission, but if not, create it
        result = TestResult(
            test_attempt_id=attempt_id,
            overall_band_score=0.0
        )
        db.add(result)
    
    # Get Writing Score
    writing_sub = db.query(WritingSubmission).filter(
        WritingSubmission.test_attempt_id == attempt_id,
        WritingSubmission.status == "graded"
    ).first() # Assuming one writing submission per test for now, or average if multiple
    
    if writing_sub:
        grade = db.query(WritingGrade).filter(WritingGrade.submission_id == writing_sub.id).first()
        if grade:
            result.writing_score = grade.overall_band_score
            
    # Get Speaking Score
    speaking_sub = db.query(SpeakingSubmission).filter(
        SpeakingSubmission.test_attempt_id == attempt_id,
        SpeakingSubmission.status == "graded"
    ).first()
    
    if speaking_sub:
        grade = db.query(SpeakingGrade).filter(SpeakingGrade.submission_id == speaking_sub.id).first()
        if grade:
            result.speaking_score = grade.overall_band_score
            
    # Calculate Overall Band Score
    scores = []
    if result.listening_score is not None: scores.append(result.listening_score)
    if result.reading_score is not None: scores.append(result.reading_score)
    if result.writing_score is not None: scores.append(result.writing_score)
    if result.speaking_score is not None: scores.append(result.speaking_score)
    
    if scores:
        avg = sum(scores) / len(scores)
        result.overall_band_score = round(avg * 2) / 2
        
        # Update attempt overall score too
        from app.models import TestAttempt
        attempt = db.query(TestAttempt).get(attempt_id)
        if attempt:
            attempt.overall_band_score = result.overall_band_score
            if len(scores) == 4: # All parts graded
                attempt.status = "graded"
    
    db.commit()
