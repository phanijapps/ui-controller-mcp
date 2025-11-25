from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ui_controller_mcp.desktop.base import DesktopController

class BaseSkill(ABC):
    """
    Abstract base class for all application skills.
    A skill represents a high-level capability (e.g., "send message on Signal").
    """
    
    def __init__(self, controller: DesktopController):
        self.controller = controller

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the skill (e.g., 'signal:send')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the skill does."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> Dict[str, str]:
        """Dictionary of parameter names and their descriptions."""
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the skill with the given parameters.
        Returns a dictionary with 'success' and 'message'.
        """
        pass

class SkillRegistry:
    """
    Registry to manage and retrieve available skills.
    """
    _skills: Dict[str, BaseSkill] = {}

    @classmethod
    def register(cls, skill: BaseSkill):
        cls._skills[skill.name] = skill

    @classmethod
    def get_skill(cls, name: str) -> Optional[BaseSkill]:
        return cls._skills.get(name)

    @classmethod
    def list_skills(cls) -> List[Dict[str, Any]]:
        return [
            {
                "name": skill.name,
                "description": skill.description,
                "parameters": skill.parameters
            }
            for skill in cls._skills.values()
        ]
