from __future__ import annotations

from .noop_controller import NoOpDesktopController
from .pyautogui_controller import PyAutoGUIController


def get_controller() -> NoOpDesktopController | PyAutoGUIController:
    controller = PyAutoGUIController()
    if controller.pyautogui is not None:
        return controller
    return NoOpDesktopController()
