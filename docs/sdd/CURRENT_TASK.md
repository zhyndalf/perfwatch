# Current Task

> **Status**: READY TO START
> **Task ID**: T015
> **Task Name**: CPU Perf Metrics

---

## Quick Context

Extend CPU performance metrics with additional perf_events counters. This may include branch predictions, TLB metrics, or other CPU-specific counters.

---

## What's Done (context)

- **Phase 1 Complete (5/5)**: Foundation - SDD, Docker, Database, Auth, Vue Base
- **Phase 2 Complete (7/7)**: Core Metrics - Collectors, WebSocket, Dashboard UI
- **Phase 3 In Progress (2/5)**: T013 Perf Events, T014 Cache Metrics completed
- T014 Cache Metrics: L1D and LLC cache miss rates added to PerfEventsCollector
- 166 backend tests passing

---

## What's Next

1. Review T015 task file (to be created)
2. Add additional CPU performance counters (branches, TLB, etc.)
3. Update schema and tests

---

## Key Files from Previous Session

| File | Description |
|------|-------------|
| `backend/app/collectors/perf_events.py` | Now includes cache metrics (L1D, LLC) |
| `backend/app/schemas/metrics.py` | PerfEventsMetrics with cache fields |
| `backend/tests/test_perf_events.py` | 35 tests for perf_events |

---

## Resume Instructions

**To continue PerfWatch development:**
1. Start services: `docker compose up -d`
2. Add more CPU performance counters to perf_events collector
3. Note: perf_events may not work in unprivileged Docker containers or VMs

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
- T007 COMPLETED: CPU Collector complete
- T008 COMPLETED: Memory Collector complete
- T009 COMPLETED: Network Collector complete
- T010 COMPLETED: Disk Collector complete
- T011 COMPLETED: WebSocket Streaming complete

**Session 7** (2026-01-20):
- T012 COMPLETED: Dashboard UI complete - ECharts charts, WebSocket integration, responsive layout
- **Phase 2 Core Metrics Complete!**

**Session 8** (2026-01-20):
- T013 COMPLETED: Perf Events Setup - Linux perf_events with ctypes, cycles/instructions/IPC metrics
- T014 COMPLETED: Cache Metrics - L1D and LLC cache miss rates added
- **Phase 3 Advanced Metrics 40% complete!**

**Next Session**:
- Start T015: CPU Perf Metrics
