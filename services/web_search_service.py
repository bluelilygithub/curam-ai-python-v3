# services/web_search_service.py

import httpx # For making HTTP requests asynchronously or synchronously
import json
import logging
import os

from config import Config # Import your Config for API keys

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.api_key = Config.GOOGLE_CSE_API_KEY
        self.cx = Config.GOOGLE_CSE_CX
        self.base_url = "https://www.googleapis.com/customsearch/v1"
        self.top_n_results = Config.GOOGLE_CSE_TOP_N_RESULTS

        if not self.api_key or not self.cx:
            logger.warning("⚠️ Google Custom Search API keys (GOOGLE_CSE_API_KEY or GOOGLE_CSE_CX) not configured. Web search will be unavailable.")
            self.is_available = False
        else:
            self.is_available = True
            logger.info("✅ WebSearchService initialized.")

    def _build_search_url(self, query: str) -> str:
        """Constructs the URL for the Google Custom Search API."""
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query,
            "num": self.top_n_results # Number of results to fetch
        }
        # httpx.URL handles URL encoding of parameters
        return httpx.URL(self.base_url, params=params)

    async def search(self, query: str) -> dict:
        """
        Performs a web search using the Google Custom Search API.
        Returns a dictionary of search results (simplified for LLM consumption).
        """
        if not self.is_available:
            logger.error("❌ WebSearchService is not available due to missing configuration.")
            return {"error": "Web search not configured."}

        search_url = self._build_search_url(query)
        logger.info(f"🔍 Performing web search for query: '{query}'")

        try:
            async with httpx.AsyncClient(timeout=10) as client: # Use AsyncClient for non-blocking I/O
                response = await client.get(str(search_url))
                response.raise_for_status() # Raise an exception for 4xx or 5xx responses

            search_results = response.json()
            
            # Extract relevant information for the LLM
            formatted_results = []
            if search_results.get('items'):
                for item in search_results['items']:
                    formatted_results.append({
                        "title": item.get('title'),
                        "link": item.get('link'),
                        "snippet": item.get('snippet')
                    })
            
            logger.info(f"✅ Web search for '{query}' successful. Found {len(formatted_results)} relevant items.")
            return {"success": True, "query": query, "results": formatted_results}

        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error during web search for '{query}': {e.response.status_code} - {e.response.text}")
            return {"success": False, "error": f"HTTP error: {e.response.status_code} - {e.response.text}"}
        except httpx.RequestError as e:
            logger.error(f"❌ Network error during web search for '{query}': {e}")
            return {"success": False, "error": f"Network error during search: {e}"}
        except Exception as e:
            logger.error(f"❌ Unexpected error during web search for '{query}': {e}")
            return {"success": False, "error": f"Unexpected search error: {e}"}

    def get_health_status(self) -> dict:
        """Returns the health status of the Web Search Service."""
        return {
            "name": "WebSearchService",
            "status": "operational" if self.is_available else "unavailable",
            "details": "API Key/CX configured" if self.is_available else "API Key/CX missing",
            "last_checked": datetime.now().isoformat()
        }