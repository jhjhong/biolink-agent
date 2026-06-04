from typing import Dict, Any
from agents.base import BaseAgent
from tools.protein.uniprot_tool import UniProtTool
from tools.protein.alphafold_tool import AlphaFoldDBTool

class ProteinAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ProteinAgent", 
            description="Handles searches for protein structure, function, and sequences using UniProt and AlphaFold. IMPORTANT: For UniProt, pass the Gene Symbol or Protein Name. For AlphaFold, pass the EXACT UniProt Accession ID (e.g. 'P04637')."
        )
        self.register_tool(UniProtTool())
        self.register_tool(AlphaFoldDBTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [ProteinAgent] Executing tools for: '{task_query}'")
        
        # Decide which tool to use based on the context or query
        # Very simple heuristic: if it looks like a UniProt ID (alphanumeric, 6 chars), use AlphaFold, else UniProt
        is_uniprot_id = len(task_query.strip()) == 6 and task_query.strip().isalnum()
        
        tool = self.tools[1] if is_uniprot_id else self.tools[0]
        result = await tool.execute(task_query, max_results=3)
        return result
