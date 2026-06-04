from abc import ABC, abstractmethod
from typing import List, Dict, Any
from core.llm_provider import LLMProvider

class BaseAgent(ABC):
    """Base class for all Specialized Domain Agents (Variant, Literature, etc.)."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.llm = LLMProvider()
        self.tools = []

    def register_tool(self, tool):
        self.tools.append(tool)

    @abstractmethod
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Process a specific sub-task delegated by the Coordinator.
        Should return a dictionary with evidence or results.
        """
        pass
