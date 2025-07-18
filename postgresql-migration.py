"""
PostgreSQL Database Migration for Brisbane Property Intelligence
Enhanced schema with analytics and trend tracking capabilities
"""

import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json

logger = logging.getLogger(__name__)

class PostgreSQLPropertyDatabase:
    """Enhanced PostgreSQL database for property intelligence with analytics"""
    
    def __init__(self, connection_string: str = None):
        self.connection_string = connection_string or self._get_connection_string()
        self.conn = None
        self.init_database()
    
    def _get_connection_string(self) -> str:
        """Get PostgreSQL connection string from environment or Railway"""
        # Railway PostgreSQL format
        if os.getenv('DATABASE_URL'):
            return os.getenv('DATABASE_URL')
        
        # Manual configuration
        return f"postgresql://{os.getenv('DB_USER', 'postgres')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'property_intelligence')}"
    
    def get_connection(self):
        """Get database connection with error handling"""
        try:
            if not self.conn or self.conn.closed:
                self.conn = psycopg2.connect(
                    self.connection_string,
                    cursor_factory=RealDictCursor
                )
            return self.conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            raise e
    
    def init_database(self):
        """Initialize enhanced PostgreSQL database schema"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Create tables in order of dependencies
            self._create_property_queries_table(cursor)
            self._create_development_applications_table(cursor)
            self._create_data_sources_table(cursor)
            self._create_trend_analysis_table(cursor)
            self._create_analytics_summary_table(cursor)
            
            conn.commit()
            cursor.close()
            logger.info("✅ PostgreSQL database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise e
    
    def _create_property_queries_table(self, cursor):
        """Enhanced property queries table with analytics"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS property_queries (
                id SERIAL PRIMARY KEY,
                question TEXT NOT NULL,
                question_type VARCHAR(50) DEFAULT 'custom',
                answer TEXT,
                processing_time REAL,
                success BOOLEAN DEFAULT FALSE,
                
                -- LLM Processing Details
                claude_success BOOLEAN DEFAULT FALSE,
                gemini_success BOOLEAN DEFAULT FALSE,
                claude_model VARCHAR(100),
                gemini_model VARCHAR(100),
                
                -- Analysis Metadata
                question_category VARCHAR(100),
                suburbs_mentioned TEXT[], -- PostgreSQL array
                confidence_score REAL,
                data_sources_count INTEGER DEFAULT 0,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queries_created_at ON property_queries(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queries_type ON property_queries(question_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queries_success ON property_queries(success)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_queries_category ON property_queries(question_category)')
    
    def _create_development_applications_table(self, cursor):
        """Store real development applications data"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS development_applications (
                id SERIAL PRIMARY KEY,
                application_id VARCHAR(100) UNIQUE NOT NULL,
                
                -- Application Details
                address TEXT NOT NULL,
                suburb VARCHAR(100),
                postcode VARCHAR(10),
                description TEXT,
                application_type VARCHAR(100),
                
                -- Dates
                date_lodged DATE,
                date_decided DATE,
                date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                -- Status
                status VARCHAR(50),
                decision VARCHAR(100),
                
                -- Geolocation
                latitude REAL,
                longitude REAL,
                
                -- Source Information
                source_url TEXT,
                data_source VARCHAR(100) DEFAULT 'planning_alerts',
                
                -- Raw Data
                raw_data JSONB,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for analytics
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dev_apps_suburb ON development_applications(suburb)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dev_apps_date_lodged ON development_applications(date_lodged)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dev_apps_type ON development_applications(application_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dev_apps_status ON development_applications(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_dev_apps_location ON development_applications(latitude, longitude)')
    
    def _create_data_sources_table(self, cursor):
        """Track real data sources and their reliability"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_sources (
                id SERIAL PRIMARY KEY,
                source_name VARCHAR(200) NOT NULL,
                source_type VARCHAR(50), -- rss, api, scraping
                source_url TEXT,
                
                -- Reliability Metrics
                last_successful_fetch TIMESTAMP,
                last_failed_fetch TIMESTAMP,
                success_rate REAL DEFAULT 0.0,
                total_requests INTEGER DEFAULT 0,
                failed_requests INTEGER DEFAULT 0,
                
                -- Data Quality
                data_quality_score REAL DEFAULT 0.0,
                average_response_time REAL DEFAULT 0.0,
                
                -- Configuration
                fetch_interval INTEGER DEFAULT 3600, -- seconds
                is_active BOOLEAN DEFAULT TRUE,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Insert default data sources
        cursor.execute('''
            INSERT INTO data_sources (source_name, source_type, source_url, is_active)
            VALUES 
                ('Planning Alerts API', 'api', 'https://api.planningalerts.org.au/authorities/brisbane/applications.json', TRUE),
                ('Brisbane City Council RSS', 'rss', 'https://www.brisbane.qld.gov.au/about-council/news-media/news/rss', TRUE)
            ON CONFLICT DO NOTHING
        ''')
    
    def _create_trend_analysis_table(self, cursor):
        """Store trend analysis results for predictive analytics"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trend_analysis (
                id SERIAL PRIMARY KEY,
                analysis_type VARCHAR(100) NOT NULL, -- monthly, quarterly, yearly
                category VARCHAR(100) NOT NULL, -- development_applications, suburb_activity, etc.
                
                -- Geographic Scope
                suburb VARCHAR(100),
                area_type VARCHAR(50), -- suburb, region, city-wide
                
                -- Trend Data
                period_start DATE NOT NULL,
                period_end DATE NOT NULL,
                current_value REAL,
                previous_value REAL,
                percentage_change REAL,
                trend_direction VARCHAR(20), -- up, down, stable
                
                -- Confidence and Quality
                confidence_score REAL DEFAULT 0.0,
                data_quality_score REAL DEFAULT 0.0,
                sample_size INTEGER,
                
                -- Metadata
                calculation_method VARCHAR(100),
                notes TEXT,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for trend queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_category ON trend_analysis(category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_suburb ON trend_analysis(suburb)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_trends_period ON trend_analysis(period_start, period_end)')
    
    def _create_analytics_summary_table(self, cursor):
        """Store pre-calculated analytics summaries for performance"""
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analytics_summary (
                id SERIAL PRIMARY KEY,
                summary_type VARCHAR(100) NOT NULL, -- daily, weekly, monthly
                summary_date DATE NOT NULL,
                
                -- Key Metrics
                total_applications INTEGER DEFAULT 0,
                approved_applications INTEGER DEFAULT 0,
                rejected_applications INTEGER DEFAULT 0,
                pending_applications INTEGER DEFAULT 0,
                
                -- Geographic Distribution
                top_suburbs JSONB, -- {"suburb": count, ...}
                application_types JSONB, -- {"type": count, ...}
                
                -- Trends
                week_over_week_change REAL,
                month_over_month_change REAL,
                year_over_year_change REAL,
                
                -- Predictions
                next_week_prediction REAL,
                next_month_prediction REAL,
                prediction_confidence REAL,
                
                -- Timestamps
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                
                UNIQUE(summary_type, summary_date)
            )
        ''')
    
    def migrate_from_sqlite(self, sqlite_db_path: str):
        """Migrate existing data from SQLite to PostgreSQL"""
        try:
            import sqlite3
            
            # Connect to SQLite
            sqlite_conn = sqlite3.connect(sqlite_db_path)
            sqlite_cursor = sqlite_conn.cursor()
            
            # Get existing data
            sqlite_cursor.execute('SELECT * FROM property_queries')
            queries = sqlite_cursor.fetchall()
            
            # Get column names
            sqlite_cursor.execute('PRAGMA table_info(property_queries)')
            columns = [col[1] for col in sqlite_cursor.fetchall()]
            
            # Migrate to PostgreSQL
            postgres_conn = self.get_connection()
            postgres_cursor = postgres_conn.cursor()
            
            for query in queries:
                query_dict = dict(zip(columns, query))
                
                postgres_cursor.execute('''
                    INSERT INTO property_queries 
                    (question, question_type, answer, processing_time, success, created_at)
                    VALUES (%(question)s, %(question_type)s, %(answer)s, %(processing_time)s, %(success)s, %(created_at)s)
                ''', query_dict)
            
            postgres_conn.commit()
            postgres_cursor.close()
            sqlite_conn.close()
            
            logger.info(f"✅ Migrated {len(queries)} queries from SQLite to PostgreSQL")
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            raise e
    
    def store_query(self, question: str, answer: str, question_type: str = 'custom', 
                   processing_time: float = 0, success: bool = True, 
                   analysis_metadata: Dict = None) -> int:
        """Store query with enhanced metadata"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            metadata = analysis_metadata or {}
            
            cursor.execute('''
                INSERT INTO property_queries 
                (question, question_type, answer, processing_time, success,
                 claude_success, gemini_success, claude_model, gemini_model,
                 question_category, suburbs_mentioned, confidence_score, data_sources_count)
                VALUES (%(question)s, %(question_type)s, %(answer)s, %(processing_time)s, %(success)s,
                        %(claude_success)s, %(gemini_success)s, %(claude_model)s, %(gemini_model)s,
                        %(question_category)s, %(suburbs_mentioned)s, %(confidence_score)s, %(data_sources_count)s)
                RETURNING id
            ''', {
                'question': question,
                'question_type': question_type,
                'answer': answer,
                'processing_time': processing_time,
                'success': success,
                'claude_success': metadata.get('claude_success', False),
                'gemini_success': metadata.get('gemini_success', False),
                'claude_model': metadata.get('claude_model'),
                'gemini_model': metadata.get('gemini_model'),
                'question_category': metadata.get('question_category'),
                'suburbs_mentioned': metadata.get('suburbs_mentioned', []),
                'confidence_score': metadata.get('confidence_score'),
                'data_sources_count': metadata.get('data_sources_count', 0)
            })
            
            query_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            
            return query_id
            
        except Exception as e:
            logger.error(f"Failed to store query: {e}")
            raise e
    
    def get_trend_analysis(self, category: str, suburb: str = None, 
                          days_back: int = 30) -> Dict:
        """Get trend analysis for predictive analytics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Calculate trends from development applications
            base_query = '''
                SELECT 
                    DATE_TRUNC('week', date_lodged) as week,
                    COUNT(*) as count,
                    suburb
                FROM development_applications 
                WHERE date_lodged >= %s
            '''
            
            params = [datetime.now() - timedelta(days=days_back)]
            
            if suburb:
                base_query += ' AND suburb = %s'
                params.append(suburb)
            
            base_query += ' GROUP BY week, suburb ORDER BY week'
            
            cursor.execute(base_query, params)
            results = cursor.fetchall()
            
            # Calculate percentage changes
            if len(results) >= 2:
                current_count = results[-1]['count']
                previous_count = results[-2]['count']
                percentage_change = ((current_count - previous_count) / previous_count) * 100
            else:
                percentage_change = 0
            
            cursor.close()
            
            return {
                'category': category,
                'suburb': suburb,
                'current_period_count': results[-1]['count'] if results else 0,
                'previous_period_count': results[-2]['count'] if len(results) >= 2 else 0,
                'percentage_change': round(percentage_change, 1),
                'trend_direction': 'up' if percentage_change > 5 else 'down' if percentage_change < -5 else 'stable',
                'confidence_score': min(len(results) / 10, 1.0),  # More data = higher confidence
                'data_points': len(results)
            }
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            return {}
    
    def get_database_stats(self) -> Dict:
        """Get comprehensive database statistics"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query statistics
            cursor.execute('SELECT COUNT(*) FROM property_queries')
            total_queries = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM property_queries WHERE success = TRUE')
            successful_queries = cursor.fetchone()[0]
            
            cursor.execute('SELECT AVG(processing_time) FROM property_queries WHERE processing_time IS NOT NULL')
            avg_processing_time = cursor.fetchone()[0] or 0
            
            # Development applications statistics
            cursor.execute('SELECT COUNT(*) FROM development_applications')
            total_applications = cursor.fetchone()[0] or 0
            
            cursor.execute('SELECT COUNT(DISTINCT suburb) FROM development_applications')
            unique_suburbs = cursor.fetchone()[0] or 0
            
            # Recent activity
            cursor.execute('''
                SELECT COUNT(*) FROM development_applications 
                WHERE date_scraped >= %s
            ''', [datetime.now() - timedelta(days=7)])
            recent_applications = cursor.fetchone()[0] or 0
            
            cursor.close()
            
            return {
                'total_queries': total_queries,
                'successful_queries': successful_queries,
                'success_rate': (successful_queries / total_queries * 100) if total_queries > 0 else 0,
                'avg_processing_time': round(avg_processing_time, 2),
                'total_development_applications': total_applications,
                'unique_suburbs': unique_suburbs,
                'recent_applications_7_days': recent_applications,
                'database_type': 'PostgreSQL'
            }
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}