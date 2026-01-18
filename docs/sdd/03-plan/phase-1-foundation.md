# Phase 1: Foundation

> Project setup, Docker, Database, Authentication, Basic UI

---

## Overview

| Aspect | Details |
|--------|---------|
| Duration | ~10 hours (5 sessions) |
| Tasks | T001-T005 |
| Goal | Working skeleton with auth |

---

## Task Summary

| Task | Name | Est. Time | Status |
|------|------|-----------|--------|
| T001 | SDD & Project Scaffold | 1-2 hrs | ⏳ In Progress |
| T002 | Docker Setup | 1-2 hrs | ⬜ Not Started |
| T003 | Database Setup | 2-3 hrs | ⬜ Not Started |
| T004 | Auth Backend | 2-3 hrs | ⬜ Not Started |
| T005 | Vue Frontend Base | 2-3 hrs | ⬜ Not Started |

---

## T001: SDD & Project Scaffold {#t001}

**Objective**: Create the SDD documentation structure and project directories.

**Task File**: [T001-project-scaffold.md](../04-tasks/phase-1/T001-project-scaffold.md)

**Deliverables**:
- Complete SDD directory structure
- All constitution documents
- All specification documents
- Phase plan files
- Task files for Phase 1
- Empty project directories

**Acceptance Criteria**:
- [ ] SDD structure created
- [ ] Constitution files populated
- [ ] Specification files populated
- [ ] All Phase 1 task files exist
- [ ] Project directory structure ready

---

## T002: Docker Setup {#t002}

**Objective**: Create Docker Compose configuration for all services.

**Task File**: [T002-docker-setup.md](../04-tasks/phase-1/T002-docker-setup.md)

**Deliverables**:
- `docker-compose.yml`
- Backend Dockerfile
- Frontend Dockerfile
- `.env.example`
- Basic `README.md`

**Acceptance Criteria**:
- [ ] `docker-compose up` starts without errors
- [ ] All three services (backend, frontend, db) running
- [ ] Services can communicate
- [ ] Environment variables working

---

## T003: Database Setup {#t003}

**Objective**: Configure PostgreSQL with SQLAlchemy and Alembic migrations.

**Task File**: [T003-database-setup.md](../04-tasks/phase-1/T003-database-setup.md)

**Deliverables**:
- SQLAlchemy models (User, MetricsSnapshot, Config)
- Alembic configuration
- Initial migration
- Database connection module
- Init script for default data

**Acceptance Criteria**:
- [ ] PostgreSQL container runs
- [ ] Models defined correctly
- [ ] Migrations run successfully
- [ ] Can connect from FastAPI

---

## T004: Auth Backend {#t004}

**Objective**: Implement JWT authentication with FastAPI.

**Task File**: [T004-auth-backend.md](../04-tasks/phase-1/T004-auth-backend.md)

**Deliverables**:
- Auth service with password hashing
- Login/logout endpoints
- JWT token generation/validation
- Auth middleware
- Protected route decorator

**Acceptance Criteria**:
- [ ] Login endpoint returns JWT
- [ ] Protected endpoints require valid token
- [ ] Password properly hashed
- [ ] Token expiration working

---

## T005: Vue Frontend Base {#t005}

**Objective**: Set up Vue.js 3 application with routing and login page.

**Task File**: [T005-vue-frontend-base.md](../04-tasks/phase-1/T005-vue-frontend-base.md)

**Deliverables**:
- Vite + Vue 3 setup
- Vue Router configuration
- Pinia store setup
- TailwindCSS integration
- Login page component
- Auth composable
- Basic layout components

**Acceptance Criteria**:
- [ ] `npm run dev` starts development server
- [ ] Login page renders
- [ ] Can authenticate with backend
- [ ] Protected routes redirect to login
- [ ] Token stored and used for requests

---

## Dependency Graph

```
T001 (SDD & Scaffold)
  │
  └──► T002 (Docker Setup)
         │
         ├──► T003 (Database Setup)
         │      │
         │      └──► T004 (Auth Backend)
         │
         └──► T005 (Vue Frontend Base)
```

---

## End State

After Phase 1 is complete:

1. **Infrastructure**: Docker Compose with all services
2. **Database**: PostgreSQL with schema, migrations, default user
3. **Backend**: FastAPI with working authentication
4. **Frontend**: Vue app with login functionality
5. **Documentation**: Complete SDD structure

### Verification Commands

```bash
# Start all services
docker-compose up -d

# Check services
docker-compose ps

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Access frontend
open http://localhost:3000
```
