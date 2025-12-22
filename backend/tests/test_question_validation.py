"""
Unit tests for question validation service.
"""
import pytest
from app.services.question_validation import validate_question_data
from app.models.question_types import QuestionTypeEnum


class TestCompletionValidation:
    """Tests for completion question validation"""

    def test_valid_completion_question(self):
        type_specific_data = {
            "template": "The event is on [BLANK_1] at [BLANK_2].",
            "blanks": [
                {"id": "BLANK_1", "max_words": 2},
                {"id": "BLANK_2", "max_words": 1}
            ]
        }
        answer_data = {
            "BLANK_1": "Monday",
            "BLANK_2": "9am"
        }
        
        result = validate_question_data(
            QuestionTypeEnum.LISTENING_SENTENCE_COMPLETION,
            type_specific_data,
            answer_data
        )
        assert result == True

    def test_completion_missing_template(self):
        type_specific_data = {
            "blanks": [{"id": "BLANK_1", "max_words": 2}]
        }
        answer_data = {"BLANK_1": "answer"}
        
        with pytest.raises(ValueError, match="require a template"):
            validate_question_data(
                QuestionTypeEnum.READING_FORM_COMPLETION,
                type_specific_data,
                answer_data
            )

    def test_completion_blank_mismatch(self):
        type_specific_data = {
            "template": "Text with [BLANK_1] and [BLANK_2].",
            "blanks": [{"id": "BLANK_1", "max_words": 2}]  # Missing BLANK_2
        }
        answer_data = {"BLANK_1": "answer"}
        
        with pytest.raises(ValueError, match="don't match"):
            validate_question_data(
                QuestionTypeEnum.LISTENING_NOTE_COMPLETION,
                type_specific_data,
                answer_data
            )

    def test_completion_missing_answer(self):
        type_specific_data = {
            "template": "Text with [BLANK_1].",
            "blanks": [{"id": "BLANK_1", "max_words": 2}]
        }
        answer_data = {}  # No answer provided
        
        with pytest.raises(ValueError, match="Missing correct answer"):
            validate_question_data(
                QuestionTypeEnum.READING_SUMMARY_COMPLETION,
                type_specific_data,
                answer_data
            )


class TestMatchingValidation:
    """Tests for matching question validation"""

    def test_valid_matching_question(self):
        type_specific_data = {
            "items": [
                {"number": 1, "text": "Item 1"},
                {"number": 2, "text": "Item 2"}
            ],
            "options": [
                {"letter": "A", "text": "Option A"},
                {"letter": "B", "text": "Option B"},
                {"letter": "C", "text": "Option C"}
            ],
            "allow_multiple_use": False
        }
        answer_data = {"1": "A", "2": "B"}
        
        result = validate_question_data(
            QuestionTypeEnum.READING_MATCHING_HEADINGS,
            type_specific_data,
            answer_data
        )
        assert result == True

    def test_matching_missing_items(self):
        type_specific_data = {
            "items": [],
            "options": [{"letter": "A", "text": "Option A"}]
        }
        answer_data = {}
        
        with pytest.raises(ValueError, match="require items and options"):
            validate_question_data(
                QuestionTypeEnum.LISTENING_MATCHING_HEADINGS,
                type_specific_data,
                answer_data
            )

    def test_matching_insufficient_options(self):
        type_specific_data = {
            "items": [
                {"number": 1, "text": "Item 1"},
                {"number": 2, "text": "Item 2"},
                {"number": 3, "text": "Item 3"}
            ],
            "options": [
                {"letter": "A", "text": "Option A"},
                {"letter": "B", "text": "Option B"}
            ],
            "allow_multiple_use": False
        }
        answer_data = {"1": "A", "2": "B", "3": "A"}
        
        with pytest.raises(ValueError, match="at least as many options"):
            validate_question_data(
                QuestionTypeEnum.READING_MATCHING_FEATURES,
                type_specific_data,
                answer_data
            )

    def test_matching_invalid_option(self):
        type_specific_data = {
            "items": [{"number": 1, "text": "Item 1"}],
            "options": [{"letter": "A", "text": "Option A"}]
        }
        answer_data = {"1": "Z"}  # Invalid option
        
        with pytest.raises(ValueError, match="Invalid option"):
            validate_question_data(
                QuestionTypeEnum.LISTENING_NAME_MATCHING,
                type_specific_data,
                answer_data
            )


class TestMCQValidation:
    """Tests for multiple choice validation"""

    def test_valid_mcq(self):
        type_specific_data = {
            "options": [
                {"label": "A", "text": "Option A"},
                {"label": "B", "text": "Option B"},
                {"label": "C", "text": "Option C"}
            ],
            "multi_select": False
        }
        answer_data = {"correct": ["B"]}
        
        result = validate_question_data(
            QuestionTypeEnum.READING_MULTIPLE_CHOICE,
            type_specific_data,
            answer_data
        )
        assert result == True

    def test_mcq_insufficient_options(self):
        type_specific_data = {
            "options": [{"label": "A", "text": "Only one option"}]
        }
        answer_data = {"correct": ["A"]}
        
        with pytest.raises(ValueError, match="at least 2 options"):
            validate_question_data(
                QuestionTypeEnum.LISTENING_MULTIPLE_CHOICE,
                type_specific_data,
                answer_data
            )

    def test_mcq_single_select_multiple_answers(self):
        type_specific_data = {
            "options": [
                {"label": "A", "text": "Option A"},
                {"label": "B", "text": "Option B"}
            ],
            "multi_select": False
        }
        answer_data = {"correct": ["A", "B"]}  # Multiple answers for single-select
        
        with pytest.raises(ValueError, match="exactly 1 correct answer"):
            validate_question_data(
                QuestionTypeEnum.READING_MULTIPLE_CHOICE,
                type_specific_data,
                answer_data
            )

    def test_mcq_invalid_correct_answer(self):
        type_specific_data = {
            "options": [
                {"label": "A", "text": "Option A"},
                {"label": "B", "text": "Option B"}
            ]
        }
        answer_data = {"correct": ["Z"]}  # Invalid option
        
        with pytest.raises(ValueError, match="Invalid correct answer"):
            validate_question_data(
                QuestionTypeEnum.LISTENING_MULTIPLE_CHOICE,
                type_specific_data,
                answer_data
            )


class TestDiagramValidation:
    """Tests for diagram labeling validation"""

    def test_valid_diagram(self):
        type_specific_data = {
            "image_url": "/uploads/diagram.png",
            "labels": [
                {"id": "L1", "x": 10, "y": 20},
                {"id": "L2", "x": 50, "y": 60}
            ]
        }
        answer_data = {"L1": "library", "L2": "cafe"}
        
        result = validate_question_data(
            QuestionTypeEnum.LISTENING_DIAGRAM_LABELING,
            type_specific_data,
            answer_data
        )
        assert result == True

    def test_diagram_missing_image(self):
        type_specific_data = {
            "labels": [{"id": "L1", "x": 10, "y": 20}]
        }
        answer_data = {"L1": "answer"}
        
        with pytest.raises(ValueError, match="require an image"):
            validate_question_data(
                QuestionTypeEnum.READING_DIAGRAM_LABELING,
                type_specific_data,
                answer_data
            )

    def test_diagram_no_labels(self):
        type_specific_data = {
            "image_url": "/uploads/diagram.png",
            "labels": []
        }
        answer_data = {}
        
        with pytest.raises(ValueError, match="at least 1 label"):
            validate_question_data(
                QuestionTypeEnum.LISTENING_MAP_LABELING,
                type_specific_data,
                answer_data
            )

    def test_diagram_missing_label_answer(self):
        type_specific_data = {
            "image_url": "/uploads/diagram.png",
            "labels": [
                {"id": "L1", "x": 10, "y": 20},
                {"id": "L2", "x": 50, "y": 60}
            ]
        }
        answer_data = {"L1": "library"}  # Missing L2
        
        with pytest.raises(ValueError, match="Missing answer for label"):
            validate_question_data(
                QuestionTypeEnum.READING_FLOWCHART,
                type_specific_data,
                answer_data
            )
