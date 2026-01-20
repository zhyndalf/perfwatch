# T020: Data Retention

> **Phase**: 4 - History & Polish
> **Status**: ✅ Completed
> **Priority**: Medium
> **Estimated Effort**: 2-3 hours
> **Dependencies**: T018 (History Storage)

---

## Overview

Add retention policy settings, cleanup execution, and UI controls for managing
historical data retention and downsampling.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Provide retention policy API (get/update) | Must |
| FR-2 | Support manual cleanup trigger | Must |
| FR-3 | Periodic cleanup runs in backend | Must |
| FR-4 | UI for retention policy settings | Must |

### Non-Functional Requirements

| ID | Requirement |
|----|-------------|
| NFR-1 | Auth-protected endpoints |
| NFR-2 | Validation for invalid values |

---

## Implementation Notes

- Retention policy endpoints live under `/api/retention`.
- Cleanup runs periodically in the FastAPI lifespan.
- UI controls added to Settings view.

---

## Acceptance Criteria

- [x] API supports get/update for retention policy.
- [x] Manual cleanup endpoint executes and returns counts.
- [x] Periodic cleanup runs in background.
- [x] Settings UI exposes retention controls.

---

## Files Updated

| File | Description |
|------|-------------|
| `backend/app/api/retention.py` | Retention policy endpoints |
| `backend/app/services/retention.py` | Cleanup service |
| `backend/app/main.py` | Background cleanup loop |
| `backend/app/config.py` | Cleanup settings |
| `frontend/src/views/Settings.vue` | Retention UI |
| `frontend/src/stores/retention.js` | Retention store |

