from app.schemas.question import ReadingQuestionCreate, ReadingQuestionUpdate, ReadingQuestionResponse

def test_reading_question_schema_with_json_fields():
    # Test Create Schema
    create_data = {
        "question_number": 1,
        "question_type": "reading_table_completion",
        "question_text": "Complete the table below.",
        "order": 1,
        "has_options": False,
        "marks": 5,
        "passage_id": 1,
        "type_specific_data": {
            "table_structure": {
                "headers": ["Col1", "Col2"],
                "rows": [["A", "B"], ["C", "D"]]
            }
        },
        "answer_data": {
            "blanks": {"BLANK_1": ["answer"]}
        }
    }
    
    question_create = ReadingQuestionCreate(**create_data)
    assert question_create.type_specific_data == create_data["type_specific_data"]
    assert question_create.answer_data == create_data["answer_data"]
    
    # Test Update Schema
    update_data = {
        "type_specific_data": {
            "table_structure": {
                "headers": ["New Col"],
                "rows": [["New Val"]]
            }
        }
    }
    
    question_update = ReadingQuestionUpdate(**update_data)
    assert question_update.type_specific_data == update_data["type_specific_data"]
    
    # Test Response Schema
    response_data = {
        "id": 1,
        "passage_id": 1,
        "question_number": 1,
        "question_type": "reading_table_completion",
        "question_text": "Complete the table below.",
        "order": 1,
        "has_options": False,
        "marks": 5,
        "type_specific_data": create_data["type_specific_data"],
        "answer_data": create_data["answer_data"]
    }
    
    question_response = ReadingQuestionResponse(**response_data)
    assert question_response.type_specific_data == create_data["type_specific_data"]
    assert question_response.answer_data == create_data["answer_data"]
    
    print("All schema tests passed!")

if __name__ == "__main__":
    test_reading_question_schema_with_json_fields()
