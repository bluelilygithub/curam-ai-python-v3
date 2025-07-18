"""
Configuration management for Australian Property Intelligence
Centralized configuration with validation
"""

import os
import logging

logger = logging.getLogger(__name__)

class Config:
    """Centralized configuration management"""
    
    # API Keys
    CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # New API Keys
    STABILITY_API_KEY = os.getenv('STABILITY_API_KEY')
    HUGGING_FACE_API_KEY = os.getenv('HUGGING_FACE_API_KEY')
    MAILCHANNELS_API_KEY = os.getenv('MAILCHANNELS_API_KEY')
    
    # LLM Configuration
    LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', '30'))
    LLM_MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', '3'))
    
    # Claude Models (in priority order)
    CLAUDE_MODELS = [
        'claude-3-5-sonnet-20241022',
        'claude-3-haiku-20240307',
        'claude-3-sonnet-20240229'
    ]
    
    # Gemini Models (in priority order)
    GEMINI_MODELS = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    
    # Feature Flags
    CLAUDE_ENABLED = os.getenv('CLAUDE_ENABLED', 'true').lower() == 'true'
    GEMINI_ENABLED = os.getenv('GEMINI_ENABLED', 'true').lower() == 'true'
    
    # New Service Feature Flags
    STABILITY_ENABLED = os.getenv('STABILITY_ENABLED', 'true').lower() == 'true'
    HUGGING_FACE_ENABLED = os.getenv('HUGGING_FACE_ENABLED', 'true').lower() == 'true'
    MAILCHANNELS_ENABLED = os.getenv('MAILCHANNELS_ENABLED', 'true').lower() == 'true'
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'property_intelligence.db')
    
    # CORS
    CORS_ORIGINS = [
        'https://curam-ai.com.au',
        'https://curam-ai.com.au/python-hub/',
        'https://curam-ai.com.au/python-hub-v2/',
        'https://curam-ai.com.au/ai-intelligence/',
        'http://localhost:3000',
        'http://localhost:8000'
    ]
    
    # Add development origins if in development
    if os.getenv('FLASK_ENV') == 'development':
        CORS_ORIGINS.append('*')
    
    # Australian Property Questions
    PRESET_QUESTIONS = [
    "What are the current trends in the Australian property market?",
    "Which Australian cities are showing the strongest property growth?", 
    "What major infrastructure projects are affecting property values across Australia?",
    "Which suburbs across Australia are trending in property investment?",
    "What regulatory changes are impacting the Australian property market?",
    "What are the latest property development approvals across major Australian cities?",
    "Which Australian property markets offer the best investment opportunities?",
    "What are the emerging property hotspots in Australia?"
    ]
    
    # RSS Data Sources
    AUSTRALIAN_RSS_CONFIG = {
            'cache_duration_hours': 1,
            'max_articles_per_feed': 10,
            'timeout_seconds': 15,
            'national_focus': True
        }
    
    # Stability AI Configuration
    STABILITY_CONFIG = {
        'base_url': 'https://api.stability.ai/v1',
        'models': {
            'chart_generation': 'stable-diffusion-v1-6',
            'infographic': 'stable-diffusion-xl-1024-v1-0'
        },
        'default_params': {
            'steps': 30,
            'width': 1024,
            'height': 1024,
            'cfg_scale': 7.0
        }
    }
    
    # Hugging Face Configuration
    HUGGING_FACE_CONFIG = {
        'models': {
            'sentiment': 'cardiffnlp/twitter-roberta-base-sentiment-latest',
            'classification': 'facebook/bart-large-mnli',
            'summarization': 'facebook/bart-large-cnn'
        },
        'api_url': 'https://api-inference.huggingface.co/models'
    }
    
    # MailChannels Configuration
    MAILCHANNELS_CONFIG = {
        'api_url': 'https://api.mailchannels.net/tx/v1/send',
        'from_email': 'noreply@curam-ai.com.au',
        'from_name': 'Australian Property Intelligence',
        'notification_types': [
            'trend_alerts',
            'weekly_summaries',
            'system_updates'
        ]
    }
    
    @classmethod
    def validate_config(cls):
        """Validate critical configuration"""
        issues = []
        
        # LLM Providers
        if not cls.CLAUDE_API_KEY and cls.CLAUDE_ENABLED:
            issues.append("CLAUDE_API_KEY missing but Claude is enabled")
        
        if not cls.GEMINI_API_KEY and cls.GEMINI_ENABLED:
            issues.append("GEMINI_API_KEY missing but Gemini is enabled")
        
        if not cls.CLAUDE_ENABLED and not cls.GEMINI_ENABLED:
            issues.append("No LLM providers enabled")
        
        # New Services
        if not cls.STABILITY_API_KEY and cls.STABILITY_ENABLED:
            issues.append("STABILITY_API_KEY missing but Stability AI is enabled")
        
        if not cls.HUGGING_FACE_API_KEY and cls.HUGGING_FACE_ENABLED:
            issues.append("HUGGING_FACE_API_KEY missing but Hugging Face is enabled")
        
        if not cls.MAILCHANNELS_API_KEY and cls.MAILCHANNELS_ENABLED:
            issues.append("MAILCHANNELS_API_KEY missing but MailChannels is enabled")
        
        # Timeouts
        if cls.LLM_TIMEOUT < 5:
            issues.append("LLM_TIMEOUT too low (minimum 5 seconds)")
        
        if issues:
            logger.warning(f"Configuration issues: {', '.join(issues)}")
        
        return len(issues) == 0
    
    @classmethod
    def get_enabled_llm_providers(cls):
        """Get list of enabled LLM providers"""
        providers = []
        if cls.CLAUDE_ENABLED and cls.CLAUDE_API_KEY:
            providers.append('claude')
        if cls.GEMINI_ENABLED and cls.GEMINI_API_KEY:
            providers.append('gemini')
        return providers
    
    @classmethod
    def get_enabled_services(cls):
        """Get list of all enabled services"""
        services = []
        
        # LLM Services
        if cls.CLAUDE_ENABLED and cls.CLAUDE_API_KEY:
            services.append('claude')
        if cls.GEMINI_ENABLED and cls.GEMINI_API_KEY:
            services.append('gemini')
        
        # New Services
        if cls.STABILITY_ENABLED and cls.STABILITY_API_KEY:
            services.append('stability_ai')
        if cls.HUGGING_FACE_ENABLED and cls.HUGGING_FACE_API_KEY:
            services.append('hugging_face')
        if cls.MAILCHANNELS_ENABLED and cls.MAILCHANNELS_API_KEY:
            services.append('mailchannels')
        
        return services
    
    @classmethod
    def log_config_status(cls):
        """Log configuration status for debugging"""
        logger.info("=== Configuration Status ===")
        
        # LLM Providers
        logger.info(f"Claude Enabled: {cls.CLAUDE_ENABLED}")
        logger.info(f"Claude API Key: {'✓' if cls.CLAUDE_API_KEY else '✗'}")
        logger.info(f"Gemini Enabled: {cls.GEMINI_ENABLED}")
        logger.info(f"Gemini API Key: {'✓' if cls.GEMINI_API_KEY else '✗'}")
        
        # New Services
        logger.info(f"Stability AI Enabled: {cls.STABILITY_ENABLED}")
        logger.info(f"Stability AI API Key: {'✓' if cls.STABILITY_API_KEY else '✗'}")
        logger.info(f"Hugging Face Enabled: {cls.HUGGING_FACE_ENABLED}")
        logger.info(f"Hugging Face API Key: {'✓' if cls.HUGGING_FACE_API_KEY else '✗'}")
        logger.info(f"MailChannels Enabled: {cls.MAILCHANNELS_ENABLED}")
        logger.info(f"MailChannels API Key: {'✓' if cls.MAILCHANNELS_API_KEY else '✗'}")
        
        # System
        logger.info(f"LLM Timeout: {cls.LLM_TIMEOUT}s")
        logger.info(f"Database Path: {cls.DATABASE_PATH}")
        logger.info(f"All Enabled Services: {cls.get_enabled_services()}")
        logger.info("=" * 30)