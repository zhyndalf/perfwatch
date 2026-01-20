# T014: Cache Metrics

> **Phase**: 3 - Advanced Metrics
> **Status**: ✅ Completed
> **Priority**: High
> **Estimated Effort**: Medium
> **Dependencies**: T013 (Perf Events Setup)
> **Completed**: 2026-01-20

---

## Overview

Extend the PerfEventsCollector to collect CPU cache performance metrics including L1, L2, L3/LLC cache misses and references. Calculate cache miss rates to identify memory-bound performance issues.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Collect L1 data cache misses | Must |
| FR-2 | Collect L1 data cache references (accesses) | Must |
| FR-3 | Collect LLC (Last Level Cache) misses | Must |
| FR-4 | Collect LLC references | Must |
| FR-5 | Calculate cache miss rates (misses/references) | Must |
| FR-6 | Gracefully handle unavailable cache counters | Must |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Reuse existing perf_events infrastructure from T013 |
| NFR-2 | No additional external dependencies |
| NFR-3 | Graceful degradation when specific cache events unavailable |
| NFR-4 | Include cache metrics in WebSocket stream |

---

## Technical Design

### Hardware Cache Events

Linux perf_events provides hardware cache events via `PERF_TYPE_HW_CACHE`:

| Event | Description |
|-------|-------------|
| L1-dcache-load-misses | L1 data cache read misses |
| L1-dcache-loads | L1 data cache reads (references) |
| LLC-load-misses | Last Level Cache read misses |
| LLC-loads | Last Level Cache reads |

### Cache Event Encoding

Cache events use a 64-bit config value encoded as:
```
config = (perf_hw_cache_id) | (perf_hw_cache_op_id << 8) | (perf_hw_cache_op_result_id << 16)
```

Where:
- `perf_hw_cache_id`: L1D=0, L1I=1, LL=2, DTLB=3, ITLB=4, BPU=5, NODE=6
- `perf_hw_cache_op_id`: READ=0, WRITE=1, PREFETCH=2
- `perf_hw_cache_op_result_id`: ACCESS=0, MISS=1

### Metrics to Collect

| Metric | Formula | Description |
|--------|---------|-------------|
| l1d_misses | Counter | L1 data cache misses |
| l1d_references | Counter | L1 data cache accesses |
| l1d_miss_rate | misses/references | L1 miss rate (0.0-1.0) |
| llc_misses | Counter | LLC misses |
| llc_references | Counter | LLC accesses |
| llc_miss_rate | misses/references | LLC miss rate (0.0-1.0) |

---

## Implementation Files

| File | Action | Description |
|------|--------|-------------|
| `backend/app/collectors/perf_events.py` | Modify | Add cache event constants and collection |
| `backend/app/schemas/metrics.py` | Modify | Add cache fields to PerfEventsMetrics |
| `backend/tests/test_perf_events.py` | Modify | Add cache metrics tests |
| `docs/sdd/04-tasks/phase-3/T014-cache-metrics.md` | Create | This file |

---

## Acceptance Criteria

- [x] L1 data cache misses and references collected
- [x] LLC misses and references collected
- [x] Cache miss rates calculated correctly
- [x] Graceful degradation when cache events unavailable
- [x] Schema updated with cache fields
- [x] Tests added for cache metrics (9 new tests)
- [x] Works alongside existing cycles/instructions metrics

---

## Testing Plan

### Unit Tests

1. `test_cache_event_encoding` - Verify cache config encoding
2. `test_collect_cache_metrics_available` - Full cache metrics when available
3. `test_collect_cache_metrics_unavailable` - Graceful degradation
4. `test_cache_miss_rate_calculation` - Verify miss rate math
5. `test_cache_miss_rate_zero_references` - Handle division by zero

### Manual Verification

```bash
# Compare with perf stat
perf stat -e L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses sleep 1
```

---

## References

- [perf_event_open man page - Hardware Cache Events](https://man7.org/linux/man-pages/man2/perf_event_open.2.html)
- [Linux kernel perf_event.h](https://github.com/torvalds/linux/blob/master/include/uapi/linux/perf_event.h)
