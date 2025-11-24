import base64
from pathlib import Path

from ui_controller_mcp.desktop.noop_controller import NoOpDesktopController
from ui_controller_mcp.tools.definitions import tool_definitions
from ui_controller_mcp.tools.handlers import ToolExecutor
from ui_controller_mcp.utils.safety import SafetyGuard


def test_tool_definitions_include_required_tools():
    names = {tool["name"] for tool in tool_definitions()}
    assert {
        "launch_app",
        "list_windows",
        "focus_window",
        "click",
        "type_text",
        "scroll",
        "screenshot",
        "get_bytes",
    }.issubset(names)


def test_tool_schemas_are_objects():
    definitions = tool_definitions()
    for tool in definitions:
        assert tool["input_schema"]["type"] == "object"
        assert tool["output_schema"]["type"] == "object"


def test_get_bytes_encodes_file_content(tmp_path: Path):
    file_path = tmp_path / "sample.txt"
    payload = b"hello world"
    file_path.write_bytes(payload)

    executor = ToolExecutor(NoOpDesktopController(), SafetyGuard())
    result = executor.execute("get_bytes", {"path": str(file_path)})

    assert result["success"] is True
    assert result["data"]["path"] == str(file_path.resolve())
    assert result["data"]["size"] == len(payload)
    assert result["data"]["base64_data"] == base64.b64encode(payload).decode("ascii")


def test_get_bytes_rejects_missing_file(tmp_path: Path):
    executor = ToolExecutor(NoOpDesktopController(), SafetyGuard())
    missing_file = tmp_path / "absent.txt"

    result = executor.execute("get_bytes", {"path": str(missing_file)})

    assert result["success"] is False
    assert "File not found" in result.get("error", "")
