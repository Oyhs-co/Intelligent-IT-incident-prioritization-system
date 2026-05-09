# Stage 1: Build dependencies
FROM python:3.14-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Evita timeouts de pip/poetry
ENV PIP_DEFAULT_TIMEOUT=1000 \
    POETRY_REQUESTS_TIMEOUT=1000 \
    POETRY_VIRTUALENVS_CREATE=false

COPY pyproject.toml poetry.lock* ./

RUN pip install --no-cache-dir poetry && \
    poetry config installer.max-workers 10 && \
    poetry install --no-interaction --no-ansi --no-root --only main

# Stage 2: Runtime
FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONPATH=/app

COPY --from=builder /usr/local/lib/python3.14/site-packages /usr/local/lib/python3.14/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY . .

RUN mkdir -p logs data && \
    chmod 777 logs data && \
    chmod +x scripts/entrypoint.sh

EXPOSE 8000

ENV PYTHONPATH=/app

ENTRYPOINT ["./scripts/entrypoint.sh"]