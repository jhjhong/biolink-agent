import asyncio
import json
from mcp.server.fastmcp import FastMCP
from database.connection import init_db
from agents.coordinator import CoordinatorAgent
from agents.literature_agent import LiteratureAgent
from agents.variant_agent import VariantAgent
from agents.protein_agent import ProteinAgent
from agents.genomics_agent import GenomicsAgent
from agents.chem_agent import ChemAgent
from agents.pathway_agent import PathwayAgent
from agents.expression_agent import ExpressionAgent
from agents.interaction_agent import InteractionAgent
from agents.ontology_agent import OntologyAgent
from agents.structure_agent import StructureAgent
from agents.pharmacogenomics_agent import PharmacogenomicsAgent
from agents.disease_agent import DiseaseAgent
from agents.taxonomy_agent import TaxonomyAgent
from agents.dbsnp_agent import DbSNPAgent
from agents.gnomad_agent import GnomadAgent

# Initialize the FastMCP server
mcp = FastMCP("BioLink-Agent", description="BioLink Multi-Agent Scientific Research Platform")

# Global variables to hold our initialized agent state
coordinator = None

async def setup_biolink():
    global coordinator
    if coordinator is not None:
        return
        
    print("Initializing Database...", flush=True)
    await init_db()
    
    print("Registering Sub-agents...", flush=True)
    coordinator = CoordinatorAgent()
    coordinator.register_agent(LiteratureAgent())
    coordinator.register_agent(VariantAgent())
    coordinator.register_agent(ProteinAgent())
    coordinator.register_agent(GenomicsAgent())
    coordinator.register_agent(ChemAgent())
    coordinator.register_agent(PathwayAgent())
    coordinator.register_agent(ExpressionAgent())
    coordinator.register_agent(InteractionAgent())
    coordinator.register_agent(OntologyAgent())
    coordinator.register_agent(StructureAgent())
    coordinator.register_agent(PharmacogenomicsAgent())
    coordinator.register_agent(DiseaseAgent())
    coordinator.register_agent(TaxonomyAgent())
    coordinator.register_agent(DbSNPAgent())
    coordinator.register_agent(GnomadAgent())
    print("BioLink Agents ready.", flush=True)

@mcp.tool()
async def ask_biolink(query: str) -> str:
    """Submit a natural language biomedical question to the BioLink multi-agent platform.
    The platform will automatically route the query to relevant databases (PubMed, ClinVar, Ensembl, UniProt, etc.),
    gather evidence, and return a synthesized answer.
    
    Args:
        query: A specific scientific or biomedical question. Can be in English or Traditional Chinese.
    """
    await setup_biolink()
    
    try:
        result = await coordinator.execute_workflow(query, history=[])
        
        # Format the result nicely
        answer = result.get("final_answer", "")
        evidence_collected = result.get("evidence_collected", 0)
        
        response = f"BioLink Answer:\n{answer}\n\n[Metadata: Retrieved evidence from {evidence_collected} sources using BioLink agents.]"
        return response
    except Exception as e:
        return f"Error executing BioLink query: {str(e)}"

if __name__ == "__main__":
    # Ensure database and agents are initialized before processing events
    # FastMCP uses synchronous run() method
    mcp.run(transport="stdio")
