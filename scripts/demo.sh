#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
if [ -x .venv/bin/python ]; then P=.venv/bin/python; else P=python3; fi
exec "$P" src/server.py
