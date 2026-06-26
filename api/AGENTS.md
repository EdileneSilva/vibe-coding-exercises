# API AGENTS.md

**AI Assistant Guide for FastAPI Backend Development**

This file provides domain-specific context for AI agents working on the API component of the Docker To-Do App.

---

## 🎯 API Overview

The API is a **FastAPI** application providing RESTful endpoints for todo management, using:
- **SQLAlchemy 2.0** ORM for database operations
- **Pydantic v2** for request/response validation
- **Uvicorn** as ASGI server
- **SQLite** (default) or **PostgreSQL** for data persistence

---

## 📁 API Structure

```text
api/
├── main.py              # FastAPI app initialization, routes, health checks, middleware, startup logic
├── database.py          # Database engine, session factory, get_db dependency, Base class
├── models.py            # SQLAlchemy ORM models (Todo table definition)
├── schemas.py           # Pydantic models for request/response validation
├── crud.py              # Database CRUD operations (create, read, update, delete)
├── tests/               # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py      # Pytest fixtures (db_session, client)
│   ├── test_api.py      # API endpoint integration tests
│   └── test_crud.py     # CRUD operation unit tests
├── pyproject.toml       # Python project metadata and dependencies
├── uv.lock              # Locked dependency versions (managed by uv)
├── Dockerfile           # Container image for API service (python:3.12-slim + uv)
├── .dockerignore        # Files excluded from Docker build context
└── .env.example         # Environment variables template (DATABASE_URL)
```

---

## 🏗️ Architecture

### Request Flow

```text
HTTP Request
     ↓
Request Logging Middleware (logs method, URL, duration)
     ↓
CORS Middleware (handles cross-origin requests)
     ↓
FastAPI Router (main.py)
     ↓
Dependency Injection (get_db from database.py)
     ↓
Pydantic Validation (schemas.py)
     ↓
CRUD Operations (crud.py)
     ↓
SQLAlchemy ORM (models.py)
     ↓
Database (SQLite/PostgreSQL)
     ↓
Response (Pydantic model)
```

### Health Check Architecture

```text
Health Check Request
     ↓
Health Endpoints (main.py)
     ↓
Database Health Check: Executes "SELECT 1" query
     ↓
Metrics Endpoint: Counts todos from database
     ↓
Response: JSON with status, timestamp, and details
```

### Database Schema

```
┌─────────────────────────────────────────────────────────┐
│                      todos table                            │
├──────────┬──────────────┬──────────┬────────────┬─────────┤
│ Column    │ Type         │ Nullable │ Default     │ Index   │
├──────────┼──────────────┼──────────┼────────────┼─────────┤
│ id        │ INTEGER      │ NO       │ -           │ PRIMARY │
│ title     │ VARCHAR(200) │ NO       │ -           │ -       │
│ description│ VARCHAR(500)│ YES      │ NULL        │ -       │
│ completed │ BOOLEAN      │ NO       │ FALSE       │ -       │
│ created_at│ TIMESTAMP    │ NO       │ NOW()       │ -       │
│ updated_at│ TIMESTAMP    │ YES      │ NOW()       │ -       │
└──────────┴──────────────┴──────────┴────────────┴─────────┘
```

---

## 📡 API Endpoints

### Base URL
- **Development**: `http://localhost:8000`
- **Production (Docker)**: `http://api:8000` (internal) or via nginx at `/api`
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

### Health Check Endpoints

| Method | Endpoint | Description | Response | Status Codes |
|--------|----------|-------------|----------|--------------|
| GET | `/health` | Basic service health check | `HealthCheckResponse` | 200 |
| GET | `/health/db` | Database connectivity check | `DatabaseHealthResponse` | 200, 503 |
| GET | `/metrics` | Application metrics | `MetricsResponse` | 200 |

### Todo CRUD Endpoints

| Method | Endpoint | Description | Request Body | Response | Status Codes |
|--------|----------|-------------|--------------|----------|--------------|
| GET | `/todos` | List all todos | - | `TodoResponse[]` | 200 |
| GET | `/todos/{todo_id}` | Get todo by ID | - | `TodoResponse` | 200, 404 |
| POST | `/todos` | Create new todo | `TodoCreate` | `TodoResponse` | 201, 422 |
| PUT | `/todos/{todo_id}` | Update todo | `TodoUpdate` | `TodoResponse` | 200, 404, 422 |
| DELETE | `/todos/{todo_id}` | Delete todo | - | - | 204, 404 |

### Request/Response Schemas

```python
# Pydantic Models (schemas.py)

class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool = False

class TodoCreate(TodoBase):
    """Request body for creating a todo"""
    pass

class TodoUpdate(BaseModel):
    """Request body for updating a todo (all fields optional)"""
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool | None = None

class TodoResponse(TodoBase):
    """Response model with additional fields"""
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    
    model_config = {"from_attributes": True}  # For ORM to Pydantic conversion
```

---

## 🗃️ Database Models

### Todo Model (models.py)

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500), nullable=True)
    completed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

---

## 🔧 CRUD Operations

### Functions (crud.py)

```python
from sqlalchemy.orm import Session
from models import Todo
from schemas import TodoCreate, TodoUpdate

def get_todos(db: Session) -> list[Todo]:
    """Get all todos ordered by created_at descending"""
    return db.query(Todo).order_by(Todo.created_at.desc()).all()

def get_todo(db: Session, todo_id: int) -> Todo | None:
    """Get a single todo by ID"""
    return db.query(Todo).filter(Todo.id == todo_id).first()

def create_todo(db: Session, todo: TodoCreate) -> Todo:
    """Create a new todo item"""
    db_todo = Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def update_todo(db: Session, todo_id: int, todo: TodoUpdate) -> Todo | None:
    """Update an existing todo"""
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return None
    update_data = todo.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_todo, field, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo

def delete_todo(db: Session, todo_id: int) -> bool:
    """Delete a todo by ID, returns True if deleted"""
    db_todo = get_todo(db, todo_id)
    if not db_todo:
        return False
    db.delete(db_todo)
    db.commit()
    return True
```

---

## 🔌 Database Configuration

### database.py

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

# SQLite requires special connection args
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
class Base(DeclarativeBase):
    pass

# Dependency for FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite:///./todo.db` | Database connection URL |

**Supported Formats:**
- SQLite: `sqlite:///./todo.db`
- PostgreSQL: `postgresql://user:password@host:port/database`

---

## ⚡ FastAPI Configuration

### main.py

```python
import logging
from datetime import datetime
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import schemas
from database import Base, engine, get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="To-Do API",
    description="REST API for managing to-do tasks",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoints
@app.get("/health")
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint."""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "todo-api",
        "version": "0.1.0",
    }

@app.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Database health check endpoint."""
    try:
        db.execute("SELECT 1")
        logger.info("Database health check passed")
        return {
            "status": "healthy",
            "database": "connected",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database connection failed: {str(e)}")

@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    """Application metrics endpoint."""
    from database import SessionLocal
    try:
        db = SessionLocal()
        todo_count = len(crud.get_todos(db))
        db.close()
        return {
            "metrics": {"todos_total": todo_count, "api_uptime": "up"},
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        logger.error(f"Metrics endpoint error: {e}")
        return {"metrics": {"error": str(e)}, "timestamp": datetime.utcnow().isoformat() + "Z"}

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests for monitoring."""
    logger.info(f"Incoming request: {request.method} {request.url}")
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    logger.info(f"Request completed: {request.method} {request.url} - Status: {response.status_code} - Duration: {process_time:.2f}ms")
    return response

# CRUD endpoints
@app.get("/todos", response_model=list[schemas.TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    """List all todos."""
    return crud.get_todos(db)

@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    """Get a single todo by ID."""
    todo = crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    """Create a new todo."""
    return crud.create_todo(db, todo)

@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    """Update an existing todo."""
    updated = crud.update_todo(db, todo_id, todo)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    """Delete a todo."""
    if not crud.delete_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
```

---

## 🐳 Docker Configuration

### Dockerfile

The API Dockerfile uses uv for dependency management and runs as a non-root user:

```dockerfile
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Create non-root user with /app owned by them
RUN useradd --create-home appuser && mkdir -p /app && chown appuser:appuser /app

WORKDIR /app

USER appuser

# Install dependencies (cached layer)
COPY --chown=appuser:appuser pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copy application code
COPY --chown=appuser:appuser . .

EXPOSE 8000

ENV PATH="/app/.venv/bin:$PATH"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### docker-compose.yml (API service)

The API service configuration with health checks and proper dependencies:

```yaml
services:
  api:
    build:
      context: ./api
    environment:
      DATABASE_URL: ${DATABASE_URL}
      LOG_LEVEL: INFO
    ports:
      - "8000:8000"
    networks:
      - backend
      - frontend
    depends_on:
      db:
        condition: service_healthy
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "0.50"
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
```

---

## 🧪 Testing

### Test Files

```text
tests/
├── __init__.py
├── conftest.py          # Pytest fixtures for database and client
├── test_api.py          # API endpoint integration tests
└── test_crud.py         # CRUD operation unit tests
```

### Test Setup (conftest.py)

The test configuration uses in-memory SQLite for fast, isolated testing:

```python
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from database import Base, get_db
from main import app

@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a TestClient with database override for API tests."""
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
```

### Example Tests

```python
# test_crud.py
def test_create_todo(db_session):
    from api.crud import create_todo
    from api.schemas import TodoCreate
    
    todo_data = TodoCreate(title="Test task", description="Test description")
    todo = create_todo(db_session, todo_data)
    
    assert todo.id is not None
    assert todo.title == "Test task"
    assert todo.description == "Test description"
    assert todo.completed is False
    assert todo.created_at is not None

def test_get_todo_not_found(db_session):
    from api.crud import get_todo
    
    result = get_todo(db_session, 999)
    assert result is None

# test_main.py
def test_list_todos_empty(client):
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == []

def test_create_todo(client):
    response = client.post("/todos", json={
        "title": "Buy milk",
        "description": "Get milk from store"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["id"] is not None

def test_get_todo(client):
    # First create a todo
    create_response = client.post("/todos", json={"title": "Test"})
    todo_id = create_response.json()["id"]
    
    # Then get it
    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    assert response.json()["id"] == todo_id

def test_update_todo(client):
    # Create
    create_response = client.post("/todos", json={"title": "Test"})
    todo_id = create_response.json()["id"]
    
    # Update
    response = client.put(f"/todos/{todo_id}", json={
        "title": "Updated",
        "completed": True
    })
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["completed"] is True

def test_delete_todo(client):
    # Create
    create_response = client.post("/todos", json={"title": "Test"})
    todo_id = create_response.json()["id"]
    
    # Delete
    response = client.delete(f"/todos/{todo_id}")
    assert response.status_code == 204
    
    # Verify deleted
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404
```

---

## 📦 Dependencies

### pyproject.toml

```toml
[project]
name = "todo-api"
version = "0.1.0"
description = "FastAPI backend for Docker To-Do App"
readme = "README.md"
requires-python = ">=3.10"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn>=0.34.0",
    "sqlalchemy>=2.0.0",
    "pydantic>=2.0.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-cov>=4.0.0",
    "httpx>=0.25.0",
    "ruff>=0.1.0",
    "psycopg2-binary>=2.9.9",
]

[build-system]
requires = ["uv>=0.5.0"]
build-backend = "uv.build"
```

---

## 🔒 Security Considerations

### Environment Variables
- Always use environment variables for database credentials
- Never hardcode `DATABASE_URL` in source code
- Use `.env.example` to document required variables

### Database Security
- Use parameterized queries (SQLAlchemy ORM handles this)
- Never use string concatenation for SQL queries
- Set appropriate permissions on database files
- Use connection pooling for PostgreSQL

### API Security
- Validate all input using Pydantic models
- Use appropriate HTTP status codes
- Implement proper error handling
- Consider rate limiting for production

---

## 📝 Common Tasks

### Adding a New Endpoint

1. **Add Pydantic schema** in `schemas.py`
2. **Add CRUD function** in `crud.py`
3. **Add route** in `main.py`
4. **Add tests** in `tests/`

### Adding a New Model

1. **Add SQLAlchemy model** in `models.py`
2. **Add Pydantic schemas** in `schemas.py`
3. **Add CRUD functions** in `crud.py`
4. **Create and run migrations** (if using Alembic)
5. **Add endpoints** in `main.py`

### Database Migration

For SQLite (current setup):
- Models are created automatically on startup via `Base.metadata.create_all()`
- For schema changes, update models and restart

For PostgreSQL with Alembic (future):
```bash
# Setup Alembic
uv pip install alembic
alembic init migrations

# Configure alembic.ini and env.py
# Update models

# Create migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head
```

---

## 🎯 API-Specific Rules

### Code Style
- Follow PEP 8 guidelines
- Use type hints for all functions
- Use snake_case for variables and functions
- Use PascalCase for classes
- Keep functions small and focused
- Use docstrings for public functions

### Error Handling
- Use FastAPI's `HTTPException` for API errors
- Provide descriptive error messages
- Use appropriate HTTP status codes:
  - 200 OK - Success
  - 201 Created - Resource created
  - 204 No Content - Resource deleted
  - 400 Bad Request - Validation error
  - 404 Not Found - Resource not found
  - 500 Internal Server Error - Unexpected error

### Validation
- Use Pydantic's `Field` for validation constraints
- Validate at the schema level, not in CRUD functions
- Use `model_dump(exclude_unset=True)` for partial updates

---

## 📚 Related Documentation

- [Root AGENTS.md](../AGENTS.md) - Main AI assistant guide
- [docs/AGENTS.md](../docs/AGENTS.md) - Extended AI guide
- [docs/TECHNICAL_GUIDE.md](../docs/TECHNICAL_GUIDE.md) - Technical implementation
- [docs/COMPONENT_REFERENCE.md](../docs/COMPONENT_REFERENCE.md) - API component reference
- [README.md](README.md) - API-specific README

---

### Running Tests

```bash
# Run all API tests
cd api && uv run pytest tests/ -v

# Run specific test file
cd api && uv run pytest tests/test_api.py -v

# Run with coverage
cd api && uv run pytest tests/ --cov=./ --cov-report=term

# Run in watch mode (requires pytest-watch)
cd api && uv run pytest --watch tests/
```

---

*Last updated: 2026-06-26*
*Generated by Mistral Vibe for API-specific static context*