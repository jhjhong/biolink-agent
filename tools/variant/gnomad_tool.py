import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class GnomadTool(ScientificTool):
    @property
    def name(self) -> str:
        return "gnomAD Variant Frequency Search"

    @property
    def description(self) -> str:
        return "Search for variant allele frequencies and variant IDs in the Genome Aggregation Database (gnomAD)."

    async def execute(self, query: str, dataset: str = "gnomad_r4", **kwargs) -> Dict[str, Any]:
        """
        Query gnomAD API to resolve an rsID or variant ID and fetch its allele frequency.
        """
        url = "https://gnomad.broadinstitute.org/api"
        
        # Query 1: Resolve rsID/query to variant_id
        search_query = """
        query($query: String!, $dataset: DatasetId!) {
          variant_search(query: $query, dataset: $dataset) {
            variant_id
          }
        }
        """
        
        headers = {"Content-Type": "application/json"}
        
        async with httpx.AsyncClient() as client:
            try:
                # Step 1: Search variant
                response = await client.post(
                    url, 
                    json={"query": search_query, "variables": {"query": query, "dataset": dataset}},
                    headers=headers,
                    timeout=15.0
                )
                response.raise_for_status()
                data = response.json()
                
                variants = data.get("data", {}).get("variant_search", [])
                if not variants:
                    return {"status": "success", "results": [], "message": "No variants found in gnomAD."}
                
                variant_id = variants[0].get("variant_id")
                
                # Step 2: Fetch detailed variant info (frequencies)
                detail_query = """
                query($variant_id: String!, $dataset: DatasetId!) {
                  variant(variant_id: $variant_id, dataset: $dataset) {
                    variant_id
                    reference_genome
                    chrom
                    pos
                    ref
                    alt
                    exome {
                      ac
                      an
                      af
                    }
                    genome {
                      ac
                      an
                      af
                    }
                  }
                }
                """
                detail_response = await client.post(
                    url,
                    json={"query": detail_query, "variables": {"variant_id": variant_id, "dataset": dataset}},
                    headers=headers,
                    timeout=15.0
                )
                detail_response.raise_for_status()
                detail_data = detail_response.json()
                
                variant_info = detail_data.get("data", {}).get("variant")
                if not variant_info:
                    return {"status": "success", "results": [{"variant_id": variant_id}], "message": "Variant resolved but details not found."}
                
                return {
                    "status": "success",
                    "query": query,
                    "results": [variant_info],
                    "metadata": {
                        "source": "gnomAD",
                        "dataset": dataset
                    }
                }
                
            except httpx.RequestError as e:
                return {
                    "status": "error",
                    "message": f"Failed to reach gnomAD API: {str(e)}"
                }
