# Current Task

> **Status**: READY TO START
> **Task ID**: T013
> **Task Name**: Perf Events Setup

---

## Quick Context

Set up Linux perf_events integration for advanced hardware performance counters. This is the first task of Phase 3 (Advanced Metrics).

---

## What's Done (context)

- **Phase 1 Complete (5/5)**: Foundation - SDD, Docker, Database, Auth, Vue Base
- **Phase 2 Complete (7/7)**: Core Metrics - Collectors, WebSocket, Dashboard UI
- T012 Dashboard UI completed: Real-time charts for CPU/Memory/Network/Disk streaming via WebSocket
- 131 backend tests passing

---

## What's Next

1. Review T013 task file at `docs/sdd/04-tasks/phase-3/T013-perf-events-setup.md`
2. Implement perf_events integration with graceful degradation
3. Test with and without perf_events availability

---

## Key Files from Previous Session

| File | Description |
|------|-------------|
| `frontend/src/stores/metrics.js` | Pinia store for WebSocket metrics |
| `frontend/src/views/Dashboard.vue` | Real-time dashboard with ECharts |
| `backend/app/api/websocket.py` | WebSocket streaming endpoint |
| `backend/app/collectors/` | CPU, Memory, Network, Disk collectors |

---

## Resume Instructions

**To continue PerfWatch development:**
1. Read T013 task file: `docs/sdd/04-tasks/phase-3/T013-perf-events-setup.md`
2. Start services: `docker compose up -d`
3. Begin implementing perf_events collector with graceful degradation

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

**Next Session**:
- Start T013: Perf Events Setup (Phase 3)
