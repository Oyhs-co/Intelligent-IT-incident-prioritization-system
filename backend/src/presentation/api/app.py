"""FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.infrastructure.database import close_db, init_db
from src.shared.config import get_settings
from src.shared.exceptions import (
    AIServiceException,
    AuthenticationException,
    AuthorizationException,
    ConflictException,
    DatabaseException,
    NotFoundException,
    ValidationException,
)
from src.shared.logging import get_logger

from .middleware import LoggingMiddleware, RateLimitMiddleware, TraceMiddleware
from .routes.auth import router as auth_router
from .routes.incidents import router as incidents_router
from .routes.metrics import router as metrics_router
from .routes.users import router as users_router

settings = get_settings()
logger = get_logger("app")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for the application."""
    logger.info("Starting application...")

    try:
        await init_db()
        logger.info("Database initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    yield

    logger.info("Shutting down application...")
    await close_db()
    logger.info("Application shutdown complete")


def create_app() -> FastAPI:
    """Creates and configures the FastAPI application."""
    app = FastAPI(
        title="Incident Prioritization System",
        description="API for intelligent IT incident prioritization using AI",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TraceMiddleware)

    app.include_router(incidents_router)
    app.include_router(metrics_router)
    app.include_router(auth_router)
    app.include_router(users_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    _add_exception_handlers(app)

    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "name": "Incident Prioritization System",
            "version": "1.0.0",
            "status": "running",
        }

    @app.get("/health")
    async def health():
        """Health check endpoint."""
        return {"status": "healthy"}

    logger.info("Application configured successfully")
    return app


def _add_exception_handlers(app: FastAPI) -> None:
    """Registra los exception handlers globales."""

    @app.exception_handler(NotFoundException)
    async def not_found_handler(request: Request, exc: NotFoundException):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": exc.code, "detail": exc.message},
        )

    @app.exception_handler(ValidationException)
    async def validation_handler(request: Request, exc: ValidationException):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": exc.code, "detail": exc.message},
        )

    @app.exception_handler(AuthenticationException)
    async def auth_handler(request: Request, exc: AuthenticationException):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": exc.code, "detail": exc.message},
        )

    @app.exception_handler(AuthorizationException)
    async def authorization_handler(request: Request, exc: AuthorizationException):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": exc.code, "detail": exc.message},
        )

    @app.exception_handler(ConflictException)
    async def conflict_handler(request: Request, exc: ConflictException):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": exc.code, "detail": exc.message},
        )

    @app.exception_handler(DatabaseException)
    async def database_handler(request: Request, exc: DatabaseException):
        logger.error(f"Database error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": exc.code, "detail": "A database error occurred"},
        )

    @app.exception_handler(AIServiceException)
    async def ai_handler(request: Request, exc: AIServiceException):
        logger.error(f"AI service error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"error": exc.code, "detail": exc.message},
        )

    @app.exception_handler(Exception)
    async def global_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "INTERNAL_ERROR", "detail": "An unexpected error occurred"},
        )


app = create_app()
