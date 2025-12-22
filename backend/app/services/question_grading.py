"""
Question Grading Service

Type-aware grading logic for all IELTS question families.
This module handles the actual answer comparison and scoring.
"""
from typing import Dict, Any, List, Tuple
from app.models.question_types import get_question_family


def grade_question(
    question_type: str,
    user_answer: Any,
    answer_data: Dict[str, Any],
    type_specific_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Grade a question based on its type.
    
    Args:
        question_type: The enum value (e.g., 'listening_sentence_completion')
        user_answer: The user's submitted answer (structure depends on type)
        answer_data: The correct answer data from the question
        type_specific_data: Type-specific configuration (max_words, case_sensitive, etc.)
    
    Returns:
        {
            "is_correct": bool,
            "score": float (0.0 to 1.0),
            "details": dict (type-specific grading details)
        }
    """
    if not answer_data:
        answer_data = {}
    if not type_specific_data:
        type_specific_data = {}
    
    family = get_question_family(question_type)
    
    if family == "completion":
        return grade_completion(user_answer, answer_data, type_specific_data)
    elif family == "matching":
        return grade_matching(user_answer, answer_data, type_specific_data)
    elif family == "mcq":
        return grade_mcq(user_answer, answer_data, type_specific_data)
    elif family == "tfng":
        return grade_tfng(user_answer, answer_data)
    elif family == "diagram":
        return grade_diagram(user_answer, answer_data, type_specific_data)
    elif family == "short_answer":
        return grade_short_answer(user_answer, answer_data, type_specific_data)
    else:
        # Fallback to simple string comparison
        return grade_simple(user_answer, answer_data)


def normalize_text(text: str, case_sensitive: bool = False) -> str:
    """Normalize text for comparison"""
    if not text:
        return ""
    result = text.strip()
    if not case_sensitive:
        result = result.lower()
    return result


def expand_optional_answers(text: str) -> List[str]:
    """
    Expand a text with optional words in parentheses into all valid variations.
    Example: "(fast) food" -> ["fast food", "food"]
             "speed (limit)" -> ["speed limit", "speed"]
    """
    if not text:
        return []
    
    import re
    
    # Find all parenthesized groups
    # This regex handles simple non-nested parentheses
    pattern = r'\((.*?)\)'
    matches = list(re.finditer(pattern, text))
    
    if not matches:
        return [text]
    
    # Generate all combinations (include/exclude each optional part)
    # For N optional parts, there are 2^N variations
    num_options = len(matches)
    variations = []
    
    for i in range(1 << num_options):
        # Build the string for this combination
        result = ""
        last_idx = 0
        
        for j, match in enumerate(matches):
            # Add text before this group
            result += text[last_idx:match.start()]
            
            # Check if we should include this optional part (bit j set)
            if (i >> j) & 1:
                result += match.group(1)
            
            last_idx = match.end()
            
        # Add remaining text
        result += text[last_idx:]
        
        # Clean up extra spaces that might result from removal
        clean_result = " ".join(result.split())
        variations.append(clean_result)
        
    return list(set(variations))  # Unique variations


def check_word_count(text: str, max_words: int) -> bool:
    """Check if text is within word limit"""
    if not text:
        return True
    word_count = len(text.strip().split())
    return word_count <= max_words


def grade_completion(
    user_answer: Any,
    answer_data: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Grade completion (fill-in-blank) questions.
    
    user_answer: {"blanks": {"BLANK_1": "user text", "BLANK_2": "..."}}
    answer_data: {"blanks": {"BLANK_1": ["answer1", "alt1"], "BLANK_2": ["answer2"]}}
    config: {"blanks": [{"blank_id": "BLANK_1", "max_words": 3, "case_sensitive": false}, ...]}
    """
    results = {}
    correct_count = 0
    
    # Parse user answer
    user_blanks = {}
    if isinstance(user_answer, dict):
        user_blanks = user_answer.get("blanks", {})
    elif isinstance(user_answer, str):
        # Legacy: single answer text
        user_blanks = {"BLANK_1": user_answer}
    
    correct_blanks = answer_data.get("blanks", {})
    blank_configs = {b.get("blank_id"): b for b in config.get("blanks", [])}
    
    total_blanks = len(correct_blanks)
    
    for blank_id, correct_answers in correct_blanks.items():
        user_text = user_blanks.get(blank_id, "")
        blank_config = blank_configs.get(blank_id, {})
        
        max_words = blank_config.get("max_words", 3)
        case_sensitive = blank_config.get("case_sensitive", False)
        
        # Check word count
        if not check_word_count(user_text, max_words):
            results[blank_id] = {
                "correct": False,
                "reason": "word_limit_exceeded",
                "user_answer": user_text,
                "max_words": max_words
            }
            continue
        
        # Normalize and compare
        user_normalized = normalize_text(user_text, case_sensitive)
        
        # Check against all acceptable answers
        is_correct = False
        
        raw_correct_list = correct_answers if isinstance(correct_answers, list) else [correct_answers]
        acceptable_variations = []
        
        for raw_ans in raw_correct_list:
            # Expand optional words: "(fast) food" -> ["fast food", "food"]
            expanded = expand_optional_answers(raw_ans)
            for exp in expanded:
                acceptable_variations.append(normalize_text(exp, case_sensitive))
                
        is_correct = user_normalized in acceptable_variations
        
        results[blank_id] = {
            "correct": is_correct,
            "user_answer": user_text
        }
        
        if is_correct:
            correct_count += 1
    
    return {
        "is_correct": correct_count == total_blanks,
        "score": correct_count / max(total_blanks, 1),
        "details": {
            "blanks": results,
            "correct_count": correct_count,
            "total_blanks": total_blanks
        }
    }


def grade_matching(
    user_answer: Any,
    answer_data: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Grade matching questions.
    
    user_answer: {"mappings": {"1": "A", "2": "C"}}
    answer_data: {"mappings": {"1": "A", "2": "B", "3": "C"}}
    """
    results = {}
    correct_count = 0
    
    user_mappings = {}
    if isinstance(user_answer, dict):
        user_mappings = user_answer.get("mappings", {})
    
    correct_mappings = answer_data.get("mappings", {})
    total_items = len(correct_mappings)
    
    for item_num, correct_option in correct_mappings.items():
        user_option = user_mappings.get(str(item_num), "")
        
        is_correct = user_option.upper() == correct_option.upper()
        
        results[item_num] = {
            "correct": is_correct,
            "user_answer": user_option,
            "correct_answer": correct_option
        }
        
        if is_correct:
            correct_count += 1
    
    return {
        "is_correct": correct_count == total_items,
        "score": correct_count / max(total_items, 1),
        "details": {
            "mappings": results,
            "correct_count": correct_count,
            "total_items": total_items
        }
    }


def grade_mcq(
    user_answer: Any,
    answer_data: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Grade multiple choice questions.
    
    user_answer: {"selected": ["A"]} or just "A"
    answer_data: {"correct_options": ["A"]} or {"correct_options": ["A", "C"]}
    config: {"allow_multiple": false}
    """
    # Parse user selection
    user_selected = []
    if isinstance(user_answer, dict):
        user_selected = user_answer.get("selected", [])
    elif isinstance(user_answer, str):
        user_selected = [user_answer]
    elif isinstance(user_answer, list):
        user_selected = user_answer
    
    # Normalize to uppercase
    user_selected = [s.upper() for s in user_selected if s]
    
    correct_options = answer_data.get("correct_options", [])
    if not isinstance(correct_options, list):
        correct_options = [correct_options]
    correct_options = [c.upper() for c in correct_options]
    
    allow_multiple = config.get("allow_multiple", False)
    
    # For single select: exact match
    # For multi-select: must match exactly (no extra, no missing)
    user_set = set(user_selected)
    correct_set = set(correct_options)
    
    is_correct = user_set == correct_set
    
    # Calculate partial score for multi-select
    if allow_multiple and correct_set:
        correct_count = len(user_set & correct_set)
        wrong_count = len(user_set - correct_set)
        # Score is (correct - wrong) / total_correct, clamped at 0
        score = max(0.0, (correct_count - wrong_count) / len(correct_set))
    else:
        score = 1.0 if is_correct else 0.0
    
    return {
        "is_correct": is_correct,
        "score": score,
        "details": {
            "selected": list(user_selected),
            "correct": list(correct_options)
        }
    }


def grade_tfng(
    user_answer: Any,
    answer_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Grade True/False/Not Given or Yes/No/Not Given questions.
    
    user_answer: {"answers": {"1": "TRUE", "2": "FALSE"}}
    answer_data: {"answers": {"1": "TRUE", "2": "NOT GIVEN", "3": "FALSE"}}
    """
    results = {}
    correct_count = 0
    
    user_answers = {}
    if isinstance(user_answer, dict):
        user_answers = user_answer.get("answers", {})
    
    correct_answers = answer_data.get("answers", {})
    total_statements = len(correct_answers)
    
    for stmt_num, correct_value in correct_answers.items():
        user_value = user_answers.get(str(stmt_num), "")
        
        # Normalize for comparison
        user_normalized = user_value.upper().replace("_", " ").strip()
        correct_normalized = correct_value.upper().replace("_", " ").strip()
        
        is_correct = user_normalized == correct_normalized
        
        results[stmt_num] = {
            "correct": is_correct,
            "user_answer": user_value,
            "correct_answer": correct_value
        }
        
        if is_correct:
            correct_count += 1
    
    return {
        "is_correct": correct_count == total_statements,
        "score": correct_count / max(total_statements, 1),
        "details": {
            "statements": results,
            "correct_count": correct_count,
            "total_statements": total_statements
        }
    }


def grade_diagram(
    user_answer: Any,
    answer_data: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Grade diagram/map labeling questions.
    
    user_answer: {"labels": {"1": "library", "2": "cafe"}}
    answer_data: {"labels": {"1": ["library", "the library"], "2": ["cafe", "coffee shop"]}}
    """
    results = {}
    correct_count = 0
    
    user_labels = {}
    if isinstance(user_answer, dict):
        user_labels = user_answer.get("labels", {})
    
    correct_labels = answer_data.get("labels", {})
    max_words = config.get("max_words_per_label", 2)
    total_labels = len(correct_labels)
    
    for label_id, correct_answers in correct_labels.items():
        user_text = user_labels.get(str(label_id), "")
        
        # Check word count
        if not check_word_count(user_text, max_words):
            results[label_id] = {
                "correct": False,
                "reason": "word_limit_exceeded",
                "user_answer": user_text
            }
            continue
        
        # Compare (case-insensitive)
        user_normalized = normalize_text(user_text, case_sensitive=False)
        
        is_correct = False
        if isinstance(correct_answers, list):
            for correct in correct_answers:
                if normalize_text(correct, case_sensitive=False) == user_normalized:
                    is_correct = True
                    break
        else:
            is_correct = normalize_text(correct_answers, case_sensitive=False) == user_normalized
        
        results[label_id] = {
            "correct": is_correct,
            "user_answer": user_text
        }
        
        if is_correct:
            correct_count += 1
    
    return {
        "is_correct": correct_count == total_labels,
        "score": correct_count / max(total_labels, 1),
        "details": {
            "labels": results,
            "correct_count": correct_count,
            "total_labels": total_labels
        }
    }


def grade_short_answer(
    user_answer: Any,
    answer_data: Dict[str, Any],
    config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Grade short answer questions.
    
    user_answer: {"text": "the answer"} or just "the answer"
    answer_data: {"correct_answers": ["answer1", "alternate1", "alternate2"]}
    """
    user_text = ""
    if isinstance(user_answer, dict):
        user_text = user_answer.get("text", "")
    elif isinstance(user_answer, str):
        user_text = user_answer
    
    max_words = config.get("max_words", 3)
    case_sensitive = config.get("case_sensitive", False)
    
    # Check word count
    if not check_word_count(user_text, max_words):
        return {
            "is_correct": False,
            "score": 0.0,
            "details": {
                "reason": "word_limit_exceeded",
                "user_answer": user_text,
                "max_words": max_words
            }
        }
    
    correct_answers = answer_data.get("correct_answers", [])
    if not isinstance(correct_answers, list):
        correct_answers = [correct_answers]
    
    user_normalized = normalize_text(user_text, case_sensitive)
    
    # Check against expanded optional answers
    is_correct = False
    for correct in correct_answers:
        expanded = expand_optional_answers(correct)
        for exp in expanded:
            if normalize_text(exp, case_sensitive) == user_normalized:
                is_correct = True
                break
        if is_correct:
            break
    
    return {
        "is_correct": is_correct,
        "score": 1.0 if is_correct else 0.0,
        "details": {
            "user_answer": user_text
        }
    }


def grade_simple(
    user_answer: Any,
    answer_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Fallback simple grading for legacy questions.
    Compares user answer string to correct_answer string.
    """
    user_text = ""
    if isinstance(user_answer, str):
        user_text = user_answer
    elif isinstance(user_answer, dict):
        user_text = str(user_answer.get("text", user_answer.get("answer", "")))
    
    correct_answer = answer_data.get("correct_answer", "")
    alternatives = answer_data.get("alternative_answers", [])
    case_sensitive = answer_data.get("case_sensitive", False)
    
    all_correct = [correct_answer] + (alternatives if isinstance(alternatives, list) else [])
    
    user_normalized = normalize_text(user_text, case_sensitive)
    
    # Check against expanded optional answers
    is_correct = False
    for correct in all_correct:
        expanded = expand_optional_answers(correct)
        for exp in expanded:
            if normalize_text(exp, case_sensitive) == user_normalized:
                is_correct = True
                break
        if is_correct:
            break
    
    return {
        "is_correct": is_correct,
        "score": 1.0 if is_correct else 0.0,
        "details": {
            "user_answer": user_text
        }
    }
