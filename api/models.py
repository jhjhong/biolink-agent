from pydantic import BaseModel
from typing import List, Any, Optional, Dict

class QueryRequest(BaseModel):
    query: str
    user_email: Optional[str] = None
    conversation_id: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    plan: List[Any]
    evidence_collected: int
    conversation_id: int

class UserSettingsRequest(BaseModel):
    user_email: str
    api_keys: Optional[Dict[str, str]] = None
    db_configs: Optional[Dict[str, str]] = None

