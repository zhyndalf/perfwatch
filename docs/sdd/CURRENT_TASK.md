# Current Task

> **Status**: IN PROGRESS
> **Task ID**: T020
> **Task Name**: Data Retention

---

## Quick Context

Implement data retention policies, downsampling, and cleanup for historical metrics storage.

---

## What's Done (context)

- **Phase 1 Complete (5/5)**: Foundation - SDD, Docker, Database, Auth, Vue Base
- **Phase 2 Complete (7/7)**: Core Metrics - Collectors, WebSocket, Dashboard UI
- **Phase 3 Complete (5/5)**: Advanced Metrics - Perf Events, Cache, CPU Perf, Memory Bandwidth, Advanced Dashboard
- T017 Advanced Dashboard: ECharts visualization for all metrics, graceful degradation for perf_events
- Fixed perf_events collector to correctly report unavailable when cycles/instructions not accessible
- T019 Comparison View: compare endpoint + overlay charts + summary stats
- T020 Retention (in progress): API endpoints + cleanup service + Settings UI controls
- 203 backend tests passing

---

## What's Next

1. Wire retention settings into shared store/state
2. Add scheduled cleanup job or manual trigger in backend
3. Update docs and finalize T020

---

## Key Files from Previous Session

| File | Description |
|------|-------------|
| `backend/app/services/metrics_storage.py` | History query + batch persistence helpers |
| `backend/app/api/history.py` | History API endpoints |
| `frontend/src/views/History.vue` | History view + charts |

---

## Resume Instructions

**To continue PerfWatch development:**
1. Start services: `docker compose up -d`
2. Implement retention settings and cleanup logic
3. Update Settings UI for retention controls

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

**Session 9** (2026-01-20):
- T015 COMPLETED: CPU Perf Metrics - Branch prediction and DTLB metrics added
- T016 COMPLETED: Memory Bandwidth - /proc/vmstat page I/O monitoring

**Session 10** (2026-01-20):
- T017 COMPLETED: Advanced Dashboard - ECharts for perf_events & memory bandwidth
- Fixed perf_events collector availability check (requires cycles+instructions)
- **Phase 3 Advanced Metrics Complete!**

**Next Session**:
- Start T020: Data Retention
