from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, Float, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import enum
from app.database import Base

class TestType(str, enum.Enum):
    ACADEMIC = "academic"
    GENERAL_TRAINING = "general_training"

class SectionType(str, enum.Enum):
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"

class TestTemplate(Base):
    __tablename__ = "test_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    test_type = Column(Enum(TestType), nullable=False)
    difficulty_level = Column(String(50), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    is_published = Column(Boolean, default=False, nullable=False)
    
    # Soft delete fields
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    
    # Foreign keys with proper cascade
    created_by = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    creator = relationship("User", back_populates="created_tests")
    sections = relationship("TestSection", back_populates="test_template", cascade="all, delete-orphan")
    test_attempts = relationship("TestAttempt", back_populates="test_template")

class TestSection(Base):
    __tablename__ = "test_sections"
    
    id = Column(Integer, primary_key=True, index=True)
    test_template_id = Column(Integer, ForeignKey("test_templates.id", ondelete="CASCADE"), nullable=False)
    section_type = Column(Enum(SectionType), nullable=False)
    order = Column(Integer, nullable=False)
    total_questions = Column(Integer, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    test_template = relationship("TestTemplate", back_populates="sections")
    listening_parts = relationship("ListeningPart", back_populates="section")
    listening_questions = relationship("ListeningQuestion", back_populates="section")
    reading_passages = relationship("ReadingPassage", back_populates="section")
    writing_tasks = relationship("WritingTask", back_populates="section")
    speaking_tasks = relationship("SpeakingTask", back_populates="section")

class TestAttempt(Base):
    __tablename__ = "test_attempts"
    __table_args__ = (
        Index('idx_attempt_user_status', 'user_id', 'status'),
        Index('idx_attempt_template', 'test_template_id'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    test_template_id = Column(Integer, ForeignKey("test_templates.id", ondelete="RESTRICT"), nullable=False)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    end_time = Column(DateTime, nullable=True)
    status = Column(String(20), default="in_progress", nullable=False)
    overall_band_score = Column(Float, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    user = relationship("User", back_populates="test_attempts")
    test_template = relationship("TestTemplate", back_populates="test_attempts")
    listening_submissions = relationship("ListeningSubmission", back_populates="test_attempt")
    reading_submissions = relationship("ReadingSubmission", back_populates="test_attempt")
    writing_submissions = relationship("WritingSubmission", back_populates="test_attempt")
    speaking_submissions = relationship("SpeakingSubmission", back_populates="test_attempt")
    result = relationship("TestResult", back_populates="test_attempt", uselist=False)

