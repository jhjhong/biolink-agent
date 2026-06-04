from typing import Dict, Any
from agents.base import BaseAgent
from tools.interaction.string_tool import StringDBTool

class InteractionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="InteractionAgent", 
            description="Handles searches for protein-protein interactions (PPI) and protein networks using STRING DB. IMPORTANT: Your task_query MUST be EXACTLY the Gene Symbol or Protein Name only (e.g. 'BRCA1')."
        )
        self.register_tool(StringDBTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [InteractionAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=5)
        return result
