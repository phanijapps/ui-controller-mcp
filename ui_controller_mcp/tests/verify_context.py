from unittest.mock import MagicMock
from ui_controller_mcp.tools.handlers import ToolExecutor
from ui_controller_mcp.desktop.base import DesktopController
from ui_controller_mcp.utils.safety import SafetyGuard

def test_context_tracking():
    # Mock dependencies
    mock_controller = MagicMock(spec=DesktopController)
    mock_safety = MagicMock(spec=SafetyGuard)
    
    # Setup executor
    executor = ToolExecutor(mock_controller, mock_safety)
    
    # 1. Execute some tools
    print("Executing tools...")
    
    # Mock launch_app success
    mock_safety.validate_launch_target.return_value.allowed = True
    
    launch_result = MagicMock()
    launch_result.success = True
    launch_result.message = "Launched"
    launch_result.data = {}
    mock_controller.launch_app.return_value = launch_result
    
    executor.execute("launch_app", {"target": "gedit"})
    
    # Mock type_text success
    type_result = MagicMock()
    type_result.success = True
    type_result.message = "Typed"
    type_result.data = {}
    mock_controller.type_text.return_value = type_result
    
    executor.execute("type_text", {"text": "Hello World"})
    
    # 2. Retrieve history
    print("Retrieving history...")
    result = executor.execute("get_agent_history", {"limit": 5})
    
    if not result["success"]:
        print("❌ get_agent_history failed")
        return

    history = result["history"]
    print(f"History items: {len(history)}")
    
    # 3. Verify logs (newest first)
    # Expect: get_agent_history (current), type_text, launch_app
    
    # Note: get_agent_history is logged AFTER it returns, so it might not be in the list 
    # returned BY the call itself depending on implementation details.
    # In our implementation: log_action is called AFTER _execute_tool returns.
    # So the call to get_agent_history returns the history BEFORE the current call is logged.
    # Thus we expect: type_text, launch_app
    
    if len(history) >= 2:
        latest = history[0]
        previous = history[1]
        
        print(f"Latest: {latest['tool_name']}")
        print(f"Previous: {previous['tool_name']}")
        
        if latest["tool_name"] == "type_text" and previous["tool_name"] == "launch_app":
            print("✅ Context tracking verified")
        else:
            print("❌ Unexpected history order")
    else:
        print("❌ Not enough history items")

if __name__ == "__main__":
    test_context_tracking()
