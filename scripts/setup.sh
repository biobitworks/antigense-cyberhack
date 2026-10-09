#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
: "${ANTIGENSE_PYTHON:=python3}"
"$ANTIGENSE_PYTHON" -m venv .venv
.venv/bin/python -m pip install 'semgrep==1.180.0'
