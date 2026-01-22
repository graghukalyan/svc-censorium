"""Annotation service for managing versioned annotation submissions."""
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc

from app.db.models import Annotation, Task, Worker
from app.core.exceptions import (
    TaskNotFoundException,
    WorkerNotFoundException,
    UnauthorizedAnnotationException
)


class AnnotationService:
    """Service for managing annotation submissions."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def submit_annotation(
        self,
        task_id: str,
        worker_id: str,
        assignment_id: str,
        result: dict
    ) -> Annotation:
        """
        Submit an annotation for a task (creates new version).
        
        Args:
            task_id: Task ID
            worker_id: Worker ID
            assignment_id: Assignment ID
            result: Annotation result data
            
        Returns:
            Created Annotation object
            
        Raises:
            TaskNotFoundException: If task doesn't exist
            WorkerNotFoundException: If worker doesn't exist
        """
        # Validate task exists
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise TaskNotFoundException(task_id)
        
        # Validate worker exists
        worker = self.db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise WorkerNotFoundException(worker_id)
        
        # Get current version number for this worker-task combination
        latest = (
            self.db.query(Annotation)
            .filter(
                Annotation.task_id == task_id,
                Annotation.worker_id == worker_id
            )
            .order_by(desc(Annotation.version))
            .first()
        )
        
        new_version = (latest.version + 1) if latest else 1
        
        # Mark all previous annotations from this worker as not latest
        self.db.query(Annotation).filter(
            Annotation.task_id == task_id,
            Annotation.worker_id == worker_id,
            Annotation.is_latest == True
        ).update({"is_latest": False})
        
        # Create new annotation
        annotation = Annotation(
            task_id=task_id,
            worker_id=worker_id,
            assignment_id=assignment_id,
            result=result,
            version=new_version,
            is_latest=True
        )
        
        self.db.add(annotation)
        self.db.commit()
        self.db.refresh(annotation)
        
        return annotation
    
    def get_annotation(self, annotation_id: str) -> Optional[Annotation]:
        """
        Get annotation by ID.
        
        Args:
            annotation_id: Annotation ID
            
        Returns:
            Annotation object or None
        """
        return (
            self.db.query(Annotation)
            .filter(Annotation.id == annotation_id)
            .first()
        )
    
    def get_task_annotations(
        self,
        task_id: str,
        latest_only: bool = False
    ) -> List[Annotation]:
        """
        Get all annotations for a task.
        
        Args:
            task_id: Task ID
            latest_only: If True, return only latest versions
            
        Returns:
            List of Annotation objects
        """
        query = (
            self.db.query(Annotation)
            .filter(Annotation.task_id == task_id)
            .options(joinedload(Annotation.worker))
        )
        
        if latest_only:
            query = query.filter(Annotation.is_latest == True)
        
        return query.order_by(desc(Annotation.submitted_at)).all()
    
    def get_latest_annotation(
        self,
        task_id: str,
        worker_id: str
    ) -> Optional[Annotation]:
        """
        Get latest annotation for a task-worker combination.
        
        Args:
            task_id: Task ID
            worker_id: Worker ID
            
        Returns:
            Latest Annotation object or None
        """
        return (
            self.db.query(Annotation)
            .filter(
                Annotation.task_id == task_id,
                Annotation.worker_id == worker_id,
                Annotation.is_latest == True
            )
            .first()
        )
    
    def get_annotation_history(
        self,
        task_id: str,
        worker_id: str
    ) -> List[Annotation]:
        """
        Get all annotation versions for a task-worker combination.
        
        Args:
            task_id: Task ID
            worker_id: Worker ID
            
        Returns:
            List of Annotation objects ordered by version descending
        """
        return (
            self.db.query(Annotation)
            .filter(
                Annotation.task_id == task_id,
                Annotation.worker_id == worker_id
            )
            .order_by(desc(Annotation.version))
            .all()
        )
    
    def get_worker_annotations(
        self,
        worker_id: str,
        latest_only: bool = True
    ) -> List[Annotation]:
        """
        Get all annotations submitted by a worker.
        
        Args:
            worker_id: Worker ID
            latest_only: If True, return only latest versions
            
        Returns:
            List of Annotation objects
        """
        query = (
            self.db.query(Annotation)
            .filter(Annotation.worker_id == worker_id)
        )
        
        if latest_only:
            query = query.filter(Annotation.is_latest == True)
        
        return query.order_by(desc(Annotation.submitted_at)).all()
