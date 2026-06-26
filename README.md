# Docker To-Do App

<!-- markdownlint-disable -->
<p align="center">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/docker/docker-original.svg" alt="Docker" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/fastapi/fastapi-original.svg" alt="FastAPI" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/svelte/svelte-original.svg" alt="Svelte" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/tailwindcss/tailwindcss-original.svg" alt="Tailwind CSS" width="80" height="80" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/postgresql/postgresql-original.svg" alt="PostgreSQL" width="80" height="80" />
</p>

<p align="center">
  <strong>Dockerized To-Do application with FastAPI, SvelteKit, Tailwind v4, and PostgreSQL</strong>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" />
  </a>
  <a href="https://gitmoji.dev">
    <img src="https://img.shields.io/badge/gitmoji-%20😜%20😍-FFDD67.svg" alt="Gitmoji" />
  </a>
</p>
<!-- markdownlint-restore -->

---

A multi-container To-Do application orchestrated with Docker Compose, featuring a **FastAPI**
REST API with health check endpoints, a **SvelteKit + Tailwind v4** frontend served by **nginx**, 
and a **PostgreSQL** database. The project includes comprehensive testing (API, frontend, E2E),
AI agent extensions, and robust security configurations.

## Architecture

```text
┌──────────────────────────────────────────────────────────────────┐
│                       Docker Compose                             │
│                                                                  │
│  ┌──────────────┐      ┌──────────────┐      ┌────────────────┐  │
│  │  web (nginx) │ ───▶ │  api (uvic.) │ ───▶ │   db (Postgres)│  │
│  │   :8080      │      │   :8000      │      │     :5432      │  │
│  └──────────────┘      └──────────────┘      └────────────────┘  │
│       ▲                                                ▲         │
│       │                                                │         │
│   (browser)                                     [pgdata volume]  │
└──────────────────────────────────────────────────────────────────┘
        frontend network             backend network
```

The web container serves the prebuilt SvelteKit static bundle and proxies `/api/*` to the
FastAPI service through the internal Docker network — no CORS configuration is needed. The API 
includes health check endpoints (`/health`, `/health/db`, `/metrics`) and request logging middleware.

## Tech Stack

| Service  | Technology                       | Description                                |
|----------|----------------------------------|--------------------------------------------|
| api      | FastAPI + Uvicorn                | REST API with CRUD operations & health checks |
| web      | SvelteKit + Tailwind v4 / nginx  | Static SPA + reverse proxy to the API      |
| db       | PostgreSQL 16                    | Persistent data storage                    |
| ORM      | SQLAlchemy 2                     | Database abstraction layer                 |
| Bundler  | Vite                             | Build the SvelteKit app to static assets   |
| Compose  | Docker Compose                   | Multi-container orchestration              |
| E2E Tests | Playwright                      | End-to-end browser testing                 |
| Package Manager (JS) | Bun                     | JavaScript runtime and package manager     |
| Package Manager (Python) | uv                  | Python dependency management                 |

## Prerequisites

- [Docker](https://docs.docker.com/get-started/) >= 24.0
- [Docker Compose](https://docs.docker.com/compose/) >= 2.20
- [Bun](https://bun.sh/) >= 1.3 (lint tooling and frontend development)
- [uv](https://docs.astral.sh/uv/) >= 0.5 (Python API development)

## Quick Start

### 1. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your Postgres credentials (used by Compose). Per-project examples live at
`api/.env.example` (API runtime config) and `web/.env.example` (web public env).

```env
POSTGRES_USER=todouser
POSTGRES_PASSWORD=todopassword
POSTGRES_DB=tododb
DATABASE_URL=postgresql://todouser:todopassword@db:5432/tododb
```

### 2. Build and run

```bash
docker compose up --build       # Foreground
docker compose up --build -d    # Detached
```

### 3. Access the application

| Service               | URL                                       |
|-----------------------|-------------------------------------------|
| Web UI                | <http://localhost:8080>                   |
| FastAPI Swagger UI    | <http://localhost:8000/docs>              |
| FastAPI ReDoc         | <http://localhost:8000/redoc>             |

## API Endpoints

| Method   | Endpoint        | Description       |
|----------|-----------------|-------------------|
| `GET`    | `/health`       | Health check      |
| `GET`    | `/health/db`    | Database health check |
| `GET`    | `/metrics`      | Application metrics |
| `GET`    | `/todos`        | List all tasks    |
| `GET`    | `/todos/{id}`   | Get a task by ID  |
| `POST`   | `/todos`        | Create a task     |
| `PUT`    | `/todos/{id}`   | Update a task     |
| `DELETE` | `/todos/{id}`   | Delete a task     |

## Project Structure

```text
.
├── api/                        # FastAPI service
│   ├── main.py                 # Entry point with routes, health checks, middleware
│   ├── database.py             # Database connection and session management
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic validation schemas
│   ├── crud.py                 # Database CRUD operations
│   ├── tests/                  # API unit and integration tests
│   │   ├── conftest.py
│   │   ├── test_api.py
│   │   └── test_crud.py
│   ├── pyproject.toml          # Python project metadata
│   ├── uv.lock                 # Locked dependencies
│   ├── Dockerfile              # API container image
│   ├── .dockerignore
│   └── .env.example
├── web/                        # SvelteKit + Tailwind v4 frontend
│   ├── src/
│   │   ├── lib/
│   │   │   ├── api.ts          # Typed fetch client
│   │   │   ├── types.ts        # TypeScript interfaces
│   │   │   └── components/
│   │   │       └── TodoItem.svelte
│   │   └── routes/
│   │       ├── +layout.svelte
│   │       └── +page.svelte
│   ├── tests/                  # Frontend tests
│   │   ├── api.test.ts
│   │   ├── filter.test.ts
│   │   └── mocks/
│   ├── nginx.conf              # Reverse proxy + SPA fallback
│   ├── svelte.config.js
│   ├── vite.config.ts
│   ├── package.json
│   ├── Dockerfile              # Web image (multi-stage)
│   ├── .dockerignore
│   └── .env.example
├── e2e/                        # End-to-end tests
│   ├── tests/
│   │   └── todo.spec.ts       # Playwright test suite
│   ├── playwright.config.ts
│   ├── package.json
│   └── Dockerfile
├── .vibe/                      # Mistral Vibe extensions
│   ├── skills/
│   ├── mcp/
│   ├── hooks/
│   └── commands/
├── scripts/                   # Utility scripts
│   ├── commit-msg-hook.js
│   ├── pre-commit-hook.js
│   ├── pre-push-hook.js
│   └── secrets-scan.js
├── .github/                    # GitHub configuration
│   └── workflows/
│       ├── build.yml
│       ├── lint.yml
│       ├── security.yml
│       ├── setup.yml
│       └── test.yml
├── docs/                       # Documentation
├── docker-compose.yml          # Service orchestration
├── .env.example                # Compose-level env (Postgres credentials)
├── package.json                # Root package.json (linting, commits)
├── pyproject.toml              # Root pyproject.toml
└── README.md                   # This file
```

## Local Development (without Docker)

The API can run against SQLite without Docker — useful for quick iteration:

```bash
# API
cd api
uv sync                            # creates .venv and installs dependencies
uv run uvicorn main:app --reload   # http://localhost:8000

# Frontend (in another terminal)
cd web
bun install
bun run dev                        # http://localhost:5173 (proxies /api → :8000)

# E2E tests (requires API and web running)
cd e2e
bun install
bun run test                       # Run Playwright tests
```

## Development Commands

```bash
# Docker
docker compose up --build       # Build and start all services
docker compose up --build -d    # Build and start in background
docker compose down             # Stop all services
docker compose down -v          # Stop and remove volumes
docker compose logs -f          # Follow all service logs
docker compose exec api bash    # Enter API container
docker compose exec web bash    # Enter web container

# Linting (requires bun install at root)
bun install           # Install linting dependencies
bun run lint          # Lint markdown and yaml
bun run lint:md       # Lint markdown only
bun run lint:md:fix   # Auto-fix markdown issues
bun run lint:yaml     # Lint yaml files
bun run lint:commit   # Validate last commit message

# Frontend
cd web && bun install           # Install dependencies
cd web && bun run check         # Type-check with svelte-check + tsc
cd web && bun run dev           # Start dev server at http://localhost:5173
cd web && bun run build         # Build static bundle (used by web/Dockerfile)
cd web && bun run preview        # Preview production build
cd web && bun test              # Run frontend tests (vitest)

# API
cd api && uv sync               # Setup Python virtual env and dependencies
cd api && uv run uvicorn main:app --reload  # Start API at http://localhost:8000
cd api && uv run pytest tests/   # Run API tests

# E2E Tests
cd e2e && bun install           # Install Playwright and browsers
cd e2e && bun run test          # Run end-to-end tests

# Git
bun run commit                  # Interactive gitmoji commit tool
```

## Documentation

| File | Description |
|------|-------------|
| [`docs/AGENTS.md`](docs/AGENTS.md) | AI assistant guide and conventions |
| [`docs/CONVENTIONS.md`](docs/CONVENTIONS.md) | Code style and git conventions |
| [`docs/TECHNICAL_GUIDE.md`](docs/TECHNICAL_GUIDE.md) | Technical implementation and deployment |
| [`docs/PROJECT_STRUCTURE.md`](docs/PROJECT_STRUCTURE.md) | Directory and file organization |
| [`docs/FEATURES.md`](docs/FEATURES.md) | Epics and user stories |
| [`docs/COMPONENT_REFERENCE.md`](docs/COMPONENT_REFERENCE.md) | API endpoints and Svelte components |
| [`docs/SCREEN_FLOW.md`](docs/SCREEN_FLOW.md) | Web app navigation flows |
| [`docs/TASKS.md`](docs/TASKS.md) | Project task tracking |
| [`docs/DESIGN_SYSTEM.md`](docs/DESIGN_SYSTEM.md) | Tailwind v4 UI design system |
| [`docs/briefs/docker.md`](docs/briefs/docker.md) | Original Docker project brief |
| [`docs/briefs/agentic-coding.md`](docs/briefs/agentic-coding.md) | Agentic coding project brief |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Contribution guidelines |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history |
| [`AGENTS.md`](AGENTS.md) | Master AI assistant guide with full project context |

## License

MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Maxime Lenne** - [maxime-lenne.fr](https://maxime-lenne.fr)
