from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict

from ui_controller_mcp.ai.client import AIClient
from ui_controller_mcp.desktop.base import DesktopController
from ui_controller_mcp.utils.safety import SafetyGuard


class ToolExecutor:
    """Executes tool invocations using the provided controller and safety guard."""

    def __init__(
        self,
        controller: DesktopController,
        safety_guard: SafetyGuard,
        ai_client: AIClient | None = None,
        *,
        max_read_size: int = 5 * 1024 * 1024,
    ) -> None:
        self.controller = controller
        self.safety_guard = safety_guard
        self.ai_client = ai_client
        self.max_read_size = max_read_size

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
        if name == "get_bytes":
            return self._get_bytes(params)
        if name == "perceive":
            return self._perceive(params)
        if name == "reason":
            return self._reason(params)
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
        # Ensure 'windows' key exists even if empty
        if "windows" not in payload:
            payload["windows"] = []
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

    def _get_bytes(self, params: Dict[str, Any]) -> dict[str, Any]:
        raw_path = params.get("path", "")
        if not raw_path:
            return {"success": False, "error": "File path is required"}

        path = Path(raw_path).expanduser().resolve()
        if not path.exists():
            return {"success": False, "error": f"File not found: {path}"}
        if not path.is_file():
            return {"success": False, "error": f"Path is not a file: {path}"}

        try:
            size = path.stat().st_size
        except OSError as exc:  # noqa: BLE001
            return {"success": False, "error": f"Unable to read file metadata: {exc}"}

        if size > self.max_read_size:
            return {
                "success": False,
                "error": f"File is too large to read safely (size={size} bytes, limit={self.max_read_size} bytes)",
            }

        try:
            content = path.read_bytes()
        except OSError as exc:  # noqa: BLE001
            return {"success": False, "error": f"Unable to read file: {exc}"}

        encoded = base64.b64encode(content).decode("ascii")
        return {
            "success": True,
            "message": "File bytes encoded",
            "data": {"path": str(path), "size": size, "base64_data": encoded},
        }

    def _perceive(self, params: Dict[str, Any]) -> dict[str, Any]:
        if not self.ai_client:
            return {"success": False, "error": "AI capabilities not available"}

        # Take a screenshot first
        screenshot_result = self.controller.screenshot()
        if not screenshot_result.success or not screenshot_result.data:
            return {"success": False, "error": f"Failed to take screenshot: {screenshot_result.message}"}

        image_data = screenshot_result.data.get("base64_data")
        if not image_data:
            return {"success": False, "error": "No base64 image data available from screenshot"}

        instruction = params.get("instruction", "")

        analysis = self.ai_client.analyze_image(image_data, instruction)
        return {"success": True, "message": "Screen analyzed", "analysis": analysis}

    def _reason(self, params: Dict[str, Any]) -> dict[str, Any]:
        if not self.ai_client:
            return {"success": False, "error": "AI capabilities not available"}

        analysis = params.get("analysis", "")
        goal = params.get("goal", "")

        plan = self.ai_client.plan_action(analysis, goal)
        return {"success": True, "message": "Action planned", "plan": plan}
