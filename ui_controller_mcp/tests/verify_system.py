from ui_controller_mcp.desktop.pyautogui_controller import PyAutoGUIController
from ui_controller_mcp.tools.handlers import ToolExecutor
from ui_controller_mcp.utils.safety import SafetyGuard

def test_system_tools():
    controller = PyAutoGUIController()
    safety = SafetyGuard()
    executor = ToolExecutor(controller, safety)
    
    print("Testing run_terminal_cmd...")
    result = executor.execute("run_terminal_cmd", {"command": "echo 'Hello System'"})
    print(f"Result: {result}")
    
    if result["success"] and "Hello System" in result["stdout"]:
        print("✅ run_terminal_cmd passed")
    else:
        print("❌ run_terminal_cmd failed")

    print("\nTesting check_notification...")
    # This will likely return nothing, but should not crash
    result = executor.execute("check_notification", {"timeout": 2})
    print(f"Result: {result}")
    
    if result["success"]:
        print("✅ check_notification passed (basic run)")
    else:
        print("❌ check_notification failed")

if __name__ == "__main__":
    test_system_tools()
