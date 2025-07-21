import os
import logging

logger = logging.getLogger(__name__)

class Config:
    # --- General Application Settings ---
    APP_NAME = "Australian Property Intelligence API"
    APP_VERSION = "3.0.0"
    
    # --- Database Configuration ---
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'property_intelligence.db')

    # --- API Keys and LLM Settings ---
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    CLAUDE_TEMPERATURE = 0.7
    
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = "gemini-1.5-flash"
    GEMINI_TEMPERATURE = 0.7
    
    GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_CSE_API_KEY')
    GOOGLE_CSE_CX = os.getenv('GOOGLE_CSE_CX')
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
        {"name": "Smart Property Investment", "url": "https://www.smartpropertyinvestment.com.au/rss.xml", "categories": ["investment", "strategy"], "locations": ["national"]},
        {"name": "View.com.au Property News", "url": "https://www.view.com.au/news/rss", "categories": ["market", "trends"], "locations": ["national"]},
    ]
    RSS_TOP_N_ARTICLES_FOR_LLM = 5
    RSS_CACHE_DURATION_HOURS = 1

    # --- Default Questions (Fallback for UI if no history/popular queries) ---
    DEFAULT_EXAMPLE_QUESTIONS = [
        "What are the current property market trends in Brisbane?",
        "How does interest rate change affect property values in Sydney?",
        "Analyze recent infrastructure developments impacting Melbourne property.",
        "What are the investment opportunities in Perth's residential market?"
    ]

    @staticmethod
    def log_config_status():
        """Logs the status of various configurations and API keys for debugging."""
        logger.info("=== Configuration Status ===")
        logger.info(f"Claude Enabled: {'True' if Config.CLAUDE_ENABLED else 'False'}")
        logger.info(f"Claude API Key: {'✓' if Config.CLAUDE_API_KEY else '✗'}")
        logger.info(f"Gemini Enabled: {'True' if Config.GEMINI_ENABLED else 'False'}")
        logger.info(f"Gemini API Key: {'✓' if Config.GEMINI_API_KEY else '✗'}")
        
        logger.info(f"Google CSE Enabled: {'True' if Config.GOOGLE_CSE_ENABLED else 'False'}")
        logger.info(f"Google CSE API Key: {'✓' if Config.GOOGLE_CSE_API_KEY else '✗'}")
        logger.info(f"Google CSE CX (Search Engine ID): {'✓' if Config.GOOGLE_CSE_CX else '✗'}")
        logger.info(f"Google CSE Top N Results: {Config.GOOGLE_CSE_TOP_N_RESULTS}")
        logger.info(f"Google CSE Snippet Max Length: {Config.GOOGLE_CSE_SNIPPET_MAX_LENGTH}")

        logger.info(f"Stability AI Enabled: {'True' if Config.STABILITY_AI_API_KEY else 'False'}")
        logger.info(f"Stability AI API Key: {'✓' if Config.STABILITY_AI_API_KEY else '✗'}")
        
        logger.info(f"Hugging Face Enabled: {'True' if Config.HUGGING_FACE_API_KEY else 'False'}")
        logger.info(f"Hugging Face API Key: {'✓' if Config.HUGGING_FACE_API_KEY else '✗'}")
        
        logger.info(f"MailChannels Enabled: {'True' if Config.MAILCHANNELS_API_KEY else 'False'}")
        logger.info(f"MailChannels API Key: {'✓' if Config.MAILCHANNELS_API_KEY else '✗'}")
        
        logger.info(f"LLM Timeout: {Config.LLM_TIMEOUT}s")
        logger.info(f"Database Path: {Config.DATABASE_PATH}")

        enabled_services_list = []
        if Config.CLAUDE_ENABLED: enabled_services_list.append('claude')
        if Config.GEMINI_ENABLED: enabled_services_list.append('gemini')
        if Config.STABILITY_AI_ENABLED: enabled_services_list.append('stability_ai')
        if Config.HUGGING_FACE_ENABLED: enabled_services_list.append('hugging_face')
        if Config.MAILCHANNELS_ENABLED: enabled_services_list.append('mailchannels')
        if Config.GOOGLE_CSE_ENABLED: enabled_services_list.append('google_cse')

        logger.info(f"All Enabled Services: {enabled_services_list}")
        logger.info("==============================")

    @staticmethod
    def validate_config():
        """
        Performs essential configuration validation checks.
        Logs errors/warnings if critical settings are missing or incorrect.
        """
        logger.info("Running Config.validate_config()...")
        # Check DATABASE_URL for PostgreSQL
        if not Config.DATABASE_URL:
            logger.error("❌ CRITICAL: DATABASE_URL is not set. Database connection will likely fail.")
        else:
            logger.info(f"✅ DATABASE_URL detected.")

        # Check LLM API keys and their enabled status
        if not Config.CLAUDE_API_KEY:
            logger.warning("⚠️ CLAUDE_API_KEY is not set. Claude service will be unavailable.")
        if not Config.GEMINI_API_KEY:
            logger.warning("⚠️ GEMINI_API_KEY is not set. Gemini service will be unavailable.")
        if not (Config.CLAUDE_ENABLED or Config.GEMINI_ENABLED):
            logger.error("❌ CRITICAL: No LLM (Claude or Gemini) is enabled. Property analysis will fail.")

        # Check Google CSE API keys
        if not Config.GOOGLE_CSE_API_KEY or not Config.GOOGLE_CSE_CX:
            logger.warning("⚠️ Google CSE API keys/CX not fully set. Web search service will be unavailable.")
        else:
            logger.info("✅ Google CSE API keys detected.")

        # Check other optional services if desired
        if not Config.STABILITY_AI_API_KEY:
            logger.info("ℹ️ Stability AI API Key not set. Image generation disabled.")
        if not Config.HUGGING_FACE_API_KEY:
            logger.info("ℹ️ Hugging Face API Key not set. HF models disabled.")
        if not Config.MAILCHANNELS_API_KEY:
            logger.info("ℹ️ MailChannels API Key not set. Email service disabled.")

        logger.info("Config validation complete.")