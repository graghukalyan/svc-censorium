"""Task API routes."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.req import CreateTaskRequest, AssignTaskRequest, SubmitAnnotationRequest
from app.models.resp import (
    TaskResponse, TaskDetailResponse, TaskWithAssignmentsResponse,
    AnnotationResponse, AnnotationWithWorkerResponse, AssignmentDetailResponse
)
from app.services.task_service import TaskService
from app.services.assignment_service import AssignmentService
from app.services.annotation_service import AnnotationService
from app.core.exceptions import (
    BaseAPIException, UnauthorizedAnnotationException
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    request: CreateTaskRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new annotation task.
    
    - **input_payload**: Opaque JSON data to be annotated
    - **worker_id**: ID of the worker creating the task
    """
    task_service = TaskService(db)
    task = task_service.create_task(
        input_payload=request.input_payload,
        worker_id=request.worker_id
    )
    
    return TaskResponse.from_orm(task)


@router.post("/{task_id}/assign", response_model=TaskWithAssignmentsResponse)
def assign_task(
    task_id: str,
    request: AssignTaskRequest,
    db: Session = Depends(get_db)
):
    """
    Assign a task to a worker.
    
    - **task_id**: ID of the task to assign
    - **worker_id**: ID of the worker to assign to
    
    Transitions task from PENDING to IN_PROGRESS on first assignment.
    """
    task_service = TaskService(db)
    assignment_service = AssignmentService(db)
    
    # Validate task is not completed
    task_service.validate_task_not_completed(task_id)
    
    # Create assignment
    assignment = assignment_service.assign_task(task_id, request.worker_id)
    
    # Transition task to IN_PROGRESS if it's still PENDING
    task = task_service.get_task(task_id)
    if task.status.value == "PENDING":
        task = task_service.transition_to_in_progress(task_id)
    
    # Get updated task with assignments
    task = task_service.get_task_with_details(task_id)
    
    # Build response
    response = TaskWithAssignmentsResponse.from_orm(task)
    response.assigned_workers = [a.worker_id for a in task.assignments]
    
    return response


@router.post("/{task_id}/annotate", response_model=AnnotationResponse)
def submit_annotation(
    task_id: str,
    request: SubmitAnnotationRequest,
    db: Session = Depends(get_db)
):
    """
    Submit an annotation for a task.
    
    - **task_id**: ID of the task to annotate
    - **worker_id**: ID of the worker submitting annotation
    - **result**: Annotation result data (opaque JSON)
    
    Only assigned workers can submit annotations.
    Creates a new version for each submission.
    Transitions task to COMPLETED on submission.
    """
    task_service = TaskService(db)
    assignment_service = AssignmentService(db)
    annotation_service = AnnotationService(db)
    
    # Validate worker is assigned to this task
    try:
        assignment = assignment_service.validate_assignment(task_id, request.worker_id)
    except BaseAPIException:
        raise UnauthorizedAnnotationException(request.worker_id, task_id)
    
    # Submit annotation (creates new version)
    annotation = annotation_service.submit_annotation(
        task_id=task_id,
        worker_id=request.worker_id,
        assignment_id=assignment.id,
        result=request.result
    )
    
    # Transition task to COMPLETED
    task = task_service.get_task(task_id)
    if task.status.value == "IN_PROGRESS":
        task_service.transition_to_completed(task_id)
    
    # Update assignment status
    assignment_service.update_assignment_status(
        task_id, request.worker_id, task.status
    )
    
    return AnnotationResponse.from_orm(annotation)


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a task.
    
    - **task_id**: ID of the task
    
    Returns task with all assignments and annotations.
    """
    task_service = TaskService(db)
    annotation_service = AnnotationService(db)
    
    # Get task with relationships
    task = task_service.get_task_with_details(task_id)
    
    # Build response
    response = TaskDetailResponse(
        id=task.id,
        input_payload=task.input_payload,
        status=task.status.value,
        created_at=task.created_at,
        updated_at=task.updated_at,
        created_by=task.created_by,
        creator_name=task.creator.name,
        creator_email=task.creator.email,
        assignments=[
            AssignmentDetailResponse(
                id=a.id,
                task_id=a.task_id,
                worker_id=a.worker_id,
                assigned_at=a.assigned_at,
                status=a.status.value,
                worker_name=a.worker.name,
                worker_email=a.worker.email
            )
            for a in task.assignments
        ],
        annotations=[
            AnnotationWithWorkerResponse(
                id=ann.id,
                task_id=ann.task_id,
                worker_id=ann.worker_id,
                assignment_id=ann.assignment_id,
                result=ann.result,
                version=ann.version,
                submitted_at=ann.submitted_at,
                is_latest=ann.is_latest,
                worker_name=ann.worker.name,
                worker_email=ann.worker.email
            )
            for ann in task.annotations
        ]
    )
    
    # Get latest annotation if exists
    latest_annotations = [a for a in task.annotations if a.is_latest]
    if latest_annotations:
        latest = latest_annotations[0]
        response.latest_annotation = AnnotationWithWorkerResponse(
            id=latest.id,
            task_id=latest.task_id,
            worker_id=latest.worker_id,
            assignment_id=latest.assignment_id,
            result=latest.result,
            version=latest.version,
            submitted_at=latest.submitted_at,
            is_latest=latest.is_latest,
            worker_name=latest.worker.name,
            worker_email=latest.worker.email
        )
    
    return response
