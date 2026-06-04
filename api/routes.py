from fastapi import APIRouter, Depends
from api.models import QueryRequest, QueryResponse
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
from database.connection import AsyncSessionLocal
from database.models import QueryLog
import json

router = APIRouter()

# Dependency to provide the Coordinator
def get_coordinator():
    coordinator = CoordinatorAgent()
    # Register agents
    lit_agent = LiteratureAgent()
    var_agent = VariantAgent()
    prot_agent = ProteinAgent()
    geno_agent = GenomicsAgent()
    chem_agent = ChemAgent()
    pathway_agent = PathwayAgent()
    expr_agent = ExpressionAgent()
    interaction_agent = InteractionAgent()
    ontology_agent = OntologyAgent()
    structure_agent = StructureAgent()
    pharma_agent = PharmacogenomicsAgent()
    disease_agent = DiseaseAgent()
    tax_agent = TaxonomyAgent()
    dbsnp_agent = DbSNPAgent()
    
    coordinator.register_agent(lit_agent)
    coordinator.register_agent(var_agent)
    coordinator.register_agent(prot_agent)
    coordinator.register_agent(geno_agent)
    coordinator.register_agent(chem_agent)
    coordinator.register_agent(pathway_agent)
    coordinator.register_agent(expr_agent)
    coordinator.register_agent(interaction_agent)
    coordinator.register_agent(ontology_agent)
    coordinator.register_agent(structure_agent)
    coordinator.register_agent(pharma_agent)
    coordinator.register_agent(disease_agent)
    coordinator.register_agent(tax_agent)
    coordinator.register_agent(dbsnp_agent)
    return coordinator

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, coordinator: CoordinatorAgent = Depends(get_coordinator)):
    # 1. Execute agent workflow
    result = await coordinator.execute_workflow(request.query)
    
    # 2. Log request and result to Database
    async with AsyncSessionLocal() as session:
        log_entry = QueryLog(
            user_query=request.query,
            plan=json.dumps(result["plan"], ensure_ascii=False),
            evidence=json.dumps(result.get("evidence", []), ensure_ascii=False),
            final_answer=result["final_answer"]
        )
        session.add(log_entry)
        await session.commit()
    
    # 3. Return JSON response
    return QueryResponse(
        answer=result["final_answer"],
        plan=result["plan"],
        evidence_collected=result["evidence_collected"]
    )
