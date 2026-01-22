# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

# PerfWatch - Real-time System Performance Monitor

> **PerfWatch** is a real-time system performance monitoring web application that collects CPU, memory, network, disk, and hardware counter metrics via WebSocket streaming.
>
> **Status**: 100% Complete (22/22 tasks) • 238 backend tests passing

---

## Quick Start (Resume Checklist)

**When resuming work on PerfWatch:**

1. **Read** [`docs/sdd/CURRENT_TASK.md`](docs/sdd/CURRENT_TASK.md) - Current task and completion status
2. **Read** the referenced task file in `docs/sdd/04-tasks/` if continuing work
3. **Start services**: `docker compose up -d`
4. **Run migrations** (if needed): `docker compose exec backend alembic upgrade head`
5. **Verify setup**: Visit http://localhost:3000 (login: admin/admin123)

---

## CRITICAL RULES

### Before Git Commit and Push

**ALWAYS update `README.md` before committing:**
- Update progress percentage if tasks completed
- Update Mermaid diagram with task status changes
- Update test counts if tests added
- Keep README synchronized with actual project state

This ensures GitHub always shows accurate project status.

### bcrypt Password Hashing

**MUST use bcrypt directly, NOT passlib:**
```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

### SQLAlchemy 2.0 Style

**Use modern SQLAlchemy 2.0 patterns:**
- `Mapped` type hints, not legacy `Column`
- `mapped_column()`, not `Column()`
- Async sessions with `async_sessionmaker`
- Explicit typing: `Mapped[int]`, `Mapped[Optional[str]]`

---

## Essential Commands

### Docker Development (Primary)

```bash
# Start all services (backend, frontend, database)
docker compose up -d

# View live logs
docker compose logs -f backend
docker compose logs -f frontend

# Rebuild after code changes
docker compose build backend && docker compose up -d

# Stop all services
docker compose down

# Full reset (including database)
docker compose down -v
```

### Database

```bash
# Run migrations
docker compose exec backend alembic upgrade head

# Create new migration
docker compose exec backend alembic revision --autogenerate -m "description"

# Rollback one migration
docker compose exec backend alembic downgrade -1

# Access PostgreSQL directly
docker compose exec db psql -U perfwatch

# Check database status
curl http://localhost:8000/api/db-status
```

### Testing

```bash
# Run all backend tests (238 tests)
docker compose run --rm backend pytest tests/ -v

# Run specific test file
docker compose run --rm backend pytest tests/test_auth.py -v

# Run specific test function
docker compose run --rm backend pytest tests/test_auth.py::test_login -v

# Run with coverage report
docker compose run --rm backend pytest tests/ --cov=app --cov-report=html

# Run tests matching pattern
docker compose run --rm backend pytest tests/ -k "collector" -v

# Run tests in parallel (faster)
docker compose run --rm backend pytest tests/ -n auto
```

### Local Development (Without Docker)

**Backend:**
```bash
cd backend
pip install -e ".[dev]"
export DATABASE_URL="postgresql+asyncpg://perfwatch:perfwatch@localhost:5432/perfwatch"
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev        # Development server
npm run build      # Production build
npm run preview    # Preview production build
```

### Debugging

```bash
# Check service health
curl http://localhost:8000/health

# Test authentication
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Watch WebSocket metrics (requires wscat)
wscat -c "ws://localhost:8000/api/ws/metrics?token=YOUR_JWT_TOKEN"

# Check background collection status
docker compose logs backend | grep "Background collection"

# Monitor retention cleanup
docker compose logs backend | grep "Retention cleanup"
```

---

## Tech Stack

| Aspect | Choice |
|--------|--------|
| Frontend | Vue.js 3 + Pinia + TailwindCSS + ECharts |
| Backend | FastAPI + WebSocket |
| Database | PostgreSQL 15 (JSONB for metrics) |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | JWT (python-jose) + bcrypt |
| Collectors | psutil + perf_events (perf stat, Linux) |
| Deployment | Docker Compose |
| Testing | pytest + pytest-asyncio + httpx |

---

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │◄────│   Backend   │◄────│  Collectors │
│  Vue.js 3   │ WS  │   FastAPI   │     │   psutil    │
│  ECharts    │     │ WebSocket   │     │ perf_events │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │    JSONB    │
                    └─────────────┘
```

**Data Flow**:
1. Linux Kernel → psutil/perf stat
2. Collectors → Aggregator (every 5s)
3. Aggregator → Database (metrics_snapshot table)
4. Aggregator → WebSocket → Frontend (live updates)
5. Frontend → ECharts (visualization)

**Key Components:**
- **Collectors**: Inherit from `BaseCollector`, implement `collect()` method, return dict
- **Aggregator**: Coordinates all collectors, combines results, broadcasts via WebSocket
- **WebSocket**: `/api/ws/metrics` endpoint with JWT auth in query param
- **Background Tasks**: Metrics collection loop + retention cleanup loop
- **Graceful Degradation**: Missing metrics show "N/A", never crash

→ Full architecture: [`docs/sdd/02-specification/architecture.md`](docs/sdd/02-specification/architecture.md)

---

## Design Principles

| Principle | Implementation |
|-----------|----------------|
| **Simplicity First** | Fixed dashboard layout, single 5s interval, no customization |
| **Real-time First** | WebSocket streaming primary, historical queries secondary |
| **Graceful Degradation** | Collectors return None for unavailable metrics, UI shows "N/A" |
| **Docker First** | All development in containers, no bare-metal setup |
| **Convention over Config** | Defaults: 30-day retention, admin user, 5s sampling |
| **TDD Approach** | Write tests alongside implementation, 238 tests total |

**Explicitly Won't Support**:
- Windows or macOS (Linux-only via perf)
- Remote monitoring (localhost only)
- Multiple users (single admin)
- Custom metrics or plugins
- Drag-and-drop dashboards

→ Full principles: [`docs/sdd/01-constitution/principles.md`](docs/sdd/01-constitution/principles.md)

---

## Project Structure

```
perfwatch/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app, lifespan events, CORS
│   │   ├── config.py            # Settings (pydantic-settings)
│   │   ├── database.py          # Async SQLAlchemy setup
│   │   ├── init_db.py           # Create default admin user
│   │   ├── api/
│   │   │   ├── auth.py          # JWT login, /me, password change
│   │   │   ├── websocket.py     # /ws/metrics + background collection
│   │   │   ├── history.py       # Historical data queries
│   │   │   ├── retention.py     # Retention policy API
│   │   │   ├── config.py        # App configuration API
│   │   │   └── deps.py          # Shared dependencies (get_current_user)
│   │   ├── collectors/
│   │   │   ├── base.py          # BaseCollector abstract class
│   │   │   ├── aggregator.py    # MetricsAggregator coordinator
│   │   │   ├── cpu.py           # CPU usage, frequency, temp
│   │   │   ├── memory.py        # Memory, swap usage
│   │   │   ├── network.py       # Network I/O, interfaces
│   │   │   ├── disk.py          # Disk usage, I/O
│   │   │   ├── perf_events.py   # Hardware counters (perf stat)
│   │   │   └── memory_bandwidth.py  # Page I/O, swap activity
│   │   ├── models/
│   │   │   ├── user.py          # User model (auth)
│   │   │   ├── metrics.py       # MetricsSnapshot (JSONB)
│   │   │   ├── config.py        # Config key-value store
│   │   │   └── archive_policy.py # Retention settings
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   └── services/
│   │       └── retention.py     # Retention cleanup logic
│   ├── alembic/                 # Database migrations
│   │   └── versions/            # Migration files (timestamped)
│   └── tests/                   # 238 tests, pytest + httpx
├── frontend/
│   └── src/
│       ├── api/client.js        # Axios with JWT interceptor
│       ├── router/index.js      # Vue Router + auth guards
│       ├── stores/auth.js       # Pinia auth store
│       ├── views/
│       │   ├── Login.vue        # Auth page
│       │   ├── Dashboard.vue    # Real-time metrics (ECharts)
│       │   ├── History.vue      # Historical queries + comparison
│       │   └── Settings.vue     # System info + retention config
│       └── components/
│           ├── Layout.vue       # App wrapper with nav
│           └── Header.vue       # Top navigation bar
├── docs/sdd/                    # Specification Driven Development docs
│   ├── CURRENT_TASK.md          # Resume point, current status
│   ├── PROGRESS.md              # Overall progress (100%)
│   ├── 01-constitution/         # Vision, principles, glossary
│   ├── 02-specification/        # Architecture, API, data model
│   ├── 03-plan/                 # Roadmap, phase breakdown
│   ├── 04-tasks/                # Task implementation files (T001-T022)
│   └── 05-implementation/       # Decisions, changelog, learnings
├── docker-compose.yml           # Service orchestration
└── .env.example                 # Environment template
```

---

## Collectors System

All collectors inherit from `BaseCollector` and follow this pattern:

```python
from app.collectors.base import BaseCollector
from typing import Dict, Any

class MyCollector(BaseCollector):
    name = "my_collector"  # Unique identifier

    async def collect(self) -> Dict[str, Any]:
        # Collect metrics, may raise exceptions
        return {"metric": value}
```

**BaseCollector provides:**
- `safe_collect()`: Wraps `collect()` with error handling
- `enabled` flag: Disable collectors without removing them
- Automatic timestamping: `_timestamp` field
- Graceful errors: `_error` field on failure

**Available Collectors:**

| Collector | Metrics | Availability |
|-----------|---------|--------------|
| **CPUCollector** | usage_percent, per_core, user/system/idle, frequency, load_avg, temperature | Always |
| **MemoryCollector** | total, available, used, swap, buffers, cached | Always |
| **NetworkCollector** | bytes_sent/recv per sec, packets, errors, per-interface | Always |
| **DiskCollector** | partition usage, read/write bytes per sec, I/O counts | Always |
| **PerfEventsCollector** | perf stat counters (cpu-clock, context-switches, cpu-migrations, page-faults, cycles, instructions, branches, branch-misses, L1-dcache-loads, L1-dcache-load-misses, LLC-loads, LLC-load-misses, L1-icache-loads, dTLB-loads, dTLB-load-misses, iTLB-loads, iTLB-load-misses) | Linux perf + PMU only |
| **MemoryBandwidthCollector** | page in/out per sec, swap in/out per sec, page faults | /proc/vmstat only |

**Usage in aggregator:**
```python
from app.collectors import MetricsAggregator, CPUCollector, MemoryCollector

aggregator = MetricsAggregator(collectors=[
    CPUCollector(),
    MemoryCollector(),
    # ...
])

snapshot = await aggregator.collect_all()
# Returns: {"cpu": {...}, "memory": {...}, "timestamp": "..."}
```

---

## Database Models (SQLAlchemy 2.0)

The application uses SQLAlchemy 2.0 with modern `Mapped` type hints and async sessions. Main models:
- **User**: Authentication (username, password_hash, last_login)
- **MetricsSnapshot**: Time-series metrics stored as JSONB (timestamp, metric_type, metric_data)
- **Config**: Key-value configuration store
- **ArchivePolicy**: Retention policy settings (retention_days, downsample_interval)

→ Full data model with schemas: [`docs/sdd/02-specification/data-model.md`](docs/sdd/02-specification/data-model.md)

---

## API Endpoints Quick Reference

The API provides endpoints for authentication, real-time WebSocket streaming, historical queries, and configuration. Key endpoints:
- **Auth**: `/api/auth/login`, `/api/auth/me`, `/api/auth/password`
- **WebSocket**: `/api/ws/metrics` (real-time streaming with JWT token in query param)
- **History**: `/api/history/metrics`, `/api/history/metrics/types`, `/api/history/compare` (time-range queries and comparisons with relative or custom ranges)
- **Retention**: `/api/retention/*` (policy management and cleanup)
- **Config**: `/api/config` (system info and settings)

→ Full API spec with request/response schemas: [`docs/sdd/02-specification/api-spec.md`](docs/sdd/02-specification/api-spec.md)

---

## Testing Architecture

**Test Database:**
- Tests use `perfwatch_test` database, not `perfwatch`
- Created automatically by `conftest.py` fixtures
- Tables created/dropped per test session
- All tests are async with `pytest-asyncio`

**Key Fixtures (conftest.py):**
```python
@pytest_asyncio.fixture
async def db_session(async_engine) -> AsyncSession:
    # Provides isolated database session per test

@pytest_asyncio.fixture
async def client(db_session):
    # Provides httpx AsyncClient with database override
```

**Running Tests:**
```bash
# All tests
docker compose run --rm backend pytest tests/ -v

# Specific test file
docker compose run --rm backend pytest tests/test_auth.py -v

# Pattern matching
docker compose run --rm backend pytest tests/ -k "collector" -v

# With coverage
docker compose run --rm backend pytest tests/ --cov=app
```

**Test Categories:**
- `test_api.py` - Basic API health checks
- `test_auth.py` - JWT authentication flow
- `test_database.py` - Database connection
- `test_init_db.py` - Default data creation
- `test_models.py` - SQLAlchemy models
- `test_*_collector.py` - Individual collectors (CPU, memory, network, disk)
- `test_perf_events.py` - Hardware counter collection
- `test_memory_bandwidth.py` - Memory bandwidth metrics
- `test_history.py` - Historical queries and comparison
- `test_config.py` - Configuration API

---

## Key Technical Decisions

1. **SQLAlchemy 2.0 Style**: `Mapped` type hints, `mapped_column()`, async sessions
2. **bcrypt directly**: NOT passlib (compatibility issues in Docker)
3. **Async everything**: `asyncpg`, `async_sessionmaker`, async fixtures
4. **PostgreSQL for tests**: JSONB column type requires PostgreSQL (not SQLite)
5. **JSONB for metrics**: Flexible schema, efficient indexing, native PostgreSQL
6. **WebSocket for real-time**: HTTP polling too inefficient for 5s updates
7. **Background tasks**: Metrics collection + retention cleanup in asyncio tasks
8. **JWT in query param for WS**: No header support in browser WebSocket API
9. **Graceful degradation**: perf stat may fail (permissions, kernel/PMU), show "N/A"
10. **Docker privileged mode**: Required for perf access on Linux

---

## Code Patterns

### Async Database Session
```python
from app.database import AsyncSessionLocal
from sqlalchemy import select

async with AsyncSessionLocal() as session:
    result = await session.execute(select(User).where(User.username == "admin"))
    user = result.scalar_one_or_none()
    await session.commit()
```

### Dependency Injection (FastAPI)
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.api.deps import get_current_user

@app.get("/api/data")
async def get_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # db is an async session
    # current_user is validated JWT user
    pass
```

### Creating Migrations
```bash
# After modifying models in app/models/
docker compose exec backend alembic revision --autogenerate -m "add new field"

# Review the generated migration in backend/alembic/versions/
# Then apply it:
docker compose exec backend alembic upgrade head
```

---

## Environment Variables

Key settings in `.env` (see `.env.example`):

```bash
# Database
POSTGRES_USER=perfwatch
POSTGRES_PASSWORD=perfwatch
POSTGRES_DB=perfwatch

# JWT
JWT_SECRET=change-this-in-production

# Admin User
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Metrics Collection
SAMPLING_INTERVAL_SECONDS=5
BACKGROUND_COLLECTION_ENABLED=true
RETENTION_CLEANUP_ENABLED=true
RETENTION_CLEANUP_INTERVAL_MINUTES=60
```

---

## Known Issues / Gotchas

1. **Migrations must run before backend**: Backend crashes if tables don't exist
   - Solution: `docker compose exec backend alembic upgrade head`

2. **perf requires privileged mode**: `docker-compose.yml` has `privileged: true`
   - Without it, hardware counters unavailable (gracefully degrades)

3. **CPU percent needs priming**: First `psutil.cpu_percent()` call returns 0
   - Collectors handle this by calling with interval parameter

4. **Tests use separate database**: `perfwatch_test`, auto-created by fixtures
   - Don't manually create it

5. **pydantic v2 deprecation warnings**: Using class-based `Config`
   - Future: Migrate to `ConfigDict` pattern

6. **WebSocket auth via query param**: Browser WebSocket can't set headers
   - Token passed as `?token=JWT` in URL

7. **Background collection in tests**: Disabled via env var
   - `conftest.py` sets `BACKGROUND_COLLECTION_ENABLED=false`

8. **JSONB requires PostgreSQL**: Can't use SQLite for tests
   - Tests run against `perfwatch_test` PostgreSQL database

---

## URLs & Default Credentials

| Resource | URL/Value |
|----------|-----------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |
| Admin Username | admin |
| Admin Password | admin123 |
| Database Host | localhost:5432 |
| Database Name | perfwatch |
| Database User | perfwatch |
| Database Password | perfwatch |

---

## SDD Documentation Map

The project uses **Specification Driven Development (SDD)**:

```
docs/sdd/
├── CURRENT_TASK.md        ← Start here when resuming
├── PROGRESS.md            ← Overall progress (100% complete)
├── 01-constitution/       ← WHY: Vision, principles, glossary
│   ├── vision.md
│   ├── principles.md
│   └── glossary.md
├── 02-specification/      ← WHAT: Architecture, API, data model
│   ├── architecture.md
│   ├── api-spec.md
│   ├── data-model.md
│   └── component-specs.md
├── 03-plan/               ← WHEN: Roadmap, phase breakdown
│   ├── roadmap.md
│   ├── phase1-foundation.md
│   ├── phase2-core.md
│   ├── phase3-advanced.md
│   └── phase4-polish.md
├── 04-tasks/              ← DO: Task implementation files
│   ├── T001-sdd-scaffold.md
│   ├── T002-docker-setup.md
│   ├── ...
│   └── T022-polish.md
└── 05-implementation/     ← DONE: Decisions, changelog, learnings
    ├── decisions.md
    ├── changelog.md
    └── learnings.md
```

**Workflow:**
1. Read `CURRENT_TASK.md` to see current status
2. Read linked task file in `04-tasks/` for detailed requirements
3. Implement according to specs in `02-specification/`
4. Update `CURRENT_TASK.md` and `PROGRESS.md` when done
5. Document decisions in `05-implementation/decisions.md`

---

## GitHub Repository

https://github.com/zhyndalf/perfwatch
