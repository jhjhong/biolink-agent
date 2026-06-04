from abc import ABC, abstractmethod
from typing import Any, Dict

class ScientificTool(ABC):
    """Base interface for all scientific tools."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the tool (e.g., 'PubMed', 'ClinVar')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what the tool does, for the Router Agent."""
        pass

    @abstractmethod
    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute the tool with the given query.
        Returns a dictionary containing the results and metadata.
        """
        pass
