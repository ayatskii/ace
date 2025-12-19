from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ListeningSubmission(Base):
    __tablename__ = "listening_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id"))
    question_id = Column(Integer, ForeignKey("listening_questions.id"))
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    test_attempt = relationship("TestAttempt", back_populates="listening_submissions")
    question = relationship("ListeningQuestion", back_populates="submissions")

class ReadingSubmission(Base):
    __tablename__ = "reading_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id"))
    question_id = Column(Integer, ForeignKey("reading_questions.id"))
    user_answer = Column(String, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    test_attempt = relationship("TestAttempt", back_populates="reading_submissions")
    question = relationship("ReadingQuestion", back_populates="submissions")

class WritingSubmission(Base):
    __tablename__ = "writing_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id"))
    task_id = Column(Integer, ForeignKey("writing_tasks.id"))
    response_text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, under_review, graded
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    
    test_attempt = relationship("TestAttempt", back_populates="writing_submissions")
    task = relationship("WritingTask", back_populates="submissions")
    assigned_teacher = relationship("User", foreign_keys=[assigned_teacher_id])
    grade = relationship("WritingGrade", back_populates="submission", uselist=False, cascade="all, delete-orphan")

class SpeakingSubmission(Base):
    __tablename__ = "speaking_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id"))
    task_id = Column(Integer, ForeignKey("speaking_tasks.id"))
    audio_url = Column(String, nullable=False)
    duration_seconds = Column(Integer, nullable=False)
    status = Column(String, default="pending")  # pending, under_review, graded
    submitted_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    assigned_teacher_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    graded_at = Column(DateTime, nullable=True)
    
    test_attempt = relationship("TestAttempt", back_populates="speaking_submissions")
    task = relationship("SpeakingTask", back_populates="submissions")
    assigned_teacher = relationship("User", foreign_keys=[assigned_teacher_id])
    grade = relationship("SpeakingGrade", back_populates="submission", uselist=False, cascade="all, delete-orphan")
