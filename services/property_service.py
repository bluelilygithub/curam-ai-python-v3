# services/property_service.py

import logging
import time
from services.llm_service import LLMService
from services.rss_service import RSSService
from services.web_search_service import WebSearchService # NEW import

logger = logging.getLogger(__name__)

class PropertyAnalysisService:
    def __init__(self, llm_service: LLMService, rss_service: RSSService = None, web_search_service: WebSearchService = None):
        self.llm_service = llm_service
        self.rss_service = rss_service
        self.web_search_service = web_search_service # NEW: Inject web search service
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
            # 1. Location Detection (Existing Logic)
            location_info = self._detect_location(question)
            logger.info(f"LOCATION DETECTION FINAL RESULT: {location_info}")

            # 2. Initial Data Gathering: RSS Feeds (Existing Logic)
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
            # Prompt the LLM to decide if it needs web search and/or to refine the question.
            initial_prompt = self._build_initial_llm_prompt(question, location_info, rss_context)
            logger.info("🤖 Initial LLM prompt sent to determine search necessity.")

            initial_llm_response = await self.llm_service.analyze_with_claude(initial_prompt) # Use Claude for initial decision
            llm_provider = "claude" # Assume Claude for this first step

            if not initial_llm_response['success']:
                raise Exception(initial_llm_response['error'])

            # --- NEW: Check if LLM indicates a need for web search ---
            # This is a simplified decision-making. In a real agent, LLM would output JSON for tool calls.
            # For this demo, we'll look for keywords in the initial LLM response or a specific structured output if possible.
            search_needed = self._check_for_search_necessity(initial_llm_response['answer'])
            search_results_context = ""
            if search_needed and self.web_search_service and self.web_search_service.is_available:
                logger.info(f"🌐 LLM determined web search is needed. Performing search for: '{search_needed['query']}'")
                search_response = await self.web_search_service.search(search_needed['query'])
                if search_response['success']:
                    search_results_context = "\n\nWeb Search Results:\n" + "\n".join([
                        f"- Title: {item['title']}\n  Snippet: {item['snippet']}\n  Link: {item['link']}"
                        for item in search_response['results'][:Config.GOOGLE_CSE_TOP_N_RESULTS] # Limit context tokens
                    ])
                    logger.info(f"✅ Web search completed with {len(search_response['results'])} results.")
                else:
                    logger.warning(f"⚠️ Web search failed: {search_response['error']}. Proceeding without search context.")
            else:
                if search_needed and not (self.web_search_service and self.web_search_service.is_available):
                    logger.warning("⚠️ Web search determined necessary but service is unavailable. Proceeding without search context.")
            # --- END NEW ---

            # 4. Final LLM Analysis with All Context (existing logic, modified prompt)
            # Combine all available context for the final LLM prompt.
            final_llm_prompt = self._build_final_llm_prompt(question, location_info, rss_context, search_results_context)
            logger.info("🤖 Final LLM prompt sent with all gathered context.")

            # Prioritize Gemini for comprehensive report generation, fallback to Claude
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
            confidence = llm_response.get('confidence', 0.90) # Assume higher confidence if all steps successful

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
            "claude_result": None, # You can populate these if you want to expose raw LLM results
            "gemini_result": None
        }

    def _detect_location(self, question: str) -> dict:
        # Existing logic for location detection (can be moved to a separate utility if complex)
        location_mapping = {
            'brisbane': {'scope': 'Brisbane', 'keywords': ['brisbane', 'queensland', 'qld', 'gold coast', 'sunshine coast']},
            'sydney': {'scope': 'Sydney', 'keywords': ['sydney', 'nsw', 'new south wales']},
            'melbourne': {'scope': 'Melbourne', 'keywords': ['melbourne', 'victoria', 'vic']},
            'perth': {'scope': 'Perth', 'keywords': ['perth', 'western australia', 'wa']},
            'adelaide': {'scope': 'Adelaide', 'keywords': ['adelaide', 'south australia', 'sa']},
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
        """
        location_scope = location_info.get('scope', 'National')
        
        # Guide the LLM to identify if it needs a specific factual number, and suggest search.
        prompt = f"""You are an expert Australian property market analyst.
The user has asked the following question about the {location_scope} property market:

User Question: "{question}"

Your task is to first:
1.  **Determine if this question requires a specific, up-to-date factual number (e.g., an average price, current rental yield, specific market statistic).**
2.  If it does, suggest a precise search query that could find this information.
3.  If it does not, proceed with analysis based on general knowledge and provided context.

Context provided:
- Location Scope: {location_scope}
- Relevant RSS News/Trends: {rss_context if rss_context else "No relevant RSS articles found."}

Based on the question and context, please indicate if a web search is required to find a specific number.
If a search is required, respond ONLY with a JSON object like this:
```json
{{
    "action": "web_search",
    "query": "precise search query for the factual number"
}}