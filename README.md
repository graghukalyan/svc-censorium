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

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
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
