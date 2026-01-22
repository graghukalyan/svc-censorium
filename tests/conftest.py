"""Pytest configuration and fixtures."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.db.models import Worker, Task, TaskStatus

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def db():
    """Create fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    """Create test client with overridden database."""
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_worker(db):
    """Create a sample worker for testing."""
    worker = Worker(name="Test Worker", email="test@example.com")
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@pytest.fixture
def another_worker(db):
    """Create another worker for testing."""
    worker = Worker(name="Another Worker", email="another@example.com")
    db.add(worker)
    db.commit()
    db.refresh(worker)
    return worker


@pytest.fixture
def sample_task(db, sample_worker):
    """Create a sample task for testing."""
    task = Task(
        input_payload={"text": "Sample text to annotate"},
        status=TaskStatus.PENDING,
        created_by=sample_worker.id
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
