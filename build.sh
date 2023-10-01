#!/usr/bin/env bash
set -o errexit

pip install --upgrade pip

pip install 'poetry==1.3.1'

poetry config virtualenvs.create false

poetry install