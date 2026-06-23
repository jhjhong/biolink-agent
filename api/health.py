import httpx
import asyncio
import time
from fastapi import APIRouter

router = APIRouter()

# Lightweight ping endpoints to avoid rate limits and large payloads
PING_ENDPOINTS = {
    "PubMed": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=pubmed",
    "arXiv": "http://export.arxiv.org/api/query?search_query=all:electron&max_results=1",
    "bioRxiv": "https://api.crossref.org/works?filter=prefix:10.1101&rows=1",
    "Europe PMC": "https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=test&format=json&resultType=lite&pageSize=1",
    "OpenAlex": "https://api.openalex.org/works?per-page=1",
    "NCBI Sequence": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=nuccore",
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
    "NCBI Taxonomy": "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/einfo.fcgi?db=taxonomy",
    "dbSNP": "https://api.ncbi.nlm.nih.gov/variation/v0/refsnp/7412",
    "gnomAD": "https://gnomad.broadinstitute.org/"
}

# Global state to store the latest health check results
HEALTH_STATE = {
    "status": "checking",
    "databases": {}
}

async def ping_service(client: httpx.AsyncClient, name: str, url: str, max_retries: int = 3, timeout: float = 40.0) -> dict:
    for attempt in range(max_retries):
        try:
            start_time = time.time()
            response = await client.get(url, timeout=timeout)
            elapsed = time.time() - start_time
            if response.status_code < 500:
                if elapsed > 20.0:
                    return {name: "degraded"}
                return {name: "online"}
        except Exception:
            pass
        
        # If it failed and we haven't reached max retries, wait before retrying
        if attempt < max_retries - 1:
            await asyncio.sleep(5) # Wait 5 seconds between retries
            
    return {name: "offline"}

async def quick_health_check():
    """Fast initial health check on startup (10s timeout, no retries).
    This ensures HEALTH_STATE is populated quickly so the frontend
    receives real status data on the first request.
    """
    global HEALTH_STATE
    try:
        results = {}
        async with httpx.AsyncClient() as client:
            tasks = [
                ping_service(client, name, url, max_retries=1, timeout=10.0)
                for name, url in PING_ENDPOINTS.items()
            ]
            completed = await asyncio.gather(*tasks)
            for res in completed:
                results.update(res)
        
        is_healthy = all(status == "online" for status in results.values())
        HEALTH_STATE["status"] = "healthy" if is_healthy else "degraded"
        HEALTH_STATE["databases"] = results
        print(f"Quick health check completed: {results}")
    except Exception as e:
        print(f"Quick health check failed: {e}")

async def background_health_check():
    """Background task to periodically check database health without blocking API calls.
    Runs a quick check immediately on startup, then a full check every 30 minutes.
    """
    # First: fast check so the frontend gets real data quickly
    await quick_health_check()
    
    while True:
        # Wait for 30 minutes before the next full check
        await asyncio.sleep(1800)
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

@router.get("/health")
async def health_check():
    """Instantly return the latest cached health status."""
    return HEALTH_STATE
