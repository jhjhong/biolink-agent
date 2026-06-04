import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class AlphaFoldDBTool(ScientificTool):
    @property
    def name(self) -> str:
        return "AlphaFold DB Structure Search"

    @property
    def description(self) -> str:
        return "Retrieve 3D structure predictions, PDB download URLs, and PAE/pLDDT scores using a UniProt Accession ID."

    async def execute(self, query: str, max_results: int = 1, **kwargs) -> Dict[str, Any]:
        # query should be exactly the UniProt ID (e.g., P04637)
        uniprot_id = query.strip()
        url = f"https://alphafold.ebi.ac.uk/api/prediction/{uniprot_id}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=15.0)
                if response.status_code == 404:
                    return {"status": "success", "results": [], "message": f"No AlphaFold prediction found for UniProt ID: {uniprot_id}"}
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data:
                    results.append({
                        "uniprotAccession": entry.get("uniprotAccession"),
                        "pdbUrl": entry.get("pdbUrl"),
                        "cifUrl": entry.get("cifUrl"),
                        "paeImageUrl": entry.get("paeImageUrl"),
                        "paeDocUrl": entry.get("paeDocUrl")
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results[:max_results],
                    "metadata": {"count": len(results), "source": "AlphaFold DB"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"AlphaFold API Error: {str(e)}"}
