"""Script para inicializar la base de datos."""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.database import init_db, close_db
from src.shared.logging import get_logger

logger = get_logger("init_db")


async def main():
    """Inicializa la base de datos."""
    logger.info("Initializing database...")

    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return 1
    finally:
        await close_db()

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
