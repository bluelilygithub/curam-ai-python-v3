# services/rss_service.py (Inside your RSSService class)

import logging
import feedparser # Assuming this is used for parsing RSS feeds
import httpx # Assuming this is used for fetching RSS feeds
import time
from datetime import datetime

from config import Config # Import your Config for RSS_FEEDS

logger = logging.getLogger(__name__)

class RSSService:
    def __init__(self):
        self.rss_feeds = Config.RSS_FEEDS
        self.cache = {} # Simple in-memory cache for RSS data
        self.cache_duration_hours = Config.RSS_CACHE_DURATION_HOURS

        # Add is_available flag
        if not self.rss_feeds:
            logger.warning("⚠️ No RSS feeds configured in Config.RSS_FEEDS. RSS service will be unavailable.")
            self.is_available = False
        else:
            self.is_available = True
            logger.info(f"✅ RSS Service initialized with {len(self.rss_feeds)} feeds.")
            # Optional: Test initial fetch here to confirm availability

    async def _fetch_feed(self, url: str) -> list:
        """Fetches and parses a single RSS feed asynchronously."""
        if url in self.cache and (time.time() - self.cache[url]['timestamp']) < self.cache_duration_hours * 3600:
            logger.info(f"Using cached data for RSS feed: {url}")
            return self.cache[url]['data']
        
        logger.info(f"Fetching RSS feed from: {url}")
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get(url)
                response.raise_for_status()
            
            feed = feedparser.parse(response.text)
            parsed_articles = []
            for entry in feed.entries:
                parsed_articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "description": entry.summary if hasattr(entry, 'summary') else entry.title,
                    "published": getattr(entry, 'published', ''),
                    "source_url": url # Keep track of original source
                })
            self.cache[url] = {'data': parsed_articles, 'timestamp': time.time()}
            logger.info(f"Successfully fetched {len(parsed_articles)} articles from {url}.")
            return parsed_articles
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error fetching RSS feed {url}: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            logger.error(f"❌ Network error fetching RSS feed {url}: {e}")
        except Exception as e:
            logger.error(f"❌ Error parsing RSS feed {url}: {e}")
        return []

    async def get_relevant_articles(self, location_scope: str = 'National') -> list:
        """
        Fetches articles from all configured RSS feeds and filters them by relevance
        to location scope and property categories.
        """
        all_articles = []
        for feed_config in self.rss_feeds:
            articles = await self._fetch_feed(feed_config['url'])
            all_articles.extend(articles)
        
        # Simple filtering logic (can be enhanced)
        filtered_articles = []
        for article in all_articles:
            is_relevant_location = False
            if location_scope == 'National':
                is_relevant_location = True # All articles are relevant for national scope
            else:
                # Check if article title or description contains location keywords
                location_keywords = [location_scope.lower()] # Simplified, can use more specific keywords
                if any(keyword in article['title'].lower() or keyword in article['description'].lower() for keyword in location_keywords):
                    is_relevant_location = True
            
            # Check if article is within property categories (can be enhanced with LLM filtering)
            is_relevant_category = False
            property_categories = ["property", "real estate", "housing", "market", "investment", "home"]
            if any(keyword in article['title'].lower() or keyword in article['description'].lower() for keyword in property_categories):
                is_relevant_category = True
            
            if is_relevant_location and is_relevant_category:
                filtered_articles.append(article)
        
        logger.info(f"Filtered down to {len(filtered_articles)} relevant articles for {location_scope}.")
        return filtered_articles

    def get_health_status(self) -> dict:
        """Returns the health status of the RSS Service."""
        return {
            "name": "RSSService",
            "status": "operational" if self.is_available else "unavailable",
            "details": "Feeds configured" if self.is_available else "No feeds configured",
            "last_checked": datetime.now().isoformat()
        }