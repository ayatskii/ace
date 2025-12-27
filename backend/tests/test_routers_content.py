import pytest
from app.models import TestSection

@pytest.fixture
def admin_token(client, user_factory):
    user_factory(email="admin_content@example.com", password="password123", role="admin")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin_content@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def test_section(db, test_template_factory):
    template = test_template_factory()
    return template.sections[0] # Usually listening

@pytest.fixture
def reading_section(db, test_template_factory):
    template = test_template_factory()
    return next(s for s in template.sections if s.section_type == "reading")

@pytest.fixture
def writing_section(db, test_template_factory):
    template = test_template_factory()
    return next(s for s in template.sections if s.section_type == "writing")

@pytest.fixture
def speaking_section(db, test_template_factory):
    template = test_template_factory()
    return next(s for s in template.sections if s.section_type == "speaking")

# --- Listening Tests ---
def test_create_listening_part(client, admin_token, test_section):
    response = client.post(
        "/api/v1/listening/parts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "section_id": test_section.id,
            "part_number": 2,
            "audio_url": "http://test.com/audio.mp3",
            "transcript": "Test transcript"
        }
    )
    assert response.status_code == 201
    assert response.json()["part_number"] == 2

def test_create_listening_question(client, admin_token, test_section):
    # Create part first
    part_res = client.post(
        "/api/v1/listening/parts",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "section_id": test_section.id,
            "part_number": 1,
            "audio_url": "http://test.com/audio.mp3"
        }
    )
    part_id = part_res.json()["id"]
    
    response = client.post(
        "/api/v1/listening/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "question": {
                "section_id": test_section.id,
                "part_id": part_id,
                "question_number": 1,
                "question_type": "listening_multiple_choice",
                "question_text": "What is the answer?",
                "order": 1,
                "options": [{"option_label": "A", "option_text": "Option A"}, {"option_label": "B", "option_text": "Option B"}]
            },
            "answer": {
                "correct_answer": "A"
            }
        }
    )
    assert response.status_code == 201
    assert response.json()["question_text"] == "What is the answer?"

# --- Reading Tests ---
def test_create_reading_passage(client, admin_token, reading_section):
    response = client.post(
        "/api/v1/reading/passages",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "section_id": reading_section.id,
            "passage_number": 1,
            "title": "Test Passage",
            "content": "This is a test passage content.",
            "order": 1
        }
    )
    assert response.status_code == 201
    assert response.json()["word_count"] == 6

def test_create_reading_question(client, admin_token, reading_section):
    # Create passage
    pass_res = client.post(
        "/api/v1/reading/passages",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "section_id": reading_section.id,
            "passage_number": 1,
            "title": "Passage 1",
            "content": "Content",
            "order": 1
        }
    )
    passage_id = pass_res.json()["id"]
    
    response = client.post(
        "/api/v1/reading/questions",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "question": {
                "passage_id": passage_id,
                "question_number": 1,
                "question_type": "reading_true_false_not_given",
                "question_text": "Is this true?",
                "order": 1
            },
            "answer": {
                "correct_answer": "TRUE"
            }
        }
    )
    assert response.status_code == 201

# --- Writing Tests ---
def test_create_writing_task(client, admin_token, writing_section):
    response = client.post(
        "/api/v1/writing/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "section_id": writing_section.id,
            "task_number": 1,
            "task_type": "writing_task1_academic",
            "prompt_text": "Describe the chart.",
            "word_limit_min": 150,
            "time_limit_minutes": 20
        }
    )
    assert response.status_code == 201
    assert response.json()["task_number"] == 1

# --- Speaking Tests ---
def test_create_speaking_task(client, admin_token, speaking_section):
    response = client.post(
        "/api/v1/speaking/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "section_id": speaking_section.id,
            "part_number": 1,
            "task_type": "speaking_part1",
            "prompt_text": "Introduction",
            "speaking_time_seconds": 300,
            "order": 1
        }
    )
    assert response.status_code == 201
    assert response.json()["part_number"] == 1
