"""Response models (Pydantic schemas)."""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model."""
    
    class Config:
        from_attributes = True  # Allows creation from ORM models


# Worker responses
class WorkerResponse(BaseResponse):
    """Response model for worker data."""
    id: str
    name: str
    email: str
    created_at: datetime


# Assignment responses
class AssignmentResponse(BaseResponse):
    """Response model for assignment data."""
    id: str
    task_id: str
    worker_id: str
    assigned_at: datetime
    status: str


class AssignmentDetailResponse(AssignmentResponse):
    """Detailed assignment response with worker info."""
    worker_name: str
    worker_email: str


# Annotation responses
class AnnotationResponse(BaseResponse):
    """Response model for annotation data."""
    id: str
    task_id: str
    worker_id: str
    assignment_id: str
    result: Dict[str, Any]
    version: int
    submitted_at: datetime
    is_latest: bool


class AnnotationWithWorkerResponse(AnnotationResponse):
    """Annotation response with worker details."""
    worker_name: str
    worker_email: str


# Task responses
class TaskResponse(BaseResponse):
    """Response model for task data."""
    id: str
    input_payload: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime
    created_by: str


class TaskWithAssignmentsResponse(TaskResponse):
    """Task response with assignment information."""
    assigned_workers: List[str] = Field(default_factory=list, description="List of worker IDs assigned to this task")


class TaskDetailResponse(TaskResponse):
    """Detailed task response with all relationships."""
    creator_name: str
    creator_email: str
    assignments: List[AssignmentDetailResponse] = Field(default_factory=list)
    annotations: List[AnnotationWithWorkerResponse] = Field(default_factory=list)
    latest_annotation: Optional[AnnotationWithWorkerResponse] = None


# List responses
class TaskListResponse(BaseResponse):
    """Response model for paginated task list."""
    tasks: List[TaskWithAssignmentsResponse]
    total: int
    skip: int
    limit: int


class WorkerTasksResponse(BaseResponse):
    """Response model for worker's assigned tasks."""
    worker_id: str
    worker_name: str
    tasks: List[TaskResponse]
    total: int


# Error responses
class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error type/code")
    message: str = Field(..., description="Human-readable error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# Success responses
class SuccessResponse(BaseModel):
    """Generic success response."""
    success: bool = True
    message: str
    data: Optional[Dict[str, Any]] = None
