from unittest.mock import MagicMock, patch
from ui_controller_mcp.skills.messaging import SignalSendSkill, WhatsAppSendSkill
from ui_controller_mcp.desktop.base import DesktopController

def test_signal_skill():
    mock_controller = MagicMock(spec=DesktopController)
    skill = SignalSendSkill(mock_controller)
    
    # Mock pyautogui
    with patch("ui_controller_mcp.skills.messaging.pyautogui") as mock_pyautogui:
        result = skill.execute({"contact": "Alice", "message": "Hello"})
        
        assert result["success"] is True
        mock_controller.launch_app.assert_called_with("signal-desktop")
        mock_pyautogui.hotkey.assert_called_with('ctrl', 'f')
        # Verify typing calls: contact then message
        assert mock_controller.type_text.call_count == 2
        mock_controller.type_text.assert_any_call("Alice", enter=True)
        mock_controller.type_text.assert_any_call("Hello", enter=True)
        print("✅ Signal Skill passed")

def test_whatsapp_skill():
    mock_controller = MagicMock(spec=DesktopController)
    skill = WhatsAppSendSkill(mock_controller)
    
    with patch("ui_controller_mcp.skills.messaging.pyautogui") as mock_pyautogui:
        result = skill.execute({"contact": "Bob", "message": "Hi there"})
        
        assert result["success"] is True
        mock_controller.launch_app.assert_called_with("firefox")
        # Verify navigation
        mock_controller.type_text.assert_any_call("web.whatsapp.com", enter=True)
        # Verify contact and message
        mock_controller.type_text.assert_any_call("Bob", enter=True)
        mock_controller.type_text.assert_any_call("Hi there", enter=True)
        print("✅ WhatsApp Skill passed")

if __name__ == "__main__":
    test_signal_skill()
    test_whatsapp_skill()
