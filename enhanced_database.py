import os
import logging
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean, Float, func
from sqlalchemy.orm import sessionmaker
# No longer need declarative_base here, as it's now imported from models.py
from datetime import datetime

# Import Config and models
from config import Config 
from models import Base, Query # Ensure Base and Query are imported from models.py

logger = logging.getLogger(__name__)

class PropertyDatabase:
    def __init__(self):
        # === ENHANCED RAILWAY POSTGRESQL CONNECTION LOGIC ===
        
        # 1. Primary: Try Railway's DATABASE_URL (most common)
        database_url = os.getenv('DATABASE_URL')
        
        # 2. Fallback: Construct from individual Railway variables
        if not database_url:
            pg_host = os.getenv('PGHOST')
            pg_port = os.getenv('PGPORT', '5432')
            pg_user = os.getenv('PGUSER', 'postgres')
            pg_password = os.getenv('PGPASSWORD')
            pg_database = os.getenv('PGDATABASE', 'railway')
            
            if all([pg_host, pg_password]):
                database_url = f"postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}"
                logger.info("✅ Constructed DATABASE_URL from individual Railway variables.")
            else:
                logger.error("❌ Missing Railway PostgreSQL environment variables.")
                logger.error(f"PGHOST: {'✓' if pg_host else '✗'}")
                logger.error(f"PGPASSWORD: {'✓' if pg_password else '✗'}")
                logger.error(f"PGUSER: {pg_user}")
                logger.error(f"PGDATABASE: {pg_database}")
                logger.error(f"PGPORT: {pg_port}")
        
        # 3. Final validation
        if not database_url:
            logger.critical("❌ NO DATABASE CONNECTION POSSIBLE!")
            logger.critical("Missing both DATABASE_URL and individual Railway PostgreSQL variables.")
            logger.critical("Check your Railway PostgreSQL service environment variables.")
            raise ValueError(
                "❌ RAILWAY DATABASE CONNECTION FAILED!\n"
                "Required: Either DATABASE_URL or PGHOST+PGPASSWORD environment variables.\n"
                "Check your Railway PostgreSQL service variables tab."
            )
        
        # 4. Log connection details (safely, without password)
        safe_url = database_url.split('@')[1] if '@' in database_url else "unknown"
        logger.info(f"🔗 Connecting to PostgreSQL: ...@{safe_url}")
        
        # 5. Create SQLAlchemy engine with Railway-optimized settings
        try:
            self.engine = create_engine(
                database_url,
                # Railway-specific optimizations
                pool_size=5,  # Conservative pool size for Railway
                max_overflow=10,
                pool_timeout=30,
                pool_recycle=300,  # Recycle connections every 5 minutes
                connect_args={
                    "sslmode": "require",  # Railway requires SSL
                    "connect_timeout": 10,
                }
            )
            logger.info("✅ PostgreSQL engine created with Railway optimizations.")
        except Exception as e:
            logger.error(f"❌ Failed to create database engine: {e}")
            raise
        
        # 6. Test connection immediately
        try:
            from sqlalchemy import text
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT version()"))
                version = result.fetchone()[0]
                logger.info(f"✅ DATABASE CONNECTION SUCCESSFUL!")
                logger.info(f"📊 PostgreSQL Version: {version[:50]}...")
        except Exception as e:
            logger.error(f"❌ DATABASE CONNECTION TEST FAILED: {e}")
            logger.error("This usually means:")
            logger.error("1. Wrong DATABASE_URL format")
            logger.error("2. Railway PostgreSQL service not running")  
            logger.error("3. Network connectivity issues")
            logger.error("4. Invalid credentials")
            raise ConnectionError(f"Cannot connect to Railway PostgreSQL: {e}")
        
        # 7. Create tables if needed (development/init mode)
        should_init_tables = (
            os.getenv('FLASK_ENV') == 'development' or 
            os.getenv('DB_INIT_ON_STARTUP') == 'true' or
            os.getenv('RAILWAY_ENVIRONMENT') == 'development'  # Railway-specific
        )
        
        if should_init_tables:
            logger.info("🔧 Creating/updating database tables (development mode)...")
            try:
                Base.metadata.create_all(self.engine)
                logger.info("✅ Database tables verified/created successfully.")
            except Exception as e:
                logger.error(f"❌ Failed to create database tables: {e}")
                logger.error("Check database permissions and table structure.")
                raise
        else:
            logger.info("⏭️  Skipping table creation (production mode).")
            
        # 8. Initialize session maker
        self.Session = sessionmaker(bind=self.engine)
        logger.info("🚀 PropertyDatabase initialization complete!")
        
        # 9. Log final status
        self._log_connection_status()
    
    def _log_connection_status(self):
        """Log the current database connection status for debugging."""
        try:
            with self.engine.connect() as conn:
                # Test basic query
                result = conn.execute(func.text("SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';"))
                table_count = result.fetchone()[0]
                logger.info(f"📊 Database Status: {table_count} tables in public schema")
                
                # Check if our specific table exists
                result = conn.execute(
                    func.text("SELECT COUNT(*) FROM information_schema.tables WHERE table_name = 'queries';")
                )
                queries_table_exists = result.fetchone()[0] > 0
                logger.info(f"📋 Queries table exists: {'✅ Yes' if queries_table_exists else '❌ No'}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not verify database status: {e}")

    def store_query(self, question: str, answer: str, question_type: str, 
                    processing_time: float, success: bool, location_detected: str, 
                    llm_provider: str, confidence_score: float, user_id: str,
                    total_tokens_used: int = 0) -> int: # Added total_tokens_used parameter with default
        """
        Stores a new query and its analysis result in the database.
        Returns the ID of the newly created query.
        Also stores the total tokens used for the query.
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
                created_at=datetime.now(),
                total_tokens_used=total_tokens_used # Save the token count
            )
            session.add(new_query)
            session.commit()
            logger.info(f"💾 Query stored: ID {new_query.id} by user '{user_id}'. Tokens: {total_tokens_used}")
            return new_query.id
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Failed to store query for user '{user_id}': {e}")
            raise
        finally:
            session.close()

    def get_query_history(self, limit: int = 20, user_id: str = None) -> list:
        """
        Retrieves recent query history, optionally filtered by user_id.
        Returns a list of dictionaries, newest first, including total_tokens_used.
        """
        session = self.Session()
        try:
            query = session.query(Query).order_by(Query.created_at.desc())
            if user_id:
                query = query.filter_by(user_id=user_id)
            
            history_records = query.limit(limit).all()
            
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
                    'llm_provider': record.llm_provider,
                    'total_tokens_used': record.total_tokens_used # Include tokens in history
                })
            logger.debug(f"📊 Retrieved {len(history_data)} history records for user '{user_id}'.")
            return history_data
        except Exception as e:
            logger.error(f"❌ Failed to get query history for user '{user_id}': {e}")
            return []
        finally:
            session.close()

    def get_user_stats(self, user_id: str) -> dict:
        """
        Retrieves statistics for a specific user, including total token usage.
        Returns a dictionary with user info, stats, and recent queries.
        """
        session = self.Session()
        try:
            total_queries = session.query(Query).filter_by(user_id=user_id).count()
            
            avg_time_result = session.query(
                func.avg(Query.processing_time)
            ).filter_by(user_id=user_id, success=True).scalar()
            
            avg_processing_time = round(avg_time_result, 2) if avg_time_result is not None else 0.0

            # NEW: Calculate total tokens used by the user across all their queries
            total_user_tokens = session.query(
                func.sum(Query.total_tokens_used)
            ).filter_by(user_id=user_id).scalar()
            total_user_tokens = int(total_user_tokens) if total_user_tokens is not None else 0
            
            recent_queries = self.get_query_history(limit=5, user_id=user_id)
            user_info = self._get_demo_user_info(user_id)
            
            return {
                'user': user_info,
                'stats': {
                    'total_queries': total_queries,
                    'avg_processing_time': avg_processing_time,
                    'successful_queries': session.query(Query).filter_by(user_id=user_id, success=True).count(),
                    'failed_queries': session.query(Query).filter_by(user_id=user_id, success=False).count(),
                    'total_tokens_used': total_user_tokens, # Add total tokens used by user
                },
                'recent_queries': recent_queries
            }
        except Exception as e:
            logger.error(f"❌ Failed to get user stats for '{user_id}': {e}")
            user_info = self._get_demo_user_info(user_id)
            return {
                'user': user_info,
                'stats': {
                    'total_queries': 0,
                    'avg_processing_time': 0.0,
                    'successful_queries': 0,
                    'failed_queries': 0,
                    'total_tokens_used': 0, # Return 0 on error
                    'error': str(e)
                },
                'recent_queries': []
            }
        finally:
            session.close()

    def _get_demo_user_info(self, user_id: str) -> dict:
        """Helper to get hardcoded demo user info."""
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
        return demo_users_data.get(user_id, {
            'user_id': user_id, 
            'name': 'Unknown User', 
            'profile_type': 'guest', 
            'avatar': '👤'
        })

    def get_demo_users(self) -> list:
        """Retrieves a list of all demo users for the frontend."""
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
                'database_engine': 'postgresql',
                'connection_status': 'connected'
            }
        except Exception as e:
            logger.error(f"❌ Failed to get database stats: {e}")
            return {
                'error': str(e),
                'connection_status': 'error'
            }
        finally:
            session.close()

    def get_popular_questions(self, limit: int = 5, user_id: str = None) -> list:
        """
        Retrieves the most popular questions based on frequency.
        """
        session = self.Session()
        try:
            counted_questions_subquery = session.query(
                Query.question,
                func.count(Query.question).label('question_count'),
                func.max(Query.id).label('representative_id')
            ).group_by(Query.question)

            if user_id:
                counted_questions_subquery = counted_questions_subquery.filter_by(user_id=user_id)
            
            popular_records = counted_questions_subquery.order_by(func.count(Query.question).desc()) \
                                   .limit(limit).all()
            
            popular_data = []
            for record in popular_records:
                popular_data.append({
                    'question': record.question,
                    'count': record.question_count,
                    'id': record.representative_id
                })
            
            logger.debug(f"📊 Retrieved {len(popular_data)} popular questions.")
            return popular_data
        except Exception as e:
            logger.error(f"❌ Failed to get popular questions: {e}")
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
                logger.info(f"🗑️ Query ID {query_id} successfully deleted.")
                return True
            else:
                logger.warning(f"⚠️ Query ID {query_id} not found for deletion.")
                return False
        except Exception as e:
            session.rollback()
            logger.error(f"❌ Error deleting query ID {query_id}: {e}")
            raise
        finally:
            session.close()