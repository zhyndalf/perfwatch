# PerfWatch Diagrams

> **Comprehensive visual documentation for PerfWatch, organized by audience**

This directory contains Mermaid diagrams that document PerfWatch's architecture, design, and flows. All diagrams are GitHub-native (no external tools required) and organized by target audience.

---

## 📐 Navigation by Audience

### [For Architects](./architects/)
**High-level architecture and technology decisions**

- [C4 System Context](./architects/c4-system-context.md) - External systems and users
- [C4 Container Diagram](./architects/c4-container.md) - Major application containers
- [C4 Component Diagram](./architects/c4-component.md) - Internal component structure
- [Technology Stack](./architects/tech-stack.md) - Technology choices and layers

### [For Developers](./developers/)
**Implementation details, code structure, and technical flows**

**Deployment:**
- [Docker Architecture](./developers/deployment.md) - Container orchestration

**Sequence Diagrams:**
- [Authentication Flow](./developers/sequences/authentication.md) - Login and JWT lifecycle
- [WebSocket Metrics](./developers/sequences/websocket.md) - Real-time streaming
- [Historical Queries](./developers/sequences/historical-query.md) - Time-range data retrieval
- [Retention Cleanup](./developers/sequences/retention.md) - Background cleanup tasks

**Data & Code Structure:**
- [Database Schema](./developers/database-schema.md) - ER diagram with relationships
- [Collector Classes](./developers/classes/collectors.md) - BaseCollector hierarchy
- [SQLAlchemy Models](./developers/classes/models.md) - Database models
- [Pinia Stores](./developers/classes/stores.md) - Frontend state management

### [For Product Managers](./product-managers/)
**User journeys, feature flows, and system behavior**

- [User Flows](./product-managers/user-flows.md) - End-to-end user journeys
- [WebSocket States](./product-managers/websocket-states.md) - Connection state machine
- [Feature Flows](./product-managers/feature-flows.md) - Key feature pipelines

---

## 🎨 Diagram Format

All diagrams use **Mermaid**, a text-based diagramming language that renders natively on GitHub:

- ✅ No build step required
- ✅ Version control friendly (plain text)
- ✅ Automatic rendering in GitHub markdown
- ✅ Easy to update and maintain

**Diagram Types Used:**
- `graph TB/LR` - Architecture and flow diagrams
- `sequenceDiagram` - Interaction flows
- `erDiagram` - Database schema
- `classDiagram` - Class hierarchies
- `stateDiagram-v2` - State machines
- `flowchart TD` - User and feature flows

---

## 🔗 Quick Links

**Most Frequently Referenced:**
- [System Architecture Overview](./architects/c4-container.md)
- [WebSocket Real-time Flow](./developers/sequences/websocket.md)
- [Database Schema](./developers/database-schema.md)
- [User Journey](./product-managers/user-flows.md)

**Related Documentation:**
- [SDD Specifications](../sdd/02-specification/) - Detailed text specifications
- [Architecture Document](../sdd/02-specification/architecture.md) - Text-based architecture
- [API Specification](../sdd/02-specification/api-spec.md) - API contracts
- [Root README](../../README.md) - Project overview

---

## 📝 Contributing

When updating diagrams:
1. Test Mermaid syntax at [Mermaid Live Editor](https://mermaid.live/)
2. Verify rendering on GitHub preview
3. Keep diagrams focused (one concept per file)
4. Update related text documentation if needed
5. Cross-reference with actual code to ensure accuracy

---

**Last Updated:** 2026-01-21
