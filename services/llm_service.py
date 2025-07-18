"""
Professional LLM Service
Handles Claude and Gemini integration with proper error handling
UPDATED: Location info passed as parameter (not detected from question)
"""

import os
import logging
import time
from typing import Dict, Optional
from config import Config

logger = logging.getLogger(__name__)

class LLMService:
    """Professional LLM service with multiple providers and location intelligence"""
    
    def __init__(self):
        self.claude_client = None
        self.gemini_model = None
        self.working_claude_model = None
        self.working_gemini_model = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize LLM clients with proper error handling"""
        if Config.CLAUDE_ENABLED:
            self._init_claude()
        
        if Config.GEMINI_ENABLED:
            self._init_gemini()
    
    def _init_claude(self):
        """Initialize Claude client with working configuration"""
        try:
            if not Config.CLAUDE_API_KEY:
                logger.warning("Claude API key not configured")
                return
            
            import anthropic
            
            # Use the exact same configuration that worked in debug
            self.claude_client = anthropic.Anthropic(
                api_key=Config.CLAUDE_API_KEY.strip(),
                base_url="https://api.anthropic.com"
            )
            
            # Test connection with working models
            self._test_claude_connection()
            logger.info(f"Claude client initialized with model: {self.working_claude_model}")
            
        except Exception as e:
            logger.error(f"Claude initialization failed: {e}")
            self.claude_client = None
    
    def _init_gemini(self):
        """Initialize Gemini client with working models"""
        try:
            if not Config.GEMINI_API_KEY:
                logger.warning("Gemini API key not configured")
                return
            
            import google.generativeai as genai
            genai.configure(api_key=Config.GEMINI_API_KEY.strip())
            
            # Test with models in priority order
            for model_name in Config.GEMINI_MODELS:
                try:
                    self.gemini_model = genai.GenerativeModel(model_name)
                    self._test_gemini_connection()
                    self.working_gemini_model = model_name
                    logger.info(f"Gemini initialized with model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Gemini model {model_name} failed: {e}")
                    continue
            
            if not self.working_gemini_model:
                logger.error("No working Gemini models found")
                self.gemini_model = None
            
        except ImportError:
            logger.error("google-generativeai library not installed")
            self.gemini_model = None
        except Exception as e:
            logger.error(f"Gemini initialization failed: {e}")
            self.gemini_model = None
    
    def _test_claude_connection(self):
        """Test Claude connection with working model"""
        for model in Config.CLAUDE_MODELS:
            try:
                response = self.claude_client.messages.create(
                    model=model,
                    max_tokens=5,
                    messages=[{"role": "user", "content": "Hi"}]
                )
                self.working_claude_model = model
                logger.info(f"Claude model {model} working")
                return True
            except Exception as e:
                logger.warning(f"Claude model {model} test failed: {e}")
                continue
        
        raise Exception("No working Claude models found")
    
    def _test_gemini_connection(self):
        """Test Gemini connection with minimal call"""
        response = self.gemini_model.generate_content("hi")
        return True
    
    def analyze_with_claude_location(self, enhanced_question: str, location_info: Dict) -> Dict:
        """Analyze question with Claude using provided location info"""
        if not self.claude_client:
            return self._error_response("Claude client not available")
        
        try:
            prompt = self._create_strategic_prompt_with_location(enhanced_question, location_info)
            
            # ADD DEBUG LOGGING
            logger.info(f"CLAUDE PROMPT BEING SENT: {prompt}")
            
            model = self.working_claude_model or Config.CLAUDE_MODELS[0]
            
            start_time = time.time()
            response = self.claude_client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'analysis': response.content[0].text,
                'model_used': model,
                'processing_time': processing_time,
                'provider': 'claude'
            }
            
        except Exception as e:
            logger.error(f"Claude analysis failed: {e}")
            return self._error_response(f"Claude analysis failed: {str(e)}")
    
    def analyze_with_gemini_location(self, enhanced_question: str, claude_context: str, location_info: Dict) -> Dict:
        """Analyze question with Gemini using provided location info"""
        if not self.gemini_model:
            return self._error_response("Gemini model not available")
        
        try:
            prompt = self._create_comprehensive_prompt_with_location(enhanced_question, claude_context, location_info)
            
            # ADD DEBUG LOGGING
            logger.info(f"GEMINI PROMPT BEING SENT: {prompt}")
            
            model = self.working_gemini_model or Config.GEMINI_MODELS[0]
            
            start_time = time.time()
            response = self.gemini_model.generate_content(prompt)
            processing_time = time.time() - start_time
            
            return {
                'success': True,
                'analysis': response.text,
                'model_used': model,
                'processing_time': processing_time,
                'provider': 'gemini'
            }
            
        except Exception as e:
            logger.error(f"Gemini analysis failed: {e}")
            return self._error_response(f"Gemini analysis failed: {str(e)}")
    
    def _create_strategic_prompt_with_location(self, enhanced_question: str, location_info: Dict) -> str:
        """Create location-aware strategic prompt for Claude using provided location info"""
        
        if location_info['scope'] == 'national':
            return f"""You are an Australian property research specialist with expertise across all major Australian markets. Analyze this question and provide strategic insights:

{enhanced_question}

Please provide:
1. What type of property question this is (development, market, infrastructure, regulatory, etc.)
2. Which Australian cities/regions are most relevant (Sydney, Melbourne, Brisbane, Perth, Adelaide)
3. What data sources and market indicators would help answer this question
4. Key insights to look for across Australian property markets
5. How different markets might show varying trends or responses

Keep your response strategic and focused on Australian property markets nationally, highlighting regional variations where relevant."""
        
        else:
            return f"""You are an Australian property research specialist with deep expertise in {location_info['focus']} within the broader Australian market context. Analyze this question:

{enhanced_question}

Please provide:
1. What type of property question this is (development, market, infrastructure, regulatory, etc.)
2. Which specific areas within {location_info['focus']} are most relevant
3. How this relates to broader Australian property market trends
4. What data sources would help answer this question
5. Key insights to look for in the local and national context

Keep your response strategic and focused on {location_info['focus']} while considering Australian market dynamics."""
    
    def _create_comprehensive_prompt_with_location(self, enhanced_question: str, claude_context: str, location_info: Dict) -> str:
        """Create location-aware comprehensive prompt for Gemini using provided location info"""
        
        if location_info['scope'] == 'national':
            base_prompt = f"""You are an Australian property market analyst with comprehensive knowledge of all major Australian property markets. Provide a detailed analysis of this question:

{enhanced_question}

Please provide a comprehensive Australian property market analysis that:
- Covers major Australian cities (Sydney, Melbourne, Brisbane, Perth, Adelaide) as relevant
- Discusses current national market trends and regional variations
- Includes investment and development implications across different markets
- Provides professional insights for Australian property industry professionals
- References current market conditions and data where applicable

Focus on delivering actionable information for Australian property professionals with national market perspective."""
        
        else:
            base_prompt = f"""You are an Australian property market analyst with specialized knowledge of {location_info['focus']} and its position within the Australian property market. Provide a comprehensive analysis:

{enhanced_question}

Please provide a detailed {location_info['focus']} property market analysis that:
- Focuses specifically on {location_info['focus']} areas and suburbs
- Connects local trends to broader Australian market dynamics
- Includes investment and development implications for this region
- Provides professional insights for property professionals in this market
- References current market conditions and local data where applicable

Focus on delivering actionable information for property professionals working in {location_info['focus']}."""
        
        if claude_context:
            return f"""{base_prompt}

Strategic Research Context: {claude_context}

Build upon this strategic context to provide your comprehensive analysis."""
        
        return base_prompt
    
    # KEEP OLD METHODS FOR BACKWARD COMPATIBILITY
    def analyze_with_claude(self, question: str) -> Dict:
        """Legacy method - detects location from question"""
        location_info = self._detect_location_scope_legacy(question)
        return self.analyze_with_claude_location(question, location_info)
    
    def analyze_with_gemini(self, question: str, claude_context: str = "") -> Dict:
        """Legacy method - detects location from question"""
        location_info = self._detect_location_scope_legacy(question)
        return self.analyze_with_gemini_location(question, claude_context, location_info)
    
    def _detect_location_scope_legacy(self, question: str) -> Dict:
        """Legacy location detection for backward compatibility"""
        question_lower = question.lower()
        
        # Brisbane/Queensland specific keywords
        brisbane_keywords = ['brisbane', 'queensland', 'qld', 'gold coast', 'sunshine coast']
        
        # Other major Australian cities
        sydney_keywords = ['sydney', 'nsw', 'new south wales']
        melbourne_keywords = ['melbourne', 'victoria', 'vic']
        perth_keywords = ['perth', 'western australia', 'wa']
        adelaide_keywords = ['adelaide', 'south australia', 'sa']
        
        # Check for specific locations
        if any(keyword in question_lower for keyword in brisbane_keywords):
            return {'scope': 'brisbane', 'focus': 'Brisbane and Queensland'}
        elif any(keyword in question_lower for keyword in sydney_keywords):
            return {'scope': 'sydney', 'focus': 'Sydney and New South Wales'}
        elif any(keyword in question_lower for keyword in melbourne_keywords):
            return {'scope': 'melbourne', 'focus': 'Melbourne and Victoria'}
        elif any(keyword in question_lower for keyword in perth_keywords):
            return {'scope': 'perth', 'focus': 'Perth and Western Australia'}
        elif any(keyword in question_lower for keyword in adelaide_keywords):
            return {'scope': 'adelaide', 'focus': 'Adelaide and South Australia'}
        else:
            return {'scope': 'national', 'focus': 'Australian national property market'}
    
    def _error_response(self, error_msg: str) -> Dict:
        """Standardized error response"""
        return {
            'success': False,
            'analysis': None,
            'error': error_msg,
            'processing_time': 0
        }
    
    def get_health_status(self) -> Dict:
        """Get health status of all LLM services"""
        return {
            'claude': {
                'available': self.claude_client is not None,
                'enabled': Config.CLAUDE_ENABLED,
                'working_model': self.working_claude_model,
                'api_key_configured': bool(Config.CLAUDE_API_KEY)
            },
            'gemini': {
                'available': self.gemini_model is not None,
                'enabled': Config.GEMINI_ENABLED,
                'working_model': self.working_gemini_model,
                'api_key_configured': bool(Config.GEMINI_API_KEY)
            }
        }
    
    def get_available_providers(self) -> list:
        """Get list of currently available LLM providers"""
        providers = []
        if self.claude_client:
            providers.append('claude')
        if self.gemini_model:
            providers.append('gemini')
        return providers