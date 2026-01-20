# PerfWatch Changelog

> Track significant changes to the project

---

## Format

```
## [Date] - Task ID - Brief Description

### Added
- New features

### Changed
- Modifications to existing features

### Fixed
- Bug fixes

### Removed
- Removed features
```

---

## [2025-01-18] - T001 - SDD & Project Scaffold

### Added
- Complete SDD documentation structure
- Constitution documents (vision, principles, glossary)
- Technical specifications (architecture, API, data model, metrics, UI)
- Phase planning documents (roadmap, phase 1-4)
- Phase 1 task files (T001-T005)
- Implementation tracking files (decisions, changelog, learnings)
- Project directory structure (backend, frontend, scripts)

### Notes
- Initial project setup
- Foundation for all future development

---

## [2026-01-20] - T018 - History Storage

### Added
- Batch metrics persistence for WebSocket snapshots
- History query API with interval-based downsampling
- T018 task file and Phase 4 tracking

### Changed
- WebSocket aggregation interval now uses configured sampling setting

### Fixed
- History persistence tests now use injected sessions to avoid loop conflicts

---

## [2026-01-20] - T019 - Comparison View

### Added
- `/api/history/compare` endpoint for same-period comparisons
- Comparison UI controls and overlay series in History view
- Summary statistics for current vs comparison periods

### Changed
- Comparison series aligned to current-period timestamps for overlays

---

## [2026-01-20] - T020 - Data Retention

### Added
- Retention policy API with update + manual cleanup
- Settings UI controls for retention and scheduled cleanup
- Periodic cleanup task in FastAPI lifespan

### Changed
- Retention cleanup now counts deletions before delete for reliable reporting

---

## [2026-01-20] - T021 - Settings Page

### Added
- `/api/config` endpoints and config service layer
- Settings UI system info panel (perf events, sampling interval, version)
- Config store and tests for config endpoints

---

## [2026-01-20] - T022 - Polish & Testing

### Changed
- Fixed websocket batch writer loop handling for tests
- Adjusted dashboard/history chart layout and Settings UX
- Updated settings/config UI interactions and data load

### Tests
- Full backend test suite passed (238 tests)

---

## Upcoming

*Future changes will be logged here as tasks are completed*

### After T002 (Docker Setup)
- Docker Compose configuration
- Dockerfiles for backend and frontend
- Environment variable setup

### After T003 (Database Setup)
- SQLAlchemy models
- Alembic migrations
- Database initialization

### After T004 (Auth Backend)
- JWT authentication
- Login/logout endpoints
- Auth middleware

### After T005 (Vue Frontend Base)
- Vue.js 3 project setup
- Router and state management
- Login page implementation
