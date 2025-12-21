from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Writing Grade Schemas
class WritingGradeCreate(BaseModel):
    task_achievement_score: float = Field(..., ge=0, le=9, description="Task Achievement/Response score (0-9)")
    coherence_cohesion_score: float = Field(..., ge=0, le=9, description="Coherence and Cohesion score (0-9)")
    lexical_resource_score: float = Field(..., ge=0, le=9, description="Lexical Resource score (0-9)")
    grammatical_range_score: float = Field(..., ge=0, le=9, description="Grammatical Range and Accuracy score (0-9)")
    feedback_text: Optional[str] = None

class WritingGradeUpdate(BaseModel):
    task_achievement_score: Optional[float] = Field(None, ge=0, le=9)
    coherence_cohesion_score: Optional[float] = Field(None, ge=0, le=9)
    lexical_resource_score: Optional[float] = Field(None, ge=0, le=9)
    grammatical_range_score: Optional[float] = Field(None, ge=0, le=9)
    feedback_text: Optional[str] = None

class WritingGradeResponse(BaseModel):
    id: int
    submission_id: int
    teacher_id: int
    task_achievement_score: float
    coherence_cohesion_score: float
    lexical_resource_score: float
    grammatical_range_score: float
    overall_band_score: float
    feedback_text: Optional[str]
    graded_at: datetime
    
    class Config:
        from_attributes = True

# Speaking Grade Schemas
class SpeakingGradeCreate(BaseModel):
    fluency_coherence_score: float = Field(..., ge=0, le=9, description="Fluency and Coherence score (0-9)")
    lexical_resource_score: float = Field(..., ge=0, le=9, description="Lexical Resource score (0-9)")
    grammatical_range_score: float = Field(..., ge=0, le=9, description="Grammatical Range and Accuracy score (0-9)")
    pronunciation_score: float = Field(..., ge=0, le=9, description="Pronunciation score (0-9)")
    feedback_text: Optional[str] = None

class SpeakingGradeUpdate(BaseModel):
    fluency_coherence_score: Optional[float] = Field(None, ge=0, le=9)
    lexical_resource_score: Optional[float] = Field(None, ge=0, le=9)
    grammatical_range_score: Optional[float] = Field(None, ge=0, le=9)
    pronunciation_score: Optional[float] = Field(None, ge=0, le=9)
    feedback_text: Optional[str] = None

class SpeakingGradeResponse(BaseModel):
    id: int
    submission_id: int
    teacher_id: int
    fluency_coherence_score: float
    lexical_resource_score: float
    grammatical_range_score: float
    pronunciation_score: float
    overall_band_score: float
    feedback_text: Optional[str]
    graded_at: datetime
    
    class Config:
        from_attributes = True

# Test Result Schemas
class TestResultResponse(BaseModel):
    id: int
    test_attempt_id: int
    listening_score: Optional[float]
    reading_score: Optional[float]
    writing_score: Optional[float]
    speaking_score: Optional[float]
    overall_band_score: float
    generated_at: datetime
    
    class Config:
        from_attributes = True

class TestResultDetailed(TestResultResponse):
    test_attempt: "TestAttemptResponse"

# Teacher Assignment Schemas
class TeacherAssignmentCreate(BaseModel):
    teacher_id: int
    submission_id: int
    submission_type: str = Field(..., description="writing or speaking")

class TeacherAssignmentUpdate(BaseModel):
    status: Optional[str] = Field(None, description="pending or completed")
    completed_at: Optional[datetime] = None

class TeacherAssignmentResponse(BaseModel):
    id: int
    teacher_id: int
    submission_id: int
    submission_type: str
    assigned_at: datetime
    status: str
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class TeacherWorkload(BaseModel):
    teacher_id: int
    teacher_name: str
    pending_writing: int
    pending_speaking: int
    completed_today: int
    total_pending: int
