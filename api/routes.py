from fastapi import APIRouter, Depends, HTTPException
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

from sqlalchemy.future import select
from database.models import User, UserSetting, QueryLog
from core.context import request_api_keys
from api.models import UserSettingsRequest

@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest, coordinator: CoordinatorAgent = Depends(get_coordinator)):
    # 0. Load user settings if user_email provided
    if request.user_email:
        async with AsyncSessionLocal() as session:
            # Upsert User to ensure foreign keys don't fail
            result = await session.execute(select(User).where(User.email == request.user_email))
            user = result.scalars().first()
            if not user:
                user = User(email=request.user_email)
                session.add(user)
                await session.commit()
            
            # Fetch UserSettings
            result = await session.execute(select(UserSetting).where(UserSetting.email == request.user_email))
            user_setting = result.scalars().first()
            if user_setting and user_setting.api_keys:
                try:
                    request_api_keys.set(json.loads(user_setting.api_keys))
                except:
                    pass

    # 1. Execute agent workflow
    result = await coordinator.execute_workflow(request.query)
    
    # 2. Log request and result to Database
    async with AsyncSessionLocal() as session:
        log_entry = QueryLog(
            user_email=request.user_email,
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

@router.get("/settings/{email}")
async def get_settings(email: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(UserSetting).where(UserSetting.email == email))
        user_setting = result.scalars().first()
        if user_setting:
            return {
                "api_keys": json.loads(user_setting.api_keys or "{}"),
                "db_configs": json.loads(user_setting.db_configs or "{}")
            }
        return {"api_keys": {}, "db_configs": {}}

@router.post("/settings")
async def update_settings(request: UserSettingsRequest):
    async with AsyncSessionLocal() as session:
        # Upsert User
        result = await session.execute(select(User).where(User.email == request.user_email))
        user = result.scalars().first()
        if not user:
            user = User(email=request.user_email)
            session.add(user)
            await session.commit()
            
        result = await session.execute(select(UserSetting).where(UserSetting.email == request.user_email))
        user_setting = result.scalars().first()
        
        if not user_setting:
            user_setting = UserSetting(
                email=request.user_email,
                api_keys=json.dumps(request.api_keys or {}),
                db_configs=json.dumps(request.db_configs or {})
            )
            session.add(user_setting)
        else:
            if request.api_keys is not None:
                user_setting.api_keys = json.dumps(request.api_keys)
            if request.db_configs is not None:
                user_setting.db_configs = json.dumps(request.db_configs)
                
        await session.commit()
    return {"status": "success"}

@router.get("/history/{email}")
async def get_history(email: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(QueryLog)
            .where(QueryLog.user_email == email)
            .order_by(QueryLog.created_at.desc())
            .limit(50)
        )
        logs = result.scalars().all()
        return [{"id": log.id, "query": log.user_query, "created_at": log.created_at} for log in logs]

@router.get("/history/chat/{log_id}")
async def get_chat_history(log_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(QueryLog).where(QueryLog.id == log_id))
        log = result.scalars().first()
        if not log:
            raise HTTPException(status_code=404, detail="Chat history not found")
        
        # Parse plan back into objects
        try:
            plan = json.loads(log.plan) if log.plan else []
        except:
            plan = []
            
        try:
            evidence = json.loads(log.evidence) if log.evidence else []
        except:
            evidence = []
            
        return {
            "id": log.id,
            "query": log.user_query,
            "created_at": log.created_at,
            "answer": log.final_answer,
            "plan": plan,
            "evidence_collected": len(evidence) if isinstance(evidence, list) else 0
        }
