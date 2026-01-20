# Current Task

> **Status**: READY TO START
> **Task ID**: T018
> **Task Name**: History Storage

---

## Quick Context

Implement persistent storage for metrics snapshots. Save WebSocket metrics to the database and create API endpoints for querying historical data with time-range filters.

---

## What's Done (context)

- **Phase 1 Complete (5/5)**: Foundation - SDD, Docker, Database, Auth, Vue Base
- **Phase 2 Complete (7/7)**: Core Metrics - Collectors, WebSocket, Dashboard UI
- **Phase 3 Complete (5/5)**: Advanced Metrics - Perf Events, Cache, CPU Perf, Memory Bandwidth, Advanced Dashboard
- T017 Advanced Dashboard: ECharts visualization for all metrics, graceful degradation for perf_events
- Fixed perf_events collector to correctly report unavailable when cycles/instructions not accessible
- 203 backend tests passing

---

## What's Next

1. Save metrics snapshots to `metrics_snapshot` table during WebSocket broadcast
2. Create `/api/history/metrics` endpoint with time-range query parameters
3. Add downsampling for older data to manage storage
4. Frontend History view to display historical charts

---

## Key Files from Previous Session

| File | Description |
|------|-------------|
| `backend/app/collectors/perf_events.py` | Fixed availability check for cycles/instructions |
| `frontend/src/views/Dashboard.vue` | Complete dashboard with all advanced metrics |
| `frontend/src/stores/metrics.js` | Metrics store with history arrays |
| `backend/app/api/websocket.py` | WebSocket endpoint broadcasting all metrics |

---

## Resume Instructions

**To continue PerfWatch development:**
1. Start services: `docker compose up -d`
2. Implement metrics persistence in WebSocket handler
3. Create history API endpoint with filters
4. Add History view in frontend

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
- Start T018: History Storage
