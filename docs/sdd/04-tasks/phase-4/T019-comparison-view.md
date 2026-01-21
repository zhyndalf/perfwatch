# T019: Comparison View

> **Phase**: 4 - History & Polish
> **Status**: ✅ Completed
> **Priority**: Medium
> **Estimated Effort**: 2-3 hours
> **Dependencies**: T018 (History Storage)

---

## Overview

Add time period comparison for historical metrics. Provide an API to compare two time periods using either relative comparison (period + compare_to) or custom range comparison (explicit timestamps), and visualize the overlay in the History view with summary statistics.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Provide `/api/history/compare` endpoint with dual modes | Must |
| FR-2 | Support relative comparison: periods (hour, day, week) and compare_to (yesterday, last_week) | Must |
| FR-3 | Support custom range comparison: 4 explicit timestamps (start_time_1, end_time_1, start_time_2, end_time_2) | Must |
| FR-4 | Return both time series data_points and summary stats | Must |
| FR-5 | Frontend overlay chart shows both series | Must |
| FR-6 | Validate custom ranges have same duration | Must |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Reuse existing aggregation/downsampling logic |
| NFR-2 | Handle missing data gracefully |
| NFR-3 | Maintain auth protection |

---

## API Contract

`GET /api/history/compare`

**Mode 1: Relative Comparison**
Query params:
- `metric_type` (cpu, memory, network, disk, perf_events, memory_bandwidth)
- `period` (hour, day, week)
- `compare_to` (yesterday, last_week)
- `limit` (optional: default 1000, max 10000)
- `interval` (optional: 5s, 1m, 5m, 1h, auto - default: auto)

**Mode 2: Custom Range Comparison**
Query params:
- `metric_type` (cpu, memory, network, disk, perf_events, memory_bandwidth)
- `start_time_1` (ISO datetime - Period 1 start)
- `end_time_1` (ISO datetime - Period 1 end)
- `start_time_2` (ISO datetime - Period 2 start)
- `end_time_2` (ISO datetime - Period 2 end)
- `limit` (optional: default 1000, max 10000)
- `interval` (optional: 5s, 1m, 5m, 1h, auto - default: auto)

Response:
```json
{
  "metric_type": "cpu",
  "period": "hour",
  "compare_to": "yesterday",
  "interval": "1m",
  "current": {
    "start_time": "2026-01-21T14:00:00Z",
    "end_time": "2026-01-21T15:00:00Z",
    "data_points": [
      {
        "timestamp": "2026-01-21T14:00:00Z",
        "data": {
          "usage_percent": 52.3,
          "user": 35.2,
          "system": 17.1
        }
      }
    ]
  },
  "comparison": {
    "start_time": "2026-01-20T14:00:00Z",
    "end_time": "2026-01-20T15:00:00Z",
    "data_points": [
      {
        "timestamp": "2026-01-20T14:00:00Z",
        "data": {
          "usage_percent": 45.8,
          "user": 30.1,
          "system": 15.7
        }
      }
    ]
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

1. Add comparison query functions in metrics service (`compare_metrics_history` and `compare_metrics_custom_range`).
2. Implement `/api/history/compare` endpoint with dual mode support and validation.
3. Add backend tests for both comparison modes and edge cases.
4. Update History view to overlay chart and show summary for both modes.

---

## Acceptance Criteria

- [x] `/api/history/compare` supports both relative and custom range comparisons.
- [x] Relative mode: period + compare_to parameters work correctly.
- [x] Custom mode: 4 timestamp parameters validated for same duration.
- [x] Returns current and comparison series with full data_points arrays.
- [x] Summary stats (current_avg, comparison_avg, change_percent) are accurate.
- [x] UI overlay displays both series and comparison summary.
- [x] Invalid params return 400 with clear messages.
- [x] Tests cover both comparison modes, logic, and endpoint.

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
