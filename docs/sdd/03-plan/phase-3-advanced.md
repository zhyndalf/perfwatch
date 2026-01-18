# Phase 3: Advanced Metrics

> perf_events integration for hardware performance counters

---

## Overview

| Aspect | Details |
|--------|---------|
| Duration | ~13 hours (5 sessions) |
| Tasks | T013-T017 |
| Goal | Hardware counters visible |
| Prerequisites | Phase 2 complete |

---

## Task Summary

| Task | Name | Est. Time | Status |
|------|------|-----------|--------|
| T013 | Perf Events Setup | 3-4 hrs | ⬜ Not Started |
| T014 | Cache Metrics | 2-3 hrs | ⬜ Not Started |
| T015 | CPU Perf Metrics | 2-3 hrs | ⬜ Not Started |
| T016 | Memory Bandwidth | 2-3 hrs | ⬜ Not Started |
| T017 | Advanced Dashboard | 2-3 hrs | ⬜ Not Started |

---

## T013: Perf Events Setup {#t013}

**Objective**: Set up perf_event_open wrapper and basic event reading.

**Task File**: [T013-perf-events-setup.md](../04-tasks/phase-3/T013-perf-events-setup.md)

**Deliverables**:
- Python wrapper for `perf_event_open` syscall
- Event configuration structures
- Basic event reading (cycles, instructions)
- Availability detection
- Graceful fallback when unavailable

**Key Challenges**:
- System call interface from Python
- Handling permission errors
- CPU-specific event codes

**Acceptance Criteria**:
- [ ] Can open perf events successfully
- [ ] Reads basic counters (cycles/instructions)
- [ ] Detects when unavailable
- [ ] Returns None gracefully on failure

---

## T014: Cache Metrics {#t014}

**Objective**: Collect cache miss metrics via perf_events.

**Task File**: [T014-cache-metrics.md](../04-tasks/phase-3/T014-cache-metrics.md)

**Deliverables**:
- L1 instruction cache miss collection
- L1 data cache miss collection
- L2 cache miss collection (if available)
- L3/LLC cache miss collection
- Miss rate calculations

**Key Challenges**:
- Not all CPUs support all cache events
- Event codes vary by CPU architecture
- Need to handle unsupported events

**Acceptance Criteria**:
- [ ] L1-I cache misses collected
- [ ] L1-D cache misses collected
- [ ] LLC misses collected
- [ ] Miss rates calculated correctly
- [ ] Unsupported events handled gracefully

---

## T015: CPU Perf Metrics {#t015}

**Objective**: Collect IPC and detailed CPU performance metrics.

**Task File**: [T015-cpu-perf-metrics.md](../04-tasks/phase-3/T015-cpu-perf-metrics.md)

**Deliverables**:
- IPC calculation (instructions/cycles)
- Branch prediction metrics (if available)
- Interrupt counting
- Context switch counting

**Key Challenges**:
- Accurate IPC calculation
- Multiplexing when too many events
- Per-core vs system-wide collection

**Acceptance Criteria**:
- [ ] IPC calculated and accurate
- [ ] Values match `perf stat` output
- [ ] Handles event multiplexing
- [ ] Integrates with existing CPU collector

---

## T016: Memory Bandwidth {#t016}

**Objective**: Measure memory read/write bandwidth via IMC counters.

**Task File**: [T016-memory-bandwidth.md](../04-tasks/phase-3/T016-memory-bandwidth.md)

**Deliverables**:
- IMC (Integrated Memory Controller) counter access
- Read bandwidth calculation (MB/s)
- Write bandwidth calculation (MB/s)
- Total bandwidth reporting

**Key Challenges**:
- IMC counters are CPU-specific
- Requires uncore perf events
- May need different approach for AMD vs Intel

**Acceptance Criteria**:
- [ ] Read bandwidth measured
- [ ] Write bandwidth measured
- [ ] Values reasonable (sanity check)
- [ ] Works on target system

---

## T017: Advanced Dashboard {#t017}

**Objective**: Add advanced metrics to dashboard UI.

**Task File**: [T017-advanced-dashboard.md](../04-tasks/phase-3/T017-advanced-dashboard.md)

**Deliverables**:
- Cache performance card and chart
- IPC display component
- Memory bandwidth display
- "Unavailable" state UI
- Integration with existing dashboard

**Acceptance Criteria**:
- [ ] Cache metrics displayed
- [ ] IPC shown prominently
- [ ] Bandwidth visualized
- [ ] Graceful UI when unavailable
- [ ] No layout issues

---

## Dependency Graph

```
T013 (Perf Events Setup)
  │
  ├──► T014 (Cache Metrics)
  │
  ├──► T015 (CPU Perf Metrics)
  │
  └──► T016 (Memory Bandwidth)
         │
         └──► T017 (Advanced Dashboard)
```

Note: T014-T016 can be done in any order after T013.

---

## Technical Background

### perf_event_open System Call

```c
int perf_event_open(
    struct perf_event_attr *attr,
    pid_t pid,      // -1 for all processes
    int cpu,        // -1 for all CPUs
    int group_fd,   // -1 for new group
    unsigned long flags
);
```

### Python Wrapper Approach

```python
import ctypes

# Load libc
libc = ctypes.CDLL('libc.so.6', use_errno=True)

# Define perf_event_attr structure
class perf_event_attr(ctypes.Structure):
    _fields_ = [
        ('type', ctypes.c_uint32),
        ('size', ctypes.c_uint32),
        ('config', ctypes.c_uint64),
        # ... more fields
    ]

# Make syscall
fd = libc.syscall(298, ctypes.byref(attr), -1, cpu, -1, 0)
```

### Event Types

| Type | Value | Description |
|------|-------|-------------|
| PERF_TYPE_HARDWARE | 0 | Generic hardware events |
| PERF_TYPE_SOFTWARE | 1 | Software events |
| PERF_TYPE_HW_CACHE | 3 | Hardware cache events |
| PERF_TYPE_RAW | 4 | CPU-specific raw events |

---

## End State

After Phase 3 is complete:

1. **perf_events**: Working wrapper in Python
2. **Cache Metrics**: L1/L2/L3 miss rates available
3. **CPU Perf**: IPC and cycles displayed
4. **Memory Bandwidth**: Read/write MB/s shown
5. **Dashboard**: All advanced metrics visible

### Verification Steps

```bash
# Check if perf_events available
cat /proc/sys/kernel/perf_event_paranoid

# Verify in container
docker-compose exec backend python -c "
from app.collectors.perf_events import PerfEventsCollector
c = PerfEventsCollector()
print('Available:', c.is_available())
print(c.collect())
"

# Compare with perf stat
perf stat -e cycles,instructions,L1-dcache-load-misses sleep 1
```

### Graceful Degradation

When perf_events is not available:
1. Backend returns `available: false` in perf data
2. Frontend shows "Not available on this system"
3. Other metrics continue working normally
4. No errors or crashes
