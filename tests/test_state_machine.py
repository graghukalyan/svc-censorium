"""Tests for state machine and state transitions."""
import pytest
from app.db.models import TaskStatus, ALLOWED_TRANSITIONS
from app.services.task_service import TaskService
from app.core.exceptions import InvalidStateTransitionException


def test_allowed_transitions_definition():
    """Test that allowed transitions are properly defined."""
    assert TaskStatus.PENDING in ALLOWED_TRANSITIONS
    assert TaskStatus.IN_PROGRESS in ALLOWED_TRANSITIONS[TaskStatus.PENDING]
    assert TaskStatus.COMPLETED in ALLOWED_TRANSITIONS[TaskStatus.IN_PROGRESS]
    assert len(ALLOWED_TRANSITIONS[TaskStatus.COMPLETED]) == 0


def test_valid_transition_pending_to_in_progress(db, sample_task):
    """Test valid transition from PENDING to IN_PROGRESS."""
    service = TaskService(db)
    
    assert sample_task.status == TaskStatus.PENDING
    
    updated_task = service.update_task_status(sample_task.id, TaskStatus.IN_PROGRESS)
    
    assert updated_task.status == TaskStatus.IN_PROGRESS


def test_valid_transition_in_progress_to_completed(db, sample_task):
    """Test valid transition from IN_PROGRESS to COMPLETED."""
    service = TaskService(db)
    
    # First move to IN_PROGRESS
    service.update_task_status(sample_task.id, TaskStatus.IN_PROGRESS)
    
    # Then move to COMPLETED
    updated_task = service.update_task_status(sample_task.id, TaskStatus.COMPLETED)
    
    assert updated_task.status == TaskStatus.COMPLETED


def test_invalid_transition_pending_to_completed(db, sample_task):
    """Test invalid transition from PENDING directly to COMPLETED."""
    service = TaskService(db)
    
    assert sample_task.status == TaskStatus.PENDING
    
    with pytest.raises(InvalidStateTransitionException) as exc_info:
        service.update_task_status(sample_task.id, TaskStatus.COMPLETED)
    
    assert "PENDING" in str(exc_info.value)
    assert "COMPLETED" in str(exc_info.value)


def test_invalid_transition_from_completed(db, sample_task):
    """Test that no transitions are allowed from COMPLETED state."""
    service = TaskService(db)
    
    # Move to COMPLETED
    service.update_task_status(sample_task.id, TaskStatus.IN_PROGRESS)
    service.update_task_status(sample_task.id, TaskStatus.COMPLETED)
    
    # Try to transition back
    with pytest.raises(InvalidStateTransitionException):
        service.update_task_status(sample_task.id, TaskStatus.IN_PROGRESS)


def test_transition_validation_can_be_bypassed(db, sample_task):
    """Test that transition validation can be bypassed when needed."""
    service = TaskService(db)
    
    # This would normally fail, but we bypass validation
    updated_task = service.update_task_status(
        sample_task.id,
        TaskStatus.COMPLETED,
        validate_transition=False
    )
    
    assert updated_task.status == TaskStatus.COMPLETED


def test_helper_methods_for_transitions(db, sample_task):
    """Test convenience methods for specific transitions."""
    service = TaskService(db)
    
    # Test transition_to_in_progress
    task = service.transition_to_in_progress(sample_task.id)
    assert task.status == TaskStatus.IN_PROGRESS
    
    # Test transition_to_completed
    task = service.transition_to_completed(sample_task.id)
    assert task.status == TaskStatus.COMPLETED
