from typing import Dict, Any
from agents.base import BaseAgent
from tools.variant.gnomad_tool import GnomadTool

class GnomadAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GnomadAgent", 
            description="Handles queries for genetic variant allele frequencies and constraints using gnomAD."
        )
        self.register_tool(GnomadTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [GnomadAgent] Executing tool search for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        # Depending on the query, we may want to determine dataset, but we will default to gnomad_r4
        result = await tool.execute(task_query, dataset="gnomad_r4")
        return result
