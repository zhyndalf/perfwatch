# T008: Memory Collector

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 2 - Core Metrics |
| **Estimated Time** | 2 hours |
| **Dependencies** | T006 (Collector Base) |
| **Status** | ⬜ NOT_STARTED |

---

## Objective

Implement a Memory metrics collector using psutil that gathers RAM and swap usage.

---

## Acceptance Criteria

### Memory Metrics Collection
- [ ] Total physical memory
- [ ] Available/used memory
- [ ] Memory usage percentage
- [ ] Swap total/used/percentage
- [ ] Buffer and cache (Linux)

### Implementation
- [ ] Inherits from BaseCollector
- [ ] Uses psutil for all metrics
- [ ] Handles missing metrics gracefully

### Testing
- [ ] Unit tests for Memory collector
- [ ] Integration test with aggregator
