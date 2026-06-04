from typing import Dict, Any
from agents.base import BaseAgent
from tools.chemistry.pubchem_tool import PubChemTool
from tools.chemistry.chembl_tool import ChEMBLTool

class ChemAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ChemAgent", 
            description="Handles searches for chemical compounds, small molecules, drugs, and bioactivity using PubChem and ChEMBL. IMPORTANT: Your task_query MUST be EXACTLY the Compound/Molecule Name only (e.g. 'aspirin'). Do NOT pass sentences."
        )
        self.register_tool(PubChemTool())
        self.register_tool(ChEMBLTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [ChemAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        # Execute both tools to get a comprehensive chemical profile
        # Note: In a real advanced system, this could be parallelized via asyncio.gather
        pubchem_tool = self.tools[0]
        chembl_tool = self.tools[1]
        
        pubchem_res = await pubchem_tool.execute(task_query, max_results=1)
        chembl_res = await chembl_tool.execute(task_query, max_results=3)
        
        return {
            "query": task_query,
            "pubchem_data": pubchem_res,
            "chembl_data": chembl_res
        }
