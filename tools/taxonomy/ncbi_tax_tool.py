import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class NCBITaxonomyTool(ScientificTool):
    @property
    def name(self) -> str:
        return "NCBI Taxonomy Search"

    @property
    def description(self) -> str:
        return "Search for the taxonomy, scientific name, and lineage of species, bacteria, or viruses."

    async def execute(self, query: str, max_results: int = 3, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip()
        search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. Search for TaxID
                search_params = {
                    "db": "taxonomy",
                    "term": clean_query,
                    "retmode": "json",
                    "retmax": max_results
                }
                search_res = await client.get(search_url, params=search_params, timeout=10.0)
                search_res.raise_for_status()
                id_list = search_res.json().get("esearchresult", {}).get("idlist", [])
                
                if not id_list:
                    return {"status": "success", "results": [], "message": f"No taxonomy found for: {clean_query}"}
                
                # 2. Fetch summary for IDs
                summary_params = {
                    "db": "taxonomy",
                    "id": ",".join(id_list),
                    "retmode": "json"
                }
                summary_res = await client.get(summary_url, params=summary_params, timeout=10.0)
                summary_res.raise_for_status()
                data = summary_res.json().get("result", {})
                
                results = []
                for tax_id in id_list:
                    if tax_id in data:
                        entry = data[tax_id]
                        results.append({
                            "tax_id": tax_id,
                            "scientific_name": entry.get("scientificname", ""),
                            "common_name": entry.get("commonname", ""),
                            "rank": entry.get("rank", "")
                        })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "metadata": {"count": len(results), "source": "NCBI Taxonomy"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"NCBI Taxonomy API Error: {str(e)}"}
