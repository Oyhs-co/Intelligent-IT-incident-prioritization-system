"""Tests unitarios para RedisSubscriber."""

from __future__ import annotations

import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.infrastructure.messaging.redis_subscriber import RedisSubscriber


@pytest.fixture
def subscriber():
    return RedisSubscriber(host="localhost", port=6379, db=0)


class TestRedisSubscriber:
    """Tests para RedisSubscriber."""

    @pytest.mark.asyncio
    async def test_connect_success(self, subscriber):
        """Conexión exitosa debe crear pubsub."""
        with patch("redis.asyncio.Redis") as mock_redis_cls:
            mock_redis = AsyncMock()
            mock_pubsub = MagicMock()
            mock_redis.pubsub.return_value = mock_pubsub
            mock_redis_cls.return_value = mock_redis

            await subscriber.connect()

            assert subscriber._client is not None
            assert subscriber._pubsub is not None
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, subscriber):
        """Fallo de conexión debe lanzar excepción."""
        with patch("redis.asyncio.Redis") as mock_redis_cls:
            mock_redis = AsyncMock()
            mock_redis.ping.side_effect = Exception("Connection failed")
            mock_redis_cls.return_value = mock_redis

            with pytest.raises(Exception):
                await subscriber.connect()

    @pytest.mark.asyncio
    async def test_disconnect(self, subscriber):
        """Disconnect debe cancelar tarea y cerrar pubsub."""
        task = asyncio.create_task(asyncio.sleep(0))
        pubsub = AsyncMock()
        client = AsyncMock()
        subscriber._task = task
        subscriber._pubsub = pubsub
        subscriber._client = client
        subscriber._running = True

        await subscriber.disconnect()

        assert subscriber._running is False
        pubsub.close.assert_called_once()
        client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_no_client(self, subscriber):
        """Disconnect sin cliente no debe fallar."""
        await subscriber.disconnect()

    @pytest.mark.asyncio
    async def test_subscribe_adds_handler(self, subscriber):
        """subscribe debe agregar handler al canal."""
        async def handler(data):
            pass

        pubsub = MagicMock()
        pubsub.subscribe = AsyncMock()
        subscriber._pubsub = pubsub
        subscriber.subscribe("test-channel", handler)

        assert "test-channel" in subscriber._handlers
        assert handler in subscriber._handlers["test-channel"]

    @pytest.mark.asyncio
    async def test_subscribe_same_channel_multiple_handlers(self, subscriber):
        """subscribe múltiples handlers al mismo canal."""
        async def handler1(data):
            pass

        async def handler2(data):
            pass

        pubsub = MagicMock()
        pubsub.subscribe = AsyncMock()
        subscriber._pubsub = pubsub
        subscriber.subscribe("test-channel", handler1)
        subscriber.subscribe("test-channel", handler2)

        assert len(subscriber._handlers["test-channel"]) == 2

    @pytest.mark.asyncio
    async def test_subscribe_no_pubsub(self, subscriber):
        """subscribe sin pubsub (no conectado)."""
        async def handler(data):
            pass

        subscriber._pubsub = None
        subscriber.subscribe("ch", handler)
        assert "ch" in subscriber._handlers

    @pytest.mark.asyncio
    async def test_unsubscribe_removes_handler(self, subscriber):
        """unsubscribe debe remover handler."""
        async def handler(data):
            pass

        pubsub = MagicMock()
        pubsub.subscribe = AsyncMock()
        pubsub.unsubscribe = AsyncMock()
        subscriber._pubsub = pubsub
        subscriber.subscribe("test-channel", handler)
        subscriber.unsubscribe("test-channel", handler)

        assert "test-channel" not in subscriber._handlers

    @pytest.mark.asyncio
    async def test_unsubscribe_unknown_channel(self, subscriber):
        """unsubscribe de canal desconocido no debe fallar."""
        async def handler(data):
            pass

        subscriber.unsubscribe("nonexistent", handler)

    @pytest.mark.asyncio
    async def test_start_listening_not_connected(self, subscriber):
        """start_listening sin conexión debe lanzar RuntimeError."""
        subscriber._pubsub = None

        with pytest.raises(RuntimeError, match="Not connected"):
            await subscriber.start_listening()

    @pytest.mark.asyncio
    async def test_start_listening_success(self, subscriber):
        """start_listening debe crear tarea de escucha."""
        subscriber._pubsub = MagicMock()
        subscriber._pubsub.get_message = AsyncMock(return_value=None)

        await subscriber.start_listening()

        assert subscriber._running is True
        assert subscriber._task is not None

        subscriber._running = False
        subscriber._task.cancel()
        try:
            await subscriber._task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_dispatch_with_handlers(self, subscriber):
        """_dispatch debe llamar a handlers registrados."""
        handler = AsyncMock()
        subscriber._handlers["test-channel"] = [handler]

        data = {"event_id": "evt-001", "channel": "test-channel", "data": {"key": "val"}}
        await subscriber._dispatch("test-channel", data)

        handler.assert_called_once_with(data)

    @pytest.mark.asyncio
    async def test_dispatch_no_handlers(self, subscriber):
        """_dispatch sin handlers no debe hacer nada."""
        await subscriber._dispatch("empty-channel", {"data": "test"})

    @pytest.mark.asyncio
    async def test_dispatch_handler_error(self, subscriber):
        """_dispatch con handler que falla no debe propagar."""
        async def failing_handler(data):
            raise Exception("Handler error")

        subscriber._handlers["test-channel"] = [failing_handler]

        await subscriber._dispatch("test-channel", {"data": "test"})

    @pytest.mark.asyncio
    async def test_get_message_count(self, subscriber):
        """get_message_count debe retornar conteo por canal."""
        async def h1(data):
            pass

        async def h2(data):
            pass

        subscriber._handlers = {"ch1": [h1], "ch2": [h1, h2]}
        counts = await subscriber.get_message_count()

        assert counts["ch1"] == 1
        assert counts["ch2"] == 2

    @pytest.mark.asyncio
    async def test_listen_loop_processes_message(self, subscriber):
        """_listen_loop debe procesar mensaje y llamar _dispatch."""
        subscriber._running = True
        subscriber._pubsub = MagicMock()

        message = {
            "type": "message",
            "channel": "test-channel",
            "data": json.dumps({"event_id": "evt-001"}),
        }

        call_count = 0

        async def get_message(ignore_subscribe_messages=True, timeout=1.0):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return message
            subscriber._running = False
            return None

        subscriber._pubsub.get_message = get_message
        subscriber._dispatch = AsyncMock()

        await subscriber._listen_loop()

        subscriber._dispatch.assert_called_once()

    @pytest.mark.asyncio
    async def test_listen_loop_cancelled(self, subscriber):
        """_listen_loop con CancelledError debe salir gracefully."""

        async def get_message(ignore_subscribe_messages=True, timeout=1.0):
            raise asyncio.CancelledError()

        subscriber._running = True
        subscriber._pubsub = MagicMock()
        subscriber._pubsub.get_message = get_message

        await subscriber._listen_loop()
