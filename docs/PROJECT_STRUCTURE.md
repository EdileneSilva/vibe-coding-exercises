# Project Structure

## Directory Organization

```text
todo-app/
├── api/                                # FastAPI application
│   ├── main.py                         # API entry point, routes, health checks, middleware
│   ├── database.py                     # Database connection, session factory, Base class
│   ├── models.py                       # SQLAlchemy ORM models (Todo table)
│   ├── schemas.py                      # Pydantic validation schemas for request/response
│   ├── crud.py                         # Database CRUD operations (create, read, update, delete)
│   ├── tests/                          # API unit and integration tests
│   │   ├── __init__.py
│   │   ├── conftest.py                 # Pytest fixtures (db_session, client)
│   │   ├── test_api.py                 # API endpoint integration tests
│   │   └── test_crud.py                # CRUD operation unit tests
│   ├── pyproject.toml                  # Python project metadata and dependencies
│   ├── uv.lock                         # Locked dependency versions (managed by uv)
│   ├── Dockerfile                      # API container image (python:3.12-slim + uv)
│   ├── .dockerignore                   # Files to exclude from API Docker build
│   └── .env.example                    # API runtime environment template
│
├── web/                                # SvelteKit + Tailwind v4 frontend
│   ├── src/
│   │   ├── app.html                    # HTML shell template
│   │   ├── app.css                     # Tailwind v4 entry point (@import 'tailwindcss')
│   │   ├── app.d.ts                    # SvelteKit type augmentation
│   │   ├── lib/
│   │   │   ├── api.ts                  # Typed fetch client for API communication
│   │   │   ├── types.ts                # Shared TypeScript type definitions (Todo, Filter, etc.)
│   │   │   └── components/
│   │   │       └── TodoItem.svelte     # Individual todo item component with edit/delete
│   │   └── routes/
│   │       ├── +layout.svelte          # Root layout with Tailwind CSS import
│   │       └── +page.svelte            # Main todo list page with state management
│   ├── tests/                          # Frontend tests (vitest)
│   │   ├── api.test.ts                 # API client tests with fetch mocking
│   │   ├── filter.test.ts              # Filter logic unit tests
│   │   └── mocks/
│   │       └── env-public.ts           # Mock environment variables
│   ├── package.json                    # Frontend dependencies and scripts
│   ├── svelte.config.js                # SvelteKit configuration with static adapter
│   ├── vite.config.ts                  # Vite configuration with /api proxy for development
│   ├── tsconfig.json                   # TypeScript configuration
│   ├── nginx.conf                      # Production nginx reverse proxy configuration
│   ├── Dockerfile                      # Web container (multi-stage: bun + nginx-unprivileged)
│   ├── .dockerignore                   # Files to exclude from web Docker build
│   └── .env.example                    # Web public environment template
│
├── e2e/                               # End-to-end tests
│   ├── tests/
│   │   └── todo.spec.ts               # Playwright E2E test suite (API + UI tests)
│   ├── playwright.config.ts            # Playwright test configuration
│   ├── package.json                    # E2E dependencies (@playwright/test)
│   └── Dockerfile                      # E2E test container image
│
├── .vibe/                             # Mistral Vibe extensions
│   ├── skills/                         # Auto-triggered specialized skills
│   │   ├── todo-management/
│   │   │   └── skill.md                # Todo management skill definition
│   │   ├── docker-helper/
│   │   │   └── skill.md                # Docker operations skill definition
│   │   └── code-reviewer/
│   │       └── skill.md                # Code review skill definition
│   ├── mcp/                            # Model Context Protocol servers
│   │   ├── file-indexer/
│   │   │   ├── server.py               # File system indexing MCP server
│   │   │   └── README.md               # MCP server documentation
│   │   ├── docker-monitor/
│   │   │   ├── server.py               # Docker status monitoring MCP server
│   │   │   └── README.md
│   │   └── git-analyzer/
│   │       ├── server.py               # Git repository analysis MCP server
│   │       └── README.md
│   ├── hooks/                          # Event-driven hooks
│   │   ├── pre-commit/
│   │   │   └── secrets_hook.py         # Secrets detection pre-commit hook
│   │   └── pre-push/
│   │       └── secrets_hook.py         # Secrets detection pre-push hook
│   └── commands/                       # Slash commands
│       ├── todo-command/
│       │   ├── command.md              # /todo command definition
│       │   └── handler.py              # Command handler
│       └── docker-command/
│           ├── command.md              # /docker command definition
│           └── handler.py
│
├── scripts/                          # Utility and security scripts
│   ├── commit-msg-hook.js             # Commit message validation hook (commitlint)
│   ├── pre-commit-hook.js             # Pre-commit validation hook
│   ├── pre-push-hook.js               # Pre-push validation hook
│   └── secrets-scan.js                # Secrets scanning utility
│
├── .github/                            # GitHub configuration
│   ├── workflows/                      # GitHub Actions CI/CD workflows
│   │   ├── build.yml                  # Docker image build workflow
│   │   ├── dependabot-lockfile.yml    # Dependabot lockfile update workflow
│   │   ├── lint.yml                    # Markdown and YAML linting workflow
│   │   ├── security.yml                # Security scanning workflow
│   │   ├── setup.yml                   # Repository setup workflow
│   │   └── test.yml                    # Test execution workflow
│   ├── ISSUE_TEMPLATE/                 # GitHub issue templates
│   │   ├── bug.md                      # Bug report template
│   │   ├── bug_report.yml              # Bug report template (YAML format)
│   │   ├── config.yml                 # Issue template configuration
│   │   └── feature_request.yml         # Feature request template
│   ├── pull_request_template.md        # Pull request template
│   ├── CODEOWNERS                      # Code ownership rules
│   ├── dependabot.yml                  # Dependabot configuration
│   └── settings.yml                    # Repository settings
│
├── docs/                               # Documentation
│   ├── AGENTS.md                       # Extended AI assistant guide
│   ├── PROJECT_STRUCTURE.md            # This file - directory layout
│   ├── CONVENTIONS.md                  # Code style and git conventions
│   ├── TECHNICAL_GUIDE.md              # Technical implementation details
│   ├── DESIGN_SYSTEM.md                # Tailwind v4 UI design system
│   ├── COMPONENT_REFERENCE.md          # API endpoints and Svelte components
│   ├── FEATURES.md                     # Epics, user stories, feature status
│   ├── SCREEN_FLOW.md                  # Web app screen flows and navigation
│   ├── TASKS.md                        # Project task tracking and backlog
│   └── briefs/
│       ├── docker.md                  # Original Docker project brief (French)
│       └── agentic-coding.md           # Agentic coding project brief (French)
│
├── docker-compose.yml                  # Service orchestration (db, api, web)
├── .env.example                        # Docker Compose environment variables template
├── .env                              # Environment variables (gitignored)
├── .gitleaks.toml                     # Gitleaks secrets detection configuration
├── .env                              # Environment variables (gitignored)
├── .gitignore                          # Git ignore rules
├── .gitmoji.json                       # Gitmoji-cli configuration
├── .markdownlint.json                  # Markdown linting rules
├── .yamllint.yml                       # YAML linting rules
├── .editorconfig                       # Editor settings (consistent across IDEs)
├── .releaserc.json                     # Semantic-release configuration
├── .husky/                             # Git hooks managed by Husky
│   └── pre-commit                      # Pre-commit hook script
├── bun.lock                            # Bun lock file (frontend dependencies)
├── commitlint.config.js                # Commit message validation configuration
├── package.json                        # Root package.json (linting, commits, test scripts)
├── pyproject.toml                      # Root pyproject.toml (Python project metadata)
├── renovate.json                       # Renovate automatic dependency updates configuration
├── CHANGELOG.md                        # Version history (gitmoji + conventional commits)
├── CONTRIBUTING.md                     # Contribution guidelines
├── LICENSE                             # MIT License
└── README.md                           # Main project documentation
```

---

## Application Code

### API (`api/`)

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization, route definitions, health check endpoints, request logging middleware, startup logic |
| `database.py` | SQLAlchemy engine, session factory, `get_db` dependency, Base class for models |
| `models.py` | SQLAlchemy ORM models (`Todo` table with id, title, description, completed, created_at, updated_at) |
| `schemas.py` | Pydantic models for request/response validation (TodoBase, TodoCreate, TodoUpdate, TodoResponse) |
| `crud.py` | Database CRUD operations (get_todos, get_todo, create_todo, update_todo, delete_todo) |
| `pyproject.toml` | Python project metadata, dependencies, pytest configuration |
| `uv.lock` | Locked dependency versions managed by uv |

### Web (`web/`)

| File | Purpose |
|------|---------|
| `src/routes/+layout.svelte` | Root layout, imports `app.css` for Tailwind styles |
| `src/routes/+page.svelte` | Main task list page with reactive state management, filters, form handling |
| `src/lib/components/TodoItem.svelte` | Single task row component with checkbox toggle, inline edit form, delete button |
| `src/lib/api.ts` | Typed fetch client targeting `/api` proxy with error handling and 204 support |
| `src/lib/types.ts` | Shared TypeScript interfaces (Todo, TodoCreate, TodoUpdate, Filter) |
| `src/app.html` | HTML shell template for SvelteKit |
| `src/app.css` | Tailwind v4 entry point with `@import 'tailwindcss'` |
| `vite.config.ts` | Vite plugins (Tailwind, SvelteKit) and `/api` development proxy configuration |
| `svelte.config.js` | SvelteKit adapter configuration with static adapter and fallback |
| `nginx.conf` | Production nginx reverse proxy with `/api/*` proxy to API service and SPA fallback |
| `package.json` | Frontend dependencies and scripts |
| `Dockerfile` | Multi-stage Docker build (bun for build, nginx-unprivileged for runtime) |

### E2E Tests (`e2e/`)

| File | Purpose |
|------|---------|
| `tests/todo.spec.ts` | Playwright test suite with API tests and UI tests (add, toggle, filter, delete) |
| `playwright.config.ts` | Playwright configuration with parallel execution, retry logic, and reporting |
| `package.json` | E2E dependencies (@playwright/test) |
| `Dockerfile` | E2E test container with bun and Playwright browsers |

---

## Configuration Files

### Project Configuration

| File | Purpose |
|------|---------|
| `package.json` (root) | Bun dependencies (linting, commits), scripts for lint, test, Docker operations |
| `pyproject.toml` (root) | Root Python project metadata |
| `bun.lock` (root) | Locked dependency versions for root package.json |
| `.gitmoji.json` | Gitmoji-cli configuration for interactive commit messages |
| `.env.example` | Docker Compose-level environment variables template (PostgreSQL credentials, DATABASE_URL) |
| `.gitleaks.toml` | Gitleaks configuration for secrets detection |

### Code Quality

| File | Purpose |
|------|---------|
| `.markdownlint.json` | Markdown linting rules (for markdownlint-cli) |
| `.yamllint.yml` | YAML linting rules (for yaml-lint) |
| `.editorconfig` | Editor settings for consistent coding style across IDEs |
| `commitlint.config.js` | Commit message validation configuration |

### CI/CD

| File | Purpose |
|------|---------|
| `.github/workflows/build.yml` | Docker image build workflow (API and web images) |
| `.github/workflows/lint.yml` | Markdown and YAML linting workflow on push/PR |
| `.github/workflows/release.yml` | Semantic release workflow for automated versioning |
| `.github/workflows/security.yml` | Security scanning workflow |
| `.github/workflows/setup.yml` | Repository setup workflow |
| `.github/workflows/test.yml` | Test execution workflow |
| `.github/workflows/dependabot-lockfile.yml` | Dependabot lockfile update workflow |
| `renovate.json` | Renovate configuration for automatic dependency updates |
| `.github/dependabot.yml` | Dependabot configuration for security updates |
| `.github/settings.yml` | Repository settings configuration |
| `.github/CODEOWNERS` | Code ownership rules for PR reviews |

### Git Hooks

| Directory/File | Purpose |
|---------------|---------|
| `.husky/` | Git hooks managed by Husky |
| `.husky/pre-commit` | Pre-commit hook script (runs linting and validation) |
| `scripts/commit-msg-hook.js` | Commit message validation hook (commitlint) |
| `scripts/pre-commit-hook.js` | Pre-commit validation hook |
| `scripts/pre-push-hook.js` | Pre-push validation hook |
| `scripts/secrets-scan.js` | Secrets scanning utility for pre-commit/pre-push |

### AI Agent Extensions

| Directory | Purpose |
|-----------|---------|
| `.vibe/skills/` | Auto-triggered specialized skills for AI agents |
| `.vibe/mcp/` | Model Context Protocol servers for enhanced AI capabilities |
| `.vibe/hooks/` | Event-driven hooks for secrets detection and security |
| `.vibe/commands/` | Slash commands for direct chat interactions |

---

## Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `AGENTS.md` | Extended AI assistant guide with documentation standards and workflows |
| `PROJECT_STRUCTURE.md` | This file - comprehensive directory and file organization |
| `CONVENTIONS.md` | Code style, naming conventions, git conventions, testing conventions |
| `TECHNICAL_GUIDE.md` | Technical implementation details (API, frontend, CI/CD, Docker) |
| `DESIGN_SYSTEM.md` | Tailwind v4 UI design system with color palette, layout, components |
| `COMPONENT_REFERENCE.md` | API endpoints, data models, Pydantic schemas, Svelte components |
| `FEATURES.md` | Epics, user stories, feature status, technical features |
| `SCREEN_FLOW.md` | Web app screen flows, user flows, API communication flow |
| `TASKS.md` | Project task tracking, completed tasks, backlog |
| `briefs/docker.md` | Original Docker project brief (French language) |
| `briefs/agentic-coding.md` | Agentic coding project brief (French language) |

---

*Last updated: 2026-06-26*
