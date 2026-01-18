# PerfWatch Vision

> The guiding vision and goals for the PerfWatch project

## Mission Statement

**PerfWatch** provides developers and system administrators with a comprehensive, real-time view of their local machine's performance metrics through an intuitive web interface.

---

## Vision

A single-pane-of-glass dashboard that reveals:
- What your CPU is really doing (and how efficiently)
- Where your memory is going
- Network traffic patterns
- Disk I/O bottlenecks
- Low-level hardware performance counters

All updating in real-time, with historical comparison capabilities.

---

## Goals

### Primary Goals

1. **Real-time Visibility**
   - Display all key performance metrics updating every 5 seconds
   - Smooth, lag-free WebSocket streaming
   - Responsive charts that don't overwhelm the browser

2. **Hardware-level Insights**
   - Go beyond basic OS metrics
   - Expose CPU cache hit/miss rates
   - Show IPC (Instructions Per Cycle)
   - Memory bandwidth utilization

3. **Historical Comparison**
   - Compare current performance to same time yesterday/last week
   - Identify patterns and anomalies
   - Track trends over time

4. **Simple Deployment**
   - Single `docker-compose up` command
   - No complex configuration required
   - Works out of the box for local monitoring

### Non-Goals

1. **NOT a distributed monitoring system** - This is for local machine only
2. **NOT a replacement for Prometheus/Grafana** - Different use case
3. **NOT a log aggregator** - Metrics only
4. **NOT a process-level profiler** - System-wide metrics only
5. **NOT an alerting system** - Visualization focused

---

## Target Users

### Primary: Developers
- Want to understand performance while developing
- Need to correlate code changes with performance impact
- Interested in low-level hardware metrics

### Secondary: System Administrators
- Monitoring personal workstations
- Quick diagnostics without heavy tooling
- Learning environment for performance concepts

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Dashboard load time | < 2 seconds |
| Metric update latency | < 100ms from collection to display |
| Memory usage (backend) | < 200MB |
| Memory usage (frontend) | < 100MB |
| Setup time | < 5 minutes from clone to running |

---

## Competitive Landscape

| Tool | Pros | Cons | PerfWatch Differentiator |
|------|------|------|--------------------------|
| htop | Simple, fast | Terminal only, no history | Web UI, historical data |
| Grafana | Powerful, flexible | Complex setup, overkill for local | Single-purpose, easy |
| Intel VTune | Deep insights | Commercial, complex | Free, simple |
| perf CLI | Powerful | Steep learning curve | Accessible web interface |

---

## Timeline

| Phase | Duration | Focus |
|-------|----------|-------|
| Phase 1 | ~1 week | Foundation (Docker, DB, Auth, Basic UI) |
| Phase 2 | ~1 week | Core Metrics (CPU, Memory, Network, Disk) |
| Phase 3 | ~1 week | Advanced Metrics (perf_events, cache, IPC) |
| Phase 4 | ~1 week | History, Comparison, Polish |

**Total Estimated**: ~4 weeks / ~52 hours / ~22 sessions
