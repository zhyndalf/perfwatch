# Architecture Diagrams

> **High-level architecture views for system architects**

This directory contains C4 architecture diagrams and technology stack visualizations for PerfWatch.

---

## 📊 Diagrams

### C4 Architecture Model

The C4 model provides a hierarchical view of PerfWatch's architecture:

1. **[System Context](./c4-system-context.md)** - Level 1
   - External users and systems
   - PerfWatch as a black box
   - System boundaries

2. **[Container Diagram](./c4-container.md)** - Level 2
   - Major application containers (frontend, backend, database)
   - Communication protocols
   - Technology choices

3. **[Component Diagram](./c4-component.md)** - Level 3
   - Internal components within each container
   - Responsibilities and dependencies
   - Data flow patterns

### Technology

4. **[Technology Stack](./tech-stack.md)**
   - Layer-by-layer technology choices
   - Frontend, backend, database, infrastructure
   - Rationale for key decisions

---

## 🎯 Key Architectural Decisions

**Real-time First:**
- WebSocket streaming for 5-second metrics
- HTTP endpoints for historical queries only

**Simplicity First:**
- Single-page dashboard (no customization)
- Fixed 5s sampling interval
- Linux-only (perf_events dependency)

**Docker First:**
- All services containerized
- PostgreSQL in Docker (no SQLite)
- Privileged mode for hardware counters

**Graceful Degradation:**
- Collectors return None for unavailable metrics
- Frontend shows "N/A" for missing data
- No crashes on missing perf_events

---

## 📚 Related Documentation

- [Architecture Specification](../../sdd/02-specification/architecture.md) - Text-based architecture
- [Design Principles](../../sdd/01-constitution/principles.md) - Guiding principles
- [Technology Decisions](../../sdd/05-implementation/decisions.md) - Implementation choices
- [Developer Diagrams](../developers/) - Implementation-level diagrams

---

**Navigation:** [← Back to Diagrams Index](../README.md)
