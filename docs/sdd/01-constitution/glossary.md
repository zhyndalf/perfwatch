# PerfWatch Glossary

> Domain terminology and definitions used throughout the project

---

## General Terms

### PerfWatch
The name of this project - a real-time system performance monitoring web application.

### SDD (Specification Driven Development)
Our development methodology where all specifications, plans, and tasks are documented in markdown files that persist across conversations and serve as the single source of truth.

### Session
A single development conversation, typically 2-4 hours, completing one atomic task.

---

## Architecture Terms

### Collector
A Python module responsible for gathering a specific category of metrics (CPU, memory, network, disk, perf_events). Each collector implements a common interface.

### Aggregator
The central component that coordinates all collectors, runs them on schedule (every 5 seconds), and distributes collected metrics to WebSocket clients and database storage.

### Metric Snapshot
A single point-in-time collection of all metrics, stored with a timestamp. The atomic unit of metric storage.

---

## Metric Categories

### Basic Metrics
Metrics available through standard OS interfaces (psutil):
- CPU usage and time breakdown
- Memory usage and swap
- Network bandwidth and packets
- Disk I/O and usage

### Advanced Metrics
Metrics requiring hardware counter access (perf_events):
- Cache miss rates (L1, L2, L3)
- IPC (Instructions Per Cycle)
- CPU cycles
- Memory bandwidth

---

## CPU Metrics Glossary

### CPU Usage %
Percentage of CPU time spent doing work (non-idle).

### CPU Time Breakdown
- **User**: Time running user-space programs
- **System**: Time in kernel/system calls
- **Idle**: Time doing nothing
- **IOWait**: Time waiting for I/O operations
- **IRQ**: Time handling hardware interrupts
- **SoftIRQ**: Time handling software interrupts

### IPC (Instructions Per Cycle)
How many instructions the CPU completes per clock cycle. Higher is better. Typical values: 0.5-3.0.

### CPU Cycles
Total clock cycles consumed. Used with instructions to calculate IPC.

---

## Memory Metrics Glossary

### Memory Usage Types
- **Used**: Memory actively in use by applications
- **Free**: Completely unused memory
- **Available**: Memory that could be made available (free + reclaimable cache)
- **Cached**: Memory used for file system cache
- **Buffers**: Memory used for I/O buffers

### Swap
Disk space used as virtual memory when RAM is full.
- **Swap In**: Pages moved from disk to RAM
- **Swap Out**: Pages moved from RAM to disk

### Hugepages
Large memory pages (2MB or 1GB instead of 4KB) for reducing TLB misses.

### Memory Bandwidth
Rate of data transfer between CPU and RAM (GB/s). Measured via perf_events.

---

## Cache Metrics Glossary

### Cache Hierarchy
```
CPU Core
  └── L1 Cache (fastest, smallest)
       ├── L1-I (Instructions)
       └── L1-D (Data)
  └── L2 Cache (medium)
  └── L3/LLC Cache (largest, shared between cores)
```

### Cache Miss
When requested data is not found in cache and must be fetched from a slower level.

### L1-icache-load-misses
L1 instruction cache misses - code not found in fastest cache.

### L1-dcache-load-misses
L1 data cache misses - data not found in fastest cache.

### LLC-load-misses
Last Level Cache (L3) misses - data must come from main memory.

---

## Network Metrics Glossary

### Bandwidth
Data transfer rate (bytes/second):
- **bytes_sent**: Outgoing data
- **bytes_recv**: Incoming data

### Packet Rate
Network packets per second:
- **packets_sent**: Outgoing packets
- **packets_recv**: Incoming packets

### Connection States
TCP connection states:
- **ESTABLISHED**: Active connections
- **TIME_WAIT**: Recently closed, waiting for cleanup
- **LISTEN**: Waiting for incoming connections

---

## Disk Metrics Glossary

### Throughput
Data transfer rate (MB/s):
- **Read MB/s**: Data read from disk
- **Write MB/s**: Data written to disk

### IOPS
I/O Operations Per Second - how many read/write operations.

### Latency
Time for an I/O operation to complete (milliseconds).

### Usage %
Percentage of disk space used per partition.

---

## Technical Terms

### perf_events
Linux kernel subsystem for accessing hardware performance counters. Requires elevated privileges.

### PMU (Performance Monitoring Unit)
Hardware in the CPU that counts performance events (cache misses, cycles, instructions).

### IMC (Integrated Memory Controller)
CPU component managing RAM access. Has counters for memory bandwidth.

### psutil
Python library for system metrics. Cross-platform abstraction over OS APIs.

### JWT (JSON Web Token)
Authentication token format. Contains encoded user info and signature.

### WebSocket
Bidirectional communication protocol. Used for real-time metric streaming.

### JSONB
PostgreSQL binary JSON format. Used for flexible metric storage.

---

## UI Terms

### Dashboard
The main view showing all real-time metrics in chart form.

### History View
Page for querying and viewing historical metric data.

### Comparison View
Feature to compare current metrics with same time period in the past.

### Metric Card
UI component displaying a single metric category with its chart.

---

## Data Management Terms

### Retention Policy
Rules for how long to keep metric data before deletion.

### Downsampling
Aggregating fine-grained data into coarser intervals (e.g., 5-second data → 1-minute averages).

### Archive
Moving old data to compressed storage or deleting it based on retention policy.
