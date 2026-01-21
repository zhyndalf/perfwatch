"""PerfWatch Backend - Main Application Entry Point"""

import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import close_db, AsyncSessionLocal
from app.api.auth import router as auth_router
from app.api.websocket import router as websocket_router, start_background_collection, stop_background_collection
from app.api.history import router as history_router
from app.api.retention import router as retention_router
from app.api.config import router as config_router
from app.services.retention import apply_retention_policy

logger = logging.getLogger(__name__)

_retention_task: asyncio.Task | None = None
_retention_stop: asyncio.Event | None = None


async def _retention_loop() -> None:
    """Run retention cleanup on a fixed interval."""
    assert _retention_stop is not None

    while not _retention_stop.is_set():
        if settings.RETENTION_CLEANUP_ENABLED:
            try:
                async with AsyncSessionLocal() as session:
                    deleted, _ = await apply_retention_policy(session)
                    if deleted:
                        logger.info("Retention cleanup removed %s snapshots", deleted)
            except Exception:
                logger.exception("Retention cleanup failed")

        try:
            interval_seconds = max(settings.RETENTION_CLEANUP_INTERVAL_MINUTES, 1) * 60
            await asyncio.wait_for(_retention_stop.wait(), timeout=interval_seconds)
        except asyncio.TimeoutError:
            continue


async def start_retention_cleanup() -> None:
    """Start the periodic retention cleanup task."""
    global _retention_task, _retention_stop
    if _retention_task is not None:
        return
    _retention_stop = asyncio.Event()
    _retention_task = asyncio.create_task(_retention_loop())


async def stop_retention_cleanup() -> None:
    """Stop the periodic retention cleanup task."""
    global _retention_task, _retention_stop
    if _retention_task is None or _retention_stop is None:
        return
    _retention_stop.set()
    await _retention_task
    _retention_task = None
    _retention_stop = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    # Startup
    print(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Note: Migrations should be run separately via alembic
    # Initialize default data
    from app.init_db import init_default_data
    await init_default_data()
    if settings.BACKGROUND_COLLECTION_ENABLED:
        await start_background_collection()
    if settings.RETENTION_CLEANUP_ENABLED:
        await start_retention_cleanup()

    yield

    # Shutdown
    print("Shutting down...")
    if settings.BACKGROUND_COLLECTION_ENABLED:
        await stop_background_collection()
    if settings.RETENTION_CLEANUP_ENABLED:
        await stop_retention_cleanup()
    await close_db()


app = FastAPI(
    title="PerfWatch API",
    description="Real-time system performance monitoring API",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(websocket_router)
app.include_router(history_router)
app.include_router(retention_router)
app.include_router(config_router)


@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestration."""
    return {"status": "healthy", "service": "perfwatch-backend"}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/api/db-status")
async def db_status():
    """Check database connection status."""
    from sqlalchemy import text

    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        return {"status": "connected", "database": "postgresql"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
