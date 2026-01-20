# T021: Settings Page

> **Phase**: 4 - History & Polish
> **Status**: ✅ Completed
> **Priority**: Medium
> **Estimated Effort**: 2-3 hours
> **Dependencies**: T020 (Data Retention)

---

## Overview

Add system configuration visibility on the Settings page, backed by a config API.

---

## Requirements

### Functional Requirements

| ID | Requirement | Priority |
|----|-------------|----------|
| FR-1 | Provide `/api/config` endpoint | Must |
| FR-2 | Show system info in Settings UI | Must |
| FR-3 | Support config read/update operations | Should |

---

## Acceptance Criteria

- [x] Config API returns sampling interval, perf events flag, retention fields.
- [x] Settings page displays system info.
- [x] Config tests cover GET + update.

---

## Files Updated

| File | Description |
|------|-------------|
| `backend/app/api/config.py` | Config endpoints |
| `backend/app/services/config.py` | Config storage service |
| `backend/app/schemas/config.py` | Config schemas |
| `frontend/src/views/Settings.vue` | System info panel |
| `frontend/src/stores/config.js` | Config store |
| `backend/tests/test_config.py` | Config API tests |

