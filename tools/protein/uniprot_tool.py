import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class UniProtTool(ScientificTool):
    @property
    def name(self) -> str:
        return "UniProt Protein Search"

    @property
    def description(self) -> str:
        return "Search for protein sequences, functions, domains, and annotations using UniProtKB."

    async def execute(self, query: str, max_results: int = 3, **kwargs) -> Dict[str, Any]:
        url = "https://rest.uniprot.org/uniprotkb/search"
        
        # Clean the query if LLM passed a sentence
        clean_query = query.split()[-1] if " " in query else query.strip()
        
        async with httpx.AsyncClient() as client:
            params = {
                "query": f"(gene:{clean_query}) AND (model_organism:9606)",
                "format": "json",
                "size": max_results,
                "fields": "accession,id,protein_name,gene_names,organism_name,sequence"
            }
            try:
                response = await client.get(url, params=params, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for entry in data.get("results", []):
                    results.append({
                        "accession": entry.get("primaryAccession"),
                        "name": entry.get("proteinDescription", {}).get("recommendedName", {}).get("fullName", {}).get("value", "Unknown"),
                        "genes": [g.get("geneName", {}).get("value") for g in entry.get("genes", [])],
                        "organism": entry.get("organism", {}).get("scientificName", "Unknown"),
                        "sequence_length": entry.get("sequence", {}).get("length", 0)
                    })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results,
                    "metadata": {"count": len(results), "source": "UniProt"}
                }
            except httpx.RequestError as e:
                return {"status": "error", "message": f"UniProt API Error: {str(e)}"}
