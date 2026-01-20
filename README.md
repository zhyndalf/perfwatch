# PerfWatch

Real-time system performance monitoring web application.

## Features

- **Real-time Metrics**: CPU, Memory, Disk, Network monitoring with 5-second updates
- **Interactive Charts**: Beautiful visualizations powered by ECharts
- **Process Monitoring**: Track individual process resource usage
- **WebSocket Updates**: Live data streaming to the browser
- **JWT Authentication**: Secure login with token-based auth
- **Dark Theme**: Modern dark UI with TailwindCSS
- **Dockerized**: Easy setup with Docker Compose

## Development Progress

> **55% Complete** (12/22 tasks) | Next: T013 - Perf Events Setup

```mermaid
flowchart TB
    subgraph P1["Phase 1: Foundation (100%) ✅"]
        T001["✅ T001<br/>SDD Scaffold"]
        T002["✅ T002<br/>Docker Setup"]
        T003["✅ T003<br/>Database"]
        T004["✅ T004<br/>Auth Backend"]
        T005["✅ T005<br/>Vue Base"]
        T001 --> T002 --> T003 --> T004 --> T005
    end

    subgraph P2["Phase 2: Core Metrics (100%) ✅"]
        T006["✅ T006<br/>Collector Base"]
        T007["✅ T007<br/>CPU"]
        T008["✅ T008<br/>Memory"]
        T009["✅ T009<br/>Network"]
        T010["✅ T010<br/>Disk"]
        T011["✅ T011<br/>WebSocket"]
        T012["✅ T012<br/>Dashboard"]
        T006 --> T007 --> T008 --> T009 --> T010 --> T011 --> T012
    end

    subgraph P3["Phase 3: Advanced (0%)"]
        T013["⬜ T013<br/>Perf Events"]
        T014["⬜ T014<br/>Cache"]
        T015["⬜ T015<br/>CPU Perf"]
        T016["⬜ T016<br/>Mem BW"]
        T017["⬜ T017<br/>Adv Dashboard"]
        T013 --> T014 --> T015 --> T016 --> T017
    end

    subgraph P4["Phase 4: Polish (0%)"]
        T018["⬜ T018<br/>History"]
        T019["⬜ T019<br/>Compare"]
        T020["⬜ T020<br/>Retention"]
        T021["⬜ T021<br/>Settings"]
        T022["⬜ T022<br/>Polish"]
        T018 --> T019 --> T020 --> T021 --> T022
    end

    P1 --> P2 --> P3 --> P4

    %% Styles
    classDef done fill:#2ecc71,stroke:#27ae60,color:#fff
    classDef progress fill:#f39c12,stroke:#e67e22,color:#fff
    classDef todo fill:#95a5a6,stroke:#7f8c8d,color:#fff

    class T001,T002,T003,T004,T005,T006,T007,T008,T009,T010,T011,T012 done
    class T013,T014,T015,T016,T017,T018,T019,T020,T021,T022 todo
```

| Phase | Status | Tasks |
|-------|--------|-------|
| Phase 1: Foundation | ✅ 100% | 5/5 |
| Phase 2: Core Metrics | ✅ 100% | 7/7 |
| Phase 3: Advanced | 0% | 0/5 |
| Phase 4: Polish | 0% | 0/5 |

> 📋 Detailed progress: [docs/sdd/PROGRESS.md](./docs/sdd/PROGRESS.md)

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Vue.js 3 + Pinia + TailwindCSS + ECharts |
| Backend | FastAPI + WebSocket + SQLAlchemy 2.0 |
| Database | PostgreSQL 15 (JSONB) |
| Auth | JWT (python-jose) + bcrypt |
| Collectors | psutil (CPU, Memory, Network, Disk) |
| Deployment | Docker Compose |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/zhyndalf/perfwatch.git
   cd perfwatch
   ```

2. Copy environment file:
   ```bash
   cp .env.example .env
   ```

3. Start all services:
   ```bash
   docker compose up -d
   ```

4. Run database migrations:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

5. Access the application:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Docs**: http://localhost:8000/docs

### Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

### Verify Setup

```bash
# Check service status
docker compose ps

# Check logs
docker compose logs -f

# Test backend health
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Stop all services
docker compose down
```

## Development

### Project Structure

```
perfwatch/
├── backend/           # FastAPI backend
│   ├── app/           # Application code
│   │   ├── api/       # API endpoints
│   │   ├── collectors/# Metrics collectors (CPU, Memory, Network, Disk)
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   ├── alembic/       # Database migrations
│   └── tests/         # Backend tests (125 tests)
├── frontend/          # Vue.js frontend
│   └── src/
│       ├── api/       # Axios client
│       ├── components/# Vue components
│       ├── router/    # Vue Router
│       ├── stores/    # Pinia stores
│       ├── styles/    # TailwindCSS
│       └── views/     # Page components
├── docs/              # Documentation
│   └── sdd/           # Specification Driven Development docs
├── docker-compose.yml # Service orchestration
└── .env.example       # Environment template
```

### Running Tests

```bash
# Run backend tests (131 tests)
docker compose run --rm backend pytest tests/ -v

# Run with coverage
docker compose run --rm backend pytest tests/ --cov=app
```

### Running Locally (Development)

**Backend:**
```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## Collectors

PerfWatch includes 4 system metrics collectors:

| Collector | Metrics |
|-----------|---------|
| **CPU** | Usage %, per-core %, user/system/idle, frequency, load average, temperature |
| **Memory** | Total, available, used, swap, buffers, cached |
| **Network** | Bytes sent/recv per second, packets, errors, per-interface stats |
| **Disk** | Partition usage, I/O read/write rates, counts |

## API Endpoints

| Endpoint | Method | Description | Auth |
|----------|--------|-------------|------|
| `/api/auth/login` | POST | Get JWT token | No |
| `/api/auth/me` | GET | Current user info | Yes |
| `/api/auth/password` | PUT | Change password | Yes |
| `/health` | GET | Health check | No |

## Documentation

See [docs/sdd/README.md](./docs/sdd/README.md) for detailed project documentation including:
- Architecture decisions
- API specifications
- Development roadmap
- Task tracking

## License

MIT License - see [LICENSE](./LICENSE) for details.
