import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class RCSBPDBTool(ScientificTool):
    @property
    def name(self) -> str:
        return "RCSB PDB Experimental Structure Search"

    @property
    def description(self) -> str:
        return "Search for experimental 3D structures (X-ray, Cryo-EM) in the Protein Data Bank (PDB)."

    async def execute(self, query: str, max_results: int = 3, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip()
        search_url = "https://search.rcsb.org/rcsbsearch/v2/query"
        
        payload = {
          "query": {
            "type": "terminal",
            "service": "full_text",
            "parameters": {
              "value": clean_query
            }
          },
          "return_type": "entry",
          "request_options": {
            "paginate": {
              "start": 0,
              "rows": max_results
            }
          }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. Search for PDB IDs
                search_res = await client.post(search_url, json=payload, timeout=15.0)
                if search_res.status_code == 204: # No content (no matches)
                    return {"status": "success", "results": [], "message": f"No PDB structures found for: {clean_query}"}
                search_res.raise_for_status()
                
                identifiers = [entry["identifier"] for entry in search_res.json().get("result_set", [])]
                
                # 2. Fetch details for each ID
                results = []
                for pdb_id in identifiers:
                    detail_url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
                    detail_res = await client.get(detail_url, timeout=10.0)
                    if detail_res.status_code == 200:
                        data = detail_res.json()
                        struct = data.get("struct", {})
                        rcsb_entry = data.get("rcsb_entry_info", {})
                        results.append({
                            "pdb_id": pdb_id,
                            "title": struct.get("title", ""),
                            "experimental_method": rcsb_entry.get("experimental_method", ""),
                            "resolution_angstrom": rcsb_entry.get("resolution_combined", [None])[0]
                        })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "metadata": {"count": len(results), "source": "RCSB PDB"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"RCSB PDB API Error: {str(e)}"}
