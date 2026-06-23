# AGENTS.md

**Main guide for AI assistants working on this repository.**

This file provides the static context that persists across all sessions. It is versioned in Git and shared with the entire team.

---

## 📋 Quick Start Guide

### Project Overview

**Docker To-Do App** is a multi-container application featuring:
- **FastAPI** REST API with SQLite/PostgreSQL
- **SvelteKit + Tailwind v4** frontend
- **Docker Compose** orchestration
- **nginX** reverse proxy for production

### Essential Commands

```bash
# Docker operations
docker compose up --build       # Build and start all services (foreground)
docker compose up --build -d    # Build and start in background (detached)
docker compose down             # Stop all services
docker compose down -v          # Stop and remove volumes (clean slate)
docker compose logs -f          # Follow all service logs
docker compose exec api bash    # Enter API container
docker compose exec web bash    # Enter web container

# Development (without Docker)
cd api && uv sync                    # Setup Python virtual env and dependencies
cd api && uv run uvicorn main:app --reload  # Start API at http://localhost:8000

cd web && bun install               # Install frontend dependencies
cd web && bun run dev               # Start frontend at http://localhost:5173

# Linting and quality (requires bun install at root)
bun install           # Install linting dependencies
bun run lint          # Lint markdown and yaml
bun run lint:md       # Lint markdown only
bun run lint:md:fix   # Auto-fix markdown issues
bun run lint:yaml     # Lint yaml files
bun run lint:commit   # Validate last commit message
bun run commit        # Interactive gitmoji commit tool

# Frontend checks
cd web && bun run check         # Type-check with svelte-check + tsc
cd web && bun run build         # Production build
cd web && bun run preview        # Preview production build

# Testing
cd api && python -m pytest tests/          # Run API tests
cd web && bun test                     # Run frontend tests (vitest)
```

---

## 🏗️ Architecture

### Service Topology

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
│  (browser:8080)                                  [pgdata volume]      │
└──────────────────────────────────────────────────────────────────┘
        frontend network (traefik_frontend)    backend network (traefik_backend)
```

### Development Topology

```text
┌────────────────────┐        ┌─────────────────────┐        ┌────────────┐
│  SvelteKit (Vite)   │  ───▶  │   FastAPI (uvicorn) │  ───▶  │  Database  │
│   localhost:5173    │        │    localhost:8000   │        │  (SQLite)  │
└────────────────────┘        └─────────────────────┘        └────────────┘
       (browser)              (proxied via /api in dev)        (todo.db)
```

The Vite dev server proxies `/api/*` to FastAPI, eliminating CORS issues in development.

---

## 📚 Documentation Index

### Core Documentation

| File | Purpose | Description |
|------|---------|-------------|
| [`AGENTS.md`](./AGENTS.md) | **This file** | Master guide for AI agents, static context |
| [`docs/AGENTS.md`](./docs/AGENTS.md) | Extended AI Guide | Detailed conventions, rules, and best practices |
| [`README.md`](./README.md) | Project Overview | Quick start, architecture, endpoints |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | Contribution Guide | How to contribute to the project |

### Technical Documentation

| File | Purpose | Description |
|------|---------|-------------|
| [`docs/PROJECT_STRUCTURE.md`](./docs/PROJECT_STRUCTURE.md) | Architecture | Directory layout, file organization |
| [`docs/CONVENTIONS.md`](./docs/CONVENTIONS.md) | Code Style | Naming, formatting, git conventions |
| [`docs/TECHNICAL_GUIDE.md`](./docs/TECHNICAL_GUIDE.md) | Implementation | API, database, frontend, CI/CD details |
| [`docs/DESIGN_SYSTEM.md`](./docs/DESIGN_SYSTEM.md) | UI/UX | Tailwind v4 tokens, layout patterns |
| [`docs/COMPONENT_REFERENCE.md`](./docs/COMPONENT_REFERENCE.md) | Components | API endpoints, Pydantic schemas, Svelte components |

### Feature & Workflow Documentation

| File | Purpose | Description |
|------|---------|-------------|
| [`docs/FEATURES.md`](./docs/FEATURES.md) | Features | Epics, user stories, feature status |
| [`docs/SCREEN_FLOW.md`](./docs/SCREEN_FLOW.md) | Navigation | Web app screen flows and UX |
| [`docs/TASKS.md`](./docs/TASKS.md) | Tasks | Task tracking and backlog |

### Domain-Specific AGENTS.md (Hierarchical)

| File | Purpose | Scope |
|------|---------|-------|
| [`api/AGENTS.md`](./api/AGENTS.md) | API Development | FastAPI, SQLAlchemy, database |
| [`web/AGENTS.md`](./web/AGENTS.md) | Frontend Development | SvelteKit, Tailwind, TypeScript |
| [`docs/AGENTS.md`](./docs/AGENTS.md) | Documentation Standards | Markdown, structure, conventions |

---

## 🛠️ Technology Stack

### Backend Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| API Framework | FastAPI | >= 0.115.0 | REST API with automatic OpenAPI docs |
| ASGI Server | Uvicorn | >= 0.34.0 | Production-ready ASGI server |
| ORM | SQLAlchemy | >= 2.0.0 | Database abstraction layer |
| Validation | Pydantic | >= 2.0.0 | Data validation and serialization |
| Database | SQLite | Built-in | Default development database |
| Database | PostgreSQL | 16 | Production database |
| Python | CPython | >= 3.10 | Runtime |
| Package Manager | uv | >= 0.5 | Python dependency management |

### Frontend Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| Framework | SvelteKit | ^2.15 | Full-stack framework (Svelte 5 runes) |
| Styling | Tailwind CSS | ^4.0 | Utility-first CSS framework |
| Bundler | Vite | ^6.0 | Fast frontend build tool |
| Language | TypeScript | ^5.7 | Type-safe JavaScript superset |
| Package Manager | Bun | >= 1.3 | JavaScript runtime and package manager |

### DevOps & Tooling

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| Containerization | Docker | >= 24.0 | Container runtime |
| Orchestration | Docker Compose | >= 2.20 | Multi-container management |
| Reverse Proxy | nginx | Latest | Production web server and API proxy |
| Git Hooks | Husky | ^9.1 | Git hook management |
| Commit Lint | commitlint | ^20.4 | Commit message validation |
| Markdown Lint | markdownlint-cli | ^0.48 | Markdown style enforcement |
| YAML Lint | yamllint | Latest | YAML validation |
| Python Lint | Ruff | Latest | Fast Python linter |
| Dependency Updates | Renovate | Latest | Automatic dependency updates |
| CI/CD | GitHub Actions | Latest | Continuous integration |

---

## 📁 Project Structure

```text
todo-app/
├── api/                                # FastAPI application
│   ├── main.py                         # API entry point, routes, startup
│   ├── database.py                     # Database connection, session factory
│   ├── models.py                       # SQLAlchemy ORM models
│   ├── schemas.py                      # Pydantic validation schemas
│   ├── crud.py                         # Database CRUD operations
│   ├── tests/                          # API unit and integration tests
│   ├── pyproject.toml                  # Python project metadata
│   ├── uv.lock                         # Locked dependencies (uv)
│   ├── Dockerfile                      # API container image
│   ├── .dockerignore                   # Files to exclude from API image
│   └── .env.example                    # API runtime environment template
│
├── web/                                # SvelteKit + Tailwind v4 frontend
│   ├── src/
│   │   ├── app.html                    # HTML shell template
│   │   ├── app.css                     # Tailwind v4 entry point
│   │   ├── app.d.ts                    # SvelteKit type augmentation
│   │   ├── lib/
│   │   │   ├── api.ts                  # Typed fetch client for API
│   │   │   ├── types.ts                # Shared TypeScript type definitions
│   │   │   └── components/
│   │   │       └── TodoItem.svelte     # Individual todo item component
│   │   └── routes/
│   │       ├── +layout.svelte          # Root layout (Tailwind imports)
│   │       └── +page.svelte            # Main todo list page
│   ├── tests/                          # Frontend tests (vitest)
│   ├── package.json                    # Frontend dependencies and scripts
│   ├── svelte.config.js                # SvelteKit configuration
│   ├── vite.config.ts                  # Vite configuration with API proxy
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── nginx.conf                      # Production nginx configuration
│   ├── Dockerfile                      # Web container image (multi-stage)
│   ├── .dockerignore                   # Files to exclude from web image
│   └── .env.example                    # Web public environment template
│
├── .github/                            # GitHub configuration
│   ├── workflows/
│   │   ├── lint.yml                    # Markdown and YAML linting workflow
│   │   ├── release.yml                 # Semantic release workflow
│   │   └── setup.yml                   # Repository setup workflow
│   ├── ISSUE_TEMPLATE/                 # GitHub issue templates
│   │   ├── bug.md                      # Bug report template
│   │   └── us.md                       # User story template
│   ├── pull_request_template.md        # PR template
│   ├── CODEOWNERS                      # Code ownership rules
│   ├── dependabot.yml                  # Dependabot configuration
│   └── settings.yml                    # Repository settings
│
├── docs/                               # Documentation
│   ├── AGENTS.md                       # AI assistant comprehensive guide
│   ├── PROJECT_STRUCTURE.md            # Directory and file organization
│   ├── CONVENTIONS.md                  # Code style and git conventions
│   ├── TECHNICAL_GUIDE.md              # Technical implementation details
│   ├── DESIGN_SYSTEM.md                # Tailwind v4 UI design system
│   ├── COMPONENT_REFERENCE.md          # API endpoints and Svelte components
│   ├── FEATURES.md                     # Epics and user stories
│   ├── SCREEN_FLOW.md                  # Web app navigation flows
│   ├── TASKS.md                        # Project task tracking
│   └── briefs/                         # Project briefs and specifications
│
├── .vibe/                             # Mistral Vibe extensions
│   ├── skills/                         # Auto-triggered specialized skills
│   │   ├── todo-management/            # Todo management skill
│   │   │   └── skill.md                # Skill definition and workflows
│   │   ├── docker-helper/              # Docker operations skill
│   │   │   └── skill.md
│   │   └── code-reviewer/               # Code review skill
│   │       └── skill.md
│   ├── mcp/                            # Model Context Protocol servers
│   │   ├── file-indexer/               # File system indexing MCP
│   │   │   ├── server.py               # MCP server implementation
│   │   │   └── README.md               # Documentation
│   │   ├── docker-monitor/             # Docker status monitoring MCP
│   │   │   ├── server.py
│   │   │   └── README.md
│   │   └── git-analyzer/               # Git repository analysis MCP
│   │       ├── server.py
│   │       └── README.md
│   ├── hooks/                          # Event-driven hooks
│   │   ├── pre-commit/                 # Pre-commit validation hooks
│   │   │   └── secrets-hook.py         # Secrets detection hook
│   │   └── pre-push/                   # Pre-push validation hooks
│   │       └── secrets-hook.py         # Secrets detection hook
│   └── commands/                       # Slash commands
│       ├── todo-command/              # /todo command
│       │   ├── command.md              # Command definition
│       │   └── handler.py              # Command handler
│       └── docker-command/             # /docker command
│           ├── command.md
│           └── handler.py
│
├── .husky/                            # Git hooks (Husky)
│   └── pre-commit                      # Pre-commit hook script
│
├── .env.example                        # Environment variables template (Compose-level)
├── .gitignore                          # Git ignore rules
├── .gitmoji.json                       # Gitmoji-cli configuration
├── .editorconfig                       # Editor settings
├── .markdownlint.json                  # Markdown linting rules
├── .yamllint.yml                       # YAML linting rules
├── .releaserc.json                     # Semantic-release configuration
├── bun.lock                            # Bun lock file
├── commitlint.config.js                # Commit message validation
├── docker-compose.yml                  # Service orchestration
├── package.json                        # Bun configuration (linting, commits)
├── pyproject.toml                      # Python project metadata (root)
├── renovate.json                       # Renovate configuration
├── CHANGELOG.md                        # Version history
├── CONTRIBUTING.md                     # Contribution guidelines
├── LICENSE                             # MIT License
└── README.md                           # Main project documentation
```

---

## 🎯 Essential Rules

### Critical Rules (Never Override)

1. **Never commit secrets** - `.env` files, passwords, API keys, tokens
2. **Never commit to `main` directly** - Always use feature branches via PR
3. **Never commit to `develop` directly** - Always use feature/fix branches
4. **Never force-push to protected branches** - `main`, `develop`, `release/*`
5. **Always read before modifying** - Understand existing code before changing
6. **Always consult documentation** - Check `docs/` before any modification

### Fundamental Principles

1. **Read before modifying** - Always read a file before proposing changes
2. **Consult documentation first** - Check relevant `docs/` files before any task
3. **Respect existing patterns** - Follow the style and conventions already in place
4. **Minimize changes** - Only modify what is necessary for the task
5. **Document changes** - Update relevant docs if behavior changes
6. **Run checks before committing** - Lint, type-check, and test
7. **Use English for all content** - Documentation, code, commits, messages

---

## 💬 Communication Protocols

### Language Rule

**All written content must be in English**, regardless of the user's prompt language:

- Documentation (markdown files, comments)
- Commit messages
- Tasks and subtasks
- Epics and user stories
- Code comments and docstrings
- Variable and function names
- Error messages and logs
- User-facing text

### Commit Convention

This project accepts **Gitmoji** or **Conventional Commits**:

```bash
# Interactive gitmoji tool (recommended)
bun run commit
```

**Gitmoji Format:** `<emoji> <description>`

| Emoji | Description | When to Use |
|-------|-------------|-------------|
| ✨ | New feature | Adding new functionality |
| 🐛 | Bug fix | Fixing a bug |
| 📝 | Documentation | Documentation changes |
| ♻️ | Refactor | Code refactoring |
| 🔧 | Configuration | Configuration changes |
| 💄 | UI / styling | UI and styling changes |
| 🔒 | Security fix | Security-related changes |
| 🐳 | Docker-related | Docker and container changes |
| ✅ | Add tests | Adding tests |
| 🔥 | Remove code/files | Removing code or files |
| ⬆️ | Upgrade dependency | Dependency updates |
| 📦 | Add dependency | Adding new dependencies |
| 🗑 | Deprecate | Deprecating code |

**Conventional Commits Format:** `<type>(scope): <description>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

Examples:
- `feat(api): Add task filtering endpoint`
- `fix(db): Fix connection retry on startup`
- `docs: Update Docker Compose networking`
- `refactor(web): Extract TodoItem component`

Full gitmoji reference: [gitmoji.dev](https://gitmoji.dev)

---

## 🏆 Priorities (In Order)

1. **Functionality** - Code must work end-to-end (API + frontend)
2. **Type safety** - TypeScript strict, Pydantic schemas at boundaries
3. **Readability** - Code must be understandable and maintainable
4. **Consistency** - Follow existing patterns and conventions
5. **Simplicity** - Avoid over-engineering; keep it simple

---

## 📋 Code Generation Preferences

### Python

- PEP 8 compliance
- Type hints for all functions and variables
- Pydantic models for request/response validation
- SQLAlchemy 2.0 ORM style
- FastAPI best practices

### TypeScript / Svelte

- Strict mode enabled
- Explicit types at module boundaries
- Svelte 5 runes (`$state`, `$derived`, `$effect`, `$props`)
- **NO legacy reactive syntax** (`$:`) - use runes instead
- Type-safe API client
- Proper error handling

### Tailwind CSS v4

- Utility classes inline
- Prefer composition over `@apply`
- Single `@import 'tailwindcss'` in `app.css`

### Markdown

- Follow markdownlint rules
- No trailing whitespace
- Single blank line between sections
- Fenced code blocks with language identifier

### YAML

- Follow yamllint rules
- Consistent 2-space indentation
- Quoted strings when necessary

### SQL

- Uppercase keywords (SELECT, INSERT, WHERE, etc.)
- snake_case for table and column names
- Proper indentation and formatting

---

## 🚫 Behaviors to Avoid

### General

- Do not create unnecessary files
- Do not add dependencies without justification
- Do not modify project structure without discussion
- Do not ignore linting errors
- Do not comment out dead code - delete it
- Do not hardcode secrets or database credentials
- Do not commit `.env` files or files in `.gitignore`

### Frontend-Specific

- Do not bypass the Vite `/api` proxy with hardcoded `localhost:8000` URLs
- Do not mix Svelte 5 runes with legacy `$:` reactive syntax
- Do not use `any` types in TypeScript
- Do not add unused dependencies to `package.json`

### Backend-Specific

- Do not expose database connection strings in logs
- Do not use raw SQL without parameterization (SQL injection risk)
- Do not commit database files (`.db`, `.sqlite`)
- Do not hardcode database URLs

### Documentation-Specific

- Do not add files without updating the documentation index
- Do not create documentation that duplicates existing docs
- Do not use inconsistent terminology

---

## ✅ Pre-commit Checklist

Before committing any changes, ensure:

- [ ] `bun run lint` passes (markdown and YAML linting)
- [ ] Frontend type-checks: `cd web && bun run check`
- [ ] Frontend builds: `cd web && bun run build`
- [ ] API endpoints respond correctly: `curl http://localhost:8000/todos`
- [ ] Web UI loads and functions correctly
- [ ] All relevant tests pass
- [ ] Documentation updated if behavior changed
- [ ] Commit message follows gitmoji or conventional commits convention
- [ ] No secrets or `.env` files are committed
- [ ] No files in `.gitignore` are committed

---

## 🎓 Development Workflow

### Standard Feature Development

```bash
# 1. Update local main
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/short-description

# 3. Develop
# API (terminal 1)
cd api
uv sync                    # Setup virtual environment
uv run uvicorn main:app --reload

# Frontend (terminal 2)
cd web
bun install
bun run dev

# 4. Lint, test, commit
bun run lint
bun run commit  # or use git commit with proper message

# 5. Push and create PR
git push origin feature/short-description
```

### Rebase Workflow (Required)

```bash
# Always rebase on develop before opening PR
git checkout develop
git pull origin develop
git checkout feature/your-feature
git rebase origin/develop

# If conflicts, resolve and continue
git add .
git rebase --continue

# Force push (allowed on feature branches)
git push origin feature/your-feature --force-with-lease
```

**Golden Rules:**
1. Never `git merge main` into `develop` - use `git rebase origin/main`
2. Always rebase your branch on `develop` before opening a PR
3. Never force-push to `main`, `develop`, or `release/*`

---

## 🌐 Network Configuration

### Docker Networks

| Network | Services | Purpose |
|---------|----------|---------|
| `traefik_frontend` | web (nginx) | Frontend network for web traffic |
| `traefik_backend` | api, db | Backend network for internal communication |

### Port Mapping

| Service | Container Port | Host Port | Protocol |
|---------|----------------|-----------|----------|
| web (nginx) | 80 | 8080 | HTTP |
| api (uvicorn) | 8000 | 8000 | HTTP |
| db (PostgreSQL) | 5432 | - | Internal only |

### API Endpoints

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/todos` | List all todos | `TodoResponse[]` |
| GET | `/todos/{id}` | Get todo by ID | `TodoResponse` |
| POST | `/todos` | Create new todo | `TodoResponse` (201) |
| PUT | `/todos/{id}` | Update todo | `TodoResponse` |
| DELETE | `/todos/{id}` | Delete todo | 204 No Content |

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 🔍 Environment Variables

### Docker Compose Level (`.env`)

```env
# PostgreSQL credentials
POSTGRES_USER=todouser
POSTGRES_PASSWORD=todopassword
POSTGRES_DB=tododb

# Database URL for API
DATABASE_URL=postgresql://todouser:todopassword@db:5432/tododb
```

### API Level (`api/.env` or `api/.env.example`)

```env
# Database connection (overrides Compose-level DATABASE_URL)
DATABASE_URL=sqlite:///./todo.db
```

### Web Level (`web/.env` or `web/.env.example`)

```env
# Public API base URL (for frontend)
PUBLIC_API_BASE=/api
```

**Important:** Never commit `.env` files. Use `.env.example` templates.

---

## 🎯 Project Conventions

### Branch Naming

```text
feature/short-description          # New features
git checkout -b feature/add-filtering

fix/issue-number-description        # Bug fixes
git checkout -b fix/123-invalid-input

refactor/component-name            # Code refactoring
git checkout -b refactor/todo-service

docs/update-readme                 # Documentation updates
git checkout -b docs/update-readme

hotfix/issue-description           # Urgent fixes
git checkout -b hotfix/security-vulnerability
```

### File Naming Conventions

| Context | Convention | Example |
|---------|------------|---------|
| Python modules | snake_case | `database.py`, `crud_operations.py` |
| TypeScript files | camelCase or kebab-case | `api.ts`, `todo-utils.ts` |
| Svelte components | PascalCase | `TodoItem.svelte`, `FilterBar.svelte` |
| Config files | kebab-case | `docker-compose.yml`, `vite.config.ts` |
| Dockerfiles | PascalCase + dot | `Dockerfile`, `Dockerfile.api` |
| Documentation | UPPER_SNAKE_CASE | `TECHNICAL_GUIDE.md`, `PROJECT_STRUCTURE.md` |
| Test files | `test_` prefix | `test_crud.py`, `test_api_integration.py` |

### Code Organization

#### Python Files

```python
# 1. Standard library imports
import os
from datetime import datetime
from typing import Optional

# 2. Third-party imports
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session

# 3. Local imports
from database import get_db, Base
from models import Todo
from schemas import TodoCreate, TodoResponse

# 4. Constants
MAX_TITLE_LENGTH = 200
DEFAULT_PAGE_SIZE = 10

# 5. Code
class TodoService:
    ...
```

#### TypeScript Files

```typescript
// 1. External imports
import { writable } from 'svelte/store';
import type { Todo } from './types';

// 2. Local imports
import { api } from '$lib/api';
import { TodoItem } from '$lib/components/TodoItem.svelte';

// 3. Constants
const MAX_TITLE_LENGTH = 200;

// 4. Types
interface TodoFilter {
  status: 'all' | 'active' | 'completed';
}

// 5. Functions / Components
```

---

## 🛡️ Security Guidelines

### Secrets Management

- Use environment variables for all secrets
- Use `.env.example` to document required variables
- Add `.env` to `.gitignore`
- Use different credentials for development and production
- Never hardcode secrets in source code
- Never commit `.env` files
- Never log sensitive data

### Security Hooks

Security hooks are implemented in `.vibe/hooks/` directory:

- **pre-commit/secrets-hook.py** - Scans for secrets before commit
- **pre-push/secrets-hook.py** - Scans for secrets before push

These hooks detect:
- API keys and tokens
- Passwords and credentials
- Database connection strings
- Private keys
- Sensitive URLs

### Docker Security

- Run containers as non-root users
- Use minimal base images (`python:3.12-slim`)
- Set resource limits in Compose
- Configure restart policies appropriately
- Use named volumes for persistent data
- Isolate services on separate networks
- Never expose database ports to host
- Never run containers as root

---

## 🤖 AI Agent Extensions

This project includes Mistral Vibe extensions for enhanced AI agent capabilities:

### Skills (Auto-triggered)

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `todo-management` | Todo-related tasks | Manage todo items, projects, workflows |
| `docker-helper` | Docker commands and operations | Assist with Docker setup, debugging, deployment |
| `code-reviewer` | Code review requests | Analyze code quality, suggest improvements |

**Location:** `.vibe/skills/`

### MCP Servers (Model Context Protocol)

| MCP Server | Purpose | Capabilities |
|------------|---------|--------------|
| `file-indexer` | File system indexing | Search, analyze, and retrieve file contents |
| `docker-monitor` | Docker status monitoring | Check container status, logs, resource usage |
| `git-analyzer` | Git repository analysis | Analyze commits, branches, diffs, blames |

**Location:** `.vibe/mcp/`

### Hooks (Event-driven)

| Hook | Event | Purpose |
|------|-------|---------|
| `pre-commit/secrets-hook.py` | Pre-commit | Detect and block secrets from being committed |
| `pre-push/secrets-hook.py` | Pre-push | Detect and block secrets from being pushed |

**Location:** `.vibe/hooks/`

### Slash Commands (Manual)

| Command | Usage | Purpose |
|---------|-------|---------|
| `/todo <action>` | `/todo add Buy milk` | Manage todo items directly in chat |
| `/docker <action>` | `/docker status` | Execute Docker operations |

**Location:** `.vibe/commands/`

---

## 📖 Related Files

- [`docs/AGENTS.md`](./docs/AGENTS.md) - Extended AI assistant guide
- [`api/AGENTS.md`](./api/AGENTS.md) - API-specific AI instructions
- [`web/AGENTS.md`](./web/AGENTS.md) - Frontend-specific AI instructions
- [`CONTRIBUTING.md`](./CONTRIBUTING.md) - Contribution guidelines
- [`docs/CONVENTIONS.md`](./docs/CONVENTIONS.md) - Detailed coding conventions

---

*Last updated: 2026-06-23*
*Generated by Mistral Vibe for comprehensive static context*
