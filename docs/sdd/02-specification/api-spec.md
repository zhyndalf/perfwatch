# PerfWatch API Specification

> REST API and WebSocket endpoint definitions

---

## Base URL

- **Development**: `http://localhost:8000/api`
- **WebSocket**: `ws://localhost:8000/api/ws`

---

## Authentication

### POST /auth/login
Authenticate user and receive JWT token.

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

**Response** (401 Unauthorized):
```json
{
  "detail": "Invalid username or password"
}
```

---

### POST /auth/logout
Invalidate current session (optional - JWT is stateless).

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

### GET /auth/me
Get current user information.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "admin",
  "created_at": "2025-01-18T10:00:00Z",
  "last_login": "2025-01-18T14:30:00Z"
}
```

---

### PUT /auth/password
Change user password.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "current_password": "admin123",
  "new_password": "newSecurePassword123"
}
```

**Response** (200 OK):
```json
{
  "message": "Password updated successfully"
}
```

---

## Real-time Metrics

### WS /ws/metrics
WebSocket endpoint for real-time metric streaming.

**Connection**: `ws://localhost:8000/api/ws/metrics?token=<jwt_token>`

**Server Messages** (every 5 seconds):
```json
{
  "type": "metrics",
  "timestamp": "2025-01-18T14:30:05Z",
  "data": {
    "cpu": {
      "usage_percent": 45.2,
      "per_core": [40.1, 50.3, 42.8, 47.6],
      "user": 30.5,
      "system": 14.7,
      "idle": 54.8,
      "iowait": 0.0,
      "frequency_mhz": [3200, 3150, 3180, 3210],
      "temperature_celsius": [65, 67, 64, 66],
      "interrupts": 125840
    },
    "memory": {
      "usage_percent": 62.4,
      "total_bytes": 17179869184,
      "used_bytes": 10724843520,
      "available_bytes": 6455025664,
      "cached_bytes": 3221225472,
      "buffers_bytes": 536870912,
      "swap_used_bytes": 0,
      "swap_total_bytes": 8589934592,
      "hugepages_total": 0,
      "hugepages_free": 0
    },
    "network": {
      "interfaces": {
        "eth0": {
          "bytes_sent_per_sec": 125000,
          "bytes_recv_per_sec": 450000,
          "packets_sent_per_sec": 150,
          "packets_recv_per_sec": 400
        }
      },
      "connections": {
        "established": 45,
        "time_wait": 12,
        "listen": 8
      }
    },
    "disk": {
      "devices": {
        "sda": {
          "read_bytes_per_sec": 5242880,
          "write_bytes_per_sec": 1048576,
          "read_iops": 150,
          "write_iops": 30,
          "read_latency_ms": 0.5,
          "write_latency_ms": 1.2
        }
      },
      "partitions": {
        "/": {
          "total_bytes": 512000000000,
          "used_bytes": 256000000000,
          "usage_percent": 50.0
        }
      }
    },
    "perf": {
      "available": true,
      "ipc": 1.85,
      "cycles": 3200000000,
      "instructions": 5920000000,
      "l1i_cache_misses": 12500,
      "l1d_cache_misses": 45000,
      "l2_cache_misses": 8000,
      "llc_misses": 2500,
      "memory_bandwidth_read_mbps": 12500,
      "memory_bandwidth_write_mbps": 8000
    }
  }
}
```

**Client Messages**:
```json
{
  "type": "ping"
}
```

**Server Ping Response**:
```json
{
  "type": "pong"
}
```

---

## Historical Data

### GET /history/metrics
Query historical metric data.

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| metric_type | string | Yes | cpu, memory, network, disk, perf |
| start_time | ISO datetime | Yes | Start of time range |
| end_time | ISO datetime | Yes | End of time range |
| interval | string | No | Aggregation interval: 5s, 1m, 5m, 1h (default: auto) |

**Example**:
```
GET /history/metrics?metric_type=cpu&start_time=2025-01-18T10:00:00Z&end_time=2025-01-18T14:00:00Z&interval=1m
```

**Response** (200 OK):
```json
{
  "metric_type": "cpu",
  "start_time": "2025-01-18T10:00:00Z",
  "end_time": "2025-01-18T14:00:00Z",
  "interval": "1m",
  "data_points": [
    {
      "timestamp": "2025-01-18T10:00:00Z",
      "data": {
        "usage_percent": 45.2,
        "user": 30.5,
        "system": 14.7
      }
    },
    {
      "timestamp": "2025-01-18T10:01:00Z",
      "data": {
        "usage_percent": 48.1,
        "user": 32.0,
        "system": 16.1
      }
    }
  ]
}
```

---

### GET /history/metrics/types
Get list of available metric types for historical queries.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "metric_types": [
    "cpu",
    "disk",
    "memory",
    "memory_bandwidth",
    "network",
    "perf_events"
  ]
}
```

---

### GET /history/compare
Compare metrics between two time periods. Supports both relative comparison (period + compare_to) and custom range comparison (explicit timestamps).

**Headers**: `Authorization: Bearer <token>`

**Query Parameters**:

**Mode 1: Relative Comparison**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| metric_type | string | Yes | cpu, memory, network, disk, perf_events, memory_bandwidth |
| period | string | Yes (Mode 1) | hour, day, week |
| compare_to | string | Yes (Mode 1) | yesterday, last_week |
| limit | int | No | Maximum results per period (default: 1000, max: 10000) |
| interval | string | No | Aggregation interval: 5s, 1m, 5m, 1h, auto (default: auto) |

**Mode 2: Custom Range Comparison**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| metric_type | string | Yes | cpu, memory, network, disk, perf_events, memory_bandwidth |
| start_time_1 | ISO datetime | Yes (Mode 2) | Period 1 start time |
| end_time_1 | ISO datetime | Yes (Mode 2) | Period 1 end time |
| start_time_2 | ISO datetime | Yes (Mode 2) | Period 2 start time |
| end_time_2 | ISO datetime | Yes (Mode 2) | Period 2 end time |
| limit | int | No | Maximum results per period (default: 1000, max: 10000) |
| interval | string | No | Aggregation interval: 5s, 1m, 5m, 1h, auto (default: auto) |

**Note**: All 4 custom range parameters (start_time_1, end_time_1, start_time_2, end_time_2) must be provided together. Both periods must have the same duration.

**Example (Relative)**:
```
GET /history/compare?metric_type=cpu&period=hour&compare_to=yesterday
```

**Example (Custom Range)**:
```
GET /history/compare?metric_type=cpu&start_time_1=2026-01-20T10:00:00Z&end_time_1=2026-01-20T12:00:00Z&start_time_2=2026-01-21T10:00:00Z&end_time_2=2026-01-21T12:00:00Z
```

**Response** (200 OK):
```json
{
  "metric_type": "cpu",
  "period": "hour",
  "compare_to": "yesterday",
  "interval": "1m",
  "current": {
    "start_time": "2026-01-21T14:00:00Z",
    "end_time": "2026-01-21T15:00:00Z",
    "data_points": [
      {
        "timestamp": "2026-01-21T14:00:00Z",
        "data": {
          "usage_percent": 52.3,
          "user": 35.2,
          "system": 17.1
        }
      }
    ]
  },
  "comparison": {
    "start_time": "2026-01-20T14:00:00Z",
    "end_time": "2026-01-20T15:00:00Z",
    "data_points": [
      {
        "timestamp": "2026-01-20T14:00:00Z",
        "data": {
          "usage_percent": 45.8,
          "user": 30.1,
          "system": 15.7
        }
      }
    ]
  },
  "summary": {
    "current_avg": 52.3,
    "comparison_avg": 45.8,
    "change_percent": 14.2
  }
}
```

---

## Configuration

### GET /config
Get current configuration.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "sampling_interval_seconds": 5,
  "retention_days": 30,
  "archive_enabled": true,
  "downsample_after_days": 7,
  "downsample_interval": "1h"
}
```

---

### PUT /config
Update configuration.

**Headers**: `Authorization: Bearer <token>`

**Request Body**:
```json
{
  "retention_days": 60,
  "archive_enabled": true
}
```

**Response** (200 OK):
```json
{
  "message": "Configuration updated",
  "config": {
    "sampling_interval_seconds": 5,
    "retention_days": 60,
    "archive_enabled": true,
    "downsample_after_days": 7,
    "downsample_interval": "1h"
  }
}
```

---

### GET /config/retention
Get retention policy details.

**Headers**: `Authorization: Bearer <token>`

**Response** (200 OK):
```json
{
  "retention_days": 30,
  "archive_enabled": true,
  "downsample_after_days": 7,
  "downsample_interval": "1h",
  "current_data_size_mb": 256,
  "oldest_record": "2024-12-18T10:00:00Z",
  "newest_record": "2025-01-18T14:30:00Z"
}
```

---

## Error Responses

All endpoints may return these error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid parameter value"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized to perform this action"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error",
  "error_id": "abc123"
}
```

---

## Rate Limiting

No rate limiting implemented for local deployment.
Future consideration for multi-user scenarios.

---

## Versioning

API is not versioned in v1.0. Future breaking changes would require `/api/v2/` prefix.
