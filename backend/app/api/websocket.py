"""WebSocket endpoint for real-time metrics streaming."""

import asyncio
import json
import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import User
from app.services.auth import decode_token
from app.services.metrics_storage import MetricsBatchWriter, save_all_metrics
from app.collectors import (
    MetricsAggregator,
    CPUCollector,
    MemoryCollector,
    NetworkCollector,
    DiskCollector,
    PerfEventsCollector,
    MemoryBandwidthCollector,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ws", tags=["websocket"])


class ConnectionManager:
    """Manages WebSocket connections for broadcasting metrics.

    Keeps track of active WebSocket connections and provides methods
    to broadcast messages to all connected clients.
    """

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and store a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection from the manager."""
        async with self._lock:
            if websocket in self.active_connections:
                self.active_connections.remove(websocket)
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict) -> None:
        """Send a message to all connected clients.

        Handles connection errors gracefully by removing failed connections.
        """
        disconnected = []

        async with self._lock:
            connections = list(self.active_connections)

        for connection in connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Failed to send to client: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        if disconnected:
            async with self._lock:
                for conn in disconnected:
                    if conn in self.active_connections:
                        self.active_connections.remove(conn)

    @property
    def connection_count(self) -> int:
        """Get the number of active connections."""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()

# Global aggregator instance (will be initialized on first connection)
_aggregator: Optional[MetricsAggregator] = None
_aggregator_task: Optional[asyncio.Task] = None
_metrics_writer: Optional[MetricsBatchWriter] = None
_background_collection = False


def get_aggregator() -> MetricsAggregator:
    """Get or create the global metrics aggregator."""
    global _aggregator
    if _aggregator is None:
        _aggregator = MetricsAggregator(
            collectors=[
                CPUCollector(),
                MemoryCollector(),
                NetworkCollector(),
                DiskCollector(),
                PerfEventsCollector(),
                MemoryBandwidthCollector(),
            ],
            interval=float(settings.SAMPLING_INTERVAL_SECONDS),
        )
    return _aggregator


def get_metrics_writer() -> MetricsBatchWriter:
    """Get or create the global metrics batch writer."""
    global _metrics_writer
    if _metrics_writer is not None and not _metrics_writer.is_loop_compatible():
        _metrics_writer = None
    if _metrics_writer is None:
        _metrics_writer = MetricsBatchWriter(batch_size=50, flush_interval=2.0)
    return _metrics_writer


async def broadcast_metrics(snapshot: Dict) -> None:
    """Callback for the aggregator to broadcast metrics to all clients.

    This function both broadcasts metrics to connected WebSocket clients
    and persists them to the database for historical queries.
    """
    message = {
        "type": "metrics",
        "timestamp": snapshot.get("timestamp"),
        "data": {
            "cpu": snapshot.get("cpu"),
            "memory": snapshot.get("memory"),
            "network": snapshot.get("network"),
            "disk": snapshot.get("disk"),
            "perf_events": snapshot.get("perf_events"),
            "memory_bandwidth": snapshot.get("memory_bandwidth"),
        }
    }
    await manager.broadcast(message)

    # Persist metrics to database for history
    try:
        writer = get_metrics_writer()
        if writer is not None:
            await writer.enqueue(snapshot)
        else:
            await save_all_metrics(snapshot)
    except Exception as e:
        logger.error(f"Failed to save metrics to database: {e}")


async def start_aggregator_if_needed() -> None:
    """Start the metrics aggregator if not already running."""
    global _aggregator_task

    aggregator = get_aggregator()

    if not aggregator.is_running and _aggregator_task is None:
        logger.info("Starting metrics aggregator...")
        writer = get_metrics_writer()
        await writer.start()
        _aggregator_task = asyncio.create_task(
            aggregator.start(broadcast_metrics)
        )


async def stop_aggregator_if_no_clients() -> None:
    """Stop the aggregator if no clients are connected."""
    global _aggregator_task, _metrics_writer

    if _background_collection:
        return

    if manager.connection_count == 0 and _aggregator is not None:
        logger.info("No clients connected, stopping aggregator...")
        _aggregator.stop()

        if _aggregator_task is not None:
            try:
                # Give it time to finish the current cycle
                await asyncio.wait_for(_aggregator_task, timeout=2.0)
            except asyncio.TimeoutError:
                _aggregator_task.cancel()
            _aggregator_task = None
        if _metrics_writer is not None:
            await _metrics_writer.stop()
            _metrics_writer = None


async def start_background_collection() -> None:
    """Start background metrics collection regardless of WebSocket clients."""
    global _background_collection
    _background_collection = True
    await start_aggregator_if_needed()


async def stop_background_collection() -> None:
    """Stop background metrics collection."""
    global _background_collection, _aggregator_task
    _background_collection = False
    if _aggregator is not None:
        _aggregator.stop()
    if _aggregator_task is not None:
        try:
            await asyncio.wait_for(_aggregator_task, timeout=2.0)
        except asyncio.TimeoutError:
            _aggregator_task.cancel()
        _aggregator_task = None
    if _metrics_writer is not None:
        await _metrics_writer.stop()


async def authenticate_websocket(token: Optional[str]) -> Optional[User]:
    """Validate JWT token and return the user.

    Args:
        token: JWT token from query parameter

    Returns:
        User object if valid, None otherwise
    """
    if not token:
        return None

    payload = decode_token(token)
    if payload is None:
        return None

    user_id_str = payload.get("sub")
    if user_id_str is None:
        return None

    try:
        user_id = int(user_id_str)
    except ValueError:
        return None

    # Fetch user from database
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

    return user


@router.websocket("/metrics")
async def websocket_metrics(
    websocket: WebSocket,
    token: Optional[str] = Query(default=None),
) -> None:
    """WebSocket endpoint for real-time metrics streaming.

    Connection: ws://localhost:8000/api/ws/metrics?token=<jwt_token>

    Server sends metrics every 5 seconds:
    {
        "type": "metrics",
        "timestamp": "2025-01-18T14:30:05Z",
        "data": { cpu: {...}, memory: {...}, network: {...}, disk: {...} }
    }

    Client can send ping messages:
    { "type": "ping" }

    Server responds with:
    { "type": "pong" }
    """
    # Authenticate the connection
    user = await authenticate_websocket(token)
    if user is None:
        await websocket.close(code=4001, reason="Authentication required")
        return

    logger.info(f"WebSocket connection authenticated for user: {user.username}")

    # Accept connection and add to manager
    await manager.connect(websocket)

    # Start aggregator if this is the first client
    await start_aggregator_if_needed()

    try:
        while True:
            # Wait for messages from client
            try:
                data = await websocket.receive_json()

                # Handle ping messages
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

            except json.JSONDecodeError:
                # Ignore malformed messages
                pass

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for user: {user.username}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        # Remove from manager and potentially stop aggregator
        await manager.disconnect(websocket)
        await stop_aggregator_if_no_clients()
