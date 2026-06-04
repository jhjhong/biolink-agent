import httpx
from typing import Any, Dict
from tools.base import ScientificTool

class DGIdbTool(ScientificTool):
    @property
    def name(self) -> str:
        return "DGIdb Drug-Gene Interaction Search"

    @property
    def description(self) -> str:
        return "Search for clinical drugs that target or interact with a specific gene using the Drug Gene Interaction Database (DGIdb)."

    async def execute(self, query: str, max_results: int = 5, **kwargs) -> Dict[str, Any]:
        clean_query = query.strip().upper()
        url = "https://dgidb.org/api/graphql"
        
        graphql_query = """
        query($gene: [String!]) {
          genes(names: $gene) {
            nodes {
              name
              interactions {
                drug {
                  name
                }
                interactionAttributes {
                  name
                  value
                }
              }
            }
          }
        }
        """
        
        async with httpx.AsyncClient() as client:
            try:
                headers = {"User-Agent": "Mozilla/5.0", "Content-Type": "application/json"}
                payload = {"query": graphql_query, "variables": {"gene": [clean_query]}}
                response = await client.post(url, json=payload, headers=headers, timeout=15.0)
                response.raise_for_status()
                data = response.json()
                
                results = []
                nodes = data.get("data", {}).get("genes", {}).get("nodes", [])
                if nodes:
                    for interaction in nodes[0].get("interactions", []):
                        drug_name = interaction.get("drug", {}).get("name")
                        if drug_name:
                            results.append({
                                "drugName": drug_name,
                                "interactionDetails": interaction.get("interactionAttributes", [])
                            })
                
                return {
                    "status": "success",
                    "query": query,
                    "results": results[:max_results],
                    "metadata": {"count": len(results), "source": "DGIdb v5 GraphQL"}
                }
            except httpx.HTTPError as e:
                return {"status": "error", "message": f"DGIdb API HTTP Error: {str(e)}"}
            except Exception as e:
                return {"status": "error", "message": f"DGIdb API Error: {str(e)}"}
