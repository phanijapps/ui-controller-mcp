import asyncio

from ui_controller_mcp.server.app import server


def test_fastmcp_registers_expected_tools():
    tools = asyncio.run(server.get_tools())

    assert {
        "launch_app",
        "list_windows",
        "focus_window",
        "click",
        "type_text",
        "scroll",
        "screenshot",
        "get_bytes",
        "perceive",
        "reason",
        "manage_credentials",
        "type_password",
        "handle_sudo",
        "find_image",
        "wait_for_image",
        "run_terminal_cmd",
        "check_notification",
        "use_skill",
        "get_agent_history",
    }.issubset(tools.keys())


def test_tool_schemas_propagate_to_fastmcp():
    tools = asyncio.run(server.get_tools())

    assert tools["click"].output_schema["type"] == "object"
    assert tools["screenshot"].output_schema["properties"]["captured_at"]["type"] == "string"
