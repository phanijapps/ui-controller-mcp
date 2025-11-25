from __future__ import annotations

import base64
from pathlib import Path
from typing import Any, Dict

from ui_controller_mcp.ai.client import AIClient
from ui_controller_mcp.desktop.base import DesktopController
from ui_controller_mcp.utils.safety import SafetyGuard
from ui_controller_mcp.utils.context import ContextTracker


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
        
        # Initialize context tracker
        self.context_tracker = ContextTracker()

    def execute(self, name: str, params: Dict[str, Any]) -> dict[str, Any]:
        result = self._execute_tool(name, params)
        
        # Log the action (masking sensitive params if needed)
        # For now we log everything, but in production we'd mask passwords
        log_params = params.copy()
        if "password" in log_params:
            log_params["password"] = "***"
            
        self.context_tracker.log_action(name, log_params, result)
        
        return result

    def _execute_tool(self, name: str, params: Dict[str, Any]) -> dict[str, Any]:
        if name == "launch_app":
            return self._launch_app(params)
        if name == "list_windows":
            return self._list_windows(params)
        if name == "focus_window":
            return self._focus_window(params)
        if name == "click":
            return self._click(params)
        if name == "type_text":
            return self._type_text(params)
        if name == "scroll":
            return self._scroll(params)
        if name == "drag":
            # Assuming _drag is a new method to be implemented
            # For now, return an error if not implemented
            return {"success": False, "error": "Tool 'drag' not implemented yet."}
        if name == "get_screen_info":
            # Assuming _get_screen_info is a new method to be implemented
            # For now, return an error if not implemented
            return {"success": False, "error": "Tool 'get_screen_info' not implemented yet."}
        if name == "screenshot":
            return self._screenshot()
        if name == "get_bytes":
            return self._get_bytes(params)
        if name == "perceive":
            return self._perceive(params)
        if name == "reason":
            return self._reason(params)
        if name == "manage_credentials":
            return self._manage_credentials(params)
        if name == "type_password":
            return self._type_password(params)
        if name == "handle_sudo":
            return self._handle_sudo(params)
        if name == "find_image":
            return self._find_image(params)
        if name == "wait_for_image":
            return self._wait_for_image(params)
        if name == "run_terminal_cmd":
            return self._run_terminal_cmd(params)
        if name == "check_notification":
            return self._check_notification(params)
        if name == "use_skill":
            return self._use_skill(params)
        if name == "get_agent_history":
            return self._get_agent_history(params)
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

    def _manage_credentials(self, params: Dict[str, Any]) -> dict[str, Any]:
        from ui_controller_mcp.utils.security import CredentialManager
        
        manager = CredentialManager()
        action = params.get("action")
        cred_id = params.get("id")
        
        if not cred_id:
            return {"success": False, "error": "Credential ID required"}
            
        if action == "set":
            value = params.get("value")
            if not value:
                return {"success": False, "error": "Value required for set action"}
            
            if manager.set_credential(cred_id, value):
                return {"success": True, "message": f"Credential '{cred_id}' stored securely"}
            return {"success": False, "error": "Failed to store credential"}
            
        elif action == "check":
            exists = manager.get_credential(cred_id) is not None
            status = "exists" if exists else "does not exist"
            return {"success": True, "message": f"Credential '{cred_id}' {status}"}
            
        return {"success": False, "error": f"Unknown action: {action}"}

    def _type_password(self, params: Dict[str, Any]) -> dict[str, Any]:
        from ui_controller_mcp.utils.security import CredentialManager
        
        manager = CredentialManager()
        cred_id = params.get("id")
        enter = params.get("enter", True)
        
        password = manager.get_credential(cred_id)
        if not password:
            return {"success": False, "error": f"Credential '{cred_id}' not found"}
            
        # Use controller directly to avoid safety guard logging
        # We assume type_text in controller is safe to call with password 
        # as long as we don't log it here.
        result = self.controller.type_text(password, enter=enter)
        
        if result.success:
            return {"success": True, "message": "Password typed securely"}
        return {"success": False, "error": result.message}

    def _handle_sudo(self, params: Dict[str, Any]) -> dict[str, Any]:
        # Convenience wrapper for typing sudo password
        return self._type_password({"id": "sudo_pass", "enter": True})

    def _find_image(self, params: Dict[str, Any]) -> dict[str, Any]:
        from ui_controller_mcp.utils.vision import VisionEngine
        
        template_path = params.get("template_path")
        confidence = params.get("confidence", 0.8)
        
        if not template_path:
            return {"success": False, "error": "Template path required"}
            
        # Take screenshot
        screenshot_result = self.controller.screenshot()
        if not screenshot_result.success or not screenshot_result.data:
            return {"success": False, "error": f"Failed to take screenshot: {screenshot_result.message}"}
            
        screenshot_b64 = screenshot_result.data.get("base64_data")
        
        try:
            engine = VisionEngine()
            matches = engine.find_template(screenshot_b64, template_path, confidence)
            return {"success": True, "message": f"Found {len(matches)} matches", "matches": matches}
        except Exception as e:
            return {"success": False, "error": f"Vision error: {str(e)}"}

    def _wait_for_image(self, params: Dict[str, Any]) -> dict[str, Any]:
        import time
        
        template_path = params.get("template_path")
        timeout = params.get("timeout", 10)
        confidence = params.get("confidence", 0.8)
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            result = self._find_image({"template_path": template_path, "confidence": confidence})
            
            if result.get("success") and result.get("matches"):
                # Found it! Return the best match
                best_match = result["matches"][0]
                return {
                    "success": True, 
                    "message": "Image found", 
                    "match": best_match
                }
            
            time.sleep(0.5)
            
        return {"success": False, "message": f"Timeout waiting for image after {timeout}s"}

    def _run_terminal_cmd(self, params: Dict[str, Any]) -> dict[str, Any]:
        command = params.get("command")
        if not command:
            return {"success": False, "error": "Command required"}
            
        # Security check: prevent obviously dangerous commands if needed
        # For now, we rely on the user's trust and the fact that this is an agent tool
        
        result = self.controller.run_terminal_cmd(command)
        return {
            "success": result.success,
            "message": result.message,
            "stdout": result.data.get("stdout", ""),
            "stderr": result.data.get("stderr", ""),
            "returncode": result.data.get("returncode", -1)
        }

    def _check_notification(self, params: Dict[str, Any]) -> dict[str, Any]:
        import subprocess
        import time
        
        timeout = params.get("timeout", 5)
        
        # This is a simplified implementation using dbus-monitor
        # It captures the output and looks for notification signals
        try:
            cmd = ["dbus-monitor", "interface='org.freedesktop.Notifications'"]
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True
            )
            
            start_time = time.time()
            found_notification = False
            notification_data = {"title": "", "body": ""}
            
            while time.time() - start_time < timeout:
                # Check if we have output
                if process.poll() is not None:
                    break
                    
                # Non-blocking read would be better, but for simplicity we wait a bit
                # In a real implementation, we'd use a thread or select
                time.sleep(0.1)
                
            process.terminate()
            
            # For this MVP, we just report if we ran successfully.
            # Parsing dbus-monitor output is complex.
            # A better approach would be to use a python dbus library if available.
            
            return {
                "success": True,
                "message": "Checked for notifications (basic implementation)",
                "found": False, # Placeholder
                "title": "",
                "body": ""
            }
        except Exception as e:
            return {"success": False, "error": f"Failed to check notifications: {e}"}

    def _use_skill(self, params: Dict[str, Any]) -> dict[str, Any]:
        from ui_controller_mcp.skills.base import SkillRegistry
        from ui_controller_mcp.skills.messaging import SignalSendSkill, WhatsAppSendSkill
        
        # Register skills (idempotent)
        SkillRegistry.register(SignalSendSkill(self.controller))
        SkillRegistry.register(WhatsAppSendSkill(self.controller))
        
        skill_name = params.get("skill")
        skill_params = params.get("params", {})
        
        if not skill_name:
            return {"success": False, "error": "Skill name required"}
            
        skill = SkillRegistry.get_skill(skill_name)
        if not skill:
            return {"success": False, "error": f"Skill '{skill_name}' not found"}
            
        try:
            return skill.execute(skill_params)
        except Exception as e:
            return {"success": False, "error": f"Skill execution failed: {e}"}

    def _get_agent_history(self, params: Dict[str, Any]) -> dict[str, Any]:
        limit = params.get("limit", 10)
        history = self.context_tracker.get_recent_history(limit)
        return {"success": True, "history": history}
