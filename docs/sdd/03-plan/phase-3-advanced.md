# Phase 3: Advanced Metrics

> perf stat integration for hardware performance counters

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

**Objective**: Set up perf stat streaming and basic event parsing.

**Task File**: [T013-perf-events-setup.md](../04-tasks/phase-3/T013-perf-events-setup.md)

**Deliverables**:
- `perf stat -I` subprocess integration
- CSV output parsing for supported events
- Basic event collection (cycles, instructions, branches, cache/TLB events)
- Configurable CPU cores + interval
- Availability detection and graceful fallback

**Key Challenges**:
- perf permissions and PMU exposure (VMs, BIOS, kernel config)
- Parsing perf stat CSV output reliably
- Handling missing or unsupported events

**Acceptance Criteria**:
- [ ] perf stat starts successfully
- [ ] Reads raw counters (cycles/instructions/etc.)
- [ ] Detects missing or unsupported events
- [ ] Returns `available: false` gracefully on failure

---

## T014: Cache Metrics {#t014}

**Objective**: Collect cache and TLB counters via perf stat.

**Task File**: [T014-cache-metrics.md](../04-tasks/phase-3/T014-cache-metrics.md)

**Deliverables**:
- L1 data cache load/miss counters
- L1 instruction cache load counters
- LLC load/miss counters
- dTLB/iTLB load/miss counters
- Raw counts only (no derived rates)

**Key Challenges**:
- Not all CPUs/VMs expose cache/TLB events
- perf stat event names vary by kernel/PMU
- Need to handle unsupported events

**Acceptance Criteria**:
- [ ] L1 cache counters collected
- [ ] LLC counters collected
- [ ] TLB counters collected
- [ ] Raw counts match perf stat output
- [ ] Unsupported events handled gracefully

---

## T015: CPU Perf Metrics {#t015}

**Objective**: Collect CPU performance counters via perf stat.

**Task File**: [T015-cpu-perf-metrics.md](../04-tasks/phase-3/T015-cpu-perf-metrics.md)

**Deliverables**:
- cycles and instructions counters
- Branch counters and misses
- Context switch and migration counts
- Page fault counts

**Key Challenges**:
- Per-core vs system-wide collection
- Multiplexing if too many events requested
- Matching perf stat output timing

**Acceptance Criteria**:
- [ ] cycles/instructions/branches collected
- [ ] Values match `perf stat` output
- [ ] Handles event multiplexing
- [ ] Supports configurable core lists

---

## T016: Memory Bandwidth {#t016}

**Objective**: Estimate memory activity via /proc/vmstat rates.

**Task File**: [T016-memory-bandwidth.md](../04-tasks/phase-3/T016-memory-bandwidth.md)

**Deliverables**:
- Page in/out rates (pgpgin/pgpgout)
- Swap in/out rates (pswpin/pswpout)
- Page fault rates
- Reported as KB/s or per-second counts

**Key Challenges**:
- Interpreting /proc/vmstat fields consistently
- Sampling at consistent intervals
- Avoiding divide-by-zero or missing fields

**Acceptance Criteria**:
- [ ] pgpgin/pgpgout rates computed
- [ ] pswpin/pswpout rates computed
- [ ] Values reasonable (sanity check)
- [ ] Works on target system

---

## T017: Advanced Dashboard {#t017}

**Objective**: Add advanced metrics to dashboard UI.

**Task File**: [T017-advanced-dashboard.md](../04-tasks/phase-3/T017-advanced-dashboard.md)

**Deliverables**:
- Perf counters grid/table
- Perf event selector for history chart
- Memory bandwidth display
- "Unavailable" state UI
- Integration with existing dashboard

**Acceptance Criteria**:
- [ ] Perf counters displayed
- [ ] History chart switches by perf event
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

### perf stat Command

```bash
perf stat -I <interval_ms> -x , --no-big-num -a -e <events> [-C <cores>]
```

**Notes:**
- `-I` emits periodic samples at the requested interval.
- `-x ,` emits CSV output for parsing.
- `-C` limits collection to a CPU core list; omit for all cores.

### Output Parsing

`perf stat` emits CSV lines in the form:

```
<time>,<value>,<unit>,<event>,...
```

Samples are grouped by `<time>` to build a single snapshot. Missing or unsupported
events mark the sample unavailable.

---

## End State

After Phase 3 is complete:

1. **perf_events**: perf stat streaming with raw counters
2. **Cache/TLB**: L1/LLC/TLB counters available
3. **CPU Perf**: cycles/instructions/branches visible
4. **Memory Activity**: /proc/vmstat rates shown
5. **Dashboard**: All advanced metrics visible

### Verification Steps

```bash
# Check perf_event_paranoid
cat /proc/sys/kernel/perf_event_paranoid

# Verify perf stat in container
docker compose exec backend perf stat -e cycles,instructions -a sleep 1

# Compare against host perf stat if needed
perf stat -e cycles,instructions,L1-dcache-load-misses -a sleep 1
```

### Graceful Degradation

When perf stat is not available:
1. Backend returns `available: false` in perf data
2. Frontend shows "Not available on this system"
3. Other metrics continue working normally
4. No errors or crashes
