import asyncio
from typing import Dict, Any
from agents.base import BaseAgent
from tools.literature.pubmed_tool import PubMedTool
from tools.literature.arxiv_tool import ArxivTool
from tools.literature.biorxiv_tool import BiorxivTool
from tools.literature.europepmc_tool import EuropePmcTool
from tools.literature.openalex_tool import OpenAlexTool

class LiteratureAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="LiteratureAgent", 
            description="Handles searches for biomedical literature, papers, and evidence using PubMed, arXiv, bioRxiv, Europe PMC, and OpenAlex."
        )
        self.register_tool(PubMedTool())
        self.register_tool(ArxivTool())
        self.register_tool(BiorxivTool())
        self.register_tool(EuropePmcTool())
        self.register_tool(OpenAlexTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [LiteratureAgent] Executing tool search for: '{task_query}'")
        if not self.tools:
            return {"error": "No tools registered"}
            
        tasks = []
        for tool in self.tools:
            tasks.append(tool.execute(task_query, max_results=3))
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        aggregated_results = []
        for idx, res in enumerate(results):
            tool_name = self.tools[idx].name
            if isinstance(res, Exception):
                print(f"      [!] Tool {tool_name} failed: {str(res)}")
                continue
            if res.get("status") == "success":
                aggregated_results.extend(res.get("results", []))
            else:
                print(f"      [!] Tool {tool_name} returned error: {res.get('message')}")
                
        return {
            "status": "success",
            "query": task_query,
            "results": aggregated_results,
            "metadata": {
                "total_count": len(aggregated_results),
                "sources_queried": [t.name for t in self.tools]
            }
        }
