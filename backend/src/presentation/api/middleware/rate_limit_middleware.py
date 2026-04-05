"""Middleware de rate limiting."""

from __future__ import annotations

import time
from typing import Callable, Optional
from collections import defaultdict
from asyncio import Lock

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.shared.logging import get_logger

logger = get_logger("middleware.rate_limit")


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para rate limiting."""

    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000,
        burst_size: int = 10,
    ):
        super().__init__(app)
        self._rpm = requests_per_minute
        self._rph = requests_per_hour
        self._burst = burst_size
        self._requests: dict[str, list[float]] = defaultdict(list)
        self._lock = Lock()

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Aplica rate limiting."""
        client_ip = self._get_client_ip(request)
        now = time.time()

        async with self._lock:
            self._clean_old_requests(client_ip, now)

            is_allowed, reason = await self._check_limits(client_ip, now)

            if not is_allowed:
                logger.warning(
                    "Rate limit exceeded",
                    client_ip=client_ip,
                    path=request.url.path,
                    reason=reason,
                )
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Too Many Requests",
                        "detail": reason,
                        "retry_after": self._get_retry_after(client_ip),
                    },
                    headers={"Retry-After": str(self._get_retry_after(client_ip))},
                )

            self._requests[client_ip].append(now)

        response = await call_next(request)
        remaining = self._get_remaining(client_ip)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Limit"] = str(self._rpm)

        return response

    def _get_client_ip(self, request: Request) -> str:
        """Obtiene la IP del cliente."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _clean_old_requests(self, client_ip: str, now: float) -> None:
        """Limpia requests antiguos."""
        minute_ago = now - 60
        hour_ago = now - 3600

        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > hour_ago
        ]

    async def _check_limits(self, client_ip: str, now: float) -> tuple[bool, str]:
        """Verifica si el cliente está dentro de los límites."""
        requests = self._requests[client_ip]
        minute_ago = now - 60
        hour_ago = now - 3600

        recent_requests = [t for t in requests if t > minute_ago]
        if len(recent_requests) >= self._rpm:
            return False, f"Rate limit: max {self._rpm} requests per minute"

        hour_requests = [t for t in requests if t > hour_ago]
        if len(hour_requests) >= self._rph:
            return False, f"Rate limit: max {self._rph} requests per hour"

        return True, ""

    def _get_remaining(self, client_ip: str) -> int:
        """Obtiene requests restantes."""
        now = time.time()
        recent = [t for t in self._requests[client_ip] if t > now - 60]
        return max(0, self._rpm - len(recent))

    def _get_retry_after(self, client_ip: str) -> int:
        """Calcula segundos hasta próximo request permitido."""
        now = time.time()
        requests = self._requests[client_ip]
        if not requests:
            return 1

        oldest_recent = min([t for t in requests if t > now - 60], default=now)
        return max(1, int(60 - (now - oldest_recent)))


class SlidingWindowRateLimiter:
    """Rate limiter con ventana deslizante usando Redis."""

    def __init__(
        self,
        redis_client=None,
        requests_per_minute: int = 60,
        key_prefix: str = "ratelimit:",
    ):
        self._redis = redis_client
        self._rpm = requests_per_minute
        self._key_prefix = key_prefix

    async def is_allowed(self, identifier: str) -> tuple[bool, int]:
        """
        Verifica si el identificador puede hacer un request.

        Returns:
            (is_allowed, remaining_requests)
        """
        if not self._redis:
            return True, self._rpm

        key = f"{self._key_prefix}{identifier}"
        now = time.time()
        window_start = now - 60

        try:
            pipe = self._redis.pipeline()
            pipe.zremrangebyscore(key, 0, window_start)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, 120)
            results = await pipe.execute()

            current_count = results[1]
            remaining = max(0, self._rpm - current_count - 1)

            return current_count < self._rpm, remaining

        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True, self._rpm
