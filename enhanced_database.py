"""
Enhanced Property Database V3
SQLAlchemy-based database service that maintains compatibility with existing interface
"""

import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Import Config, assuming it's available and defines DATABASE_PATH
from config import Config 

logger = logging.getLogger(__name__)

# Define the base for declarative models
Base = declarative_base()

# Define the Query model for SQLAlchemy
class Query(Base):
    __tablename__ = 'queries' # Table name in the database
    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    question_type = Column(String(50), default='custom')
    processing_time = Column(Float)
    success = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
    # V3 enhanced fields for analytics and user tracking
    location_detected = Column(String(100))
    llm_provider = Column(String(50))
    confidence_score = Column(Float)
    user_id = Column(String(100), default='anonymous') # User ID for personalization

    def __repr__(self):
        return f"<Query(id={self.id}, user_id='{self.user_id}', question='{self.question[:50]}...')>"

# Main Database Service Class
class PropertyDatabase: # Assuming your class name is PropertyDatabase as in app.py
    def __init__(self):
        # Determine database URL: use DATABASE_URL environment variable for PostgreSQL,
        # otherwise, fall back to SQLite using Config.DATABASE_PATH.
        database_url = os.getenv('DATABASE_URL')
        if database_url:
            self.engine = create_engine(database_url)
            logger.info("Using PostgreSQL database.")
        else:
            # Ensure Config.DATABASE_PATH is defined in your config.py
            self.engine = create_engine(f'sqlite:///{Config.DATABASE_PATH}')
            logger.info(f"Using SQLite database at {Config.DATABASE_PATH}.")

        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        # Configure sessionmaker to create new sessions
        self.Session = sessionmaker(bind=self.engine)
        logger.info("Database initialized successfully.")

    def store_query(self, question: str, answer: str, question_type: str, 
                    processing_time: float, success: bool, location_detected: str, 
                    llm_provider: str, confidence_score: float, user_id: str) -> int:
        """
        Stores a new query and its analysis result in the database.
        Returns the ID of the newly created query.
        """
        session = self.Session()
        try:
            new_query = Query(
                question=question,
                answer=answer,
                question_type=question_type,
                processing_time=processing_time,
                success=success,
                location_detected=location_detected,
                llm_provider=llm_provider,
                confidence_score=confidence_score,
                user_id=user_id,
                created_at=datetime.now() # Ensure timestamp is explicitly set here
            )
            session.add(new_query)
            session.commit()
            logger.info(f"Query stored: '{question[:50]}...' by user '{user_id}'. ID: {new_query.id}")
            return new_query.id
        except Exception as e:
            session.rollback() # Rollback changes in case of error
            logger.error(f"Failed to store query '{question[:50]}...': {e}")
            raise # Re-raise the exception after logging
        finally:
            session.close()

    def get_query_history(self, limit: int = 20, user_id: str = None) -> list:
        """
        Retrieves recent query history, optionally filtered by user_id.
        Returns a list of dictionaries, newest first.
        """
        session = self.Session()
        try:
            query = session.query(Query).order_by(Query.created_at.desc()) # Order by newest first
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            history_records = query.limit(limit).all()
            
            # Convert SQLAlchemy objects to dictionaries for API response
            history_data = []
            for record in history_records:
                history_data.append({
                    'id': record.id,
                    'question': record.question,
                    'answer_summary': record.answer[:200] + "..." if len(record.answer) > 200 else record.answer,
                    'processing_time': record.processing_time,
                    'success': record.success,
                    'created_at': record.created_at.isoformat(),
                    'user_id': record.user_id,
                    'location': record.location_detected,
                    'llm_provider': record.llm_provider
                })
            logger.debug(f"Retrieved {len(history_data)} history records for user '{user_id}'.")
            return history_data
        except Exception as e:
            logger.error(f"Failed to get query history for user '{user_id}': {e}")
            return []
        finally:
            session.close()

    def get_user_stats(self, user_id: str) -> dict:
        """
        Retrieves statistics for a specific user.
        Includes total queries, average processing time, and recent queries.
        """
        session = self.Session()
        try:
            total_queries = session.query(Query).filter_by(user_id=user_id).count()
            
            # Calculate average processing time
            avg_time_result = session.query(
                func.avg(Query.processing_time)
            ).filter_by(user_id=user_id).scalar()
            avg_processing_time = round(avg_time_result, 2) if avg_time_result else 0
            
            # Get recent queries for this user (e.g., last 5)
            recent_queries = self.get_query_history(limit=5, user_id=user_id)
            
            # Get user info (assuming a separate User table or hardcoded demo users)
            # For this demo, user info is assumed to come from a pre-defined list or simple lookup
            user_info = self._get_demo_user_info(user_id)

            return {
                'user': user_info,
                'stats': {
                    'total_queries': total_queries,
                    'avg_processing_time': avg_processing_time,
                },
                'recent_queries': recent_queries
            }
        except Exception as e:
            logger.error(f"Failed to get stats for user '{user_id}': {e}")
            return None # Return None or raise exception to indicate failure
        finally:
            session.close()

    def _get_demo_user_info(self, user_id: str) -> dict:
        """Helper to get hardcoded demo user info. In a real app, this would be from a DB."""
        demo_users_data = {
            'sarah_buyer': {
                'user_id': 'sarah_buyer',
                'name': 'Sarah Chen',
                'profile_type': 'first_buyer',
                'description': 'First home buyer focused on affordability and transport links',
                'avatar': '👩‍💼'
            },
            'michael_investor': {
                'user_id': 'michael_investor',
                'name': 'Michael Rodriguez',
                'profile_type': 'investor',
                'description': 'Property investor focused on rental yield and growth',
                'avatar': '👨‍💻'
            }
        }
        return demo_users_data.get(user_id, {'user_id': user_id, 'name': 'Unknown User', 'profile_type': 'guest', 'avatar': '👤'})

    def get_demo_users(self) -> list:
        """Retrieves a list of all demo users for the frontend."""
        # For a simple demo, returning hardcoded users.
        # In a real app, this would query a 'users' table.
        return [
            self._get_demo_user_info('sarah_buyer'),
            self._get_demo_user_info('michael_investor')
        ]

    def get_database_stats(self) -> dict:
        """Retrieves general database statistics."""
        session = self.Session()
        try:
            total_queries = session.query(Query).count()
            last_query_time = session.query(Query.created_at).order_by(Query.created_at.desc()).first()
            
            return {
                'total_queries_stored': total_queries,
                'last_query_at': last_query_time[0].isoformat() if last_query_time else None,
                'database_engine': str(self.engine.url).split('+')[0]
            }
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {'error': str(e)}
        finally:
            session.close()

    def get_popular_questions(self, limit: int = 5, user_id: str = None) -> list:
        """
        Retrieves the most popular questions based on frequency,
        optionally filtered by user_id.
        Returns a list of dictionaries with 'question' and 'count'.
        """
        session = self.Session()
        try:
            # Import func from sqlalchemy here to avoid circular dependencies if needed globally
            from sqlalchemy import func
            
            # Group by question and count occurrences
            query = session.query(
                Query.question,
                func.count(Query.question).label('count')
            )
            
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            # Order by count in descending order and limit
            popular_records = query.group_by(Query.question) \
                                   .order_by(func.count(Query.question).desc()) \
                                   .limit(limit).all()
            
            popular_data = []
            for record in popular_records:
                # To include query_id for deletion, we would need to join with the original query ID,
                # or select the most recent query_id for each question.
                # For simplicity here, we just use the question and count.
                # If deletion is by question text, this is fine. If by ID, it's more complex.
                # Assuming here the deletion relies on the `id` from `recent_user_queries`
                # which are actual individual query instances. For popular_global, we might not have a single ID.
                # To resolve this, you might store a representative query_id or allow deletion by question text.
                # For now, popular questions obtained this way won't have a direct query_id for deletion,
                # unless you modify the schema to link popular questions to a specific ID.
                # A common solution is to take the LATEST query_id for each distinct question.
                # Let's adjust to try and get a query_id for deletion from the most recent entry of that question.
                latest_query_for_question = session.query(Query.id)\
                                                    .filter(Query.question == record.question)\
                                                    .order_by(Query.created_at.desc())\
                                                    .first()
                
                popular_data.append({
                    'question': record.question,
                    'count': record.count,
                    'id': latest_query_for_question.id if latest_query_for_question else None # Provide a representative ID
                })
            
            logger.debug(f"Retrieved {len(popular_data)} popular questions.")
            return popular_data
        except Exception as e:
            logger.error(f"Failed to get popular questions: {e}")
            return []
        finally:
            session.close()

    def delete_query(self, query_id: int) -> bool:
        """
        Deletes a query record by its ID.
        Returns True if deleted, False if not found.
        """
        session = self.Session()
        try:
            query = session.query(Query).filter_by(id=query_id).first()
            if query:
                session.delete(query)
                session.commit()
                logger.info(f"Query ID {query_id} successfully deleted from database.")
                return True
            else:
                logger.warning(f"Attempted to delete query ID {query_id}, but it was not found.")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting query ID {query_id}: {e}")
            raise # Re-raise the exception after logging and rollback
        finally:
            session.close()