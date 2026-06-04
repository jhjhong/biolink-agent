from typing import Dict, Any
from agents.base import BaseAgent
from tools.expression.hpa_tool import HPATool

class ExpressionAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ExpressionAgent", 
            description="Handles searches for gene expression levels across human tissues and cell types using HPA. IMPORTANT: Your task_query MUST be EXACTLY the Gene Symbol only (e.g. 'ACE2')."
        )
        self.register_tool(HPATool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [ExpressionAgent] Executing tools for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tool = self.tools[0]
        result = await tool.execute(task_query, max_results=1)
        return result
