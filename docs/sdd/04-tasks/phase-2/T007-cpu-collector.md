# T007: CPU Collector

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 2 - Core Metrics |
| **Estimated Time** | 2-3 hours |
| **Dependencies** | T006 (Collector Base) |
| **Status** | ✅ COMPLETED |
| **Completed** | 2026-01-19 |

---

## Objective

Implement a CPU metrics collector using psutil that gathers CPU usage, per-core stats, frequency, and load averages.

---

## Acceptance Criteria

### CPU Metrics Collection
- [x] Overall CPU usage percentage
- [x] Per-core usage percentages
- [x] User/system/idle time breakdown
- [x] I/O wait time (Linux)
- [x] CPU frequency per core (if available)
- [x] 1/5/15 minute load averages
- [x] CPU temperature (graceful if unavailable)
- [x] Logical and physical core counts

### Implementation
- [x] Inherits from BaseCollector
- [x] Uses psutil for all metrics
- [x] Handles missing metrics gracefully (returns None)
- [x] Returns data matching CPUMetrics schema

### Testing
- [x] 16 unit tests for CPU collector
- [x] Tests for graceful degradation
- [x] Integration test with aggregator

---

## Implementation Notes

### Key Features

1. **Primed measurements** - Constructor calls `cpu_percent()` once to prime the measurement for accurate subsequent readings
2. **Graceful degradation** - Optional metrics (frequency, temperature, load) return None if unavailable
3. **Cross-platform** - Works on Linux/macOS; some metrics may be unavailable on certain systems
4. **Temperature sensors** - Tries common sensor names (coretemp, cpu_thermal, k10temp, zenpower)

### Metrics Collected

| Metric | Type | Description |
|--------|------|-------------|
| `usage_percent` | float | Overall CPU usage % |
| `per_core` | List[float] | Per-core usage % |
| `user` | float | User mode time % |
| `system` | float | Kernel mode time % |
| `idle` | float | Idle time % |
| `iowait` | float | I/O wait % (Linux only) |
| `frequency_mhz` | List[float] | Per-core frequency in MHz |
| `load_avg` | List[float] | [1min, 5min, 15min] load averages |
| `temperature` | float | CPU temperature in Celsius |
| `core_count` | int | Logical core count |
| `physical_cores` | int | Physical core count |

---

## Files Created/Modified

| File | Action | Description |
|------|--------|-------------|
| `backend/app/collectors/cpu.py` | Created | CPUCollector implementation |
| `backend/app/collectors/__init__.py` | Modified | Added CPUCollector export |
| `backend/tests/test_cpu_collector.py` | Created | 16 unit tests |

---

## Verification Results

```bash
# Run CPU collector tests
docker compose run --rm backend pytest tests/test_cpu_collector.py -v
# ✅ 16 passed

# Run all tests
docker compose run --rm backend pytest tests/ -v
# ✅ 89 passed (73 existing + 16 new)

# Manual test output
docker compose exec backend python -c "..."
# CPU Metrics:
#   Usage: 0.0%
#   Per Core: [0.0, 0.0, 0.0, 0.0]
#   Load Avg: [2.64, 2.01, 1.49]
#   Frequency: [3110.4, 3110.4, 3110.4, 3110.4]
#   Cores: 4 logical, 4 physical
```

---

## Test Summary

| Test Category | Tests | Description |
|---------------|-------|-------------|
| Basic Collection | 7 | usage, per_core, times, core_count, optional fields |
| Metadata | 4 | safe_collect, disabled, name, repr |
| Graceful Degradation | 3 | frequency, temperature, load_avg unavailable |
| Integration | 2 | with aggregator, multiple collections |
| **Total** | **16** | |
