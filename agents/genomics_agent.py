import asyncio
from typing import Dict, Any
from agents.base import BaseAgent
from tools.genomics.ensembl_tool import EnsemblTool
from tools.genomics.ncbi_sequence_tool import NcbiSequenceFetchTool

class GenomicsAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="GenomicsAgent", 
            description="Handles searches for genes, genomic coordinates, transcripts, and sequences using Ensembl and NCBI. IMPORTANT: Your task_query MUST be EXACTLY the Gene Symbol or NCBI ID (e.g. 'TP53' or 'NM_000546'). Do NOT pass sentences."
        )
        self.register_tool(EnsemblTool())
        self.register_tool(NcbiSequenceFetchTool())
        
    async def process_task(self, task_query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        print(f"   -> [GenomicsAgent] Executing tool search for: '{task_query}'")
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
                if "sequence_fasta" in res:
                    aggregated_results.append({
                        "source": tool_name,
                        "sequence_fasta": res.get("sequence_fasta")
                    })
                else:
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
