import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class ClinVarTool(ScientificTool):
    @property
    def name(self) -> str:
        return "ClinVar Variant Search"

    @property
    def description(self) -> str:
        return "Search for genetic variants, clinical significance, ACMG evidence, and phenotypes in NCBI ClinVar."

    async def execute(self, query: str, max_results: int = 3, **kwargs) -> Dict[str, Any]:
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        
        async with httpx.AsyncClient() as client:
            search_params = {
                "db": "clinvar",
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
                    return {"status": "success", "results": [], "message": "No variants found in ClinVar."}

                summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
                summary_params = {
                    "db": "clinvar",
                    "id": ",".join(id_list),
                    "retmode": "json"
                }
                
                summary_response = await client.get(summary_url, params=summary_params)
                summary_response.raise_for_status()
                summary_data = summary_response.json()
                
                variants = []
                result_uids = summary_data.get("result", {}).get("uids", [])
                for uid in result_uids:
                    doc = summary_data["result"][uid]
                    sig = doc.get("clinical_significance", {}).get("description")
                    if not sig:
                        sig = doc.get("germline_classification", {}).get("description", "Unknown")
                        
                    variants.append({
                        "clinvar_uid": uid,
                        "accession": doc.get("accession_version") or doc.get("accession", ""),
                        "title": doc.get("title", ""),
                        "clinical_significance": sig,
                        "genes": doc.get("genes", []),
                        "traits": doc.get("trait_set", [])
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": variants,
                    "metadata": {
                        "count": len(variants),
                        "source": "ClinVar"
                    }
                }
            except httpx.RequestError as e:
                return {
                    "status": "error",
                    "message": f"Failed to reach ClinVar API: {str(e)}"
                }
