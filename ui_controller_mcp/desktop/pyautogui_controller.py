from __future__ import annotations

import base64
import importlib
import platform
import shlex
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

from .base import DesktopActionResult

class PyAutoGUIController:
    """
    Cross-platform Desktop Controller.
    Uses PyAutoGUI for input/visuals and PyWinCtl for window management.
    """

    def __init__(self) -> None:
        self.pyautogui = self._load_module("pyautogui")
        self.pywinctl = self._load_module("pywinctl")
        self.os_name = platform.system()

    def _load_module(self, name: str) -> Any | None:
        """Helper to safely load required modules."""
        try:
            module = importlib.import_module(name)
            if name == "pyautogui":
                # Fail-safe triggers when mouse is in corner. 
                # Disable for headless/server environments if needed.
                module.FAILSAFE = False 
            return module
        except ImportError:
            return None

    def launch_app(self, target: str) -> DesktopActionResult:
        """
        OS-agnostic application launcher.
        """
        try:
            command = []
            
            if self.os_name == "Darwin":  # macOS
                # use 'open -a' for applications, 'open' for paths
                if "/" in target or "\\" in target:
                    command = ["open", target]
                else:
                    command = ["open", "-a", target]
            
            elif self.os_name == "Linux":
                # Try xdg-open for generic handling, or just the command
                if "/" in target:
                    command = ["xdg-open", target]
                else:
                    command = shlex.split(target)
            
            elif self.os_name == "Windows":
                # Windows handles paths/exes natively in subprocess usually
                # using shell=True helps with resolving PATH vars but introduces security risks.
                # sticking to split for safety unless it's a complex string.
                command = shlex.split(target)
            
            else:
                # Fallback
                command = shlex.split(target)

            # start_new_session=True detaches the child process (POSIX)
            # creationflags=DETACHED_PROCESS (Windows) - optional refinement
            subprocess.Popen(command)
            
            return DesktopActionResult(True, f"Launched '{target}' on {self.os_name}")
        except Exception as exc:
            return DesktopActionResult(False, f"Failed to launch '{target}': {exc}")

    def list_windows(self) -> DesktopActionResult:
        """
        Lists windows using PyWinCtl (Cross-platform).
        """
        if self.pywinctl is None:
            return DesktopActionResult(False, "PyWinCtl not installed/available")

        try:
            # pywinctl provides a unified API for getting titles
            all_windows = self.pywinctl.getAllTitles()
            # Filter out empty strings
            windows = [title for title in all_windows if title.strip()]
            
            return DesktopActionResult(True, "Windows listed", data={"windows": windows})
        except Exception as exc:
            return DesktopActionResult(False, f"Unable to list windows: {exc}")

    def focus_window(self, title: str) -> DesktopActionResult:
        """
        Focuses a window using PyWinCtl.
        """
        if self.pywinctl is None:
            return DesktopActionResult(False, "PyWinCtl not installed/available")

        try:
            # Find window by partial title match
            target_window = None
            for win_title in self.pywinctl.getAllTitles():
                if title.lower() in win_title.lower():
                    # Get the window object
                    wins = self.pywinctl.getWindowsWithTitle(win_title)
                    if wins:
                        target_window = wins[0]
                        break
            
            if target_window:
                # Activate brings window to front and gives focus
                target_window.activate()
                return DesktopActionResult(True, f"Focused window '{target_window.title}'")
            
            return DesktopActionResult(False, f"No window found matching '{title}'")
        except Exception as exc:
            return DesktopActionResult(False, f"Unable to focus window: {exc}")

    def click(self, x: int | None = None, y: int | None = None, button: str = "left") -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available")
        
        try:
            # Determine current position if x/y not provided
            if x is None or y is None:
                curr_x, curr_y = self.pyautogui.position()
                x = x if x is not None else curr_x
                y = y if y is not None else curr_y

            self.pyautogui.click(x=x, y=y, button=button)
            return DesktopActionResult(True, f"Clicked {button} at ({x}, {y})")
        except Exception as exc:
            return DesktopActionResult(False, f"Click failed: {exc}")

    def type_text(self, text: str) -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available")
        
        try:
            # Use write() for general text (supports all characters)
            # interval helps prevent missing keystrokes on some OSs
            self.pyautogui.write(text, interval=0.01)
            return DesktopActionResult(True, "Text typed")
        except Exception as exc:
            return DesktopActionResult(False, f"Typing failed: {exc}")

    def scroll(self, amount: int, direction: str = "vertical") -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available")
        
        try:
            if direction == "horizontal":
                # Linux/Mac support for hscroll varies in pyautogui
                try:
                    self.pyautogui.hscroll(amount)
                except AttributeError:
                    return DesktopActionResult(False, "Horizontal scroll not supported on this OS by PyAutoGUI")
            else:
                self.pyautogui.scroll(amount)
            return DesktopActionResult(True, f"{direction.title()} scroll executed")
        except Exception as exc:
            return DesktopActionResult(False, f"Scroll failed: {exc}")

    def screenshot(self) -> DesktopActionResult:
        if self.pyautogui is None:
            return DesktopActionResult(False, "PyAutoGUI not available")
        
        try:
            image = self.pyautogui.screenshot()
            
            output_dir = Path.cwd() / "screenshots"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Use UTC now, formatted cleanly
            captured_at = datetime.utcnow().isoformat()
            filename = f"screenshot-{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.png"
            file_path = output_dir / filename
            
            image.save(file_path)
            
            # Encode for transport (e.g. to an LLM or API)
            encoded = base64.b64encode(file_path.read_bytes()).decode("ascii")
            
            return DesktopActionResult(
                True,
                "Screenshot captured",
                data={
                    "path": str(file_path), 
                    "captured_at": captured_at, 
                    "base64_data": encoded
                },
            )
        except Exception as exc:
            return DesktopActionResult(False, f"Screenshot failed: {exc}")