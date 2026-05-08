"""Tests unitarios para RedisPublisher."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from src.infrastructure.messaging.redis_publisher import EventChannel, RedisPublisher


@pytest.fixture
def publisher():
    return RedisPublisher(host="localhost", port=6379, db=0)


class TestRedisPublisher:
    """Tests para RedisPublisher."""

    @pytest.mark.asyncio
    async def test_connect_success(self, publisher):
        """Conexión exitosa debe establecer _connected."""
        with patch("redis.asyncio.Redis") as mock_redis_cls:
            mock_redis = AsyncMock()
            mock_redis_cls.return_value = mock_redis

            await publisher.connect()

            assert publisher._connected is True
            mock_redis.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, publisher):
        """Fallo de conexión debe lanzar excepción."""
        with patch("redis.asyncio.Redis") as mock_redis_cls:
            mock_redis = AsyncMock()
            mock_redis.ping.side_effect = Exception("Connection refused")
            mock_redis_cls.return_value = mock_redis

            with pytest.raises(Exception):
                await publisher.connect()

            assert publisher._connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, publisher):
        """Disconnect debe cerrar cliente."""
        publisher._client = AsyncMock()
        publisher._connected = True

        await publisher.disconnect()

        assert publisher._connected is False
        publisher._client.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_disconnect_no_client(self, publisher):
        """Disconnect sin cliente no debe fallar."""
        publisher._client = None
        await publisher.disconnect()
        assert publisher._connected is False

    @pytest.mark.asyncio
    async def test_publish_success(self, publisher):
        """publish debe enviar mensaje y retornar número de suscriptores."""
        publisher._client = AsyncMock()
        publisher._client.publish = AsyncMock(return_value=3)

        subscribers = await publisher.publish(
            EventChannel.INCIDENTS_CREATED,
            {"incident_id": "123", "title": "Test"},
        )

        assert subscribers == 3
        publisher._client.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_no_client(self, publisher):
        """publish sin conexión debe retornar 0."""
        publisher._client = None
        subscribers = await publisher.publish(
            EventChannel.INCIDENTS_CREATED,
            {"test": "data"},
        )
        assert subscribers == 0

    @pytest.mark.asyncio
    async def test_publish_error(self, publisher):
        """publish con error debe retornar 0."""
        publisher._client = AsyncMock()
        publisher._client.publish.side_effect = Exception("Redis error")

        subscribers = await publisher.publish(
            EventChannel.INCIDENTS_CREATED,
            {"test": "data"},
        )
        assert subscribers == 0

    @pytest.mark.asyncio
    async def test_publish_incident_created(self, publisher):
        """publish_incident_created debe publicar en canal correcto."""
        publisher.publish = AsyncMock(return_value=1)

        result = await publisher.publish_incident_created(
            incident_id="INC-001",
            ticket_number="TKT-001",
            title="Server down",
            priority=4,
        )

        assert result == 1
        call_args = publisher.publish.call_args
        assert call_args[0][0] == EventChannel.INCIDENTS_CREATED
        assert call_args[0][1]["incident_id"] == "INC-001"

    @pytest.mark.asyncio
    async def test_publish_incident_classified(self, publisher):
        """publish_incident_classified debe publicar en canal correcto."""
        publisher.publish = AsyncMock(return_value=1)

        result = await publisher.publish_incident_classified(
            incident_id="INC-001",
            ticket_number="TKT-001",
            priority=4,
            confidence=0.95,
            explanation="High urgency",
        )

        assert result == 1
        call_args = publisher.publish.call_args
        assert call_args[0][0] == EventChannel.INCIDENTS_CLASSIFIED
        assert call_args[0][1]["confidence"] == 0.95

    @pytest.mark.asyncio
    async def test_publish_sla_alert_warning(self, publisher):
        """publish_sla_alert con hours_remaining > 0 debe ser warning."""
        publisher.publish = AsyncMock(return_value=1)

        result = await publisher.publish_sla_alert(
            incident_id="INC-001",
            ticket_number="TKT-001",
            hours_remaining=2.5,
            priority=4,
        )

        assert result == 1
        call_data = publisher.publish.call_args[0][1]
        assert call_data["alert_type"] == "sla_warning"

    @pytest.mark.asyncio
    async def test_publish_sla_alert_breach(self, publisher):
        """publish_sla_alert con hours_remaining <= 0 debe ser breach."""
        publisher.publish = AsyncMock(return_value=1)

        await publisher.publish_sla_alert(
            incident_id="INC-001",
            ticket_number="TKT-001",
            hours_remaining=-1.0,
            priority=4,
        )

        call_data = publisher.publish.call_args[0][1]
        assert call_data["alert_type"] == "sla_breach"

    @pytest.mark.asyncio
    async def test_publish_metrics_update(self, publisher):
        """publish_metrics_update debe publicar en canal METRICS_UPDATED."""
        publisher.publish = AsyncMock(return_value=1)

        result = await publisher.publish_metrics_update(
            metrics_type="overview",
            metrics_data={"total": 10},
        )

        assert result == 1
        call_args = publisher.publish.call_args
        assert call_args[0][0] == EventChannel.METRICS_UPDATED
        assert call_args[0][1]["type"] == "overview"

    @pytest.mark.asyncio
    async def test_is_connected_true(self, publisher):
        """is_connected con cliente activo debe retornar True."""
        publisher._client = AsyncMock()
        publisher._client.ping = AsyncMock(return_value=True)

        assert await publisher.is_connected() is True

    @pytest.mark.asyncio
    async def test_is_connected_false_no_client(self, publisher):
        """is_connected sin cliente debe retornar False."""
        publisher._client = None
        assert await publisher.is_connected() is False

    @pytest.mark.asyncio
    async def test_is_connected_false_ping_fails(self, publisher):
        """is_connected con ping fallido debe retornar False."""
        publisher._client = AsyncMock()
        publisher._client.ping.side_effect = Exception("No connection")

        assert await publisher.is_connected() is False

    def test_generate_event_id(self, publisher):
        """_generate_event_id debe retornar string."""
        event_id = publisher._generate_event_id()
        assert isinstance(event_id, str)
        assert float(event_id) > 0
