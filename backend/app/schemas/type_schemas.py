"""
Type-specific Pydantic schemas for IELTS question data structures.
These define the shape of type_specific_data and answer_data JSON fields.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict


# =============================================================================
# COMPLETION FAMILY (Form, Note, Table, Summary, Sentence Completion)
# =============================================================================

class BlankConfig(BaseModel):
    """Configuration for a single blank in a completion question"""
    blank_id: str = Field(..., description="e.g., 'BLANK_1', 'BLANK_2'")
    max_words: int = Field(default=3, ge=1, le=10, description="Maximum word limit for this blank")
    case_sensitive: bool = Field(default=False, description="Whether answer matching is case-sensitive")


class CompletionTypeSpecificData(BaseModel):
    """
    Type-specific data for all completion-type questions.
    The template_text contains [BLANK_X] markers that are replaced with inputs.
    """
    template_text: str = Field(..., description="Text with [BLANK_1], [BLANK_2], etc. markers")
    blanks: List[BlankConfig] = Field(default_factory=list, description="Configuration for each blank")


class CompletionAnswerData(BaseModel):
    """
    Answer data for completion questions.
    Maps blank_id to list of acceptable answers (first is primary, rest are alternatives).
    """
    blanks: Dict[str, List[str]] = Field(
        ..., 
        description="e.g., {'BLANK_1': ['answer1', 'alt1'], 'BLANK_2': ['answer2']}"
    )


# =============================================================================
# MATCHING FAMILY (Headings, Sentence Endings, Paragraphs, Names, Features)
# =============================================================================

class MatchingItem(BaseModel):
    """A numbered item to be matched"""
    item_number: int = Field(..., ge=1)
    item_text: str


class MatchingOption(BaseModel):
    """A lettered option that items are matched to"""
    option_label: str = Field(..., description="A, B, C, etc.")
    option_text: str


class MatchingTypeSpecificData(BaseModel):
    """Type-specific data for matching questions"""
    items: List[MatchingItem] = Field(default_factory=list)
    options: List[MatchingOption] = Field(default_factory=list)
    allow_option_reuse: bool = Field(default=False, description="Can options be used for multiple items?")


class MatchingAnswerData(BaseModel):
    """Answer data for matching questions - maps item number to correct option"""
    mappings: Dict[str, str] = Field(
        ...,
        description="e.g., {'1': 'A', '2': 'C', '3': 'B'}"
    )


# =============================================================================
# MULTIPLE CHOICE FAMILY
# =============================================================================

class MCQOption(BaseModel):
    """An option in a multiple choice question"""
    option_label: str = Field(..., description="A, B, C, D, etc.")
    option_text: str


class MCQTypeSpecificData(BaseModel):
    """Type-specific data for multiple choice questions"""
    options: List[MCQOption] = Field(default_factory=list)
    allow_multiple: bool = Field(default=False, description="Allow selecting multiple answers?")


class MCQAnswerData(BaseModel):
    """Answer data for MCQ - list of correct option labels"""
    correct_options: List[str] = Field(
        ...,
        description="['A'] for single select, ['A', 'C'] for multi-select"
    )


# =============================================================================
# DIAGRAM/MAP/FLOWCHART LABELING
# =============================================================================

class LabelPoint(BaseModel):
    """A label point on an image with coordinates"""
    label_id: str = Field(..., description="e.g., '1', '2', etc.")
    x: float = Field(..., ge=0, le=100, description="X coordinate as percentage (0-100)")
    y: float = Field(..., ge=0, le=100, description="Y coordinate as percentage (0-100)")


class DiagramTypeSpecificData(BaseModel):
    """Type-specific data for diagram/map labeling questions"""
    image_url: str = Field(..., description="URL of the diagram/map image")
    labels: List[LabelPoint] = Field(default_factory=list)
    max_words_per_label: int = Field(default=2, ge=1)


class DiagramAnswerData(BaseModel):
    """Answer data for diagram questions - maps label_id to acceptable answers"""
    labels: Dict[str, List[str]] = Field(
        ...,
        description="e.g., {'1': ['library', 'the library'], '2': ['cafe']}"
    )


# =============================================================================
# TRUE/FALSE/NOT GIVEN and YES/NO/NOT GIVEN
# =============================================================================

class TFNGStatement(BaseModel):
    """A statement for True/False/Not Given questions"""
    statement_number: int = Field(..., ge=1)
    statement_text: str


class TFNGTypeSpecificData(BaseModel):
    """Type-specific data for T/F/NG or Y/N/NG questions"""
    statements: List[TFNGStatement] = Field(default_factory=list)
    answer_type: str = Field(
        default="true_false_not_given",
        description="'true_false_not_given' or 'yes_no_not_given'"
    )


class TFNGAnswerData(BaseModel):
    """Answer data for T/F/NG questions"""
    answers: Dict[str, str] = Field(
        ...,
        description="e.g., {'1': 'TRUE', '2': 'FALSE', '3': 'NOT GIVEN'}"
    )


# =============================================================================
# SHORT ANSWER
# =============================================================================

class ShortAnswerTypeSpecificData(BaseModel):
    """Type-specific data for short answer questions"""
    max_words: int = Field(default=3, ge=1, le=10)
    case_sensitive: bool = Field(default=False)


class ShortAnswerAnswerData(BaseModel):
    """Answer data for short answer - list of acceptable answers"""
    correct_answers: List[str] = Field(
        ...,
        description="Primary answer + alternatives"
    )


# =============================================================================
# USER ANSWER SCHEMAS (for submissions)
# =============================================================================

class CompletionUserAnswer(BaseModel):
    """User's answer structure for completion questions"""
    blanks: Dict[str, str] = Field(
        default_factory=dict,
        description="e.g., {'BLANK_1': 'user answer', 'BLANK_2': 'another'}"
    )


class MatchingUserAnswer(BaseModel):
    """User's answer structure for matching questions"""
    mappings: Dict[str, str] = Field(
        default_factory=dict,
        description="e.g., {'1': 'B', '2': 'A'}"
    )


class MCQUserAnswer(BaseModel):
    """User's answer structure for MCQ"""
    selected: List[str] = Field(
        default_factory=list,
        description="['A'] or ['A', 'C'] for multi"
    )


class DiagramUserAnswer(BaseModel):
    """User's answer structure for diagram labeling"""
    labels: Dict[str, str] = Field(
        default_factory=dict,
        description="e.g., {'1': 'library', '2': 'cafe'}"
    )


class TFNGUserAnswer(BaseModel):
    """User's answer structure for T/F/NG"""
    answers: Dict[str, str] = Field(
        default_factory=dict,
        description="e.g., {'1': 'TRUE', '2': 'NOT GIVEN'}"
    )


class ShortAnswerUserAnswer(BaseModel):
    """User's answer structure for short answer"""
    text: str = Field(default="")
