# Developer Diagrams

> **Implementation-level diagrams for developers working on PerfWatch**

This directory contains detailed technical diagrams showing deployment architecture, sequence flows, database schema, and class structures.

---

## 📊 Diagrams

### Deployment
- **[Docker Architecture](./deployment.md)** - Container orchestration, ports, volumes, networks

### Sequence Diagrams (Interaction Flows)
- **[Authentication Flow](./sequences/authentication.md)** - Login, JWT lifecycle, navigation guards
- **[WebSocket Metrics](./sequences/websocket.md)** - Real-time streaming, background collection, broadcast
- **[Historical Queries](./sequences/historical-query.md)** - Time-range queries, downsampling, comparison
- **[Retention Cleanup](./sequences/retention.md)** - Background task, policy application, deletion

### Data Structure
- **[Database Schema](./database-schema.md)** - ER diagram, relationships, JSONB structure, indexes

### Code Structure (Class Diagrams)
- **[Collector Classes](./classes/collectors.md)** - BaseCollector hierarchy, 6 implementations
- **[SQLAlchemy Models](./classes/models.md)** - Database models, relationships
- **[Pinia Stores](./classes/stores.md)** - Frontend state management architecture

---

## 🎯 Quick Navigation

**Getting Started:**
1. [Docker Architecture](./deployment.md) - Understand how services are orchestrated
2. [Database Schema](./database-schema.md) - Learn the data model
3. [Collector Classes](./classes/collectors.md) - See how metrics are collected

**Implementing New Features:**
- Adding a new collector? → [Collector Classes](./classes/collectors.md)
- Adding a new API endpoint? → [Authentication Flow](./sequences/authentication.md) for auth patterns
- Modifying WebSocket? → [WebSocket Metrics](./sequences/websocket.md)
- Changing database schema? → [Database Schema](./database-schema.md) + Alembic migration

**Debugging:**
- Auth issues? → [Authentication Flow](./sequences/authentication.md)
- WebSocket disconnects? → [WebSocket Metrics](./sequences/websocket.md)
- Missing metrics? → [Collector Classes](./classes/collectors.md)
- Retention not working? → [Retention Cleanup](./sequences/retention.md)

---

## 🔧 Development Tips

**Reading Sequence Diagrams:**
- Time flows from top to bottom
- Arrows show messages between components
- Boxes show activation (processing time)
- Notes provide additional context

**Reading Class Diagrams:**
- Solid lines = inheritance
- Dashed lines = dependencies
- `+` = public, `-` = private, `#` = protected
- `<<abstract>>` = abstract class

**Reading ER Diagrams:**
- Boxes = tables
- Lines = relationships (1:1, 1:N, N:N)
- Key symbols = primary/foreign keys
- Data types shown in columns

---

## 📚 Related Documentation

- [CLAUDE.md](../../../CLAUDE.md) - Developer guide with commands
- [API Specification](../../sdd/02-specification/api-spec.md) - Endpoint contracts
- [Component Specs](../../sdd/02-specification/component-specs.md) - Component details
- [Architecture Diagrams](../architects/) - High-level views

---

**Navigation:** [← Back to Diagrams Index](../README.md)
