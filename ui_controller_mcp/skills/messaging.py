import time
import pyautogui
from typing import Dict, Any
from ui_controller_mcp.skills.base import BaseSkill

class SignalSendSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "signal:send"

    @property
    def description(self) -> str:
        return "Send a message to a contact on Signal Desktop."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "contact": "Name of the contact to message",
            "message": "The text message to send"
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        contact = params.get("contact")
        message = params.get("message")
        
        if not contact or not message:
            return {"success": False, "message": "Missing contact or message"}

        # 1. Launch/Focus Signal
        self.controller.launch_app("signal-desktop")
        time.sleep(2) # Wait for app to focus
        
        # 2. Search for contact (Ctrl+f is standard search in Signal)
        # We use pyautogui directly via controller methods if available, 
        # but controller.type_text doesn't support hotkeys directly yet.
        # We'll assume the controller has a way to press keys or we simulate it.
        # Since we don't have press_hotkey exposed in controller yet, we might need to rely on 
        # the fact that type_text types characters. 
        # Actually, for a robust skill, we might need to add hotkey support to controller 
        # or use a workaround. 
        # For now, let's assume we can click the search bar if we knew where it was, 
        # OR we can try to implement a simple hotkey helper in the skill if we import pyautogui.
        # But skills shouldn't import pyautogui directly if possible to keep abstraction.
        # Let's check if we can add a simple hotkey method to controller or just use tab navigation.
        
        # Workaround: Signal usually focuses search on start or we can Tab to it.
        # Let's try sending Ctrl+f using a direct import for now as a "skill implementation detail"
        # or better, let's add press_hotkey to the controller in a separate step if needed.
        # 2. Search for contact (Ctrl+f is standard search in Signal)
        
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.5)
        
        # 3. Type contact name
        self.controller.type_text(contact, enter=True)
        time.sleep(1.0) # Wait for search results and selection
        
        # 4. Type message
        self.controller.type_text(message, enter=True)
        
        return {"success": True, "message": f"Sent Signal message to {contact}"}

class WhatsAppSendSkill(BaseSkill):
    @property
    def name(self) -> str:
        return "whatsapp:send"

    @property
    def description(self) -> str:
        return "Send a message on WhatsApp Web (via Firefox)."

    @property
    def parameters(self) -> Dict[str, str]:
        return {
            "contact": "Name of the contact to message",
            "message": "The text message to send"
        }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        contact = params.get("contact")
        message = params.get("message")
        
        if not contact or not message:
            return {"success": False, "message": "Missing contact or message"}

        # 1. Launch/Focus Firefox
        self.controller.launch_app("firefox")
        time.sleep(1)
        
        # 2. Open WhatsApp Web
        pyautogui.hotkey('ctrl', 't')
        time.sleep(0.5)
        self.controller.type_text("web.whatsapp.com", enter=True)
        
        # 3. Wait for load (this is where wait_for_image would be great, but we'll use sleep for MVP)
        time.sleep(8) 
        
        # 4. Search contact (Ctrl+alt+/ is standard, or Tab navigation)
        # WhatsApp Web often focuses search or we can use Tab
        pyautogui.hotkey('ctrl', 'alt', '/')
        time.sleep(0.5)
        
        # 5. Type contact
        self.controller.type_text(contact, enter=True)
        time.sleep(1.0)
        
        # 6. Type message
        self.controller.type_text(message, enter=True)
        
        return {"success": True, "message": f"Sent WhatsApp message to {contact}"}
