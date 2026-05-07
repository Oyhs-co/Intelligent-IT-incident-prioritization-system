"""Tests unitarios para middlewares de la API."""

import time
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from fastapi import Request, Response
from starlette.types import ASGIApp



class TestRateLimitMiddleware:
    """Tests para RateLimitMiddleware."""

    @pytest.fixture
    def middleware(self):
        from src.presentation.api.middleware.rate_limit_middleware import (
            RateLimitMiddleware,
        )
        mock_app = MagicMock(spec=ASGIApp)
        mw = RateLimitMiddleware(mock_app, requests_per_minute=5, requests_per_hour=100)
        return mw

    @pytest.mark.asyncio
    async def test_dispatch_allows_request_within_limit(self, middleware):
        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.headers = {}

        response = Response("OK", status_code=200)
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)
        assert result.status_code == 200
        assert "X-RateLimit-Remaining" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_blocks_when_limit_exceeded(self, middleware):
        middleware._rpm = 2
        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.headers = {}

        response = Response("OK", status_code=200)
        call_next = AsyncMock(return_value=response)

        await middleware.dispatch(request, call_next)
        await middleware.dispatch(request, call_next)
        result = await middleware.dispatch(request, call_next)

        assert result.status_code == 429
        body = result.body.decode()
        assert "Too Many Requests" in body or "Rate limit" in body

    @pytest.mark.asyncio
    async def test_dispatch_blocks_when_hourly_limit_exceeded(self, middleware):
        middleware._rpm = 999
        middleware._rph = 2
        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.headers = {}

        response = Response("OK", status_code=200)
        call_next = AsyncMock(return_value=response)

        await middleware.dispatch(request, call_next)
        await middleware.dispatch(request, call_next)
        result = await middleware.dispatch(request, call_next)

        assert result.status_code == 429

    def test_get_client_ip_with_forwarded(self, middleware):
        request = MagicMock(spec=Request)
        request.headers = {"X-Forwarded-For": "203.0.113.1, 10.0.0.1"}
        ip = middleware._get_client_ip(request)
        assert ip == "203.0.113.1"

    def test_get_client_ip_without_forwarded(self, middleware):
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client.host = "192.168.1.1"
        ip = middleware._get_client_ip(request)
        assert ip == "192.168.1.1"

    def test_get_client_ip_unknown(self, middleware):
        request = MagicMock(spec=Request)
        request.headers = {}
        request.client = None
        ip = middleware._get_client_ip(request)
        assert ip == "unknown"

    def test_clean_old_requests(self, middleware):
        now = time.time()
        middleware._requests["test"] = [
            now - 4000,
            now - 100,
            now - 30,
            now,
        ]
        middleware._clean_old_requests("test", now)
        assert all(t > now - 3600 for t in middleware._requests["test"])

    @pytest.mark.asyncio
    async def test_check_limits_within_both(self, middleware):
        now = time.time()
        is_allowed, reason = await middleware._check_limits("fresh_ip", now)
        assert is_allowed is True
        assert reason == ""

    @pytest.mark.asyncio
    async def test_check_limits_minute_exceeded(self, middleware):
        now = time.time()
        middleware._requests["heavy"] = [now - i for i in range(middleware._rpm + 1)]
        is_allowed, reason = await middleware._check_limits("heavy", now)
        assert is_allowed is False
        assert "minute" in reason

    def test_get_remaining(self, middleware):
        middleware._requests["test"] = [time.time() - i * 5 for i in range(3)]
        remaining = middleware._get_remaining("test")
        assert 0 <= remaining <= middleware._rpm

    def test_get_retry_after_with_requests(self, middleware):
        now = time.time()
        middleware._requests["test"] = [now - 10]
        retry = middleware._get_retry_after("test")
        assert 1 <= retry <= 60

    def test_get_retry_after_empty(self, middleware):
        retry = middleware._get_retry_after("empty")
        assert retry == 1


class SlidingWindowRateLimiter:
    """Tests para SlidingWindowRateLimiter."""

    @staticmethod
    def _make_pipeline(execute_result):
        """Creates a pipeline-like object that supports chaining."""
        class _Pipe:
            def zremrangebyscore(self, *a, **kw): return self
            def zcard(self, *a, **kw): return self
            def zadd(self, *a, **kw): return self
            def expire(self, *a, **kw): return self
            async def execute(self): return execute_result
        return _Pipe()

    @pytest.mark.asyncio
    async def test_is_allowed_without_redis(self):
        from src.presentation.api.middleware.rate_limit_middleware import (
            SlidingWindowRateLimiter as SWL,
        )
        limiter = SWL(redis_client=None)
        allowed, remaining = await limiter.is_allowed("test")
        assert allowed is True
        assert remaining == 60

    @pytest.mark.asyncio
    async def test_is_allowed_with_redis(self):
        from src.presentation.api.middleware.rate_limit_middleware import (
            SlidingWindowRateLimiter as SWL,
        )
        redis_mock = AsyncMock()
        redis_mock.pipeline.return_value = self._make_pipeline([None, 3, None, None])

        limiter = SWL(redis_client=redis_mock, requests_per_minute=10)
        allowed, remaining = await limiter.is_allowed("test_id")
        assert allowed is True
        assert remaining == 6

    @pytest.mark.asyncio
    async def test_is_allowed_exceeded_with_redis(self):
        from src.presentation.api.middleware.rate_limit_middleware import (
            SlidingWindowRateLimiter as SWL,
        )
        redis_mock = AsyncMock()
        redis_mock.pipeline.return_value = self._make_pipeline([None, 10, None, None])

        limiter = SWL(redis_client=redis_mock, requests_per_minute=5)
        allowed, remaining = await limiter.is_allowed("blocked")
        assert allowed is False

    @pytest.mark.asyncio
    async def test_is_allowed_redis_error(self):
        from src.presentation.api.middleware.rate_limit_middleware import (
            SlidingWindowRateLimiter as SWL,
        )
        redis_mock = AsyncMock()
        redis_mock.pipeline.side_effect = Exception("Redis connection error")

        limiter = SWL(redis_client=redis_mock)
        allowed, remaining = await limiter.is_allowed("error_test")
        assert allowed is True
        assert remaining == 60



class TestTraceMiddleware:
    """Tests para TraceMiddleware."""

    @pytest.fixture
    def middleware(self):
        from src.presentation.api.middleware.trace_middleware import TraceMiddleware
        mock_app = MagicMock(spec=ASGIApp)
        return TraceMiddleware(mock_app)

    @pytest.mark.asyncio
    async def test_dispatch_adds_trace_headers(self, middleware):
        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        request.headers = {}

        response = Response("OK", status_code=200)
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)
        assert "X-Trace-ID" in result.headers
        assert "X-Span-ID" in result.headers
        assert "X-Parent-Span" in result.headers
        assert result.status_code == 200

    @pytest.mark.asyncio
    async def test_dispatch_preserves_incoming_trace_id(self, middleware):
        trace_id = str(uuid4())
        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        request.headers = {"X-Trace-ID": trace_id}

        response = Response("OK", status_code=200)
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)
        assert result.headers["X-Trace-ID"] == trace_id

    @pytest.mark.asyncio
    async def test_dispatch_handles_exception(self, middleware):
        request = MagicMock(spec=Request)
        request.url.path = "/error"
        request.method = "GET"
        request.headers = {}

        call_next = AsyncMock(side_effect=ValueError("Something broke"))

        with pytest.raises(ValueError, match="Something broke"):
            await middleware.dispatch(request, call_next)

    def test_get_or_create_trace_id_returns_incoming(self, middleware):
        request = MagicMock(spec=Request)
        request.headers = {"X-Trace-ID": "incoming-trace"}
        result = middleware._get_or_create_trace_id(request)
        assert result == "incoming-trace"

    def test_get_or_create_trace_id_creates_new(self, middleware):
        request = MagicMock(spec=Request)
        request.headers = {}
        result = middleware._get_or_create_trace_id(request)
        assert result is not None
        assert len(result) > 10


class TestSpanContext:
    """Tests para SpanContext."""

    @pytest.fixture
    def span(self):
        from src.presentation.api.middleware.trace_middleware import SpanContext
        return SpanContext(
            trace_id="trace-1",
            span_id="span-1",
            parent_span_id="parent-1",
        )

    def test_create_span(self, span):
        assert span.trace_id == "trace-1"
        assert span.span_id == "span-1"
        assert span.parent_span_id == "parent-1"

    def test_set_tag(self, span):
        span.set_tag("key1", "value1")
        assert span.tags["key1"] == "value1"

    def test_finish_returns_metadata(self, span):
        span.set_tag("component", "test")
        result = span.finish()
        assert result["trace_id"] == "trace-1"
        assert result["span_id"] == "span-1"
        assert result["parent_span_id"] == "parent-1"
        assert "duration_ms" in result
        assert result["tags"]["component"] == "test"

    def test_context_manager_exit_without_error(self, span):
        with span as s:
            s.set_tag("phase", "testing")
        assert span.tags["phase"] == "testing"

    def test_context_manager_exit_with_error(self, span):
        with pytest.raises(RuntimeError):
            with span:
                raise RuntimeError("test error")



class TestLoggingMiddleware:
    """Tests para LoggingMiddleware."""

    @pytest.fixture
    def middleware(self):
        from src.presentation.api.middleware.logging_middleware import (
            LoggingMiddleware,
        )
        mock_app = MagicMock(spec=ASGIApp)
        return LoggingMiddleware(mock_app)

    @pytest.mark.asyncio
    async def test_dispatch_adds_headers(self, middleware):
        request = MagicMock(spec=Request)
        request.url.path = "/test"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.headers = {"user-agent": "pytest"}

        response = Response("OK", status_code=200)
        call_next = AsyncMock(return_value=response)

        result = await middleware.dispatch(request, call_next)
        assert "X-Trace-ID" in result.headers
        assert "X-Request-ID" in result.headers
        assert "X-Response-Time" in result.headers

    @pytest.mark.asyncio
    async def test_dispatch_handles_exception(self, middleware):
        request = MagicMock(spec=Request)
        request.url.path = "/error"
        request.method = "GET"
        request.client.host = "127.0.0.1"
        request.headers = {}

        call_next = AsyncMock(side_effect=RuntimeError("Server error"))

        with pytest.raises(RuntimeError, match="Server error"):
            await middleware.dispatch(request, call_next)
