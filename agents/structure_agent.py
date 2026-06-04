from typing import Dict, Any
from agents.base import BaseAgent
from tools.structure.pdb_tool import RCSBPDBTool

class StructureAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="StructureAgent", 
            description="Handles searches for experimental 3D structures (X-ray, Cryo-EM) from the Protein Data Bank (PDB). IMPORTANT: Your task_query MUST be EXACTLY a Protein Name or Gene Symbol (e.g. 'insulin receptor')."
        )
        self.register_tool(RCSBPDBTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [StructureAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=3)
        return result
