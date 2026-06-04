import httpx
import asyncio
from fastapi import APIRouter

router = APIRouter()

# Lightweight ping endpoints to avoid rate limits and large payloads
PING_ENDPOINTS = {
    "PubMed": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed",
    "Ensembl": "https://rest.ensembl.org/info/ping?content-type=application/json",
    "UniProt": "https://rest.uniprot.org/uniprotkb/search?query=TP53&size=0",
    "AlphaFold": "https://alphafold.ebi.ac.uk/api/prediction/P04637",
    "RCSB PDB": "https://data.rcsb.org/rest/v1/core/entry/1TUP",
    "STRING DB": "https://string-db.org/api/json/version",
    "QuickGO": "https://www.ebi.ac.uk/QuickGO/services/ontology/go/about",
    "Reactome": "https://reactome.org/ContentService/data/database/version",
    "Human Protein Atlas": "https://www.proteinatlas.org/api/search_download.php?search=TP53&format=json&columns=g",
    "ClinVar": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=clinvar",
    "GWAS Catalog": "https://www.ebi.ac.uk/gwas/rest/api/",
    "PubChem": "https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/cid/2244/property/MolecularWeight/JSON",
    "ChEMBL": "https://www.ebi.ac.uk/chembl/api/data/status?format=json",
    "DGIdb": "https://dgidb.org/api/v2/interactions.json?genes=EGFR",
    "NCBI Taxonomy": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=taxonomy"
}

# Global state to store the latest health check results
HEALTH_STATE = {
    "status": "checking",
    "databases": {}
}

async def ping_service(client: httpx.AsyncClient, name: str, url: str) -> dict:
    try:
        response = await client.get(url, timeout=10.0) # 10s timeout to avoid false negatives
        if response.status_code < 500:
            return {name: "online"}
        return {name: "offline"}
    except Exception:
        return {name: "offline"}

async def background_health_check():
    """Background task to periodically check database health without blocking API calls."""
    while True:
        try:
            results = {}
            async with httpx.AsyncClient() as client:
                tasks = [ping_service(client, name, url) for name, url in PING_ENDPOINTS.items()]
                completed = await asyncio.gather(*tasks)
                for res in completed:
                    results.update(res)
            
            is_healthy = all(status == "online" for status in results.values())
            HEALTH_STATE["status"] = "healthy" if is_healthy else "degraded"
            HEALTH_STATE["databases"] = results
            print("Background health check completed.")
        except Exception as e:
            print(f"Background health check failed: {e}")
            
        # Wait for 30 minutes (1800 seconds) before the next check
        await asyncio.sleep(1800)

@router.get("/health")
async def health_check():
    """Instantly return the latest cached health status."""
    return HEALTH_STATE
