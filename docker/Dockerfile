FROM python:3.10-alpine AS base

FROM base as builder

ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && \
    apk add --no-cache build-base musl-dev python3-dev libffi-dev openssl-dev

COPY Pipfile Pipfile.lock ./

RUN pip install --upgrade pip

RUN pip install pipenv

# The `dev` stage creates an image and runs the application with development settings
FROM builder as dev

ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . ./

RUN pipenv install --dev

ENTRYPOINT ["pipenv", "run", "python3", "main.py"]

# The `prod` stage creates an image that will run the application with production
#  settings
FROM builder As prod

ENV PYTHONDONTWRITEBYTECODE 1

RUN pipenv install

ENTRYPOINT ["pipenv", "run", "python3", "main.py"]
