import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class EnsemblTool(ScientificTool):
    @property
    def name(self) -> str:
        return "Ensembl Gene Search"

    @property
    def description(self) -> str:
        return "Search for human genomic features, genes, transcripts, and loci using Ensembl."

    async def execute(self, query: str, max_results: int = 3, **kwargs) -> Dict[str, Any]:
        # Clean up the query in case the LLM still passes extra words
        gene_symbol = query.split()[-1] if " " in query else query.strip()
        url = f"https://rest.ensembl.org/lookup/symbol/homo_sapiens/{gene_symbol}"
        
        async with httpx.AsyncClient() as client:
            headers = {"Content-Type": "application/json"}
            try:
                response = await client.get(url, headers=headers, params={"expand": 1}, timeout=15.0)
                if response.status_code in [400, 404]:
                    return {"status": "success", "results": [], "message": f"No gene found for symbol: {gene_symbol}"}
                response.raise_for_status()
                data = response.json()
                
                return {
                    "status": "success",
                    "query": query,
                    "results": [{
                        "id": data.get("id"),
                        "biotype": data.get("biotype"),
                        "description": data.get("description"),
                        "assembly": data.get("assembly_name"),
                        "seq_region_name": data.get("seq_region_name"),
                        "start": data.get("start"),
                        "end": data.get("end"),
                        "strand": data.get("strand")
                    }],
                    "metadata": {"count": 1, "source": "Ensembl"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"Ensembl API Error: {str(e)}"}
