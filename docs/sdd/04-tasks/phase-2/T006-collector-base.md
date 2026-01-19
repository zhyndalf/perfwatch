# T006: Collector Base

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 2 - Core Metrics |
| **Estimated Time** | 2-3 hours |
| **Dependencies** | T003 (Database Setup), T005 (Vue Frontend Base) |
| **Status** | ✅ COMPLETED |
| **Completed** | 2026-01-19 |

---

## Objective

Create the base collector infrastructure using psutil for system metrics collection, with an aggregator that coordinates multiple collectors and prepares data for WebSocket streaming.

---

## Context

The collector system forms the heart of PerfWatch's metrics gathering:
- Each collector (CPU, Memory, Network, Disk) inherits from a base class
- The aggregator coordinates collection on a 5-second interval
- Data is structured for both real-time streaming and historical storage

This task creates the foundation; specific collectors come in T007-T010.

---

## Acceptance Criteria

### Base Collector Class
- [x] Abstract base class with `collect()` method
- [x] Collector name and enabled configuration
- [x] Error handling with graceful degradation via `safe_collect()`
- [x] Timestamp attachment to collected data

### Aggregator
- [x] Coordinates multiple collectors
- [x] Runs on configurable interval (default 5s)
- [x] Combines metrics into unified snapshot
- [x] Async-friendly design with concurrent collection
- [x] Support for both sync and async callbacks

### Data Structures
- [x] Pydantic models for CPU, Memory, Network, Disk metrics
- [x] JSONB-compatible output format
- [x] Type hints throughout

### Testing
- [x] 22 unit tests for collector infrastructure
- [x] Mock collectors for testing
- [x] Tests for error handling and concurrency

---

## Implementation Notes

### Key Decisions

1. **Concurrent collection** - Uses `asyncio.gather()` to collect from all collectors simultaneously
2. **Graceful degradation** - `safe_collect()` catches exceptions and returns error info instead of crashing
3. **Disabled collectors** - Can disable collectors without removing them, returns `_enabled: False`
4. **Flexible callbacks** - `start()` method supports both sync and async callbacks

### Architecture

```
BaseCollector (abstract)
    ├── collect() - abstract method, implemented by subclasses
    └── safe_collect() - wraps collect() with error handling

MetricsAggregator
    ├── add_collector() / remove_collector()
    ├── collect_all() - concurrent collection from all collectors
    └── start() / stop() - periodic collection with callback
```

---

## Files Created

| File | Description |
|------|-------------|
| `backend/app/collectors/__init__.py` | Package exports |
| `backend/app/collectors/base.py` | BaseCollector abstract class |
| `backend/app/collectors/aggregator.py` | MetricsAggregator coordinator |
| `backend/app/schemas/metrics.py` | Pydantic schemas for all metric types |
| `backend/tests/test_collectors.py` | 22 unit tests |

---

## Verification Results

```bash
# Run collector tests
docker compose run --rm backend pytest tests/test_collectors.py -v
# ✅ 22 passed

# Run all tests
docker compose run --rm backend pytest tests/ -v
# ✅ 73 passed (51 existing + 22 new)

# Quick import test
docker compose exec backend python -c "
from app.collectors import BaseCollector, MetricsAggregator
print('Imports successful!')
"
# ✅ Imports successful
```

---

## Test Summary

| Test Category | Tests | Description |
|---------------|-------|-------------|
| BaseCollector | 5 | collect, safe_collect, error handling, disabled, repr |
| MetricsAggregator | 15 | init, add/remove, collect_all, concurrent, start/stop |
| Integration | 2 | full cycle, graceful degradation |
| **Total** | **22** | |
