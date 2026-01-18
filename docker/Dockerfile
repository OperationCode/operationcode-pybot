FROM python:3.14-slim AS base

RUN apt-get update && apt-get upgrade -y && apt-get install wget -y && apt clean

FROM base AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install poetry
RUN pip install --no-cache-dir poetry

# Copy dependency files
COPY pyproject.toml poetry.lock README.md logging.yml manage.py ./
COPY pybot ./pybot

# Install dependencies into .venv in project
RUN poetry install --only=main --no-interaction --no-cache --compile && \
    rm -rf $POETRY_CACHE_DIR

# Production image
FROM base AS prod

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Copy application and virtual environment from builder
COPY --from=builder /app ./

CMD ["python", "-m", "pybot"]
