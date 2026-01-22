# Quick Start Guide

Get the API running in under 2 minutes.

## 1. Install Dependencies

```bash
# If you haven't already, create virtual environment
python -m venv dev_env
source dev_env/bin/activate  # On Windows: dev_env\Scripts\activate

# Install dependencies
pip install -e .
```

## 2. Run the Server

```bash
uvicorn app.main:app --reload
```

The API will be available at: http://localhost:8000

- **Swagger Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## 3. Test the API

### Create a Worker
```bash
curl -X POST http://localhost:8000/workers \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice", "email": "alice@example.com"}'
```

Save the `id` from the response (we'll call it `WORKER_ID`).

### Create a Task
```bash
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "input_payload": {"text": "Is this spam?", "url": "example.com"},
    "worker_id": "WORKER_ID"
  }'
```

Save the `id` from the response (we'll call it `TASK_ID`).

### Assign Task to Worker
```bash
curl -X POST http://localhost:8000/tasks/TASK_ID/assign \
  -H "Content-Type: application/json" \
  -d '{"worker_id": "WORKER_ID"}'
```

**Note:** Task status changes from `PENDING` → `IN_PROGRESS`

### Submit Annotation
```bash
curl -X POST http://localhost:8000/tasks/TASK_ID/annotate \
  -H "Content-Type: application/json" \
  -d '{
    "worker_id": "WORKER_ID",
    "result": {"is_spam": true, "confidence": 0.95}
  }'
```

**Note:** Task status changes to `COMPLETED`

### Get Task Details
```bash
curl http://localhost:8000/tasks/TASK_ID
```

### Get Worker's Tasks
```bash
curl http://localhost:8000/workers/WORKER_ID/tasks
```

## 4. Run Tests

```bash
pytest -v
```

Expected output:
```
tests/test_tasks.py::test_create_task PASSED
tests/test_tasks.py::test_assign_task PASSED
tests/test_tasks.py::test_submit_annotation PASSED
tests/test_state_machine.py::test_allowed_transitions_definition PASSED
... [all tests should pass]
```

## 5. Explore the API

Open http://localhost:8000/docs for interactive API documentation.

Try these scenarios:
1. ✅ Create multiple workers
2. ✅ Assign same task to different workers (should fail - single assignment)
3. ✅ Submit annotation without assignment (should fail - unauthorized)
4. ✅ Try invalid state transition (should fail - state machine)
5. ✅ Submit multiple annotations (creates versions)

## Common Commands

```bash
# Run server with auto-reload
uvicorn app.main:app --reload

# Run tests with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_state_machine.py -v

# Clear database (restart fresh)
rm censorium.db test.db
```

## Project Structure

```
src/app/
├── main.py              # FastAPI app, routes registration
├── db/
│   ├── models.py        # ⭐ SQLAlchemy models, state machine
│   └── database.py      # Database connection
├── services/            # ⭐ Business logic layer
│   ├── task_service.py
│   ├── annotation_service.py
│   └── assignment_service.py
├── api/                 # API route handlers
│   ├── task_routes.py
│   └── worker_routes.py
├── models/              # Pydantic schemas
│   ├── req.py           # Request models
│   └── resp.py          # Response models
└── core/
    ├── config.py        # Configuration
    └── exceptions.py    # Custom exceptions

tests/
├── conftest.py          # Pytest fixtures
├── test_tasks.py        # ⭐ Task endpoint tests
├── test_workers.py      # Worker endpoint tests
└── test_state_machine.py # ⭐ State transition tests
```

⭐ = Priority files for interview study

## Next Steps

1. Read `INTERVIEW_STUDY_GUIDE.md` for deep dive on critical concepts
2. Experiment with the API using Swagger UI
3. Review the test files to understand expected behavior
4. Practice explaining the architecture out loud

Good luck! 🚀
