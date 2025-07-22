# models.py (Create this file)

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Declare a base class for declarative models
Base = declarative_base()

# Define your database model for storing queries
class Query(Base):
    __tablename__ = 'queries' # The name of the table in your database
    
    # Core fields for each query
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    question_type = Column(String(50), default='custom') # e.g., 'custom', 'preset', 'voice'
    processing_time = Column(Float) # Time taken for analysis
    success = Column(Boolean, default=True) # Was the analysis successful?
    created_at = Column(DateTime, default=datetime.now) # Timestamp of query creation

    tokens_used = Column(Integer, default=0)  # Tokens consumed by this specific query
    tokens_remaining = Column(Integer)         # Tokens remaining after this query

    
    # Enhanced fields for V3 analytics and user tracking
    location_detected = Column(String(100)) # e.g., 'Brisbane', 'National'
    llm_provider = Column(String(50)) # e.g., 'claude', 'gemini'
    confidence_score = Column(Float) # LLM's confidence or internal score
    user_id = Column(String(100), default='anonymous') # ID of the user who made the query

    def __repr__(self):
        """String representation for debugging."""
        return f"<Query(id={self.id}, user_id='{self.user_id}', question='{self.question[:50]}...')>"


class UserSession(Base):
__tablename__ = 'user_sessions'

id = Column(Integer, primary_key=True, autoincrement=True)
user_id = Column(String(100), nullable=False)
session_start = Column(DateTime, default=datetime.now)
session_end = Column(DateTime)
total_tokens_used = Column(Integer, default=0)
token_limit = Column(Integer, nullable=False)
queries_count = Column(Integer, default=0)
is_active = Column(Boolean, default=True)