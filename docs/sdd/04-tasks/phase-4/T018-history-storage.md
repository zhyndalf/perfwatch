# T018: History Storage

> **Phase**: 4 - History & Polish
> **Status**: ✅ Completed
> **Priority**: High
> **Estimated Effort**: 2-3 hours
> **Dependencies**: T011 (WebSocket Streaming), T003 (Database Setup)
> **Completed**: 2026-01-20

---

## Overview

Persist metrics snapshots to PostgreSQL and expose a history query API with time-range filters and aggregation intervals. This enables the History page and comparison features in later tasks.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Persist metrics snapshots to `metrics_snapshot` during live collection | Must |
| FR-2 | Provide history query endpoint with `metric_type`, `start_time`, `end_time` | Must |
| FR-3 | Support aggregation intervals (5s, 1m, 5m, 1h, auto) | Must |
| FR-4 | Downsample/aggregate older data when interval > 5s | Must |
| FR-5 | Do not impact real-time WebSocket performance | Must |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Async database writes and queries |
| NFR-2 | Batch inserts for efficiency |
| NFR-3 | Graceful handling of missing data |
| NFR-4 | Use existing JSONB storage model |

---

## Technical Design

### Data Flow

```
Collectors -> Aggregator -> WebSocket broadcast
                          -> Async snapshot persistence (batch)
```

### History Query

Endpoint: `GET /api/history/metrics`

Query params:
- `metric_type` (cpu, memory, network, disk, perf)
- `start_time` (ISO datetime)
- `end_time` (ISO datetime)
- `interval` (optional: 5s, 1m, 5m, 1h, auto)

### Aggregation Strategy

- If `interval=auto`, choose based on time range:
  - <= 2 hours: 5s
  - <= 24 hours: 1m
  - <= 7 days: 5m
  - > 7 days: 1h
- When interval > 5s, group by time bucket and aggregate:
  - Numeric fields: average
  - Arrays: element-wise average (when lengths match)
  - Nested objects: recurse into numeric fields

---

## Implementation Plan

1. Add persistence hook in WebSocket/aggregator loop with async batch insert.
2. Implement history service function for time-range queries + aggregation.
3. Add FastAPI endpoint and schemas for history response.
4. Add backend tests for persistence + history API.

---

## Acceptance Criteria

- [x] Metrics snapshots are persisted every collection interval without blocking WebSocket.
- [x] `/api/history/metrics` returns data for a valid time range.
- [x] Aggregation interval works and data is downsampled for older ranges.
- [x] Invalid parameters return 400 with clear error.
- [x] Tests cover persistence and query logic.

---

## Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/api/websocket.py` | Modify | Persist snapshots while broadcasting |
| `backend/app/services/metrics.py` | Modify/Create | History query + aggregation |
| `backend/app/api/history.py` | Create | History endpoints |
| `backend/app/schemas/metrics.py` | Modify | History query/response schemas |
| `backend/tests/test_history.py` | Create | History endpoint tests |
| `backend/tests/test_metrics_persistence.py` | Create | Snapshot persistence tests |

---

## References

- [API Spec - History](../../02-specification/api-spec.md#historical-data)
- [Data Model - metrics_snapshot](../../02-specification/data-model.md#table-metrics_snapshot)
- [Architecture](../../02-specification/architecture.md)
