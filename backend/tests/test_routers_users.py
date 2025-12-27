import pytest
from app.models import User

@pytest.fixture
def student_token(client, user_factory):
    user_factory(email="student_me@example.com", password="password123", role="student", full_name="Student User")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "student_me@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

@pytest.fixture
def admin_token(client, user_factory):
    user_factory(email="admin_user@example.com", password="password123", role="admin", full_name="Admin User")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "admin_user@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

def test_get_current_user(client, student_token):
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "student_me@example.com"
    assert data["role"] == "student"

def test_update_current_user(client, student_token):
    response = client.put(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"full_name": "Updated Name", "phone": "1234567890"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Updated Name"
    assert data["phone"] == "1234567890"

def test_change_password(client, student_token, db):
    # Change password
    response = client.post(
        "/api/v1/users/me/change-password",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"old_password": "password123", "new_password": "newpassword123"}
    )
    assert response.status_code == 200
    
    # Verify login with new password
    login_response = client.post(
        "/api/v1/auth/token",
        data={"username": "student_me@example.com", "password": "newpassword123"}
    )
    assert login_response.status_code == 200
    
    # Verify old password fails
    fail_response = client.post(
        "/api/v1/auth/token",
        data={"username": "student_me@example.com", "password": "password123"}
    )
    assert fail_response.status_code == 401

def test_user_profile_lifecycle(client, student_token):
    # 1. Create Profile
    create_response = client.post(
        "/api/v1/users/me/profile",
        headers={"Authorization": f"Bearer {student_token}"},
        json={
            "target_band_score": 7.5,
            "preparation_level": "Intermediate",
            "preferred_test_type": "academic"
        }
    )
    assert create_response.status_code == 201
    
    # 2. Get Profile
    get_response = client.get(
        "/api/v1/users/me/profile",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert get_response.status_code == 200
    assert get_response.json()["target_band_score"] == 7.5
    
    # 3. Update Profile
    update_response = client.put(
        "/api/v1/users/me/profile",
        headers={"Authorization": f"Bearer {student_token}"},
        json={"target_band_score": 8.0}
    )
    assert update_response.status_code == 200
    assert update_response.json()["target_band_score"] == 8.0
    
    # 4. Delete Profile
    delete_response = client.delete(
        "/api/v1/users/me/profile",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert delete_response.status_code == 204
    
    # Verify deleted
    get_again = client.get(
        "/api/v1/users/me/profile",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert get_again.status_code == 404

def test_admin_get_users(client, admin_token, user_factory):
    # Create some users
    user_factory(email="u1@test.com", role="student")
    user_factory(email="u2@test.com", role="teacher")
    
    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3 # admin + 2 created

def test_admin_create_delete_user(client, admin_token):
    # Create
    create_response = client.post(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "email": "created_by_admin@test.com",
            "password": "password123",
            "full_name": "Created User",
            "role": "student"
        }
    )
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]
    
    # Get by ID
    get_response = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_response.status_code == 200
    
    # Delete
    delete_response = client.delete(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert delete_response.status_code == 204
    
    # Verify deleted
    get_again = client.get(
        f"/api/v1/users/{user_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_again.status_code == 404

def test_get_student_stats(client, student_token):
    response = client.get(
        "/api/v1/users/me/stats",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "tests_completed" in data
    assert "average_score" in data
