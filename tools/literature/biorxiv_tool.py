import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class BiorxivTool(ScientificTool):
    """Tool for searching literature on bioRxiv using Crossref."""
    
    @property
    def name(self) -> str:
        return "bioRxiv Literature Search"

    @property
    def description(self) -> str:
        return "Search for biological and medical preprints on bioRxiv via Crossref."

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        # bioRxiv doesn't have a simple text search API, but we can query Crossref for bioRxiv preprints
        base_url = "https://api.crossref.org/works"
        params = {
            "query": query,
            "filter": "prefix:10.1101", # bioRxiv DOI prefix
            "rows": max_results,
            "select": "title,author,abstract,URL,published,DOI"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                items = data.get("message", {}).get("items", [])
                articles = []
                for item in items:
                    title = item.get("title", [""])[0] if item.get("title") else ""
                    authors = [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in item.get("author", [])]
                    url = item.get("URL", "")
                    
                    articles.append({
                        "title": title,
                        "authors": authors,
                        "source_url": url,
                        "doi": item.get("DOI", "")
                    })
                    
                return {
                    "status": "success",
                    "query": query,
                    "results": articles,
                    "metadata": {
                        "count": len(articles),
                        "source": "bioRxiv"
                    }
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to reach Crossref API for bioRxiv: {str(e)}"
                }
