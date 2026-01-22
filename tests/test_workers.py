"""Tests for worker endpoints."""
import pytest
from fastapi import status


def test_create_worker(client):
    """Test creating a new worker."""
    response = client.post(
        "/workers",
        json={"name": "John Doe", "email": "john@example.com"}
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "John Doe"
    assert data["email"] == "john@example.com"
    assert "id" in data
    assert "created_at" in data


def test_create_worker_duplicate_email(client, sample_worker):
    """Test creating worker with duplicate email fails."""
    response = client.post(
        "/workers",
        json={"name": "Duplicate", "email": sample_worker.email}
    )
    
    assert response.status_code == status.HTTP_409_CONFLICT
    data = response.json()
    assert "already exists" in data["message"]


def test_create_worker_invalid_email(client):
    """Test creating worker with invalid email fails."""
    response = client.post(
        "/workers",
        json={"name": "Invalid", "email": "not-an-email"}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


def test_get_worker(client, sample_worker):
    """Test getting worker by ID."""
    response = client.get(f"/workers/{sample_worker.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_worker.id
    assert data["name"] == sample_worker.name
    assert data["email"] == sample_worker.email


def test_get_worker_not_found(client):
    """Test getting non-existent worker."""
    response = client.get("/workers/nonexistent-id")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_worker_tasks_empty(client, sample_worker):
    """Test getting tasks for worker with no assignments."""
    response = client.get(f"/workers/{sample_worker.id}/tasks")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["worker_id"] == sample_worker.id
    assert data["tasks"] == []
    assert data["total"] == 0


def test_get_worker_tasks_with_assignments(client, sample_worker, sample_task):
    """Test getting tasks for worker with assignments."""
    # Assign task to worker
    assign_response = client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    assert assign_response.status_code == status.HTTP_200_OK
    
    # Get worker tasks
    response = client.get(f"/workers/{sample_worker.id}/tasks")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["total"] == 1
    assert len(data["tasks"]) == 1
    assert data["tasks"][0]["id"] == sample_task.id
