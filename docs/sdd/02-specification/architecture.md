# PerfWatch Architecture

> System architecture and component design

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue.js 3)                       │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │  Dashboard  │ │  History    │ │  Settings   │ │   Login    │ │
│  │   (ECharts) │ │  Compare    │ │   Page      │ │   Page     │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
└───────────────────────────┬─────────────────────────────────────┘
                            │ WebSocket + REST API
┌───────────────────────────┴─────────────────────────────────────┐
│                      Backend (FastAPI)                           │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌────────────┐ │
│  │  WebSocket  │ │  REST API   │ │    Auth     │ │   Config   │ │
│  │  Handler    │ │  Endpoints  │ │  Middleware │ │   Manager  │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └────────────┘ │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                    Metrics Aggregator                       ││
│  │  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────────────┐   ││
│  │  │ CPU │ │ Mem │ │ Net │ │Disk │ │Cache│ │ Perf Events │   ││
│  │  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────────────┘   ││
│  └─────────────────────────────────────────────────────────────┘│
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────────┐
│                      PostgreSQL Database                         │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐               │
│  │   Metrics   │ │    Users    │ │   Config    │               │
│  │   Tables    │ │    Table    │ │   Table     │               │
│  └─────────────┘ └─────────────┘ └─────────────┘               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Details

### Frontend Components

#### Vue.js 3 Application
- **Framework**: Vue.js 3 with Composition API
- **Build Tool**: Vite
- **Routing**: Vue Router
- **State Management**: Pinia
- **Charts**: ECharts
- **Styling**: TailwindCSS
- **HTTP Client**: Axios

#### Pages
| Page | Purpose | Route |
|------|---------|-------|
| Login | Authentication | `/login` |
| Dashboard | Real-time metrics display | `/` |
| History | Historical data & comparison | `/history` |
| Settings | Configuration & user settings | `/settings` |

#### Key Composables
- `useWebSocket.js` - WebSocket connection management
- `useAuth.js` - Authentication state and methods

---

### Backend Components

#### FastAPI Application Structure
```
app/
├── main.py              # Application entry point
├── config.py            # Configuration management
├── database.py          # Database connection
├── models/              # SQLAlchemy models
├── schemas/             # Pydantic schemas
├── api/                 # API endpoints
│   ├── auth.py          # Authentication endpoints
│   ├── metrics.py       # Metrics endpoints
│   ├── history.py       # Historical data endpoints
│   └── websocket.py     # WebSocket handler
├── collectors/          # Metric collectors
│   ├── base.py          # Base collector class
│   ├── cpu.py           # CPU metrics
│   ├── memory.py        # Memory metrics
│   ├── network.py       # Network metrics
│   ├── disk.py          # Disk metrics
│   ├── perf_events.py   # perf stat hardware counters
│   └── aggregator.py    # Collector coordinator
├── services/            # Business logic
│   ├── auth.py          # Auth service
│   ├── metrics.py       # Metrics service
│   └── archive.py       # Data retention service
└── utils/               # Utilities
```

#### Collector Architecture
```python
# Base collector interface
class BaseCollector:
    async def collect() -> dict
    def get_metric_type() -> str
    def is_available() -> bool

# Aggregator coordinates collectors
class Aggregator:
    collectors: List[BaseCollector]

    async def collect_all() -> MetricSnapshot
    async def start_collection_loop()
    def register_websocket_client()
```

---

### Data Flow

#### Real-time Metrics Flow
```
1. Aggregator schedules collection (every 5 seconds)
2. Each collector gathers its metrics
3. Aggregator combines into MetricSnapshot
4. Snapshot sent to:
   a. All connected WebSocket clients
   b. Database (async, batched)
5. Frontend receives WebSocket message
6. Charts update with new data
```

#### Historical Query Flow
```
1. Frontend requests history via REST API
2. Backend queries PostgreSQL
3. Data aggregated/downsampled if needed
4. JSON response returned
5. Frontend renders historical charts
```

---

## Deployment Architecture

### Docker Compose Services
```yaml
services:
  backend:      # FastAPI application
  frontend:     # Vue.js (served by nginx)
  db:           # PostgreSQL
```

### Container Configuration
| Service | Port | Privileged | Notes |
|---------|------|------------|-------|
| backend | 8000 | Yes | Required for perf stat |
| frontend | 3000 | No | Static file serving |
| db | 5432 | No | Internal only |

### Network
```
┌─────────────────────────────────────┐
│         Docker Network              │
│  ┌─────────┐ ┌─────────┐ ┌──────┐  │
│  │ frontend│ │ backend │ │  db  │  │
│  │  :3000  │ │  :8000  │ │:5432 │  │
│  └────┬────┘ └────┬────┘ └──┬───┘  │
│       │           │         │       │
└───────┼───────────┼─────────┼───────┘
        │           │         │
   localhost:3000  localhost:8000
        ↑
      Browser
```

---

## Security Architecture

### Authentication Flow
```
1. User submits credentials
2. Backend validates against database
3. JWT token generated (24hr expiry)
4. Token returned to frontend
5. Frontend stores token (localStorage)
6. Token sent with all API requests
7. Backend validates token on each request
```

### Protected Resources
| Resource | Authentication Required |
|----------|------------------------|
| `/api/auth/login` | No |
| `/api/auth/*` | Yes |
| `/api/metrics/*` | Yes |
| `/api/history/*` | Yes |
| `/api/config/*` | Yes |
| `/api/ws/metrics` | Yes (token in query param) |

---

## Scalability Notes

### Current Design (Single Machine)
- Single backend instance
- In-memory WebSocket client tracking
- Direct database writes

### Future Considerations (Not Implemented)
- Redis for WebSocket pub/sub
- Multiple backend instances
- TimescaleDB for time-series optimization
- Remote metric collection agents
