"""FastAPI application."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.infrastructure.database import init_db, close_db
from src.shared.config import get_settings
from src.shared.logging import get_logger

from .routes.incidents import router as incidents_router
from .routes.metrics import router as metrics_router
from .routes.auth import router as auth_router

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

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(incidents_router)
    app.include_router(metrics_router)
    app.include_router(auth_router)

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


app = create_app()
