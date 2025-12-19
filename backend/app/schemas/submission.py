from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Listening Submission Schemas
class ListeningSubmissionCreate(BaseModel):
    test_attempt_id: int
    question_id: int
    user_answer: str

class ListeningSubmissionUpdate(BaseModel):
    user_answer: Optional[str] = None

class ListeningSubmissionResponse(BaseModel):
    id: int
    test_attempt_id: int
    question_id: int
    user_answer: str
    is_correct: bool
    submitted_at: datetime
    
    class Config:
        from_attributes = True

# Reading Submission Schemas
class ReadingSubmissionCreate(BaseModel):
    test_attempt_id: int
    question_id: int
    user_answer: str

class ReadingSubmissionUpdate(BaseModel):
    user_answer: Optional[str] = None

class ReadingSubmissionResponse(BaseModel):
    id: int
    test_attempt_id: int
    question_id: int
    user_answer: str
    is_correct: bool
    submitted_at: datetime
    
    class Config:
        from_attributes = True

# Writing Submission Schemas
class WritingSubmissionCreate(BaseModel):
    test_attempt_id: int
    task_id: int
    response_text: str

class WritingSubmissionUpdate(BaseModel):
    response_text: Optional[str] = None
    status: Optional[str] = Field(None, description="pending, under_review, graded")
    assigned_teacher_id: Optional[int] = None

class WritingSubmissionResponse(BaseModel):
    id: int
    test_attempt_id: int
    task_id: int
    response_text: str
    word_count: int
    status: str
    submitted_at: datetime
    assigned_teacher_id: Optional[int]
    graded_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class WritingSubmissionWithGrade(WritingSubmissionResponse):
    grade: Optional["WritingGradeResponse"] = None

# Speaking Submission Schemas
class SpeakingSubmissionCreate(BaseModel):
    test_attempt_id: int
    task_id: int
    audio_url: str
    duration_seconds: int = Field(..., gt=0)

class SpeakingSubmissionUpdate(BaseModel):
    audio_url: Optional[str] = None
    duration_seconds: Optional[int] = Field(None, gt=0)
    status: Optional[str] = Field(None, description="pending, under_review, graded")
    assigned_teacher_id: Optional[int] = None

class SpeakingSubmissionResponse(BaseModel):
    id: int
    test_attempt_id: int
    task_id: int
    audio_url: str
    duration_seconds: int
    status: str
    submitted_at: datetime
    assigned_teacher_id: Optional[int]
    graded_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SpeakingSubmissionWithGrade(SpeakingSubmissionResponse):
    grade: Optional["SpeakingGradeResponse"] = None

# Batch Submission Schemas
class AnswerItem(BaseModel):
    question_id: int
    user_answer: str

class BatchListeningSubmission(BaseModel):
    test_attempt_id: int
    submissions: List[AnswerItem]

class BatchReadingSubmission(BaseModel):
    test_attempt_id: int
    submissions: List[AnswerItem]

class BatchSubmissionResponse(BaseModel):
    total: int
    correct: int
    incorrect: int
    submissions: List[ListeningSubmissionResponse] | List[ReadingSubmissionResponse]

# Import after class definitions to avoid circular imports
# These must be available at runtime for Pydantic to resolve forward references
from app.schemas.grade import (
    WritingGradeResponse,
    SpeakingGradeResponse
)