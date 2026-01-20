# Repository Guidelines

## Project Status
- Current task: T020 - Data Retention (see `docs/sdd/CURRENT_TASK.md`)
- Progress tracking: `docs/sdd/PROGRESS.md`

## Project Structure & Module Organization
- `backend/` contains the FastAPI service. Core modules live in `backend/app/` with `api/`, `collectors/`, `models/`, `schemas/`, and `services/`.
- `backend/tests/` holds pytest tests; `backend/alembic/` contains database migrations.
- `frontend/` is the Vue 3 client; source is under `frontend/src/` with `api/`, `components/`, `router/`, `stores/`, `styles/`, and `views/`.
- `docs/sdd/` stores specification-driven documentation and task tracking.
- `docker-compose.yml` orchestrates the app and database for local/dev usage.

## Build, Test, and Development Commands
- Start stack: `docker compose up -d`
- Run migrations: `docker compose exec backend alembic upgrade head`
- Backend tests: `docker compose run --rm backend pytest tests/ -v`
- Backend dev server: `cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload`
- Frontend dev server: `cd frontend && npm install && npm run dev`
- Frontend build: `cd frontend && npm run build`

## Coding Style & Naming Conventions
- Python uses 4-space indentation; Vue/JS/CSS use 2-space indentation.
- Follow existing module naming (snake_case for Python files, PascalCase for Vue components).
- Keep API schemas in `backend/app/schemas/` and SQLAlchemy models in `backend/app/models/`.
- No dedicated formatter is configured; match existing code patterns and keep changes minimal.

## Testing Guidelines
- Backend tests are pytest-based with `pytest-asyncio`; files use `test_*.py` naming in `backend/tests/`.
- Prefer adding tests alongside new collectors, API endpoints, or storage logic.
- No frontend test harness is configured yet; verify UI changes manually via `npm run dev`.

## Commit & Pull Request Guidelines
- Commit style in history uses `type(T###): message` for task work (e.g., `feat(T017): ...`) and `docs: ...` for documentation-only updates.
- Before committing, update `README.md` to keep progress, tasks, and counts accurate.
- PRs should describe the change, link the relevant task doc in `docs/sdd/04-tasks/`, and include screenshots for UI changes.

## Configuration Tips
- Copy `.env.example` to `.env` for local settings if needed.
- Default services expect PostgreSQL via Docker Compose and a running backend before frontend auth works.
