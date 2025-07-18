import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional

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
                    answer TEXT,
                    processing_time REAL,
                    success BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {str(e)}")
            raise e
    
    def store_query(self, question: str, answer: str, question_type: str = 'custom', 
                   processing_time: float = 0, success: bool = True) -> int:
        """Store a query and its answer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO property_queries (question, question_type, answer, processing_time, success)
                VALUES (?, ?, ?, ?, ?)
            ''', (question, question_type, answer, processing_time, success))
            
            query_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Stored query with ID: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Failed to store query: {str(e)}")
            raise e
    
    def get_query_history(self, limit: int = 50) -> List[Dict]:
        """Get recent query history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, question, question_type, answer, success, 
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
                    'answer': row[3],
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
            
            conn.close()
            
            return {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                'avg_processing_time': round(avg_processing_time, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {str(e)}")
            return {}
    
    def clear_all_data(self):
        """Clear all data from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM property_queries')
            conn.commit()
            conn.close()
            logger.info("Database cleared successfully")
        except Exception as e:
            logger.error(f"Failed to clear database: {str(e)}")
            raise e