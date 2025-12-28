from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
import enum

class QuestionTypeEnum(str, enum.Enum):
    # ===========================================
    # LISTENING TYPES - Completion Family
    # ===========================================
    LISTENING_FORM_COMPLETION = "listening_form_completion"
    LISTENING_NOTE_COMPLETION = "listening_note_completion"
    LISTENING_TABLE_COMPLETION = "listening_table_completion"
    LISTENING_SUMMARY_COMPLETION = "listening_summary_completion"
    LISTENING_SENTENCE_COMPLETION = "listening_sentence_completion"
    
    # LISTENING TYPES - Matching Family
    LISTENING_MATCHING_HEADINGS = "listening_matching_headings"
    LISTENING_MATCHING_SENTENCE_ENDINGS = "listening_matching_sentence_endings"
    LISTENING_MATCHING_PARAGRAPHS = "listening_matching_paragraphs"
    LISTENING_NAME_MATCHING = "listening_name_matching"
    
    # LISTENING TYPES - Choice/Short Answer
    LISTENING_MULTIPLE_CHOICE = "listening_multiple_choice"
    LISTENING_SHORT_ANSWER = "listening_short_answer"
    
    # LISTENING TYPES - Diagram/Map
    LISTENING_DIAGRAM_LABELING = "listening_diagram_labeling"
    LISTENING_MAP_LABELING = "listening_map_labeling"
    
    # ===========================================
    # READING TYPES - Completion Family
    # ===========================================
    READING_FORM_COMPLETION = "reading_form_completion"
    READING_TABLE_COMPLETION = "reading_table_completion"
    READING_NOTE_COMPLETION = "reading_note_completion"
    READING_SENTENCE_COMPLETION = "reading_sentence_completion"
    READING_SUMMARY_COMPLETION = "reading_summary_completion"
    
    # READING TYPES - Matching Family
    READING_MATCHING_HEADINGS = "reading_matching_headings"
    READING_MATCHING_INFORMATION = "reading_matching_information"
    READING_MATCHING_FEATURES = "reading_matching_features"
    READING_MATCHING_SENTENCE_ENDINGS = "reading_matching_sentence_endings"
    
    # READING TYPES - Choice/Short Answer
    READING_MULTIPLE_CHOICE = "reading_multiple_choice"
    READING_SHORT_ANSWER = "reading_short_answer"
    
    # READING TYPES - Diagram/Flowchart
    READING_DIAGRAM_LABELING = "reading_diagram_labeling"
    READING_FLOWCHART = "reading_flowchart"
    
    # READING TYPES - True/False/Not Given
    READING_TRUE_FALSE_NOT_GIVEN = "reading_true_false_not_given"
    READING_YES_NO_NOT_GIVEN = "reading_yes_no_not_given"
    
    # ===========================================
    # WRITING TYPES
    # ===========================================
    WRITING_TASK1_ACADEMIC = "writing_task1_academic"
    WRITING_TASK1_GENERAL = "writing_task1_general"
    WRITING_TASK2_ESSAY = "writing_task2_essay"
    
    # ===========================================
    # SPEAKING TYPES
    # ===========================================
    SPEAKING_PART1 = "speaking_part1"  # Introduction and interview
    SPEAKING_PART2 = "speaking_part2"  # Long turn (cue card)
    SPEAKING_PART3 = "speaking_part3"  # Discussion

def get_question_family(question_type: str) -> str:
    """Returns the question family for routing to appropriate editor/grader"""
    completion_types = [
        "form_completion", "note_completion", "table_completion",
        "summary_completion", "sentence_completion"
    ]
    matching_types = [
        "matching_headings", "matching_sentence_endings", "matching_paragraphs",
        "name_matching", "matching_information", "matching_features"
    ]
    diagram_types = ["diagram_labeling", "map_labeling", "flowchart"]
    tfng_types = ["true_false_not_given", "yes_no_not_given"]
    mcq_types = ["multiple_choice"]
    short_answer_types = ["short_answer"]
    
    type_suffix = question_type.split("_", 1)[1] if "_" in question_type else question_type
    
    if any(t in type_suffix for t in completion_types):
        return "completion"
    elif any(t in type_suffix for t in matching_types):
        return "matching"
    elif any(t in type_suffix for t in diagram_types):
        return "diagram"
    elif any(t in type_suffix for t in tfng_types):
        return "tfng"
    elif any(t in type_suffix for t in mcq_types):
        return "mcq"
    elif any(t in type_suffix for t in short_answer_types):
        return "short_answer"
    else:
        return "simple"

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
