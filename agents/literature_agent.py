from typing import Dict, Any
from agents.base import BaseAgent
from tools.literature.pubmed_tool import PubMedTool

class LiteratureAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="LiteratureAgent", 
            description="Handles searches for biomedical literature, papers, and evidence using PubMed."
        )
        self.register_tool(PubMedTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [LiteratureAgent] Executing tool search for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=3)
        return result
