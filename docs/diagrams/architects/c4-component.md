# C4 Component Diagram

> **Level 3: Component Diagram - Internal components within each container**

This diagram shows the major components inside the Frontend and Backend containers and how they interact.

---

## Backend Components

```mermaid
graph TB
    subgraph Backend["FastAPI Backend Container"]
        Main[main.py<br/>Application Entry<br/>CORS, lifespan events]

        subgraph APIRouters["API Routers"]
            AuthAPI[auth.py<br/>Login, /me,<br/>password change]
            WSAPI[websocket.py<br/>WebSocket manager<br/>/ws/metrics]
            HistoryAPI[history.py<br/>Historical queries<br/>comparison]
            RetentionAPI[retention.py<br/>Policy management<br/>cleanup triggers]
            ConfigAPI[config.py<br/>System info<br/>settings]
        end

        subgraph Services["Services Layer"]
            Aggregator[MetricsAggregator<br/>Coordinates collectors<br/>combines results]
            RetentionSvc[RetentionService<br/>Cleanup logic<br/>policy application]
            BatchWriter[BatchMetricsWriter<br/>Batch DB writes<br/>queue management]
        end

        subgraph Collectors["Collectors"]
            BaseCol[BaseCollector<br/>Abstract base<br/>safe_collect()]
            CPUCol[CPUCollector]
            MemCol[MemoryCollector]
            NetCol[NetworkCollector]
            DiskCol[DiskCollector]
            PerfCol[PerfEventsCollector]
            BandCol[MemoryBandwidthCollector]
        end

        subgraph Models["SQLAlchemy Models"]
            UserModel[User<br/>Authentication]
            MetricsModel[MetricsSnapshot<br/>JSONB storage]
            ConfigModel[Config<br/>Key-value]
            PolicyModel[ArchivePolicy<br/>Retention rules]
        end

        Database[(PostgreSQL<br/>Database)]
        LinuxKernel[🐧 Linux Kernel]
    end

    Main --> APIRouters
    WSAPI --> Aggregator
    HistoryAPI --> Database
    RetentionAPI --> RetentionSvc
    Aggregator --> Collectors
    BaseCol --> CPUCol
    BaseCol --> MemCol
    BaseCol --> NetCol
    BaseCol --> DiskCol
    BaseCol --> PerfCol
    BaseCol --> BandCol
    CPUCol --> LinuxKernel
    MemCol --> LinuxKernel
    NetCol --> LinuxKernel
    DiskCol --> LinuxKernel
    PerfCol --> LinuxKernel
    BandCol --> LinuxKernel
    BatchWriter --> Database
    Aggregator --> BatchWriter
    RetentionSvc --> Database
    AuthAPI --> UserModel
    WSAPI --> MetricsModel
    HistoryAPI --> MetricsModel
    RetentionAPI --> PolicyModel
    ConfigAPI --> ConfigModel

    classDef entryStyle fill:#FF6F00,stroke:#E65100,color:#fff
    classDef apiStyle fill:#42A5F5,stroke:#1565C0,color:#fff
    classDef serviceStyle fill:#66BB6A,stroke:#2E7D32,color:#fff
    classDef collectorStyle fill:#AB47BC,stroke:#6A1B9A,color:#fff
    classDef modelStyle fill:#FFA726,stroke:#E65100,color:#fff
    classDef dbStyle fill:#78909C,stroke:#37474F,color:#fff

    class Main entryStyle
    class AuthAPI,WSAPI,HistoryAPI,RetentionAPI,ConfigAPI apiStyle
    class Aggregator,RetentionSvc,BatchWriter serviceStyle
    class BaseCol,CPUCol,MemCol,NetCol,DiskCol,PerfCol,BandCol collectorStyle
    class UserModel,MetricsModel,ConfigModel,PolicyModel modelStyle
    class Database,LinuxKernel dbStyle
```

---

## Frontend Components

```mermaid
graph TB
    subgraph Frontend["Vue.js Frontend Container"]
        Router[Vue Router<br/>Navigation<br/>Auth guards]

        subgraph Views["Views (Pages)"]
            LoginView[Login.vue<br/>Authentication UI]
            DashView[Dashboard.vue<br/>Real-time metrics<br/>ECharts]
            HistView[History.vue<br/>Time-range queries<br/>Comparison]
            SettingsView[Settings.vue<br/>System info<br/>Retention config]
        end

        subgraph Stores["Pinia Stores"]
            AuthStore[authStore<br/>JWT management<br/>User state]
            MetricsStore[metricsStore<br/>WebSocket client<br/>Real-time data]
            HistoryStore[historyStore<br/>Query state<br/>Comparison data]
            RetentionStore[retentionStore<br/>Policy state]
            ConfigStore[configStore<br/>System info]
        end

        subgraph Components["Shared Components"]
            Layout[Layout.vue<br/>App wrapper]
            Header[Header.vue<br/>Navigation bar]
        end

        APIClient[API Client<br/>Axios instance<br/>JWT interceptor]
        WSClient[WebSocket Client<br/>Connection manager<br/>Auto-reconnect]
    end

    Backend[FastAPI Backend]

    Router --> Views
    Views --> Stores
    LoginView --> AuthStore
    DashView --> MetricsStore
    HistView --> HistoryStore
    SettingsView --> RetentionStore
    SettingsView --> ConfigStore
    Layout --> Header
    Views --> Layout
    AuthStore --> APIClient
    HistoryStore --> APIClient
    RetentionStore --> APIClient
    ConfigStore --> APIClient
    MetricsStore --> WSClient
    APIClient --> Backend
    WSClient --> Backend

    classDef routerStyle fill:#FF6F00,stroke:#E65100,color:#fff
    classDef viewStyle fill:#42A5F5,stroke:#1565C0,color:#fff
    classDef storeStyle fill:#66BB6A,stroke:#2E7D32,color:#fff
    classDef componentStyle fill:#AB47BC,stroke:#6A1B9A,color:#fff
    classDef clientStyle fill:#FFA726,stroke:#E65100,color:#fff
    classDef backendStyle fill:#78909C,stroke:#37474F,color:#fff

    class Router routerStyle
    class LoginView,DashView,HistView,SettingsView viewStyle
    class AuthStore,MetricsStore,HistoryStore,RetentionStore,ConfigStore storeStyle
    class Layout,Header componentStyle
    class APIClient,WSClient clientStyle
    class Backend backendStyle
```

---

## Component Responsibilities

### Backend Components

#### main.py (Application Entry)
**Type:** Application bootstrap
**Responsibilities:**
- Initialize FastAPI application
- Configure CORS for frontend access
- Register API routers
- Define lifespan events (startup/shutdown)
- Start background tasks (metrics collection, retention cleanup)

**Key Code:**
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database, start background tasks
    yield
    # Shutdown: cleanup resources
```

---

#### API Routers

**auth.py:**
- `POST /api/auth/login` - Validate credentials, issue JWT
- `GET /api/auth/me` - Return current user info
- `POST /api/auth/password` - Change password (bcrypt)

**websocket.py:**
- `GET /api/ws/metrics` - WebSocket endpoint (JWT in query param)
- Manage active connections (connect, disconnect, broadcast)
- Background collection loop (every 5s)

**history.py:**
- `GET /api/history/metrics` - Query time range with downsampling
- `GET /api/history/compare` - Compare two time periods
- Aggregation logic for large datasets

**retention.py:**
- `GET /api/retention` - Get current policy
- `PUT /api/retention` - Update retention days
- `POST /api/retention/cleanup` - Trigger manual cleanup

**config.py:**
- `GET /api/config` - System information (hostname, CPU count, memory)
- Application settings

---

#### Services Layer

**MetricsAggregator:**
- Coordinates all 6 collectors
- Calls `safe_collect()` on each collector
- Combines results into single snapshot
- Handles collector failures gracefully

**RetentionService:**
- Applies retention policy (delete old snapshots)
- Runs in background task (every 1 hour)
- Logs cleanup statistics

**BatchMetricsWriter:**
- Queues metrics snapshots for batch insertion
- Reduces database write overhead
- Flushes queue every 5 seconds or when full

---

#### Collectors

**BaseCollector (Abstract):**
- Defines `collect()` interface
- Implements `safe_collect()` with error handling
- Provides `enabled` flag

**Concrete Collectors:**
- **CPUCollector:** psutil.cpu_percent(), cpu_freq(), sensors_temperatures()
- **MemoryCollector:** psutil.virtual_memory(), swap_memory()
- **NetworkCollector:** psutil.net_io_counters(), per_interface stats
- **DiskCollector:** psutil.disk_usage(), disk_io_counters()
- **PerfEventsCollector:** perf_event_open() for hardware counters
- **MemoryBandwidthCollector:** /proc/vmstat parsing

---

#### SQLAlchemy Models

**User:**
- Authentication table
- Bcrypt password hashing
- Last login tracking

**MetricsSnapshot:**
- Time-series data storage
- JSONB column for flexible schema
- Indexed by timestamp

**Config:**
- Key-value configuration store
- Updated_at timestamp

**ArchivePolicy:**
- Retention days setting
- Downsample interval (future use)

---

### Frontend Components

#### Vue Router
**Responsibilities:**
- Define routes: `/login`, `/`, `/history`, `/settings`
- Authentication guards: redirect to login if no JWT
- Navigation management

**Key Routes:**
```javascript
{
  path: '/',
  component: Dashboard,
  meta: { requiresAuth: true }
}
```

---

#### Views (Pages)

**Login.vue:**
- Username/password form
- Call authStore.login()
- Redirect to dashboard on success

**Dashboard.vue:**
- Display real-time metrics from metricsStore
- 6 ECharts (CPU, memory, network, disk, perf, bandwidth)
- Auto-updates every 5 seconds via WebSocket

**History.vue:**
- Date/time range picker
- Query button → historyStore.fetchMetrics()
- Comparison mode with two time periods
- ECharts line charts for historical trends

**Settings.vue:**
- Display system info from configStore
- Retention policy editor
- Save button → retentionStore.updatePolicy()

---

#### Pinia Stores

**authStore:**
- State: `user`, `token`, `isAuthenticated`
- Actions: `login()`, `logout()`, `fetchMe()`
- Persists JWT in localStorage

**metricsStore:**
- State: `currentMetrics`, `connectionState`
- Actions: `connect()`, `disconnect()`
- WebSocket message handler updates `currentMetrics`

**historyStore:**
- State: `metrics`, `comparisonMetrics`, `loading`
- Actions: `fetchMetrics()`, `fetchComparison()`
- Transforms API response for ECharts

**retentionStore:**
- State: `policy`, `loading`
- Actions: `fetchPolicy()`, `updatePolicy()`

**configStore:**
- State: `systemInfo`
- Actions: `fetchConfig()`

---

#### Shared Components

**Layout.vue:**
- App wrapper with sidebar navigation
- Logout button
- Slot for view content

**Header.vue:**
- Top navigation bar
- Current user display
- Navigation links

---

#### API Clients

**APIClient (Axios):**
- Base URL: `http://localhost:8000`
- JWT interceptor: adds `Authorization: Bearer <token>` header
- Error handling: logout on 401

**WSClient (WebSocket):**
- Connection URL: `ws://localhost:8000/api/ws/metrics?token=JWT`
- Auto-reconnect on disconnect
- Message parsing and store updates

---

## Component Interactions

### Real-time Metrics Flow
```
Background Task (5s) → MetricsAggregator → Collectors → Linux Kernel
                                        → BatchWriter → Database
                                        → WebSocket Broadcast
                                                     → WSClient (Frontend)
                                                     → metricsStore
                                                     → Dashboard.vue (ECharts)
```

### Authentication Flow
```
Login.vue → authStore.login() → APIClient → POST /api/auth/login → UserModel
                                                                  → JWT issued
         ← authStore (save token) ← Response
         → Router (redirect to /)
```

### Historical Query Flow
```
History.vue → historyStore.fetchMetrics() → APIClient → GET /api/history/metrics
                                                       → MetricsModel (database query)
                                          ← Response (JSON)
            ← historyStore (update state)
            → ECharts (render chart)
```

---

## Design Patterns

**Backend:**
- **Repository Pattern:** Models abstract database access
- **Service Layer:** Business logic separate from API routes
- **Dependency Injection:** FastAPI `Depends()` for database sessions
- **Background Tasks:** asyncio tasks for collection and cleanup
- **Strategy Pattern:** BaseCollector interface with multiple implementations

**Frontend:**
- **Composition API:** Vue 3 `<script setup>` pattern
- **Store Pattern:** Pinia for centralized state management
- **Observer Pattern:** WebSocket updates trigger reactive UI updates
- **Guard Pattern:** Router navigation guards for authentication
- **Interceptor Pattern:** Axios request/response interceptors for JWT

---

**Navigation:**
- [← Previous: Container Diagram](./c4-container.md)
- [Next: Technology Stack →](./tech-stack.md)
- [↑ Diagrams Index](../README.md)
