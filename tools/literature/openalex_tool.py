import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class OpenAlexTool(ScientificTool):
    """Tool for searching literature on OpenAlex."""
    
    @property
    def name(self) -> str:
        return "OpenAlex Literature Search"

    @property
    def description(self) -> str:
        return "Search scholarly works across multiple disciplines using OpenAlex."

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        base_url = "https://api.openalex.org/works"
        params = {
            "search": query,
            "per-page": max_results
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # OpenAlex strongly recommends an email in polite pool, but it works without it for small tests.
                # To be polite, we can add a generic header or params.
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = data.get("results", [])
                articles = []
                for item in results:
                    authors = [a.get("author", {}).get("display_name", "") for a in item.get("authorships", [])]
                    articles.append({
                        "title": item.get("title", ""),
                        "authors": authors,
                        "publication_year": item.get("publication_year", ""),
                        "source_url": item.get("id", ""), # OpenAlex ID URL
                        "doi": item.get("doi", "")
                    })
                    
                return {
                    "status": "success",
                    "query": query,
                    "results": articles,
                    "metadata": {
                        "count": len(articles),
                        "source": "OpenAlex"
                    }
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to reach OpenAlex API: {str(e)}"
                }
