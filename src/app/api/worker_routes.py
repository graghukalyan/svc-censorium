"""Worker API routes."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.req import CreateWorkerRequest
from app.models.resp import WorkerResponse, WorkerTasksResponse, TaskResponse
from app.services.worker_service import WorkerService
from app.services.assignment_service import AssignmentService

router = APIRouter(prefix="/workers", tags=["workers"])


@router.post("", response_model=WorkerResponse, status_code=status.HTTP_201_CREATED)
def create_worker(
    request: CreateWorkerRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new worker.
    
    - **name**: Worker's name
    - **email**: Worker's email (must be unique)
    """
    worker_service = WorkerService(db)
    worker = worker_service.create_worker(
        name=request.name,
        email=request.email
    )
    
    return WorkerResponse.from_orm(worker)


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(
    worker_id: str,
    db: Session = Depends(get_db)
):
    """
    Get worker details.
    
    - **worker_id**: ID of the worker
    """
    worker_service = WorkerService(db)
    worker = worker_service.get_worker(worker_id)
    
    return WorkerResponse.from_orm(worker)


@router.get("/{worker_id}/tasks", response_model=WorkerTasksResponse)
def get_worker_tasks(
    worker_id: str,
    status: str = None,
    db: Session = Depends(get_db)
):
    """
    Get all tasks assigned to a worker.
    
    - **worker_id**: ID of the worker
    - **status**: Optional filter by task status (PENDING, IN_PROGRESS, COMPLETED)
    """
    worker_service = WorkerService(db)
    assignment_service = AssignmentService(db)
    
    # Validate worker exists
    worker = worker_service.get_worker(worker_id)
    
    # Get worker's assignments
    assignments = assignment_service.get_worker_assignments(worker_id, status)
    
    # Build response
    tasks = [TaskResponse.from_orm(a.task) for a in assignments]
    
    return WorkerTasksResponse(
        worker_id=worker.id,
        worker_name=worker.name,
        tasks=tasks,
        total=len(tasks)
    )
