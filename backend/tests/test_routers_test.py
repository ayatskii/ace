import pytest

@pytest.fixture
def admin_token(client, user_factory):
    user_factory(email="admin@example.com", password="password123", role="admin", full_name="Admin User")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def student_token(client, user_factory):
    user_factory(email="student@example.com", password="password123", role="student", full_name="Student User")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "student@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

def test_create_test_template(client, admin_token):
    response = client.post(
        "/api/v1/tests/templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "IELTS Mock Test 1",
            "description": "A full mock test",
            "test_type": "ACADEMIC",
            "duration_minutes": 180
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "IELTS Mock Test 1"
    assert data["id"] is not None

def test_get_tests_list(client, admin_token):
    # Create a test
    client.post(
        "/api/v1/tests/templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Test 1",
            "test_type": "ACADEMIC",
            "duration_minutes": 180
        }
    )
    
    response = client.get(
        "/api/v1/tests/templates",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1

def test_create_test_section(client, admin_token):
    # Create test
    test_res = client.post(
        "/api/v1/tests/templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Test 1", "test_type": "ACADEMIC", "duration_minutes": 180}
    )
    test_id = test_res.json()["id"]
    
    # Create section
    response = client.post(
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
    assert response.status_code == 201
    data = response.json()
    assert data["test_template_id"] == test_id

def test_get_test_details(client, admin_token):
    # Create test
    test_res = client.post(
        "/api/v1/tests/templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Test 1", "test_type": "ACADEMIC", "duration_minutes": 180}
    )
    test_id = test_res.json()["id"]
    
    response = client.get(
        f"/api/v1/tests/templates/{test_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test 1"

def test_delete_test(client, admin_token):
    # Create test
    test_res = client.post(
        "/api/v1/tests/templates",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"title": "Test to Delete", "test_type": "ACADEMIC", "duration_minutes": 180}
    )
    test_id = test_res.json()["id"]
    
    # Delete
    response = client.delete(
        f"/api/v1/tests/templates/{test_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 204
    
    # Verify deleted
    get_res = client.get(
        f"/api/v1/tests/templates/{test_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_res.status_code == 404
