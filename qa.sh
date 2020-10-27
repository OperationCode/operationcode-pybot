#!/bin/sh

set -xe

isort Bot
rstcheck -r .
pydocstyle Bot
flake8 Bot