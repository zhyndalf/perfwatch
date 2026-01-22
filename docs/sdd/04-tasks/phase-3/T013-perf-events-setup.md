# T013: Perf Events Setup

> **Phase**: 3 - Advanced Metrics
> **Status**: ✅ Completed
> **Priority**: High
> **Estimated Effort**: Medium
> **Dependencies**: T006 (Collector Base), T011 (WebSocket Streaming)
> **Completed**: 2026-01-20

---

## Overview

Implement perf stat integration for hardware performance counters. This is the foundation for Phase 3 (Advanced Metrics) and enables raw perf counters in the dashboard and history views.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Detect if perf stat is available on the system | Must |
| FR-2 | Collect configured perf stat events when available | Must |
| FR-3 | Support configurable CPU core list and interval | Must |
| FR-4 | Return `{"available": False}` when any event is missing/unsupported | Must |
| FR-5 | Integrate with WebSocket streaming | Must |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | No external Python dependencies (use asyncio subprocess) |
| NFR-2 | Graceful degradation on permission errors |
| NFR-3 | No crashes in Docker containers without perf access |
| NFR-4 | Follow existing BaseCollector pattern |

---

## Technical Design

### Approach

Use `perf stat -I` as a subprocess and parse its CSV output. This avoids low-level syscall bindings
and tracks hardware counters through the supported perf interface.

### Key Components

1. **Command Builder**: `perf stat -I <interval> -x , --no-big-num -a -e <events> [-C <cores>]`
2. **Streaming Reader**: Async read loop to consume perf output continuously
3. **CSV Parser**: Parse `<time>,<value>,<unit>,<event>` lines into events map
4. **Availability Detection**:
   - Check `perf` binary exists
   - Track missing or unsupported events per sample
5. **Snapshot Assembly**: Build `{available, cpu_cores, interval_ms, events}` payloads

### Hardware Events

perf stat events collected:

- cpu-clock
- context-switches
- cpu-migrations
- page-faults
- cycles
- instructions
- branches
- branch-misses
- L1-dcache-loads
- L1-dcache-load-misses
- LLC-loads
- LLC-load-misses
- L1-icache-loads
- dTLB-loads
- dTLB-load-misses
- iTLB-loads
- iTLB-load-misses

### perf stat Command

```bash
perf stat -I 1000 -x , --no-big-num -a -e cycles,instructions,branches
```

### Graceful Degradation

| Condition | Response |
|-----------|----------|
| `perf` binary missing | `{"available": False, "error": "perf binary not found"}` |
| perf permission denied (`perf_event_paranoid` too high) | `{"available": False}` |
| Unsupported/missing event names | `{"available": False, "missing_events": [...]}` |
| perf stat stops unexpectedly | `{"available": False, "error": "perf stat stopped"}` |
| perf stat running and all events present | Full metrics collection |

---

## Implementation Files

| File | Action | Description |
|------|--------|-------------|
| `backend/app/collectors/perf_events.py` | Create | PerfEventsCollector implementation |
| `backend/app/schemas/metrics.py` | Modify | Add PerfEventsMetrics schema |
| `backend/app/collectors/__init__.py` | Modify | Export PerfEventsCollector |
| `backend/app/api/websocket.py` | Modify | Add to aggregator |
| `backend/tests/test_perf_events.py` | Create | Unit and integration tests |

---

## Acceptance Criteria

- [x] PerfEventsCollector follows BaseCollector pattern
- [x] Detects perf stat availability and permissions
- [x] Collects configured perf stat events when available
- [x] Returns `{"available": False}` when events are missing or unsupported
- [x] Integrated with WebSocket streaming
- [x] All tests pass (including graceful degradation)
- [x] Works in Docker (or degrades gracefully)

---

## Testing Plan

### Unit Tests

1. `test_parse_perf_stat_line` - Parse perf stat CSV lines
2. `test_collect_when_unavailable` - Returns `{"available": False}`
3. `test_collect_when_available` - Returns events map (mocked)
4. `test_collect_missing_events` - Marks unavailable with missing events
5. `test_disabled_collector` - Respects enabled flag
6. `test_collector_name` - Has correct name attribute

### Integration Tests

1. `test_with_aggregator` - Works in MetricsAggregator context
2. `test_safe_collect_metadata` - Adds timestamp and error fields

### Manual Verification

```bash
# In Docker container
docker compose exec backend perf stat -e cycles,instructions -a sleep 1

# Compare with host perf (if available)
perf stat -e cycles,instructions -a sleep 1
```

---

## References

- [perf-stat man page](https://man7.org/linux/man-pages/man1/perf-stat.1.html)
- [perf_event_paranoid settings](https://www.kernel.org/doc/html/latest/admin-guide/perf-security.html)

---

## Notes

- perf stat requires special permissions (CAP_PERFMON or CAP_SYS_ADMIN) or `perf_event_paranoid <= 2`
- Docker containers may need `--privileged` flag or specific capabilities
- VM environments need PMU passthrough to expose counters
