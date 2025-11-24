from __future__ import annotations

from typing import Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ui_controller_mcp.desktop.factory import get_controller
from ui_controller_mcp.routes import invoke, sse
from ui_controller_mcp.server.ngrok_manager import NgrokManager
from ui_controller_mcp.tools.definitions import tool_definitions
from ui_controller_mcp.tools.handlers import ToolExecutor
from ui_controller_mcp.utils.logging import configure_logging
from ui_controller_mcp.utils.safety import SafetyGuard

logger = configure_logging()


def create_app() -> FastAPI:
    app = FastAPI(title="ui-controller-mcp", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next: Callable[[Request], Response]):
        logger.info("Incoming request %s %s", request.method, request.url)
        response = await call_next(request)
        logger.info("Response status %s for %s", response.status_code, request.url)
        return response

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):  # type: ignore[override]
        logger.exception("Unhandled error: %s", exc)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": "Internal server error"},
        )

    app.include_router(sse.router)
    app.include_router(invoke.router)

    app.state.tool_definitions = tool_definitions()
    app.state.tool_executor = ToolExecutor(get_controller(), SafetyGuard())
    app.state.ngrok_manager = NgrokManager(port=8000)

    @app.on_event("startup")
    async def start_ngrok() -> None:
        url = app.state.ngrok_manager.start()
        if url:
            logger.info("ngrok tunnel established: %s", url)
            print(f"ngrok tunnel available at {url}")

    @app.on_event("shutdown")
    async def stop_ngrok() -> None:
        app.state.ngrok_manager.stop()

    @app.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/schema")
    async def schema() -> dict[str, object]:
        return {
            "protocol": "mcp/1.0",
            "tools": app.state.tool_definitions,
        }

    return app


app = create_app()
