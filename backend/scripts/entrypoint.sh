#!/bin/bash
set -e

echo "[entrypoint] Inicializando base de datos..."
python scripts/init_db.py

echo "[entrypoint] Ejecutando seeds (opcional)..."
python scripts/seed_data.py 2>/dev/null || echo "[entrypoint] Seeds omitidos o ya ejecutados"

echo "[entrypoint] Iniciando servidor..."
exec uvicorn src.main:app --host 0.0.0.0 --port "${PORT:-8000}"
