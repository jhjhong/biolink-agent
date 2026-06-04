import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class StringDBTool(ScientificTool):
    @property
    def name(self) -> str:
        return "STRING DB Protein Interaction Search"

    @property
    def description(self) -> str:
        return "Retrieve known and predicted protein-protein interactions (PPI) for a given gene/protein in humans using STRING DB."

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip()
        url = "https://string-db.org/api/json/network"
        
        async with httpx.AsyncClient() as client:
            params = {
                "identifiers": clean_query,
                "species": 9606, # Homo sapiens
                "limit": max_results
            }
            try:
                response = await client.get(url, params=params, timeout=15.0)
                if response.status_code == 404:
                    return {"status": "success", "results": [], "message": f"No interactions found for: {clean_query}"}
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data:
                    results.append({
                        "proteinA": entry.get("preferredName_A"),
                        "proteinB": entry.get("preferredName_B"),
                        "score": entry.get("score"),
                        "experimental_score": entry.get("escore"),
                        "database_score": entry.get("dscore")
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results[:max_results],
                    "metadata": {"count": len(results), "source": "STRING DB"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"STRING DB API Error: {str(e)}"}
