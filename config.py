import os
import logging

# Set up a logger for the config module
logger = logging.getLogger(__name__)

class Config:
    # --- General Application Settings ---
    APP_NAME = "Australian Property Intelligence API"
    APP_VERSION = "3.0.0"
    
    # --- Database Configuration ---
    # Use environment variable for PostgreSQL, fallback to SQLite for local development
    DATABASE_URL = os.getenv('DATABASE_URL')
    DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'database', 'property_intelligence.db')

    # --- API Keys and LLM Settings ---
    # Claude API Key
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
    CLAUDE_TEMPERATURE = 0.7
    
    # Gemini API Key
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = "gemini-1.5-flash"
    GEMINI_TEMPERATURE = 0.7
    
    # Google Custom Search API Configuration for Web Search Tool
    GOOGLE_CSE_API_KEY = os.getenv('GOOGLE_SEARCH_API_KEY') # Your API Key from Google Cloud
    GOOGLE_CSE_CX = os.getenv('GOOGLE_SEARCH_CX')           # Your Custom Search Engine ID (cx)
    GOOGLE_CSE_TOP_N_RESULTS = 3                         # Number of top search results to return
    GOOGLE_CSE_SNIPPET_MAX_LENGTH = 300                  # Max length of snippet to send to LLM (for context window management)

    # Stability AI (for image generation, if implemented in future phases)
    STABILITY_AI_API_KEY = os.getenv('STABILITY_AI_API_KEY')
    
    # Hugging Face (for advanced NLP/ML models, if implemented)
    HUGGING_FACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY') # Note: env var name matches Hugging Face convention

    # MailChannels (for email functionality, if implemented)
    MAILCHANNELS_API_KEY = os.getenv('MAILCHANNELS_API_KEY')

    # General LLM Timeout (in seconds)
    LLM_TIMEOUT = 30 
    
    # --- Frontend/CORS Configuration ---
    CORS_ORIGINS = [
        'https://curam-ai.com.au',                 # Main frontend domain
        'https://curam-ai.com.au/python-hub/',     # Specific frontend path if used
        'https://curam-ai.com.au/python-hub-v3/',  # Specific frontend path for V3
        'http://localhost:3000',                   # Common React/frontend dev server
        'http://localhost:8000',                   # Common Python dev server
        # Add your Railway backend URL here if the frontend might call it directly (unlikely if served from same origin)
        'https://curam-ai-python-v3-production.up.railway.app' # Allow self-access for health checks/internal
    ]

    # --- RSS Feed Configuration ---
    RSS_FEEDS = [
        # Real Estate News & Market Updates
        {"name": "RealEstate.com.au News", "url": "https://www.realestate.com.au/news/feed/", "categories": ["market", "investment"], "locations": ["national"]},
        {"name": "Smart Property Investment", "url": "https://www.smartpropertyinvestment.com.au/rss.xml", "categories": ["investment", "strategy"], "locations": ["national"]},
        {"name": "View.com.au Property News", "url": "https://www.view.com.au/news/rss", "categories": ["market", "trends"], "locations": ["national"]},
        # Add more specific Australian property feeds as needed
        # {"name": "REIQ News (QLD)", "url": "https://www.reiq.com/feed/", "categories": ["market", "qld"], "locations": ["brisbane", "queensland"]}
    ]
    RSS_TOP_N_ARTICLES_FOR_LLM = 5 # Max articles to send to LLM for context
    RSS_CACHE_DURATION_HOURS = 1 # Cache RSS feed data to avoid frequent external calls

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
        logger.info(f"Claude Enabled: {'True' if Config.CLAUDE_API_KEY else 'False'}")
        logger.info(f"Claude API Key: {'✓' if Config.CLAUDE_API_KEY else '✗'}")
        logger.info(f"Gemini Enabled: {'True' if Config.GEMINI_API_KEY else 'False'}")
        logger.info(f"Gemini API Key: {'✓' if Config.GEMINI_API_KEY else '✗'}")
        
        logger.info(f"Google CSE Enabled: {'True' if Config.GOOGLE_CSE_API_KEY and Config.GOOGLE_CSE_CX else 'False'}")
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
        if Config.CLAUDE_API_KEY: enabled_services_list.append('claude')
        if Config.GEMINI_API_KEY: enabled_services_list.append('gemini')
        if Config.STABILITY_AI_API_KEY: enabled_services_list.append('stability_ai')
        if Config.HUGGING_FACE_API_KEY: enabled_services_list.append('hugging_face')
        if Config.MAILCHANNELS_API_KEY: enabled_services_list.append('mailchannels')
        if Config.GOOGLE_CSE_API_KEY and Config.GOOGLE_CSE_CX: enabled_services_list.append('google_cse')

        logger.info(f"All Enabled Services: {enabled_services_list}")
        logger.info("==============================")