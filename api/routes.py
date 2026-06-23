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
from agents.gnomad_agent import GnomadAgent
from database.connection import AsyncSessionLocal
from database.models import QueryLog, Conversation, User, UserSetting
from core.llm_provider import LLMProvider
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
    gnomad_agent = GnomadAgent()
    
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
    coordinator.register_agent(gnomad_agent)
    return coordinator

from sqlalchemy.future import select
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

    # 1. Check for Zero-Token Cache (Exact Match)
    cached_result = None
    async with AsyncSessionLocal() as session:
        # We look for the most recent successful query matching the exact string
        cache_check = await session.execute(
            select(QueryLog)
            .where(QueryLog.user_query == request.query)
            .where(QueryLog.final_answer != None)
            .order_by(QueryLog.created_at.desc())
            .limit(1)
        )
        cached_log = cache_check.scalars().first()
        if cached_log:
            print(f"-> [Cache Hit] Found identical query from {cached_log.created_at}")
            try:
                cached_result = {
                    "plan": json.loads(cached_log.plan) if cached_log.plan else [],
                    "evidence": json.loads(cached_log.evidence) if cached_log.evidence else [],
                    "final_answer": cached_log.final_answer
                }
                cached_result["evidence_collected"] = len(cached_result["evidence"]) if isinstance(cached_result["evidence"], list) else 0
            except json.JSONDecodeError:
                cached_result = None

    if cached_result:
        result = cached_result
    else:
        # 1.5 Execute agent workflow if no cache
        result = await coordinator.execute_workflow(request.query)

    # 2. Handle Conversation and Log Request
    conversation_id = request.conversation_id
    
    async with AsyncSessionLocal() as session:
        if not conversation_id:
            # Create a new conversation and generate a title
            llm = LLMProvider()
            title = await llm.generate_title(request.query)
            
            new_conv = Conversation(
                user_email=request.user_email,
                title=title
            )
            session.add(new_conv)
            await session.commit()
            await session.refresh(new_conv)
            conversation_id = new_conv.id
            
        log_entry = QueryLog(
            conversation_id=conversation_id,
            user_email=request.user_email,
            user_query=request.query,
            plan=json.dumps(result["plan"], ensure_ascii=False),
            evidence=json.dumps(result.get("evidence", []), ensure_ascii=False),
            final_answer=result["final_answer"]
        )
        session.add(log_entry)
        
        # Optionally update conversation's updated_at
        if conversation_id:
            res = await session.execute(select(Conversation).where(Conversation.id == conversation_id))
            conv = res.scalars().first()
            if conv:
                conv.updated_at = log_entry.created_at
                
        await session.commit()
    
    # 3. Return JSON response
    return QueryResponse(
        answer=result["final_answer"],
        plan=result["plan"],
        evidence_collected=result["evidence_collected"],
        conversation_id=conversation_id
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
            select(Conversation)
            .where(Conversation.user_email == email)
            .order_by(Conversation.updated_at.desc())
            .limit(50)
        )
        conversations = result.scalars().all()
        return [{"id": c.id, "title": c.title, "created_at": c.created_at, "updated_at": c.updated_at} for c in conversations]

@router.get("/history/chat/{conversation_id}")
async def get_chat_history(conversation_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(QueryLog)
            .where(QueryLog.conversation_id == conversation_id)
            .order_by(QueryLog.created_at.asc())
        )
        logs = result.scalars().all()
        
        if not logs:
            raise HTTPException(status_code=404, detail="Chat history not found")
        
        history_list = []
        for log in logs:
            # Parse plan back into objects
            try:
                plan = json.loads(log.plan) if log.plan else []
            except:
                plan = []
                
            try:
                evidence = json.loads(log.evidence) if log.evidence else []
            except:
                evidence = []
                
            history_list.append({
                "id": log.id,
                "query": log.user_query,
                "created_at": log.created_at,
                "answer": log.final_answer,
                "plan": plan,
                "evidence_collected": len(evidence) if isinstance(evidence, list) else 0
            })
            
        return history_list

from pydantic import BaseModel
class RenameRequest(BaseModel):
    title: str

@router.put("/history/{conversation_id}")
async def rename_conversation(conversation_id: int, request: RenameRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = result.scalars().first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conv.title = request.title
        await session.commit()
        return {"status": "success", "title": conv.title}

@router.delete("/history/{conversation_id}")
async def delete_conversation(conversation_id: int):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = result.scalars().first()
        if not conv:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        # Delete associated query logs first
        await session.execute(QueryLog.__table__.delete().where(QueryLog.conversation_id == conversation_id))
        # Delete conversation
        await session.delete(conv)
        await session.commit()
        return {"status": "success"}
