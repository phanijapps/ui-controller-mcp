# ui-controller-mcp

A lightweight Model Context Protocol (MCP) server built on [FastMCP](https://github.com/modelcontextprotocol/fastmcp) that exposes desktop UI control tools over Server-Sent Events (SSE). It provides structured tool definitions, JSON Schema contracts, and optional ngrok tunneling for remote access.

## Features
- MCP-compatible SSE streaming at `/sse` with tool metadata and heartbeats.
- Tool execution via `/invoke` with consistent JSON success/error envelopes.
- Desktop automation abstracted into interchangeable controllers (PyAutoGUI-backed when available, safe no-op otherwise).
- Request/response logging and safety guards against destructive commands.
- Ready for local and remote usage with ngrok support.

## Getting started

### Prerequisites
- Python 3.12+
- Optional: `ngrok` auth token for remote tunneling (create a `.env` file using `.env.example`).

### Installation
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running locally
```bash
./start.sh
```
Visit `http://localhost:8000/health` to confirm the server is up.

### Running with ngrok (remote)
```bash
cp .env.example .env
# add your NGROK_AUTH_TOKEN to .env
./start-remote.sh
```
On startup the server prints the public ngrok URL once the tunnel is established.

## API overview
- `GET /sse`: SSE stream that emits a `ready` event with tool schemas followed by periodic `ping` events.
- `POST /messages`: MCP message transport handled by FastMCP for tool invocation.
- `GET /health`: Lightweight health check.

### SSE handshake sample
Connect to `GET /sse` and expect an initial event similar to:
```
event: ready
data: {"protocol": "mcp/1.0", "server": {"name": "ui-controller-mcp", "version": "0.1.0"}, "tools": [...], "timestamp": "..."}
```
Followed by `ping` events every 10 seconds.

## Project structure
```
ui_controller_mcp/
├── desktop/        # UI automation controllers
├── routes/         # FastAPI route handlers (/sse, /invoke)
├── server/         # FastAPI app factory and ngrok integration
├── tools/          # Tool schemas and execution dispatcher
└── utils/          # Logging and safety helpers
```

## Testing
```bash
pytest
```

## Security & safety
- Safety guard rejects obviously destructive launch commands and text inputs.
- Logging middleware records inbound requests and responses for observability.
- No-op controller ensures safe execution in environments without a desktop UI.
