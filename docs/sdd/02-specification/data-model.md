# PerfWatch Data Model

> Database schema and SQLAlchemy models

---

## Database: PostgreSQL 15

### Connection
```
postgresql+asyncpg://perfwatch:perfwatch@db:5432/perfwatch
```

---

## Tables Overview

| Table | Purpose | Key Fields |
|-------|---------|------------|
| users | User authentication | id, username, password_hash |
| metrics_snapshot | Time-series metrics data | id, timestamp, metric_type, metric_data |
| config | Application configuration | key, value |
| archive_policy | Data retention settings | retention_days, downsample settings |

---

## Table: users

Stores user authentication information.

### Schema
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_users_username ON users(username);
```

### SQLAlchemy Model
```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
```

### Initial Data
```sql
-- Default admin user (password: admin123)
INSERT INTO users (username, password_hash)
VALUES ('admin', '$2b$12$...');  -- bcrypt hash
```

---

## Table: metrics_snapshot

Stores all collected metrics as JSONB for flexibility.

### Schema
```sql
CREATE TABLE metrics_snapshot (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    metric_data JSONB NOT NULL
);

-- Indexes for query performance
CREATE INDEX idx_metrics_timestamp ON metrics_snapshot(timestamp);
CREATE INDEX idx_metrics_type_timestamp ON metrics_snapshot(metric_type, timestamp);

-- Optional: Partition by time for better performance with large datasets
-- CREATE TABLE metrics_snapshot_2025_01 PARTITION OF metrics_snapshot
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
```

### SQLAlchemy Model
```python
class MetricsSnapshot(Base):
    __tablename__ = "metrics_snapshot"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True
    )
    metric_type: Mapped[str] = mapped_column(String(50), nullable=False)
    metric_data: Mapped[dict] = mapped_column(JSONB, nullable=False)

    __table_args__ = (
        Index('idx_metrics_type_timestamp', 'metric_type', 'timestamp'),
    )
```

### Metric Types
| Type | Description | Data Structure |
|------|-------------|----------------|
| cpu | CPU metrics | See CPU JSONB structure |
| memory | Memory metrics | See Memory JSONB structure |
| network | Network metrics | See Network JSONB structure |
| disk | Disk I/O metrics | See Disk JSONB structure |
| perf_events | perf stat data | See Perf JSONB structure |

### CPU JSONB Structure
```json
{
  "usage_percent": 45.2,
  "per_core": [40.1, 50.3, 42.8, 47.6],
  "user": 30.5,
  "system": 14.7,
  "idle": 54.8,
  "iowait": 0.0,
  "irq": 0.0,
  "softirq": 0.0,
  "frequency_mhz": [3200, 3150, 3180, 3210],
  "temperature_celsius": [65, 67, 64, 66],
  "interrupts": 125840
}
```

### Memory JSONB Structure
```json
{
  "usage_percent": 62.4,
  "total_bytes": 17179869184,
  "used_bytes": 10724843520,
  "available_bytes": 6455025664,
  "free_bytes": 2147483648,
  "cached_bytes": 3221225472,
  "buffers_bytes": 536870912,
  "swap_total_bytes": 8589934592,
  "swap_used_bytes": 0,
  "swap_free_bytes": 8589934592,
  "hugepages_total": 0,
  "hugepages_free": 0,
  "hugepages_reserved": 0
}
```

### Network JSONB Structure
```json
{
  "interfaces": {
    "eth0": {
      "bytes_sent": 125000000,
      "bytes_recv": 450000000,
      "bytes_sent_per_sec": 125000,
      "bytes_recv_per_sec": 450000,
      "packets_sent": 150000,
      "packets_recv": 400000,
      "packets_sent_per_sec": 150,
      "packets_recv_per_sec": 400,
      "errors_in": 0,
      "errors_out": 0,
      "drops_in": 0,
      "drops_out": 0
    }
  },
  "connections": {
    "tcp": {
      "established": 45,
      "time_wait": 12,
      "close_wait": 0,
      "listen": 8
    },
    "udp": {
      "count": 15
    }
  }
}
```

### Disk JSONB Structure
```json
{
  "devices": {
    "sda": {
      "read_bytes": 5242880000,
      "write_bytes": 1048576000,
      "read_bytes_per_sec": 5242880,
      "write_bytes_per_sec": 1048576,
      "read_count": 150000,
      "write_count": 30000,
      "read_iops": 150,
      "write_iops": 30,
      "read_time_ms": 75000,
      "write_time_ms": 36000,
      "read_latency_ms": 0.5,
      "write_latency_ms": 1.2
    }
  },
  "partitions": {
    "/": {
      "device": "/dev/sda1",
      "fstype": "ext4",
      "total_bytes": 512000000000,
      "used_bytes": 256000000000,
      "free_bytes": 256000000000,
      "usage_percent": 50.0
    },
    "/home": {
      "device": "/dev/sda2",
      "fstype": "ext4",
      "total_bytes": 1000000000000,
      "used_bytes": 400000000000,
      "free_bytes": 600000000000,
      "usage_percent": 40.0
    }
  }
}
```

### Perf JSONB Structure
```json
{
  "available": true,
  "cpu_cores": "all",
  "interval_ms": 1000,
  "sample_time": "1.000000000",
  "events": {
    "cpu-clock": { "value": 1012.3, "unit": "msec" },
    "context-switches": { "value": 120, "unit": null },
    "cpu-migrations": { "value": 3, "unit": null },
    "page-faults": { "value": 456, "unit": null },
    "cycles": { "value": 3200000000, "unit": null },
    "instructions": { "value": 5920000000, "unit": null },
    "branches": { "value": 1800000000, "unit": null },
    "branch-misses": { "value": 12000000, "unit": null },
    "L1-dcache-loads": { "value": 5000000, "unit": null },
    "L1-dcache-load-misses": { "value": 45000, "unit": null },
    "LLC-loads": { "value": 8000, "unit": null },
    "LLC-load-misses": { "value": 2500, "unit": null },
    "L1-icache-loads": { "value": 1000000, "unit": null },
    "dTLB-loads": { "value": 3000000, "unit": null },
    "dTLB-load-misses": { "value": 3000, "unit": null },
    "iTLB-loads": { "value": 1800000, "unit": null },
    "iTLB-load-misses": { "value": 2500, "unit": null }
  },
  "missing_events": [],
  "unsupported_events": []
}
```

---

## Table: config

Key-value store for application configuration.

### Schema
```sql
CREATE TABLE config (
    key VARCHAR(100) PRIMARY KEY,
    value JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### SQLAlchemy Model
```python
class Config(Base):
    __tablename__ = "config"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[dict] = mapped_column(JSONB, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
```

### Default Configuration
```sql
INSERT INTO config (key, value) VALUES
('sampling', '{"interval_seconds": 5}'),
('retention', '{"days": 30, "archive_enabled": true, "downsample_after_days": 7, "downsample_interval": "1h"}'),
('features', '{"perf_events_enabled": true, "perf_events_cpu_cores": "all", "perf_events_interval_ms": 1000}');
```

---

## Table: archive_policy

Detailed retention policy settings.

### Schema
```sql
CREATE TABLE archive_policy (
    id SERIAL PRIMARY KEY,
    retention_days INTEGER NOT NULL DEFAULT 30,
    archive_enabled BOOLEAN DEFAULT true,
    downsample_after_days INTEGER DEFAULT 7,
    downsample_interval VARCHAR(20) DEFAULT '1 hour',
    last_archive_run TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### SQLAlchemy Model
```python
class ArchivePolicy(Base):
    __tablename__ = "archive_policy"

    id: Mapped[int] = mapped_column(primary_key=True)
    retention_days: Mapped[int] = mapped_column(default=30)
    archive_enabled: Mapped[bool] = mapped_column(default=True)
    downsample_after_days: Mapped[int] = mapped_column(default=7)
    downsample_interval: Mapped[str] = mapped_column(String(20), default="1 hour")
    last_archive_run: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
```

---

## Pydantic Schemas

### User Schemas
```python
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
```

### Metrics Schemas
```python
class MetricsSnapshotCreate(BaseModel):
    timestamp: datetime
    metric_type: str
    metric_data: dict

class MetricsSnapshotResponse(BaseModel):
    id: int
    timestamp: datetime
    metric_type: str
    metric_data: dict

    class Config:
        from_attributes = True

class HistoryQuery(BaseModel):
    metric_type: str
    start_time: datetime
    end_time: datetime
    interval: Optional[str] = None
```

---

## Database Migrations (Alembic)

### Directory Structure
```
backend/
├── alembic.ini
└── alembic/
    ├── env.py
    ├── script.py.mako
    └── versions/
        ├── 001_initial_schema.py
        └── ...
```

### Example Migration
```python
# 001_initial_schema.py
def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('username', sa.String(50), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True)
    )
    # ... other tables

def downgrade():
    op.drop_table('users')
    # ... other tables
```

---

## Data Volume Estimates

| Scenario | Data per Day | Data per Month |
|----------|--------------|----------------|
| 5s interval, all metrics | ~50 MB | ~1.5 GB |
| 5s interval, downsampled to 1h after 7 days | ~15 MB | ~450 MB |

### Storage Optimization
1. JSONB compression (automatic in PostgreSQL)
2. Downsampling old data (5s → 1h averages)
3. Configurable retention period
4. Partition by month for large deployments
