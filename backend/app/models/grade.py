from sqlalchemy import Column, Integer, Float, Text, DateTime, ForeignKey, String, CheckConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class WritingGrade(Base):
    __tablename__ = "writing_grades"
    __table_args__ = (
        CheckConstraint('task_achievement_score >= 0 AND task_achievement_score <= 9', name='check_task_achievement'),
        CheckConstraint('coherence_cohesion_score >= 0 AND coherence_cohesion_score <= 9', name='check_coherence'),
        CheckConstraint('lexical_resource_score >= 0 AND lexical_resource_score <= 9', name='check_lexical_writing'),
        CheckConstraint('grammatical_range_score >= 0 AND grammatical_range_score <= 9', name='check_grammar_writing'),
        CheckConstraint('overall_band_score >= 0 AND overall_band_score <= 9', name='check_overall_writing'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("writing_submissions.id", ondelete="CASCADE"), unique=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    task_achievement_score = Column(Float, nullable=False)
    coherence_cohesion_score = Column(Float, nullable=False)
    lexical_resource_score = Column(Float, nullable=False)
    grammatical_range_score = Column(Float, nullable=False)
    overall_band_score = Column(Float, nullable=False)
    feedback_text = Column(Text, nullable=True)
    graded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    submission = relationship("WritingSubmission", back_populates="grade")
    teacher = relationship("User", foreign_keys=[teacher_id])

class SpeakingGrade(Base):
    __tablename__ = "speaking_grades"
    __table_args__ = (
        CheckConstraint('fluency_coherence_score >= 0 AND fluency_coherence_score <= 9', name='check_fluency'),
        CheckConstraint('lexical_resource_score >= 0 AND lexical_resource_score <= 9', name='check_lexical_speaking'),
        CheckConstraint('grammatical_range_score >= 0 AND grammatical_range_score <= 9', name='check_grammar_speaking'),
        CheckConstraint('pronunciation_score >= 0 AND pronunciation_score <= 9', name='check_pronunciation'),
        CheckConstraint('overall_band_score >= 0 AND overall_band_score <= 9', name='check_overall_speaking'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("speaking_submissions.id", ondelete="CASCADE"), unique=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    fluency_coherence_score = Column(Float, nullable=False)
    lexical_resource_score = Column(Float, nullable=False)
    grammatical_range_score = Column(Float, nullable=False)
    pronunciation_score = Column(Float, nullable=False)
    overall_band_score = Column(Float, nullable=False)
    feedback_text = Column(Text, nullable=True)
    graded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    submission = relationship("SpeakingSubmission", back_populates="grade")
    teacher = relationship("User", foreign_keys=[teacher_id])

class TestResult(Base):
    __tablename__ = "test_results"
    __table_args__ = (
        CheckConstraint('listening_score IS NULL OR (listening_score >= 0 AND listening_score <= 9)', name='check_listening_result'),
        CheckConstraint('reading_score IS NULL OR (reading_score >= 0 AND reading_score <= 9)', name='check_reading_result'),
        CheckConstraint('writing_score IS NULL OR (writing_score >= 0 AND writing_score <= 9)', name='check_writing_result'),
        CheckConstraint('speaking_score IS NULL OR (speaking_score >= 0 AND speaking_score <= 9)', name='check_speaking_result'),
        CheckConstraint('overall_band_score >= 0 AND overall_band_score <= 9', name='check_overall_result'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    test_attempt_id = Column(Integer, ForeignKey("test_attempts.id", ondelete="CASCADE"), unique=True, nullable=False)
    listening_score = Column(Float, nullable=True)
    reading_score = Column(Float, nullable=True)
    writing_score = Column(Float, nullable=True)
    speaking_score = Column(Float, nullable=True)
    overall_band_score = Column(Float, nullable=False)
    generated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    test_attempt = relationship("TestAttempt", back_populates="result")

class TeacherAssignment(Base):
    __tablename__ = "teacher_assignments"
    __table_args__ = (
        Index('idx_teacher_status', 'teacher_id', 'status'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    submission_id = Column(Integer, nullable=False)  # Can be writing or speaking submission
    submission_type = Column(String(20), nullable=False)  # 'writing' or 'speaking'
    assigned_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending, completed
    completed_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    teacher = relationship("User", foreign_keys=[teacher_id])
