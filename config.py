import os
import logging

logger = logging.getLogger(__name__)

class Config:
    # --- General Application Settings ---
    APP_NAME = "Australian Property Intelligence API"
    APP_VERSION = "3.0.0"
    
    # --- ENHANCED RAILWAY DATABASE CONFIGURATION ---
    # Primary: Railway's automatically provided DATABASE_URL
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Fallback: Individual Railway PostgreSQL variables
    PGHOST = os.getenv('PGHOST')
    PGPORT = os.getenv('PGPORT', '5432')
    PGUSER = os.getenv('PGUSER', 'postgres')
    PGPASSWORD = os.getenv('PGPASSWORD')
    PGDATABASE = os.getenv('PGDATABASE', 'railway')
    
    # Legacy SQLite path (not used in Railway, but kept for compatibility)
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'property_intelligence.db')

    # --- API Keys and LLM Settings ---
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    CLAUDE_TEMPERATURE = 0.7
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = "gemini-1.5-flash"
    GEMINI_TEMPERATURE = 0.7
    
    GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY')
    GOOGLE_CSE_CX = os.getenv('GOOGLE_SEARCH_CX')
    GOOGLE_CSE_TOP_N_RESULTS = 3
    GOOGLE_CSE_SNIPPET_MAX_LENGTH = 300

    STABILITY_AI_API_KEY = os.getenv('STABILITY_AI_API_KEY')
    HUGGING_FACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    MAILCHANNELS_API_KEY = os.getenv('MAILCHANNELS_API_KEY')

    LLM_TIMEOUT = 30 
    
    # --- Flags for service enablement based on API keys presence ---
    CLAUDE_ENABLED = True if os.getenv('CLAUDE_API_KEY') else False
    GEMINI_ENABLED = True if os.getenv('GEMINI_API_KEY') else False
    STABILITY_AI_ENABLED = True if os.getenv('STABILITY_AI_API_KEY') else False
    HUGGING_FACE_ENABLED = True if os.getenv('HUGGINGFACE_API_KEY') else False
    MAILCHANNELS_ENABLED = True if os.getenv('MAILCHANNELS_API_KEY') else False
    GOOGLE_CSE_ENABLED = True if os.getenv('GOOGLE_CSE_API_KEY') and os.getenv('GOOGLE_CSE_CX') else False

    # --- Frontend/CORS Configuration ---
    CORS_ORIGINS = [
        'https://curam-ai.com.au',
        'https://curam-ai.com.au/python-hub/',
        'https://curam-ai.com.au/python-hub-v3/',
        'http://localhost:3000',
        'http://localhost:8000',
        'https://curam-ai-python-v3-production.up.railway.app'
    ]

    # --- RSS Feed Configuration ---
    RSS_FEEDS = [
        {"name": "RealEstate.com.au News", "url": "https://www.realestate.com.au/news/feed/", "categories": ["market", "investment"], "locations": ["national"]},
    #    {"name": "Smart Property Investment", "url": "https://www.smartpropertyinvestment.com.au/rss.xml", "categories": ["investment", "strategy"], "locations": ["national"]},
    #    {"name": "View.com.au Property News", "url": "https://www.view.com.au/news/rss", "categories": ["market", "trends"], "locations": ["national"]},
    ]
    RSS_TOP_N_ARTICLES_FOR_LLM = 5
    RSS_CACHE_DURATION_HOURS = 1

    # --- Default Questions ---
    DEFAULT_EXAMPLE_QUESTIONS = [
        "What are the current property market trends in Brisbane?",
        "How does interest rate change affect property values in Sydney?",
        "Analyze recent infrastructure developments impacting Melbourne property.",
        "What are the investment opportunities in Perth's residential market?"
    ]

    @staticmethod
    def log_config_status():
        """Logs the status of various configurations and API keys for debugging."""
        logger.info("=== 🚀 RAILWAY CONFIGURATION STATUS ===")
        
        # Database Configuration Status
        logger.info("--- DATABASE CONFIGURATION ---")
        logger.info(f"DATABASE_URL: {'✅ Set' if Config.DATABASE_URL else '❌ Missing'}")
        if Config.DATABASE_URL:
            # Log safely without exposing password
            safe_url = Config.DATABASE_URL.split('@')[1] if '@' in Config.DATABASE_URL else "Invalid format"
            logger.info(f"Database Host: ...@{safe_url}")
        
        # Individual Railway PostgreSQL variables
        logger.info(f"PGHOST: {'✅ ' + Config.PGHOST if Config.PGHOST else '❌ Missing'}")
        logger.info(f"PGUSER: {'✅ ' + Config.PGUSER if Config.PGUSER else '❌ Missing'}")
        logger.info(f"PGDATABASE: {'✅ ' + Config.PGDATABASE if Config.PGDATABASE else '❌ Missing'}")
        logger.info(f"PGPORT: {'✅ ' + Config.PGPORT if Config.PGPORT else '❌ Missing'}")
        logger.info(f"PGPASSWORD: {'✅ Set' if Config.PGPASSWORD else '❌ Missing'}")
        
        # Railway environment detection
        railway_env = os.getenv('RAILWAY_ENVIRONMENT', 'unknown')
        railway_project = os.getenv('RAILWAY_PROJECT_NAME', 'unknown')
        logger.info(f"Railway Environment: {railway_env}")
        logger.info(f"Railway Project: {railway_project}")
        
        # LLM Configuration
        logger.info("--- LLM CONFIGURATION ---")
        logger.info(f"Claude Enabled: {'✅ True' if Config.CLAUDE_ENABLED else '❌ False'}")
        logger.info(f"Claude API Key: {'✅ Set' if Config.CLAUDE_API_KEY else '❌ Missing'}")
        logger.info(f"Gemini Enabled: {'✅ True' if Config.GEMINI_ENABLED else '❌ False'}")
        logger.info(f"Gemini API Key: {'✅ Set' if Config.GEMINI_API_KEY else '❌ Missing'}")
        
        # Other Services
        logger.info("--- OTHER SERVICES ---")
        logger.info(f"Google CSE Enabled: {'✅ True' if Config.GOOGLE_CSE_ENABLED else '❌ False'}")
        logger.info(f"Google CSE API Key: {'✅ Set' if Config.GOOGLE_CSE_API_KEY else '❌ Missing'}")
        logger.info(f"Google CSE CX: {'✅ Set' if Config.GOOGLE_CSE_CX else '❌ Missing'}")
        
        logger.info(f"Stability AI Enabled: {'✅ True' if Config.STABILITY_AI_API_KEY else '❌ False'}")
        logger.info(f"Hugging Face Enabled: {'✅ True' if Config.HUGGING_FACE_API_KEY else '❌ False'}")
        logger.info(f"MailChannels Enabled: {'✅ True' if Config.MAILCHANNELS_API_KEY else '❌ False'}")
        
        logger.info(f"LLM Timeout: {Config.LLM_TIMEOUT}s")

        # Summary of enabled services
        enabled_services_list = []
        if Config.CLAUDE_ENABLED: enabled_services_list.append('claude')
        if Config.GEMINI_ENABLED: enabled_services_list.append('gemini')
        if Config.STABILITY_AI_ENABLED: enabled_services_list.append('stability_ai')
        if Config.HUGGING_FACE_ENABLED: enabled_services_list.append('hugging_face')
        if Config.MAILCHANNELS_ENABLED: enabled_services_list.append('mailchannels')
        if Config.GOOGLE_CSE_ENABLED: enabled_services_list.append('google_cse')

        logger.info(f"🚀 All Enabled Services: {enabled_services_list}")
        logger.info("===================================")

    @staticmethod
    def validate_config():
        """
        Performs essential configuration validation for Railway deployment.
        """
        logger.info("🔍 Running Railway Config Validation...")
        
        # === CRITICAL: DATABASE VALIDATION ===
        database_ok = False
        
        # Check primary DATABASE_URL
        if Config.DATABASE_URL:
            logger.info("✅ PRIMARY: DATABASE_URL is set.")
            if 'postgresql://' in Config.DATABASE_URL or 'postgres://' in Config.DATABASE_URL:
                logger.info("✅ DATABASE_URL format appears correct (PostgreSQL).")
                database_ok = True
            else:
                logger.warning(f"⚠️ DATABASE_URL format may be incorrect: {Config.DATABASE_URL[:20]}...")
        else:
            logger.warning("⚠️ PRIMARY: DATABASE_URL is not set.")
            
            # Check fallback: individual Railway variables
            if Config.PGHOST and Config.PGPASSWORD:
                logger.info("✅ FALLBACK: Individual Railway PostgreSQL variables available.")
                database_ok = True
            else:
                logger.error("❌ FALLBACK: Missing critical Railway variables.")
                logger.error(f"PGHOST: {'✓' if Config.PGHOST else '✗'}")
                logger.error(f"PGPASSWORD: {'✓' if Config.PGPASSWORD else '✗'}")
        
        if not database_ok:
            logger.critical("❌ CRITICAL: NO DATABASE CONNECTION POSSIBLE!")
            logger.critical("🔧 RAILWAY FIX REQUIRED:")
            logger.critical("1. Check Railway PostgreSQL service is running")
            logger.critical("2. Verify environment variables in Railway dashboard")
            logger.critical("3. Ensure Flask service is connected to PostgreSQL service")
        else:
            logger.info("✅ DATABASE CONFIGURATION: Ready for connection")

        # === LLM VALIDATION ===
        if not Config.CLAUDE_API_KEY:
            logger.warning("⚠️ CLAUDE_API_KEY is not set. Claude service will be unavailable.")
        if not Config.GEMINI_API_KEY:
            logger.warning("⚠️ GEMINI_API_KEY is not set. Gemini service will be unavailable.")
        if not (Config.CLAUDE_ENABLED or Config.GEMINI_ENABLED):
            logger.error("❌ CRITICAL: No LLM (Claude or Gemini) is enabled. Property analysis will fail.")

        # === OTHER SERVICES ===
        if not Config.GOOGLE_CSE_API_KEY or not Config.GOOGLE_CSE_CX:
            logger.warning("⚠️ Google CSE API keys not set. Web search service unavailable.")
        else:
            logger.info("✅ Google CSE API keys detected.")

        # Railway-specific environment checks
        railway_env = os.getenv('RAILWAY_ENVIRONMENT')
        if railway_env:
            logger.info(f"🚂 Railway Environment Detected: {railway_env}")
        else:
            logger.info("ℹ️ Not running on Railway (or RAILWAY_ENVIRONMENT not set)")

        logger.info("🔍 Config validation complete.")
        return database_ok

    @staticmethod
    def get_database_connection_info():
        """
        Returns database connection information for debugging.
        SAFE: Does not expose passwords.
        """
        info = {
            "has_database_url": bool(Config.DATABASE_URL),
            "has_pghost": bool(Config.PGHOST),
            "has_pgpassword": bool(Config.PGPASSWORD),
            "pguser": Config.PGUSER,
            "pgdatabase": Config.PGDATABASE,
            "pgport": Config.PGPORT,
            "railway_environment": os.getenv('RAILWAY_ENVIRONMENT', 'unknown'),
            "railway_project": os.getenv('RAILWAY_PROJECT_NAME', 'unknown')
        }
        
        if Config.DATABASE_URL:
            # Safely extract host info without password
            try:
                host_part = Config.DATABASE_URL.split('@')[1] if '@' in Config.DATABASE_URL else "unknown"
                info["database_host"] = host_part
            except:
                info["database_host"] = "parsing_error"
        
        return info