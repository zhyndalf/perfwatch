"""Tests for the WebSocket metrics streaming endpoint."""

import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import datetime, timezone
from typing import Tuple

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from starlette.websockets import WebSocketDisconnect

from app.api import websocket as ws_module
from app.database import Base
from app.models import User
from app.services.auth import create_access_token, hash_password


# Test database URL
TEST_DATABASE_URL = "postgresql+asyncpg://perfwatch:perfwatch@db:5432/perfwatch_test"


# Create a test app without the production lifespan (which causes event loop issues)
@asynccontextmanager
async def _noop_lifespan(app: FastAPI):
    """Minimal lifespan for testing - skip init_default_data."""
    yield


ws_test_app = FastAPI(lifespan=_noop_lifespan)
ws_test_app.include_router(ws_module.router)


class StubAggregator:
    """Lightweight aggregator stub to avoid real collectors during tests."""

    def __init__(self):
        self.started = False
        self.stopped = False
        self.is_running = False
        self.start_snapshot = None

    async def start(self, callback):
        self.started = True
        self.is_running = True
        if self.start_snapshot is not None:
            await callback(self.start_snapshot)
        self.is_running = False

    def stop(self):
        self.stopped = True
        self.is_running = False


def create_user_sync(engine, username: str = "wsuser") -> User:
    """Create a test user using synchronous operations for TestClient compatibility."""
    import asyncio
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    async def _create():
        session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
        async with session_maker() as session:
            user = User(username=username, password_hash=hash_password("secret123"))
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    # Run in a new event loop to avoid conflicts with TestClient
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(_create())
    finally:
        loop.close()


@pytest.fixture
def websocket_env(monkeypatch: pytest.MonkeyPatch):
    """Prepare DB override, aggregator stub, and clean connection manager state.

    This is a sync fixture to work properly with TestClient which manages its own event loop.
    """
    import asyncio

    # Reset any module state first
    ws_module._aggregator = None
    ws_module._aggregator_task = None
    ws_module.manager.active_connections.clear()

    # Create a fresh engine for this test with isolation_level for clean transactions
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        pool_pre_ping=True,  # Verify connections are valid
    )

    # Ensure tables exist - use a completely fresh event loop
    def run_async(coro):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
            asyncio.set_event_loop(None)

    async def setup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    run_async(setup_db())

    session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    aggregator = StubAggregator()
    monkeypatch.setattr(ws_module, "AsyncSessionLocal", session_maker)
    monkeypatch.setattr(ws_module, "_aggregator", aggregator)
    monkeypatch.setattr(ws_module, "get_aggregator", lambda: aggregator)

    yield engine, session_maker, aggregator

    # Cleanup
    task = ws_module._aggregator_task
    if task is not None and not task.done():
        task.cancel()

    ws_module._aggregator_task = None
    ws_module._aggregator = None
    ws_module.manager.active_connections.clear()

    # Cleanup database
    async def cleanup_db():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    run_async(cleanup_db())


class TestWebSocketAuth:
    """Authentication behavior for WebSocket connections."""

    def test_connection_requires_token(self, websocket_env):
        engine, session_maker, aggregator = websocket_env

        with TestClient(ws_test_app) as client:
            try:
                with client.websocket_connect("/api/ws/metrics") as websocket:
                    with pytest.raises(WebSocketDisconnect) as exc:
                        websocket.receive_json()
                    code = exc.value.code
            except WebSocketDisconnect as exc:
                code = exc.code

        assert code == 4001
        assert aggregator.started is False
        assert aggregator.stopped is False

    def test_connection_rejects_invalid_token(self, websocket_env):
        engine, session_maker, aggregator = websocket_env

        with TestClient(ws_test_app) as client:
            try:
                with client.websocket_connect("/api/ws/metrics?token=not.a.valid.token") as websocket:
                    with pytest.raises(WebSocketDisconnect) as exc:
                        websocket.receive_json()
                    code = exc.value.code
            except WebSocketDisconnect as exc:
                code = exc.code

        assert code == 4001
        assert aggregator.started is False
        assert aggregator.stopped is False


class TestWebSocketMessaging:
    """Messaging behavior for WebSocket clients."""

    def test_ping_pong_roundtrip(self, websocket_env):
        engine, session_maker, aggregator = websocket_env
        user = create_user_sync(engine)
        token = create_access_token({"sub": str(user.id)})

        with TestClient(ws_test_app) as client:
            with client.websocket_connect(f"/api/ws/metrics?token={token}") as websocket:
                websocket.send_json({"type": "ping"})

                received_types = set()
                for _ in range(2):
                    message = websocket.receive_json()
                    received_types.add(message.get("type"))
                    if "pong" in received_types:
                        break

        assert "pong" in received_types

    def test_broadcast_metrics_to_connected_client(self, websocket_env):
        engine, session_maker, aggregator = websocket_env
        user = create_user_sync(engine)
        token = create_access_token({"sub": str(user.id)})

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {"usage": 12.3},
            "memory": {"used": 1024},
            "network": {"bytes_sent": 2048},
            "disk": {"read_bytes": 4096},
        }

        # Set the aggregator to send our snapshot when started
        aggregator.start_snapshot = snapshot

        with TestClient(ws_test_app) as client:
            with client.websocket_connect(f"/api/ws/metrics?token={token}") as websocket:
                message = websocket.receive_json()

        assert message["type"] == "metrics"
        assert message["timestamp"] == snapshot["timestamp"]
        assert message["data"]["cpu"]["usage"] == 12.3
        assert message["data"]["memory"]["used"] == 1024

    def test_broadcast_metrics_to_multiple_clients(self, websocket_env):
        engine, session_maker, aggregator = websocket_env
        user = create_user_sync(engine)
        token = create_access_token({"sub": str(user.id)})

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {"usage": 42.0},
            "memory": {"used": 2048},
            "network": {"bytes_sent": 10},
            "disk": {"read_bytes": 20},
        }

        # Set the aggregator to send our snapshot when started
        aggregator.start_snapshot = snapshot

        with TestClient(ws_test_app) as client:
            with client.websocket_connect(f"/api/ws/metrics?token={token}") as ws1:
                # First client receives the initial broadcast
                msg1 = ws1.receive_json()

                with client.websocket_connect(f"/api/ws/metrics?token={token}") as ws2:
                    # Send ping to trigger pong response (proves connection works)
                    ws2.send_json({"type": "ping"})
                    msg2 = ws2.receive_json()

        assert msg1["data"]["cpu"]["usage"] == 42.0
        assert msg2["type"] == "pong"  # Second client responds to ping
        assert aggregator.stopped is True
        assert ws_module.manager.connection_count == 0


class TestAggregatorLifecycle:
    """Lifecycle handling for the background aggregator."""

    def test_aggregator_starts_and_stops_with_clients(self, websocket_env):
        engine, session_maker, aggregator = websocket_env
        user = create_user_sync(engine)
        token = create_access_token({"sub": str(user.id)})

        aggregator.start_snapshot = {
            "timestamp": "2026-01-19T00:00:00Z",
            "cpu": {"usage": 1.0},
            "memory": {"used": 1},
            "network": {"bytes_sent": 1},
            "disk": {"read_bytes": 1},
        }

        with TestClient(ws_test_app) as client:
            with client.websocket_connect(f"/api/ws/metrics?token={token}") as websocket:
                initial = websocket.receive_json()
                assert initial["type"] == "metrics"

        assert aggregator.started is True
        assert aggregator.stopped is True
        assert ws_module.manager.connection_count == 0
