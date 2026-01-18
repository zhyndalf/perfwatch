# T003: Database Setup

## Metadata

| Field | Value |
|-------|-------|
| **Phase** | 1 - Foundation |
| **Estimated Time** | 2-3 hours |
| **Dependencies** | T002 (Docker Setup) |
| **Status** | ⬜ NOT_STARTED |

---

## Objective

Configure PostgreSQL database with SQLAlchemy 2.0 async ORM and Alembic migrations.

---

## Context

The database stores:
- User authentication data
- Metric snapshots (time-series with JSONB)
- Application configuration

Using async SQLAlchemy for non-blocking database operations.

---

## Specifications

Reference documents:
- [Data Model](../../02-specification/data-model.md)
- [Architecture](../../02-specification/architecture.md)

---

## Acceptance Criteria

### SQLAlchemy Setup
- [ ] `database.py` with async engine and session
- [ ] Base model class configured
- [ ] Connection pooling appropriate

### Models
- [ ] `User` model with password hash
- [ ] `MetricsSnapshot` model with JSONB
- [ ] `Config` model for settings
- [ ] `ArchivePolicy` model for retention

### Alembic
- [ ] `alembic.ini` configured
- [ ] `env.py` for async migrations
- [ ] Initial migration created
- [ ] Migration runs successfully

### Initialization
- [ ] Default admin user created
- [ ] Default config values set
- [ ] Init script for container startup

---

## Implementation Details

### database.py

```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### User Model

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
```

### MetricsSnapshot Model

```python
from sqlalchemy import Column, BigInteger, String, DateTime, Index
from sqlalchemy.dialects.postgresql import JSONB
from app.database import Base

class MetricsSnapshot(Base):
    __tablename__ = "metrics_snapshot"

    id = Column(BigInteger, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)
    metric_data = Column(JSONB, nullable=False)

    __table_args__ = (
        Index('idx_metrics_type_timestamp', 'metric_type', 'timestamp'),
    )
```

### Alembic env.py (async)

```python
import asyncio
from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base
from app.config import settings

# Import all models
from app.models import user, metrics

def run_migrations_online():
    connectable = create_async_engine(settings.DATABASE_URL)

    async def do_migrations():
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)

    asyncio.run(do_migrations())
```

### Dependencies (pyproject.toml)

```toml
[project]
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
    "sqlalchemy[asyncio]>=2.0.0",
    "asyncpg>=0.29.0",
    "alembic>=1.12.0",
    "psutil>=5.9.0",
    "passlib[bcrypt]>=1.7.4",
    "python-jose[cryptography]>=3.3.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
]
```

---

## Files to Create

| File | Description |
|------|-------------|
| `backend/app/database.py` | Async database connection |
| `backend/app/models/__init__.py` | Model exports |
| `backend/app/models/user.py` | User model |
| `backend/app/models/metrics.py` | Metrics models |
| `backend/alembic.ini` | Alembic configuration |
| `backend/alembic/env.py` | Async migration env |
| `backend/alembic/script.py.mako` | Migration template |
| `scripts/init-db.sql` | Initial data script |

---

## Verification Steps

```bash
# Start database
docker-compose up -d db

# Run migrations
docker-compose exec backend alembic upgrade head

# Verify tables
docker-compose exec db psql -U perfwatch -c "\dt"

# Check admin user exists
docker-compose exec db psql -U perfwatch -c "SELECT username FROM users"

# Test from Python
docker-compose exec backend python -c "
from app.database import engine
import asyncio

async def test():
    async with engine.connect() as conn:
        result = await conn.execute('SELECT 1')
        print('Connected:', result.scalar())

asyncio.run(test())
"
```

---

## Implementation Notes

*To be filled during implementation*

---

## Files Created/Modified

*To be filled during implementation*
