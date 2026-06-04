import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class HPATool(ScientificTool):
    @property
    def name(self) -> str:
        return "Human Protein Atlas Expression Search"

    @property
    def description(self) -> str:
        return "Search for tissue or cell expression levels for a specific gene using the Human Protein Atlas (HPA)."

    async def execute(self, query: str, max_results: int = 1, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip()
        url = "https://www.proteinatlas.org/api/search_download.php"
        
        async with httpx.AsyncClient() as client:
            params = {
                "search": clean_query,
                "format": "json",
                "columns": "g,t", # Gene, Tissue expression
                "compress": "no"
            }
            try:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data[:max_results]:
                    tissue_expression = entry.get("Tissue expression cluster", "")
                    results.append({
                        "gene": entry.get("Gene"),
                        "tissue_expression_cluster": tissue_expression
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "metadata": {"count": len(results), "source": "Human Protein Atlas"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"HPA API Error: {str(e)}"}
