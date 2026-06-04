import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class GWASCatalogTool(ScientificTool):
    @property
    def name(self) -> str:
        return "GWAS Catalog Disease & Trait Search"

    @property
    def description(self) -> str:
        return "Search for Genome-Wide Association Studies (GWAS) linking genes to complex diseases and human traits."

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip()
        url = "https://www.ebi.ac.uk/gwas/api/search"
        
        async with httpx.AsyncClient() as client:
            params = {
                "q": clean_query,
                "fq": "resourcename:association"
            }
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = await client.get(url, params=params, headers=headers, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data.get("response", {}).get("docs", [])[:max_results]:
                    results.append({
                        "trait": entry.get("traitName_s"),
                        "study": entry.get("study_s"),
                        "p_value": entry.get("pValue_d"),
                        "association": entry.get("association_s")
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "metadata": {"count": len(results), "source": "GWAS Catalog"}
                }
            except httpx.HTTPError as e:
                return {"status": "error", "message": f"GWAS Catalog API Error: {str(e)}"}
            except Exception as e:
                return {"status": "error", "message": f"Unexpected Error: {str(e)}"}
