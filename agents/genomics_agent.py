from typing import Dict, Any
from agents.base import BaseAgent
from tools.genomics.ensembl_tool import EnsemblTool

class GenomicsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GenomicsAgent", 
            description="Handles searches for genes, genomic coordinates, and transcripts using Ensembl. IMPORTANT: Your task_query MUST be EXACTLY the Gene Symbol only (e.g. 'TP53'). Do NOT pass sentences."
        )
        self.register_tool(EnsemblTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [GenomicsAgent] Executing tool search for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=3)
        return result
