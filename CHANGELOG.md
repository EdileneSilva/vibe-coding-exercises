# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- ✨ Complete Docker To-Do application with FastAPI backend and SvelteKit frontend
- ✨ Health check endpoints (`/health`, `/health/db`, `/metrics`) for API monitoring
- ✨ Request logging middleware for HTTP request monitoring
- ✨ CORS middleware configuration for cross-origin support
- ✨ Comprehensive test suite: API tests, frontend tests, E2E tests with Playwright
- ✨ Mistral Vibe extensions: skills, MCP servers, hooks, slash commands
- ✨ Security hooks: pre-commit and pre-push secrets detection
- ✨ Gitleaks configuration for secrets scanning
- ✨ Complete project documentation with AGENTS.md files

### Changed
- 📝 Updated all documentation files to reflect actual project implementation
- 📝 Enhanced README.md with complete project structure and development commands
- 📝 Updated docs/PROJECT_STRUCTURE.md with comprehensive file organization
- 📝 Updated docs/TECHNICAL_GUIDE.md with actual implementation details
- 📝 Updated docs/COMPONENT_REFERENCE.md with health check endpoints
- 📝 Updated docs/FEATURES.md with completed features
- 📝 Updated docs/TASKS.md with completed task checklist

---

## [0.1.0] - 2026-06-26

### Added
- ✨ Initial project structure with FastAPI API and SvelteKit frontend
- ✨ Docker Compose orchestration with PostgreSQL, API, and web services
- ✨ SQLAlchemy models and Pydantic schemas for todo management
- ✨ CRUD operations for todo items (create, read, update, delete)
- ✨ SvelteKit UI with task list, add form, filters, and inline editing
- ✨ Tailwind CSS v4 styling with responsive design
- ✨ Vite development server with `/api` proxy to FastAPI
- ✨ Docker multi-stage builds for API and web services
- ✨ nginx reverse proxy configuration
- ✨ GitHub Actions workflows for linting, testing, and deployment
- ✨ Git hooks with Husky for pre-commit validation
- ✨ Commitlint for commit message validation
- ✨ Gitmoji for conventional commit messages
- ✨ Renovate and Dependabot for dependency management
- ✨ Complete documentation set (AGENTS.md, CONVENTIONS.md, etc.)

---

*Changelog generated using [gitmoji](https://gitmoji.dev) conventions.* 
