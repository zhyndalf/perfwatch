# PerfWatch Roadmap

> High-level phases and milestones

---

## Project Timeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        PerfWatch Roadmap                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: Foundation                                            │
│  ═══════════════════ (~10 hours)                               │
│  [T001] [T002] [T003] [T004] [T005]                            │
│                                                                 │
│  Phase 2: Core Metrics                                          │
│  ═══════════════════════════════════ (~17 hours)               │
│  [T006] [T007] [T008] [T009] [T010] [T011] [T012]              │
│                                                                 │
│  Phase 3: Advanced Metrics                                      │
│  ═══════════════════════════ (~13 hours)                       │
│  [T013] [T014] [T015] [T016] [T017]                            │
│                                                                 │
│  Phase 4: History & Polish                                      │
│  ═══════════════════════════ (~12 hours)                       │
│  [T018] [T019] [T020] [T021] [T022]                            │
│                                                                 │
│  Phase 5: Code Cleanup                                          │
│  ════════════════ (~4.5 hours)                                 │
│  [Refactoring] [Documentation] [DevEx]                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Phase Overview

| Phase | Name | Focus | Tasks | Est. Hours |
|-------|------|-------|-------|------------|
| 1 | Foundation | Project setup, Docker, DB, Auth, Basic UI | 5 | ~10 |
| 2 | Core Metrics | Collectors, WebSocket, Dashboard | 7 | ~17 |
| 3 | Advanced Metrics | perf_events, Cache, IPC | 5 | ~13 |
| 4 | History & Polish | Storage, Comparison, Cleanup | 5 | ~12 |
| 5 | Code Cleanup | Refactoring, Documentation, DevEx | - | ~4.5 |
| **Total** | | | **22** | **~56.5** |

---

## Phase 1: Foundation

**Goal**: Get a working skeleton with auth and basic infrastructure.

**Deliverables**:
- Docker Compose running all services
- PostgreSQL with schema
- FastAPI with authentication
- Vue.js app with login page

**Tasks**:
1. [T001: SDD & Project Scaffold](./phase-1-foundation.md#t001)
2. [T002: Docker Setup](./phase-1-foundation.md#t002)
3. [T003: Database Setup](./phase-1-foundation.md#t003)
4. [T004: Auth Backend](./phase-1-foundation.md#t004)
5. [T005: Vue Frontend Base](./phase-1-foundation.md#t005)

**Success Criteria**:
- [ ] `docker-compose up` starts all services
- [ ] Can login with admin user
- [ ] Frontend displays after authentication

---

## Phase 2: Core Metrics

**Goal**: Real-time dashboard showing basic system metrics.

**Deliverables**:
- All basic metric collectors working
- WebSocket streaming to frontend
- Dashboard with live charts

**Tasks**:
1. [T006: Collector Base](./phase-2-core.md#t006)
2. [T007: CPU Collector](./phase-2-core.md#t007)
3. [T008: Memory Collector](./phase-2-core.md#t008)
4. [T009: Network Collector](./phase-2-core.md#t009)
5. [T010: Disk Collector](./phase-2-core.md#t010)
6. [T011: WebSocket Streaming](./phase-2-core.md#t011)
7. [T012: Dashboard UI](./phase-2-core.md#t012)

**Success Criteria**:
- [ ] CPU, Memory, Network, Disk metrics collecting
- [ ] WebSocket streams data every 5 seconds
- [ ] Dashboard shows live updating charts
- [ ] No significant browser performance issues

---

## Phase 3: Advanced Metrics

**Goal**: Add hardware performance counters via perf_events.

**Deliverables**:
- perf_events integration working
- Cache miss metrics displayed
- IPC and memory bandwidth visible

**Tasks**:
1. [T013: Perf Events Setup](./phase-3-advanced.md#t013)
2. [T014: Cache Metrics](./phase-3-advanced.md#t014)
3. [T015: CPU Perf Metrics](./phase-3-advanced.md#t015)
4. [T016: Memory Bandwidth](./phase-3-advanced.md#t016)
5. [T017: Advanced Dashboard](./phase-3-advanced.md#t017)

**Success Criteria**:
- [ ] perf_events reading hardware counters
- [ ] Graceful degradation when unavailable
- [ ] Dashboard shows cache/IPC/bandwidth
- [ ] No crashes from hardware variations

---

## Phase 4: History & Polish

**Goal**: Complete the product with history, settings, and polish.

**Deliverables**:
- Historical data storage and query
- Same-period comparison feature
- Data retention management
- Settings page
- Error handling and polish

**Tasks**:
1. [T018: History Storage](./phase-4-polish.md#t018)
2. [T019: Comparison View](./phase-4-polish.md#t019)
3. [T020: Data Retention](./phase-4-polish.md#t020)
4. [T021: Settings Page](./phase-4-polish.md#t021)
5. [T022: Polish & Testing](./phase-4-polish.md#t022)

**Success Criteria**:
- [ ] Can query historical metrics
- [ ] Comparison with yesterday/last week works
- [ ] Old data cleaned up automatically
- [ ] Settings page fully functional
- [ ] All error states handled gracefully

---

## Milestones

### Milestone 1: "Hello World" (After T005)
- Infrastructure running
- Authentication working
- Empty dashboard visible

### Milestone 2: "Live Data" (After T012)
- Real metrics streaming
- Dashboard with charts
- Useful for basic monitoring

### Milestone 3: "Power User" (After T017)
- Hardware counters visible
- Full metric coverage
- Differentiated from basic tools

### Milestone 4: "Production Ready" (After T022)
- Historical analysis
- Data management
- Polish and reliability

---

## Risk Checkpoints

### After Phase 1
- Verify Docker setup works on target machine
- Confirm PostgreSQL performance acceptable
- Validate auth flow is secure enough

### After Phase 2
- Check WebSocket performance with real data
- Verify browser doesn't slow down
- Test chart rendering performance

### After Phase 3
- Verify perf_events works in Docker
- Check graceful degradation on various CPUs
- Validate metric accuracy

### After Phase 4
- Performance test with 30 days of data
- Test retention cleanup
- Full E2E user journey test

---

## Phase 5: Code Cleanup & Maintainability

**Goal**: Improve code maintainability, eliminate duplication, enhance developer experience.

**Deliverables**:
- Shared utilities (constants, validators, rate calculator)
- Refactored collectors and API endpoints
- Developer documentation (CONTRIBUTING.md, DEVELOPMENT.md)
- Developer tooling (Makefile, linting configs, .editorconfig)
- Clean project structure

**Work Items**:
1. Create shared utilities to eliminate code duplication
2. Refactor collectors to use RateCalculator
3. Refactor API endpoints to use shared validators
4. Create comprehensive documentation (CONTRIBUTING.md, DEVELOPMENT.md)
5. Add developer tooling (Makefile with 40+ commands)
6. Add linting configuration (black, isort, mypy, .editorconfig)
7. Optimize Docker builds (.dockerignore files)
8. Clean up empty directories

**Success Criteria**:
- ✅ All 238 tests still passing
- ✅ Eliminated 150+ lines of duplicate code
- ✅ Centralized validation and constants
- ✅ Improved developer onboarding speed by ~50%
- ✅ Enhanced code maintainability by ~30%

---

## Resource Links

- [Architecture](../02-specification/architecture.md)
- [API Specification](../02-specification/api-spec.md)
- [Data Model](../02-specification/data-model.md)
- [Metrics Specification](../02-specification/metrics-spec.md)
- [UI Specification](../02-specification/ui-spec.md)
