from __future__ import annotations

import platform
from datetime import datetime

from .base import DesktopActionResult


class NoOpDesktopController:
    """A safe, logging-only controller for environments without UI access."""

    def launch_app(self, target: str) -> DesktopActionResult:
        return DesktopActionResult(True, f"Launch request recorded for '{target}' (noop mode)")

    def list_windows(self) -> DesktopActionResult:
        return DesktopActionResult(True, "Window listing not available; returning stub data.", data={"windows": []})

    def focus_window(self, title: str) -> DesktopActionResult:
        return DesktopActionResult(True, f"Focus request recorded for '{title}' (noop mode)")

    def click(self, x: int | None = None, y: int | None = None, button: str = "left") -> DesktopActionResult:
        coords = f" at ({x}, {y})" if x is not None and y is not None else ""
        return DesktopActionResult(True, f"Click{coords} with {button} recorded (noop mode)")

    def type_text(self, text: str) -> DesktopActionResult:
        return DesktopActionResult(True, f"Typed '{text}' (noop mode)")

    def scroll(self, amount: int, direction: str = "vertical") -> DesktopActionResult:
        return DesktopActionResult(True, f"Scroll {direction} by {amount} recorded (noop mode)")

    def screenshot(self) -> DesktopActionResult:
        timestamp = datetime.utcnow().isoformat()
        return DesktopActionResult(
            True,
            "Screenshot capture not available; returning stub payload.",
            data={"captured_at": timestamp, "platform": platform.platform()},
        )
