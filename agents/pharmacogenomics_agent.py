from typing import Dict, Any
from agents.base import BaseAgent
from tools.pharmacogenomics.dgidb_tool import DGIdbTool

class PharmacogenomicsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="PharmacogenomicsAgent", 
            description="Handles searches for drug-gene interactions and precision medicine targets. IMPORTANT: Your task_query MUST be EXACTLY the Gene Symbol (e.g. 'EGFR')."
        )
        self.register_tool(DGIdbTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [PharmacogenomicsAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=5)
        return result
