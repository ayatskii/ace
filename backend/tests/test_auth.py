import pytest
from app.core.security import verify_password, get_password_hash
from app.models import User

def test_login_user(client, user_factory):
    # Create user directly
    user_factory(email="test@example.com", password="password123")
    
    # Login
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, user_factory):
    # Create user directly
    user_factory(email="test@example.com", password="password123")
    
    # Login with wrong password
    response = client.post(
        "/api/v1/auth/token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]

def test_get_current_user(client, user_factory):
    # Create user directly
    user_factory(email="test@example.com", password="password123")
    
    # Login to get token
    login_res = client.post(
        "/api/v1/auth/token",
        data={
            "username": "test@example.com",
            "password": "password123"
        }
    )
    token = login_res.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

def test_refresh_token(client, user_factory):
    # Create user
    user_factory(email="test_refresh@example.com", password="password123")
    
    # Login first
    login_res = client.post(
        "/api/v1/auth/token",
        data={"username": "test_refresh@example.com", "password": "password123"}
    )
    token = login_res.json()["access_token"]
    
    # Refresh
    response = client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_forgot_password(client, user_factory):
    user_factory(email="test_forgot@example.com")
    
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "test_forgot@example.com"}
    )
    assert response.status_code == 200
    assert "reset link" in response.json()["message"]

def test_forgot_password_unknown_email(client):
    response = client.post(
        "/api/v1/auth/forgot-password",
        json={"email": "unknown@example.com"}
    )
    assert response.status_code == 200 # Should still return 200 for security

def test_reset_password_flow(client, user_factory):
    user = user_factory(email="test_reset@example.com", password="oldpassword")
    
    # 1. Get reset token (simulated by generating one manually as we can't intercept print)
    from app.core.security import create_access_token
    from datetime import timedelta
    
    reset_token = create_access_token(
        data={"sub": str(user.id), "type": "reset"},
        expires_delta=timedelta(minutes=15)
    )
    
    # 2. Reset password
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": reset_token, "new_password": "newpassword123"}
    )
    assert response.status_code == 200
    
    # 3. Verify login with new password
    login_res = client.post(
        "/api/v1/auth/token",
        data={"username": "test_reset@example.com", "password": "newpassword123"}
    )
    assert login_res.status_code == 200

def test_reset_password_invalid_token(client):
    response = client.post(
        "/api/v1/auth/reset-password",
        json={"token": "invalid_token", "new_password": "newpassword123"}
    )
    assert response.status_code == 400
