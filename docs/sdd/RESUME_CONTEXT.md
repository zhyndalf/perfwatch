# Resume Context for Claude

> **Last Updated**: 2026-01-20
> **Last Task Completed**: T014 - Cache Metrics
> **Next Task**: T015 - CPU Perf Metrics

---

## Quick Resume Commands

```bash
# Start services
docker compose up -d

# Run tests (166 tests should pass)
docker compose run --rm backend pytest tests/ -v

# Check current status
cat docs/sdd/CURRENT_TASK.md
```

---

## Current Project State

### Progress: 64% Complete (14/22 tasks)

| Phase | Status |
|-------|--------|
| Phase 1: Foundation | ✅ 100% (5/5) |
| Phase 2: Core Metrics | ✅ 100% (7/7) |
| Phase 3: Advanced | 40% (2/5) - T013, T014 done |
| Phase 4: Polish | 0% (0/5) |

### Completed Tasks (Phase 3)
- **T013**: Perf Events Setup - Linux perf_events with ctypes syscall
- **T014**: Cache Metrics - L1D and LLC cache miss rates

### Remaining Tasks (Phase 3)
- **T015**: CPU Perf Metrics - Branch predictions, TLB metrics
- **T016**: Memory Bandwidth - DDR read/write rates
- **T017**: Advanced Dashboard - Add perf metrics to UI

---

## Key Technical Context

### PerfEventsCollector (`backend/app/collectors/perf_events.py`)

The collector uses ctypes to directly call `perf_event_open` syscall:
- Collects: cycles, instructions, IPC, L1D cache, LLC cache
- Gracefully returns `{"available": False}` when perf_events unavailable
- Works on x86_64, aarch64, arm architectures

**Current metrics collected:**
```python
{
    "available": True,
    "cycles": int,
    "instructions": int,
    "ipc": float,  # instructions / cycles
    "l1d_references": int,
    "l1d_misses": int,
    "l1d_miss_rate": float,  # misses / references
    "llc_references": int,
    "llc_misses": int,
    "llc_miss_rate": float,
}
```

### Important Notes
1. **perf_events won't work in VM** - The host has `perf_event_paranoid=4` and PMU not exposed
2. **Graceful degradation is correct behavior** - Returns `{"available": False}`
3. **WebSocket test fix** - Uses separate `test_app` to avoid event loop conflicts

---

## Files Modified in Recent Sessions

| File | Purpose |
|------|---------|
| `backend/app/collectors/perf_events.py` | Perf events + cache metrics collector |
| `backend/app/schemas/metrics.py` | PerfEventsMetrics schema |
| `backend/app/api/websocket.py` | Includes perf_events in stream |
| `backend/tests/test_perf_events.py` | 35 tests for perf_events |
| `backend/tests/test_websocket.py` | Fixed event loop isolation |

---

## T015 Implementation Plan (Next Task)

### What to Add
Branch prediction and TLB metrics using existing perf_events infrastructure:

```python
# Hardware events to add
PERF_COUNT_HW_BRANCH_INSTRUCTIONS = 4
PERF_COUNT_HW_BRANCH_MISSES = 5

# Cache events for TLB
PERF_COUNT_HW_CACHE_DTLB = 3  # Already defined
PERF_COUNT_HW_CACHE_ITLB = 4  # Already defined
```

### Metrics to collect
- `branch_instructions`: Total branches
- `branch_misses`: Mispredicted branches
- `branch_miss_rate`: misses / instructions
- `dtlb_misses`: Data TLB misses (optional)
- `itlb_misses`: Instruction TLB misses (optional)

### Files to modify
1. `backend/app/collectors/perf_events.py` - Add branch/TLB events
2. `backend/app/schemas/metrics.py` - Add new fields
3. `backend/tests/test_perf_events.py` - Add tests
4. `docs/sdd/04-tasks/phase-3/T015-cpu-perf-metrics.md` - Create task file

---

## Test Summary

- **166 total tests**
- All passing as of last commit
- perf_events tests: 35 (26 original + 9 cache)

---

## Git Status

- **Branch**: dev
- **Last commit**: `e0621d3` - feat(T014): Add cache metrics
- **Remote**: Up to date with origin/dev

---

## To Continue Development

1. Read `docs/sdd/CURRENT_TASK.md` for context
2. Start with T015 - CPU Perf Metrics
3. Follow the pattern established in T013/T014
4. Run tests frequently: `docker compose run --rm backend pytest tests/test_perf_events.py -v`
