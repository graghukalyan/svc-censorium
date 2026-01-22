"""Worker service for managing workers."""
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import Worker
from app.core.exceptions import WorkerNotFoundException, DuplicateEmailException


class WorkerService:
    """Service for worker management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_worker(self, name: str, email: str) -> Worker:
        """
        Create a new worker.
        
        Args:
            name: Worker name
            email: Worker email (must be unique)
            
        Returns:
            Created Worker object
            
        Raises:
            DuplicateEmailException: If email already exists
        """
        # Check for duplicate email
        existing = self.db.query(Worker).filter(Worker.email == email).first()
        if existing:
            raise DuplicateEmailException(email)
        
        worker = Worker(name=name, email=email)
        
        try:
            self.db.add(worker)
            self.db.commit()
            self.db.refresh(worker)
        except IntegrityError:
            self.db.rollback()
            raise DuplicateEmailException(email)
        
        return worker
    
    def get_worker(self, worker_id: str) -> Worker:
        """
        Get worker by ID.
        
        Args:
            worker_id: Worker ID
            
        Returns:
            Worker object
            
        Raises:
            WorkerNotFoundException: If worker doesn't exist
        """
        worker = self.db.query(Worker).filter(Worker.id == worker_id).first()
        if not worker:
            raise WorkerNotFoundException(worker_id)
        return worker
    
    def get_worker_by_email(self, email: str) -> Optional[Worker]:
        """
        Get worker by email.
        
        Args:
            email: Worker email
            
        Returns:
            Worker object or None
        """
        return self.db.query(Worker).filter(Worker.email == email).first()
    
    def list_workers(self, skip: int = 0, limit: int = 100) -> tuple[list[Worker], int]:
        """
        List all workers with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Tuple of (workers list, total count)
        """
        query = self.db.query(Worker)
        total = query.count()
        workers = query.order_by(Worker.created_at.desc()).offset(skip).limit(limit).all()
        
        return workers, total
