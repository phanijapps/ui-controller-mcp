from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.server.http import create_sse_app
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ui_controller_mcp.desktop.factory import get_controller
from ui_controller_mcp.server.ngrok_manager import NgrokManager
from ui_controller_mcp.tools.definitions import tool_definitions
from ui_controller_mcp.tools.handlers import ToolExecutor
from ui_controller_mcp.utils.logging import configure_logging
from ui_controller_mcp.utils.safety import SafetyGuard

logger = configure_logging()

controller = get_controller()
safety_guard = SafetyGuard()
_tool_metadata = {tool["name"]: tool for tool in tool_definitions()}
tool_executor = ToolExecutor(controller, safety_guard)
ngrok_manager = NgrokManager(port=8000)


def _tool_info(name: str) -> dict[str, Any]:
    """Return the stored metadata for the given tool name."""

    return _tool_metadata[name]


@asynccontextmanager
async def _lifespan(_: FastMCP):
    """Manage optional ngrok lifecycle for the MCP server."""

    url = ngrok_manager.start()
    if url:
        logger.info("ngrok tunnel established: %s", url)
        print(f"ngrok tunnel available at {url}")

    try:
        yield
    finally:
        ngrok_manager.stop()


server = FastMCP(
    name="ui-controller-mcp",
    version="0.1.0",
    instructions="Desktop UI controller built with FastMCP.",
    lifespan=_lifespan,
)


@server.tool(
    name="launch_app",
    description=_tool_info("launch_app")["description"],
    output_schema=_tool_info("launch_app")["output_schema"],
)
def launch_app(target: str) -> dict[str, Any]:
    """Launch an application by name or path."""

    return tool_executor.execute("launch_app", {"target": target})


@server.tool(
    name="list_windows",
    description=_tool_info("list_windows")["description"],
    output_schema=_tool_info("list_windows")["output_schema"],
)
def list_windows() -> dict[str, Any]:
    """List currently open windows."""

    return tool_executor.execute("list_windows", {})


@server.tool(
    name="focus_window",
    description=_tool_info("focus_window")["description"],
    output_schema=_tool_info("focus_window")["output_schema"],
)
def focus_window(title: str) -> dict[str, Any]:
    """Focus a window by matching its title."""

    return tool_executor.execute("focus_window", {"title": title})


@server.tool(
    name="click",
    description=_tool_info("click")["description"],
    output_schema=_tool_info("click")["output_schema"],
)
def click(
    x: int | None = None,
    y: int | None = None,
    button: Literal["left", "right", "middle"] = "left",
) -> dict[str, Any]:
    """Perform a mouse click at the provided coordinates."""

    return tool_executor.execute("click", {"x": x, "y": y, "button": button})


@server.tool(
    name="type_text",
    description=_tool_info("type_text")["description"],
    output_schema=_tool_info("type_text")["output_schema"],
)
def type_text(text: str) -> dict[str, Any]:
    """Type text into the active window with safety checks."""

    return tool_executor.execute("type_text", {"text": text})


@server.tool(
    name="scroll",
    description=_tool_info("scroll")["description"],
    output_schema=_tool_info("scroll")["output_schema"],
)
def scroll(
    amount: int,
    direction: Literal["vertical", "horizontal"] = "vertical",
) -> dict[str, Any]:
    """Scroll vertically or horizontally by the provided amount."""

    return tool_executor.execute("scroll", {"amount": amount, "direction": direction})


@server.tool(
    name="screenshot",
    description=_tool_info("screenshot")["description"],
    output_schema=_tool_info("screenshot")["output_schema"],
)
def screenshot() -> dict[str, Any]:
    """Capture a screenshot of the current screen."""

    return tool_executor.execute("screenshot", {})


@server.tool(
    name="get_bytes",
    description=_tool_info("get_bytes")["description"],
    output_schema=_tool_info("get_bytes")["output_schema"],
)
def get_bytes(path: str) -> dict[str, Any]:
    """Read a file from disk and return its contents encoded as base64."""

    return tool_executor.execute("get_bytes", {"path": path})


async def health(_: Request) -> JSONResponse:  # pragma: no cover - trivial
    """Lightweight health endpoint for container orchestrators."""

    return JSONResponse({"status": "ok"})


app = create_sse_app(
    server,
    message_path="/messages",
    sse_path="/sse",
    routes=[Route("/health", health)],
)
