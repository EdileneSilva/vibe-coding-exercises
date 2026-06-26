# Tasks

Project task tracking based on the project brief.

## Part 1: Multi-Container Application

### PostgreSQL Setup

- [x] Pull and configure the official PostgreSQL Docker image (postgres:16-alpine)
- [x] Create the `tododb` database with dedicated user
- [x] Configure a Docker volume (`pgdata`) for data persistence
- [x] Test database connectivity from a client
- [x] Configure healthcheck for PostgreSQL service
- [x] Set resource limits (CPU: 0.50, Memory: 256M)

### FastAPI API Dockerization

- [x] Adapt `database.py` to connect to PostgreSQL (via `DATABASE_URL` override)
- [x] Create SQLAlchemy models for the Todo entity with all fields
- [x] Create Pydantic schemas for request/response validation
- [x] Implement CRUD operations (create, read, update, delete)
- [x] Create `Dockerfile` with Python slim base image and uv
- [x] Configure Uvicorn as the ASGI server
- [x] Add health check endpoints (`/health`, `/health/db`, `/metrics`)
- [x] Add request logging middleware
- [x] Add CORS middleware configuration
- [x] Test API endpoints via Swagger UI
- [ ] Push API image to Docker Hub

### Web (SvelteKit) Dockerization

- [x] Configure SvelteKit with `@sveltejs/adapter-static` and `fallback: 'index.html'`
- [x] Implement Svelte UI with task list display
- [x] Implement add, edit, delete, and toggle task actions with optimistic updates
- [x] Implement filtering (All, Active, Completed) with counts
- [x] Implement error handling with inline alerts
- [x] Create `Dockerfile` (multi-stage: bun builder + nginx-unprivileged runtime)
- [x] Add `web/nginx.conf` reverse-proxying `/api/*` to the api service
- [x] Configure Vite proxy for `/api` in development
- [x] Test web-to-API communication through the nginx proxy
- [x] Add environment variable support (`PUBLIC_API_BASE`)
- [ ] Push web image to Docker Hub

### Docker Compose Orchestration

- [x] Create `docker-compose.yml` with all three services (db, api, web)
- [x] Configure internal Docker networks (backend, frontend)
- [x] Set up environment variable substitution from `.env`
- [x] Configure service startup dependencies (`depends_on` + healthcheck)
- [x] Create `.env.example` with documented variables
- [x] Test full orchestration with `docker compose up --build`
- [x] Configure healthchecks for all services
- [x] Set resource limits for all services
- [x] Use non-root users in all containers

---

## Part 2: Security and Optimization

### Container Security

- [x] Create non-root users in all Dockerfiles (api: `appuser`; web: `nginx-unprivileged` image)
- [x] Restrict PostgreSQL to internal backend network only (`internal: true`)
- [x] Ensure no direct web-to-database communication (web is only on `frontend`)
- [x] Verify `.env` file is in `.gitignore`
- [x] Use specific image tags (no `latest`) — `postgres:16-alpine`, `oven/bun:1-alpine`,
      `nginxinc/nginx-unprivileged:1.27-alpine`, `python:3.12-slim`
- [x] Add `.gitleaks.toml` for secrets detection configuration
- [x] Implement pre-commit and pre-push secrets scanning hooks

### Resource Management

- [x] Define CPU and memory limits for PostgreSQL in Compose (0.50 CPU, 256M memory)
- [x] Define CPU and memory limits for API in Compose (0.50 CPU, 256M memory)
- [x] Define CPU and memory limits for the web in Compose (0.25 CPU, 256M memory)
- [x] Optimize Docker images (slim base, `uv sync --frozen --no-dev`, `bun install --frozen-lockfile`,
      multi-stage build)

### Orchestration Security

- [x] Configure `restart: unless-stopped` for all services
- [x] Verify network isolation (test external connection rejection)
- [x] Add healthchecks for all services with appropriate intervals
- [x] Configure proper startup dependencies and wait conditions
- [ ] Run Trivy vulnerability scan on all images (optional)

---

## Part 3: Cloud Deployment (Optional)

- [ ] Create Railway account and project
- [ ] Deploy PostgreSQL via Railway plugin
- [ ] Deploy FastAPI service with `DATABASE_URL` from Railway
- [ ] Deploy web service pointing at the public API URL (or co-host behind nginx)
- [ ] Test CRUD operations on deployed application
- [ ] Document deployment steps in README.md
- [ ] Take screenshots of deployed application

---

### Testing and Quality Assurance

- [x] Create comprehensive API test suite (test_api.py, test_crud.py)
- [x] Create frontend test suite (api.test.ts, filter.test.ts)
- [x] Create E2E test suite with Playwright (todo.spec.ts)
- [x] Configure pytest with fixtures for database sessions
- [x] Configure vitest for frontend testing
- [x] Configure Playwright for E2E testing
- [x] Add test scripts to package.json

### AI Agent Extensions

- [x] Create Mistral Vibe skills (todo-management, docker-helper, code-reviewer)
- [x] Create MCP servers (file-indexer, docker-monitor, git-analyzer)
- [x] Create pre-commit and pre-push hooks for secrets detection
- [x] Create slash commands (/todo, /docker)
- [x] Create comprehensive AGENTS.md files (root, api, web, docs)
- [x] Create complete project documentation

### Completed (Template Setup)

- [x] Workflow release with changelog and GitHub release
- [x] Clean all docs
- [x] Issue and PR templates (bug.md, bug_report.yml, feature_request.yml, config.yml)
- [x] Dependabot configuration (.github/dependabot.yml, dependabot-lockfile.yml)
- [x] Renovate configuration
- [x] Commitlint (gitmoji) configuration
- [x] Changelog (gitmoji + conventional commits)
- [x] Semantic-release (gitmoji) configuration
- [x] EditorConfig for consistent editor settings
- [x] CONTRIBUTING.md with contribution guidelines
- [x] Adapt all documentation files for the SvelteKit + FastAPI stack
- [x] Add comprehensive type hints and docstrings
- [x] Add security configurations (.gitleaks.toml, secrets scanning)

---

*Last updated: 2026-06-26*
