# T019: Comparison View

> **Phase**: 4 - History & Polish
> **Status**: ✅ Completed
> **Priority**: Medium
> **Estimated Effort**: 2-3 hours
> **Dependencies**: T018 (History Storage)

---

## Overview

Add same-period comparison for historical metrics. Provide an API to compare the current period against a prior period (yesterday/last week), and visualize the overlay in the History view with summary statistics.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Provide `/api/history/compare` endpoint | Must |
| FR-2 | Support periods: hour, day, week | Must |
| FR-3 | Support comparisons: yesterday, last_week | Must |
| FR-4 | Return both time series and summary stats | Must |
| FR-5 | Frontend overlay chart shows both series | Must |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Reuse existing aggregation/downsampling logic |
| NFR-2 | Handle missing data gracefully |
| NFR-3 | Maintain auth protection |

---

## API Contract

`GET /api/history/compare`

Query params:
- `metric_type` (cpu, memory, network, disk, perf_events, memory_bandwidth)
- `period` (hour, day, week)
- `compare_to` (yesterday, last_week)
- `interval` (optional: 5s, 1m, 5m, 1h, auto)

Response:
```json
{
  "metric_type": "cpu",
  "period": "hour",
  "compare_to": "yesterday",
  "current": {
    "start_time": "...",
    "end_time": "...",
    "data_points": [...]
  },
  "comparison": {
    "start_time": "...",
    "end_time": "...",
    "data_points": [...]
  },
  "summary": {
    "current_avg": 52.3,
    "comparison_avg": 45.8,
    "change_percent": 14.2
  }
}
```

---

## Implementation Plan

1. Add comparison query function in metrics service.
2. Implement `/api/history/compare` endpoint with validation.
3. Add backend tests for compare logic and endpoint.
4. Update History view to overlay chart and show summary.

---

## Acceptance Criteria

- [x] `/api/history/compare` returns current and comparison series.
- [x] Summary stats (avg + change %) are accurate.
- [x] UI overlay displays both series and comparison summary.
- [x] Invalid params return 400 with clear messages.
- [x] Tests cover comparison logic and endpoint.

---

## Files to Modify

| File | Action | Description |
|------|--------|-------------|
| `backend/app/services/metrics_storage.py` | Modify | Comparison query helper |
| `backend/app/api/history.py` | Modify | Add compare endpoint |
| `backend/tests/test_history.py` | Modify | Add comparison tests |
| `frontend/src/views/History.vue` | Modify | Comparison UI and chart overlay |
| `frontend/src/stores/history.js` | Modify | Comparison state |

---

## References

- [API Spec - History](../../02-specification/api-spec.md#historical-data)
- [UI Spec - History Page](../../02-specification/ui-spec.md#history-page-history)
