# Current Task

> **Status**: IN_PROGRESS
> **Task ID**: T011
> **Task Name**: WebSocket Streaming

---

## Quick Context

Implement WebSocket endpoint for real-time metrics streaming to the frontend. The endpoint streams CPU, Memory, Network, and Disk metrics every 5 seconds.

---

## What's Done (T011 - Partial)

- [x] Created `backend/app/api/websocket.py` with WebSocket endpoint
- [x] Implemented `ConnectionManager` class for handling multiple clients
- [x] Implemented JWT authentication for WebSocket via query parameter (`?token=<jwt>`)
- [x] Integrated `MetricsAggregator` with all 4 collectors (CPU, Memory, Network, Disk)
- [x] Added broadcast callback for 5-second metric streaming
- [x] Registered WebSocket router in `main.py`
- [ ] Write unit tests for WebSocket streaming
- [ ] Update README.md and progress files

---

## What's Next (T011 - Remaining)

1. Write unit tests for WebSocket endpoint
2. Test the WebSocket connection manually
3. Update documentation and progress files
4. After T011: Continue to T012 (Dashboard UI)

---

## Key Files Created/Modified This Session

| File | Action | Description |
|------|--------|-------------|
| `backend/app/api/websocket.py` | Created | WebSocket endpoint with ConnectionManager |
| `backend/app/main.py` | Modified | Added websocket_router import and registration |

---

## WebSocket API Details

**Endpoint**: `ws://localhost:8000/api/ws/metrics?token=<jwt_token>`

**Server sends every 5 seconds**:
```json
{
  "type": "metrics",
  "timestamp": "2026-01-19T14:30:05Z",
  "data": {
    "cpu": { ... },
    "memory": { ... },
    "network": { ... },
    "disk": { ... }
  }
}
```

**Client can send**:
```json
{ "type": "ping" }
```

**Server responds**:
```json
{ "type": "pong" }
```

---

## Resume Instructions

**To continue PerfWatch development:**
1. Say "Let's continue perfwatch" or "Continue T011"
2. Read this file for context
3. Remaining work: Write tests for WebSocket, update docs

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
- T011 IN PROGRESS: WebSocket Streaming (core implementation done, tests pending)

**Current Session Work**:
- Created WebSocket endpoint with JWT auth
- Created ConnectionManager for multi-client support
- Integrated MetricsAggregator for 5-second broadcasts
- Merged dev to main branch and pushed

**Next**:
- Complete T011 (write tests, update docs)
- T012: Dashboard UI with real-time charts
