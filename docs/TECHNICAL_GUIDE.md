# Technical Guide

Detailed guide for technical implementation aspects.

## Tech Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| API Framework | FastAPI | >= 0.115.0 | REST API with automatic OpenAPI docs |
| ASGI Server | Uvicorn | >= 0.34.0 | Production-ready ASGI server |
| ORM | SQLAlchemy | >= 2.0.0 | Database abstraction layer |
| Validation | Pydantic | >= 2.0.0 | Data validation and serialization |
| Database | SQLite (built-in) | - | Default development database |
| Database | PostgreSQL | 16 | Production database |
| Frontend | SvelteKit (Svelte 5 runes) | ^2.15 | Full-stack framework with reactive state |
| Styling | Tailwind CSS | ^4.0 | Utility-first CSS framework |
| Bundler | Vite | ^6.0 | Fast frontend build tool |
| Language (frontend) | TypeScript | ^5.7 | Type-safe JavaScript superset |
| Language (backend) | Python | >= 3.12 | Backend runtime |
| Package Manager (JS) | Bun | >= 1.1.45 | JavaScript runtime and package manager |
| Package Manager (Python) | uv | >= 0.5 | Python dependency management |
| Git Hooks | Husky | ^9.1 | Git hook management |
| Commit Lint | commitlint | ^20.4 | Commit message validation |
| Markdown Lint | markdownlint-cli | ^0.48 | Markdown style enforcement |
| Testing (Python) | pytest | >= 8.0.0 | Python test framework |
| Testing (JavaScript) | vitest | ^2.1.8 | JavaScript test framework |
| E2E Testing | Playwright | ^1.48.0 | End-to-end browser testing |

---

## Architecture

### Development Architecture

```text
┌────────────────────┐        ┌─────────────────────┐        ┌────────────┐
│  SvelteKit (Vite)  │  ───▶  │   FastAPI (uvicorn) │  ───▶  │  Database  │
│   localhost:5173   │        │    localhost:8000   │        │  (SQLite)  │
└────────────────────┘        └─────────────────────┘        └────────────┘
       (browser)              (proxied via /api in dev)        (todo.db)
```

The Vite dev server proxies `/api/*` requests to the FastAPI service, eliminating CORS issues during development.

### Production Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                       Docker Compose Production                    │
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────────┐  │
│  │  web (nginx) │ ←─── │  api (uvic.) │ ←─── │   db (Postgres)│  │
│  │   :8080      │      │   :8000      │      │     :5432      │  │
│  └──────────────┘      └──────────────┘      └────────────────┘  │
│       ▲                                                ▲              │
│       │                                                │              │
│   (browser)                                     [pgdata volume]    │
└──────────────────────────────────────────────────────────────────┘
        frontend network (traefik_frontend)    backend network (traefik_backend)
```

In production, nginx serves the static SvelteKit build and proxies `/api/*` requests to the FastAPI service
through the internal Docker network. The API includes health check endpoints and CORS middleware for flexibility.

---

## FastAPI Application

The FastAPI application (`api/main.py`) includes:
- RESTful CRUD endpoints for todo management (`/todos`)
- Health check endpoints (`/health`, `/health/db`, `/metrics`)
- Request logging middleware for monitoring
- CORS middleware configuration
- Automatic table creation on startup

### Health Check Endpoints

The API provides health check endpoints for monitoring and observability:

- **GET `/health`** - Basic health check returning service status, timestamp, and version
- **GET `/health/db`** - Database connectivity check that executes a test query
- **GET `/metrics`** - Application metrics including todo count and uptime status

### Request Logging Middleware

All HTTP requests are logged with:
- Request method and URL
- Processing time in milliseconds
- Response status code

This provides visibility into API usage and performance without additional monitoring tools.

### Database Connection (`database.py`)

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Models (`models.py`)

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

### Schemas (`schemas.py`)

```python
from datetime import datetime
from pydantic import BaseModel, Field


class TodoBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=200)
    description: str | None = Field(None, max_length=500)
    completed: bool | None = None


class TodoResponse(TodoBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}
```

### Endpoints (`main.py`)

```python
from datetime import datetime
from typing import Any
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import crud
import schemas
from database import Base, engine, get_db

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

# CORS middleware configuration
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
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "service": "todo-api",
        "version": "0.1.0",
    }

@app.get("/health/db")
async def database_health_check(db: Session = Depends(get_db)) -> dict[str, Any]:
    """Database health check endpoint."""
    db.execute("SELECT 1")
    return {
        "status": "healthy",
        "database": "connected",
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

@app.get("/metrics")
async def metrics() -> dict[str, Any]:
    """Application metrics endpoint."""
    from database import SessionLocal
    db = SessionLocal()
    todo_count = len(crud.get_todos(db))
    db.close()
    return {
        "metrics": {
            "todos_total": todo_count,
            "api_uptime": "up",
        },
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests for monitoring."""
    start_time = datetime.utcnow()
    response = await call_next(request)
    process_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    # Log request details (method, URL, status, duration)
    return response

# CRUD endpoints
@app.get("/todos", response_model=list[schemas.TodoResponse])
def list_todos(db: Session = Depends(get_db)):
    return crud.get_todos(db)

@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    todo = crud.get_todo(db, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo

@app.post("/todos", response_model=schemas.TodoResponse, status_code=201)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, todo)

@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    updated = crud.update_todo(db, todo_id, todo)
    if not updated:
        raise HTTPException(status_code=404, detail="Todo not found")
    return updated

@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    if not crud.delete_todo(db, todo_id):
        raise HTTPException(status_code=404, detail="Todo not found")
```

---

## SvelteKit Frontend

### Vite Configuration (`vite.config.ts`)

The Vite dev server proxies `/api/*` to the FastAPI service, removing the need for CORS in
development.

```ts
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';

export default defineConfig({
  plugins: [tailwindcss(), sveltekit()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
});
```

### Tailwind v4 Entry (`src/app.css`)

Tailwind v4 is loaded with a single CSS-first import. No `tailwind.config.js` is required for the
default token set.

```css
@import 'tailwindcss';
```

### Typed Fetch Client (`src/lib/api.ts`)

The API client uses environment variables for base URL configuration and provides type-safe communication:

```ts
import { env } from '$env/dynamic/public';
import type { Todo, TodoCreate, TodoUpdate } from './types';

const BASE = env.PUBLIC_API_BASE || '/api';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export const api = {
  listTodos: () => request<Todo[]>('/todos'),
  getTodo: (id: number) => request<Todo>(`/todos/${id}`),
  createTodo: (payload: TodoCreate) =>
    request<Todo>('/todos', { method: 'POST', body: JSON.stringify(payload) }),
  updateTodo: (id: number, payload: TodoUpdate) =>
    request<Todo>(`/todos/${id}`, { method: 'PUT', body: JSON.stringify(payload) }),
  deleteTodo: (id: number) => request<void>(`/todos/${id}`, { method: 'DELETE' })
};
```

### Reactive State (Svelte 5 runes)

The main page uses runes for reactive state and derived values:

```svelte
<script lang="ts">
  import { api } from '$lib/api';

  let todos = $state<Todo[]>([]);
  let filter = $state<'all' | 'active' | 'completed'>('all');

  const visibleTodos = $derived.by(() => {
    if (filter === 'active') return todos.filter((t) => !t.completed);
    if (filter === 'completed') return todos.filter((t) => t.completed);
    return todos;
  });

  $effect(() => {
    api.listTodos().then((list) => (todos = list));
  });
</script>
```

---

## CI/CD

### GitHub Actions Workflows

The project uses GitHub Actions for continuous integration with the following workflows:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `lint.yml` | Push/PR to develop/main | Markdown and YAML linting |
| `test.yml` | Push/PR | Run API, frontend, and E2E tests |
| `build.yml` | Push to main | Docker image builds and pushes |
| `security.yml` | Push/PR | Security scanning |
| `setup.yml` | Repository setup | Initial setup and configuration |
| `dependabot-lockfile.yml` | Schedule | Dependabot lockfile updates |

### Lint Workflow

The lint workflow runs on every push and PR to `develop` and `main`:

```yaml
# .github/workflows/lint.yml
name: Lint

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop, main]

jobs:
  markdownlint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: oven-sh/setup-bun@v2
      - run: bun install --frozen-lockfile
      - run: bun run lint:md

  yamllint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: uvx yamllint .
```

### Test Workflow

The test workflow runs API, frontend, and E2E tests on every push and PR:

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test-api:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
      - run: cd api && uv sync && uv run pytest tests/ -v

  test-frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: oven-sh/setup-bun@v2
      - run: cd web && bun install && bun run check && bun test

  test-e2e:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: oven-sh/setup-bun@v2
      - run: cd e2e && bun install && bun run test
```

### Security Workflow

The security workflow runs vulnerability scanning on the codebase:

```yaml
# .github/workflows/security.yml
name: Security

on: [push, pull_request]

jobs:
  secrets-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: oven-sh/setup-bun@v2
      - run: bun install --frozen-lockfile
      - run: bun run secrets:scan
```

---

## Git Hooks

### Husky Configuration

Husky manages Git hooks with the following setup:

- **pre-commit**: Runs linting and validation scripts via `scripts/pre-commit-hook.js`
- **commit-msg**: Validates commit messages via `scripts/commit-msg-hook.js` (commitlint)

### Pre-commit Hook

The pre-commit hook runs multiple validation steps:

```json
{
  "lint-staged": {
    "*.md": "markdownlint --fix",
    "*.{yml,yaml}": "yamllint"
  }
}
```

Additional validation is provided by:
- `scripts/pre-commit-hook.js` - Runs comprehensive pre-commit checks
- `scripts/pre-push-hook.js` - Runs pre-push validation
- `scripts/secrets-scan.js` - Scans for secrets in staged files
- `.vibe/hooks/pre-commit/secrets_hook.py` - Mistral Vibe secrets detection hook
- `.vibe/hooks/pre-push/secrets_hook.py` - Mistral Vibe pre-push secrets detection

### Commit-msg Hook

Commitlint validates commit messages using either Gitmoji or Conventional Commits format.

### Setup

```bash
# Install dependencies (runs husky prepare script automatically)
bun install

# Manual setup if needed
bun run pre-commit-hook
```

---

## Development Workflow

### Feature Development

```bash
# 1. Update local main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/short-description

# 3. Develop
# API (terminal 1)
cd api
uv sync                            # creates .venv and installs dependencies
uv run uvicorn main:app --reload   # http://localhost:8000

# Frontend (terminal 2)
cd web
bun install
bun run dev                        # http://localhost:5173

# Optional: E2E tests (terminal 3)
cd e2e
bun install
# Run tests against dev servers
bun run test

# 4. Lint, test, commit
bun run lint
bun run test:all
bun run commit  # or use git commit with proper message

# 5. Push and create PR
git push origin feature/short-description
```

### Pre-commit Checklist

- [ ] `bun run lint` passes (markdown and YAML linting)
- [ ] `cd web && bun run check` passes (frontend type-checking)
- [ ] `cd web && bun run build` succeeds (frontend build)
- [ ] `cd api && uv run pytest tests/` passes (API tests)
- [ ] `cd web && bun test` passes (frontend tests)
- [ ] API endpoints respond correctly (`curl http://localhost:8000/todos`)
- [ ] Web UI loads and functions at <http://localhost:5173>
- [ ] Health check endpoints work (`curl http://localhost:8000/health`)
- [ ] Documentation updated if needed
- [ ] No sensitive data committed
- [ ] Commit message follows gitmoji or conventional commits convention

### Docker Development

```bash
# Build and start all services
docker compose up --build -d

# View logs
docker compose logs -f

# Enter containers for debugging
docker compose exec api bash
docker compose exec web bash

# Stop services
docker compose down -v
```

---

## AI Agent Extensions

This project includes Mistral Vibe extensions for enhanced AI agent capabilities:

### Skills

Auto-triggered specialized skills that provide domain-specific guidance:

| Skill | Location | Trigger | Purpose |
|-------|----------|---------|---------|
| `todo-management` | `.vibe/skills/todo-management/` | Todo-related tasks | Manage todo items, projects, workflows |
| `docker-helper` | `.vibe/skills/docker-helper/` | Docker commands | Assist with Docker setup, debugging, deployment |
| `code-reviewer` | `.vibe/skills/code-reviewer/` | Code review requests | Analyze code quality, suggest improvements |

### MCP Servers

Model Context Protocol servers for enhanced AI capabilities:

| MCP Server | Location | Purpose |
|------------|----------|---------|
| `file-indexer` | `.vibe/mcp/file-indexer/` | File system indexing for search and retrieval |
| `docker-monitor` | `.vibe/mcp/docker-monitor/` | Docker container status monitoring |
| `git-analyzer` | `.vibe/mcp/git-analyzer/` | Git repository analysis (commits, branches, diffs) |

### Hooks

Event-driven hooks for security and validation:

| Hook | Location | Event | Purpose |
|------|----------|-------|---------|
| `secrets_hook.py` | `.vibe/hooks/pre-commit/` | Pre-commit | Detect and block secrets from being committed |
| `secrets_hook.py` | `.vibe/hooks/pre-push/` | Pre-push | Detect and block secrets from being pushed |

### Slash Commands

Manual commands for direct chat interactions:

| Command | Location | Usage | Purpose |
|---------|----------|-------|---------|
| `/todo` | `.vibe/commands/todo-command/` | `/todo add Buy milk` | Manage todo items directly |
| `/docker` | `.vibe/commands/docker-command/` | `/docker status` | Execute Docker operations |

---

*Last updated: 2026-06-26*
