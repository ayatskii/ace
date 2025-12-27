import pytest
from app.services.question_grading import (
    expand_optional_answers,
    grade_completion,
    grade_mcq,
    grade_short_answer,
    grade_diagram
)
from app.services.question_validation import validate_question_data
from app.models.question_types import QuestionTypeEnum

# --- Question Grading Edge Cases ---

def test_expand_optional_answers_complex():
    # Multiple optional groups
    text = "(fast) food (truck)"
    variations = expand_optional_answers(text)
    expected = {
        "fast food truck",
        "food truck",
        "fast food",
        "food"
    }
    assert set(variations) == expected

    # Nested or adjacent? The regex `\((.*?)\)` handles non-nested.
    # "(a) (b)" -> a b, a, b, "" (empty string if all removed?)
    text = "(a) (b)"
    variations = expand_optional_answers(text)
    # "a b", "b", "a", "" -> normalized might strip empty
    assert "a b" in variations
    assert "a" in variations
    assert "b" in variations
    # The function joins with spaces and strips, so "" might be empty string
    
def test_grade_completion_legacy_input():
    # user_answer as string instead of dict
    user_answer = "my answer"
    answer_data = {"blanks": {"BLANK_1": "my answer"}}
    config = {"blanks": [{"blank_id": "BLANK_1"}]}
    
    result = grade_completion(user_answer, answer_data, config)
    assert result["is_correct"] is True
    assert result["score"] == 1.0

def test_grade_mcq_edge_cases():
    # user_answer as list
    user_answer = ["A", "B"]
    answer_data = {"correct_options": ["A", "B"]}
    config = {"allow_multiple": True}
    result = grade_mcq(user_answer, answer_data, config)
    assert result["is_correct"] is True
    
    # correct_options as string (robustness)
    user_answer = "A"
    answer_data = {"correct_options": "A"} # Not a list
    config = {}
    result = grade_mcq(user_answer, answer_data, config)
    assert result["is_correct"] is True

def test_grade_short_answer_robustness():
    # correct_answers as string
    user_answer = "answer"
    answer_data = {"correct_answers": "answer"} # Not a list
    config = {}
    result = grade_short_answer(user_answer, answer_data, config)
    assert result["is_correct"] is True

def test_grade_diagram_single_correct_answer():
    # correct_answers as string (not list) in diagram
    user_answer = {"labels": {"1": "engine"}}
    answer_data = {"labels": {"1": "engine"}} # Not a list
    config = {}
    result = grade_diagram(user_answer, answer_data, config)
    assert result["is_correct"] is True


# --- Question Validation Edge Cases ---

def test_validate_empty_type_specific_data():
    # Should not raise error if type doesn't require it, or handle gracefully
    # But validate_question_data checks for it.
    # If we pass None, it should default to {}
    # But then specific types might raise ValueError if they need data.
    
    # Test with a type that doesn't check much, or check that it handles None
    try:
        validate_question_data("unknown_type", None, None)
    except ValueError:
        pytest.fail("Should not raise ValueError for unknown type with None data")

def test_validate_matching_missing_mapping():
    q_type = QuestionTypeEnum.LISTENING_MATCHING_HEADINGS
    type_data = {
        "items": [{"number": 1}],
        "options": [{"letter": "A"}]
    }
    answer_data = {} # Missing mapping for item 1
    
    with pytest.raises(ValueError, match="Missing answer mapping for item 1"):
        validate_question_data(q_type, type_data, answer_data)

def test_validate_mcq_invalid_correct_structure():
    q_type = QuestionTypeEnum.LISTENING_MULTIPLE_CHOICE
    type_data = {"options": [{"label": "A"}, {"label": "B"}]}
    
    # Correct answers not a list
    answer_data = {"correct": "A"}
    with pytest.raises(ValueError, match="Correct answers must be a list"):
        validate_question_data(q_type, type_data, answer_data)
        
    # Empty correct answers
    type_data["multi_select"] = True
    answer_data = {"correct": []}
    with pytest.raises(ValueError, match="Must have at least 1 correct answer"):
        validate_question_data(q_type, type_data, answer_data)
