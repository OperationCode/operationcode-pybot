# Pin the exact patch release and Debian suite. A new tag invalidates the CI
# build cache, so the apt-get upgrade below runs again and picks up security fixes.
FROM python:3.15.0-slim-trixie AS base

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends ca-certificates wget && rm -rf /var/lib/apt/lists/*

FROM base AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=on \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.5.1 \
    POETRY_HOME="/opt/poetry" \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_OPTIONS_NO_PIP=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry into its own isolated environment
RUN --mount=type=cache,target=/root/.cache \
    curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

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

# pip is not used at runtime, and its vendored packages carry CVEs
RUN python -m pip uninstall -y pip

# Copy application and virtual environment from builder
COPY --from=builder /app ./

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
    CMD wget -q -O /dev/null http://localhost:5000/health || exit 1

CMD ["python", "-m", "pybot"]
