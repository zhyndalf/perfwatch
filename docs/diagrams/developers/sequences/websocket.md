# WebSocket Metrics Flow Sequence Diagram

> **Real-time metrics streaming via WebSocket**

This diagram shows the complete WebSocket lifecycle from connection establishment to real-time metrics broadcasting.

---

## WebSocket Connection Establishment

```mermaid
sequenceDiagram
    participant DashView as Dashboard.vue
    participant MetricsStore as metricsStore
    participant WSClient as WebSocket Client
    participant Backend as FastAPI Backend
    participant WSAPI as websocket.py
    participant AuthDep as get_current_user_ws
    participant DB as PostgreSQL

    DashView->>MetricsStore: connect() (on mount)
    activate MetricsStore

    MetricsStore->>MetricsStore: token = authStore.token
    MetricsStore->>WSClient: new WebSocket(url + ?token=JWT)
    activate WSClient

    WSClient->>Backend: ws://localhost:8000/api/ws/metrics?token=JWT
    activate Backend

    Backend->>WSAPI: websocket_endpoint(websocket, token)
    activate WSAPI

    WSAPI->>AuthDep: Validate JWT token
    activate AuthDep

    AuthDep->>AuthDep: decode_jwt(token)

    alt Invalid or expired token
        AuthDep-->>WSAPI: 401 Unauthorized
        WSAPI->>WSClient: Close connection with 1008 code
        WSClient-->>MetricsStore: onclose event
        MetricsStore->>MetricsStore: connectionState = 'error'
        MetricsStore-->>DashView: Update UI: "Authentication failed"
    else Valid token
        AuthDep->>DB: SELECT * FROM users WHERE id = ?
        DB-->>AuthDep: User object
        AuthDep-->>WSAPI: User validated ✅
        deactivate AuthDep

        WSAPI->>WSAPI: await websocket.accept()
        WSAPI->>WSAPI: manager.connect(websocket)
        Note over WSAPI: Add to active connections list

        WSAPI-->>Backend: Connection established
        Backend-->>WSClient: WebSocket handshake complete (101 Switching Protocols)
        deactivate Backend

        WSClient-->>MetricsStore: onopen event
        MetricsStore->>MetricsStore: connectionState = 'connected'
        MetricsStore-->>DashView: Update UI: "Connected ✅"
        deactivate MetricsStore
        deactivate WSClient
    end
```

---

## Background Metrics Collection Loop

```mermaid
sequenceDiagram
    participant BGTask as Background Task<br/>(asyncio loop)
    participant Aggregator as MetricsAggregator
    participant Collectors as 6 Collectors
    participant LinuxKernel as Linux Kernel
    participant BatchWriter as BatchMetricsWriter
    participant DB as PostgreSQL
    participant WSManager as WebSocket Manager
    participant Clients as Connected Clients

    loop Every 5 seconds
        BGTask->>Aggregator: collect_all()
        activate Aggregator

        par Collect from all collectors
            Aggregator->>Collectors: cpu_collector.safe_collect()
            activate Collectors
            Collectors->>LinuxKernel: psutil.cpu_percent()
            LinuxKernel-->>Collectors: CPU usage data
            Collectors-->>Aggregator: { usage: 45.2, ... }
            deactivate Collectors

            Aggregator->>Collectors: memory_collector.safe_collect()
            activate Collectors
            Collectors->>LinuxKernel: psutil.virtual_memory()
            LinuxKernel-->>Collectors: Memory data
            Collectors-->>Aggregator: { total: 16GB, ... }
            deactivate Collectors

            Aggregator->>Collectors: network_collector.safe_collect()
            activate Collectors
            Collectors->>LinuxKernel: psutil.net_io_counters()
            LinuxKernel-->>Collectors: Network I/O data
            Collectors-->>Aggregator: { bytes_sent: 1024, ... }
            deactivate Collectors

            Aggregator->>Collectors: disk_collector.safe_collect()
            activate Collectors
            Collectors->>LinuxKernel: psutil.disk_io_counters()
            LinuxKernel-->>Collectors: Disk I/O data
            Collectors-->>Aggregator: { read_bytes: 2048, ... }
            deactivate Collectors

            Aggregator->>Collectors: perf_events_collector.safe_collect()
            activate Collectors
            Collectors->>LinuxKernel: perf stat subprocess
            alt perf stat available
                LinuxKernel-->>Collectors: Hardware counters
                Collectors-->>Aggregator: { available: true, events: {...} }
            else Permission denied or PMU missing
                Collectors-->>Aggregator: { available: false, error: "perf stat unavailable" }
            end
            deactivate Collectors

            Aggregator->>Collectors: memory_bandwidth_collector.safe_collect()
            activate Collectors
            Collectors->>LinuxKernel: Read /proc/vmstat
            LinuxKernel-->>Collectors: Page I/O stats
            Collectors-->>Aggregator: { pgpgin: 100, ... }
            deactivate Collectors
        end

        Aggregator->>Aggregator: Combine all results
        Note over Aggregator: Create unified snapshot:<br/>{ cpu: {...}, memory: {...}, ... }

        Aggregator-->>BGTask: metrics_snapshot
        deactivate Aggregator

        par Persist + Broadcast
            BGTask->>BatchWriter: queue(snapshot)
            activate BatchWriter
            BatchWriter->>BatchWriter: Add to batch queue
            alt Queue size >= batch_size (10)
                BatchWriter->>DB: INSERT INTO metrics_snapshots (bulk)
                DB-->>BatchWriter: Inserted
            end
            BatchWriter-->>BGTask: Queued
            deactivate BatchWriter

            BGTask->>WSManager: broadcast(snapshot)
            activate WSManager
            loop For each connected client
                WSManager->>Clients: send_json(snapshot)
                Clients-->>WSManager: Received
            end
            WSManager-->>BGTask: Broadcast complete
            deactivate WSManager
        end

        BGTask->>BGTask: await asyncio.sleep(5)
    end
```

---

## Client Receiving Metrics

```mermaid
sequenceDiagram
    participant WSClient as WebSocket Client
    participant MetricsStore as metricsStore
    participant DashView as Dashboard.vue
    participant ECharts as ECharts Components

    WSClient->>WSClient: onmessage event
    activate WSClient

    WSClient->>WSClient: Parse JSON message
    Note over WSClient: { cpu: {...}, memory: {...}, ... }

    WSClient->>MetricsStore: handleMessage(data)
    activate MetricsStore

    MetricsStore->>MetricsStore: Update currentMetrics state
    MetricsStore->>MetricsStore: Update lastUpdateTime
    MetricsStore->>MetricsStore: connectionState = 'connected'

    MetricsStore-->>WSClient: State updated
    deactivate WSClient

    Note over MetricsStore,DashView: Vue reactivity triggers re-render

    MetricsStore-->>DashView: Reactive state change
    activate DashView

    DashView->>DashView: Computed properties recalculate
    DashView->>ECharts: Update CPU chart
    DashView->>ECharts: Update Memory chart
    DashView->>ECharts: Update Network chart
    DashView->>ECharts: Update Disk chart
    DashView->>ECharts: Update Perf chart
    DashView->>ECharts: Update Bandwidth chart

    ECharts-->>DashView: Charts updated ✅
    deactivate DashView

    DashView-->>MetricsStore: Render complete
    deactivate MetricsStore
```

---

## WebSocket Disconnection & Reconnection

```mermaid
sequenceDiagram
    participant WSClient as WebSocket Client
    participant MetricsStore as metricsStore
    participant DashView as Dashboard.vue
    participant Backend as FastAPI Backend

    Backend->>WSClient: Connection lost (network error)
    activate WSClient

    WSClient->>WSClient: onclose event
    WSClient->>MetricsStore: handleClose()
    activate MetricsStore

    MetricsStore->>MetricsStore: connectionState = 'disconnected'
    MetricsStore-->>DashView: Update UI: "Disconnected ⚠️"

    alt Auto-reconnect enabled
        MetricsStore->>MetricsStore: reconnectAttempts++
        MetricsStore->>MetricsStore: setTimeout(reconnect, delay)
        Note over MetricsStore: Exponential backoff:<br/>1s, 2s, 4s, 8s, ...

        loop Retry until success or max attempts
            MetricsStore->>MetricsStore: connectionState = 'connecting'
            MetricsStore-->>DashView: Update UI: "Reconnecting..."

            MetricsStore->>WSClient: new WebSocket(url + ?token=JWT)
            WSClient->>Backend: ws://localhost:8000/api/ws/metrics?token=JWT

            alt Reconnect successful
                Backend-->>WSClient: 101 Switching Protocols
                WSClient->>MetricsStore: onopen event
                MetricsStore->>MetricsStore: connectionState = 'connected'
                MetricsStore->>MetricsStore: reconnectAttempts = 0
                MetricsStore-->>DashView: Update UI: "Connected ✅"
                Note over MetricsStore: Exit retry loop
            else Reconnect failed
                Backend-->>WSClient: Connection refused
                WSClient->>MetricsStore: onerror event
                MetricsStore->>MetricsStore: reconnectAttempts++
                alt reconnectAttempts < maxAttempts (10)
                    MetricsStore->>MetricsStore: setTimeout(reconnect, delay)
                    Note over MetricsStore: Wait longer before retry
                else Max attempts reached
                    MetricsStore->>MetricsStore: connectionState = 'error'
                    MetricsStore-->>DashView: Update UI: "Failed to reconnect ❌"
                    Note over MetricsStore: Stop retrying
                end
            end
        end
    else Auto-reconnect disabled
        MetricsStore-->>DashView: Update UI: "Disconnected ⚠️"
        Note over DashView: Show "Retry" button
    end

    deactivate MetricsStore
    deactivate WSClient
```

---

## Client Disconnect (User Navigates Away)

```mermaid
sequenceDiagram
    actor User
    participant DashView as Dashboard.vue
    participant MetricsStore as metricsStore
    participant WSClient as WebSocket Client
    participant Backend as FastAPI Backend
    participant WSAPI as websocket.py

    User->>DashView: Navigate to /history
    activate DashView

    DashView->>DashView: onBeforeUnmount lifecycle hook
    DashView->>MetricsStore: disconnect()
    activate MetricsStore

    MetricsStore->>WSClient: close()
    activate WSClient

    WSClient->>Backend: Close WebSocket (code 1000)
    activate Backend

    Backend->>WSAPI: Connection closed
    activate WSAPI

    WSAPI->>WSAPI: manager.disconnect(websocket)
    Note over WSAPI: Remove from active connections list

    WSAPI->>WSAPI: Log: "Client disconnected"
    WSAPI-->>Backend: Cleanup complete
    deactivate WSAPI
    deactivate Backend

    WSClient-->>MetricsStore: onclose event
    deactivate WSClient

    MetricsStore->>MetricsStore: connectionState = 'disconnected'
    MetricsStore->>MetricsStore: Clear currentMetrics
    MetricsStore-->>DashView: Disconnected
    deactivate MetricsStore

    DashView-->>User: Navigate to History page
    deactivate DashView
```

---

## Batch Writer Flush

```mermaid
sequenceDiagram
    participant BGTask as Background Task
    participant BatchWriter as BatchMetricsWriter
    participant DB as PostgreSQL

    loop Every 5 seconds
        BGTask->>BatchWriter: queue(snapshot)
        activate BatchWriter

        BatchWriter->>BatchWriter: batch.append(snapshot)
        BatchWriter->>BatchWriter: Check batch size

        alt Batch size >= 10
            BatchWriter->>BatchWriter: Prepare bulk INSERT
            Note over BatchWriter: INSERT INTO metrics_snapshots<br/>(timestamp, metric_type, metric_data)<br/>VALUES (...), (...), ... (10 rows)

            BatchWriter->>DB: Execute bulk INSERT
            activate DB
            DB->>DB: Insert 10 rows in single transaction
            DB-->>BatchWriter: Rows inserted
            deactivate DB

            BatchWriter->>BatchWriter: Clear batch queue
            BatchWriter->>BatchWriter: Log: "Inserted 10 snapshots"
        else Batch size < 10
            Note over BatchWriter: Keep in queue,<br/>wait for more snapshots
        end

        BatchWriter-->>BGTask: Queued/Flushed
        deactivate BatchWriter
    end

    Note over BatchWriter,DB: On shutdown: Flush remaining batch
```

---

## WebSocket Manager Implementation

```python
# backend/app/api/websocket.py
from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        for connection in self.active_connections[:]:  # Copy to avoid modification during iteration
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send to client: {e}")
                self.disconnect(connection)

manager = ConnectionManager()
```

---

## WebSocket Endpoint Implementation

```python
# backend/app/api/websocket.py
from fastapi import WebSocket, Query, HTTPException
from app.api.deps import get_current_user_ws

@router.websocket("/ws/metrics")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),  # JWT in query param (browsers can't set WS headers)
):
    # Validate token
    user = await get_current_user_ws(token)
    if not user:
        await websocket.close(code=1008)  # Policy violation (auth failed)
        return

    # Accept connection
    await manager.connect(websocket)

    try:
        # Keep connection alive, wait for client close
        while True:
            data = await websocket.receive_text()  # Ping/pong or client messages
            # Echo back or ignore (client doesn't send data in this design)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

---

## Frontend WebSocket Client

```javascript
// frontend/src/stores/metrics.js
import { defineStore } from 'pinia'
import { useAuthStore } from './auth'

export const useMetricsStore = defineStore('metrics', {
  state: () => ({
    ws: null,
    currentMetrics: null,
    connectionState: 'disconnected',  // disconnected, connecting, connected, error
    reconnectAttempts: 0,
    maxReconnectAttempts: 10
  }),

  actions: {
    connect() {
      const authStore = useAuthStore()
      if (!authStore.token) {
        console.error('No auth token available')
        return
      }

      this.connectionState = 'connecting'
      const wsUrl = `ws://localhost:8000/api/ws/metrics?token=${authStore.token}`
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        this.connectionState = 'connected'
        this.reconnectAttempts = 0
        console.log('WebSocket connected')
      }

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.currentMetrics = data
        this.lastUpdateTime = new Date()
      }

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        this.connectionState = 'error'
      }

      this.ws.onclose = () => {
        this.connectionState = 'disconnected'
        console.log('WebSocket disconnected')
        this.attemptReconnect()
      }
    },

    disconnect() {
      if (this.ws) {
        this.ws.close()
        this.ws = null
      }
      this.connectionState = 'disconnected'
    },

    attemptReconnect() {
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.connectionState = 'error'
        console.error('Max reconnect attempts reached')
        return
      }

      this.reconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000)  // Exponential backoff, max 30s
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)

      setTimeout(() => {
        this.connect()
      }, delay)
    }
  }
})
```

---

## Performance Considerations

### Backend

**Collection Interval:**
- 5 seconds (configurable via `SAMPLING_INTERVAL_SECONDS`)
- Balance between real-time updates and system overhead
- Too fast: High CPU usage from collectors
- Too slow: Missed transient spikes

**Batch Writing:**
- Queue size: 10 snapshots (50 seconds of data)
- Reduces database write overhead by 90%
- Trade-off: 50s delay in database (WebSocket still real-time)

**Concurrent Connections:**
- Single user design: Max 1-2 concurrent connections
- Manager can handle 100+ connections if needed
- No broadcasting optimization (small message size)

---

### Frontend

**WebSocket Message Size:**
- ~2 KB per snapshot (JSON)
- 5-second interval = 0.4 KB/s bandwidth
- Negligible network overhead

**ECharts Updates:**
- Vue reactivity triggers chart updates
- ECharts efficiently handles incremental data
- 60 FPS rendering (no noticeable lag)

**Reconnection Strategy:**
- Exponential backoff: 1s, 2s, 4s, 8s, ... up to 30s
- Max 10 attempts before giving up
- Prevents connection spam on backend

---

## Error Scenarios

### Backend Crashes

**Symptom:** All WebSocket connections close
**Client Behavior:** Auto-reconnect after backend restarts
**Data Loss:** Metrics during downtime not collected

### Database Unavailable

**Symptom:** Metrics collection continues, but writes fail
**Client Behavior:** WebSocket still delivers real-time data
**Data Loss:** Metrics not persisted (no historical data)

### Invalid JWT Token

**Symptom:** WebSocket connection rejected with 1008 code
**Client Behavior:** Redirect to login, clear token
**User Action:** Re-authenticate

### Collector Failure

**Symptom:** perf_events returns `available: false` (perf stat permission denied)
**Client Behavior:** UI shows "Hardware Performance Counters Unavailable"
**System Behavior:** Other collectors continue normally (graceful degradation)

---

## Testing WebSocket Flow

### Manual Testing with wscat

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket (replace with valid JWT)
wscat -c "ws://localhost:8000/api/ws/metrics?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Should receive JSON metrics every 5 seconds
```

---

### Automated Tests

```python
# backend/tests/test_websocket.py
async def test_websocket_connection(client, auth_headers):
    token = auth_headers["Authorization"].split(" ")[1]
    async with client.websocket_connect(f"/api/ws/metrics?token={token}") as ws:
        data = await ws.receive_json()
        assert "cpu" in data
        assert "memory" in data
        assert "timestamp" in data

async def test_websocket_invalid_token(client):
    with pytest.raises(WebSocketDisconnect):
        async with client.websocket_connect("/api/ws/metrics?token=invalid"):
            pass
```

---

**Navigation:**
- [← Previous: Authentication](./authentication.md)
- [Next: Historical Queries →](./historical-query.md)
- [↑ Diagrams Index](../../README.md)
