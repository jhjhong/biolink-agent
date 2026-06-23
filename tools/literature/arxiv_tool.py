import httpx
import xml.etree.ElementTree as ET
from typing import Any, Dict
from tools.base import ScientificTool

class ArxivTool(ScientificTool):
    """Tool for searching literature on arXiv."""
    
    @property
    def name(self) -> str:
        return "arXiv Literature Search"

    @property
    def description(self) -> str:
        return "Search for physics, mathematics, computer science, and quantitative biology preprints on arXiv."

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        base_url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(base_url, params=params)
                response.raise_for_status()
                
                # Parse XML
                root = ET.fromstring(response.text)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                
                articles = []
                for entry in root.findall('atom:entry', ns):
                    title = entry.find('atom:title', ns)
                    summary = entry.find('atom:summary', ns)
                    published = entry.find('atom:published', ns)
                    link = entry.find('atom:id', ns)
                    authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns) if a.find('atom:name', ns) is not None]
                    
                    articles.append({
                        "title": title.text.replace('\n', ' ') if title is not None else "",
                        "abstract": summary.text.replace('\n', ' ') if summary is not None else "",
                        "authors": authors,
                        "published": published.text if published is not None else "",
                        "source_url": link.text if link is not None else ""
                    })
                    
                return {
                    "status": "success",
                    "query": query,
                    "results": articles,
                    "metadata": {
                        "count": len(articles),
                        "source": "arXiv"
                    }
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to reach arXiv API: {str(e)}"
                }
