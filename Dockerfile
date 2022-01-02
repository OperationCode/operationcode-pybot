FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /pybot

RUN python3 -m pip install --upgrade pip

RUN pip install pipenv

COPY Pipfile Pipfile.lock /pybot/

RUN pipenv install --system --dev --pre

COPY . /pybot/