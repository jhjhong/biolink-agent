from pydantic import BaseModel
from typing import List, Any

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    plan: List[Any]
    evidence_collected: int
