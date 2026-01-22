# T014: Cache Metrics

> **Phase**: 3 - Advanced Metrics
> **Status**: ✅ Completed
> **Priority**: High
> **Estimated Effort**: Medium
> **Dependencies**: T013 (Perf Events Setup)
> **Completed**: 2026-01-20

---

## Overview

Extend the PerfEventsCollector to collect CPU cache and TLB counters via perf stat. Use raw counts without derived miss rates.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Collect L1 data cache loads | Must |
| FR-2 | Collect L1 data cache load misses | Must |
| FR-3 | Collect L1 instruction cache loads | Must |
| FR-4 | Collect LLC (Last Level Cache) loads | Must |
| FR-5 | Collect LLC load misses | Must |
| FR-6 | Gracefully handle unavailable cache counters | Must |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Reuse existing perf stat infrastructure from T013 |
| NFR-2 | No additional external dependencies |
| NFR-3 | Graceful degradation when specific cache events unavailable |
| NFR-4 | Include cache metrics in WebSocket stream |

---

## Technical Design

### Hardware Cache Events

Perf stat exposes cache/TLB events by name:

- L1-dcache-loads
- L1-dcache-load-misses
- L1-icache-loads
- LLC-loads
- LLC-load-misses
- dTLB-loads
- dTLB-load-misses
- iTLB-loads
- iTLB-load-misses

### Metrics to Collect

| Metric | Description |
|--------|-------------|
| L1-dcache-loads | L1 data cache loads |
| L1-dcache-load-misses | L1 data cache load misses |
| L1-icache-loads | L1 instruction cache loads |
| LLC-loads | Last Level Cache loads |
| LLC-load-misses | Last Level Cache load misses |
| dTLB-loads | Data TLB loads |
| dTLB-load-misses | Data TLB load misses |
| iTLB-loads | Instruction TLB loads |
| iTLB-load-misses | Instruction TLB load misses |

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

- [x] L1 data cache loads/misses collected
- [x] L1 instruction cache loads collected
- [x] LLC loads/misses collected
- [x] TLB counters collected
- [x] Graceful degradation when cache events unavailable
- [x] Schema updated with cache fields
- [x] Tests added for cache metrics
- [x] Works alongside existing perf stat events

---

## Testing Plan

### Unit Tests

1. `test_collect_cache_metrics_available` - Cache counters when available
2. `test_collect_cache_metrics_unavailable` - Graceful degradation
3. `test_missing_cache_event_marks_unavailable` - Missing event handling
4. `test_cache_events_in_event_list` - Event list includes cache counters

### Manual Verification

```bash
# Compare with perf stat
perf stat -e L1-dcache-loads,L1-dcache-load-misses,LLC-loads,LLC-load-misses -a sleep 1
```

---

## References

- [perf-stat man page](https://man7.org/linux/man-pages/man1/perf-stat.1.html)
