import pytest
from app.models import WritingSubmission, SpeakingSubmission, TestAttempt

@pytest.fixture
def teacher_token(client, user_factory):
    user_factory(email="teacher@example.com", password="password123", role="teacher", full_name="Teacher User")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "teacher@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

def test_get_grading_queue(client, teacher_token, submission_factory):
    # Create pending submissions
    submission_factory(submission_type="writing", status="pending")
    submission_factory(submission_type="speaking", status="pending")
    
    response = client.get(
        "/api/v1/grading/queue",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["pending_writing"] >= 1
    assert data["pending_speaking"] >= 1
    assert len(data["recent_submissions"]) >= 2

def test_get_grading_stats(client, teacher_token):
    response = client.get(
        "/api/v1/grading/stats",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "graded_today" in data
    assert "avg_grading_time" in data

def test_grade_writing_submission(client, teacher_token, submission_factory, db):
    # Create pending submission
    submission = submission_factory(submission_type="writing", status="pending")
    
    # Grade it
    response = client.post(
        f"/api/v1/grading/writing/{submission.id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "task_achievement_score": 7.0,
            "coherence_cohesion_score": 6.5,
            "lexical_resource_score": 7.0,
            "grammatical_range_score": 6.5,
            "feedback_text": "Good job!"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["overall_band_score"] == 7.0 # (7+6.5+7+6.5)/4 = 6.75 -> 7.0
    
    # Verify submission status updated
    db.refresh(submission)
    assert submission.status == "graded"
    assert submission.assigned_teacher_id is not None

def test_grade_speaking_submission(client, teacher_token, submission_factory, db):
    # Create pending submission
    submission = submission_factory(submission_type="speaking", status="pending")
    
    # Grade it
    response = client.post(
        f"/api/v1/grading/speaking/{submission.id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "fluency_coherence_score": 6.0,
            "lexical_resource_score": 6.0,
            "grammatical_range_score": 6.0,
            "pronunciation_score": 6.0,
            "feedback_text": "Speak clearer."
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["overall_band_score"] == 6.0
    
    # Verify submission status updated
    db.refresh(submission)
    assert submission.status == "graded"

def test_get_grading_history(client, teacher_token, submission_factory):
    # Create and grade a submission (we can reuse the grade endpoint or do it manually)
    # Let's use the API to ensure history picks it up
    submission = submission_factory(submission_type="writing", status="pending")
    client.post(
        f"/api/v1/grading/writing/{submission.id}",
        headers={"Authorization": f"Bearer {teacher_token}"},
        json={
            "task_achievement_score": 7.0,
            "coherence_cohesion_score": 7.0,
            "lexical_resource_score": 7.0,
            "grammatical_range_score": 7.0,
            "feedback_text": "History check"
        }
    )
    
    response = client.get(
        "/api/v1/grading/history",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["submission_id"] == submission.id

def test_teacher_workload(client, teacher_token, submission_factory):
    # Create pending
    submission_factory(submission_type="writing", status="pending")
    
    response = client.get(
        "/api/v1/grading/workload",
        headers={"Authorization": f"Bearer {teacher_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["pending_writing"] >= 1
