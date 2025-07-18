import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Any

logger = logging.getLogger(__name__)

class PropertyDatabase:
    def __init__(self, db_path: str = 'property_intelligence.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main queries table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS property_queries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    question_type TEXT DEFAULT 'custom',
                    claude_analysis TEXT,
                    scraped_data TEXT,
                    gemini_processing TEXT,
                    huggingface_summary TEXT,
                    final_answer TEXT,
                    processing_log TEXT,
                    processing_time REAL,
                    success BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Data sources tracking table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS data_sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    category TEXT,
                    last_accessed TIMESTAMP,
                    last_status TEXT,
                    success_count INTEGER DEFAULT 0,
                    error_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Processing logs table for detailed tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS processing_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_id INTEGER,
                    stage TEXT NOT NULL,
                    message TEXT NOT NULL,
                    status TEXT NOT NULL,
                    execution_time REAL,
                    error_details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (query_id) REFERENCES property_queries (id)
                )
            ''')
            
            # Insert default data sources
            self._insert_default_data_sources(cursor)
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise e
    
    def _insert_default_data_sources(self, cursor):
        """Insert default Brisbane data sources"""
        default_sources = [
            {
                'name': 'Brisbane City Council - Development Applications',
                'url': 'https://www.brisbane.qld.gov.au/planning-building/planning-guidelines-and-tools/online-services/development-applications',
                'source_type': 'government',
                'category': 'development'
            },
            {
                'name': 'Brisbane City Council - News & Media',
                'url': 'https://www.brisbane.qld.gov.au/about-council/news-media',
                'source_type': 'government',
                'category': 'news'
            },
            {
                'name': 'Property Observer Brisbane',
                'url': 'https://www.propertyobserver.com.au/location/brisbane',
                'source_type': 'news',
                'category': 'property_news'
            },
            {
                'name': 'RealEstate.com.au Brisbane News',
                'url': 'https://www.realestate.com.au/news/brisbane/',
                'source_type': 'news',
                'category': 'property_news'
            },
            {
                'name': 'Queensland Government Open Data',
                'url': 'https://www.data.qld.gov.au/',
                'source_type': 'government',
                'category': 'data'
            }
        ]
        
        for source in default_sources:
            cursor.execute('''
                INSERT OR IGNORE INTO data_sources (name, url, source_type, category)
                VALUES (?, ?, ?, ?)
            ''', (source['name'], source['url'], source['source_type'], source['category']))
    
    def store_query(self, question: str, question_type: str = 'custom') -> int:
        """Store a new query and return its ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO property_queries (question, question_type)
                VALUES (?, ?)
            ''', (question, question_type))
            
            query_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Stored query with ID: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Failed to store query: {str(e)}")
            raise e
    
    def update_query_stage(self, query_id: int, stage: str, data: str, success: bool = True):
        """Update a specific stage of query processing"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Update the appropriate column based on stage
            stage_columns = {
                'claude_analysis': 'claude_analysis',
                'scraped_data': 'scraped_data', 
                'gemini_processing': 'gemini_processing',
                'huggingface_summary': 'huggingface_summary',
                'final_answer': 'final_answer'
            }
            
            if stage in stage_columns:
                cursor.execute(f'''
                    UPDATE property_queries 
                    SET {stage_columns[stage]} = ?, success = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (data, success, query_id))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated query {query_id} stage: {stage}")
            
        except Exception as e:
            logger.error(f"Failed to update query stage: {str(e)}")
            raise e
    
    def add_processing_log(self, query_id: int, stage: str, message: str, 
                          status: str = 'success', execution_time: float = None, 
                          error_details: str = None):
        """Add a processing log entry"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO processing_logs 
                (query_id, stage, message, status, execution_time, error_details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (query_id, stage, message, status, execution_time, error_details))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to add processing log: {str(e)}")
    
    def get_query_history(self, limit: int = 50) -> List[Dict]:
        """Get recent query history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, question, question_type, final_answer, success, 
                       processing_time, created_at
                FROM property_queries
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            history = []
            for row in results:
                history.append({
                    'id': row[0],
                    'question': row[1],
                    'question_type': row[2],
                    'final_answer': row[3],
                    'success': bool(row[4]),
                    'processing_time': row[5],
                    'created_at': row[6]
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get query history: {str(e)}")
            return []
    
    def get_popular_questions(self, limit: int = 10) -> List[Dict]:
        """Get most frequently asked questions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT question, COUNT(*) as count, MAX(created_at) as last_asked
                FROM property_queries
                WHERE success = 1
                GROUP BY question
                ORDER BY count DESC, last_asked DESC
                LIMIT ?
            ''', (limit,))
            
            results = cursor.fetchall()
            conn.close()
            
            questions = []
            for row in results:
                questions.append({
                    'question': row[0],
                    'count': row[1],
                    'last_asked': row[2]
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"Failed to get popular questions: {str(e)}")
            return []
    
    def get_query_details(self, query_id: int) -> Optional[Dict]:
        """Get detailed information about a specific query"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get main query data
            cursor.execute('''
                SELECT * FROM property_queries WHERE id = ?
            ''', (query_id,))
            
            query_row = cursor.fetchone()
            if not query_row:
                return None
            
            # Get processing logs
            cursor.execute('''
                SELECT stage, message, status, execution_time, error_details, created_at
                FROM processing_logs
                WHERE query_id = ?
                ORDER BY created_at ASC
            ''', (query_id,))
            
            logs = cursor.fetchall()
            conn.close()
            
            # Build detailed response
            columns = [desc[0] for desc in cursor.description]
            query_data = dict(zip(columns, query_row))
            
            # Add processing logs
            query_data['processing_logs'] = []
            for log in logs:
                query_data['processing_logs'].append({
                    'stage': log[0],
                    'message': log[1],
                    'status': log[2],
                    'execution_time': log[3],
                    'error_details': log[4],
                    'created_at': log[5]
                })
            
            return query_data
            
        except Exception as e:
            logger.error(f"Failed to get query details: {str(e)}")
            return None
    
    def update_data_source_status(self, source_name: str, status: str, success: bool = True):
        """Update data source access status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if success:
                cursor.execute('''
                    UPDATE data_sources 
                    SET last_accessed = CURRENT_TIMESTAMP, 
                        last_status = ?, 
                        success_count = success_count + 1
                    WHERE name = ?
                ''', (status, source_name))
            else:
                cursor.execute('''
                    UPDATE data_sources 
                    SET last_accessed = CURRENT_TIMESTAMP, 
                        last_status = ?, 
                        error_count = error_count + 1
                    WHERE name = ?
                ''', (status, source_name))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to update data source status: {str(e)}")
    
    def get_data_sources(self) -> List[Dict]:
        """Get all configured data sources"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, url, source_type, category, last_accessed, 
                       last_status, success_count, error_count
                FROM data_sources
                ORDER BY source_type, name
            ''')
            
            results = cursor.fetchall()
            conn.close()
            
            sources = []
            for row in results:
                sources.append({
                    'name': row[0],
                    'url': row[1],
                    'source_type': row[2],
                    'category': row[3],
                    'last_accessed': row[4],
                    'last_status': row[5],
                    'success_count': row[6],
                    'error_count': row[7]
                })
            
            return sources
            
        except Exception as e:
            logger.error(f"Failed to get data sources: {str(e)}")
            return []
    
    def clear_all_data(self):
        """Clear all data from the database (for reset functionality)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM processing_logs')
            cursor.execute('DELETE FROM property_queries')
            # Don't delete data_sources as they're configuration
            
            conn.commit()
            conn.close()
            
            logger.info("Database cleared successfully")
            
        except Exception as e:
            logger.error(f"Failed to clear database: {str(e)}")
            raise e
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM property_queries')
            total_queries = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM property_queries WHERE success = 1')
            successful_queries = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(processing_time) FROM property_queries WHERE processing_time IS NOT NULL')
            avg_processing_time = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(*) FROM data_sources')
            total_sources = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                'avg_processing_time': round(avg_processing_time, 2),
                'total_data_sources': total_sources
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {}