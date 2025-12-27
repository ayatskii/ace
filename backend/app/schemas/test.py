from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List


# Test Template Schemas
class TestTemplateBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    test_type: str = Field(..., description="academic or general_training")
    difficulty_level: Optional[str] = Field(None, description="Easy, Medium, Hard")
    duration_minutes: int = Field(..., gt=0, description="Total test duration in minutes")

class TestTemplateCreate(TestTemplateBase):
    pass

class TestTemplateUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    test_type: Optional[str] = None
    difficulty_level: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, gt=0)
    is_published: Optional[bool] = None

class TestTemplateResponse(TestTemplateBase):
    id: int
    is_published: bool
    created_by: Optional[int] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class TestTemplateWithSections(TestTemplateResponse):
    sections: List["TestSectionResponse"] = []

# Test Section Schemas
class TestSectionBase(BaseModel):
    section_type: str = Field(..., description="listening, reading, writing, or speaking")
    order: int = Field(..., ge=1, description="Section order in the test")
    total_questions: int = Field(..., ge=0)
    duration_minutes: int = Field(..., gt=0)

class TestSectionCreate(TestSectionBase):
    test_template_id: int

class TestSectionUpdate(BaseModel):
    section_type: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    total_questions: Optional[int] = Field(None, ge=0)
    duration_minutes: Optional[int] = Field(None, gt=0)

class TestSectionResponse(TestSectionBase):
    id: int
    test_template_id: int
    
    model_config = ConfigDict(from_attributes=True)

# Test Result Schema
class TestResultResponse(BaseModel):
    id: int
    test_attempt_id: int
    listening_score: Optional[float]
    reading_score: Optional[float]
    writing_score: Optional[float]
    speaking_score: Optional[float]
    overall_band_score: float
    generated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# Test Attempt Schemas
class TestAttemptCreate(BaseModel):
    test_template_id: int

class TestAttemptUpdate(BaseModel):
    status: Optional[str] = Field(None, description="in_progress, submitted, graded")
    end_time: Optional[datetime] = None

class TestAttemptResponse(BaseModel):
    id: int
    user_id: int
    test_template_id: int
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    overall_band_score: Optional[float]
    created_at: datetime
    
    # Relationships
    test_template: Optional[TestTemplateResponse] = None
    result: Optional[TestResultResponse] = None
    
    model_config = ConfigDict(from_attributes=True)

# Import after class definitions to avoid circular imports
# These must be available at runtime for Pydantic to resolve forward references
from app.schemas.submission import (
    ListeningSubmissionResponse,
    ReadingSubmissionResponse,
    WritingSubmissionResponse,
    SpeakingSubmissionResponse
)
from app.schemas.question import (
    ListeningPartResponse,
    ListeningQuestionResponse,
    ReadingPassageResponse,
    ReadingQuestionResponse,
    WritingTaskResponse,
    SpeakingTaskResponse
)

class TestStructureResponse(BaseModel):
    listening_parts: List[ListeningPartResponse] = []
    listening_questions: List[ListeningQuestionResponse] = []
    reading_passages: List[ReadingPassageResponse] = []
    reading_questions: List[ReadingQuestionResponse] = []
    writing_tasks: List[WritingTaskResponse] = []
    speaking_tasks: List[SpeakingTaskResponse] = []

class TestAttemptWithDetails(TestAttemptResponse):
    test_template: TestTemplateWithSections
    test_structure: Optional[TestStructureResponse] = None
    listening_submissions: List["ListeningSubmissionResponse"] = []
    reading_submissions: List["ReadingSubmissionResponse"] = []
    writing_submissions: List["WritingSubmissionResponse"] = []
    speaking_submissions: List["SpeakingSubmissionResponse"] = []

class WritingAnswerItem(BaseModel):
    task_id: int
    response_text: str

class StandardAnswerItem(BaseModel):
    question_id: int
    user_answer: str

class TestSubmission(BaseModel):
    writing_answers: List[WritingAnswerItem] = []
    listening_answers: List[StandardAnswerItem] = []
    reading_answers: List[StandardAnswerItem] = []