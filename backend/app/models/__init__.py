from app.database import Base

# Import all models
from .user import User, UserProfile, UserRole
from .test import TestTemplate, TestSection, TestAttempt, TestType, SectionType
from .question import (
    ListeningPart,
    ListeningQuestion, 
    ListeningAnswer,
    ReadingPassage, 
    ReadingQuestion, 
    ReadingAnswer,
    WritingTask, 
    SpeakingTask
)
from .question_types import (
    QuestionTypeEnum,
    QuestionTypeTemplate,
    QuestionOption
)
from .submission import (
    ListeningSubmission,
    ReadingSubmission,
    WritingSubmission,
    SpeakingSubmission
)
from .grade import (
    WritingGrade,
    SpeakingGrade,
    TestResult,
    TeacherAssignment
)

# Export all models
__all__ = [
    # Base
    "Base",
    
    # User models
    "User",
    "UserProfile",
    "UserRole",
    
    # Test models
    "TestTemplate",
    "TestSection",
    "TestAttempt",
    "TestType",
    "SectionType",
    
    # Question models
    "ListeningPart",
    "ListeningQuestion",
    "ListeningAnswer",
    "ReadingPassage",
    "ReadingQuestion",
    "ReadingAnswer",
    "WritingTask",
    "SpeakingTask",
    
    # Question type models
    "QuestionTypeEnum",
    "QuestionTypeTemplate",
    "QuestionOption",
    
    # Submission models
    "ListeningSubmission",
    "ReadingSubmission",
    "WritingSubmission",
    "SpeakingSubmission",
    
    # Grade models
    "WritingGrade",
    "SpeakingGrade",
    "TestResult",
    "TeacherAssignment",
]
