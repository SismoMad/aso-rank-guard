#!/bin/bash
set -e

ROOT_DIR="/root/aso-rank-guard"
VENV_PY="$ROOT_DIR/venv_bot/bin/python"
LOG_FILE="$ROOT_DIR/logs/daily_tracking.log"

mkdir -p "$ROOT_DIR/logs"
cd "$ROOT_DIR"

$VENV_PY "$ROOT_DIR/scripts/daily_tracking.py" >> "$LOG_FILE" 2>&1
