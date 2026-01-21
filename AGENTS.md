# Repository Guidelines

## Project Status
- **Status**: ✅ 100% Complete + Refactored (All 22 tasks done + code cleanup)
- **Latest**: Phase 5 Cleanup completed (2026-01-21) - see `docs/sdd/CURRENT_TASK.md`
- **Progress tracking**: `docs/sdd/PROGRESS.md`
- **Tests**: 238 backend tests passing

## Project Structure & Module Organization
- `backend/` contains the FastAPI service. Core modules live in `backend/app/` with `api/`, `collectors/`, `models/`, `schemas/`, `services/`, and `utils/`.
- `backend/app/utils/` contains shared utilities: `constants.py`, `validators.py`, `rate_calculator.py`
- `backend/tests/` holds pytest tests; `backend/alembic/` contains database migrations.
- `frontend/` is the Vue 3 client; source is under `frontend/src/` with `api/`, `components/`, `router/`, `stores/`, `styles/`, and `views/`.
- `docs/sdd/` stores specification-driven documentation and task tracking.
- `docker-compose.yml` orchestrates the app and database for local/dev usage.
- **New**: `Makefile`, `CONTRIBUTING.md`, `DEVELOPMENT.md`, `.editorconfig` for improved developer experience

## Build, Test, and Development Commands

### Using Makefile (Recommended)
- Start stack: `make docker-up` or `make dev`
- Run tests: `make test` or `make backend-test`
- Check health: `make health`
- Database migrations: `make db-upgrade`
- View logs: `make logs`
- Stop services: `make stop` or `make docker-down`

### Direct Commands
- Start stack: `docker compose up -d`
- Run migrations: `docker compose exec backend alembic upgrade head`
- Backend tests: `docker compose run --rm backend pytest tests/ -v`
- Backend dev server: `cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload`
- Frontend dev server: `cd frontend && npm install && npm run dev`
- Frontend build: `cd frontend && npm run build`

## Coding Style & Naming Conventions
- Python uses 4-space indentation; Vue/JS/CSS use 2-space indentation.
- **Linting configured**: black (line-length=100), isort (profile=black), mypy for Python
- Use `.editorconfig` for consistent formatting across editors
- Follow existing module naming (snake_case for Python files, PascalCase for Vue components).
- Keep API schemas in `backend/app/schemas/` and SQLAlchemy models in `backend/app/models/`.
- Shared utilities in `backend/app/utils/` (constants, validators, rate_calculator)
- Match existing code patterns and keep changes minimal.

## Testing Guidelines
- Backend tests are pytest-based with `pytest-asyncio`; files use `test_*.py` naming in `backend/tests/`.
- **All 238 tests must pass** before committing changes
- Prefer adding tests alongside new collectors, API endpoints, or storage logic.
- Run tests: `make test` or `docker compose run --rm backend pytest tests/ -v`
- Coverage: `make backend-test-coverage`
- No frontend test harness is configured yet; verify UI changes manually via `npm run dev`.

## Commit & Pull Request Guidelines
- See `CONTRIBUTING.md` for full guidelines
- Commit style: `type: message` (e.g., `feat: add new feature`, `refactor: improve code structure`)
- Add co-authorship for AI assistance: `Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>`
- Before committing, update `README.md` to keep progress, tasks, and counts accurate.
- PRs should describe the change, link relevant docs, and include screenshots for UI changes.

## Configuration Tips
- Copy `.env.example` to `.env` for local settings if needed.
- Default services expect PostgreSQL via Docker Compose and a running backend before frontend auth works.
- Check `DEVELOPMENT.md` for comprehensive setup guide and troubleshooting
