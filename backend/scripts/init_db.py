"""Script para inicializar la base de datos.

Uso:
    python scripts/init_db.py

Crea todas las tablas definidas en los modelos SQLAlchemy
si aún no existen. Es idempotente: ejecutable múltiples veces.
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import models so they are registered with Base.metadata
from src.infrastructure.database import close_db, init_db
from src.infrastructure.database.models import (  # noqa: F401
    CommentModel,
    IncidentEventModel,
    IncidentModel,
    IncidentSimilarityModel,
    MetricModel,
    UserModel,
)
from src.shared.logging import get_logger

logger = get_logger("init_db")


async def main() -> int:
    """Inicializa la base de datos creando tablas si no existen."""
    logger.info("Inicializando base de datos...")

    try:
        await init_db()
        logger.info("Base de datos inicializada correctamente")
    except Exception as e:
        logger.error(f"Error al inicializar base de datos: {e}")
        return 1
    finally:
        await close_db()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
