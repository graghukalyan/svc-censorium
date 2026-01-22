"""Tests for task endpoints and state transitions."""
import pytest
from fastapi import status


def test_create_task(client, sample_worker):
    """Test creating a new task."""
    response = client.post(
        "/tasks",
        json={
            "input_payload": {"text": "Please annotate this", "type": "classification"},
            "worker_id": sample_worker.id
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["status"] == "PENDING"
    assert data["input_payload"]["text"] == "Please annotate this"
    assert data["created_by"] == sample_worker.id
    assert "id" in data


def test_create_task_invalid_worker(client):
    """Test creating task with non-existent worker fails."""
    response = client.post(
        "/tasks",
        json={
            "input_payload": {"text": "Test"},
            "worker_id": "nonexistent-worker"
        }
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_task(client, sample_task):
    """Test getting task details."""
    response = client.get(f"/tasks/{sample_task.id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_task.id
    assert data["status"] == "PENDING"
    assert "creator_name" in data
    assert "assignments" in data
    assert "annotations" in data


def test_get_task_not_found(client):
    """Test getting non-existent task."""
    response = client.get("/tasks/nonexistent-id")
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_assign_task(client, sample_task, sample_worker):
    """Test assigning a task to a worker."""
    response = client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == sample_task.id
    assert data["status"] == "IN_PROGRESS"  # Should transition to IN_PROGRESS
    assert sample_worker.id in data["assigned_workers"]


def test_assign_task_duplicate(client, sample_task, sample_worker):
    """Test assigning same task to same worker twice fails."""
    # First assignment
    response1 = client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    assert response1.status_code == status.HTTP_200_OK
    
    # Duplicate assignment
    response2 = client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    assert response2.status_code == status.HTTP_409_CONFLICT


def test_assign_task_invalid_worker(client, sample_task):
    """Test assigning task to non-existent worker fails."""
    response = client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": "nonexistent-worker"}
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_submit_annotation(client, sample_task, sample_worker):
    """Test submitting an annotation."""
    # First assign the task
    assign_response = client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    assert assign_response.status_code == status.HTTP_200_OK
    
    # Submit annotation
    response = client.post(
        f"/tasks/{sample_task.id}/annotate",
        json={
            "worker_id": sample_worker.id,
            "result": {"label": "positive", "confidence": 0.95}
        }
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["task_id"] == sample_task.id
    assert data["worker_id"] == sample_worker.id
    assert data["version"] == 1
    assert data["is_latest"] is True
    assert data["result"]["label"] == "positive"


def test_submit_annotation_unauthorized(client, sample_task, sample_worker, another_worker):
    """Test submitting annotation without assignment fails."""
    # Assign to sample_worker
    assign_response = client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    assert assign_response.status_code == status.HTTP_200_OK
    
    # Try to submit as another_worker (not assigned)
    response = client.post(
        f"/tasks/{sample_task.id}/annotate",
        json={
            "worker_id": another_worker.id,
            "result": {"label": "negative"}
        }
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_submit_multiple_annotations_versioning(client, sample_task, sample_worker):
    """Test submitting multiple annotations creates versions."""
    # Assign task
    client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    
    # Submit first annotation
    response1 = client.post(
        f"/tasks/{sample_task.id}/annotate",
        json={
            "worker_id": sample_worker.id,
            "result": {"label": "positive", "version": 1}
        }
    )
    assert response1.status_code == status.HTTP_200_OK
    data1 = response1.json()
    assert data1["version"] == 1
    assert data1["is_latest"] is True
    
    # Get task to check it's completed
    task_response = client.get(f"/tasks/{sample_task.id}")
    assert task_response.json()["status"] == "COMPLETED"
    
    # Submit second annotation (revision)
    response2 = client.post(
        f"/tasks/{sample_task.id}/annotate",
        json={
            "worker_id": sample_worker.id,
            "result": {"label": "negative", "version": 2}
        }
    )
    assert response2.status_code == status.HTTP_200_OK
    data2 = response2.json()
    assert data2["version"] == 2
    assert data2["is_latest"] is True


def test_task_state_transitions(client, sample_task, sample_worker):
    """Test complete task state transition flow."""
    # Initial state: PENDING
    task = client.get(f"/tasks/{sample_task.id}").json()
    assert task["status"] == "PENDING"
    
    # Assign task: PENDING → IN_PROGRESS
    client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    task = client.get(f"/tasks/{sample_task.id}").json()
    assert task["status"] == "IN_PROGRESS"
    
    # Submit annotation: IN_PROGRESS → COMPLETED
    client.post(
        f"/tasks/{sample_task.id}/annotate",
        json={
            "worker_id": sample_worker.id,
            "result": {"label": "done"}
        }
    )
    task = client.get(f"/tasks/{sample_task.id}").json()
    assert task["status"] == "COMPLETED"


def test_cannot_assign_completed_task(client, sample_task, sample_worker, another_worker):
    """Test that completed tasks cannot be assigned to new workers."""
    # Assign and complete task
    client.post(f"/tasks/{sample_task.id}/assign", json={"worker_id": sample_worker.id})
    client.post(
        f"/tasks/{sample_task.id}/annotate",
        json={"worker_id": sample_worker.id, "result": {"done": True}}
    )
    
    # Try to assign completed task to another worker
    response = client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": another_worker.id}
    )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "already completed" in response.json()["message"]


def test_task_with_full_details(client, sample_task, sample_worker):
    """Test getting task with all relationships."""
    # Assign task
    client.post(
        f"/tasks/{sample_task.id}/assign",
        json={"worker_id": sample_worker.id}
    )
    
    # Submit annotation
    client.post(
        f"/tasks/{sample_task.id}/annotate",
        json={
            "worker_id": sample_worker.id,
            "result": {"label": "test", "score": 0.9}
        }
    )
    
    # Get full task details
    response = client.get(f"/tasks/{sample_task.id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == sample_task.id
    assert data["status"] == "COMPLETED"
    assert len(data["assignments"]) == 1
    assert len(data["annotations"]) == 1
    assert data["latest_annotation"] is not None
    assert data["latest_annotation"]["version"] == 1
    assert data["latest_annotation"]["result"]["label"] == "test"
