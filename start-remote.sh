#!/usr/bin/env bash
set -euo pipefail

if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

if [ -z "${NGROK_AUTH_TOKEN:-}" ]; then
  echo "NGROK_AUTH_TOKEN is not set. Remote tunneling will be skipped." >&2
fi

export PYTHONPATH=$(pwd)
PORT=${PORT:-8000}

echo "Starting ui-controller-mcp on port ${PORT} with ngrok support..."
.venv/bin/uvicorn ui_controller_mcp.server.app:app --host 0.0.0.0 --port "${PORT}"
