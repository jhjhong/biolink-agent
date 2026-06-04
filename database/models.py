import json
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from database.connection import Base

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(String, index=True)
    language = Column(String, nullable=True)
    plan = Column(Text)       # Storing JSON string
    evidence = Column(Text)   # Storing JSON string
    final_answer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
