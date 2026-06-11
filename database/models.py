import json
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from datetime import datetime
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    email = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSetting(Base):
    __tablename__ = "user_settings"
    
    email = Column(String, ForeignKey("users.email"), primary_key=True, index=True)
    api_keys = Column(Text, default="{}") # Store as JSON string: {"GEMINI_API_KEY": "..."}
    db_configs = Column(Text, default="{}") # Store as JSON string
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, index=True)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True, index=True)
    user_email = Column(String, index=True, nullable=True) # Optional for backward compatibility
    user_query = Column(String, index=True)
    language = Column(String, nullable=True)
    plan = Column(Text)       # Storing JSON string
    evidence = Column(Text)   # Storing JSON string
    final_answer = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
