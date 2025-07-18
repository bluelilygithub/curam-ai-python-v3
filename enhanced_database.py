"""
Enhanced Property Database V3
SQLAlchemy-based database service that maintains compatibility with existing interface
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from models import PropertyQuery, SystemMetrics, DemoUser, db_config

logger = logging.getLogger(__name__)

class PropertyDatabaseV3:
    """Enhanced database service with SQLAlchemy - maintains existing interface"""
    
    def __init__(self, db_path: str = None):
        """Initialize with SQLAlchemy configuration"""
        self.db_config = db_config
        self.init_database()
        self.seed_demo_users()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            self.db_config.create_tables()
            logger.info("✅ SQLAlchemy database initialized successfully")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {str(e)}")
            raise e
    
    def seed_demo_users(self):
        """Create demo users if they don't exist"""
        try:
            session = self.db_config.get_session()
            
            # Check if demo users already exist
            if session.query(DemoUser).count() > 0:
                session.close()
                return
            
            demo_users = [
                DemoUser(
                    user_id='sarah_buyer',
                    name='Sarah Chen',
                    profile_type='first_buyer',
                    description='First home buyer focused on affordability and transport links',
                    avatar='👩‍💼',
                    preferences=json.dumps({
                        "max_price": 600000,
                        "priorities": ["affordability", "transport", "safety"]
                    })
                ),
                DemoUser(
                    user_id='michael_investor',
                    name='Michael Rodriguez',
                    profile_type='investor',
                    description='Property investor focused on rental yield and growth',
                    avatar='👨‍💻',
                    preferences=json.dumps({
                        "focus": "investment",
                        "priorities": ["yield", "growth", "market_trends"]
                    })
                )
            ]
            
            for user in demo_users:
                session.add(user)
            
            session.commit()
            session.close()
            logger.info("✅ Demo users created successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to seed demo users: {str(e)}")
    
    # EXISTING INTERFACE METHODS (maintained for compatibility)
    
    def store_query(self, question: str, answer: str, question_type: str = 'custom', 
                   processing_time: float = 0, success: bool = True, **kwargs) -> int:
        """Store a query - enhanced with optional new fields"""
        try:
            session = self.db_config.get_session()
            
            query = PropertyQuery(
                question=question,
                question_type=question_type,
                answer=answer,
                processing_time=processing_time,
                success=success,
                # New optional fields
                location_detected=kwargs.get('location_detected'),
                llm_provider=kwargs.get('llm_provider'),
                confidence_score=kwargs.get('confidence_score'),
                user_id=kwargs.get('user_id', 'anonymous')
            )
            
            session.add(query)
            session.commit()
            query_id = query.id
            session.close()
            
            logger.info(f"✅ Stored query with ID: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"❌ Failed to store query: {str(e)}")
            raise e
    
    def get_query_history(self, limit: int = 50, user_id: str = None) -> List[Dict]:
        """Get recent query history - enhanced with optional user filtering"""
        try:
            session = self.db_config.get_session()
            
            query = session.query(PropertyQuery).order_by(desc(PropertyQuery.created_at))
            
            # Filter by user if specified
            if user_id:
                query = query.filter(PropertyQuery.user_id == user_id)
            
            results = query.limit(limit).all()
            session.close()
            
            history = []
            for row in results:
                history.append({
                    'id': row.id,
                    'question': row.question,
                    'question_type': row.question_type,
                    'answer': row.answer,
                    'success': row.success,
                    'processing_time': row.processing_time,
                    'created_at': row.created_at.isoformat() if row.created_at else None,
                    # Enhanced fields
                    'location_detected': row.location_detected,
                    'llm_provider': row.llm_provider,
                    'confidence_score': row.confidence_score,
                    'user_id': row.user_id
                })
            
            return history
            
        except Exception as e:
            logger.error(f"❌ Failed to get query history: {str(e)}")
            return []
    
    def get_popular_questions(self, limit: int = 10, user_id: str = None) -> List[Dict]:
        """Get most frequently asked questions - enhanced with user filtering"""
        try:
            session = self.db_config.get_session()
            
            query = session.query(
                PropertyQuery.question,
                func.count(PropertyQuery.id).label('count'),
                func.max(PropertyQuery.created_at).label('last_asked')
            ).filter(PropertyQuery.success == True)
            
            if user_id:
                query = query.filter(PropertyQuery.user_id == user_id)
            
            results = query.group_by(PropertyQuery.question)\
                          .order_by(desc('count'), desc('last_asked'))\
                          .limit(limit).all()
            
            session.close()
            
            questions = []
            for row in results:
                questions.append({
                    'question': row.question,
                    'count': row.count,
                    'last_asked': row.last_asked.isoformat() if row.last_asked else None
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"❌ Failed to get popular questions: {str(e)}")
            return []
    
    def get_database_stats(self) -> Dict:
        """Get database statistics - enhanced with new metrics"""
        try:
            session = self.db_config.get_session()
            
            total_queries = session.query(PropertyQuery).count()
            successful_queries = session.query(PropertyQuery).filter(PropertyQuery.success == True).count()
            
            avg_processing_time = session.query(func.avg(PropertyQuery.processing_time))\
                                        .filter(PropertyQuery.processing_time.isnot(None)).scalar() or 0
            
            # Enhanced stats
            user_count = session.query(func.count(func.distinct(PropertyQuery.user_id))).scalar()
            
            # LLM provider breakdown
            claude_queries = session.query(PropertyQuery).filter(PropertyQuery.llm_provider == 'claude').count()
            gemini_queries = session.query(PropertyQuery).filter(PropertyQuery.llm_provider == 'gemini').count()
            
            # Location breakdown
            location_stats = session.query(
                PropertyQuery.location_detected,
                func.count(PropertyQuery.id).label('count')
            ).filter(PropertyQuery.location_detected.isnot(None))\
             .group_by(PropertyQuery.location_detected).all()
            
            session.close()
            
            return {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                'avg_processing_time': round(avg_processing_time, 2),
                # Enhanced stats
                'unique_users': user_count,
                'llm_provider_breakdown': {
                    'claude': claude_queries,
                    'gemini': gemini_queries
                },
                'location_breakdown': {loc.location_detected: loc.count for loc in location_stats},
                'database_type': 'PostgreSQL' if 'postgresql' in self.db_config.database_url else 'SQLite'
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {str(e)}")
            return {}
    
    def clear_all_data(self):
        """Clear all data from the database"""
        try:
            session = self.db_config.get_session()
            session.query(PropertyQuery).delete()
            session.query(SystemMetrics).delete()
            session.commit()
            session.close()
            logger.info("✅ Database cleared successfully")
        except Exception as e:
            logger.error(f"❌ Failed to clear database: {str(e)}")
            raise e
    
    # NEW V3 METHODS (for enhanced features)
    
    def get_demo_users(self) -> List[Dict]:
        """Get available demo users"""
        try:
            session = self.db_config.get_session()
            users = session.query(DemoUser).all()
            session.close()
            
            return [
                {
                    'user_id': user.user_id,
                    'name': user.name,
                    'profile_type': user.profile_type,
                    'description': user.description,
                    'avatar': user.avatar,
                    'preferences': json.loads(user.preferences) if user.preferences else {}
                }
                for user in users
            ]
        except Exception as e:
            logger.error(f"❌ Failed to get demo users: {str(e)}")
            return []
    
    def get_user_stats(self, user_id: str) -> Dict:
        """Get statistics for a specific user"""
        try:
            session = self.db_config.get_session()
            
            user = session.query(DemoUser).filter(DemoUser.user_id == user_id).first()
            if not user:
                session.close()
                return {}
            
            query_count = session.query(PropertyQuery).filter(PropertyQuery.user_id == user_id).count()
            
            avg_processing_time = session.query(func.avg(PropertyQuery.processing_time))\
                                        .filter(PropertyQuery.user_id == user_id,
                                               PropertyQuery.processing_time.isnot(None)).scalar() or 0
            
            recent_queries = session.query(PropertyQuery)\
                                   .filter(PropertyQuery.user_id == user_id)\
                                   .order_by(desc(PropertyQuery.created_at))\
                                   .limit(5).all()
            
            session.close()
            
            return {
                'user': {
                    'name': user.name,
                    'profile_type': user.profile_type,
                    'description': user.description,
                    'avatar': user.avatar
                },
                'stats': {
                    'total_queries': query_count,
                    'avg_processing_time': round(avg_processing_time, 2),
                    'success_rate': 100  # Could calculate actual success rate
                },
                'recent_queries': [
                    {
                        'id': q.id,
                        'question': q.question,
                        'location': q.location_detected,
                        'processing_time': q.processing_time,
                        'created_at': q.created_at.isoformat() if q.created_at else None,
                        'success': q.success
                    }
                    for q in recent_queries
                ]
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get user stats: {str(e)}")
            return {}
    
    def record_system_metric(self, metric_type: str, value: float, user_id: str = 'system', metadata: dict = None):
        """Record system performance metrics"""
        try:
            session = self.db_config.get_session()
            
            metric = SystemMetrics(
                metric_type=metric_type,
                metric_value=value,
                user_id=user_id,
                metadata=json.dumps(metadata) if metadata else None
            )
            
            session.add(metric)
            session.commit()
            session.close()
            
        except Exception as e:
            logger.error(f"❌ Failed to record metric: {str(e)}")

# For backwards compatibility - create alias to existing interface
PropertyDatabase = PropertyDatabaseV3