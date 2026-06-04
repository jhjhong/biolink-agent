from typing import Dict, Any
from agents.base import BaseAgent
from tools.taxonomy.ncbi_tax_tool import NCBITaxonomyTool

class TaxonomyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="TaxonomyAgent", 
            description="Handles searches for species classification, biological lineage, and organism taxonomy. IMPORTANT: Your task_query MUST be EXACTLY the species or organism name (e.g. 'Homo sapiens', 'SARS-CoV-2')."
        )
        self.register_tool(NCBITaxonomyTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [TaxonomyAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=3)
        return result
