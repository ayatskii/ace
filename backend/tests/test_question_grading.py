"""
Unit tests for the question grading service.

Tests all question type families:
- Completion (fill-in-blank)
- Matching
- Multiple Choice
- True/False/Not Given
- Diagram labeling
- Short Answer
"""
import pytest
from app.services.question_grading import (
    grade_question,
    grade_completion,
    grade_matching,
    grade_mcq,
    grade_tfng,
    grade_diagram,
    grade_short_answer,
    grade_simple,
    normalize_text,
    check_word_count
)


class TestHelperFunctions:
    """Tests for helper utility functions"""

    def test_normalize_text_case_insensitive(self):
        assert normalize_text("  Hello World  ", case_sensitive=False) == "hello world"

    def test_normalize_text_case_sensitive(self):
        assert normalize_text("  Hello World  ", case_sensitive=True) == "Hello World"

    def test_normalize_text_empty(self):
        assert normalize_text("", case_sensitive=False) == ""
        assert normalize_text(None, case_sensitive=False) == ""

    def test_check_word_count_within_limit(self):
        assert check_word_count("hello world", 3) == True
        assert check_word_count("one two three", 3) == True

    def test_check_word_count_exceeds_limit(self):
        assert check_word_count("one two three four", 3) == False

    def test_check_word_count_empty(self):
        assert check_word_count("", 3) == True
        assert check_word_count("  ", 3) == True


class TestCompletionGrading:
    """Tests for completion/fill-in-blank question grading"""

    def test_completion_all_correct(self):
        user_answer = {"blanks": {"BLANK_1": "9 am", "BLANK_2": "Monday"}}
        answer_data = {
            "blanks": {
                "BLANK_1": ["9 am", "nine am", "9:00"],
                "BLANK_2": ["Monday"]
            }
        }
        config = {
            "blanks": [
                {"blank_id": "BLANK_1", "max_words": 2, "case_sensitive": False},
                {"blank_id": "BLANK_2", "max_words": 1, "case_sensitive": False}
            ]
        }

        result = grade_completion(user_answer, answer_data, config)
        
        assert result["is_correct"] == True
        assert result["score"] == 1.0
        assert result["details"]["correct_count"] == 2

    def test_completion_partial_correct(self):
        user_answer = {"blanks": {"BLANK_1": "9 am", "BLANK_2": "Tuesday"}}
        answer_data = {
            "blanks": {
                "BLANK_1": ["9 am"],
                "BLANK_2": ["Monday"]
            }
        }
        config = {"blanks": []}

        result = grade_completion(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        assert result["score"] == 0.5
        assert result["details"]["correct_count"] == 1

    def test_completion_word_limit_exceeded(self):
        user_answer = {"blanks": {"BLANK_1": "nine o clock in the morning"}}
        answer_data = {"blanks": {"BLANK_1": ["9 am"]}}
        config = {"blanks": [{"blank_id": "BLANK_1", "max_words": 2}]}

        result = grade_completion(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        assert result["details"]["blanks"]["BLANK_1"]["reason"] == "word_limit_exceeded"

    def test_completion_case_insensitive(self):
        user_answer = {"blanks": {"BLANK_1": "MONDAY"}}
        answer_data = {"blanks": {"BLANK_1": ["monday"]}}
        config = {"blanks": [{"blank_id": "BLANK_1", "case_sensitive": False}]}

        result = grade_completion(user_answer, answer_data, config)
        
        assert result["is_correct"] == True

    def test_completion_case_sensitive(self):
        user_answer = {"blanks": {"BLANK_1": "MONDAY"}}
        answer_data = {"blanks": {"BLANK_1": ["Monday"]}}
        config = {"blanks": [{"blank_id": "BLANK_1", "case_sensitive": True}]}

        result = grade_completion(user_answer, answer_data, config)
        
        assert result["is_correct"] == False

    def test_completion_alternative_answer(self):
        user_answer = {"blanks": {"BLANK_1": "nine am"}}
        answer_data = {"blanks": {"BLANK_1": ["9 am", "nine am", "9:00 am"]}}
        config = {"blanks": []}

        result = grade_completion(user_answer, answer_data, config)
        
        assert result["is_correct"] == True


class TestMatchingGrading:
    """Tests for matching question grading"""

    def test_matching_all_correct(self):
        user_answer = {"mappings": {"1": "A", "2": "C", "3": "B"}}
        answer_data = {"mappings": {"1": "A", "2": "C", "3": "B"}}
        config = {}

        result = grade_matching(user_answer, answer_data, config)
        
        assert result["is_correct"] == True
        assert result["score"] == 1.0

    def test_matching_partial_correct(self):
        user_answer = {"mappings": {"1": "A", "2": "B", "3": "C"}}
        answer_data = {"mappings": {"1": "A", "2": "C", "3": "B"}}
        config = {}

        result = grade_matching(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        assert result["score"] == 1/3  # Only 1 correct

    def test_matching_case_insensitive(self):
        user_answer = {"mappings": {"1": "a", "2": "b"}}
        answer_data = {"mappings": {"1": "A", "2": "B"}}
        config = {}

        result = grade_matching(user_answer, answer_data, config)
        
        assert result["is_correct"] == True

    def test_matching_missing_answers(self):
        user_answer = {"mappings": {"1": "A"}}  # Missing 2 and 3
        answer_data = {"mappings": {"1": "A", "2": "B", "3": "C"}}
        config = {}

        result = grade_matching(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        assert result["score"] == 1/3


class TestMCQGrading:
    """Tests for multiple choice question grading"""

    def test_mcq_single_correct(self):
        user_answer = {"selected": ["A"]}
        answer_data = {"correct_options": ["A"]}
        config = {"allow_multiple": False}

        result = grade_mcq(user_answer, answer_data, config)
        
        assert result["is_correct"] == True
        assert result["score"] == 1.0

    def test_mcq_single_incorrect(self):
        user_answer = {"selected": ["B"]}
        answer_data = {"correct_options": ["A"]}
        config = {"allow_multiple": False}

        result = grade_mcq(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        assert result["score"] == 0.0

    def test_mcq_multi_all_correct(self):
        user_answer = {"selected": ["A", "C"]}
        answer_data = {"correct_options": ["A", "C"]}
        config = {"allow_multiple": True}

        result = grade_mcq(user_answer, answer_data, config)
        
        assert result["is_correct"] == True
        assert result["score"] == 1.0

    def test_mcq_multi_partial_correct(self):
        user_answer = {"selected": ["A"]}  # Missing C
        answer_data = {"correct_options": ["A", "C"]}
        config = {"allow_multiple": True}

        result = grade_mcq(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        # Partial score: 1 correct out of 2
        assert result["score"] == 0.5

    def test_mcq_multi_with_wrong_selection(self):
        user_answer = {"selected": ["A", "B"]}  # B is wrong
        answer_data = {"correct_options": ["A", "C"]}
        config = {"allow_multiple": True}

        result = grade_mcq(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        # 1 correct - 1 wrong = 0 out of 2
        assert result["score"] == 0.0

    def test_mcq_string_answer(self):
        """Test legacy string format"""
        user_answer = "A"  # String instead of dict
        answer_data = {"correct_options": ["A"]}
        config = {}

        result = grade_mcq(user_answer, answer_data, config)
        
        assert result["is_correct"] == True


class TestTFNGGrading:
    """Tests for True/False/Not Given grading"""

    def test_tfng_all_correct(self):
        user_answer = {"answers": {"1": "TRUE", "2": "FALSE", "3": "NOT GIVEN"}}
        answer_data = {"answers": {"1": "TRUE", "2": "FALSE", "3": "NOT GIVEN"}}

        result = grade_tfng(user_answer, answer_data)
        
        assert result["is_correct"] == True
        assert result["score"] == 1.0

    def test_tfng_partial_correct(self):
        user_answer = {"answers": {"1": "TRUE", "2": "TRUE", "3": "FALSE"}}
        answer_data = {"answers": {"1": "TRUE", "2": "FALSE", "3": "NOT GIVEN"}}

        result = grade_tfng(user_answer, answer_data)
        
        assert result["is_correct"] == False
        assert result["score"] == 1/3

    def test_tfng_case_insensitive(self):
        user_answer = {"answers": {"1": "true", "2": "false"}}
        answer_data = {"answers": {"1": "TRUE", "2": "FALSE"}}

        result = grade_tfng(user_answer, answer_data)
        
        assert result["is_correct"] == True

    def test_tfng_with_underscores(self):
        user_answer = {"answers": {"1": "NOT_GIVEN"}}
        answer_data = {"answers": {"1": "NOT GIVEN"}}

        result = grade_tfng(user_answer, answer_data)
        
        assert result["is_correct"] == True


class TestDiagramGrading:
    """Tests for diagram/map labeling grading"""

    def test_diagram_all_correct(self):
        user_answer = {"labels": {"1": "library", "2": "cafe"}}
        answer_data = {"labels": {"1": ["library"], "2": ["cafe", "coffee shop"]}}
        config = {"max_words_per_label": 2}

        result = grade_diagram(user_answer, answer_data, config)
        
        assert result["is_correct"] == True
        assert result["score"] == 1.0

    def test_diagram_alternative_answer(self):
        user_answer = {"labels": {"1": "coffee shop"}}
        answer_data = {"labels": {"1": ["cafe", "coffee shop"]}}
        config = {}

        result = grade_diagram(user_answer, answer_data, config)
        
        assert result["is_correct"] == True

    def test_diagram_word_limit_exceeded(self):
        user_answer = {"labels": {"1": "the main library building"}}
        answer_data = {"labels": {"1": ["library"]}}
        config = {"max_words_per_label": 2}

        result = grade_diagram(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        assert result["details"]["labels"]["1"]["reason"] == "word_limit_exceeded"


class TestShortAnswerGrading:
    """Tests for short answer grading"""

    def test_short_answer_correct(self):
        user_answer = {"text": "global warming"}
        answer_data = {"correct_answers": ["global warming", "climate change"]}
        config = {"max_words": 3, "case_sensitive": False}

        result = grade_short_answer(user_answer, answer_data, config)
        
        assert result["is_correct"] == True

    def test_short_answer_alternative(self):
        user_answer = {"text": "climate change"}
        answer_data = {"correct_answers": ["global warming", "climate change"]}
        config = {}

        result = grade_short_answer(user_answer, answer_data, config)
        
        assert result["is_correct"] == True

    def test_short_answer_word_limit(self):
        user_answer = {"text": "the phenomenon of global warming"}
        answer_data = {"correct_answers": ["global warming"]}
        config = {"max_words": 2}

        result = grade_short_answer(user_answer, answer_data, config)
        
        assert result["is_correct"] == False
        assert result["details"]["reason"] == "word_limit_exceeded"

    def test_short_answer_string_format(self):
        """Test legacy string format"""
        user_answer = "answer text"
        answer_data = {"correct_answers": ["answer text"]}
        config = {}

        result = grade_short_answer(user_answer, answer_data, config)
        
        assert result["is_correct"] == True


class TestGradeQuestionDispatcher:
    """Tests for the main grade_question dispatcher"""

    def test_dispatch_completion(self):
        result = grade_question(
            question_type="listening_sentence_completion",
            user_answer={"blanks": {"BLANK_1": "monday"}},
            answer_data={"blanks": {"BLANK_1": ["Monday"]}},
            type_specific_data={"blanks": []}
        )
        assert "is_correct" in result

    def test_dispatch_matching(self):
        result = grade_question(
            question_type="reading_matching_headings",
            user_answer={"mappings": {"1": "A"}},
            answer_data={"mappings": {"1": "A"}},
            type_specific_data={}
        )
        assert result["is_correct"] == True

    def test_dispatch_mcq(self):
        result = grade_question(
            question_type="listening_multiple_choice",
            user_answer={"selected": ["B"]},
            answer_data={"correct_options": ["B"]},
            type_specific_data={}
        )
        assert result["is_correct"] == True

    def test_dispatch_tfng(self):
        result = grade_question(
            question_type="reading_true_false_not_given",
            user_answer={"answers": {"1": "TRUE"}},
            answer_data={"answers": {"1": "TRUE"}},
            type_specific_data={}
        )
        assert result["is_correct"] == True

    def test_dispatch_diagram(self):
        result = grade_question(
            question_type="listening_diagram_labeling",
            user_answer={"labels": {"1": "hall"}},
            answer_data={"labels": {"1": ["hall", "main hall"]}},
            type_specific_data={}
        )
        assert result["is_correct"] == True

    def test_dispatch_short_answer(self):
        result = grade_question(
            question_type="reading_short_answer",
            user_answer={"text": "carbon dioxide"},
            answer_data={"correct_answers": ["carbon dioxide", "CO2"]},
            type_specific_data={}
        )
        assert result["is_correct"] == True


class TestSimpleGrading:
    """Tests for legacy simple grading (fallback)"""

    def test_simple_correct(self):
        user_answer = "correct answer"
        answer_data = {
            "correct_answer": "correct answer",
            "alternative_answers": ["alt answer"],
            "case_sensitive": False
        }

        result = grade_simple(user_answer, answer_data)
        
        assert result["is_correct"] == True

    def test_simple_alternative(self):
        user_answer = "alt answer"
        answer_data = {
            "correct_answer": "correct answer",
            "alternative_answers": ["alt answer"]
        }

        result = grade_simple(user_answer, answer_data)
        
        assert result["is_correct"] == True
