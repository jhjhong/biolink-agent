import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class ChEMBLTool(ScientificTool):
    @property
    def name(self) -> str:
        return "ChEMBL Molecule Search"

    @property
    def description(self) -> str:
        return "Search for bioactivity, molecule type, and clinical trial phases for molecules or targets using ChEMBL."

    async def execute(self, query: str, max_results: int = 3, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip()
        url = "https://www.ebi.ac.uk/chembl/api/data/molecule/search"
        
        async with httpx.AsyncClient() as client:
            params = {
                "q": clean_query,
                "format": "json",
                "limit": max_results
            }
            try:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data.get("molecules", []):
                    results.append({
                        "chembl_id": entry.get("molecule_chembl_id"),
                        "pref_name": entry.get("pref_name"),
                        "molecule_type": entry.get("molecule_type"),
                        "max_phase": entry.get("max_phase"),
                        "therapeutic_flag": entry.get("therapeutic_flag")
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "metadata": {"count": len(results), "source": "ChEMBL"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"ChEMBL API Error: {str(e)}"}
