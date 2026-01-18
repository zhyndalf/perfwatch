# PerfWatch Task Backlog

> Tasks not yet broken down into detailed task files

---

## Phase 2: Core Metrics

| Task ID | Name | Brief Description |
|---------|------|-------------------|
| T006 | Collector Base | Base collector class and aggregator |
| T007 | CPU Collector | CPU usage, frequency, temperature |
| T008 | Memory Collector | Memory and swap usage |
| T009 | Network Collector | Bandwidth and connection stats |
| T010 | Disk Collector | I/O throughput and disk usage |
| T011 | WebSocket Streaming | Real-time metrics delivery |
| T012 | Dashboard UI | ECharts integration and layout |

Detailed task files will be created when Phase 1 is complete.

---

## Phase 3: Advanced Metrics

| Task ID | Name | Brief Description |
|---------|------|-------------------|
| T013 | Perf Events Setup | perf_event_open wrapper |
| T014 | Cache Metrics | L1/L2/L3 cache miss rates |
| T015 | CPU Perf Metrics | IPC, cycles, instructions |
| T016 | Memory Bandwidth | DDR read/write rates |
| T017 | Advanced Dashboard | Add perf metrics to UI |

Detailed task files will be created when Phase 2 is complete.

---

## Phase 4: History & Polish

| Task ID | Name | Brief Description |
|---------|------|-------------------|
| T018 | History Storage | Persist metrics to database |
| T019 | Comparison View | Same-period comparison feature |
| T020 | Data Retention | Auto-cleanup and downsampling |
| T021 | Settings Page | Configuration UI |
| T022 | Polish & Testing | Final polish and tests |

Detailed task files will be created when Phase 3 is complete.

---

## Future Ideas (Not Planned)

These are out of scope but noted for potential future work:

- [ ] Multi-user support
- [ ] Remote agent monitoring
- [ ] Custom metrics plugins
- [ ] Alerting system
- [ ] Mobile app
- [ ] Export to CSV/JSON
- [ ] Integration with Grafana
- [ ] Container metrics (Docker stats)
- [ ] GPU metrics (NVIDIA)

---

## Adding New Tasks

When adding a new task to the backlog:

1. Assign the next available Task ID
2. Add to appropriate phase table above
3. Update total task count in `PROGRESS.md`
4. Create detailed task file when ready to implement
