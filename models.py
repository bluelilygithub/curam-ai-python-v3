"""
SQLAlchemy Models for Australian Property Intelligence V3
FIXED: Removed reserved word 'metadata' conflict
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, Index, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os

Base = declarative_base()

class PropertyQuery(Base):
    """Enhanced property query model - matches your existing structure plus new fields"""
    __tablename__ = 'property_queries'
    
    # Existing fields (exact match to your current SQLite table)
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    question_type = Column(String(20), default='custom')
    answer = Column(Text)
    processing_time = Column(Float)
    success = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    
    # New enhanced fields for V3 features
    location_detected = Column(String(50))  # Brisbane, Sydney, National, etc.
    llm_provider = Column(String(20))      # claude, gemini
    confidence_score = Column(Float)        # 0.0 to 1.0
    user_id = Column(String(50), default='anonymous')  # For user switching feature
    
    def __repr__(self):
        return f"<PropertyQuery {self.id}: {self.question[:50]}...>"

class SystemMetrics(Base):
    """System performance and analytics tracking"""
    __tablename__ = 'system_metrics'
    
    id = Column(Integer, primary_key=True)
    metric_type = Column(String(50), nullable=False)  # 'response_time', 'llm_performance', etc.
    metric_value = Column(Float, nullable=False)
    user_id = Column(String(50), default='system')
    extra_data = Column(Text)  # FIXED: Changed from 'metadata' to 'extra_data' (JSON)
    recorded_at = Column(DateTime, default=func.now())

class DemoUser(Base):
    """Demo user profiles for user switching feature"""
    __tablename__ = 'demo_users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    profile_type = Column(String(50), nullable=False)  # 'first_buyer', 'investor'
    description = Column(Text)
    avatar = Column(String(10))  # Emoji
    preferences = Column(Text)  # JSON string
    created_at = Column(DateTime, default=func.now())

# Database indexes for performance
Index('idx_queries_created_at', PropertyQuery.created_at)
Index('idx_queries_user_id', PropertyQuery.user_id)
Index('idx_queries_success', PropertyQuery.success)
Index('idx_metrics_type_date', SystemMetrics.metric_type, SystemMetrics.recorded_at)

# Database configuration
class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.database_url = self._get_database_url()
        self.engine = self._create_engine()
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def _get_database_url(self):
        """Get database URL - PostgreSQL on Railway, SQLite locally"""
        # Railway PostgreSQL URL
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # Fix Railway postgres:// to postgresql://
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        
        # Local SQLite fallback
        return 'sqlite:///property_intelligence_v3.db'
    
    def _create_engine(self):
        """Create database engine with appropriate settings"""
        if self.database_url.startswith('sqlite'):
            return create_engine(
                self.database_url,
                connect_args={"check_same_thread": False},
                echo=False
            )
        else:
            return create_engine(
                self.database_url,
                pool_size=5,
                max_overflow=10,
                echo=False
            )
    
    def create_tables(self):
        """Create all database tables"""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

# Global database instance
db_config = DatabaseConfig()