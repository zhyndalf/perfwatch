# Resume Context for Claude

> **Last Updated**: 2026-01-21
> **Last Task Completed**: Phase 5 Cleanup + perf stat refactor
> **Next Task**: None (project complete)

---

## Quick Resume Commands

```bash
# Start services
docker compose up -d

# Run tests (238 tests should pass)
docker compose run --rm backend pytest tests/ -v

# Check current status
cat docs/sdd/CURRENT_TASK.md
```

---

## Current Project State

### Progress: 100% Complete (22/22 tasks)

| Phase | Status |
|-------|--------|
| Phase 1: Foundation | ✅ 100% |
| Phase 2: Core Metrics | ✅ 100% |
| Phase 3: Advanced Metrics | ✅ 100% |
| Phase 4: Polish | ✅ 100% |
| Phase 5: Cleanup | ✅ 100% |

### Highlights
- perf_events refactored to use `perf stat -I` streaming
- Perf events are raw counters only (no IPC or derived rates)
- Configurable perf CPU cores + interval via settings
- Frontend shows perf counters grid and perf event selector in history

---

## Key Technical Context

### PerfEventsCollector (`backend/app/collectors/perf_events.py`)

The collector uses perf stat streaming and parses CSV output:
- Collects: cpu-clock, context-switches, cpu-migrations, page-faults
- Collects: cycles, instructions, branches, branch-misses
- Collects: L1/LLC cache and dTLB/iTLB counters
- Marks `available: false` if any event is missing/unsupported

**Current return format:**
```python
{
    "available": True,
    "cpu_cores": "all",
    "interval_ms": 1000,
    "sample_time": "1.000123",
    "events": {
        "cycles": {"value": 5000000000, "unit": None},
        "instructions": {"value": 9000000000, "unit": None},
        "cpu-clock": {"value": 1000.12, "unit": "msec"}
    }
}
```

### Important Notes
1. **VMs need PMU passthrough** - perf stat requires exposed counters
2. **Permissions matter** - `perf_event_paranoid` and CAP_PERFMON/privileged
3. **Missing events** - Any missing/unsupported event marks perf_events unavailable

---

## Files Touched in Refactor

- `backend/app/collectors/perf_events.py` - perf stat subprocess + parser
- `backend/app/config.py` - perf_events CPU cores + interval settings
- `backend/app/services/config.py` - config schema updates
- `frontend/src/views/Dashboard.vue` - perf counters grid
- `frontend/src/views/History.vue` - perf event selector + chart
- `frontend/src/views/Settings.vue` - perf events config inputs
- `backend/tests/test_perf_events.py` - perf stat parsing tests

---

## Test Summary

- **238 total tests**
- All passing as of last run

---

## To Continue Development

1. Read `docs/sdd/CURRENT_TASK.md` for context
2. Run `docker compose up -d`
3. Run tests if changing collectors or schemas
