from typing import Dict, Any
from agents.base import BaseAgent
from tools.disease.gwas_tool import GWASCatalogTool

class DiseaseAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="DiseaseAgent", 
            description="Handles searches for genetic diseases, traits, and GWAS studies. IMPORTANT: Your task_query MUST be EXACTLY the Gene Symbol (e.g. 'APOE')."
        )
        self.register_tool(GWASCatalogTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [DiseaseAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=5)
        return result
