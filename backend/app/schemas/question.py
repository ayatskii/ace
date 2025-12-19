from pydantic import BaseModel, Field
from typing import Optional, List

# Question Type Template Schemas
class QuestionTypeTemplateResponse(BaseModel):
    id: int
    name: str
    type_enum: str
    section_type: str
    description: Optional[str]
    instructions: Optional[str]
    is_active: bool
    
    class Config:
        from_attributes = True

# Question Option Schema
class QuestionOptionCreate(BaseModel):
    option_text: str
    option_label: str = Field(..., description="A, B, C, D, etc.")

class QuestionOptionResponse(BaseModel):
    option_text: str
    option_label: str

# Listening Part Schemas
class ListeningPartBase(BaseModel):
    part_number: int = Field(..., ge=1, le=4)
    audio_url: str
    transcript: Optional[str] = None

class ListeningPartCreate(ListeningPartBase):
    section_id: int

class ListeningPartUpdate(BaseModel):
    part_number: Optional[int] = Field(None, ge=1, le=4)
    audio_url: Optional[str] = None
    transcript: Optional[str] = None

class ListeningPartResponse(ListeningPartBase):
    id: int
    section_id: int
    
    class Config:
        from_attributes = True

# Listening Question Schemas
class ListeningQuestionBase(BaseModel):
    question_number: int = Field(..., ge=1)
    question_type: str = Field(..., description="Type from QuestionTypeEnum")
    question_text: str
    order: int = Field(..., ge=1)
    has_options: bool = False
    marks: int = Field(default=1, ge=1)
    instructions: Optional[str] = None
    image_url: Optional[str] = None

class ListeningQuestionCreate(ListeningQuestionBase):
    section_id: int
    part_id: int
    options: Optional[List[QuestionOptionCreate]] = None

class ListeningQuestionUpdate(BaseModel):
    question_number: Optional[int] = Field(None, ge=1)
    question_type: Optional[str] = None
    question_text: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    has_options: Optional[bool] = None
    options: Optional[List[QuestionOptionCreate]] = None
    marks: Optional[int] = Field(None, ge=1)
    instructions: Optional[str] = None
    image_url: Optional[str] = None

class ListeningQuestionResponse(ListeningQuestionBase):
    id: int
    section_id: int
    part_id: int
    image_url: Optional[str] = None
    options: Optional[List[dict]] = None
    
    class Config:
        from_attributes = True

# Listening Answer Schemas
class ListeningAnswerCreate(BaseModel):
    correct_answer: str
    alternative_answers: Optional[List[str]] = None
    case_sensitive: bool = False

class ListeningAnswerUpdate(BaseModel):
    correct_answer: Optional[str] = None
    alternative_answers: Optional[List[str]] = None
    case_sensitive: Optional[bool] = None

class ListeningAnswerResponse(BaseModel):
    id: int
    question_id: int
    correct_answer: str
    alternative_answers: Optional[List[str]]
    case_sensitive: bool
    
    class Config:
        from_attributes = True

class ListeningQuestionWithAnswer(ListeningQuestionResponse):
    answers: List[ListeningAnswerResponse] = []

class ListeningQuestionWithAnswerCreate(BaseModel):
    question: ListeningQuestionCreate
    answer: ListeningAnswerCreate

# Reading Passage Schemas
class ReadingPassageBase(BaseModel):
    passage_number: int = Field(..., ge=1)
    title: str
    content: str
    order: int = Field(..., ge=1)
    difficulty_level: Optional[str] = None

class ReadingPassageCreate(ReadingPassageBase):
    section_id: int

class ReadingPassageUpdate(BaseModel):
    passage_number: Optional[int] = Field(None, ge=1)
    title: Optional[str] = None
    content: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    difficulty_level: Optional[str] = None

class ReadingPassageResponse(ReadingPassageBase):
    id: int
    section_id: int
    word_count: Optional[int]
    
    class Config:
        from_attributes = True

class ReadingPassageWithQuestions(ReadingPassageResponse):
    questions: List["ReadingQuestionResponse"] = []

# Reading Question Schemas
class ReadingQuestionBase(BaseModel):
    question_number: int = Field(..., ge=1)
    question_type: str = Field(..., description="Type from QuestionTypeEnum")
    question_text: str
    order: int = Field(..., ge=1)
    has_options: bool = False
    marks: int = Field(default=1, ge=1)
    instructions: Optional[str] = None

class ReadingQuestionCreate(ReadingQuestionBase):
    passage_id: int
    options: Optional[List[QuestionOptionCreate]] = None

class ReadingQuestionUpdate(BaseModel):
    question_number: Optional[int] = Field(None, ge=1)
    question_type: Optional[str] = None
    question_text: Optional[str] = None
    order: Optional[int] = Field(None, ge=1)
    has_options: Optional[bool] = None
    options: Optional[List[QuestionOptionCreate]] = None
    marks: Optional[int] = Field(None, ge=1)
    instructions: Optional[str] = None

class ReadingQuestionResponse(ReadingQuestionBase):
    id: int
    passage_id: int
    options: Optional[List[dict]] = None
    
    class Config:
        from_attributes = True

# Reading Answer Schemas
class ReadingAnswerCreate(BaseModel):
    correct_answer: str
    alternative_answers: Optional[List[str]] = None
    case_sensitive: bool = False

class ReadingAnswerUpdate(BaseModel):
    correct_answer: Optional[str] = None
    alternative_answers: Optional[List[str]] = None
    case_sensitive: Optional[bool] = None

class ReadingAnswerResponse(BaseModel):
    id: int
    question_id: int
    correct_answer: str
    alternative_answers: Optional[List[str]]
    case_sensitive: bool
    
    class Config:
        from_attributes = True

class ReadingQuestionWithAnswer(ReadingQuestionResponse):
    answers: List[ReadingAnswerResponse] = []

class ReadingQuestionWithAnswerCreate(BaseModel):
    question: ReadingQuestionCreate
    answer: ReadingAnswerCreate

# Writing Task Schemas
class WritingTaskBase(BaseModel):
    task_number: int = Field(..., ge=1, le=2, description="Task 1 or Task 2")
    task_type: str = Field(..., description="Type from QuestionTypeEnum")
    prompt_text: str
    image_url: Optional[str] = None
    word_limit_min: int = Field(..., ge=0)
    word_limit_max: Optional[int] = None
    instructions: Optional[str] = None
    time_limit_minutes: int = Field(..., gt=0)

class WritingTaskCreate(WritingTaskBase):
    section_id: int

class WritingTaskUpdate(BaseModel):
    task_number: Optional[int] = Field(None, ge=1, le=2)
    task_type: Optional[str] = None
    prompt_text: Optional[str] = None
    image_url: Optional[str] = None
    word_limit_min: Optional[int] = Field(None, ge=0)
    word_limit_max: Optional[int] = None
    instructions: Optional[str] = None
    time_limit_minutes: Optional[int] = Field(None, gt=0)

class WritingTaskResponse(WritingTaskBase):
    id: int
    section_id: int
    
    class Config:
        from_attributes = True

# Speaking Task Schemas
class SpeakingTaskBase(BaseModel):
    part_number: int = Field(..., ge=1, le=3, description="Part 1, 2, or 3")
    task_type: str = Field(..., description="Type from QuestionTypeEnum")
    prompt_text: str
    preparation_time_seconds: Optional[int] = Field(None, ge=0)
    speaking_time_seconds: int = Field(..., gt=0)
    order: int = Field(..., ge=1)
    cue_card_points: Optional[List[str]] = None
    instructions: Optional[str] = None

class SpeakingTaskCreate(SpeakingTaskBase):
    section_id: int

class SpeakingTaskUpdate(BaseModel):
    part_number: Optional[int] = Field(None, ge=1, le=3)
    task_type: Optional[str] = None
    prompt_text: Optional[str] = None
    preparation_time_seconds: Optional[int] = Field(None, ge=0)
    speaking_time_seconds: Optional[int] = Field(None, gt=0)
    order: Optional[int] = Field(None, ge=1)
    cue_card_points: Optional[List[str]] = None
    instructions: Optional[str] = None

class SpeakingTaskResponse(SpeakingTaskBase):
    id: int
    section_id: int
    
    class Config:
        from_attributes = True

# Batch Creation Schemas
class BatchQuestionsCreate(BaseModel):
    section_id: int
    listening_questions: Optional[List[ListeningQuestionWithAnswerCreate]] = None
    reading_passages: Optional[List[ReadingPassageCreate]] = None
    reading_questions: Optional[List[ReadingQuestionWithAnswerCreate]] = None
    writing_tasks: Optional[List[WritingTaskCreate]] = None
    speaking_tasks: Optional[List[SpeakingTaskCreate]] = None
