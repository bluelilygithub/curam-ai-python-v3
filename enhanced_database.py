import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, func
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
class PropertyDatabase:
    def __init__(self):
        database_url = os.getenv('DATABASE_URL')
        
        # --- CRITICAL CHANGE: REMOVE SQLITE FALLBACK AND FORCE PGSQL ---
        # This will explicitly crash the app if DATABASE_URL is not set,
        # providing a clearer error than the SQLite permission error.
        if not database_url:
            logger.critical("❌ DATABASE_URL environment variable is NOT set. Cannot connect to PostgreSQL.")
            raise ValueError("DATABASE_URL environment variable must be set for PostgreSQL connection.")
        
        self.engine = create_engine(database_url)
        logger.info("Using PostgreSQL database (DATABASE_URL detected).")
        # --- END CRITICAL CHANGE ---

        # Only create_all if in development mode or explicitly needed for initial setup.
        # In a real production app, you would typically use a migration tool like Alembic.
        if os.getenv('FLASK_ENV') == 'development' or os.getenv('DB_INIT_ON_STARTUP') == 'true':
            logger.info("Attempting to create database tables (development/init mode).")
            try:
                Base.metadata.create_all(self.engine)
                logger.info("Database tables checked/created.")
            except Exception as e:
                logger.error(f"Failed to create database tables: {e}. Check DB connection/permissions.")
                raise # Re-raise to crash if table creation fails
        else:
            logger.info("Skipping database table creation on startup (production mode).")

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
        Returns a dictionary with user info, stats, and recent queries.
        Returns an empty/default structure if no queries found, rather than None.
        """
        session = self.Session()
        try:
            # Get total queries for the user
            total_queries = session.query(Query).filter_by(user_id=user_id).count()
            
            # Calculate average processing time for successful queries
            # func.avg needs to be imported from sqlalchemy
            avg_time_result = session.query(
                func.avg(Query.processing_time)
            ).filter_by(user_id=user_id, success=True).scalar()
            
            # Ensure avg_processing_time is always a number, even if no queries or result is None
            avg_processing_time = round(avg_time_result, 2) if avg_time_result is not None else 0.0
            
            # Get recent queries for this user (e.g., last 5)
            # This relies on your existing get_query_history method
            recent_queries = self.get_query_history(limit=5, user_id=user_id)
            
            # Get user info (assuming a separate User table or hardcoded demo users)
            user_info = self._get_demo_user_info(user_id) # This function gets hardcoded info
            
            # Return a complete dictionary structure, even if no queries exist for the user
            return {
                'user': user_info,
                'stats': {
                    'total_queries': total_queries,
                    'avg_processing_time': avg_processing_time,
                    'successful_queries': session.query(Query).filter_by(user_id=user_id, success=True).count(),
                    'failed_queries': session.query(Query).filter_by(user_id=user_id, success=False).count(),
                },
                'recent_queries': recent_queries
            }
        except Exception as e:
            logger.error(f"Failed to get user stats for '{user_id}': {e}")
            # On error, return an empty but valid structure to avoid crashing the frontend
            user_info = self._get_demo_user_info(user_id)
            return {
                'user': user_info,
                'stats': {
                    'total_queries': 0,
                    'avg_processing_time': 0.0,
                    'successful_queries': 0,
                    'failed_queries': 0,
                    'error': str(e) # Include error detail in stats
                },
                'recent_queries': []
            }
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
        Returns a list of dictionaries with 'question', 'count', and a representative 'id'.
        """
        session = self.Session()
        try:
            # Step 1: Count occurrences of each question
            counted_questions_subquery = session.query(
                Query.question,
                func.count(Query.question).label('question_count'),
                func.max(Query.id).label('representative_id') # Get max ID for each question
            ).group_by(Query.question)

            if user_id:
                counted_questions_subquery = counted_questions_subquery.filter_by(user_id=user_id)
            
            # Order by count in descending order and limit
            popular_records = counted_questions_subquery.order_by(func.count(Query.question).desc()) \
                                   .limit(limit).all()
            
            popular_data = []
            for record in popular_records:
                popular_data.append({
                    'question': record.question,
                    'count': record.count,
                    'id': record.representative_id # Use the representative ID
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