from typing import Dict, Any
from agents.base import BaseAgent
from tools.ontology.quickgo_tool import QuickGOTool

class OntologyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="OntologyAgent", 
            description="Handles searches for Gene Ontology (GO) terms, biological processes, and molecular functions. IMPORTANT: Your task_query MUST be EXACTLY a keyword (e.g. 'apoptosis') or a GO ID (e.g. 'GO:0006915')."
        )
        self.register_tool(QuickGOTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [OntologyAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=3)
        return result
