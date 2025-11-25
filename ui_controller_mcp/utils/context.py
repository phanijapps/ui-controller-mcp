import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict

@dataclass
class ActionLog:
    timestamp: float
    tool_name: str
    params: Dict[str, Any]
    result: Dict[str, Any]
    success: bool

class ContextTracker:
    """
    Tracks the history of agent actions to provide context awareness.
    """
    
    def __init__(self, max_history: int = 50):
        self.max_history = max_history
        self._history: List[ActionLog] = []

    def log_action(self, tool_name: str, params: Dict[str, Any], result: Dict[str, Any]):
        """
        Log a completed tool action.
        """
        # Determine success from result
        success = result.get("success", False) if isinstance(result, dict) else False
        
        # Create log entry
        log = ActionLog(
            timestamp=time.time(),
            tool_name=tool_name,
            params=params,
            result=result,
            success=success
        )
        
        self._history.append(log)
        
        # Trim history if needed
        if len(self._history) > self.max_history:
            self._history.pop(0)

    def get_recent_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent actions.
        """
        # Return recent items, reversed (newest first)
        recent = self._history[-limit:]
        return [asdict(log) for log in reversed(recent)]

    def get_last_action(self) -> Optional[Dict[str, Any]]:
        """
        Get the very last action performed.
        """
        if not self._history:
            return None
        return asdict(self._history[-1])
