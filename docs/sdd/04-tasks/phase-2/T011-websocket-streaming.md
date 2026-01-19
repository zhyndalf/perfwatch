# T011: WebSocket Streaming

> **Status**: IN_PROGRESS
> **Phase**: 2 - Core Metrics
> **Estimated Time**: 2-3 hours

---

## Objective

Implement WebSocket endpoint for real-time metrics streaming from backend to frontend.

---

## Requirements

1. Create WebSocket endpoint at `/api/ws/metrics`
2. Authenticate connections via JWT token in query parameter
3. Stream metrics every 5 seconds using MetricsAggregator
4. Support multiple simultaneous client connections
5. Handle ping/pong for connection keep-alive

---

## Implementation Status

### Completed ✅

1. **WebSocket Endpoint** (`backend/app/api/websocket.py`)
   - Created `/api/ws/metrics` endpoint
   - JWT authentication via `?token=<jwt>` query parameter
   - Returns 4001 close code if authentication fails

2. **ConnectionManager Class**
   - Manages multiple WebSocket connections
   - Thread-safe with asyncio Lock
   - Broadcast method sends to all connected clients
   - Automatic cleanup of failed connections

3. **MetricsAggregator Integration**
   - Lazy initialization on first client connection
   - 5-second collection interval
   - Stops when no clients connected (resource optimization)
   - Collects from: CPU, Memory, Network, Disk collectors

4. **Router Registration**
   - Added `websocket_router` to `main.py`

### Pending ⏳

1. **Unit Tests** (`backend/tests/test_websocket.py`)
   - Test authentication (valid/invalid/missing token)
   - Test metrics broadcast format
   - Test ping/pong handling
   - Test connection manager

2. **Documentation Updates**
   - Update README.md
   - Update PROGRESS.md

---

## Key Files

| File | Status | Description |
|------|--------|-------------|
| `backend/app/api/websocket.py` | ✅ Created | WebSocket endpoint and ConnectionManager |
| `backend/app/main.py` | ✅ Modified | Router registration |
| `backend/tests/test_websocket.py` | ⏳ Pending | Unit tests |

---

## API Specification

### Connection
```
ws://localhost:8000/api/ws/metrics?token=<jwt_token>
```

### Server → Client (every 5 seconds)
```json
{
  "type": "metrics",
  "timestamp": "2026-01-19T14:30:05Z",
  "data": {
    "cpu": {
      "usage_percent": 45.2,
      "per_core": [40.1, 50.3, 42.8, 47.6],
      "user": 30.5,
      "system": 14.7,
      "idle": 54.8,
      "frequency_mhz": [3200, 3150],
      "load_avg": [1.5, 1.2, 0.9]
    },
    "memory": {
      "usage_percent": 62.4,
      "total_bytes": 17179869184,
      "used_bytes": 10724843520,
      "available_bytes": 6455025664,
      "swap_percent": 0.0
    },
    "network": {
      "bytes_sent_per_sec": 125000,
      "bytes_recv_per_sec": 450000,
      "interfaces": { ... }
    },
    "disk": {
      "partitions": { ... },
      "io": { ... }
    }
  }
}
```

### Client → Server
```json
{ "type": "ping" }
```

### Server → Client (response)
```json
{ "type": "pong" }
```

---

## Testing Checklist

- [ ] Test WebSocket connection with valid JWT
- [ ] Test WebSocket rejection with invalid JWT
- [ ] Test WebSocket rejection with no token
- [ ] Test metrics message format
- [ ] Test ping/pong handling
- [ ] Test multiple client connections
- [ ] Test connection cleanup on disconnect

---

## Verification

1. Start services: `docker compose up -d`
2. Get JWT token: `curl -X POST http://localhost:8000/api/auth/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'`
3. Test WebSocket with wscat or browser console:
   ```javascript
   const ws = new WebSocket('ws://localhost:8000/api/ws/metrics?token=<jwt>');
   ws.onmessage = (e) => console.log(JSON.parse(e.data));
   ```
4. Should receive metrics every 5 seconds
