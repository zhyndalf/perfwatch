# T013: Perf Events Setup

> **Phase**: 3 - Advanced Metrics
> **Status**: ✅ Completed
> **Priority**: High
> **Estimated Effort**: Medium
> **Dependencies**: T006 (Collector Base), T011 (WebSocket Streaming)
> **Completed**: 2026-01-20

---

## Overview

Implement Linux perf_events integration for hardware performance counters. This is the foundation for Phase 3 (Advanced Metrics) and enables cache miss, IPC, and memory bandwidth metrics in subsequent tasks.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Detect if perf_events is available on the system | Must |
| FR-2 | Collect CPU cycles count when available | Must |
| FR-3 | Collect instructions count when available | Must |
| FR-4 | Calculate IPC (Instructions Per Cycle) | Must |
| FR-5 | Return `{"available": False}` when perf_events unavailable | Must |
| FR-6 | Integrate with WebSocket streaming | Must |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | No external Python dependencies (use ctypes) |
| NFR-2 | Graceful degradation on permission errors |
| NFR-3 | No crashes in Docker containers without perf access |
| NFR-4 | Follow existing BaseCollector pattern |

---

## Technical Design

### Approach

Use Python's `ctypes` library to directly invoke the `perf_event_open` syscall. This avoids external dependencies and gives full control over the perf_events interface.

### Key Components

1. **perf_event_attr Structure**: C struct definition matching kernel headers
2. **Syscall Wrapper**: Direct syscall via `ctypes.CDLL(None).syscall`
3. **Availability Detection**:
   - Check `/proc/sys/kernel/perf_event_paranoid` exists
   - Attempt test syscall to verify permissions
4. **Counter Reading**: Read file descriptor to get counter values

### Hardware Events

| Event | Constant | Description |
|-------|----------|-------------|
| CPU Cycles | `PERF_COUNT_HW_CPU_CYCLES` (0) | Total CPU cycles |
| Instructions | `PERF_COUNT_HW_INSTRUCTIONS` (1) | Retired instructions |

### perf_event_open Syscall

```c
// Syscall signature
int perf_event_open(struct perf_event_attr *attr,
                    pid_t pid,
                    int cpu,
                    int group_fd,
                    unsigned long flags);

// Parameters used:
// pid = 0 (current process)
// cpu = -1 (any CPU)
// group_fd = -1 (no group leader)
// flags = 0
```

### Graceful Degradation

| Condition | Response |
|-----------|----------|
| `/proc/sys/kernel/perf_event_paranoid` not found | `{"available": False}` |
| `perf_event_open` returns EACCES/EPERM | `{"available": False}` |
| Running in unprivileged container | `{"available": False}` |
| Syscall succeeds | Full metrics collection |

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
- [x] `is_available()` correctly detects perf_events availability
- [x] Collects cycles and instructions when available
- [x] Calculates IPC (instructions / cycles)
- [x] Returns `{"available": False}` when unavailable (no crash)
- [x] Integrated with WebSocket streaming
- [x] All tests pass (including graceful degradation) - 26 tests
- [x] Works in Docker (or degrades gracefully)

---

## Testing Plan

### Unit Tests

1. `test_availability_detection` - Verify `is_available()` works
2. `test_collect_when_unavailable` - Returns `{"available": False}`
3. `test_collect_when_available` - Returns cycles/instructions/ipc (mocked)
4. `test_graceful_error_handling` - No crashes on permission errors
5. `test_disabled_collector` - Respects enabled flag
6. `test_collector_name` - Has correct name attribute

### Integration Tests

1. `test_with_aggregator` - Works in MetricsAggregator context
2. `test_safe_collect_metadata` - Adds timestamp and error fields

### Manual Verification

```bash
# In Docker container
docker compose exec backend python -c "
from app.collectors.perf_events import PerfEventsCollector
import asyncio
c = PerfEventsCollector()
print('Available:', c.is_available())
print(asyncio.run(c.collect()))
"

# Compare with host perf (if available)
perf stat -e cycles,instructions sleep 1
```

---

## References

- [Linux perf_event_open man page](https://man7.org/linux/man-pages/man2/perf_event_open.2.html)
- [Kernel perf_event.h](https://github.com/torvalds/linux/blob/master/include/uapi/linux/perf_event.h)
- [perf_event_paranoid settings](https://www.kernel.org/doc/html/latest/admin-guide/perf-security.html)

---

## Notes

- perf_events requires special permissions (CAP_PERFMON or CAP_SYS_ADMIN) or `perf_event_paranoid <= 2`
- Docker containers may need `--privileged` flag or specific capabilities
- ARM and x86 have different event semantics but CYCLES/INSTRUCTIONS are universal
