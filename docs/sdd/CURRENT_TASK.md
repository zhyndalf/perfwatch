# Current Task

> **Status**: READY TO START
> **Task ID**: T014
> **Task Name**: Cache Metrics

---

## Quick Context

Implement cache miss rate collection using perf_events hardware counters. This builds on T013 to add cache performance metrics.

---

## What's Done (context)

- **Phase 1 Complete (5/5)**: Foundation - SDD, Docker, Database, Auth, Vue Base
- **Phase 2 Complete (7/7)**: Core Metrics - Collectors, WebSocket, Dashboard UI
- **Phase 3 Started (1/5)**: T013 Perf Events Setup completed
- T013 Perf Events: PerfEventsCollector with ctypes syscall, graceful degradation
- 157 backend tests passing

---

## What's Next

1. Review T014 task file (to be created)
2. Add cache miss/hit counters to PerfEventsCollector
3. Calculate cache miss rate metrics
4. Update dashboard with cache metrics visualization

---

## Key Files from Previous Session

| File | Description |
|------|-------------|
| `backend/app/collectors/perf_events.py` | Linux perf_events collector (NEW) |
| `backend/app/schemas/metrics.py` | PerfEventsMetrics schema added |
| `backend/app/api/websocket.py` | Now includes perf_events in stream |
| `backend/tests/test_perf_events.py` | 26 tests for perf_events |

---

## Resume Instructions

**To continue PerfWatch development:**
1. Start services: `docker compose up -d`
2. Extend perf_events collector with cache metrics
3. Note: perf_events may not work in unprivileged Docker containers

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
- **Phase 3 Advanced Metrics Started!**

**Next Session**:
- Start T014: Cache Metrics
