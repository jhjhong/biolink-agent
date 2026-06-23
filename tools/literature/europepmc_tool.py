import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class EuropePmcTool(ScientificTool):
    """Tool for searching literature on Europe PMC."""
    
    @property
    def name(self) -> str:
        return "Europe PMC Literature Search"

    @property
    def description(self) -> str:
        return "Search life sciences literature including PubMed, PMC, and preprints on Europe PMC."

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        base_url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
        params = {
            "query": query,
            "format": "json",
            "resultType": "lite",
            "pageSize": max_results
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                result_list = data.get("resultList", {}).get("result", [])
                articles = []
                for item in result_list:
                    articles.append({
                        "title": item.get("title", ""),
                        "authors": item.get("authorString", "").split(", "),
                        "journal": item.get("journalTitle", ""),
                        "pubYear": item.get("pubYear", ""),
                        "source_url": f"https://europepmc.org/article/{item.get('source', '')}/{item.get('id', '')}"
                    })
                    
                return {
                    "status": "success",
                    "query": query,
                    "results": articles,
                    "metadata": {
                        "count": len(articles),
                        "source": "Europe PMC"
                    }
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to reach Europe PMC API: {str(e)}"
                }
