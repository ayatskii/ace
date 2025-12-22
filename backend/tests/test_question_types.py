"""
Integration tests for question type creation flows.
Tests the API endpoints for creating questions with type-specific data.
"""
import pytest
from app.models.question_types import QuestionTypeEnum, get_question_family


class TestQuestionTypeFamily:
    """Tests for get_question_family helper"""

    def test_completion_types(self):
        completion_types = [
            "listening_form_completion",
            "listening_note_completion",
            "listening_table_completion",
            "listening_summary_completion",
            "listening_sentence_completion",
            "reading_form_completion",
            "reading_table_completion",
            "reading_note_completion",
            "reading_sentence_completion",
            "reading_summary_completion"
        ]
        for qtype in completion_types:
            assert get_question_family(qtype) == "completion", f"{qtype} should be completion"

    def test_matching_types(self):
        matching_types = [
            "listening_matching_headings",
            "listening_matching_sentence_endings",
            "listening_matching_paragraphs",
            "listening_name_matching",
            "reading_matching_headings",
            "reading_matching_information",
            "reading_matching_features",
            "reading_matching_sentence_endings"
        ]
        for qtype in matching_types:
            assert get_question_family(qtype) == "matching", f"{qtype} should be matching"

    def test_diagram_types(self):
        diagram_types = [
            "listening_diagram_labeling",
            "listening_map_labeling",
            "reading_diagram_labeling",
            "reading_flowchart"
        ]
        for qtype in diagram_types:
            assert get_question_family(qtype) == "diagram", f"{qtype} should be diagram"

    def test_tfng_types(self):
        tfng_types = [
            "reading_true_false_not_given",
            "reading_yes_no_not_given"
        ]
        for qtype in tfng_types:
            assert get_question_family(qtype) == "tfng", f"{qtype} should be tfng"

    def test_mcq_types(self):
        mcq_types = [
            "listening_multiple_choice",
            "reading_multiple_choice"
        ]
        for qtype in mcq_types:
            assert get_question_family(qtype) == "mcq", f"{qtype} should be mcq"

    def test_short_answer_types(self):
        short_types = [
            "listening_short_answer",
            "reading_short_answer"
        ]
        for qtype in short_types:
            assert get_question_family(qtype) == "short_answer", f"{qtype} should be short_answer"


class TestQuestionTypeEnum:
    """Tests for QuestionTypeEnum completeness"""

    def test_listening_types_exist(self):
        listening_types = [
            "LISTENING_FORM_COMPLETION",
            "LISTENING_NOTE_COMPLETION",
            "LISTENING_TABLE_COMPLETION",
            "LISTENING_SUMMARY_COMPLETION",
            "LISTENING_SENTENCE_COMPLETION",
            "LISTENING_MATCHING_HEADINGS",
            "LISTENING_MATCHING_SENTENCE_ENDINGS",
            "LISTENING_MATCHING_PARAGRAPHS",
            "LISTENING_NAME_MATCHING",
            "LISTENING_MULTIPLE_CHOICE",
            "LISTENING_SHORT_ANSWER",
            "LISTENING_DIAGRAM_LABELING",
            "LISTENING_MAP_LABELING"
        ]
        for qtype in listening_types:
            assert hasattr(QuestionTypeEnum, qtype), f"Missing {qtype}"

    def test_reading_types_exist(self):
        reading_types = [
            "READING_FORM_COMPLETION",
            "READING_TABLE_COMPLETION",
            "READING_NOTE_COMPLETION",
            "READING_SENTENCE_COMPLETION",
            "READING_SUMMARY_COMPLETION",
            "READING_MATCHING_HEADINGS",
            "READING_MATCHING_INFORMATION",
            "READING_MATCHING_FEATURES",
            "READING_MATCHING_SENTENCE_ENDINGS",
            "READING_MULTIPLE_CHOICE",
            "READING_SHORT_ANSWER",
            "READING_DIAGRAM_LABELING",
            "READING_FLOWCHART",
            "READING_TRUE_FALSE_NOT_GIVEN",
            "READING_YES_NO_NOT_GIVEN"
        ]
        for qtype in reading_types:
            assert hasattr(QuestionTypeEnum, qtype), f"Missing {qtype}"

    def test_enum_values_are_lowercase(self):
        for member in QuestionTypeEnum:
            if member.name.startswith(("LISTENING_", "READING_")):
                assert member.value == member.value.lower(), f"{member.name} value should be lowercase"
                assert "_" in member.value, f"{member.name} value should contain underscores"
