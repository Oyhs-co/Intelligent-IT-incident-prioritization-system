"""Suscriptor Redis para eventos."""

from __future__ import annotations

import json
from typing import Any, Callable, Optional, Awaitable
from asyncio import Queue
import asyncio

import redis.asyncio as redis

from src.shared.logging import get_logger

logger = get_logger("messaging.subscriber")


MessageHandler = Callable[[dict[str, Any]], Awaitable[None]]


class RedisSubscriber:
    """Suscriptor de eventos usando Redis Pub/Sub."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
    ):
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._client: Optional[redis.Redis] = None
        self._pubsub: Optional[redis.client.PubSub] = None
        self._handlers: dict[str, list[MessageHandler]] = {}
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def connect(self) -> None:
        """Establece conexión con Redis."""
        try:
            self._client = redis.Redis(
                host=self._host,
                port=self._port,
                db=self._db,
                password=self._password,
                decode_responses=True,
            )
            self._pubsub = self._client.pubsub()
            await self._client.ping()
            logger.info("Connected to Redis subscriber")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self) -> None:
        """Cierra la conexión."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        if self._pubsub:
            await self._pubsub.close()
        if self._client:
            await self._client.close()
        logger.info("Disconnected from Redis subscriber")

    def subscribe(self, channel: str, handler: MessageHandler) -> None:
        """Suscribe un handler a un canal."""
        if channel not in self._handlers:
            self._handlers[channel] = []
            if self._pubsub:
                asyncio.create_task(self._pubsub.subscribe(channel))
        self._handlers[channel].append(handler)
        logger.info(f"Subscribed handler to channel: {channel}")

    def unsubscribe(self, channel: str, handler: MessageHandler) -> None:
        """Desuscribe un handler de un canal."""
        if channel in self._handlers:
            self._handlers[channel].remove(handler)
            if not self._handlers[channel]:
                del self._handlers[channel]
                if self._pubsub:
                    asyncio.create_task(self._pubsub.unsubscribe(channel))
        logger.info(f"Unsubscribed handler from channel: {channel}")

    async def start_listening(self) -> None:
        """Inicia la escucha de mensajes."""
        if not self._pubsub:
            raise RuntimeError("Not connected to Redis")

        self._running = True
        self._task = asyncio.create_task(self._listen_loop())
        logger.info("Started listening for messages")

    async def _listen_loop(self) -> None:
        """Loop principal de escucha."""
        while self._running:
            try:
                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=1.0,
                )
                if message and message["type"] == "message":
                    channel = message["channel"]
                    data = json.loads(message["data"])
                    await self._dispatch(channel, data)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await asyncio.sleep(0.1)

    async def _dispatch(self, channel: str, data: dict[str, Any]) -> None:
        """Despacha un mensaje a los handlers."""
        handlers = self._handlers.get(channel, [])
        if not handlers:
            logger.debug(f"No handlers for channel: {channel}")
            return

        logger.info(
            "Dispatching message",
            channel=channel,
            event_id=data.get("event_id"),
            handler_count=len(handlers),
        )

        for handler in handlers:
            try:
                await handler(data)
            except Exception as e:
                logger.error(f"Handler error: {e}", channel=channel)

    async def get_message_count(self) -> dict[str, int]:
        """Obtiene conteo de mensajes por canal."""
        counts = {}
        for channel in self._handlers:
            counts[channel] = len(self._handlers[channel])
        return counts
