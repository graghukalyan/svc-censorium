"""Custom exceptions for the annotation platform."""
from typing import Optional, Dict, Any


class BaseAPIException(Exception):
    """Base exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(BaseAPIException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, resource_id: str):
        message = f"{resource} with id '{resource_id}' not found"
        super().__init__(message, status_code=404, details={"resource": resource, "id": resource_id})


class TaskNotFoundException(NotFoundException):
    """Exception for task not found."""
    
    def __init__(self, task_id: str):
        super().__init__("Task", task_id)


class WorkerNotFoundException(NotFoundException):
    """Exception for worker not found."""
    
    def __init__(self, worker_id: str):
        super().__init__("Worker", worker_id)


class AssignmentNotFoundException(NotFoundException):
    """Exception for assignment not found."""
    
    def __init__(self, assignment_id: str):
        super().__init__("Assignment", assignment_id)


class ValidationException(BaseAPIException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=422, details=details)


class InvalidStateTransitionException(BaseAPIException):
    """Exception for invalid task state transitions."""
    
    def __init__(self, current_state: str, target_state: str):
        message = f"Invalid state transition from '{current_state}' to '{target_state}'"
        super().__init__(
            message,
            status_code=400,
            details={"current_state": current_state, "target_state": target_state}
        )


class UnauthorizedAnnotationException(BaseAPIException):
    """Exception for unauthorized annotation attempts."""
    
    def __init__(self, worker_id: str, task_id: str):
        message = f"Worker '{worker_id}' is not assigned to task '{task_id}'"
        super().__init__(
            message,
            status_code=403,
            details={"worker_id": worker_id, "task_id": task_id}
        )


class DuplicateAssignmentException(BaseAPIException):
    """Exception for duplicate task assignments."""
    
    def __init__(self, task_id: str, worker_id: str):
        message = f"Task '{task_id}' is already assigned to worker '{worker_id}'"
        super().__init__(
            message,
            status_code=409,
            details={"task_id": task_id, "worker_id": worker_id}
        )


class DuplicateEmailException(BaseAPIException):
    """Exception for duplicate email addresses."""
    
    def __init__(self, email: str):
        message = f"Worker with email '{email}' already exists"
        super().__init__(
            message,
            status_code=409,
            details={"email": email}
        )


class TaskAlreadyCompletedException(BaseAPIException):
    """Exception for operations on completed tasks."""
    
    def __init__(self, task_id: str):
        message = f"Task '{task_id}' is already completed"
        super().__init__(
            message,
            status_code=400,
            details={"task_id": task_id}
        )
