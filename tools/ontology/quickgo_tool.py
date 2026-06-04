import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class QuickGOTool(ScientificTool):
    @property
    def name(self) -> str:
        return "QuickGO Gene Ontology Search"

    @property
    def description(self) -> str:
        return "Search for Gene Ontology (GO) terms to understand Biological Processes, Molecular Functions, and Cellular Components."

    async def execute(self, query: str, max_results: int = 3, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip()
        url = "https://www.ebi.ac.uk/QuickGO/services/ontology/go/search"
        
        async with httpx.AsyncClient() as client:
            params = {
                "query": clean_query,
                "limit": max_results
            }
            try:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data.get("results", []):
                    results.append({
                        "id": entry.get("id"),
                        "name": entry.get("name"),
                        "aspect": entry.get("aspect"), # biological_process, molecular_function, cellular_component
                        "definition": entry.get("definition", {}).get("text", "")
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "metadata": {"count": len(results), "source": "QuickGO"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"QuickGO API Error: {str(e)}"}
