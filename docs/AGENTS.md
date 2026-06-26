# AI Agents Guide

Complete guide for AI assistants working on this repository.

## Documentation Index

| File | Purpose | Description |
|------|---------|-------------|
| [`AGENTS.md`](./AGENTS.md) | AI Guide | This file - conventions and rules for AI agents |
| [`PROJECT_STRUCTURE.md`](./PROJECT_STRUCTURE.md) | Architecture | Directory and file organization |
| [`CONVENTIONS.md`](./CONVENTIONS.md) | Code style | Naming conventions, code style, git |
| [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md) | Implementation | API, database, frontend, CI/CD |
| [`DESIGN_SYSTEM.md`](./DESIGN_SYSTEM.md) | UI/UX | Tailwind tokens and component styling |
| [`COMPONENT_REFERENCE.md`](./COMPONENT_REFERENCE.md) | Components | API endpoints and Svelte components |
| [`FEATURES.md`](./FEATURES.md) | Features | Epics, user stories, feature status |
| [`SCREEN_FLOW.md`](./SCREEN_FLOW.md) | Navigation | Web app screen flows |
| [`TASKS.md`](./TASKS.md) | Tasks | Task tracking and backlog |

---

## Tech Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| API Framework | FastAPI | >= 0.115.0 | REST API with automatic OpenAPI docs |
| ASGI Server | Uvicorn | >= 0.34.0 | Production-ready ASGI server |
| Database | SQLite | Built-in | Default development database |
| Database | PostgreSQL | 16 | Production database |
| ORM | SQLAlchemy | >= 2.0.0 | Database abstraction layer |
| Validation | Pydantic | >= 2.0.0 | Data validation and serialization |
| Frontend Framework | SvelteKit 2 | ^2.15 | Full-stack framework with Svelte 5 runes |
| Styling | Tailwind CSS | ^4.0 | Utility-first CSS framework |
| Bundler | Vite | ^6.0 | Fast frontend build tool |
| Language (frontend) | TypeScript | ^5.7 | Type-safe JavaScript superset |
| Language (backend) | Python | >= 3.12 | Backend runtime |
| Package Manager (JS) | Bun | >= 1.1.45 | JavaScript runtime and package manager |
| Package Manager (Python) | uv | >= 0.5 | Python dependency management |
| Git Hooks | Husky | ^9.1 | Git hook management |
| Commit Convention | Gitmoji | ^9.1 | Interactive commit messages |
| Commit Validation | commitlint | ^20.4 | Commit message validation |
| Linting (MD) | markdownlint-cli | ^0.48 | Markdown style enforcement |
| Linting (YAML) | yamllint | Latest | YAML validation |
| Linting (Python) | Ruff | Latest | Fast Python linter |
| Dependency Updates | Renovate | Latest | Automatic dependency updates |
| Dependency Updates | Dependabot | Latest | Security updates |
| CI/CD | GitHub Actions | Latest | Continuous integration |
| Testing (Python) | pytest | >= 8.0.0 | Python test framework |
| Testing (JavaScript) | vitest | ^2.1.8 | JavaScript test framework |
| E2E Testing | Playwright | ^1.48.0 | End-to-end browser testing |

### Available Commands

```bash
# Repo-level lint tooling (root)
bun install           # Install lint dependencies
bun run lint          # Lint markdown and yaml
bun run lint:md       # Lint markdown only
bun run lint:md:fix   # Auto-fix markdown
bun run lint:yaml     # Lint yaml files
bun run lint:commit   # Validate last commit message
bun run commit        # Interactive gitmoji commit
bun run secrets:scan  # Scan for secrets in the codebase

# Docker operations (root)
docker compose up --build       # Build and start all services
docker compose up --build -d    # Build and start in background
docker compose down             # Stop all services
docker compose down -v          # Stop and remove volumes
docker compose logs -f          # Follow all service logs
docker compose exec api bash    # Enter API container
docker compose exec web bash    # Enter web container

# API (from api/)
uv sync                            # Creates .venv and installs dependencies
uv run uvicorn main:app --reload   # Start API at http://localhost:8000
uv run pytest tests/ -v            # Run API tests

# Frontend (from web/)
bun install                       # Install frontend dependencies
bun run dev                        # Start dev server at http://localhost:5173
bun run check                      # Type-check with svelte-check + tsc
bun run build                      # Production build
bun run preview                    # Preview the production build
bun test                           # Run frontend tests (vitest)

# E2E tests (from e2e/)
bun install                       # Install Playwright and browsers
bun run test                      # Run end-to-end tests

# All tests (from root)
bun run test:all                  # Run API, frontend, and E2E tests
```

---

## File Summaries

### PROJECT_STRUCTURE.md

Project structure with two top-level applications. Key points:

- `api/`: FastAPI application (models, schemas, CRUD, database)
- `web/`: SvelteKit + Tailwind v4 frontend (routes, components, fetch client)
- `docs/`: All documentation files

### CONVENTIONS.md

Development conventions. Key points:

- **Python**: PEP 8, type hints, snake_case functions and variables
- **TypeScript / Svelte**: Svelte 5 runes (`$state`, `$derived`, `$props`), camelCase
- **Files**: kebab-case for config, snake_case for Python modules, PascalCase for Svelte components
- **Git branches**: feature/fix/refactor/docs from main
- **Commits**: Gitmoji convention (emoji + description)

### TECHNICAL_GUIDE.md

Technical implementation guide. Key points:

- **API**: FastAPI endpoints, SQLAlchemy models, Pydantic schemas
- **Database**: SQLite by default, Postgres via `DATABASE_URL`
- **Frontend**: SvelteKit routes, typed fetch client, Vite proxy `/api`
- **CI/CD**: GitHub Actions workflows (lint on push/PR)

### DESIGN_SYSTEM.md

UI/UX design with Tailwind v4. Key points:

- **Tokens**: Color palette, spacing, typography
- **Layout**: Single-column, max-width container, sticky header optional
- **Components**: Buttons, inputs, list items styled with utility classes

### COMPONENT_REFERENCE.md

API and UI component documentation. Key points:

- **API endpoints**: Full CRUD reference for `/todos`
- **Pydantic schemas**: Request/Response models
- **SQLAlchemy models**: Database entity definitions
- **Svelte components**: `+page.svelte`, `TodoItem.svelte`, typed `api.ts`

### FEATURES.md

Feature management. Key points:

- Organization by epics (DB, API, Web frontend, tooling)
- User stories for each epic
- Statuses: Done, In Progress, Planned

### SCREEN_FLOW.md

Web app navigation and user flows. Key points:

- Single page with task list, add form, filters, inline edit
- CRUD flows: add, toggle, edit, delete, filter

### TASKS.md

Project tracking. Key points:

- API implementation
- SvelteKit + Tailwind frontend
- Tooling and CI/CD

---

## AI Agent Specific Rules

### Language Rule

**All written content must be in English**, regardless of the user's prompt language:

- Documentation (markdown files, comments)
- Commit messages
- Tasks and subtasks
- Epics and user stories
- Code comments and docstrings
- Variable and function names
- Error messages and logs

### Commit Convention

This project accepts **Gitmoji** or **Conventional Commits**:

```bash
bun run commit  # Interactive gitmoji tool
```

**Gitmoji format:** `<emoji> <description>`

| Emoji | Description |
|-------|-------------|
| ✨ | New feature |
| 🐛 | Bug fix |
| 📝 | Documentation |
| ♻️ | Refactor |
| 🔧 | Configuration |
| 💄 | UI / styling |
| 🔒️ | Security fix |

**Conventional format:** `<type>(scope): <description>`

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`

Full gitmoji list: [gitmoji.dev](https://gitmoji.dev)

### Fundamental Principles

1. **Read before modifying** - Always read a file before proposing changes
2. **Consult documentation** - Check relevant docs/ files before any task
3. **Respect existing patterns** - Follow the style and conventions already in place
4. **Minimize changes** - Only modify what is necessary
5. **Document changes** - Update docs if behavior changes
6. **Run checks** - `bun run check` (frontend) and lint before committing

### Code Generation Preferences

| Language | Preferences |
|----------|-------------|
| **Python** | PEP 8, type hints, Pydantic models |
| **TypeScript** | Strict mode, explicit types at module boundaries |
| **Svelte** | Svelte 5 runes (`$state`, `$derived`, `$effect`, `$props`) — no legacy reactive `$:` |
| **Tailwind** | Utility classes inline, prefer composition over @apply |
| **YAML** | Follow yamllint rules, consistent indentation |
| **Markdown** | Follow markdownlint rules, no trailing spaces |
| **SQL** | Uppercase keywords, snake_case tables/columns |

### Pre-commit Checklist

- [ ] Code passes `bun run lint`
- [ ] Frontend type-checks: `cd web && bun run check`
- [ ] Frontend builds: `cd web && bun run build`
- [ ] API endpoints respond: `curl http://localhost:8000/todos`
- [ ] Documentation updated if necessary
- [ ] Commit uses gitmoji convention
- [ ] No secrets or `.env` files committed

### Behaviors to Avoid

- Do not create unnecessary files
- Do not add dependencies without justification
- Do not modify project structure without discussion
- Do not ignore linting errors
- Do not comment out dead code, delete it
- Do not hardcode secrets or database credentials
- Do not bypass the Vite `/api` proxy with hardcoded `localhost:8000` URLs in components
- Do not mix Svelte 5 runes with legacy `$:` reactive syntax in the same file

### Priorities

1. **Functionality** - Code must work end-to-end (API + frontend)
2. **Type safety** - TypeScript strict, Pydantic schemas at boundaries
3. **Readability** - Code must be understandable
4. **Consistency** - Follow existing patterns
5. **Simplicity** - Avoid over-engineering

---

---

## 📚 Documentation Standards

### Hierarchical AGENTS.md Structure

This project uses a **hierarchical AGENTS.md** approach for providing static context to AI agents:

```text
.
├── AGENTS.md                      # Root - Project-wide static context
│   └── Comprehensive guide with architecture, tech stack, commands, rules
├── api/
│   └── AGENTS.md                  # API-specific context
│       └── FastAPI, SQLAlchemy, database-specific instructions
├── web/
│   └── AGENTS.md                  # Frontend-specific context  
│       └── SvelteKit, Tailwind, TypeScript-specific instructions
└── docs/
    └── AGENTS.md                  # This file - Documentation standards
        └── Documentation conventions, templates, workflow
```

**Priority Order (when instructions conflict):**
1. Root `AGENTS.md` (highest priority)
2. Directory-specific `AGENTS.md` (e.g., `api/AGENTS.md`, `web/AGENTS.md`)
3. `docs/AGENTS.md` (this file - documentation standards)

### Documentation Philosophy

**Purpose of Documentation:**
- **Onboarding** - Help new contributors understand the project quickly
- **Reference** - Provide quick lookup for technical details
- **Maintenance** - Document design decisions and rationale
- **Consistency** - Establish and enforce conventions
- **Knowledge Sharing** - Capture institutional knowledge

**Principles:**
1. **DRY (Don't Repeat Yourself)** - Avoid duplicating information
2. **Single Source of Truth** - Each piece of information lives in one place
3. **Keep It Updated** - Documentation is only useful if accurate
4. **Practical over Perfect** - Useful > Polished but unused
5. **Context over Content** - Explain the "why" not just the "what"

### Markdown Conventions

#### Formatting Rules
- Use ATX-style headings (`#`, `##`, `###`)
- **One** top-level heading per file
- Use consistent heading hierarchy (don't skip levels)
- Use `-` for bullet lists (not `*`)
- Use `1.` for numbered lists
- Use fenced code blocks with language specification
- Always specify language for syntax highlighting

#### Code Blocks
```markdown
```python
# Good - with language
from fastapi import FastAPI
```

```bash
# Good - with language  
$ docker compose up
```
```

#### Tables
- Use GitHub-flavored markdown tables
- Include headers
- Align columns for readability

```markdown
| Column 1 | Column 2 | Description |
|----------|----------|-------------|
| Value 1  | Value 2  | Description |
```

### Documentation Workflow

#### Adding New Documentation
1. Identify the need - What information is missing?
2. Choose the right file - Existing or new file?
3. Follow existing patterns - Match style and structure
4. Add to documentation index - Update `AGENTS.md` references
5. Get review - Have team member review for clarity
6. Update version history - Add "Last updated" date

#### Updating Existing Documentation
1. Read the current version first
2. Identify what's changed
3. Make minimal changes only
4. Verify accuracy - Test examples and commands
5. Update cross-references if needed
6. Update version history

### Documentation Health

**Run these checks regularly:**
- Test all code examples in documentation
- Verify all commands work as documented
- Check for broken links
- Ensure terminology is consistent
- Remove outdated information

**Quality Metrics:**
- Coverage: >80% of codebase documented
- Accuracy: 100% of docs should be correct
- Freshness: Update within 30 days of changes
- Completeness: All required sections present

---

## 🤖 AI Agent Extensions

This project includes Mistral Vibe extensions for enhanced AI agent capabilities:

### Skills (Auto-triggered)

| Skill | Location | Trigger | Purpose |
|-------|----------|---------|---------|
| `todo-management` | `.vibe/skills/todo-management/` | Todo-related tasks | Manage todo items, projects, workflows |
| `docker-helper` | `.vibe/skills/docker-helper/` | Docker commands | Assist with Docker setup, debugging, deployment |
| `code-reviewer` | `.vibe/skills/code-reviewer/` | Code review requests | Analyze code quality, suggest improvements |

### MCP Servers (Model Context Protocol)

| MCP Server | Location | Purpose | Capabilities |
|------------|----------|---------|--------------|
| `file-indexer` | `.vibe/mcp/file-indexer/` | File system indexing | Search, analyze, retrieve file contents |
| `docker-monitor` | `.vibe/mcp/docker-monitor/` | Docker monitoring | Check container status, logs, resource usage |
| `git-analyzer` | `.vibe/mcp/git-analyzer/` | Git analysis | Analyze commits, branches, diffs, blames |

### Hooks (Event-driven)

| Hook | Location | Event | Purpose |
|------|----------|-------|---------|
| `secrets-hook.py` | `.vibe/hooks/pre-commit/` | Pre-commit | Detect and block secrets from being committed |
| `secrets-hook.py` | `.vibe/hooks/pre-push/` | Pre-push | Detect and block secrets from being pushed |

### Slash Commands (Manual)

| Command | Location | Usage | Purpose |
|---------|----------|-------|---------|
| `/todo` | `.vibe/commands/todo-command/` | `/todo add Buy milk` | Manage todo items directly in chat |
| `/docker` | `.vibe/commands/docker-command/` | `/docker status` | Execute Docker operations |

---

*Last updated: 2026-06-26*
*Generated by Mistral Vibe - Enhanced with hierarchical AGENTS.md structure and AI extensions*

---

## 🤖 AI Agent Extensions

This project includes comprehensive Mistral Vibe extensions for enhanced AI agent capabilities:

### Skills (Auto-triggered)

| Skill | Trigger | Purpose | Location |
|-------|---------|---------|----------|
| `todo-management` | Todo-related tasks | Manage todo items, projects, workflows | `.vibe/skills/todo-management/` |
| `docker-helper` | Docker commands and operations | Assist with Docker setup, debugging, deployment | `.vibe/skills/docker-helper/` |
| `code-reviewer` | Code review requests | Analyze code quality, suggest improvements | `.vibe/skills/code-reviewer/` |

### MCP Servers (Model Context Protocol)

| MCP Server | Purpose | Capabilities | Location |
|------------|---------|--------------|----------|
| `file-indexer` | File system indexing | Search, analyze, and retrieve file contents | `.vibe/mcp/file-indexer/` |
| `docker-monitor` | Docker status monitoring | Check container status, logs, resource usage | `.vibe/mcp/docker-monitor/` |
| `git-analyzer` | Git repository analysis | Analyze commits, branches, diffs, blames | `.vibe/mcp/git-analyzer/` |

### Hooks (Event-driven)

| Hook | Event | Purpose | Location |
|------|-------|---------|----------|
| `secrets_hook.py` | Pre-commit | Detect and block secrets from being committed | `.vibe/hooks/pre-commit/` |
| `secrets_hook.py` | Pre-push | Detect and block secrets from being pushed | `.vibe/hooks/pre-push/` |

### Slash Commands (Manual)

| Command | Usage | Purpose | Location |
|---------|-------|---------|----------|
| `/todo <action>` | `/todo add Buy milk` | Manage todo items directly in chat | `.vibe/commands/todo-command/` |
| `/docker <action>` | `/docker status` | Execute Docker operations | `.vibe/commands/docker-command/` |

### Scripts

Additional utility scripts for security and validation:

| Script | Purpose | Location |
|--------|---------|----------|
| `scripts/commit-msg-hook.js` | Commit message validation | `scripts/` |
| `scripts/pre-commit-hook.js` | Pre-commit validation | `scripts/` |
| `scripts/pre-push-hook.js` | Pre-push validation | `scripts/` |
| `scripts/secrets-scan.js` | Secrets scanning utility | `scripts/` |

### Security Configuration

| File | Purpose | Location |
|------|---------|----------|
| `.gitleaks.toml` | Gitleaks secrets detection configuration | Root |
| `.env.example` | Environment variables template | Root |
| `.gitignore` | Files to exclude from Git | Root |
