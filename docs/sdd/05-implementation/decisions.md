# Architecture Decision Records

> Documenting significant technical decisions made during implementation

---

## How to Use This File

When making a significant architectural decision:
1. Add a new entry with date and title
2. Document the context, decision, and rationale
3. Note any alternatives considered
4. Update if the decision changes later

---

## ADR-001: SDD File-Based Documentation

**Date**: 2025-01-18
**Status**: Accepted

### Context
Need a way to maintain project context across multiple conversation sessions with AI assistants.

### Decision
Use Specification Driven Development (SDD) with markdown files as the source of truth.

### Rationale
- Files persist across conversations
- Human-readable and version-controllable
- Can be resumed from any point
- No external tools required

### Alternatives Considered
- Traditional project management tools (too heavy)
- In-conversation context only (doesn't persist)
- Database-driven specs (over-engineered)

---

## ADR-002: Async-First Backend

**Date**: 2025-01-18
**Status**: Accepted

### Context
Backend needs to handle concurrent metrics collection, WebSocket connections, and database operations.

### Decision
Use FastAPI with async/await throughout. SQLAlchemy 2.0 async mode. asyncpg for PostgreSQL.

### Rationale
- Non-blocking I/O for better concurrency
- Better WebSocket handling
- Modern Python best practices
- FastAPI naturally async

### Alternatives Considered
- Sync SQLAlchemy (simpler but blocks)
- Different database drivers (asyncpg is fastest)
- Separate process for collection (over-complex)

---

## ADR-003: JSONB for Metrics Storage

**Date**: 2025-01-18
**Status**: Accepted

### Context
Need to store varied metric data with different structures per metric type.

### Decision
Use PostgreSQL JSONB column for flexible metric data storage.

### Rationale
- Flexible schema for different metric types
- Good query performance with indexes
- No schema migrations for new metrics
- Native PostgreSQL feature

### Alternatives Considered
- Normalized tables (too rigid)
- Time-series DB like TimescaleDB (overkill)
- Separate columns per metric (maintenance burden)

---

## ADR-004: Privileged Container for perf_events

**Date**: 2025-01-18
**Status**: Accepted

### Context
perf_events requires elevated privileges to access hardware counters.

### Decision
Run backend container with `--privileged` flag.

### Rationale
- Simplest way to enable perf_events
- Acceptable for local-only deployment
- Alternative (capabilities) is complex

### Alternatives Considered
- Linux capabilities (CAP_PERFMON) - complex setup
- Running on host - defeats Docker purpose
- Skipping perf_events - loses key feature

### Security Notes
- Only for local use
- Document security implications
- Don't expose to public network

---

## Template for New ADRs

```markdown
## ADR-XXX: [Title]

**Date**: YYYY-MM-DD
**Status**: Proposed | Accepted | Deprecated | Superseded

### Context
What is the issue that we're seeing that is motivating this decision?

### Decision
What is the change that we're proposing and/or doing?

### Rationale
Why is this change being made?

### Alternatives Considered
What other approaches were considered and why weren't they chosen?

### Consequences
What becomes easier or harder as a result of this decision?
```
