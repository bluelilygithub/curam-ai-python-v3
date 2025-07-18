"""
Migration script to upgrade from SQLite V2 to PostgreSQL/SQLAlchemy V3
Safely migrates all existing data while adding new features
"""

import sqlite3
import logging
from datetime import datetime
from database_v3 import PropertyDatabaseV3
from models import PropertyQuery, db_config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_existing_data():
    """Migrate data from existing SQLite database to new SQLAlchemy structure"""
    
    old_db_path = 'property_intelligence.db'  # Your existing database
    
    try:
        # Check if old database exists
        try:
            old_conn = sqlite3.connect(old_db_path)
            old_cursor = old_conn.cursor()
            
            # Check if table exists and get row count
            old_cursor.execute("SELECT COUNT(*) FROM property_queries")
            old_count = old_cursor.fetchone()[0]
            
            if old_count == 0:
                logger.info("📭 No existing data to migrate")
                old_conn.close()
                return True
                
            logger.info(f"📊 Found {old_count} existing queries to migrate")
            
        except sqlite3.Error as e:
            logger.info(f"📝 No existing database found ({e}). Starting fresh.")
            return True
        
        # Initialize new V3 database
        logger.info("🚀 Initializing new V3 database...")
        new_db = PropertyDatabaseV3()
        
        # Get existing data
        logger.info("📤 Extracting data from old database...")
        old_cursor.execute('''
            SELECT id, question, question_type, answer, processing_time, success, created_at
            FROM property_queries
            ORDER BY created_at
        ''')
        
        old_data = old_cursor.fetchall()
        old_conn.close()
        
        # Migrate data to new structure
        logger.info("📥 Migrating data to new database...")
        session = db_config.get_session()
        
        migrated_count = 0
        
        for row in old_data:
            try:
                # Extract old data
                old_id, question, question_type, answer, processing_time, success, created_at = row
                
                # Create new PropertyQuery with enhanced fields
                new_query = PropertyQuery(
                    question=question,
                    question_type=question_type or 'custom',
                    answer=answer,
                    processing_time=processing_time,
                    success=bool(success),
                    created_at=datetime.fromisoformat(created_at) if created_at else datetime.now(),
                    # New fields with intelligent defaults
                    location_detected=detect_location_from_question(question),
                    llm_provider=guess_llm_provider(old_id),  # Simple alternating pattern
                    confidence_score=0.85,  # Default confidence
                    user_id='legacy_user'  # Mark as migrated data
                )
                
                session.add(new_query)
                migrated_count += 1
                
                if migrated_count % 10 == 0:
                    logger.info(f"📈 Migrated {migrated_count}/{len(old_data)} queries...")
                
            except Exception as e:
                logger.error(f"❌ Failed to migrate query {old_id}: {e}")
                continue
        
        # Commit all changes
        session.commit()
        session.close()
        
        logger.info(f"✅ Migration completed successfully!")
        logger.info(f"   📊 Migrated: {migrated_count}/{len(old_data)} queries")
        logger.info(f"   🗃️ New database type: {new_db.get_database_stats().get('database_type', 'Unknown')}")
        
        # Verify migration
        verify_migration(migrated_count)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False

def detect_location_from_question(question: str) -> str:
    """Intelligently detect location from question text"""
    if not question:
        return 'National'
    
    question_lower = question.lower()
    
    if any(word in question_lower for word in ['brisbane', 'queensland', 'qld', 'gold coast', 'sunshine coast']):
        return 'Brisbane'
    elif any(word in question_lower for word in ['sydney', 'nsw', 'new south wales']):
        return 'Sydney'
    elif any(word in question_lower for word in ['melbourne', 'victoria', 'vic']):
        return 'Melbourne'
    elif any(word in question_lower for word in ['perth', 'western australia', 'wa']):
        return 'Perth'
    elif any(word in question_lower for word in ['adelaide', 'south australia', 'sa']):
        return 'Adelaide'
    else:
        return 'National'

def guess_llm_provider(query_id: int) -> str:
    """Simple pattern to assign LLM providers to migrated data"""
    # Alternate between Claude and Gemini for existing data
    return 'claude' if query_id % 2 == 0 else 'gemini'

def verify_migration(expected_count: int):
    """Verify the migration was successful"""
    try:
        new_db = PropertyDatabaseV3()
        stats = new_db.get_database_stats()
        
        actual_count = stats.get('total_queries', 0)
        
        if actual_count >= expected_count:
            logger.info(f"✅ Migration verification passed: {actual_count} queries in new database")
        else:
            logger.warning(f"⚠️ Migration verification warning: Expected {expected_count}, found {actual_count}")
        
        # Show enhanced stats
        logger.info(f"📊 Database Stats After Migration:")
        logger.info(f"   Total Queries: {stats.get('total_queries', 0)}")
        logger.info(f"   Success Rate: {stats.get('success_rate', 0):.1f}%")
        logger.info(f"   Avg Processing Time: {stats.get('avg_processing_time', 0):.2f}s")
        logger.info(f"   Database Type: {stats.get('database_type', 'Unknown')}")
        
        # Show location breakdown
        location_breakdown = stats.get('location_breakdown', {})
        if location_breakdown:
            logger.info(f"   Location Breakdown: {location_breakdown}")
        
    except Exception as e:
        logger.error(f"❌ Migration verification failed: {e}")

def backup_existing_database():
    """Create a backup of the existing database before migration"""
    import shutil
    from datetime import datetime
    
    old_db_path = 'property_intelligence.db'
    backup_path = f'property_intelligence_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    try:
        shutil.copy2(old_db_path, backup_path)
        logger.info(f"✅ Database backup created: {backup_path}")
        return backup_path
    except FileNotFoundError:
        logger.info("📝 No existing database to backup")
        return None
    except Exception as e:
        logger.error(f"❌ Backup failed: {e}")
        return None

if __name__ == "__main__":
    logger.info("🚀 Starting Australian Property Intelligence V3 Migration")
    logger.info("=" * 60)
    
    # Create backup first
    backup_path = backup_existing_database()
    
    # Perform migration
    success = migrate_existing_data()
    
    if success:
        logger.info("=" * 60)
        logger.info("🎉 Migration completed successfully!")
        logger.info("✅ Your V3 database is ready with enhanced features")
        if backup_path:
            logger.info(f"💾 Original database backed up to: {backup_path}")
    else:
        logger.error("=" * 60)
        logger.error("❌ Migration failed - please check the logs")
        if backup_path:
            logger.info(f"💾 Your original database is safe at: {backup_path}")