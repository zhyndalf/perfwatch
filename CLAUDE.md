# CLAUDE.md - PerfWatch Project Context

> **PerfWatch** is a real-time system performance monitoring web application that collects CPU, memory, network, disk, and hardware counter metrics via WebSocket streaming.

---

## Quick Start (Resume Checklist)

**When resuming work on PerfWatch:**

1. **Read** [`docs/sdd/CURRENT_TASK.md`](docs/sdd/CURRENT_TASK.md) - Shows current task and what's done
2. **Read** the linked task file in `docs/sdd/04-tasks/`
3. **Start services**: `docker compose up -d`
4. **Run migrations** (if needed): `docker compose exec backend alembic upgrade head`
5. **Continue** from "What's Next" section

**Current Task**: T017 - Advanced Dashboard ([PROGRESS.md](docs/sdd/PROGRESS.md))

---

## IMPORTANT RULES

### Before Git Commit and Push

**ALWAYS update `README.md` before committing and pushing changes:**
- Update the progress percentage and current task
- Update the Mermaid diagram with completed tasks
- Update test counts and any new features
- Keep the README in sync with actual project state

This ensures the GitHub repository always shows accurate project status.

---

## Tech Stack

| Aspect | Choice |
|--------|--------|
| Frontend | Vue.js 3 + Pinia + TailwindCSS + ECharts |
| Backend | FastAPI + WebSocket |
| Database | PostgreSQL 15 (JSONB) |
| ORM | SQLAlchemy 2.0 (async) |
| Auth | JWT (python-jose) + bcrypt |
| Collectors | psutil (CPU, Memory, Network, Disk) |
| Deployment | Docker Compose |

---

## Architecture Overview

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │◄────│   Backend   │◄────│  Collectors │
│  Vue.js 3   │ WS  │   FastAPI   │     │   psutil    │
│  ECharts    │     │             │     │ perf_events │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                    ┌──────▼──────┐
                    │  PostgreSQL │
                    │    JSONB    │
                    └─────────────┘
```

**Data Flow**: Linux Kernel → psutil/perf_events → Collectors → Aggregator → WebSocket (5s) → Frontend

→ Full architecture: [`docs/sdd/02-specification/architecture.md`](docs/sdd/02-specification/architecture.md)

---

## Design Principles

| Principle | Meaning |
|-----------|---------|
| **Simplicity First** | Fixed dashboard, no drag-and-drop, single 5s interval |
| **Real-time First** | WebSocket streaming; history is secondary |
| **Graceful Degradation** | Show "N/A" if perf_events unavailable; never crash |
| **Docker First** | All development in containers; no bare-metal |
| **Convention over Config** | Sensible defaults (30-day retention, admin user) |

**Won't Support**: Windows, remote monitoring, multiple users, custom metrics, plugins

→ Full principles: [`docs/sdd/01-constitution/principles.md`](docs/sdd/01-constitution/principles.md)

---

## API Quick Reference

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/auth/login` | POST | Get JWT token | No |
| `/api/auth/me` | GET | Current user info | Yes |
| `/api/auth/password` | PUT | Change password | Yes |
| `/api/ws/metrics` | WS | Real-time metrics stream | Yes (token in query) |
| `/api/history/metrics` | GET | Query historical data | Yes |
| `/api/config` | GET/PUT | App configuration | Yes |

→ Full API spec: [`docs/sdd/02-specification/api-spec.md`](docs/sdd/02-specification/api-spec.md)

---

## Collectors

The metrics collection system uses psutil with graceful degradation:

| Collector | File | Key Metrics |
|-----------|------|-------------|
| CPU | `collectors/cpu.py` | usage_percent, per_core, load_avg, frequency |
| Memory | `collectors/memory.py` | total, available, used, swap |
| Network | `collectors/network.py` | bytes_per_sec, interfaces, connections |
| Disk | `collectors/disk.py` | partitions, io read/write rates |

**Usage:**
```python
from app.collectors import CPUCollector, MemoryCollector, NetworkCollector, DiskCollector, MetricsAggregator

aggregator = MetricsAggregator(collectors=[
    CPUCollector(),
    MemoryCollector(),
    NetworkCollector(),
    DiskCollector(),
])

snapshot = await aggregator.collect_all()
```

---

## Data Model Quick Reference

| Table | Purpose | Key Fields |
|-------|---------|------------|
| `users` | Authentication | username, password_hash, last_login |
| `metrics_snapshot` | Time-series data | timestamp, metric_type, metric_data (JSONB) |
| `config` | App settings | key, value (JSONB) |
| `archive_policy` | Retention settings | retention_days, downsample_interval |

**Metric JSONB Example** (CPU):
```json
{
  "usage_percent": 45.2,
  "per_core": [40.1, 50.3, 42.8, 47.6],
  "user": 30.5,
  "system": 14.7,
  "frequency_mhz": [3200, 3150, 3180, 3210]
}
```

→ Full data model: [`docs/sdd/02-specification/data-model.md`](docs/sdd/02-specification/data-model.md)

---

## Essential Commands

```bash
# Start all services
docker compose up -d

# View logs
docker compose logs -f backend

# Run migrations
docker compose exec backend alembic upgrade head

# Run tests (125 tests)
docker compose run --rm backend pytest tests/ -v

# Access database
docker compose exec db psql -U perfwatch

# Rebuild after code changes
docker compose build backend && docker compose up -d
```

---

## Project Structure

```
perfwatch/
├── backend/app/           # FastAPI application
│   ├── main.py            # Entry point
│   ├── config.py          # Settings (pydantic-settings)
│   ├── database.py        # Async SQLAlchemy
│   ├── collectors/        # Metrics collectors (CPU, Memory, Network, Disk)
│   ├── models/            # User, MetricsSnapshot, Config, ArchivePolicy
│   └── schemas/           # Pydantic schemas including metrics
├── backend/tests/         # Test suite (125 tests)
├── backend/alembic/       # Database migrations
├── frontend/src/          # Vue.js application
│   ├── api/               # Axios client with JWT
│   ├── router/            # Vue Router with auth guards
│   ├── stores/            # Pinia stores (auth)
│   ├── views/             # Login, Dashboard, History, Settings
│   └── components/        # Layout, Header
├── docs/sdd/              # Specification Driven Development docs
└── docker-compose.yml
```

---

## Key Technical Decisions

1. **SQLAlchemy 2.0 style** - `Mapped` type hints, `mapped_column()` (not legacy Column)
2. **bcrypt directly** - NOT passlib (compatibility issues)
3. **Async everything** - `asyncpg`, `async_sessionmaker`, async fixtures
4. **PostgreSQL for tests** - Tests use `perfwatch_test` database (JSONB requires PG)
5. **TDD approach** - Write tests alongside implementation
6. **Graceful degradation** - Collectors return None for unavailable metrics

---

## Code Patterns

### Password Hashing (bcrypt directly - NOT passlib)
```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())
```

### Async Database Session
```python
from app.database import AsyncSessionLocal

async with AsyncSessionLocal() as session:
    result = await session.execute(select(User))
    users = result.scalars().all()
```

### Collector Pattern
```python
from app.collectors.base import BaseCollector

class MyCollector(BaseCollector):
    name = "my_collector"

    async def collect(self) -> Dict[str, Any]:
        # Collect metrics
        return {"metric": value}
```

---

## URLs & Credentials

| Resource | URL/Value |
|----------|-----------|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Admin Login | admin / admin123 |
| Database | perfwatch / perfwatch |

---

## Known Issues / Gotchas

1. **Run migrations before backend starts** - Backend fails if tables don't exist
2. **Tests use separate database** - `perfwatch_test`, not `perfwatch`
3. **Docker build may fail on network issues** - Just retry
4. **pydantic v2 deprecation warning** - Using class-based Config, should migrate to ConfigDict
5. **CPU percent needs priming** - First call returns 0, subsequent calls accurate

---

## SDD Documentation Map

```
docs/sdd/
├── CURRENT_TASK.md        ← Start here when resuming
├── PROGRESS.md            ← Overall progress dashboard (45% complete)
├── 01-constitution/       ← WHY: vision, principles, glossary
├── 02-specification/      ← WHAT: architecture, API, data model
├── 03-plan/               ← WHEN: roadmap, phase plans
├── 04-tasks/              ← DO: task implementation files (T001-T022)
└── 05-implementation/     ← DONE: decisions, changelog, learnings
```

---

## GitHub

https://github.com/zhyndalf/perfwatch
