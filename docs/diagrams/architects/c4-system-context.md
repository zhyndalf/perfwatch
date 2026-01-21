# C4 System Context Diagram

> **Level 1: System Context - PerfWatch in its environment**

This diagram shows PerfWatch as a black box, its users, and external systems it interacts with.

---

## Diagram

```mermaid
graph TB
    User[👤 System Administrator<br/>Local user monitoring<br/>Linux system performance]

    PerfWatch[PerfWatch<br/>Real-time System<br/>Performance Monitor]

    Browser[🌐 Web Browser<br/>Chrome/Firefox/Safari]
    LinuxKernel[🐧 Linux Kernel<br/>Metrics source:<br/>CPU, memory, disk, network,<br/>perf_events, vmstat]

    User -->|Views metrics via| Browser
    Browser -->|HTTP/WebSocket| PerfWatch
    PerfWatch -->|Collects metrics from| LinuxKernel

    classDef userStyle fill:#4CAF50,stroke:#2E7D32,color:#fff
    classDef systemStyle fill:#2196F3,stroke:#1565C0,color:#fff
    classDef externalStyle fill:#FF9800,stroke:#E65100,color:#fff

    class User userStyle
    class PerfWatch systemStyle
    class Browser,LinuxKernel externalStyle
```

---

## Elements

### User: System Administrator
**Type:** Person
**Description:** Local user who monitors Linux system performance in real-time

**Responsibilities:**
- Views real-time metrics dashboard
- Queries historical performance data
- Configures retention policies
- Analyzes system performance trends

**Interactions:**
- Uses web browser to access PerfWatch
- Single admin user (username: `admin`)

---

### System: PerfWatch
**Type:** Software System
**Description:** Real-time system performance monitoring web application

**Capabilities:**
- Streams live metrics every 5 seconds via WebSocket
- Stores metrics in PostgreSQL with JSONB format
- Provides historical queries with downsampling
- Manages data retention automatically
- Collects CPU, memory, network, disk, and hardware counters

**Technology:**
- Frontend: Vue.js 3 SPA
- Backend: FastAPI + WebSocket
- Database: PostgreSQL 15
- Deployment: Docker Compose

---

### External System: Web Browser
**Type:** External Software
**Description:** Modern web browser (Chrome, Firefox, Safari)

**Role:**
- Renders Vue.js single-page application
- Establishes WebSocket connection for real-time streaming
- Stores JWT authentication token
- Visualizes metrics with ECharts library

**Requirements:**
- Modern browser with WebSocket support
- JavaScript enabled
- Localhost access (http://localhost:3000)

---

### External System: Linux Kernel
**Type:** Operating System
**Description:** Linux kernel providing system metrics

**Metrics Provided:**
- **CPU:** Usage, frequency, temperature, load average (via psutil)
- **Memory:** RAM/swap usage, buffers, cached (via psutil)
- **Network:** Bytes/packets sent/received, per-interface (via psutil)
- **Disk:** Partition usage, read/write I/O (via psutil)
- **Hardware Counters:** IPC, cache misses, branch mispredictions (via perf_events)
- **Memory Bandwidth:** Page I/O, swap activity (via /proc/vmstat)

**Access Method:**
- psutil library for standard metrics
- perf_events for hardware performance counters (requires privileged mode)
- /proc filesystem for kernel statistics

---

## System Boundary

**Inside PerfWatch:**
- Web frontend (user interface)
- API backend (data collection and serving)
- PostgreSQL database (metrics storage)
- Metrics collectors (psutil, perf_events)

**Outside PerfWatch:**
- User's web browser
- Linux kernel (metrics source)
- Docker host system

---

## Key Constraints

1. **Linux Only:** perf_events hardware counters require Linux kernel
2. **Localhost Only:** No remote monitoring support
3. **Single User:** One admin account (no multi-user)
4. **Privileged Access:** Docker container needs privileged mode for perf_events
5. **Real-time Focus:** 5-second sampling interval (not configurable)

---

## Data Flow Summary

```
Linux Kernel → psutil/perf_events → PerfWatch Backend → PostgreSQL
                                  → WebSocket → Browser → User
```

---

**Navigation:**
- [← Back to Architects](./README.md)
- [Next: Container Diagram →](./c4-container.md)
- [↑ Diagrams Index](../README.md)
