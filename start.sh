#!/usr/bin/env bash
set -euo pipefail
export PYTHONPATH=$(pwd)
uvicorn ui_controller_mcp.server.app:app --host 0.0.0.0 --port 8000
