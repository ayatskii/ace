import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client(db):
    from app.database import get_db
    def override_get_db():
        try:
            yield db
        finally:
            pass
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture
def student_token(client, user_factory):
    user_factory(email="uploader@example.com", password="password123", role="student")
    response = client.post(
        "/api/v1/auth/token",
        data={"username": "uploader@example.com", "password": "password123"}
    )
    return response.json()["access_token"]

@patch("app.routers.upload.open")
@patch("app.routers.upload.Path.mkdir")
def test_upload_audio(mock_mkdir, mock_open, client, student_token):
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    
    files = {"file": ("test.mp3", b"audio content", "audio/mpeg")}
    response = client.post(
        "/api/v1/upload/audio",
        headers={"Authorization": f"Bearer {student_token}"},
        files=files
    )
    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["url"].startswith("/uploads/audio/")

@patch("app.routers.upload.open")
@patch("app.routers.upload.Path.mkdir")
def test_upload_image(mock_mkdir, mock_open, client, student_token):
    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file
    
    files = {"file": ("test.png", b"image content", "image/png")}
    response = client.post(
        "/api/v1/upload/image",
        headers={"Authorization": f"Bearer {student_token}"},
        files=files
    )
    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["url"].startswith("/uploads/images/")

def test_upload_invalid_type(client, student_token):
    files = {"file": ("test.txt", b"text content", "text/plain")}
    response = client.post(
        "/api/v1/upload/audio",
        headers={"Authorization": f"Bearer {student_token}"},
        files=files
    )
    assert response.status_code == 400
    assert "File must be audio" in response.json()["detail"]

@patch("app.routers.upload.Path.exists")
@patch("app.routers.upload.Path.iterdir")
def test_get_files(mock_iterdir, mock_exists, client, student_token):
    mock_exists.return_value = True
    
    # Mock file object
    mock_file = MagicMock()
    mock_file.is_file.return_value = True
    mock_file.name = "test.mp3"
    mock_file.stat.return_value.st_size = 1024
    mock_file.stat.return_value.st_ctime = 1000000
    
    mock_iterdir.return_value = [mock_file]
    
    response = client.get(
        "/api/v1/upload/files?type=audio",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "test.mp3"

@patch("app.routers.upload.os.remove")
@patch("app.routers.upload.Path.exists")
def test_delete_file(mock_exists, mock_remove, client, student_token):
    mock_exists.return_value = True
    
    response = client.delete(
        "/api/v1/upload/files/audio/test.mp3",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "File deleted"
    mock_remove.assert_called_once()

@patch("app.routers.upload.Path.exists")
def test_delete_file_not_found(mock_exists, client, student_token):
    mock_exists.return_value = False
    
    response = client.delete(
        "/api/v1/upload/files/audio/missing.mp3",
        headers={"Authorization": f"Bearer {student_token}"}
    )
    assert response.status_code == 404
