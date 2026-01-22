# Censorium

A Python-based service API built with FastAPI to build a production-grade annotation and review platform.

Platform infra to support human-in-the-loop ML feedback pipelines with secure task assignment, concurrent reviewers, deterministic state transitions, and replayable audit trails.

## Project Structure

```
svc-censorium/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── config.py
│       │   └── exceptions.py
│       ├── db/
│       │   ├── __init__.py
│       │   └── database.py
│       └── models/
│           ├── __init__.py
│           ├── req.py
│           └── resp.py
├── tests/
│   ├── __init__.py
│   └── test_health.py
├── pytest.ini
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Features

- ✅ **State Machine:** Deterministic PENDING → IN_PROGRESS → COMPLETED transitions
- ✅ **Versioned Annotations:** Multiple submissions with full audit trail
- ✅ **Assignment Validation:** Only assigned workers can submit annotations
- ✅ **Service Layer:** Clean separation of business logic and API layer
- ✅ **Comprehensive Tests:** Full test coverage for endpoints and state transitions
- ✅ **Error Handling:** Structured error responses with proper HTTP status codes

## Quick Start

See [QUICKSTART.md](QUICKSTART.md) for a 2-minute setup guide.

```bash
# Install
pip install -e .

# Run server
uvicorn app.main:app --reload

# Run tests
pytest -v
```

## API Endpoints

### Tasks
- `POST /tasks` - Create annotation task
- `POST /tasks/{id}/assign` - Assign task to worker
- `POST /tasks/{id}/annotate` - Submit annotation (versioned)
- `GET /tasks/{id}` - Get task with full details

### Workers
- `POST /workers` - Create worker
- `GET /workers/{id}` - Get worker details
- `GET /workers/{id}/tasks` - Get worker's assigned tasks

## Installation

1. Create a virtual environment:
```bash
python -m venv dev_env
source dev_env/bin/activate  # On Windows: dev_env\Scripts\activate
```

2. Install the package in editable mode:
```bash
pip install -e .
```

This will install the package and all its dependencies as defined in `pyproject.toml`.

## Usage

Run the development server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Testing

Run tests with pytest:
```bash
pytest
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
