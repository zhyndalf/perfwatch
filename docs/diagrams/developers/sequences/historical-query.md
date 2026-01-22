# Historical Query Sequence Diagram

> **Time-range data retrieval and comparison**

This diagram shows how users query historical metrics data and compare different time periods.

---

## Single Time Range Query

```mermaid
sequenceDiagram
    actor User
    participant HistoryVue as History.vue
    participant HistoryStore as historyStore
    participant APIClient as API Client
    participant Backend as FastAPI
    participant HistoryAPI as history.py
    participant DB as PostgreSQL
    participant ECharts as ECharts

    User->>HistoryVue: Select time range<br/>(start, end dates)
    User->>HistoryVue: Click "Query"

    HistoryVue->>HistoryStore: fetchMetrics(start, end)
    activate HistoryStore

    HistoryStore->>HistoryStore: loading = true
    HistoryStore->>APIClient: GET /api/history/metrics?start=...&end=...
    activate APIClient

    APIClient->>Backend: HTTP GET /api/history/metrics
    activate Backend
    Note over APIClient,Backend: Authorization: Bearer <JWT><br/>Query params: start_time, end_time

    Backend->>HistoryAPI: get_metrics(start, end, db)
    activate HistoryAPI

    HistoryAPI->>HistoryAPI: Calculate data points<br/>time_range_seconds / 5
    Note over HistoryAPI: Downsample if > 1000 points

    alt Data points <= 1000 (no downsampling)
        HistoryAPI->>DB: SELECT * FROM metrics_snapshots<br/>WHERE timestamp BETWEEN start AND end<br/>ORDER BY timestamp
        activate DB
        DB-->>HistoryAPI: Raw snapshots (all 5s data)
        deactivate DB

        HistoryAPI->>HistoryAPI: Transform JSONB to response format
        HistoryAPI-->>Backend: { timestamps: [...], cpu: [...], memory: [...], ... }
    else Data points > 1000 (downsample required)
        HistoryAPI->>HistoryAPI: downsample_interval = time_range / 1000
        Note over HistoryAPI: e.g., 1 hour range → 3.6s interval<br/>Use 5s (nearest multiple)

        HistoryAPI->>DB: SELECT<br/>  date_trunc('minute', timestamp) as bucket,<br/>  AVG((metric_data->>'cpu_usage')::float),<br/>  ...<br/>FROM metrics_snapshots<br/>WHERE timestamp BETWEEN start AND end<br/>GROUP BY bucket<br/>ORDER BY bucket
        activate DB
        Note over DB: Aggregate to reduce data points
        DB-->>HistoryAPI: Downsampled results (~1000 points)
        deactivate DB

        HistoryAPI->>HistoryAPI: Transform aggregated data
        HistoryAPI-->>Backend: { timestamps: [...], cpu: [...], memory: [...], ... }
    end

    deactivate HistoryAPI
    Backend-->>APIClient: 200 OK + JSON data
    deactivate Backend

    APIClient-->>HistoryStore: Response data
    deactivate APIClient

    HistoryStore->>HistoryStore: metrics = response.data
    HistoryStore->>HistoryStore: loading = false
    HistoryStore-->>HistoryVue: Data ready

    deactivate HistoryStore

    HistoryVue->>ECharts: Render charts with historical data
    activate ECharts
    ECharts->>ECharts: Plot time series (line charts)
    ECharts-->>HistoryVue: Charts rendered ✅
    deactivate ECharts

    HistoryVue-->>User: Display historical metrics
```

---

## Time Period Comparison

```mermaid
sequenceDiagram
    actor User
    participant HistoryVue as History.vue
    participant HistoryStore as historyStore
    participant APIClient as API Client
    participant Backend as FastAPI
    participant HistoryAPI as history.py
    participant DB as PostgreSQL

    User->>HistoryVue: Enable "Compare Mode"

    alt Relative Comparison
        User->>HistoryVue: Select Period (e.g., "last hour")
        User->>HistoryVue: Select Compare To (e.g., "yesterday")
        User->>HistoryVue: Click "Compare"

        HistoryVue->>HistoryStore: fetchComparison(period, compare_to)
        activate HistoryStore

        HistoryStore->>HistoryStore: loading = true
        HistoryStore->>APIClient: GET /api/history/compare<br/>?metric_type=...&period=hour&compare_to=yesterday
        activate APIClient

        APIClient->>Backend: HTTP GET /api/history/compare
        activate Backend
        Note over APIClient,Backend: Query params:<br/>metric_type, period, compare_to

        Backend->>HistoryAPI: compare_metrics_history(params, db)
        activate HistoryAPI

        HistoryAPI->>HistoryAPI: Calculate time ranges:<br/>current = now - period<br/>comparison = current - compare_shift

        par Query Current Period
            HistoryAPI->>DB: SELECT * FROM metrics_snapshots<br/>WHERE metric_type = ? AND timestamp BETWEEN current_start AND current_end
            activate DB
            DB-->>HistoryAPI: Current period snapshots
            deactivate DB
        and Query Comparison Period
            HistoryAPI->>DB: SELECT * FROM metrics_snapshots<br/>WHERE metric_type = ? AND timestamp BETWEEN comparison_start AND comparison_end
            activate DB
            DB-->>HistoryAPI: Comparison period snapshots
            deactivate DB
        end

    else Custom Range Comparison
        User->>HistoryVue: Select Period 1 (start_time_1, end_time_1)
        User->>HistoryVue: Select Period 2 (start_time_2, end_time_2)
        User->>HistoryVue: Click "Compare"

        HistoryVue->>HistoryStore: fetchComparison(period1, period2)
        activate HistoryStore

        HistoryStore->>HistoryStore: loading = true
        HistoryStore->>APIClient: GET /api/history/compare<br/>?start_time_1=...&end_time_1=...&start_time_2=...&end_time_2=...
        activate APIClient

        APIClient->>Backend: HTTP GET /api/history/compare
        activate Backend
        Note over APIClient,Backend: Query params:<br/>start_time_1, end_time_1<br/>start_time_2, end_time_2

        Backend->>HistoryAPI: compare_metrics_custom_range(params, db)
        activate HistoryAPI

        HistoryAPI->>HistoryAPI: Validate periods have same duration

        par Query Period 1
            HistoryAPI->>DB: SELECT * FROM metrics_snapshots<br/>WHERE metric_type = ? AND timestamp BETWEEN start1 AND end1
            activate DB
            DB-->>HistoryAPI: Period 1 snapshots
            deactivate DB
        and Query Period 2
            HistoryAPI->>DB: SELECT * FROM metrics_snapshots<br/>WHERE metric_type = ? AND timestamp BETWEEN start2 AND end2
            activate DB
            DB-->>HistoryAPI: Period 2 snapshots
            deactivate DB
        end
    end

    HistoryAPI->>HistoryAPI: Calculate summary statistics:<br/>- current_avg<br/>- comparison_avg<br/>- change_percent
    Note over HistoryAPI: Extract primary values<br/>and compute averages

    HistoryAPI-->>Backend: {<br/>  current: { data_points: [...] },<br/>  comparison: { data_points: [...] },<br/>  summary: { current_avg, comparison_avg, change_percent }<br/>}
    deactivate HistoryAPI

    Backend-->>APIClient: 200 OK + comparison data
    deactivate Backend

    APIClient-->>HistoryStore: Response data
    deactivate APIClient

    HistoryStore->>HistoryStore: comparisonMetrics = response.data
    HistoryStore->>HistoryStore: loading = false
    HistoryStore-->>HistoryVue: Comparison ready

    deactivate HistoryStore

    HistoryVue->>HistoryVue: Render comparison charts and table
    Note over HistoryVue: Show side-by-side time series<br/>with color-coded changes<br/>(green = improved, red = degraded)

    HistoryVue-->>User: Display comparison results
```

---

## Downsampling Strategy

### When Downsampling Applies

**Example Time Ranges:**

| Time Range | Raw Points (5s) | Downsampled To | Interval |
|------------|----------------|----------------|----------|
| 1 hour | 720 | 720 (no downsample) | 5s |
| 6 hours | 4,320 | 1,000 | 21.6s → 25s |
| 24 hours | 17,280 | 1,000 | 86.4s → 90s |
| 7 days | 120,960 | 1,000 | 604.8s → 10min |
| 30 days | 518,400 | 1,000 | 2592s → 45min |

**Algorithm:**
```python
# backend/app/api/history.py
def calculate_downsample_interval(start_time, end_time):
    time_range_seconds = (end_time - start_time).total_seconds()
    raw_points = time_range_seconds / 5  # 5-second sampling

    if raw_points <= 1000:
        return None  # No downsampling needed

    target_interval = time_range_seconds / 1000  # Target 1000 points
    # Round up to nearest multiple of 5 (original sampling rate)
    return math.ceil(target_interval / 5) * 5
```

---

### Downsampling Query (PostgreSQL)

```sql
-- No downsampling (< 1000 points)
SELECT
  timestamp,
  metric_data
FROM metrics_snapshots
WHERE timestamp BETWEEN $1 AND $2
ORDER BY timestamp;

-- With downsampling (> 1000 points)
SELECT
  date_trunc('minute', timestamp) AS bucket,  -- Or 'hour' for longer ranges
  jsonb_build_object(
    'cpu_usage', AVG((metric_data->'cpu'->>'usage_percent')::float),
    'memory_used', AVG((metric_data->'memory'->>'used_bytes')::bigint),
    'network_sent', SUM((metric_data->'network'->>'bytes_sent')::bigint),
    'disk_read', SUM((metric_data->'disk'->>'read_bytes')::bigint)
    -- ... other metrics
  ) AS aggregated_data
FROM metrics_snapshots
WHERE timestamp BETWEEN $1 AND $2
GROUP BY bucket
ORDER BY bucket
LIMIT 1000;
```

**Aggregation Functions:**
- **AVG:** CPU %, memory %, selected perf event
- **SUM:** Network bytes, disk I/O (cumulative counters)
- **MAX:** Temperature, peak values
- **MIN:** Available memory (show worst case)

---

## Response Transformation

### Database → API Response

**Database JSONB Structure:**
```json
{
  "cpu": {
    "usage_percent": 45.2,
    "per_core": [40, 50, 42, 48],
    "frequency_mhz": 2400
  },
  "memory": {
    "used_bytes": 8589934592,
    "available_bytes": 7516192768,
    "percent": 53.3
  }
}
```

**API Response (for ECharts):**
```json
{
  "timestamps": ["2026-01-21T10:00:00Z", "2026-01-21T10:00:05Z", ...],
  "cpu": {
    "usage": [45.2, 46.1, 44.8, ...],
    "frequency": [2400, 2400, 2450, ...]
  },
  "memory": {
    "used_gb": [8.0, 8.1, 8.05, ...],
    "percent": [53.3, 53.8, 53.5, ...]
  },
  "network": {
    "bytes_sent_per_sec": [1024, 2048, 1536, ...],
    "bytes_recv_per_sec": [4096, 3072, 5120, ...]
  }
}
```

**Transformation Logic:**
```python
# backend/app/api/history.py
def transform_snapshots(snapshots):
    result = {
        "timestamps": [],
        "cpu": {"usage": [], "frequency": []},
        "memory": {"used_gb": [], "percent": []},
        # ...
    }

    for snapshot in snapshots:
        result["timestamps"].append(snapshot.timestamp.isoformat())
        result["cpu"]["usage"].append(snapshot.metric_data["cpu"]["usage_percent"])
        result["memory"]["used_gb"].append(
            snapshot.metric_data["memory"]["used_bytes"] / 1024**3
        )
        # ...

    return result
```

---

## Frontend Chart Rendering

```javascript
// frontend/src/views/History.vue
import { useHistoryStore } from '@/stores/history'
import { ref, watch } from 'vue'
import * as echarts from 'echarts'

const historyStore = useHistoryStore()
const chartInstance = ref(null)

// Fetch data
await historyStore.fetchMetrics(startTime, endTime)

// Configure ECharts
const option = {
  title: { text: 'CPU Usage Over Time' },
  tooltip: {
    trigger: 'axis',
    formatter: (params) => {
      const time = new Date(params[0].name).toLocaleString()
      const value = params[0].value.toFixed(2)
      return `${time}<br/>CPU: ${value}%`
    }
  },
  xAxis: {
    type: 'category',
    data: historyStore.metrics.timestamps,
    axisLabel: {
      formatter: (value) => new Date(value).toLocaleTimeString()
    }
  },
  yAxis: {
    type: 'value',
    name: 'CPU %',
    min: 0,
    max: 100
  },
  series: [{
    name: 'CPU Usage',
    type: 'line',
    data: historyStore.metrics.cpu.usage,
    smooth: true,
    lineStyle: { width: 2 },
    areaStyle: { opacity: 0.3 }
  }]
}

chartInstance.value.setOption(option)
```

---

## Performance Optimizations

### Database Indexing

**Critical Index:**
```sql
CREATE INDEX idx_metrics_timestamp
ON metrics_snapshots(timestamp);
```

**Why:** Time-range queries (`WHERE timestamp BETWEEN`) use index scan instead of full table scan.

**Query Plan (with index):**
```
Index Scan using idx_metrics_timestamp on metrics_snapshots
  Index Cond: (timestamp >= '2026-01-21 00:00:00' AND timestamp <= '2026-01-21 23:59:59')
  Rows: 17280 (filtered to 1000 after aggregation)
```

---

### Query Performance

| Time Range | Raw Points | Query Time (no index) | Query Time (with index) |
|------------|------------|----------------------|------------------------|
| 1 hour | 720 | 50ms | 10ms |
| 24 hours | 17,280 | 500ms | 50ms |
| 7 days | 120,960 | 3000ms | 200ms |
| 30 days | 518,400 | 15000ms | 800ms |

**Bottleneck:** JSONB field extraction (`metric_data->'cpu'->>'usage_percent'`)
**Mitigation:** Downsample to reduce rows processed

---

### Frontend Optimization

**Lazy Loading:**
```javascript
// Don't fetch on page mount, wait for user to select range
const fetchOnDemand = () => {
  if (!startTime || !endTime) return
  historyStore.fetchMetrics(startTime, endTime)
}
```

**Chart Update Throttling:**
```javascript
import { debounce } from 'lodash'

const updateChart = debounce(() => {
  chartInstance.value.setOption(option)
}, 100)  // Update at most every 100ms
```

**Data Streaming (Future):**
- For very large ranges, stream data in chunks
- Render chart progressively as data arrives
- Not implemented in current version (1000-point limit sufficient)

---

## Error Handling

### Invalid Time Range

**Error:** `end_time` before `start_time`
**Response:** `400 Bad Request`
```json
{
  "detail": "end_time must be after start_time"
}
```

---

### No Data Found

**Error:** No metrics in specified range
**Response:** `200 OK` with empty arrays
```json
{
  "timestamps": [],
  "cpu": { "usage": [] },
  ...
}
```

**Frontend Behavior:** Show "No data available for this time range"

---

### Database Timeout

**Error:** Query takes > 30 seconds
**Response:** `504 Gateway Timeout`
**Frontend Behavior:** Show error message, suggest shorter time range

---

## Testing Historical Queries

### Manual Testing

```bash
# Query last hour
curl "http://localhost:8000/api/history/metrics?start_time=2026-01-21T09:00:00Z&end_time=2026-01-21T10:00:00Z" \
  -H "Authorization: Bearer <JWT>"

# Compare two periods
curl "http://localhost:8000/api/history/compare?start_time_1=2026-01-14T00:00:00Z&end_time_1=2026-01-14T23:59:59Z&start_time_2=2026-01-21T00:00:00Z&end_time_2=2026-01-21T23:59:59Z" \
  -H "Authorization: Bearer <JWT>"
```

---

### Automated Tests

```python
# backend/tests/test_history.py
async def test_get_metrics_success(client, auth_headers, db_session):
    # Create test data
    now = datetime.utcnow()
    snapshot = MetricsSnapshot(
        timestamp=now,
        metric_type="aggregated",
        metric_data={"cpu": {"usage_percent": 50}}
    )
    db_session.add(snapshot)
    await db_session.commit()

    # Query
    response = await client.get(
        f"/api/history/metrics?start_time={now.isoformat()}&end_time={now.isoformat()}",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert len(response.json()["timestamps"]) == 1

async def test_compare_periods(client, auth_headers):
    response = await client.get(
        "/api/history/compare?start_time_1=...&end_time_1=...&start_time_2=...&end_time_2=...",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert "period1" in response.json()
    assert "period2" in response.json()
    assert "diff" in response.json()
```

---

**Navigation:**
- [← Previous: WebSocket](./websocket.md)
- [Next: Retention Cleanup →](./retention.md)
- [↑ Diagrams Index](../../README.md)
