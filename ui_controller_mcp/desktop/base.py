from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class DesktopActionResult:
    success: bool
    message: str
    data: dict[str, Any] | None = None


class DesktopController(Protocol):
    def launch_app(self, target: str) -> DesktopActionResult: ...

    def list_windows(self) -> DesktopActionResult: ...

    def focus_window(self, title: str) -> DesktopActionResult: ...

    def click(self, x: int | None = None, y: int | None = None, button: str = "left") -> DesktopActionResult: ...

    def type_text(self, text: str) -> DesktopActionResult: ...

    def scroll(self, amount: int, direction: str = "vertical") -> DesktopActionResult: ...

    def screenshot(self) -> DesktopActionResult: ...
