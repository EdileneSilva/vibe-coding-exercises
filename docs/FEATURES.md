# Features

Application features organized by epics and user stories.
Each item is linked to a GitHub issue for tracking and status.

## Epics

| # | Epic | Description |
|---|------|-------------|
| 1 | Database & Persistence | Persist tasks via SQLAlchemy with SQLite by default and Postgres as an opt-in via `DATABASE_URL` |
| 2 | FastAPI Service | Implement and expose REST CRUD endpoints for todos with Pydantic validation |
| 3 | SvelteKit Frontend | Build a typed, reactive UI consuming the API through a Vite proxy, with Svelte 5 runes |
| 4 | Tailwind v4 Design System | Style the UI with Tailwind utilities and a small set of token roles (slate / indigo / red) |
| 5 | Tooling & DX | Lint, commit conventions, type-check, and CI to keep the repo healthy |

---

## User Stories

### Epic 1: Database & Persistence

| User Story | Priority |
|------------|----------|
| As a developer, I want SQLite as the default database so the app runs with no extra services | High |
| As a developer, I want SQLAlchemy to auto-create tables on API startup so onboarding is trivial | High |
| As a developer, I want to swap to PostgreSQL via `DATABASE_URL` without code changes | Medium |

### Epic 2: FastAPI Service

| User Story | Priority |
|------------|----------|
| As a user, I want CRUD endpoints (create, read, update, delete) for managing tasks | High |
| As a developer, I want Pydantic schemas for request/response validation with min/max length checks | High |
| As a developer, I want auto-generated Swagger UI and ReDoc available at `/docs` and `/redoc` | Medium |
| As a developer, I want a clean separation between routes (`main.py`), models, schemas, and CRUD helpers | Medium |

### Epic 3: SvelteKit Frontend

| User Story | Priority |
|------------|----------|
| As a user, I want to add, toggle, edit, and delete tasks from a single page | High |
| As a user, I want to filter tasks by status (All / Active / Completed) | High |
| As a user, I want to see total / active / completed counts at a glance | Medium |
| As a developer, I want a typed `api.ts` fetch client so frontend calls are checked at build time | High |
| As a developer, I want optimistic UI updates with rollback on error so the app feels responsive | Medium |
| As a developer, I want the dev server to proxy `/api/*` to the FastAPI service so no CORS is needed | High |

### Epic 4: Tailwind v4 Design System

| User Story | Priority |
|------------|----------|
| As a user, I want a clean, accessible interface with clear status indicators | High |
| As a developer, I want Tailwind v4's CSS-first setup (no JS config) so the toolchain stays small | Medium |
| As a developer, I want documented color, spacing, and typography roles in `DESIGN_SYSTEM.md` | Medium |

### Epic 5: Tooling & DX

| User Story | Priority |
|------------|----------|
| As a developer, I want `bun run lint` to validate markdown and yaml on commit | High |
| As a developer, I want commitlint + gitmoji to enforce a consistent commit style | High |
| As a developer, I want `bun run check` to type-check the SvelteKit app | High |
| As a developer, I want CI to lint on every push and PR to `main`/`develop` | Medium |
| As a developer, I want Renovate / Dependabot to keep dependencies up to date | Medium |

---

## Technical Features

| Feature | Description |
|---------|-------------|
| Auto table creation | SQLAlchemy `create_all` on API startup |
| Vite dev proxy | `/api/*` proxied to `http://localhost:8000` — no CORS in dev |
| Svelte 5 runes | `$state`, `$derived`, `$effect`, `$props` for reactive UI |
| Optimistic mutations | Local state mutated before the network round-trip, with rollback on failure |
| API documentation | Auto-generated Swagger UI and ReDoc via FastAPI |
| Health check endpoints | `/health`, `/health/db`, `/metrics` for monitoring |
| Request logging middleware | Logs all HTTP requests with method, URL, status, and duration |
| CORS middleware | Configured to allow cross-origin requests |
| Environment variable support | `PUBLIC_API_BASE` for frontend, `DATABASE_URL` for backend |
| Type-safe API client | Typed fetch client with error handling and 204 support |
| E2E testing | Playwright test suite for API and UI integration testing |
| AI agent extensions | Skills, MCP servers, hooks, and slash commands for enhanced AI capabilities |
| Security hooks | Pre-commit and pre-push secrets detection |
| Multi-stage Docker builds | Optimized container images with proper security settings |

---

*Status is managed directly on GitHub issues.*

---

*Last updated: 2026-06-26*
