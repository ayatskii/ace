from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
import enum

class QuestionTypeEnum(str, enum.Enum):
    # Listening Types
    LISTENING_MULTIPLE_CHOICE = "listening_multiple_choice"
    LISTENING_FILL_IN_BLANK = "listening_fill_in_blank"
    LISTENING_MATCHING = "listening_matching"
    LISTENING_MAP_DIAGRAM = "listening_map_diagram"
    LISTENING_NOTE_COMPLETION = "listening_note_completion"
    LISTENING_TRUE_FALSE_NOT_GIVEN = "listening_true_false_not_given"
    
    # Reading Types
    READING_MULTIPLE_CHOICE = "reading_multiple_choice"
    READING_TRUE_FALSE_NOT_GIVEN = "reading_true_false_not_given"
    READING_YES_NO_NOT_GIVEN = "reading_yes_no_not_given"
    READING_MATCHING_HEADINGS = "reading_matching_headings"
    READING_MATCHING_INFORMATION = "reading_matching_information"
    READING_MATCHING_FEATURES = "reading_matching_features"
    READING_SENTENCE_COMPLETION = "reading_sentence_completion"
    READING_SUMMARY_COMPLETION = "reading_summary_completion"
    READING_SHORT_ANSWER = "reading_short_answer"
    READING_DIAGRAM_LABELING = "reading_diagram_labeling"
    
    # Writing Types
    WRITING_TASK1_ACADEMIC = "writing_task1_academic"  
    WRITING_TASK1_GENERAL = "writing_task1_general"  
    WRITING_TASK2_ESSAY = "writing_task2_essay"
    
    # Speaking Types
    SPEAKING_PART1 = "speaking_part1"  # Introduction and interview
    SPEAKING_PART2 = "speaking_part2"  # Long turn (cue card)
    SPEAKING_PART3 = "speaking_part3"  # Discussion

class QuestionTypeTemplate(Base):
    """Predefined question type templates that admins can choose from"""
    __tablename__ = "question_type_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)  # e.g., "Multiple Choice"
    type_enum = Column(String, nullable=False)  # Maps to QuestionTypeEnum
    section_type = Column(String, nullable=False)  # listening, reading, writing, speaking
    description = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)  # Default instructions for this type
    is_active = Column(Boolean, default=True)
    
class QuestionOption(Base):
    """Options for multiple choice and matching questions"""
    __tablename__ = "question_options"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, nullable=False)  # Generic reference
    question_type = Column(String, nullable=False)  # 'listening' or 'reading'
    option_text = Column(String, nullable=False)
    option_label = Column(String, nullable=False)  # A, B, C, D
    order = Column(Integer, nullable=False)
