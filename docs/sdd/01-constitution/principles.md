# PerfWatch Design Principles

> The core principles and constraints guiding all design decisions

---

## Core Principles

### 1. Simplicity Over Flexibility

**Principle**: Make the common case trivially easy, even at the cost of advanced customization.

**Rationale**:
- Target users want quick insights, not configuration marathons
- A fixed, well-designed dashboard beats infinite customization
- Fewer options = fewer bugs = faster development

**Examples**:
- Fixed dashboard layout (not drag-and-drop)
- Predetermined chart types per metric
- Single sampling interval (5 seconds)

---

### 2. Real-time First

**Principle**: The live dashboard is the primary experience; history is secondary.

**Rationale**:
- Users typically want to see what's happening NOW
- Historical analysis is occasional, not constant
- Optimizing for real-time ensures responsive UX

**Examples**:
- WebSocket for live updates
- Dashboard is the landing page after login
- History is a separate, opt-in view

---

### 3. Graceful Degradation

**Principle**: If a metric isn't available, show what we can; never crash.

**Rationale**:
- Not all systems support all metrics (especially perf stat)
- A partially working dashboard is better than an error page
- Hardware variations are expected

**Examples**:
- perf stat fails? Show "N/A" for those metrics
- Temperature unavailable? Hide that section
- Network interface disappears? Remove from display

---

### 4. Docker-First Development

**Principle**: Everything runs in Docker; bare-metal is not supported.

**Rationale**:
- Consistent environment across all developers
- Easy setup with `docker-compose up`
- Privileged container enables perf stat access
- PostgreSQL managed automatically

**Examples**:
- All documentation assumes Docker
- No "install Python locally" instructions
- Database runs in container

---

### 5. Convention Over Configuration

**Principle**: Sensible defaults that work without modification.

**Rationale**:
- Faster time-to-working
- Fewer questions for users
- Less documentation needed

**Examples**:
- Default admin user created automatically
- 30-day retention by default
- 5-second sampling interval preset

---

## Technical Constraints

### Must Have

| Constraint | Reason |
|------------|--------|
| Python 3.11+ | Required for modern async features |
| Vue.js 3 | Composition API for cleaner code |
| PostgreSQL | JSONB for flexible metric storage |
| WebSocket | Real-time updates requirement |
| Docker | Consistent deployment environment |

### Won't Support

| Excluded | Reason |
|----------|--------|
| Windows | perf stat is Linux-only |
| Remote monitoring | Scope creep, security complexity |
| Multiple users | Overkill for local tool |
| Custom metrics | Fixed metric set is sufficient |
| Plugin system | Complexity not justified |

---

## Architectural Constraints

### Backend

```
┌─────────────────────────────────────────────┐
│              FastAPI Application            │
├─────────────────────────────────────────────┤
│  Async/Await everywhere (no blocking calls) │
│  SQLAlchemy 2.0 async (not sync ORM)        │
│  WebSocket for streaming                     │
│  JWT for authentication                      │
└─────────────────────────────────────────────┘
```

### Frontend

```
┌─────────────────────────────────────────────┐
│              Vue.js 3 Application           │
├─────────────────────────────────────────────┤
│  Composition API (not Options API)          │
│  Pinia for state (not Vuex)                 │
│  ECharts for all charts                     │
│  TailwindCSS for styling                    │
└─────────────────────────────────────────────┘
```

### Data Flow

```
Linux Kernel → psutil/perf stat → Collectors → Aggregator → WebSocket → Frontend
                                          ↓
                                    PostgreSQL (history)
```

---

## Security Constraints

### Authentication
- Basic username/password (JWT tokens)
- Single admin user (no user management UI)
- Session timeout: 24 hours

### Container Security
- Runs as root inside container (required for perf stat)
- `--privileged` flag required for hardware counters
- Network: localhost only by default
- No external API access

### Data Security
- Passwords hashed with bcrypt
- JWT secrets in environment variables
- No sensitive data in metrics (system-level only)

---

## Performance Constraints

| Metric | Target | Rationale |
|--------|--------|-----------|
| Collection overhead | < 1% CPU | Don't impact monitored system |
| WebSocket latency | < 50ms | Real-time feel |
| Database writes | Batched, async | Don't block collectors |
| Frontend memory | < 100MB | Charts can be memory-hungry |
| Chart data points | Max 300 per chart | Browser performance |

---

## Code Quality Constraints

### Backend
- Type hints everywhere
- Docstrings for public functions
- Tests for critical paths (auth, data collection)
- Async by default

### Frontend
- TypeScript-style comments (JSDoc)
- Component props validated
- Composables for reusable logic
- Consistent naming conventions

### Both
- No hardcoded values (use config)
- Log important operations
- Handle errors gracefully
- Comment the "why", not the "what"
