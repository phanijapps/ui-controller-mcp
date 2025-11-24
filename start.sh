#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=$(pwd)
.venv/bin/uvicorn ui_controller_mcp.server.app:app --host 0.0.0.0 --port 8000
