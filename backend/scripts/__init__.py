"""Scripts de administración."""

from .init_db import main as init_db
from .seed_data import main as seed_data

__all__ = ["init_db", "seed_data"]
