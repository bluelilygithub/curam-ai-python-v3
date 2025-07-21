import logging
import time
import json
import re # Ensure this is imported

from services.llm_service import LLMService
from services.rss_service import RSSService
from services.web_search_service import WebSearchService
from config import Config # Ensure Config is imported for GOOGLE_CSE_TOP_N_RESULTS, etc.

logger = logging.getLogger(__name__)

class PropertyAnalysisService:
    def __init__(self, llm_service: LLMService, rss_service: RSSService = None, web_search_service: WebSearchService = None):
        self.llm_service = llm_service
        self.rss_service = rss_service
        self.web_search_service = web_search_service
        logger.info(f"PropertyAnalysisService initialized with LLM: {llm_service is not None}, RSS: {rss_service is not None}, WebSearch: {web_search_service is not None}")

    async def analyze_property_question(self, question: str) -> dict:
        """
        Analyzes a property question, potentially using RSS data and web search,
        and generates a comprehensive answer using LLMs.
        """
        final_answer = "An error occurred during analysis."
        success = False
        confidence = 0.85
        question_type = "custom"
        llm_provider = "unknown"
        
        try:
            # 1. Location Detection
            location_info = self._detect_location(question)
            logger.info(f"LOCATION DETECTION FINAL RESULT: {location_info}")

            # 2. Initial Data Gathering: RSS Feeds
            rss_context = ""
            if self.rss_service and self.rss_service.is_available:
                try:
                    articles = await self.rss_service.get_relevant_articles(location_info['scope'])
                    if articles:
                        rss_context = "\n\nRelevant RSS Articles:\n" + "\n".join([
                            f"- Title: {a['title']}\n  Snippet: {a['description'][:200]}...\n  Link: {a['link']}" 
                            for a in articles[:Config.RSS_TOP_N_ARTICLES_FOR_LLM]
                        ])
                        logger.info(f"Retrieved {len(articles)} relevant RSS articles for {location_info['scope']}.")
                    else:
                        logger.info(f"No relevant RSS articles found for {location_info['scope']}.")
                except Exception as e:
                    logger.warning(f"Failed to get RSS data for analysis: {e}. Proceeding without RSS context.")
            else:
                logger.warning("RSS service not available or not configured. Proceeding without RSS context.")

            # 3. LLM's Initial Assessment & Tool/Search Decision
            initial_prompt = self._build_initial_llm_prompt(question, location_info, rss_context)
            logger.info("🤖 Initial LLM prompt sent to determine search necessity.")

            initial_llm_response = await self.llm_service.analyze_with_claude(initial_prompt)
            llm_provider = "claude" 

            if not initial_llm_response['success']:
                raise Exception(initial_llm_response['error'])

            search_results_context = ""
            search_decision = self._check_for_search_necessity(initial_llm_response['answer'])
            
            if search_decision and search_decision.get("action") == "web_search":
                if self.web_search_service and self.web_search_service.is_available:
                    logger.info(f"🌐 LLM determined web search is needed. Performing search for: '{search_decision['query']}'")
                    search_response = await self.web_search_service.search(search_decision['query'])
                    if search_response['success']:
                        search_results_context = "\n\nWeb Search Results:\n" + "\n".join([
                            f"- Title: {item.get('title')}\n  Snippet: {item.get('snippet', '')[:Config.GOOGLE_CSE_SNIPPET_MAX_LENGTH]}...\n  Link: {item.get('link')}"
                            for item in search_response['results'][:Config.GOOGLE_CSE_TOP_N_RESULTS]
                        ])
                        logger.info(f"✅ Web search completed with {len(search_response['results'])} results.")
                    else:
                        logger.warning(f"⚠️ Web search failed: {search_response['error']}. Proceeding without search context.")
                else:
                    logger.warning("⚠️ Web search determined necessary but service is unavailable. Proceeding without search context.")
            elif search_decision and search_decision.get("action") == "analyze_directly":
                logger.info(f"LLM decided to analyze directly based on reason: {search_decision.get('reason', 'N/A')}")
            else:
                logger.warning("LLM search decision could not be parsed or was invalid. Assuming direct analysis.")


            # 4. Final LLM Analysis with All Context
            final_llm_prompt = self._build_final_llm_prompt(question, location_info, rss_context, search_results_context)
            logger.info("🤖 Final LLM prompt sent with all gathered context.")

            if self.llm_service.gemini_is_available:
                llm_response = await self.llm_service.analyze_with_gemini(final_llm_prompt)
                llm_provider = "gemini"
            else:
                llm_response = await self.llm_service.analyze_with_claude(final_llm_prompt)
                llm_provider = "claude"

            if not llm_response['success']:
                raise Exception(llm_response['error'])

            final_answer = llm_response['answer']
            success = True
            confidence = llm_response.get('confidence', 0.90) 

        except Exception as e:
            logger.error(f"Error in property analysis pipeline: {e}")
            final_answer = f"I apologize, but I encountered an error during analysis: {e}. Please try again."
            success = False

        return {
            "success": success,
            "final_answer": final_answer,
            "confidence": confidence,
            "question_type": question_type,
            "llm_provider": llm_provider,
            "claude_result": None, 
            "gemini_result": None
        }

    def _detect_location(self, question: str) -> dict:
        location_mapping = {
            'brisbane': {'scope': 'Brisbane', 'keywords': ['brisbane', 'queensland', 'qld', 'gold coast', 'sunshine coast']},
            'sydney': {'scope': 'Sydney', 'keywords': ['sydney', 'nsw', 'new south wales']},
            'melbourne': {'scope': 'Melbourne', 'keywords': ['melbourne', 'victoria', 'vic']},
            'perth': {'scope': 'Perth', 'keywords': ['perth', 'western australia', 'wa']},
            'adelaide': {'scope': 'Adelaide', 'keywords': ['adelaide', 'south australia', 'sa']},
            'darwin': {'scope': 'Darwin', 'keywords': ['darwin', 'northern territory', 'nt']},
        }
        question_lower = question.lower()
        detected_scope = 'National'
        for loc, data in location_mapping.items():
            if any(keyword in question_lower for keyword in data['keywords']):
                detected_scope = data['scope']
                break
        return {'scope': detected_scope}

    def _build_initial_llm_prompt(self, question: str, location_info: dict, rss_context: str) -> str:
        """
        Builds the initial prompt for the LLM to assess question type and search necessity.
        This prompt guides the LLM to output a structured JSON for tool calling.
        """
        location_scope = location_info.get('scope', 'National')
        
        prompt = f"""You are an expert Australian property market analyst.
Your primary goal is to answer the user's question comprehensively and accurately.
The user's question is about the {location_scope} property market.

User Question: "{question}"

First, assess if this question requires a specific, up-to-date factual number (e.g., an average property price, current rental yield, specific market statistic, population, recent sales volume).
If it does, your **ACTION** must be to perform a `web_search`.
If it does not (e.g., it's a general trend, analysis, comparison, or opinion), your **ACTION** must be `analyze_directly`.

**Context provided for your decision:**
- Location Scope: {location_scope}
- Relevant RSS News/Trends (may contain general trends, but unlikely specific numbers):
{rss_context if rss_context else "No specific relevant RSS articles found to directly answer factual numbers."}

**Your response MUST be a JSON object with an "action" key.**

**If "action" is "web_search":**
- It MUST include a "query" key with a precise search query (e.g., "current median house price Darwin 3 bedroom").
- Example:
```json
{{
    "action": "web_search",
    "query": "median house price Darwin 3 bedroom house"
}}
"""