"""Middleware de trace para correlación de requests."""

from __future__ import annotations

from typing import Callable
from uuid import uuid4
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.shared.logging import get_logger, set_trace_id, get_trace_id

logger = get_logger("middleware.trace")


class TraceMiddleware(BaseHTTPMiddleware):
    """Middleware para trazabilidad de requests."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable,
    ) -> Response:
        """Añade trace context al request."""
        trace_id = self._get_or_create_trace_id(request)
        parent_span = request.headers.get("X-Parent-Span", str(uuid4()))
        span_id = str(uuid4())

        set_trace_id(trace_id)

        start_ns = time.perf_counter_ns()

        logger.debug(
            "Trace: request started",
            trace_id=trace_id,
            span_id=span_id,
            parent_span=parent_span,
            path=request.url.path,
            method=request.method,
        )

        try:
            response = await call_next(request)

            duration_ns = time.perf_counter_ns() - start_ns
            duration_ms = duration_ns / 1_000_000

            logger.debug(
                "Trace: request completed",
                trace_id=trace_id,
                span_id=span_id,
                duration_ms=round(duration_ms, 2),
                status_code=response.status_code,
            )

            response.headers["X-Trace-ID"] = trace_id
            response.headers["X-Span-ID"] = span_id
            response.headers["X-Parent-Span"] = parent_span

            return response

        except Exception as e:
            duration_ns = time.perf_counter_ns() - start_ns
            duration_ms = duration_ns / 1_000_000

            logger.error(
                "Trace: request failed",
                trace_id=trace_id,
                span_id=span_id,
                duration_ms=round(duration_ms, 2),
                error=str(e),
            )

            raise

    def _get_or_create_trace_id(self, request: Request) -> str:
        """Obtiene o crea el trace ID."""
        trace_id = request.headers.get("X-Trace-ID")
        if trace_id:
            return trace_id

        return str(uuid4())


class SpanContext:
    """Contexto de span para tracing."""

    def __init__(
        self,
        trace_id: str,
        span_id: str,
        parent_span_id: Optional[str] = None,
    ):
        self.trace_id = trace_id
        self.span_id = span_id
        self.parent_span_id = parent_span_id
        self.start_time = time.perf_counter_ns()
        self.tags: dict[str, str] = {}

    def set_tag(self, key: str, value: str) -> None:
        """Añade un tag al span."""
        self.tags[key] = value

    def finish(self) -> dict:
        """Finaliza el span y retorna la información."""
        duration_ns = time.perf_counter_ns() - self.start_time
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "duration_ms": duration_ns / 1_000_000,
            "tags": self.tags,
        }

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        span_data = self.finish()
        if exc_type:
            span_data["error"] = str(exc_val)
            logger.error("Span finished with error", **span_data)
        else:
            logger.debug("Span finished", **span_data)


from typing import Optional
