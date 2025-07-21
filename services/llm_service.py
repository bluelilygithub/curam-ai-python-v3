import logging
import os
import time  # Added this import
import httpx # For making asynchronous HTTP requests
import json # For handling JSON responses
from datetime import datetime # For timestamps and health checks

# Import Anthropic and Google Generative AI libraries
# These imports are here to ensure they are available when LLMService is initialized
from anthropic import Anthropic
import google.generativeai as genai

from config import Config # Import your Config class for API keys and models

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.claude_api_key = Config.CLAUDE_API_KEY
        self.gemini_api_key = Config.GEMINI_API_KEY
        self.llm_timeout = Config.LLM_TIMEOUT

        self.claude_is_available = False
        self.gemini_is_available = False

        self.claude_client = None
        self.gemini_client = None

        self._initialize_claude()
        self._initialize_gemini()

    def _initialize_claude(self):
        """Initializes the Claude client if API key is present."""
        if not self.claude_api_key:
            logger.warning("⚠️ Claude API key not configured. Claude service will be unavailable.")
            return

        try:
            self.claude_client = Anthropic(api_key=self.claude_api_key, timeout=self.llm_timeout)
            
            # Test a small call to ensure it's working
            # Use a more robust test for Claude 3.5 Sonnet
            response = self.claude_client.messages.create(
                model=Config.CLAUDE_MODEL,
                max_tokens=10,
                messages=[{"role": "user", "content": "Hello"}] # Use simple string for basic test
            )
            # Check for actual content, or a successful API response
            if response.content and response.content[0].text:
                self.claude_is_available = True
                self.working_claude_model = Config.CLAUDE_MODEL # Store working model
                logger.info(f"✅ Claude model {Config.CLAUDE_MODEL} working. Client initialized.")
            else:
                raise Exception("Claude test call returned no content.")

        except Exception as e:
            logger.error(f"❌ Claude initialization failed: {e}. Claude service will be unavailable.")
            self.claude_is_available = False

    def _initialize_gemini(self):
        """Initializes the Gemini client if API key is present."""
        if not self.gemini_api_key:
            logger.warning("⚠️ Gemini API key not configured. Gemini service will be unavailable.")
            return

        try:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_client = genai.GenerativeModel(Config.GEMINI_MODEL)
            
            # Test a small call
            response = self.gemini_client.generate_content("Hello", safety_settings={'HARASSMENT': 'BLOCK_NONE'})
            if response.text: # Check for actual text content
                self.gemini_is_available = True
                self.working_gemini_model = Config.GEMINI_MODEL # Store working model
                logger.info(f"✅ Gemini initialized with model: {Config.GEMINI_MODEL}.")
            else:
                raise Exception("Gemini test call returned no text.")

        except Exception as e:
            logger.error(f"❌ Gemini initialization failed: {e}. Gemini service will be unavailable.")
            self.gemini_is_available = False

    async def analyze_with_claude(self, prompt: str) -> dict:
        """Sends a prompt to the Claude LLM for analysis and returns token usage."""
        if not self.claude_is_available:
            return {"success": False, "error": "Claude service not available.", "tokens_used": 0}

        try:
            logger.info("CLAUDE PROMPT BEING SENT.")
            start_time = time.time()
            
            # Use httpx.AsyncClient for asynchronous calls to handle timeout
            response = await httpx.AsyncClient(timeout=self.llm_timeout).post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": self.claude_api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": self.working_claude_model,
                    "max_tokens": Config.MAX_TOKENS_PER_QUESTION, # Use the configured limit
                    "temperature": Config.CLAUDE_TEMPERATURE,
                    "messages": [{"role": "user", "content": prompt}]
                }
            )
            response.raise_for_status() # Raise an exception for HTTP errors
            
            json_response = response.json()
            answer = json_response.get("content", [{}])[0].get("text", "No response content from Claude.")

            # Extract token usage from Claude's response
            usage = json_response.get("usage", {})
            prompt_tokens = usage.get("input_tokens", 0)
            completion_tokens = usage.get("output_tokens", 0)
            total_tokens = prompt_tokens + completion_tokens 

            end_time = time.time()
            logger.info(f"✅ Claude analysis successful in {end_time - start_time:.2f}s. Tokens: {total_tokens}")
            return {
                "success": True, 
                "answer": answer, 
                "llm_provider": "claude", 
                "tokens_used": total_tokens # Return total tokens
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ Claude HTTP error: {e.response.status_code} - {e.response.text}")
            return {"success": False, "error": f"Claude API error: {e.response.status_code} - {e.response.text}", "tokens_used": 0}
        except httpx.RequestError as e:
            logger.error(f"❌ Claude Network error: {e}")
            return {"success": False, "error": f"Claude network error: {e}", "tokens_used": 0}
        except Exception as e:
            logger.error(f"❌ Claude analysis failed: {e}")
            return {"success": False, "error": f"Claude analysis failed: {e}", "tokens_used": 0}

    async def analyze_with_gemini(self, prompt: str) -> dict:
        """Sends a prompt to the Gemini LLM for analysis and returns token usage."""
        if not self.gemini_is_available:
            return {"success": False, "error": "Gemini service not available.", "tokens_used": 0}

        try:
            logger.info("GEMINI PROMPT BEING SENT.")
            start_time = time.time()
            
            response = self.gemini_client.generate_content(
                prompt,
                safety_settings=[
                    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                ],
                generation_config=genai.types.GenerationConfig(max_output_tokens=Config.MAX_TOKENS_PER_QUESTION) # Use the configured limit
            )
            
            answer = response.text
            
            # Extract token usage from Gemini's response
            total_tokens = response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0

            end_time = time.time()
            logger.info(f"✅ Gemini analysis successful in {end_time - start_time:.2f}s. Tokens: {total_tokens}")
            return {
                "success": True, 
                "answer": answer, 
                "llm_provider": "gemini", 
                "tokens_used": total_tokens # Return total tokens
            }

        except Exception as e:
            logger.error(f"❌ Gemini analysis failed: {e}")
            return {"success": False, "error": f"Gemini analysis failed: {e}", "tokens_used": 0}

    def get_health_status(self) -> dict:
        """Returns the health status of the LLM service and its providers."""
        return {
            "name": "LLMService",
            "claude_status": "operational" if self.claude_is_available else "unavailable",
            "gemini_status": "operational" if self.gemini_is_available else "unavailable",
            "details": "Both LLM providers operational" if self.claude_is_available and self.gemini_is_available 
                       else "Some LLM providers unavailable",
            "last_checked": datetime.now().isoformat()
        }