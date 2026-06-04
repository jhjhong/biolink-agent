import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class PubMedTool(ScientificTool):
    """Tool for searching literature on PubMed."""
    
    @property
    def name(self) -> str:
        return "PubMed Literature Search"

    @property
    def description(self) -> str:
        return "Search biomedical literature using PubMed E-utilities. Useful for finding latest research papers, evidence, and citations."

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        """
        Executes a search on PubMed.
        Note: This is a simplified implementation for MVP.
        """
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        async with httpx.AsyncClient() as client:
            # 1. Search for IDs
            search_params = {
                "db": "pubmed",
                "term": query,
                "retmode": "json",
                "retmax": max_results
            }
            try:
                search_response = await client.get(base_url, params=search_params)
                search_response.raise_for_status()
                search_data = search_response.json()
                
                id_list = search_data.get("esearchresult", {}).get("idlist", [])
                
                if not id_list:
                    return {"status": "success", "results": [], "message": "No literature found."}

                # 2. Fetch summaries for the IDs
                summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                summary_params = {
                    "db": "pubmed",
                    "id": ",".join(id_list),
                    "retmode": "json"
                }
                
                summary_response = await client.get(summary_url, params=summary_params)
                summary_response.raise_for_status()
                summary_data = summary_response.json()
                
                articles = []
                result_uids = summary_data.get("result", {}).get("uids", [])
                for uid in result_uids:
                    doc = summary_data["result"][uid]
                    articles.append({
                        "pmid": uid,
                        "title": doc.get("title"),
                        "authors": [a.get("name") for a in doc.get("authors", [])],
                        "journal": doc.get("fulljournalname"),
                        "pubdate": doc.get("pubdate"),
                        "source_url": f"https://pubmed.ncbi.nlm.nih.gov/{uid}/"
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": articles,
                    "metadata": {
                        "count": len(articles),
                        "source": "PubMed"
                    }
                }
                
            except httpx.RequestError as e:
                return {
                    "status": "error",
                    "message": f"Failed to reach PubMed API: {str(e)}"
                }
