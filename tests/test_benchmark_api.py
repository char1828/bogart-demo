import pytest
from fastapi.testclient import TestClient
from app.main import app
from database.repository import media_repo

client = TestClient(app)

def test_config_endpoint():
    response = client.get("/api/config")
    assert response.status_code == 200
    data = response.json()
    assert "active_profile" in data
    assert "cloud_provider" in data
    assert "database_type" in data
    assert "storage_provider" in data

def test_records_option1_metadata_only():
    """Ensure Option 1 returns metadata only and does NOT expose the heavy BLOB."""
    response = client.get("/api/records?option=1")
    assert response.status_code == 200
    records = response.json()
    assert len(records) > 0
    first = records[0]
    assert "id" in first
    assert "name" in first
    assert "size" in first
    assert "img_type" in first
    assert "img_data" not in first  # Critical: never return BLOB in listing!

def test_records_option2_metadata_and_path():
    """Ensure Option 2 returns metadata and object storage path."""
    response = client.get("/api/records?option=2")
    assert response.status_code == 200
    records = response.json()
    assert len(records) > 0
    first = records[0]
    assert "id" in first
    assert "img_Path" in first
    assert first["img_Path"].startswith("local://") or first["img_Path"].startswith("gs://")

def test_image_fetch_option1_blob():
    """Ensure on-click fetch for Option 1 retrieves binary with latency header."""
    rec_res = client.get("/api/records?option=1")
    first_id = rec_res.json()[0]["id"]
    response = client.get(f"/api/image/{first_id}?option=1")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert "X-Response-Time-MS" in response.headers
    assert "X-Storage-Source" in response.headers
    assert len(response.content) > 0

def test_image_fetch_option2_storage():
    """Ensure on-click fetch for Option 2 retrieves binary with latency header."""
    rec_res = client.get("/api/records?option=2")
    first_id = rec_res.json()[0]["id"]
    response = client.get(f"/api/image/{first_id}?option=2")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert "X-Response-Time-MS" in response.headers
    assert "X-Storage-Source" in response.headers
    assert len(response.content) > 0
