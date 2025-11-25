from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Literal

from fastmcp import FastMCP
from fastmcp.server.http import create_sse_app
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route

from ui_controller_mcp.ai.client import AIClient
from ui_controller_mcp.desktop.factory import get_controller
from ui_controller_mcp.server.ngrok_manager import NgrokManager
from ui_controller_mcp.tools.definitions import tool_definitions
from ui_controller_mcp.tools.handlers import ToolExecutor
from ui_controller_mcp.utils.logging import configure_logging
from ui_controller_mcp.utils.safety import SafetyGuard

logger = configure_logging()

controller = get_controller()
safety_guard = SafetyGuard()
ai_client = AIClient()
_tool_metadata = {tool["name"]: tool for tool in tool_definitions()}
tool_executor = ToolExecutor(controller, safety_guard, ai_client)
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
def type_text(text: str, enter: bool = False) -> dict[str, Any]:
    """Type text into the active window with safety checks."""

    return tool_executor.execute("type_text", {"text": text, "enter": enter})


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


@server.tool(
    name="perceive",
    description=_tool_info("perceive")["description"],
    output_schema=_tool_info("perceive")["output_schema"],
)
def perceive(instruction: str = "") -> dict[str, Any]:
    """Analyze the current screen state using vision AI."""

    return tool_executor.execute("perceive", {"instruction": instruction})


@server.tool(
    name="reason",
    description=_tool_info("reason")["description"],
    output_schema=_tool_info("reason")["output_schema"],
)
def reason(analysis: str, goal: str) -> dict[str, Any]:
    """Plan the next action based on UI analysis and goal."""

    return tool_executor.execute("reason", {"analysis": analysis, "goal": goal})


@server.tool(
    name="manage_credentials",
    description=_tool_info("manage_credentials")["description"],
    output_schema=_tool_info("manage_credentials")["output_schema"],
)
def manage_credentials(
    action: Literal["set", "check"],
    id: str,
    value: str | None = None,
) -> dict[str, Any]:
    """Manage secure credentials."""

    return tool_executor.execute(
        "manage_credentials", {"action": action, "id": id, "value": value}
    )


@server.tool(
    name="type_password",
    description=_tool_info("type_password")["description"],
    output_schema=_tool_info("type_password")["output_schema"],
)
def type_password(id: str, enter: bool = False) -> dict[str, Any]:
    """Type a stored password securely."""

    return tool_executor.execute("type_password", {"id": id, "enter": enter})


@server.tool(
    name="handle_sudo",
    description=_tool_info("handle_sudo")["description"],
    output_schema=_tool_info("handle_sudo")["output_schema"],
)
def handle_sudo() -> dict[str, Any]:
    """Handle sudo prompt by typing the stored sudo password."""

    return tool_executor.execute("handle_sudo", {})


@server.tool(
    name="find_image",
    description=_tool_info("find_image")["description"],
    output_schema=_tool_info("find_image")["output_schema"],
)
def find_image(template_path: str, confidence: float = 0.8) -> dict[str, Any]:
    """Find a UI element on screen using an image template."""

    return tool_executor.execute(
        "find_image", {"template_path": template_path, "confidence": confidence}
    )


@server.tool(
    name="wait_for_image",
    description=_tool_info("wait_for_image")["description"],
    output_schema=_tool_info("wait_for_image")["output_schema"],
)
def wait_for_image(
    template_path: str, timeout: int = 10, confidence: float = 0.8
) -> dict[str, Any]:
    """Wait until a specific image appears on the screen."""

    return tool_executor.execute(
        "wait_for_image",
        {"template_path": template_path, "timeout": timeout, "confidence": confidence},
    )


@server.tool(
    name="run_terminal_cmd",
    description=_tool_info("run_terminal_cmd")["description"],
    output_schema=_tool_info("run_terminal_cmd")["output_schema"],
)
def run_terminal_cmd(command: str) -> dict[str, Any]:
    """Run a shell command in the background and return the output."""

    return tool_executor.execute("run_terminal_cmd", {"command": command})


@server.tool(
    name="check_notification",
    description=_tool_info("check_notification")["description"],
    output_schema=_tool_info("check_notification")["output_schema"],
)
def check_notification(timeout: int = 5) -> dict[str, Any]:
    """Check for recent system notifications."""

    return tool_executor.execute("check_notification", {"timeout": timeout})


@server.tool(
    name="use_skill",
    description=_tool_info("use_skill")["description"],
    output_schema=_tool_info("use_skill")["output_schema"],
)
def use_skill(skill: str, params: dict[str, Any]) -> dict[str, Any]:
    """Execute a high-level application skill."""

    return tool_executor.execute("use_skill", {"skill": skill, "params": params})


@server.tool(
    name="get_agent_history",
    description=_tool_info("get_agent_history")["description"],
    output_schema=_tool_info("get_agent_history")["output_schema"],
)
def get_agent_history(limit: int = 10) -> dict[str, Any]:
    """Retrieve the history of recent actions performed by the agent."""

    return tool_executor.execute("get_agent_history", {"limit": limit})


async def health(_: Request) -> JSONResponse:  # pragma: no cover - trivial
    """Lightweight health endpoint for container orchestrators."""

    return JSONResponse({"status": "ok"})


app = create_sse_app(
    server,
    message_path="/messages",
    sse_path="/sse",
    routes=[Route("/health", health)],
)
