FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock* ./

RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root --no-directory

COPY . .

RUN mkdir -p logs data && chmod 777 logs data && \
    chmod +x scripts/entrypoint.sh

EXPOSE 8000

ENV PYTHONPATH=/app

ENTRYPOINT ["./scripts/entrypoint.sh"]
