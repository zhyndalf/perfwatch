"""Tests for the WebSocket metrics streaming endpoint."""

import asyncio
from contextlib import suppress
from datetime import datetime, timezone
from typing import Tuple

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from starlette.websockets import WebSocketDisconnect

from app.api import websocket as ws_module
from app.database import get_db
from app.main import app
from app.models import User
from app.services.auth import create_access_token, hash_password


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


async def create_user(session_maker: async_sessionmaker[AsyncSession], username: str = "wsuser") -> User:
    """Create and return a persisted test user."""
    async with session_maker() as session:
        user = User(username=username, password_hash=hash_password("secret123"))
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user


@pytest_asyncio.fixture
async def websocket_env(
    db_session: AsyncSession,
    monkeypatch: pytest.MonkeyPatch,
) -> Tuple[async_sessionmaker[AsyncSession], StubAggregator]:
    """Prepare DB override, aggregator stub, and clean connection manager state."""
    session_maker = async_sessionmaker(
        bind=db_session.bind,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    aggregator = StubAggregator()
    monkeypatch.setattr(ws_module, "AsyncSessionLocal", session_maker)
    monkeypatch.setattr(ws_module, "_aggregator", aggregator)
    monkeypatch.setattr(ws_module, "get_aggregator", lambda: aggregator)
    ws_module._aggregator_task = None
    ws_module.manager.active_connections.clear()

    yield session_maker, aggregator

    task = ws_module._aggregator_task
    if task is not None and not task.done():
        task.cancel()
        with suppress(asyncio.CancelledError):
            await task

    ws_module._aggregator_task = None
    ws_module._aggregator = None
    ws_module.manager.active_connections.clear()
    app.dependency_overrides.clear()


class TestWebSocketAuth:
    """Authentication behavior for WebSocket connections."""

    @pytest.mark.asyncio
    async def test_connection_requires_token(self, websocket_env):
        _, aggregator = websocket_env

        with TestClient(app) as client:
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

    @pytest.mark.asyncio
    async def test_connection_rejects_invalid_token(self, websocket_env):
        _, aggregator = websocket_env

        with TestClient(app) as client:
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

    @pytest.mark.asyncio
    async def test_ping_pong_roundtrip(self, websocket_env):
        session_maker, _ = websocket_env
        user = await create_user(session_maker)
        token = create_access_token({"sub": str(user.id)})

        with TestClient(app) as client:
            with client.websocket_connect(f"/api/ws/metrics?token={token}") as websocket:
                websocket.send_json({"type": "ping"})

                received_types = set()
                for _ in range(2):
                    message = websocket.receive_json()
                    received_types.add(message.get("type"))
                    if "pong" in received_types:
                        break

        assert "pong" in received_types

    @pytest.mark.asyncio
    async def test_broadcast_metrics_to_connected_client(self, websocket_env):
        session_maker, _ = websocket_env
        user = await create_user(session_maker)
        token = create_access_token({"sub": str(user.id)})

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {"usage": 12.3},
            "memory": {"used": 1024},
            "network": {"bytes_sent": 2048},
            "disk": {"read_bytes": 4096},
        }

        with TestClient(app) as client:
            with client.websocket_connect(f"/api/ws/metrics?token={token}") as websocket:
                await ws_module.broadcast_metrics(snapshot)

                message = websocket.receive_json()

        assert message["type"] == "metrics"
        assert message["timestamp"] == snapshot["timestamp"]
        assert message["data"]["cpu"]["usage"] == 12.3
        assert message["data"]["memory"]["used"] == 1024

    @pytest.mark.asyncio
    async def test_broadcast_metrics_to_multiple_clients(self, websocket_env):
        session_maker, aggregator = websocket_env
        user = await create_user(session_maker)
        token = create_access_token({"sub": str(user.id)})

        snapshot = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cpu": {"usage": 42.0},
            "memory": {"used": 2048},
            "network": {"bytes_sent": 10},
            "disk": {"read_bytes": 20},
        }

        with TestClient(app) as client:
            with client.websocket_connect(f"/api/ws/metrics?token={token}") as ws1:
                with client.websocket_connect(f"/api/ws/metrics?token={token}") as ws2:
                    await ws_module.broadcast_metrics(snapshot)

                    msg1 = ws1.receive_json()
                    msg2 = ws2.receive_json()

            await asyncio.sleep(0)

        assert msg1["data"]["cpu"]["usage"] == 42.0
        assert msg2["data"]["cpu"]["usage"] == 42.0
        assert aggregator.stopped is True
        assert ws_module.manager.connection_count == 0
        assert ws_module._aggregator_task is None


class TestAggregatorLifecycle:
    """Lifecycle handling for the background aggregator."""

    @pytest.mark.asyncio
    async def test_aggregator_starts_and_stops_with_clients(self, websocket_env):
        session_maker, aggregator = websocket_env
        user = await create_user(session_maker)
        token = create_access_token({"sub": str(user.id)})

        aggregator.start_snapshot = {
            "timestamp": "2026-01-19T00:00:00Z",
            "cpu": {"usage": 1.0},
            "memory": {"used": 1},
            "network": {"bytes_sent": 1},
            "disk": {"read_bytes": 1},
        }

        with TestClient(app) as client:
            with client.websocket_connect(f"/api/ws/metrics?token={token}") as websocket:
                initial = websocket.receive_json()
                assert initial["type"] == "metrics"

                await asyncio.sleep(0)

            await asyncio.sleep(0)

        assert aggregator.started is True
        assert aggregator.stopped is True
        assert ws_module.manager.connection_count == 0
        assert ws_module._aggregator_task is None
