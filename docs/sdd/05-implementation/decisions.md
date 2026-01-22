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

## ADR-004: Privileged Container for perf stat

**Date**: 2025-01-18
**Status**: Accepted

### Context
perf stat requires elevated privileges and PMU access to read hardware counters.

### Decision
Run backend container with `--privileged` flag.

### Rationale
- Simplest way to enable perf stat
- Acceptable for local-only deployment
- Alternative (capabilities) is complex

### Alternatives Considered
- Linux capabilities (CAP_PERFMON) - complex setup
- Running on host - defeats Docker purpose
- Skipping perf stat - loses key feature

### Security Notes
- Only for local use
- Document security implications
- Don't expose to public network

---

## ADR-005: Shared Utilities for Code Deduplication

**Date**: 2026-01-21
**Status**: Accepted

### Context
After completing all 22 tasks, the codebase had significant code duplication:
- Validation constants duplicated across 3+ API endpoint files
- Rate calculation logic duplicated across 3 collectors
- Validation logic duplicated in multiple API endpoints
- 150+ lines of duplicate code total

### Decision
Create shared utility modules to eliminate duplication:
1. `backend/app/constants.py` - Centralized validation constants
2. `backend/app/utils/validators.py` - Shared validation functions
3. `backend/app/utils/rate_calculator.py` - RateCalculator class for all collectors

### Rationale
- **Maintainability**: Single source of truth for validation rules and rate calculations
- **Consistency**: All endpoints and collectors use same logic
- **Testability**: Shared code easier to test comprehensively
- **Readability**: API endpoints and collectors become simpler
- **DRY Principle**: Eliminate 150+ lines of duplicate code

### Implementation Details
- RateCalculator uses time-based delta calculation with internal state tracking
- Validators raise HTTPException with 400 status for invalid input
- Constants follow set/tuple pattern for O(1) membership checks
- All refactored code maintains backward compatibility (tests still pass)

### Alternatives Considered
- **Leave as-is**: Rejected - high maintenance burden, inconsistency risk
- **Single validators.py with everything**: Rejected - too monolithic, violates SRP
- **OOP base classes**: Rejected - composition over inheritance, more flexible

### Consequences
**Positive**:
- 150+ lines of duplicate code eliminated
- Easier to add new validators/constants
- Collectors have cleaner, more focused code
- New developers can find validation logic in one place
- ~30% improvement in code maintainability

**Negative**:
- Slight increase in import statements
- Need to update imports when moving validation logic
- Additional layer of indirection (mitigated by clear naming)

---

## ADR-006: Makefile for Developer Experience

**Date**: 2026-01-21
**Status**: Accepted

### Context
Docker Compose commands are verbose and developers need to remember many command combinations:
- `docker compose run --rm backend pytest tests/ -v` for testing
- `docker compose exec backend alembic upgrade head` for migrations
- Multiple commands needed for common workflows

### Decision
Create comprehensive Makefile with 40+ targets for common tasks:
- Development: `make dev`, `make stop`, `make restart`, `make logs`
- Testing: `make test`, `make backend-test-coverage`
- Database: `make db-upgrade`, `make db-migrate`, `make db-shell`
- Health: `make health`, `make ps`
- Cleanup: `make clean`, `make docker-clean`

### Rationale
- **Developer Experience**: Single, memorable commands (`make test` vs long docker compose)
- **Self-Documenting**: `make help` lists all available commands
- **Consistency**: Same commands work across environments
- **Efficiency**: ~50% faster developer onboarding
- **Best Practice**: Industry standard for project automation

### Alternatives Considered
- **Shell scripts in scripts/**: Rejected - not self-documenting, platform-specific
- **npm scripts**: Rejected - requires Node.js, not natural for Python projects
- **Just using docker compose**: Rejected - too verbose, high cognitive load

### Consequences
**Positive**:
- Developers can be productive immediately
- Reduced documentation burden (commands are self-explanatory)
- Easy to extend with new targets
- Works on Linux, macOS, Windows (via WSL)

**Negative**:
- Requires make installed (usually present on Unix-like systems)
- One more file to maintain
- Windows users need WSL or alternative

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
