from __future__ import annotations

import importlib
import subprocess
import base64
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import DesktopActionResult


class PyAutoGUIController:
    """PyAutoGUI-backed controller where available."""

    def __init__(self) -> None:
        self.pyautogui = self._load_pyautogui()

    def _load_pyautogui(self) -> Any | None:
        spec = importlib.util.find_spec("pyautogui")
        if spec is None:
            return None
        try:
            module = importlib.import_module("pyautogui")
        except Exception:  # noqa: BLE001
            return None

        module.FAILSAFE = False
        return module

    def launch_app(self, target: str) -> DesktopActionResult:
        try:
            subprocess.Popen(target.split())
            return DesktopActionResult(True, f"Launched '{target}'")
        except Exception as exc:  # noqa: BLE001
            return DesktopActionResult(False, f"Failed to launch '{target}': {exc}")

    def list_windows(self) -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available for window listing")
        try:
            windows = [win.title for win in self.pyautogui.getAllWindows()]
            return DesktopActionResult(True, "Windows listed", data={"windows": windows})
        except Exception as exc:  # noqa: BLE001
            return DesktopActionResult(False, f"Unable to list windows: {exc}")

    def focus_window(self, title: str) -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available for window focus")
        try:
            for window in self.pyautogui.getAllWindows():
                if title.lower() in window.title.lower():
                    window.activate()
                    return DesktopActionResult(True, f"Focused window '{window.title}'")
            return DesktopActionResult(False, f"No window found matching '{title}'")
        except Exception as exc:  # noqa: BLE001
            return DesktopActionResult(False, f"Unable to focus window: {exc}")

    def click(self, x: int | None = None, y: int | None = None, button: str = "left") -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available for click actions")
        try:
            if x is not None and y is not None:
                self.pyautogui.click(x=x, y=y, button=button)
            else:
                self.pyautogui.click(button=button)
            return DesktopActionResult(True, "Click executed")
        except Exception as exc:  # noqa: BLE001
            return DesktopActionResult(False, f"Click failed: {exc}")

    def type_text(self, text: str) -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available for typing")
        try:
            self.pyautogui.typewrite(text)
            return DesktopActionResult(True, "Text typed")
        except Exception as exc:  # noqa: BLE001
            return DesktopActionResult(False, f"Typing failed: {exc}")

    def scroll(self, amount: int, direction: str = "vertical") -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available for scrolling")
        try:
            if direction == "horizontal":
                self.pyautogui.hscroll(amount)
            else:
                self.pyautogui.scroll(amount)
            return DesktopActionResult(True, "Scroll executed")
        except Exception as exc:  # noqa: BLE001
            return DesktopActionResult(False, f"Scroll failed: {exc}")

    def screenshot(self) -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available for screenshots")
        try:
            image = self.pyautogui.screenshot()
            output_dir = Path.cwd() / "screenshots"
            output_dir.mkdir(parents=True, exist_ok=True)
            captured_at = datetime.utcnow().isoformat()
            file_path = output_dir / f"screenshot-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.png"
            image.save(file_path)
            encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
            return DesktopActionResult(
                True,
                "Screenshot captured",
                data={"path": str(file_path), "captured_at": captured_at, "base64_data": encoded},
            )
        except Exception as exc:  # noqa: BLE001
            return DesktopActionResult(False, f"Screenshot failed: {exc}")
