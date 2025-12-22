from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, JSON, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class ListeningPart(Base):
    __tablename__ = "listening_parts"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("test_sections.id", ondelete="CASCADE"), nullable=False)
    part_number = Column(Integer, nullable=False)  # 1-4
    audio_url = Column(String(500), nullable=False)
    transcript = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    section = relationship("TestSection", back_populates="listening_parts")
    questions = relationship("ListeningQuestion", back_populates="part", cascade="all, delete-orphan")

class ListeningQuestion(Base):
    __tablename__ = "listening_questions"
    __table_args__ = (
        UniqueConstraint('section_id', 'question_number', name='uq_listening_question'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("test_sections.id", ondelete="CASCADE"), nullable=False)
    part_id = Column(Integer, ForeignKey("listening_parts.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_type = Column(String(100), nullable=False)  # From QuestionTypeEnum
    question_text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    
    # For multiple choice/matching questions
    has_options = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)  # [{"label": "A", "text": "option 1"}, ...]
    
    # Additional metadata
    marks = Column(Integer, default=1, nullable=False)
    instructions = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)  # For map/diagram questions
    
    # Type-specific configuration (varies by question_type)
    type_specific_data = Column(JSON, nullable=True)  # Template, blanks config, items/options, etc.
    answer_data = Column(JSON, nullable=True)  # Structured answers for complex types
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    section = relationship("TestSection", back_populates="listening_questions")
    part = relationship("ListeningPart", back_populates="questions")
    answers = relationship("ListeningAnswer", back_populates="question", cascade="all, delete-orphan")
    submissions = relationship("ListeningSubmission", back_populates="question")

class ListeningAnswer(Base):
    __tablename__ = "listening_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("listening_questions.id", ondelete="CASCADE"), nullable=False)
    correct_answer = Column(String(500), nullable=False)
    alternative_answers = Column(JSON, nullable=True)  # ["answer1", "answer2"] for flexibility
    case_sensitive = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    question = relationship("ListeningQuestion", back_populates="answers")

class ReadingPassage(Base):
    __tablename__ = "reading_passages"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("test_sections.id", ondelete="CASCADE"), nullable=False)
    passage_number = Column(Integer, nullable=False)
    title = Column(String(300), nullable=False)
    content = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    
    # Metadata
    word_count = Column(Integer, nullable=True)
    difficulty_level = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    section = relationship("TestSection", back_populates="reading_passages")
    questions = relationship("ReadingQuestion", back_populates="passage", cascade="all, delete-orphan")

class ReadingQuestion(Base):
    __tablename__ = "reading_questions"
    __table_args__ = (
        UniqueConstraint('passage_id', 'question_number', name='uq_reading_question'),
    )
    
    id = Column(Integer, primary_key=True, index=True)
    passage_id = Column(Integer, ForeignKey("reading_passages.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer, nullable=False)
    question_type = Column(String(100), nullable=False)  # From QuestionTypeEnum
    question_text = Column(Text, nullable=False)
    order = Column(Integer, nullable=False)
    
    # For multiple choice/matching questions
    has_options = Column(Boolean, default=False)
    options = Column(JSON, nullable=True)
    
    # Additional metadata
    marks = Column(Integer, default=1, nullable=False)
    instructions = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)  # For diagram/flowchart questions
    
    # Type-specific configuration (varies by question_type)
    type_specific_data = Column(JSON, nullable=True)  # Template, blanks config, items/options, etc.
    answer_data = Column(JSON, nullable=True)  # Structured answers for complex types
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    passage = relationship("ReadingPassage", back_populates="questions")
    answers = relationship("ReadingAnswer", back_populates="question", cascade="all, delete-orphan")
    submissions = relationship("ReadingSubmission", back_populates="question")

class ReadingAnswer(Base):
    __tablename__ = "reading_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("reading_questions.id", ondelete="CASCADE"), nullable=False)
    correct_answer = Column(String(500), nullable=False)
    alternative_answers = Column(JSON, nullable=True)
    case_sensitive = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    question = relationship("ReadingQuestion", back_populates="answers")

class WritingTask(Base):
    __tablename__ = "writing_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("test_sections.id", ondelete="CASCADE"), nullable=False)
    task_number = Column(Integer, nullable=False)  # 1 or 2
    task_type = Column(String(100), nullable=False)  # From QuestionTypeEnum
    prompt_text = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=True)  # For Task 1 Academic (graphs/charts)
    word_limit_min = Column(Integer, nullable=False)
    word_limit_max = Column(Integer, nullable=True)
    
    # Additional instructions
    instructions = Column(Text, nullable=True)
    time_limit_minutes = Column(Integer, nullable=False)  # 20 for Task 1, 40 for Task 2
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    section = relationship("TestSection", back_populates="writing_tasks")
    submissions = relationship("WritingSubmission", back_populates="task")

class SpeakingTask(Base):
    __tablename__ = "speaking_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    section_id = Column(Integer, ForeignKey("test_sections.id", ondelete="CASCADE"), nullable=False)
    part_number = Column(Integer, nullable=False)  # 1, 2, or 3
    task_type = Column(String(100), nullable=False)  # From QuestionTypeEnum
    prompt_text = Column(Text, nullable=False)
    preparation_time_seconds = Column(Integer, nullable=True)  # 60 for Part 2
    speaking_time_seconds = Column(Integer, nullable=False)
    order = Column(Integer, nullable=False)
    
    # For Part 2 cue cards
    cue_card_points = Column(JSON, nullable=True)  # ["point 1", "point 2", "point 3"]
    
    # Additional instructions
    instructions = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    section = relationship("TestSection", back_populates="speaking_tasks")
    submissions = relationship("SpeakingSubmission", back_populates="task")
