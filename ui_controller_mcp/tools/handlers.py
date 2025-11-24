from __future__ import annotations

from typing import Any, Dict

from ui_controller_mcp.desktop.base import DesktopController
from ui_controller_mcp.utils.safety import SafetyGuard


class ToolExecutor:
    def __init__(self, controller: DesktopController, safety_guard: SafetyGuard) -> None:
        self.controller = controller
        self.safety_guard = safety_guard

    def execute(self, name: str, params: Dict[str, Any]) -> dict[str, Any]:
        if name == "launch_app":
            return self._launch_app(params)
        if name == "list_windows":
            return self._list_windows()
        if name == "focus_window":
            return self._focus_window(params)
        if name == "click":
            return self._click(params)
        if name == "type_text":
            return self._type_text(params)
        if name == "scroll":
            return self._scroll(params)
        if name == "screenshot":
            return self._screenshot()
        raise ValueError(f"Unsupported tool: {name}")

    def _launch_app(self, params: Dict[str, Any]) -> dict[str, Any]:
        target = params.get("target", "").strip()
        check = self.safety_guard.validate_launch_target(target)
        if not check.allowed:
            return {"success": False, "error": check.reason}
        result = self.controller.launch_app(target)
        return {"success": result.success, "message": result.message, "data": result.data}

    def _list_windows(self) -> dict[str, Any]:
        result = self.controller.list_windows()
        payload: dict[str, Any] = {"success": result.success, "message": result.message}
        if result.data is not None:
            payload.update(result.data)
        return payload

    def _focus_window(self, params: Dict[str, Any]) -> dict[str, Any]:
        title = params.get("title", "")
        result = self.controller.focus_window(title)
        return {"success": result.success, "message": result.message}

    def _click(self, params: Dict[str, Any]) -> dict[str, Any]:
        result = self.controller.click(params.get("x"), params.get("y"), params.get("button", "left"))
        return {"success": result.success, "message": result.message}

    def _type_text(self, params: Dict[str, Any]) -> dict[str, Any]:
        text = params.get("text", "")
        check = self.safety_guard.validate_text(text)
        if not check.allowed:
            return {"success": False, "error": check.reason}
        result = self.controller.type_text(text)
        return {"success": result.success, "message": result.message}

    def _scroll(self, params: Dict[str, Any]) -> dict[str, Any]:
        result = self.controller.scroll(params.get("amount", 0), params.get("direction", "vertical"))
        return {"success": result.success, "message": result.message}

    def _screenshot(self) -> dict[str, Any]:
        result = self.controller.screenshot()
        payload: dict[str, Any] = {"success": result.success, "message": result.message}
        if result.data is not None:
            payload.update(result.data)
        return payload
