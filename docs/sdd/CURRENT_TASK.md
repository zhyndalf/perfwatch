# Current Task

> **Status**: READY_FOR_IMPLEMENTATION
> **Task ID**: T006
> **Task File**: [T006-collector-base.md](./04-tasks/phase-2/T006-collector-base.md)

---

## Quick Context

Create the base collector infrastructure using psutil for system metrics, with an aggregator that coordinates multiple collectors.

---

## What's Done (Previous Task T005)

- [x] Added pinia, tailwindcss, postcss, autoprefixer to package.json
- [x] Created tailwind.config.js with dark theme colors
- [x] Created postcss.config.js
- [x] Added @ alias in vite.config.js
- [x] Created axios client with JWT interceptors (src/api/index.js)
- [x] Created Pinia auth store (src/stores/auth.js)
- [x] Created Vue Router with navigation guards (src/router/index.js)
- [x] Created Login.vue with form validation
- [x] Created Dashboard.vue, History.vue, Settings.vue placeholders
- [x] Created Layout.vue and Header.vue components
- [x] Created main.css with Tailwind styles
- [x] Fixed login API (changed from form-urlencoded to JSON body)
- [x] All auth flow verified working

**Phase 1 COMPLETE!** Foundation is ready.

---

## What's Next (T006)

1. Create `backend/app/collectors/` package
2. Implement `BaseCollector` abstract class
3. Implement `MetricsAggregator` class
4. Create Pydantic schemas for metrics
5. Write unit tests for collector infrastructure

---

## Resume Instructions

**To continue PerfWatch development:**
1. Say "Let's continue perfwatch" or similar
2. I'll read this file and the T006 task file
3. We'll implement the collector base infrastructure

**Project Location**: `/home/zhyndalf/vibeCoding/perfwatch`
**GitHub**: https://github.com/zhyndalf/perfwatch

---

## Blockers

None currently.

---

## Session Notes

**Session 1** (2025-01-18):
- T001 COMPLETED: Full SDD structure created with 25+ documentation files
- Git initialized and pushed to GitHub
- All Phase 1 task files have detailed implementation guidance
- Project directory structure ready for code

**Session 2** (2025-01-19):
- T002 COMPLETED: Docker setup complete
- Installed Docker Engine and Docker Compose on Ubuntu 24.04
- Created docker-compose.yml with PostgreSQL, FastAPI, Vue.js services
- Created Dockerfiles for backend and frontend
- Created basic Vue.js landing page with backend status check
- Created project README.md
- Verified all services: `docker compose up` works, all endpoints responding

**Session 3** (2025-01-19):
- T003 COMPLETED: Database setup complete
- Created SQLAlchemy 2.0 async models with modern type hints
- Configured Alembic for async migrations
- Created 26 tests following TDD principles
- Fixed bcrypt compatibility issue (used bcrypt directly instead of passlib)
- All tests passing, migrations verified, default data initialized

**Session 4** (2026-01-19):
- T004 COMPLETED: Auth backend complete
- Created auth service with bcrypt and JWT (python-jose)
- Implemented login, me, password endpoints
- Created FastAPI dependencies with type aliases (CurrentUser, DbSession)
- Added 25 new tests (51 total)
- All endpoints verified working with curl

**Session 5** (2026-01-19):
- T005 COMPLETED: Vue Frontend Base complete
- Set up Vue Router, Pinia, TailwindCSS
- Created Login, Dashboard, History, Settings views
- Created Layout and Header components
- Implemented auth flow with JWT token storage
- Fixed login API (JSON body, not form-urlencoded)
- **Phase 1 Foundation Complete!**

**Next Session Focus**:
- T006: Collector Base
- BaseCollector abstract class
- MetricsAggregator coordinator
- Pydantic metric schemas
