from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint, Index, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ListeningSubmission(Base):
    __tablename__ = "listening_submissions"
    __table_args__ = (
        UniqueConstraint('test_attempt_id', 'question_id', name='uq_listening_submission'),
        Index('idx_listening_attempt', 'test_attempt_id'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("listening_questions.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    test_attempt = relationship("TestAttempt", back_populates="listening_submissions")
    question = relationship("ListeningQuestion", back_populates="submissions")

class ReadingSubmission(Base):
    __tablename__ = "reading_submissions"
    __table_args__ = (
        UniqueConstraint('test_attempt_id', 'question_id', name='uq_reading_submission'),
        Index('idx_reading_attempt', 'test_attempt_id'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("reading_questions.id", ondelete="CASCADE"), nullable=False)
    user_answer = Column(String(500), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    test_attempt = relationship("TestAttempt", back_populates="reading_submissions")
    question = relationship("ReadingQuestion", back_populates="submissions")

class WritingSubmission(Base):
    __tablename__ = "writing_submissions"
    __table_args__ = (
        UniqueConstraint('test_attempt_id', 'task_id', name='uq_writing_submission'),
        Index('idx_writing_attempt', 'test_attempt_id'),
        Index('idx_writing_status', 'status'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("writing_tasks.id", ondelete="CASCADE"), nullable=False)
    response_text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending, under_review, graded
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    assigned_teacher_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    test_attempt = relationship("TestAttempt", back_populates="writing_submissions")
    task = relationship("WritingTask", back_populates="submissions")
    assigned_teacher = relationship("User", foreign_keys=[assigned_teacher_id])
    grade = relationship("WritingGrade", back_populates="submission", uselist=False, cascade="all, delete-orphan")

class SpeakingSubmission(Base):
    __tablename__ = "speaking_submissions"
    __table_args__ = (
        UniqueConstraint('test_attempt_id', 'task_id', name='uq_speaking_submission'),
        Index('idx_speaking_attempt', 'test_attempt_id'),
        Index('idx_speaking_status', 'status'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(Integer, ForeignKey("speaking_tasks.id", ondelete="CASCADE"), nullable=False)
    audio_url = Column(String(500), nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending, under_review, graded
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    assigned_teacher_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    test_attempt = relationship("TestAttempt", back_populates="speaking_submissions")
    task = relationship("SpeakingTask", back_populates="submissions")
    assigned_teacher = relationship("User", foreign_keys=[assigned_teacher_id])
    grade = relationship("SpeakingGrade", back_populates="submission", uselist=False, cascade="all, delete-orphan")
