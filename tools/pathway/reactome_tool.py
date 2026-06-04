import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class ReactomeTool(ScientificTool):
    @property
    def name(self) -> str:
        return "Reactome Pathway Search"

    @property
    def description(self) -> str:
        return "Search for biological pathways involving a specific gene or protein using Reactome."

    async def execute(self, query: str, max_results: int = 3, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip()
        url = "https://reactome.org/ContentService/search/query"
        
        async with httpx.AsyncClient() as client:
            params = {
                "query": clean_query,
                "species": "Homo sapiens",
                "types": "Pathway"
            }
            try:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data.get("results", [])[:max_results]:
                    if entry.get("entries"):
                        for item in entry.get("entries", [])[:3]: # take top 3 from each cluster
                            results.append({
                                "stId": item.get("stId"),
                                "name": item.get("name"),
                                "compartment": [c.get("name") for c in item.get("compartment", [])]
                            })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results[:max_results],
                    "metadata": {"count": len(results), "source": "Reactome"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"Reactome API Error: {str(e)}"}
