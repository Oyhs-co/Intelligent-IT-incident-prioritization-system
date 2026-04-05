"""Logging centralizado con soporte estructurado."""

from __future__ import annotations

import sys
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4
from contextvars import ContextVar
from functools import lru_cache

from loguru import logger as loguru_logger


trace_id_var: ContextVar[Optional[str]] = ContextVar("trace_id", default=None)
span_id_var: ContextVar[Optional[str]] = ContextVar("span_id", default=None)
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


class Logger:
    """Logger centralizado con trazabilidad y métricas."""

    def __init__(self, service_name: str = "incident-service"):
        self.service_name = service_name
        self._configure()

    def _configure(self) -> None:
        """Configura loguru con formateo personalizado."""
        loguru_logger.remove()

        loguru_logger.add(
            sys.stdout,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                "{message}"
            ),
            level="DEBUG",
            colorize=True,
            backtrace=True,
            diagnose=True,
        )

        loguru_logger.add(
            "logs/{time:YYYY-MM-DD}.log",
            rotation="00:00",
            retention="30 days",
            compression="zip",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                "{name}:{function}:{line} | {message}"
            ),
            level="INFO",
            backtrace=True,
        )

        loguru_logger.add(
            "logs/errors.log",
            rotation="00:00",
            retention="90 days",
            level="ERROR",
            format=(
                "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | "
                "{name}:{function}:{line} | {message}\n{exception}"
            ),
        )

    def _build_context(self, **kwargs: Any) -> dict[str, Any]:
        """Construye contexto para el log."""
        return {
            "service": self.service_name,
            "trace_id": trace_id_var.get(),
            "span_id": span_id_var.get(),
            "request_id": request_id_var.get(),
            **kwargs,
        }

    def _format_message(self, message: str, context: dict[str, Any]) -> str:
        """Formatea mensaje con contexto."""
        parts = [message]
        if context:
            ctx_parts = [f"{k}={v}" for k, v in context.items() if v is not None]
            if ctx_parts:
                parts.append(f"[{' '.join(ctx_parts)}]")
        return " ".join(parts)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log level DEBUG."""
        context = self._build_context(**kwargs)
        loguru_logger.debug(self._format_message(message, context))

    def info(self, message: str, **kwargs: Any) -> None:
        """Log level INFO."""
        context = self._build_context(**kwargs)
        loguru_logger.info(self._format_message(message, context))

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log level WARNING."""
        context = self._build_context(**kwargs)
        loguru_logger.warning(self._format_message(message, context))

    def error(self, message: str, **kwargs: Any) -> None:
        """Log level ERROR."""
        context = self._build_context(**kwargs)
        loguru_logger.error(self._format_message(message, context))

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log level CRITICAL."""
        context = self._build_context(**kwargs)
        loguru_logger.critical(self._format_message(message, context))

    def log_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: str = "gauge",
        **labels: Any,
    ) -> None:
        """Registra una métrica en los logs."""
        context = self._build_context(
            metric_name=metric_name,
            metric_type=metric_type,
            **labels,
        )
        loguru_logger.info(
            f"METRIC: {metric_name}={value} type={metric_type}",
            **context,
        )

    def log_execution_time(
        self,
        operation: str,
        duration_ms: float,
        **context: Any,
    ) -> None:
        """Registra tiempo de ejecución."""
        ctx = self._build_context(operation=operation, **context)
        loguru_logger.info(
            f"Execution: {operation} completed in {duration_ms:.2f}ms",
            **ctx,
        )

    def log_db_query(
        self,
        query_type: str,
        duration_ms: float,
        rows_affected: int = 0,
    ) -> None:
        """Registra una query de base de datos."""
        loguru_logger.debug(
            f"DB {query_type}: {duration_ms:.2f}ms, rows={rows_affected}",
            **self._build_context(query_type="database"),
        )

    def log_ai_prediction(
        self,
        incident_id: str,
        priority: int,
        confidence: float,
        processing_time_ms: float,
        features: list[str],
    ) -> None:
        """Registra una predicción de IA."""
        loguru_logger.info(
            f"AI Prediction: incident={incident_id} priority={priority} "
            f"confidence={confidence:.2f} time={processing_time_ms:.2f}ms",
            **self._build_context(
                incident_id=incident_id,
                predicted_priority=priority,
                confidence=confidence,
                processing_time_ms=processing_time_ms,
                features=features,
            ),
        )

    def log_api_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        user_id: Optional[str] = None,
    ) -> None:
        """Registra una petición API."""
        loguru_logger.info(
            f"API {method} {path} -> {status_code} ({duration_ms:.2f}ms)",
            **self._build_context(
                method=method,
                path=path,
                status_code=status_code,
                duration_ms=duration_ms,
                user_id=user_id,
            ),
        )


@lru_cache
def get_logger(service: Optional[str] = None) -> Logger:
    """Obtiene una instancia del logger."""
    name = service or "incident-service"
    return Logger(name)


def set_trace_context(
    trace_id: Optional[str] = None,
    request_id: Optional[str] = None,
) -> None:
    """Establece contexto de trazabilidad."""
    trace_id_var.set(trace_id or str(uuid4()))
    span_id_var.set(str(uuid4())[:8])
    request_id_var.set(request_id or trace_id_var.get())


def generate_trace_id() -> str:
    """Genera un nuevo ID de trazabilidad."""
    return str(uuid4())
