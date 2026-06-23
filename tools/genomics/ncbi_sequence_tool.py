import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class NcbiSequenceFetchTool(ScientificTool):
    """Tool for fetching genomic/protein sequences from NCBI."""
    
    @property
    def name(self) -> str:
        return "NCBI Sequence Fetch"

    @property
    def description(self) -> str:
        return "Fetch nucleotide or protein sequences (FASTA format) from NCBI using E-utilities. Use NCBI accession numbers (e.g. NM_000546) as the query."

    async def execute(self, query: str, **kwargs) -> Dict[str, Any]:
        # Assume query is an accession number or sequence ID
        base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
        
        # We search 'nuccore' by default but we can also search 'protein' if the query suggests it
        db = "nuccore"
        if query.startswith("NP_") or query.startswith("YP_") or query.startswith("WP_"):
            db = "protein"
            
        params = {
            "db": db,
            "id": query,
            "rettype": "fasta",
            "retmode": "text"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(base_url, params=params)
                
                # NCBI returns 400 for bad requests like invalid IDs
                if response.status_code != 200:
                    return {
                        "status": "error",
                        "message": f"Failed to fetch sequence. Invalid ID or API error. (Status {response.status_code})"
                    }
                
                fasta_data = response.text.strip()
                
                if not fasta_data:
                    return {
                        "status": "success",
                        "results": [],
                        "message": "No sequence found for the given ID."
                    }
                    
                return {
                    "status": "success",
                    "query": query,
                    "database": db,
                    "sequence_fasta": fasta_data,
                    "metadata": {
                        "source": "NCBI E-utilities"
                    }
                }
            except Exception as e:
                return {
                    "status": "error",
                    "message": f"Failed to reach NCBI API: {str(e)}"
                }
