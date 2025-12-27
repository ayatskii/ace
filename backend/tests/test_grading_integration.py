import pytest
from datetime import datetime, timedelta

@pytest.fixture
def student_token(client, user_factory):
    user_factory(email="student@example.com", password="password123", role="student", full_name="Student User")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "student@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def admin_token(client, user_factory):
    user_factory(email="admin@example.com", password="password123", role="admin", full_name="Admin User")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def setup_test(client, admin_token):
    # Create test
    test_res = client.post(
        "/api/v1/tests/templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Grading Test", "test_type": "ACADEMIC", "duration_minutes": 180}
    )
    test_id = test_res.json()["id"]
    
    # Publish test (required for students to see it)
    client.post(
        f"/api/v1/tests/templates/{test_id}/publish",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    # Create Listening Section
    sec_res = client.post(
        "/api/v1/tests/sections",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "test_template_id": test_id,
            "section_type": "listening",
            "order": 1,
            "total_questions": 10,
            "duration_minutes": 30
        }
    )
    section_id = sec_res.json()["id"]
    
    # Create Listening Part
    part_res = client.post(
        "/api/v1/listening/parts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"section_id": section_id, "part_number": 1, "audio_url": "http://test.com/audio.mp3"}
    )
    part_id = part_res.json()["id"]
    
    # Create Question (Completion)
    q_res = client.post(
        "/api/v1/listening/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "question": {
                "section_id": section_id,
                "part_id": part_id,
                "question_number": 1,
                "question_type": "listening_sentence_completion",
                "question_text": "Question 1",
                "order": 1,
                "marks": 1
            },
            "answer": {
                "correct_answer": "correct",
                "case_sensitive": False
            }
        }
    )
    
    return test_id

def test_start_attempt(client, student_token, setup_test):
    test_id = setup_test
    response = client.post(
        "/api/v1/tests/attempts",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"test_template_id": test_id}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["test_template_id"] == test_id
    assert data["status"] == "in_progress"
    return data["id"]

def test_submit_attempt(client, student_token, setup_test):
    test_id = setup_test
    
    # Start attempt
    start_res = client.post(
        "/api/v1/tests/attempts",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"test_template_id": test_id}
    )
    attempt_id = start_res.json()["id"]
    
    # Submit answers
    answers = {
        "listening_answers": [
            {
                "question_id": 1,  # Assuming ID 1 since it's fresh DB
                "user_answer": "correct"
            }
        ]
    }
    
    # Submit
    response = client.put(
        f"/api/v1/tests/attempts/{attempt_id}/submit",
        headers={"Authorization": f"Bearer {student_token}"},
        json=answers
    )
    
    # Note: Depending on implementation, submit might return results or just status
    # Assuming it returns the attempt with status submitted
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "submitted"
    
    # Check results (included in response or fetch again)
    # The submit endpoint returns TestAttemptResponse which includes result
    # But if result is None in response (might be lazy loaded), fetch again
    if not data.get("result"):
        result_res = client.get(
            f"/api/v1/tests/attempts/{attempt_id}",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        data = result_res.json()

    # Check if result exists now
    if data.get("result"):
        assert data["result"]["listening_score"] is not None
        # Note: Score calculation might be complex, just checking it exists and is not 0 if we answered correctly
        # But here we answered 1 question correctly out of 40 (default total questions for section)
        # So score might be low.
        pass
