from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class WritingGrade(Base):
    __tablename__ = "writing_grades"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("writing_submissions.id"), unique=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    task_achievement_score = Column(Float, nullable=False)
    coherence_cohesion_score = Column(Float, nullable=False)
    lexical_resource_score = Column(Float, nullable=False)
    grammatical_range_score = Column(Float, nullable=False)
    overall_band_score = Column(Float, nullable=False)
    feedback_text = Column(Text, nullable=True)
    graded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    submission = relationship("WritingSubmission", back_populates="grade")
    teacher = relationship("User", foreign_keys=[teacher_id])

class SpeakingGrade(Base):
    __tablename__ = "speaking_grades"
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("speaking_submissions.id"), unique=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    fluency_coherence_score = Column(Float, nullable=False)
    lexical_resource_score = Column(Float, nullable=False)
    grammatical_range_score = Column(Float, nullable=False)
    pronunciation_score = Column(Float, nullable=False)
    overall_band_score = Column(Float, nullable=False)
    feedback_text = Column(Text, nullable=True)
    graded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    submission = relationship("SpeakingSubmission", back_populates="grade")
    teacher = relationship("User", foreign_keys=[teacher_id])

class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id"), unique=True)
    listening_score = Column(Float, nullable=True)
    reading_score = Column(Float, nullable=True)
    writing_score = Column(Float, nullable=True)
    speaking_score = Column(Float, nullable=True)
    overall_band_score = Column(Float, nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    test_attempt = relationship("TestAttempt", back_populates="result")

class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id"))
    submission_id = Column(Integer, nullable=False)  # Can be writing or speaking submission
    submission_type = Column(String, nullable=False)  # 'writing' or 'speaking'
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String, default="pending")  # pending, completed
    completed_at = Column(DateTime, nullable=True)
    
    teacher = relationship("User", foreign_keys=[teacher_id])
