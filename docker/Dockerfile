FROM python:3.7-alpine AS base

FROM base AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONUNBUFFERED=1

RUN apk update
RUN apk upgrade
RUN apk add --no-cache build-base musl-dev python3-dev libffi-dev openssl-dev

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY poetry.lock pyproject.toml ./

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --only=main --compile --no-interaction --no-cache

# The `built-image` stage is the base for all remaining images
# Pulls all of the built dependencies from the builder stage
FROM base AS built-image
ENV PIP_DISABLE_PIP_VERSION_CHECK=on
ENV PYTHONUNBUFFERED=1

RUN apk update
RUN apk upgrade
RUN rm -rf /var/cache/apk/*

# copy installed deps from builder image
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# The `app` stage is used as the base for images that don't
# need the development dependencies
FROM built-image AS app

COPY . /src
WORKDIR /src

# The `prod` stage creates an image that will run the application using a
# production webserver and the `environments/production.py` configuration
FROM app AS prod
ENTRYPOINT ["python3", "-m", "pybot"]
