from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from typing import AsyncGenerator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

router = APIRouter()


def _format_sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


@router.get("/sse")
async def sse_stream(request: Request) -> StreamingResponse:
    async def event_publisher() -> AsyncGenerator[str, None]:
        payload = {
            "protocol": "mcp/1.0",
            "server": {"name": "ui-controller-mcp", "version": "0.1.0"},
            "tools": request.app.state.tool_definitions,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        yield _format_sse("ready", payload)

        while True:
            if await request.is_disconnected():
                break
            heartbeat = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "status": "ok",
            }
            yield _format_sse("ping", heartbeat)
            await asyncio.sleep(10)

    return StreamingResponse(event_publisher(), media_type="text/event-stream")
