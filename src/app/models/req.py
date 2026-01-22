"""Request models (Pydantic schemas)."""
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Any, Optional


class BaseRequest(BaseModel):
    """Base request model."""
    pass


# Worker requests
class CreateWorkerRequest(BaseRequest):
    """Request model for creating a worker."""
    name: str = Field(..., description="Worker name", min_length=1, max_length=255)
    email: EmailStr = Field(..., description="Worker email address")


# Task requests
class CreateTaskRequest(BaseRequest):
    """Request model for creating an annotation task."""
    input_payload: Dict[str, Any] = Field(..., description="Opaque JSON payload for annotation")
    worker_id: str = Field(..., description="ID of worker creating the task")


class AssignTaskRequest(BaseRequest):
    """Request model for assigning a task to a worker."""
    worker_id: str = Field(..., description="ID of worker to assign task to")


class SubmitAnnotationRequest(BaseRequest):
    """Request model for submitting an annotation."""
    worker_id: str = Field(..., description="ID of worker submitting annotation")
    result: Dict[str, Any] = Field(..., description="Annotation result data")


# Query parameters
class TaskQueryParams(BaseModel):
    """Query parameters for listing tasks."""
    status: Optional[str] = Field(None, description="Filter by task status")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")
