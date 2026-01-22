"""Assignment service for task-worker assignments."""
from typing import List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError

from app.db.models import Assignment, Task, Worker, TaskStatus
from app.core.exceptions import (
    TaskNotFoundException,
    WorkerNotFoundException,
    DuplicateAssignmentException,
    AssignmentNotFoundException,
    TaskAlreadyCompletedException
)


class AssignmentService:
    """Service for managing task assignments."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def assign_task(self, task_id: str, worker_id: str) -> Assignment:
        """
        Assign a task to a worker.
        
        Args:
            task_id: Task ID
            worker_id: Worker ID
            
        Returns:
            Created Assignment object
            
        Raises:
            TaskNotFoundException: If task doesn't exist
            WorkerNotFoundException: If worker doesn't exist
            DuplicateAssignmentException: If assignment already exists
            TaskAlreadyCompletedException: If task is completed
        """
        # Validate task exists and is not completed
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise TaskNotFoundException(task_id)
        
        if task.status == TaskStatus.COMPLETED:
            raise TaskAlreadyCompletedException(task_id)
        
        # Validate worker exists
        worker = self.db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise WorkerNotFoundException(worker_id)
        
        # Check for duplicate assignment
        existing = (
            self.db.query(Assignment)
            .filter(
                Assignment.task_id == task_id,
                Assignment.worker_id == worker_id
            )
            .first()
        )
        
        if existing:
            raise DuplicateAssignmentException(task_id, worker_id)
        
        # Create assignment
        assignment = Assignment(
            task_id=task_id,
            worker_id=worker_id,
            status=TaskStatus.IN_PROGRESS
        )
        
        try:
            self.db.add(assignment)
            self.db.commit()
            self.db.refresh(assignment)
        except IntegrityError:
            self.db.rollback()
            raise DuplicateAssignmentException(task_id, worker_id)
        
        return assignment
    
    def get_assignment(self, task_id: str, worker_id: str) -> Assignment:
        """
        Get assignment by task and worker.
        
        Args:
            task_id: Task ID
            worker_id: Worker ID
            
        Returns:
            Assignment object
            
        Raises:
            AssignmentNotFoundException: If assignment doesn't exist
        """
        assignment = (
            self.db.query(Assignment)
            .filter(
                Assignment.task_id == task_id,
                Assignment.worker_id == worker_id
            )
            .first()
        )
        
        if not assignment:
            raise AssignmentNotFoundException(f"{task_id}:{worker_id}")
        
        return assignment
    
    def get_worker_assignments(
        self,
        worker_id: str,
        status: str = None
    ) -> List[Assignment]:
        """
        Get all assignments for a worker.
        
        Args:
            worker_id: Worker ID
            status: Optional status filter
            
        Returns:
            List of Assignment objects
        """
        query = (
            self.db.query(Assignment)
            .filter(Assignment.worker_id == worker_id)
            .options(joinedload(Assignment.task))
        )
        
        if status:
            try:
                status_enum = TaskStatus(status)
                query = query.filter(Assignment.status == status_enum)
            except ValueError:
                pass  # Invalid status
        
        return query.order_by(Assignment.assigned_at.desc()).all()
    
    def validate_assignment(self, task_id: str, worker_id: str) -> Assignment:
        """
        Validate that worker is assigned to task.
        
        Args:
            task_id: Task ID
            worker_id: Worker ID
            
        Returns:
            Assignment object if valid
            
        Raises:
            AssignmentNotFoundException: If worker is not assigned
        """
        return self.get_assignment(task_id, worker_id)
    
    def update_assignment_status(
        self,
        task_id: str,
        worker_id: str,
        new_status: TaskStatus
    ) -> Assignment:
        """
        Update assignment status.
        
        Args:
            task_id: Task ID
            worker_id: Worker ID
            new_status: New status
            
        Returns:
            Updated Assignment object
        """
        assignment = self.get_assignment(task_id, worker_id)
        assignment.status = new_status
        
        self.db.commit()
        self.db.refresh(assignment)
        
        return assignment
