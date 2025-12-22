from app.models.question_types import QuestionTypeEnum
import re

def validate_question_data(question_type: str, type_specific_data: dict, answer_data: dict):
    """
    Validate type-specific data and answers based on question type.
    Raises ValueError if validation fails.
    """
    if not type_specific_data:
        type_specific_data = {}
    if not answer_data:
        answer_data = {}

    # === COMPLETION TYPES ===
    if question_type in [
        QuestionTypeEnum.LISTENING_FORM_COMPLETION,
        QuestionTypeEnum.LISTENING_NOTE_COMPLETION,
        QuestionTypeEnum.LISTENING_TABLE_COMPLETION,
        QuestionTypeEnum.LISTENING_SUMMARY_COMPLETION,
        QuestionTypeEnum.LISTENING_SENTENCE_COMPLETION,
        QuestionTypeEnum.READING_FORM_COMPLETION,
        QuestionTypeEnum.READING_TABLE_COMPLETION,
        QuestionTypeEnum.READING_NOTE_COMPLETION,
        QuestionTypeEnum.READING_SENTENCE_COMPLETION,
        QuestionTypeEnum.READING_SUMMARY_COMPLETION
    ]:
        template = type_specific_data.get("template")
        blanks = type_specific_data.get("blanks", [])

        if not template:
            raise ValueError("Completion questions require a template")

        # Extract all [BLANK_X] markers from template
        found_blanks = set(re.findall(r'\[BLANK_(\d+)\]', template))
        defined_blanks = set(str(b['id'].replace('BLANK_', '')) for b in blanks)

        if found_blanks != defined_blanks:
            raise ValueError(f"Template blanks {found_blanks} don't match defined blanks {defined_blanks}")

        # Validate each blank has an answer
        # answer_data for completion is expected to be a dict: {"BLANK_1": "answer", ...}
        # But wait, ListeningAnswer.correct_answer is a string, but we are moving to JSON for complex types.
        # The answer_data passed here should be the parsed JSON of the correct answer.
        
        for blank in blanks:
            blank_id = blank['id']
            if blank_id not in answer_data:
                raise ValueError(f"Missing correct answer for {blank_id}")

    # === MATCHING TYPES ===
    elif question_type in [
        QuestionTypeEnum.LISTENING_MATCHING_HEADINGS,
        QuestionTypeEnum.LISTENING_MATCHING_SENTENCE_ENDINGS,
        QuestionTypeEnum.LISTENING_MATCHING_PARAGRAPHS,
        QuestionTypeEnum.LISTENING_NAME_MATCHING,
        QuestionTypeEnum.READING_MATCHING_HEADINGS,
        QuestionTypeEnum.READING_MATCHING_FEATURES,
        QuestionTypeEnum.READING_MATCHING_INFORMATION
    ]:
        items = type_specific_data.get("items", [])
        options = type_specific_data.get("options", [])
        allow_multiple = type_specific_data.get("allow_multiple_use", False)

        if not items or not options:
            raise ValueError("Matching questions require items and options")

        if not allow_multiple and len(options) < len(items):
            raise ValueError("Must have at least as many options as items")

        # Validate each item has a correct mapping
        # answer_data for matching: {"1": "A", "2": "B"}
        for item in items:
            item_num = str(item['number'])
            if item_num not in answer_data:
                raise ValueError(f"Missing answer mapping for item {item_num}")

            # Validate the answer is a valid option
            # answer_data[item_num] could be a single letter or list if multiple allowed? 
            # Usually matching is 1-to-1 or 1-to-many items but 1 option per item.
            selected_option = answer_data[item_num]
            valid_options = [opt['letter'] for opt in options]
            
            if selected_option not in valid_options:
                raise ValueError(f"Invalid option {selected_option} for item {item_num}")

    # === MULTIPLE CHOICE ===
    elif question_type in [
        QuestionTypeEnum.LISTENING_MULTIPLE_CHOICE,
        QuestionTypeEnum.READING_MULTIPLE_CHOICE
    ]:
        options = type_specific_data.get("options", [])
        multi_select = type_specific_data.get("multi_select", False)

        if len(options) < 2:
            raise ValueError("Multiple choice requires at least 2 options")

        # answer_data for MCQ: {"correct": ["A"]} or just "A" if simple? 
        # Let's standardize on {"correct": ["A", "B"]} for consistency or just list of strings
        correct_answers = answer_data.get("correct", [])
        
        if not isinstance(correct_answers, list):
             raise ValueError("Correct answers must be a list")

        if not multi_select and len(correct_answers) != 1:
            raise ValueError("Single-select MCQ must have exactly 1 correct answer")

        if not correct_answers:
            raise ValueError("Must have at least 1 correct answer")
            
        valid_option_labels = [opt['label'] for opt in options]
        for ans in correct_answers:
            if ans not in valid_option_labels:
                raise ValueError(f"Invalid correct answer {ans}")

    # === DIAGRAM LABELING ===
    elif question_type in [
        QuestionTypeEnum.LISTENING_DIAGRAM_LABELING,
        QuestionTypeEnum.LISTENING_MAP_LABELING,
        QuestionTypeEnum.READING_DIAGRAM_LABELING,
        QuestionTypeEnum.READING_FLOWCHART
    ]:
        if not type_specific_data.get("image_url"):
            raise ValueError("Diagram questions require an image")

        labels = type_specific_data.get("labels", [])
        if not labels:
            raise ValueError("Diagram must have at least 1 label")

        # answer_data: {"L1": "engine", "L2": "wheel"}
        for label in labels:
            label_id = label['id']
            if label_id not in answer_data:
                raise ValueError(f"Missing answer for label {label_id}")

    return True
