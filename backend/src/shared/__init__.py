"""Shared module."""

from .config import Settings, get_settings
from .logging import Logger, get_logger, set_trace_context, generate_trace_id
from .exceptions import (
    AppException,
    NotFoundException,
    ValidationException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    DatabaseException,
    AIServiceException,
)

__all__ = [
    "Settings",
    "get_settings",
    "Logger",
    "get_logger",
    "set_trace_context",
    "generate_trace_id",
    "AppException",
    "NotFoundException",
    "ValidationException",
    "AuthenticationException",
    "AuthorizationException",
    "ConflictException",
    "DatabaseException",
    "AIServiceException",
]
