FROM python:3.10-alpine AS base

FROM base as builder

ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add --no-cache build-base musl-dev python3-dev libffi-dev openssl-dev

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir 'poetry==1.5.1'

# The `dev` stage creates an image and runs the application with development settings
FROM builder as dev

ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY .. ./

RUN poetry install

ENTRYPOINT ["poetry", "run", "python3", "main.py"]

# The `prod` stage creates an image that will run the application with production
#  settings
FROM builder As prod

WORKDIR /app

COPY .. ./

ENV PYTHONDONTWRITEBYTECODE 1

RUN poetry config virtualenvs.create false

RUN poetry install

ENTRYPOINT ["python3", "main.py"]
