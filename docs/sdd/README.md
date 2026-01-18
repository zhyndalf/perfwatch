# PerfWatch - SDD Documentation

> **Specification Driven Development** - The source of truth for the PerfWatch project

## Quick Start

### Resume Work
1. Read [CURRENT_TASK.md](./CURRENT_TASK.md) - Always start here
2. Read the linked task file
3. Continue from "What's Next"

### Check Progress
- [PROGRESS.md](./PROGRESS.md) - Visual progress dashboard

## SDD Structure

```
sdd/
├── README.md                 # You are here
├── CURRENT_TASK.md           # Resume point - what's being worked on
├── PROGRESS.md               # Progress dashboard
│
├── 01-constitution/          # Why & What (Project Identity)
│   ├── vision.md             # Project vision & goals
│   ├── principles.md         # Design principles & constraints
│   └── glossary.md           # Domain terminology
│
├── 02-specification/         # How (Technical Details)
│   ├── architecture.md       # System architecture
│   ├── api-spec.md           # API endpoint specifications
│   ├── data-model.md         # Database schema & models
│   ├── metrics-spec.md       # Detailed metrics specification
│   └── ui-spec.md            # UI/UX specifications
│
├── 03-plan/                  # When (Timeline)
│   ├── roadmap.md            # High-level phases & milestones
│   ├── phase-1-foundation.md # Phase 1 detailed plan
│   ├── phase-2-core.md       # Phase 2 detailed plan
│   ├── phase-3-advanced.md   # Phase 3 detailed plan
│   └── phase-4-polish.md     # Phase 4 detailed plan
│
├── 04-tasks/                 # Do (Atomic Work Units)
│   ├── backlog.md            # Future tasks not yet planned
│   ├── phase-1/              # Phase 1 tasks (T001-T005)
│   ├── phase-2/              # Phase 2 tasks (T006-T012)
│   ├── phase-3/              # Phase 3 tasks (T013-T017)
│   └── phase-4/              # Phase 4 tasks (T018-T022)
│
└── 05-implementation/        # Done (Records)
    ├── decisions.md          # Architecture Decision Records
    ├── changelog.md          # What changed and when
    └── learnings.md          # Lessons learned
```

## How This Works

### Task-Based Development
Each task (T001, T002, etc.) is designed to be:
- **Atomic**: Completable in one conversation session (2-4 hours)
- **Self-contained**: Has all context needed in its task file
- **Testable**: Clear acceptance criteria
- **Documented**: Records decisions made during implementation

### Session Flow
1. **Start**: Read `CURRENT_TASK.md`
2. **Work**: Follow the task file instructions
3. **End**: Update `CURRENT_TASK.md` and `PROGRESS.md`
4. **Commit**: Preserve state in git

### State Preservation
All project state lives in these markdown files:
- No external tracking tools needed
- Can pause and resume anytime
- Full context is always available
- Works across different AI conversations

## Project Overview

**PerfWatch** is a real-time system performance monitoring web application.

| Aspect | Choice |
|--------|--------|
| Target | Local machine only |
| Frontend | Vue.js 3 + ECharts |
| Backend | FastAPI + WebSocket |
| Database | PostgreSQL |
| Deployment | Docker Compose |
| Sampling | Every 5 seconds |

See [01-constitution/vision.md](./01-constitution/vision.md) for full details.
