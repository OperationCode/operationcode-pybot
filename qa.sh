#!/bin/sh

set -xe

rstcheck -r .
pydocstyle Bot
flake8 Bot