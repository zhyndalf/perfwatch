# Phase 2: Core Metrics

> Collectors, WebSocket streaming, and Dashboard UI

---

## Overview

| Aspect | Details |
|--------|---------|
| Duration | ~17 hours (7 sessions) |
| Tasks | T006-T012 |
| Goal | Live dashboard with basic metrics |
| Prerequisites | Phase 1 complete |

---

## Task Summary

| Task | Name | Est. Time | Status |
|------|------|-----------|--------|
| T006 | Collector Base | 2-3 hrs | ⬜ Not Started |
| T007 | CPU Collector | 2-3 hrs | ⬜ Not Started |
| T008 | Memory Collector | 2 hrs | ⬜ Not Started |
| T009 | Network Collector | 2-3 hrs | ⬜ Not Started |
| T010 | Disk Collector | 2-3 hrs | ⬜ Not Started |
| T011 | WebSocket Streaming | 2-3 hrs | ⬜ Not Started |
| T012 | Dashboard UI | 3-4 hrs | ⬜ Not Started |

---

## T006: Collector Base {#t006}

**Objective**: Create the base collector architecture and aggregator.

**Task File**: [T006-collector-base.md](../04-tasks/phase-2/T006-collector-base.md)

**Deliverables**:
- `BaseCollector` abstract class
- `Aggregator` class with scheduling
- Collector registration mechanism
- Async collection loop
- Error handling for individual collectors

**Acceptance Criteria**:
- [ ] Base class defines collect interface
- [ ] Aggregator runs collection loop
- [ ] Failed collector doesn't stop others
- [ ] Metrics combined into snapshot

---

## T007: CPU Collector {#t007}

**Objective**: Implement CPU metrics collection using psutil.

**Task File**: [T007-cpu-collector.md](../04-tasks/phase-2/T007-cpu-collector.md)

**Deliverables**:
- CPU collector implementation
- Overall and per-core usage
- Time breakdown (user/system/idle/iowait)
- Frequency readings
- Temperature readings (if available)

**Acceptance Criteria**:
- [ ] Collects all specified CPU metrics
- [ ] Per-core data accurate
- [ ] Handles missing temperature gracefully
- [ ] Returns valid JSON structure

---

## T008: Memory Collector {#t008}

**Objective**: Implement memory metrics collection.

**Task File**: [T008-memory-collector.md](../04-tasks/phase-2/T008-memory-collector.md)

**Deliverables**:
- Memory collector implementation
- Usage breakdown (used/free/cached/buffers)
- Swap statistics
- Hugepages info (if available)

**Acceptance Criteria**:
- [ ] All memory fields collected
- [ ] Swap data accurate
- [ ] Handles systems without hugepages
- [ ] Returns valid JSON structure

---

## T009: Network Collector {#t009}

**Objective**: Implement network metrics collection.

**Task File**: [T009-network-collector.md](../04-tasks/phase-2/T009-network-collector.md)

**Deliverables**:
- Network collector implementation
- Per-interface bandwidth (bytes/sec)
- Packet rates
- Connection state counts
- Rate calculation from counters

**Acceptance Criteria**:
- [ ] Per-interface metrics working
- [ ] Rates calculated correctly
- [ ] Connection states counted
- [ ] Handles interface changes

---

## T010: Disk Collector {#t010}

**Objective**: Implement disk I/O and usage metrics collection.

**Task File**: [T010-disk-collector.md](../04-tasks/phase-2/T010-disk-collector.md)

**Deliverables**:
- Disk collector implementation
- Per-device I/O rates
- IOPS calculation
- Latency estimation
- Partition usage

**Acceptance Criteria**:
- [ ] Per-device throughput correct
- [ ] IOPS calculated accurately
- [ ] Latency estimation reasonable
- [ ] Partition usage reported

---

## T011: WebSocket Streaming {#t011}

**Objective**: Stream metrics to frontend via WebSocket.

**Task File**: [T011-websocket-streaming.md](../04-tasks/phase-2/T011-websocket-streaming.md)

**Deliverables**:
- WebSocket endpoint in FastAPI
- Client connection management
- Authentication for WebSocket
- Message broadcasting
- Reconnection handling

**Acceptance Criteria**:
- [ ] WebSocket endpoint accepts connections
- [ ] Auth token validated
- [ ] Metrics broadcast every 5 seconds
- [ ] Handles client disconnect gracefully

---

## T012: Dashboard UI {#t012}

**Objective**: Create the main dashboard with ECharts visualizations.

**Task File**: [T012-dashboard-ui.md](../04-tasks/phase-2/T012-dashboard-ui.md)

**Deliverables**:
- Dashboard page component
- WebSocket composable
- MetricCard component
- CPU chart component
- Memory chart component
- Network chart component
- Disk chart component
- Connection status display

**Acceptance Criteria**:
- [ ] Dashboard displays all metric cards
- [ ] Charts update in real-time
- [ ] Connection status visible
- [ ] No performance issues
- [ ] Responsive layout works

---

## Dependency Graph

```
T006 (Collector Base)
  │
  ├──► T007 (CPU Collector)
  │
  ├──► T008 (Memory Collector)
  │
  ├──► T009 (Network Collector)
  │
  └──► T010 (Disk Collector)
         │
         └──► T011 (WebSocket Streaming)
                │
                └──► T012 (Dashboard UI)
```

Note: T007-T010 can be done in any order after T006.

---

## End State

After Phase 2 is complete:

1. **Collectors**: CPU, Memory, Network, Disk all collecting
2. **Aggregator**: Combining metrics every 5 seconds
3. **WebSocket**: Streaming to connected clients
4. **Dashboard**: Live updating charts for all basic metrics

### Verification Steps

```bash
# Check backend logs for collection
docker-compose logs -f backend

# Connect to WebSocket (using websocat)
websocat "ws://localhost:8000/api/ws/metrics?token=<jwt>"

# Open dashboard
open http://localhost:3000

# Verify charts update every 5 seconds
# Check browser console for WebSocket messages
```

### Performance Targets

| Metric | Target |
|--------|--------|
| Collection time | < 500ms per cycle |
| WebSocket latency | < 100ms |
| Browser CPU usage | < 10% |
| Chart frame rate | 60fps smooth |
