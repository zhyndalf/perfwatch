# T006: Collector Base

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 2 - Core Metrics |
| **Estimated Time** | 2-3 hours |
| **Dependencies** | T003 (Database Setup), T005 (Vue Frontend Base) |
| **Status** | ⬜ NOT_STARTED |

---

## Objective

Create the base collector infrastructure using psutil for system metrics collection, with an aggregator that coordinates multiple collectors and prepares data for WebSocket streaming.

---

## Context

The collector system forms the heart of PerfWatch's metrics gathering:
- Each collector (CPU, Memory, Network, Disk) inherits from a base class
- The aggregator coordinates collection on a 5-second interval
- Data is structured for both real-time streaming and historical storage

This task creates the foundation; specific collectors come in T007-T010.

---

## Specifications

Reference documents:
- [Architecture - Collector System](../../02-specification/architecture.md#collector-system)
- [Data Model - Metrics JSONB](../../02-specification/data-model.md#metrics_snapshot)

---

## Acceptance Criteria

### Base Collector Class
- [ ] Abstract base class with `collect()` method
- [ ] Collector name and interval configuration
- [ ] Error handling with graceful degradation
- [ ] Timestamp attachment to collected data

### Aggregator
- [ ] Coordinates multiple collectors
- [ ] Runs on configurable interval (default 5s)
- [ ] Combines metrics into unified snapshot
- [ ] Async-friendly design for FastAPI integration

### Data Structures
- [ ] Pydantic models for metric snapshots
- [ ] JSONB-compatible output format
- [ ] Type hints throughout

### Testing
- [ ] Unit tests for base collector
- [ ] Unit tests for aggregator
- [ ] Mock collectors for testing

---

## Implementation Details

### Project Structure

```
backend/app/
├── collectors/
│   ├── __init__.py
│   ├── base.py           # BaseCollector abstract class
│   └── aggregator.py     # MetricsAggregator
└── schemas/
    └── metrics.py        # Pydantic models for metrics
```

### Base Collector Class

```python
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Dict

class BaseCollector(ABC):
    """Abstract base class for all metric collectors."""

    name: str = "base"

    @abstractmethod
    async def collect(self) -> Dict[str, Any]:
        """Collect metrics and return as dictionary."""
        pass

    async def safe_collect(self) -> Dict[str, Any]:
        """Collect with error handling - returns empty dict on failure."""
        try:
            data = await self.collect()
            data['_timestamp'] = datetime.now(timezone.utc).isoformat()
            return data
        except Exception as e:
            return {
                '_error': str(e),
                '_timestamp': datetime.now(timezone.utc).isoformat()
            }
```

### Aggregator

```python
import asyncio
from typing import Dict, List, Any

class MetricsAggregator:
    """Coordinates metric collection from multiple collectors."""

    def __init__(self, collectors: List[BaseCollector], interval: float = 5.0):
        self.collectors = collectors
        self.interval = interval
        self._running = False

    async def collect_all(self) -> Dict[str, Any]:
        """Collect from all collectors and combine results."""
        results = {}
        for collector in self.collectors:
            data = await collector.safe_collect()
            results[collector.name] = data
        return results

    async def start(self, callback):
        """Start periodic collection with callback for each snapshot."""
        self._running = True
        while self._running:
            snapshot = await self.collect_all()
            await callback(snapshot)
            await asyncio.sleep(self.interval)

    def stop(self):
        """Stop periodic collection."""
        self._running = False
```

### Metrics Schemas (Pydantic)

```python
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class MetricSnapshot(BaseModel):
    """Single metric collection snapshot."""
    timestamp: datetime
    metric_type: str
    metric_data: Dict[str, Any]

class AggregatedSnapshot(BaseModel):
    """Combined snapshot from all collectors."""
    timestamp: datetime
    cpu: Optional[Dict[str, Any]] = None
    memory: Optional[Dict[str, Any]] = None
    network: Optional[Dict[str, Any]] = None
    disk: Optional[Dict[str, Any]] = None
```

---

## Files to Create

| File | Description |
|------|-------------|
| `backend/app/collectors/__init__.py` | Package init, exports |
| `backend/app/collectors/base.py` | BaseCollector abstract class |
| `backend/app/collectors/aggregator.py` | MetricsAggregator class |
| `backend/app/schemas/metrics.py` | Pydantic metric models |
| `backend/tests/test_collectors.py` | Collector tests |

---

## Verification Steps

```bash
# Run tests
docker compose run --rm backend pytest tests/test_collectors.py -v

# Quick manual test (in Python shell)
docker compose exec backend python -c "
from app.collectors.base import BaseCollector
from app.collectors.aggregator import MetricsAggregator
print('Imports successful!')
"
```

---

## Implementation Notes

*To be filled during implementation*

---

## Files Created/Modified

*To be filled during implementation*
