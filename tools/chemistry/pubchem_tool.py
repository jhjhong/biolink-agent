import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class PubChemTool(ScientificTool):
    @property
    def name(self) -> str:
        return "PubChem Compound Search"

    @property
    def description(self) -> str:
        return "Retrieve precise molecular weights, formulas, and SMILES strings for chemical compounds or drugs using PubChem."

    async def execute(self, query: str, max_results: int = 1, **kwargs) -> Dict[str, Any]:
        # query is expected to be a chemical name (e.g., aspirin)
        clean_query = query.strip()
        url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{clean_query}/property/MolecularFormula,MolecularWeight,IUPACName,CanonicalSMILES/JSON"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=15.0)
                if response.status_code == 404:
                    return {"status": "success", "results": [], "message": f"No compound found in PubChem for: {clean_query}"}
                response.raise_for_status()
                data = response.json()
                
                properties = data.get("PropertyTable", {}).get("Properties", [])
                
                return {
                    "status": "success",
                    "query": query,
                    "results": properties[:max_results],
                    "metadata": {"count": len(properties), "source": "PubChem"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"PubChem API Error: {str(e)}"}
