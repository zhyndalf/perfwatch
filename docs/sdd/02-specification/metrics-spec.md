# PerfWatch Metrics Specification

> Detailed specification of all metrics collected by PerfWatch

---

## Overview

PerfWatch collects metrics in two categories:

1. **Basic Metrics** - Available via psutil on any Linux system
2. **Advanced Metrics** - Require perf_events (hardware counters)

All metrics are collected every **5 seconds** and streamed via WebSocket.

---

## CPU Metrics

### Basic CPU Metrics (psutil)

| Metric | Unit | Source | Description |
|--------|------|--------|-------------|
| usage_percent | % | psutil.cpu_percent() | Overall CPU utilization |
| per_core | [%] | psutil.cpu_percent(percpu=True) | Per-core utilization |
| user | % | psutil.cpu_times_percent() | Time in user space |
| system | % | psutil.cpu_times_percent() | Time in kernel space |
| idle | % | psutil.cpu_times_percent() | Idle time |
| iowait | % | psutil.cpu_times_percent() | Waiting for I/O |
| irq | % | psutil.cpu_times_percent() | Hardware interrupts |
| softirq | % | psutil.cpu_times_percent() | Software interrupts |
| frequency_mhz | [MHz] | psutil.cpu_freq(percpu=True) | Current frequency per core |
| temperature_celsius | [°C] | psutil.sensors_temperatures() | Per-core temperature |
| interrupts | count | /proc/interrupts | Total interrupt count |

### Advanced CPU Metrics (perf_events)

| Metric | Unit | perf Event | Description |
|--------|------|------------|-------------|
| cycles | count | PERF_COUNT_HW_CPU_CYCLES | Total CPU cycles |
| instructions | count | PERF_COUNT_HW_INSTRUCTIONS | Instructions retired |
| ipc | ratio | instructions / cycles | Instructions per cycle |

### Collection Code (psutil)
```python
import psutil

def collect_cpu_metrics():
    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True)
    cpu_times = psutil.cpu_times_percent(interval=None)
    cpu_freq = psutil.cpu_freq(percpu=True)

    # Temperature (may not be available on all systems)
    temps = {}
    try:
        temps = psutil.sensors_temperatures()
    except:
        pass

    return {
        "usage_percent": cpu_percent,
        "per_core": cpu_percent_per_core,
        "user": cpu_times.user,
        "system": cpu_times.system,
        "idle": cpu_times.idle,
        "iowait": getattr(cpu_times, 'iowait', 0),
        "irq": getattr(cpu_times, 'irq', 0),
        "softirq": getattr(cpu_times, 'softirq', 0),
        "frequency_mhz": [f.current for f in cpu_freq] if cpu_freq else [],
        "temperature_celsius": extract_core_temps(temps),
    }
```

---

## Memory Metrics

### Basic Memory Metrics (psutil)

| Metric | Unit | Source | Description |
|--------|------|--------|-------------|
| usage_percent | % | psutil.virtual_memory() | Memory utilization |
| total_bytes | bytes | psutil.virtual_memory().total | Total physical memory |
| used_bytes | bytes | psutil.virtual_memory().used | Used memory |
| available_bytes | bytes | psutil.virtual_memory().available | Available for use |
| free_bytes | bytes | psutil.virtual_memory().free | Completely free |
| cached_bytes | bytes | psutil.virtual_memory().cached | File system cache |
| buffers_bytes | bytes | psutil.virtual_memory().buffers | I/O buffers |
| swap_total_bytes | bytes | psutil.swap_memory().total | Total swap |
| swap_used_bytes | bytes | psutil.swap_memory().used | Used swap |
| swap_free_bytes | bytes | psutil.swap_memory().free | Free swap |

### Hugepages Metrics

| Metric | Unit | Source | Description |
|--------|------|--------|-------------|
| hugepages_total | count | /proc/meminfo | Total hugepages |
| hugepages_free | count | /proc/meminfo | Free hugepages |
| hugepages_reserved | count | /proc/meminfo | Reserved hugepages |

### Advanced Memory Metrics (perf_events)

| Metric | Unit | Source | Description |
|--------|------|--------|-------------|
| memory_bandwidth_read_mbps | MB/s | IMC counters | Memory read bandwidth |
| memory_bandwidth_write_mbps | MB/s | IMC counters | Memory write bandwidth |

### Collection Code
```python
import psutil

def collect_memory_metrics():
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    hugepages = read_hugepages_info()

    return {
        "usage_percent": mem.percent,
        "total_bytes": mem.total,
        "used_bytes": mem.used,
        "available_bytes": mem.available,
        "free_bytes": mem.free,
        "cached_bytes": getattr(mem, 'cached', 0),
        "buffers_bytes": getattr(mem, 'buffers', 0),
        "swap_total_bytes": swap.total,
        "swap_used_bytes": swap.used,
        "swap_free_bytes": swap.free,
        "hugepages_total": hugepages.get('total', 0),
        "hugepages_free": hugepages.get('free', 0),
        "hugepages_reserved": hugepages.get('reserved', 0),
    }
```

---

## Cache Metrics (perf_events)

### L1 Instruction Cache

| Metric | perf Event | Description |
|--------|------------|-------------|
| l1i_loads | L1-icache-loads | L1-I cache loads |
| l1i_misses | L1-icache-load-misses | L1-I cache misses |
| l1i_miss_rate | misses/loads | Miss rate percentage |

### L1 Data Cache

| Metric | perf Event | Description |
|--------|------------|-------------|
| l1d_loads | L1-dcache-loads | L1-D cache loads |
| l1d_misses | L1-dcache-load-misses | L1-D cache misses |
| l1d_miss_rate | misses/loads | Miss rate percentage |

### L2 Cache

| Metric | perf Event | Description |
|--------|------------|-------------|
| l2_loads | l2_rqsts.references | L2 cache references |
| l2_misses | l2_rqsts.miss | L2 cache misses |
| l2_miss_rate | misses/loads | Miss rate percentage |

### L3/LLC Cache

| Metric | perf Event | Description |
|--------|------------|-------------|
| llc_loads | LLC-loads | Last level cache loads |
| llc_misses | LLC-load-misses | Last level cache misses |
| llc_miss_rate | misses/loads | Miss rate percentage |

### Cache Collection Notes
- Requires `perf_event_paranoid` <= 1 or root privileges
- Not all CPUs support all counters
- Gracefully degrade if unavailable

---

## Network Metrics

### Per-Interface Metrics

| Metric | Unit | Source | Description |
|--------|------|--------|-------------|
| bytes_sent | bytes | psutil.net_io_counters() | Total bytes transmitted |
| bytes_recv | bytes | psutil.net_io_counters() | Total bytes received |
| bytes_sent_per_sec | bytes/s | Calculated | Send rate |
| bytes_recv_per_sec | bytes/s | Calculated | Receive rate |
| packets_sent | count | psutil.net_io_counters() | Total packets sent |
| packets_recv | count | psutil.net_io_counters() | Total packets received |
| packets_sent_per_sec | pkts/s | Calculated | Send packet rate |
| packets_recv_per_sec | pkts/s | Calculated | Receive packet rate |
| errors_in | count | psutil.net_io_counters() | Receive errors |
| errors_out | count | psutil.net_io_counters() | Transmit errors |
| drops_in | count | psutil.net_io_counters() | Receive drops |
| drops_out | count | psutil.net_io_counters() | Transmit drops |

### Connection Statistics

| Metric | Unit | Source | Description |
|--------|------|--------|-------------|
| tcp_established | count | psutil.net_connections() | Established TCP connections |
| tcp_time_wait | count | psutil.net_connections() | TIME_WAIT connections |
| tcp_close_wait | count | psutil.net_connections() | CLOSE_WAIT connections |
| tcp_listen | count | psutil.net_connections() | Listening sockets |
| udp_count | count | psutil.net_connections() | UDP sockets |

### Collection Code
```python
import psutil

class NetworkCollector:
    def __init__(self):
        self.previous = {}
        self.previous_time = None

    def collect(self):
        current_time = time.time()
        net_io = psutil.net_io_counters(pernic=True)

        result = {"interfaces": {}, "connections": {}}

        for iface, counters in net_io.items():
            if iface == 'lo':  # Skip loopback
                continue

            prev = self.previous.get(iface, {})
            time_delta = current_time - (self.previous_time or current_time)

            result["interfaces"][iface] = {
                "bytes_sent": counters.bytes_sent,
                "bytes_recv": counters.bytes_recv,
                "bytes_sent_per_sec": self._rate(counters.bytes_sent, prev.get('bytes_sent'), time_delta),
                "bytes_recv_per_sec": self._rate(counters.bytes_recv, prev.get('bytes_recv'), time_delta),
                # ... more metrics
            }
            self.previous[iface] = counters._asdict()

        # Connection stats
        connections = psutil.net_connections(kind='inet')
        result["connections"] = self._count_connection_states(connections)

        self.previous_time = current_time
        return result
```

---

## Disk Metrics

### Per-Device I/O Metrics

| Metric | Unit | Source | Description |
|--------|------|--------|-------------|
| read_bytes | bytes | psutil.disk_io_counters() | Total bytes read |
| write_bytes | bytes | psutil.disk_io_counters() | Total bytes written |
| read_bytes_per_sec | bytes/s | Calculated | Read throughput |
| write_bytes_per_sec | bytes/s | Calculated | Write throughput |
| read_count | count | psutil.disk_io_counters() | Read operations |
| write_count | count | psutil.disk_io_counters() | Write operations |
| read_iops | ops/s | Calculated | Read IOPS |
| write_iops | ops/s | Calculated | Write IOPS |
| read_time_ms | ms | psutil.disk_io_counters() | Time spent reading |
| write_time_ms | ms | psutil.disk_io_counters() | Time spent writing |
| read_latency_ms | ms | Calculated | Average read latency |
| write_latency_ms | ms | Calculated | Average write latency |

### Per-Partition Usage

| Metric | Unit | Source | Description |
|--------|------|--------|-------------|
| device | string | psutil.disk_partitions() | Device name |
| fstype | string | psutil.disk_partitions() | Filesystem type |
| mountpoint | string | psutil.disk_partitions() | Mount point |
| total_bytes | bytes | psutil.disk_usage() | Total space |
| used_bytes | bytes | psutil.disk_usage() | Used space |
| free_bytes | bytes | psutil.disk_usage() | Free space |
| usage_percent | % | psutil.disk_usage() | Usage percentage |

### Collection Code
```python
import psutil

class DiskCollector:
    def __init__(self):
        self.previous_io = {}
        self.previous_time = None

    def collect(self):
        current_time = time.time()
        time_delta = current_time - (self.previous_time or current_time)

        # I/O counters
        disk_io = psutil.disk_io_counters(perdisk=True)
        devices = {}

        for device, counters in disk_io.items():
            if device.startswith('loop'):  # Skip loop devices
                continue

            prev = self.previous_io.get(device, {})
            devices[device] = {
                "read_bytes_per_sec": self._rate(counters.read_bytes, prev.get('read_bytes'), time_delta),
                "write_bytes_per_sec": self._rate(counters.write_bytes, prev.get('write_bytes'), time_delta),
                "read_iops": self._rate(counters.read_count, prev.get('read_count'), time_delta),
                "write_iops": self._rate(counters.write_count, prev.get('write_count'), time_delta),
                # Calculate latency
                "read_latency_ms": self._latency(counters.read_time, prev.get('read_time'),
                                                  counters.read_count, prev.get('read_count')),
                # ... more metrics
            }
            self.previous_io[device] = counters._asdict()

        # Partition usage
        partitions = {}
        for part in psutil.disk_partitions():
            if 'loop' in part.device:
                continue
            usage = psutil.disk_usage(part.mountpoint)
            partitions[part.mountpoint] = {
                "device": part.device,
                "fstype": part.fstype,
                "total_bytes": usage.total,
                "used_bytes": usage.used,
                "free_bytes": usage.free,
                "usage_percent": usage.percent
            }

        self.previous_time = current_time
        return {"devices": devices, "partitions": partitions}
```

---

## Perf Events Metrics

### Availability Check
```python
def check_perf_available():
    """Check if perf_events is available."""
    try:
        # Check paranoid level
        with open('/proc/sys/kernel/perf_event_paranoid', 'r') as f:
            paranoid = int(f.read().strip())

        # Need paranoid <= 1 or root
        if paranoid > 1 and os.geteuid() != 0:
            return False, "perf_event_paranoid > 1 and not root"

        return True, None
    except Exception as e:
        return False, str(e)
```

### Event Configuration
```python
PERF_EVENTS = {
    # Hardware events
    'cycles': PERF_TYPE_HARDWARE | PERF_COUNT_HW_CPU_CYCLES,
    'instructions': PERF_TYPE_HARDWARE | PERF_COUNT_HW_INSTRUCTIONS,

    # Cache events
    'L1-icache-load-misses': PERF_TYPE_HW_CACHE | L1I | MISS,
    'L1-dcache-load-misses': PERF_TYPE_HW_CACHE | L1D | MISS,
    'LLC-load-misses': PERF_TYPE_HW_CACHE | LLC | MISS,

    # Raw events (CPU-specific, may need adjustment)
    'l2_misses': PERF_TYPE_RAW | 0x3F24,  # Intel: l2_rqsts.miss
}
```

### Graceful Degradation
```python
def collect_perf_metrics():
    available, error = check_perf_available()

    if not available:
        return {
            "available": False,
            "error": error,
            "ipc": None,
            "cache": None,
            "memory_bandwidth": None
        }

    try:
        # Collect available metrics
        # Some may fail on specific hardware
        return {
            "available": True,
            "error": None,
            "ipc": collect_ipc(),
            "cache": collect_cache_metrics(),
            "memory_bandwidth": collect_memory_bandwidth()
        }
    except Exception as e:
        return {
            "available": False,
            "error": str(e),
            # ...
        }
```

---

## Metric Aggregation

### Sampling Strategy
1. Collect all metrics every 5 seconds
2. Calculate rates from deltas (network, disk)
3. Aggregate per-core data when needed
4. Package into single MetricSnapshot

### Data Flow
```
Collectors (parallel) → Aggregator → WebSocket + Database
    ↓
    ├── CPU Collector
    ├── Memory Collector
    ├── Network Collector
    ├── Disk Collector
    └── Perf Collector
```

### Error Handling
- Individual collector failure doesn't stop others
- Failed metrics reported as `null` in snapshot
- Errors logged but not surfaced to UI prominently
