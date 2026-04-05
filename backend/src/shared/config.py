"""Configuración centralizada del proyecto."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Database
    database_url: str = "sqlite+aiosqlite:///./data/incidents.db"
    database_url_sync: str = "sqlite:///./data/incidents.db"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Security
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # AI/ML
    model_path: str = "../IA-module/models"
    vectorizer_path: str = "../IA-module/models"
    embedding_model: str = "all-MiniLM-L6-v2"

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/app.log"

    # CORS
    cors_origins: str = "http://localhost:3000,http://localhost:8080"

    # Prometheus
    enable_prometheus: bool = True

    # Application
    app_name: str = "Incident Prioritization System"
    app_version: str = "1.0.0"
    debug: bool = False

    @property
    def cors_origins_list(self) -> list[str]:
        """Retorna lista de orígenes CORS."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Verifica si es entorno de producción."""
        return "postgresql" in self.database_url.lower()

    @property
    def is_development(self) -> bool:
        """Verifica si es entorno de desarrollo."""
        return "sqlite" in self.database_url.lower()

    def get_database_config(self) -> dict[str, Any]:
        """Retorna configuración de base de datos."""
        return {
            "url": self.database_url,
            "echo": self.debug,
            "pool_pre_ping": True,
        }


@lru_cache
def get_settings() -> Settings:
    """Obtiene instancia singleton de configuración."""
    return Settings()
