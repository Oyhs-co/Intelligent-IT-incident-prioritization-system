"""Middleware de logging para requests."""

from __future__ import annotations

import time
from typing import Callable
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.shared.logging import get_logger, set_trace_id

logger = get_logger("middleware.logging")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Procesa el request con logging."""
        start_time = time.time()

        trace_id = request.headers.get("X-Trace-ID", str(uuid4()))
        set_trace_id(trace_id)

        request_id = request.headers.get("X-Request-ID", str(uuid4()))

        logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            trace_id=trace_id,
            request_id=request_id,
        )

        try:
            response = await call_next(request)

            duration_ms = (time.time() - start_time) * 1000

            logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                trace_id=trace_id,
                request_id=request_id,
            )

            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = f"{duration_ms:.2f}ms"

            return response

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000

            logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                duration_ms=round(duration_ms, 2),
                trace_id=trace_id,
                request_id=request_id,
            )

            raise
