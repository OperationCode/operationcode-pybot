FROM python:3.7-alpine AS base

FROM base as builder

ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add --no-cache build-base musl-dev python3-dev

RUN python -m venv /opt/venv
# Make sure we use the virtualenv:
ENV PATH="/opt/venv/bin:$PATH"

COPY poetry.lock pyproject.toml ./

RUN pip install poetry && \
    poetry config settings.virtualenvs.create false && \
    poetry install --no-dev --no-interaction

# The `built-image` stage is the base for all remaining images
# Pulls all of the built dependencies from the builder stage
FROM base as built-image
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# copy installed deps from builder image
COPY --from=builder /opt/venv /opt/venv

# Make sure we use the virtualenv
ENV PATH="/opt/venv/bin:$PATH"

# The `app` stage is used as the base for images that don't
# need the development dependencies
FROM built-image as app

COPY . /src
WORKDIR /src

# The `Prod` stage creates an image that will run the application using a
# production webserver and the `environments/production.py` configuration
FROM app As Prod
ENTRYPOINT ["python3", "-m", "pybot"]
