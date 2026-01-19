# Current Task

> **Status**: READY_FOR_IMPLEMENTATION
> **Task ID**: T007
> **Task File**: [T007-cpu-collector.md](./04-tasks/phase-2/T007-cpu-collector.md)

---

## Quick Context

Implement a CPU metrics collector using psutil that gathers CPU usage, per-core stats, frequency, and load averages.

---

## What's Done (Previous Task T006)

- [x] Created `backend/app/collectors/` package
- [x] Implemented `BaseCollector` abstract class with `safe_collect()` error handling
- [x] Implemented `MetricsAggregator` with concurrent collection and periodic callbacks
- [x] Created Pydantic schemas for CPU, Memory, Network, Disk metrics
- [x] Added 22 unit tests for collector infrastructure
- [x] All 73 tests passing

---

## What's Next (T007)

1. Create `CPUCollector` class using psutil
2. Collect CPU usage, per-core, user/system/idle times
3. Add frequency and load average collection
4. Handle missing metrics gracefully
5. Write unit tests

---

## Resume Instructions

**To continue PerfWatch development:**
1. Say "Let's continue perfwatch" or similar
2. I'll read this file and the T007 task file
3. We'll implement the CPU collector

**Project Location**: `/home/zhyndalf/vibeCoding/perfwatch`
**GitHub**: https://github.com/zhyndalf/perfwatch

---

## Blockers

None currently.

---

## Session Notes

**Session 1** (2025-01-18):
- T001 COMPLETED: Full SDD structure created with 25+ documentation files

**Session 2** (2025-01-19):
- T002 COMPLETED: Docker setup complete

**Session 3** (2025-01-19):
- T003 COMPLETED: Database setup complete

**Session 4** (2026-01-19):
- T004 COMPLETED: Auth backend complete

**Session 5** (2026-01-19):
- T005 COMPLETED: Vue Frontend Base complete
- **Phase 1 Foundation Complete!**

**Session 6** (2026-01-19):
- T006 COMPLETED: Collector Base complete
- Created BaseCollector abstract class
- Created MetricsAggregator with concurrent collection
- Created Pydantic schemas for all metric types
- 22 new tests (73 total)

**Next**:
- T007: CPU Collector with psutil
