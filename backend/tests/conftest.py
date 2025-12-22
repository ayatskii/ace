"""
Pytest configuration and fixtures for backend tests.
"""
import pytest
import sys
import os

# Add the app directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def completion_question_data():
    """Sample data for completion question tests"""
    return {
        "type_specific_data": {
            "template_text": "The meeting starts at [BLANK_1] on [BLANK_2].",
            "blanks": [
                {"blank_id": "BLANK_1", "max_words": 2, "case_sensitive": False},
                {"blank_id": "BLANK_2", "max_words": 1, "case_sensitive": False}
            ]
        },
        "answer_data": {
            "blanks": {
                "BLANK_1": ["9 am", "nine am", "9:00"],
                "BLANK_2": ["Monday"]
            }
        }
    }


@pytest.fixture
def matching_question_data():
    """Sample data for matching question tests"""
    return {
        "type_specific_data": {
            "items": [
                {"item_number": 1, "item_text": "The capital of France"},
                {"item_number": 2, "item_text": "The capital of Germany"},
                {"item_number": 3, "item_text": "The capital of Italy"}
            ],
            "options": [
                {"option_label": "A", "option_text": "Berlin"},
                {"option_label": "B", "option_text": "Paris"},
                {"option_label": "C", "option_text": "Rome"},
                {"option_label": "D", "option_text": "Madrid"}
            ],
            "allow_option_reuse": False
        },
        "answer_data": {
            "mappings": {"1": "B", "2": "A", "3": "C"}
        }
    }


@pytest.fixture
def mcq_question_data():
    """Sample data for MCQ question tests"""
    return {
        "type_specific_data": {
            "options": [
                {"option_label": "A", "option_text": "Option A"},
                {"option_label": "B", "option_text": "Option B"},
                {"option_label": "C", "option_text": "Option C"},
                {"option_label": "D", "option_text": "Option D"}
            ],
            "allow_multiple": False
        },
        "answer_data": {
            "correct_options": ["B"]
        }
    }


@pytest.fixture
def tfng_question_data():
    """Sample data for True/False/Not Given question tests"""
    return {
        "type_specific_data": {
            "statements": [
                {"statement_number": 1, "statement_text": "The sky is blue."},
                {"statement_number": 2, "statement_text": "Fish can fly."},
                {"statement_number": 3, "statement_text": "The author mentions climate change."}
            ],
            "answer_type": "true_false_not_given"
        },
        "answer_data": {
            "answers": {"1": "TRUE", "2": "FALSE", "3": "NOT GIVEN"}
        }
    }


@pytest.fixture
def diagram_question_data():
    """Sample data for diagram labeling question tests"""
    return {
        "type_specific_data": {
            "image_url": "/uploads/diagram.png",
            "labels": [
                {"label_id": "1", "x": 25.5, "y": 30.0},
                {"label_id": "2", "x": 60.0, "y": 45.5},
                {"label_id": "3", "x": 80.0, "y": 70.0}
            ],
            "max_words_per_label": 2
        },
        "answer_data": {
            "labels": {
                "1": ["library", "the library"],
                "2": ["cafe", "coffee shop"],
                "3": ["parking lot", "car park"]
            }
        }
    }


@pytest.fixture
def short_answer_question_data():
    """Sample data for short answer question tests"""
    return {
        "type_specific_data": {
            "max_words": 3,
            "case_sensitive": False
        },
        "answer_data": {
            "correct_answers": ["global warming", "climate change", "greenhouse effect"]
        }
    }
