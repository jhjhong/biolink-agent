from typing import Dict, Any
from agents.base import BaseAgent
from tools.pathway.reactome_tool import ReactomeTool

class PathwayAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PathwayAgent", 
            description="Handles searches for biological pathways and interactions. IMPORTANT: Your task_query MUST be EXACTLY the Gene Symbol or Protein Name only (e.g. 'mTOR')."
        )
        self.register_tool(ReactomeTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [PathwayAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=3)
        return result
