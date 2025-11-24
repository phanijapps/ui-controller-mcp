from __future__ import annotations

from typing import Any, Callable, Dict, List

from ui_controller_mcp.desktop.base import DesktopActionResult

ToolHandler = Callable[[Dict[str, Any]], DesktopActionResult]


def tool_definitions() -> List[dict[str, Any]]:
    return [
        {
            "name": "launch_app",
            "description": "Launch an application by name or path",
            "input_schema": {
                "type": "object",
                "properties": {
                    "target": {"type": "string", "description": "Application name or command"},
                },
                "required": ["target"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string"},
                },
                "required": ["message"],
            },
        },
        {
            "name": "list_windows",
            "description": "List currently open windows",
            "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            "output_schema": {
                "type": "object",
                "properties": {
                    "windows": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["windows"],
            },
        },
        {
            "name": "focus_window",
            "description": "Focus a window by matching its title",
            "input_schema": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Window title to activate"},
                },
                "required": ["title"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        },
        {
            "name": "click",
            "description": "Perform a mouse click",
            "input_schema": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer"},
                    "y": {"type": "integer"},
                    "button": {"type": "string", "enum": ["left", "right", "middle"]},
                },
                "required": [],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        },
        {
            "name": "type_text",
            "description": "Type text into the active window",
            "input_schema": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to type"},
                },
                "required": ["text"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        },
        {
            "name": "scroll",
            "description": "Scroll vertically or horizontally",
            "input_schema": {
                "type": "object",
                "properties": {
                    "amount": {"type": "integer"},
                    "direction": {"type": "string", "enum": ["vertical", "horizontal"], "default": "vertical"},
                },
                "required": ["amount"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
        },
        {
            "name": "screenshot",
            "description": "Capture a screenshot of the current screen",
            "input_schema": {"type": "object", "properties": {}, "additionalProperties": False},
            "output_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "captured_at": {"type": "string"},
                    "base64_data": {
                        "type": "string",
                        "description": "Screenshot encoded as a base64 string",
                    },
                },
                "required": ["captured_at"],
            },
        },
        {
            "name": "get_bytes",
            "description": "Read a file and return its contents as base64",
            "input_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Absolute or relative file path"},
                },
                "required": ["path"],
                "additionalProperties": False,
            },
            "output_schema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string"},
                    "size": {"type": "integer", "description": "Size in bytes"},
                    "base64_data": {"type": "string", "description": "File contents encoded as base64"},
                },
                "required": ["path", "size", "base64_data"],
            },
        },
    ]
