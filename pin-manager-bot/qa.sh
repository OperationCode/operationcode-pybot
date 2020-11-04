#!/bin/sh

set -xe

isort pin-manager-bot
rstcheck -r pin-manager-bot
pydocstyle pin-manager-bot
flake8 pin-manager-bot