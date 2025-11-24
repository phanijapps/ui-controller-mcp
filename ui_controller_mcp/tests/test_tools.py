from ui_controller_mcp.tools.definitions import tool_definitions


def test_tool_definitions_include_required_tools():
    names = {tool["name"] for tool in tool_definitions()}
    assert {"launch_app", "list_windows", "focus_window", "click", "type_text", "scroll", "screenshot"}.issubset(names)


def test_tool_schemas_are_objects():
    definitions = tool_definitions()
    for tool in definitions:
        assert tool["input_schema"]["type"] == "object"
        assert tool["output_schema"]["type"] == "object"
