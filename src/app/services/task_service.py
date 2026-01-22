"""Task service with business logic and state machine."""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from app.db.models import Task, TaskStatus, ALLOWED_TRANSITIONS, Worker
from app.core.exceptions import (
    TaskNotFoundException,
    WorkerNotFoundException,
    InvalidStateTransitionException,
    TaskAlreadyCompletedException
)

class TaskService:
    """Service for task management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_task(self, input_payload: dict, worker_id: str) -> Task:
        """
        Create a new annotation task.
        
        Args:
            input_payload: Opaque JSON data for annotation
            worker_id: ID of worker creating the task
            
        Returns:
            Created Task object
            
        Raises:
            WorkerNotFoundException: If worker doesn't exist
        """
        # Validate worker exists
        worker = self.db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise WorkerNotFoundException(worker_id)
        
        task = Task(
            input_payload=input_payload,
            status=TaskStatus.PENDING,
            created_by=worker_id
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def get_task(self, task_id: str) -> Task:
        """
        Get task by ID.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object
            
        Raises:
            TaskNotFoundException: If task doesn't exist
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise TaskNotFoundException(task_id)
        return task
    
    def get_task_with_details(self, task_id: str) -> Task:
        """
        Get task with all relationships loaded.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object with relationships
            
        Raises:
            TaskNotFoundException: If task doesn't exist
        """
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id)
            .options(
                joinedload(Task.creator),
                joinedload(Task.assignments).joinedload("worker"),
                joinedload(Task.annotations).joinedload("worker")
            )
            .first()
        )
        
        if not task:
            raise TaskNotFoundException(task_id)
        return task
    
    def list_tasks(
        self,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Task], int]:
        """
        List tasks with optional filtering.
        
        Args:
            status: Optional status filter
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (tasks list, total count)
        """
        query = self.db.query(Task)
        
        if status:
            try:
                status_enum = TaskStatus(status)
                query = query.filter(Task.status == status_enum)
            except ValueError:
                pass  # Invalid status, return empty
        
        total = query.count()
        tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
        
        return tasks, total
    
    def update_task_status(
        self,
        task_id: str,
        new_status: TaskStatus,
        validate_transition: bool = True
    ) -> Task:
        """
        Update task status with state machine validation.
        
        Args:
            task_id: Task ID
            new_status: New status to set
            validate_transition: Whether to validate state transition
            
        Returns:
            Updated Task object
            
        Raises:
            TaskNotFoundException: If task doesn't exist
            InvalidStateTransitionException: If transition is invalid
        """
        task = self.get_task(task_id)
        current_status = task.status
        
        # Validate state transition if requested
        if validate_transition:
            if new_status not in ALLOWED_TRANSITIONS.get(current_status, []):
                raise InvalidStateTransitionException(
                    current_state=current_status.value,
                    target_state=new_status.value
                )
        
        # Update status
        task.status = new_status
        task.updated_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(task)
        
        return task
    
    def transition_to_in_progress(self, task_id: str) -> Task:
        """
        Transition task from PENDING to IN_PROGRESS.
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated Task object
        """
        return self.update_task_status(task_id, TaskStatus.IN_PROGRESS)
    
    def transition_to_completed(self, task_id: str) -> Task:
        """
        Transition task from IN_PROGRESS to COMPLETED.
        
        Args:
            task_id: Task ID
            
        Returns:
            Updated Task object
        """
        return self.update_task_status(task_id, TaskStatus.COMPLETED)
    
    def validate_task_not_completed(self, task_id: str) -> Task:
        """
        Validate that task is not in COMPLETED state.
        
        Args:
            task_id: Task ID
            
        Returns:
            Task object if validation passes
            
        Raises:
            TaskAlreadyCompletedException: If task is completed
        """
        task = self.get_task(task_id)
        if task.status == TaskStatus.COMPLETED:
            raise TaskAlreadyCompletedException(task_id)
        return task
