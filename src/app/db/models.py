"""Database models for annotation platform."""
import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Enum, ForeignKey, Integer, Boolean, JSON,
    UniqueConstraint, Index, Text
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.database import Base


class TaskStatus(str, enum.Enum):
    """Task status enum with deterministic state transitions."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


# Define allowed state transitions for state machine
ALLOWED_TRANSITIONS = {
    TaskStatus.PENDING: [TaskStatus.IN_PROGRESS],
    TaskStatus.IN_PROGRESS: [TaskStatus.COMPLETED],
    TaskStatus.COMPLETED: []  # Terminal state
}


class Worker(Base):
    """Worker/Annotator model."""
    __tablename__ = "workers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by")
    assignments = relationship("Assignment", back_populates="worker", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="worker", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Worker(id={self.id}, email={self.email})>"


class Task(Base):
    """Annotation task model."""
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    input_payload = Column(JSON, nullable=False)  # Opaque JSON for annotation
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    created_by = Column(String, ForeignKey("workers.id"), nullable=False)
    
    # Relationships
    creator = relationship("Worker", back_populates="created_tasks", foreign_keys=[created_by])
    assignments = relationship("Assignment", back_populates="task", cascade="all, delete-orphan")
    annotations = relationship("Annotation", back_populates="task", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('ix_tasks_status_created_at', 'status', 'created_at'),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, status={self.status})>"


class Assignment(Base):
    """Task assignment to worker (tracks who can work on what)."""
    __tablename__ = "assignments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    worker_id = Column(String, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    status = Column(Enum(TaskStatus), default=TaskStatus.IN_PROGRESS, nullable=False)
    
    # Relationships
    task = relationship("Task", back_populates="assignments")
    worker = relationship("Worker", back_populates="assignments")
    annotations = relationship("Annotation", back_populates="assignment")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('task_id', 'worker_id', name='uq_task_worker_assignment'),
        Index('ix_assignments_worker_status', 'worker_id', 'status'),
        Index('ix_assignments_task_id', 'task_id'),
    )

    def __repr__(self):
        return f"<Assignment(task_id={self.task_id}, worker_id={self.worker_id})>"


class Annotation(Base):
    """Annotation submission with versioning support."""
    __tablename__ = "annotations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    worker_id = Column(String, ForeignKey("workers.id", ondelete="CASCADE"), nullable=False)
    assignment_id = Column(String, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False)
    result = Column(JSON, nullable=False)  # Annotation data
    version = Column(Integer, nullable=False)  # Increments per worker submission
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_latest = Column(Boolean, default=True, nullable=False, index=True)
    
    # Relationships
    task = relationship("Task", back_populates="annotations")
    worker = relationship("Worker", back_populates="annotations")
    assignment = relationship("Assignment", back_populates="annotations")
    
    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint('task_id', 'worker_id', 'version', name='uq_task_worker_version'),
        Index('ix_annotations_task_latest', 'task_id', 'is_latest'),
        Index('ix_annotations_worker_latest', 'worker_id', 'is_latest'),
    )

    def __repr__(self):
        return f"<Annotation(id={self.id}, task_id={self.task_id}, version={self.version})>"
