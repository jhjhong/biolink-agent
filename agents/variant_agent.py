from typing import Dict, Any
from agents.base import BaseAgent
from tools.variant.clinvar_tool import ClinVarTool

class VariantAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="VariantAgent", 
            description="Handles searches for genetic variants, clinical significance, ACMG evidence, and phenotypes using ClinVar."
        )
        self.register_tool(ClinVarTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [VariantAgent] Executing tool search for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=3)
        return result
