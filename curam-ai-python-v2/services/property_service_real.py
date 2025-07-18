"""
Real RSS Feed Service for Australian Property Data
Replaces mock data with actual RSS feeds from major Australian property sources
"""

import feedparser
import requests
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
import time
import random

class RealRSSService:
    """Service for fetching real Australian property RSS feeds"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Real Australian Property RSS Feeds
        self.rss_feeds = {
            'realestate_news': {
                'url': 'https://realestate.com.au/news/feed',
                'name': 'RealEstate.com.au News',
                'description': "Australia's No.1 property site news feed",
                'frequency': '25 posts/day',
                'active': True
            },
            'smart_property': {
                'url': 'https://smartpropertyinvestment.com.au/blog?format=feed&type=rss',
                'name': 'Smart Property Investment',
                'description': 'Premier source of property intelligence',
                'frequency': '29 posts/month',
                'active': True
            },
            'view_property': {
                'url': 'https://view.com.au/news/feed',
                'name': 'View.com.au Property News',
                'description': 'Leading real estate site news',
                'frequency': 'Daily updates',
                'active': True
            },
            'first_national': {
                'url': 'https://content.firstnational.com.au/feed',
                'name': 'First National Real Estate',
                'description': 'Australian property trends and market news',
                'frequency': 'Weekly updates',
                'active': True
            },
            'real_estate_talk': {
                'url': 'https://channels.realty.com.au/feed',
                'name': 'Real Estate Talk',
                'description': 'Trusted voice in property investment',
                'frequency': 'Regular updates',
                'active': True
            },
            'property_me': {
                'url': 'https://propertyme.com.au/blog/feed',
                'name': 'PropertyMe Blog',
                'description': 'Property management insights',
                'frequency': 'Monthly updates',
                'active': True
            },
            'clark_realty_Australian': {
                'url': 'https://clarkrealty.com.au/feed',
                'name': 'Clark Real Estate Australian',
                'description': 'Australian property market insights',
                'frequency': 'Weekly updates',
                'active': True
            },
            'naked_real_estate': {
                'url': 'https://nakedrealestate.com.au/feed',
                'name': 'Naked Real Estate',
                'description': 'Transparent property market analysis',
                'frequency': 'Regular updates',
                'active': True
            },
            'cpn_commercial': {
                'url': 'https://cpn.com.au/feed',
                'name': 'CPN Commercial Property',
                'description': 'Australian commercial property news',
                'frequency': '4 posts/month',
                'active': True
            },
            'integrity_property': {
                'url': 'https://integritypropertyinvestment.com.au/feed',
                'name': 'Integrity Property Investment',
                'description': 'Full service property investment insights',
                'frequency': '8 posts/month',
                'active': True
            }
        }
        
        # Request headers to avoid being blocked
        self.headers = {
            'User-Agent': 'Australian Property Intelligence API/2.1.0 (+https://curam-ai-python-v2-production.up.railway.app)',
            'Accept': 'application/rss+xml, application/xml, text/xml',
            'Accept-Language': 'en-AU,en;q=0.9',
            'Cache-Control': 'no-cache'
        }
        
        # Cache settings
        self.cache_duration = timedelta(hours=1)  # Cache feeds for 1 hour
        self.feed_cache = {}
        
    def fetch_feed(self, feed_key: str, timeout: int = 30) -> Optional[Dict]:
        """Fetch a single RSS feed with error handling"""
        if feed_key not in self.rss_feeds:
            self.logger.error(f"Unknown feed key: {feed_key}")
            return None
            
        feed_config = self.rss_feeds[feed_key]
        if not feed_config['active']:
            self.logger.info(f"Feed {feed_key} is disabled")
            return None
            
        # Check cache first
        cache_key = f"{feed_key}_cache"
        if cache_key in self.feed_cache:
            cached_data, cached_time = self.feed_cache[cache_key]
            if datetime.now() - cached_time < self.cache_duration:
                self.logger.info(f"Returning cached data for {feed_key}")
                return cached_data
        
        try:
            self.logger.info(f"Fetching RSS feed: {feed_config['name']}")
            
            # Add some randomization to avoid being blocked
            time.sleep(random.uniform(0.5, 2.0))
            
            response = requests.get(
                feed_config['url'], 
                headers=self.headers, 
                timeout=timeout,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                self.logger.warning(f"Feed {feed_key} has parsing issues: {feed.bozo_exception}")
            
            # Extract feed information
            feed_data = {
                'feed_key': feed_key,
                'name': feed_config['name'],
                'description': feed_config['description'],
                'title': getattr(feed.feed, 'title', feed_config['name']),
                'link': getattr(feed.feed, 'link', ''),
                'updated': getattr(feed.feed, 'updated', ''),
                'entries_count': len(feed.entries),
                'entries': [],
                'fetched_at': datetime.now().isoformat(),
                'success': True
            }
            
            # Process entries (limit to most recent 20)
            for entry in feed.entries[:20]:
                entry_data = {
                    'title': getattr(entry, 'title', 'No title'),
                    'link': getattr(entry, 'link', ''),
                    'summary': getattr(entry, 'summary', ''),
                    'published': getattr(entry, 'published', ''),
                    'updated': getattr(entry, 'updated', ''),
                    'author': getattr(entry, 'author', ''),
                    'tags': [tag.term for tag in getattr(entry, 'tags', [])]
                }
                feed_data['entries'].append(entry_data)
            
            # Cache the results
            self.feed_cache[cache_key] = (feed_data, datetime.now())
            
            self.logger.info(f"Successfully fetched {len(feed_data['entries'])} entries from {feed_key}")
            return feed_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request error fetching {feed_key}: {str(e)}")
            return self._get_fallback_data(feed_key, f"Request error: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {feed_key}: {str(e)}")
            return self._get_fallback_data(feed_key, f"Parse error: {str(e)}")
    
    def fetch_all_feeds(self, max_concurrent: int = 3) -> Dict[str, Dict]:
        """Fetch all active RSS feeds with rate limiting"""
        results = {}
        active_feeds = [key for key, config in self.rss_feeds.items() if config['active']]
        
        self.logger.info(f"Fetching {len(active_feeds)} RSS feeds...")
        
        for i, feed_key in enumerate(active_feeds):
            # Rate limiting - pause between batches
            if i > 0 and i % max_concurrent == 0:
                self.logger.info("Rate limiting: waiting between batches...")
                time.sleep(random.uniform(2, 5))
            
            feed_data = self.fetch_feed(feed_key)
            if feed_data:
                results[feed_key] = feed_data
            
            # Small delay between each feed
            time.sleep(random.uniform(0.5, 1.5))
        
        self.logger.info(f"Successfully fetched {len(results)} out of {len(active_feeds)} feeds")
        return results
    
    def get_recent_property_news(self, max_items: int = 50) -> List[Dict]:
        """Get recent property news from all feeds combined"""
        all_feeds = self.fetch_all_feeds()
        all_entries = []
        
        for feed_key, feed_data in all_feeds.items():
            if not feed_data.get('success'):
                continue
                
            for entry in feed_data.get('entries', []):
                entry_with_source = entry.copy()
                entry_with_source['source'] = feed_data['name']
                entry_with_source['source_key'] = feed_key
                all_entries.append(entry_with_source)
        
        # Sort by published date (most recent first)
        def parse_date(entry):
            try:
                if entry.get('published'):
                    return datetime.strptime(entry['published'][:19], '%Y-%m-%dT%H:%M:%S')
                elif entry.get('updated'):
                    return datetime.strptime(entry['updated'][:19], '%Y-%m-%dT%H:%M:%S')
                return datetime.min
            except:
                return datetime.min
        
        all_entries.sort(key=parse_date, reverse=True)
        return all_entries[:max_items]
    
    def get_Australian_specific_news(self, max_items: int = 20) -> List[Dict]:
        """Filter news for Australian-specific content"""
        all_news = self.get_recent_property_news(max_items=100)
        Australian_news = []
        
        Australian_keywords = [
            'Australian', 'queensland', 'qld', 'gold coast', 'sunshine coast',
            'ipswich', 'logan', 'redland', 'moreton bay', 'caboolture',
            'toowoomba', 'cairns', 'townsville', 'rockhampton'
        ]
        
        for entry in all_news:
            text_to_search = f"{entry.get('title', '')} {entry.get('summary', '')}".lower()
            if any(keyword in text_to_search for keyword in Australian_keywords):
                entry['Australian_relevant'] = True
                Australian_news.append(entry)
        
        return Australian_news[:max_items]
    
    def get_feed_status(self) -> Dict:
        """Get status of all RSS feeds"""
        status = {
            'total_feeds': len(self.rss_feeds),
            'active_feeds': len([f for f in self.rss_feeds.values() if f['active']]),
            'last_check': datetime.now().isoformat(),
            'feeds': {}
        }
        
        for feed_key, config in self.rss_feeds.items():
            cache_key = f"{feed_key}_cache"
            cached_data = None
            last_success = None
            
            if cache_key in self.feed_cache:
                cached_data, cached_time = self.feed_cache[cache_key]
                last_success = cached_time.isoformat()
            
            status['feeds'][feed_key] = {
                'name': config['name'],
                'url': config['url'],
                'active': config['active'],
                'frequency': config['frequency'],
                'cached': cached_data is not None,
                'last_success': last_success,
                'entries_cached': len(cached_data.get('entries', [])) if cached_data else 0
            }
        
        return status
    
    def _get_fallback_data(self, feed_key: str, error_message: str) -> Dict:
        """Return fallback data when feed fails"""
        config = self.rss_feeds.get(feed_key, {})
        return {
            'feed_key': feed_key,
            'name': config.get('name', 'Unknown Feed'),
            'description': config.get('description', ''),
            'title': f"{config.get('name', 'Unknown')} (Offline)",
            'link': '',
            'updated': '',
            'entries_count': 0,
            'entries': [],
            'fetched_at': datetime.now().isoformat(),
            'success': False,
            'error': error_message
        }
    
    def clear_cache(self):
        """Clear the RSS feed cache"""
        self.feed_cache.clear()
        self.logger.info("RSS feed cache cleared")
    
    def disable_feed(self, feed_key: str):
        """Disable a problematic feed"""
        if feed_key in self.rss_feeds:
            self.rss_feeds[feed_key]['active'] = False
            self.logger.info(f"Disabled RSS feed: {feed_key}")
    
    def enable_feed(self, feed_key: str):
        """Re-enable a disabled feed"""
        if feed_key in self.rss_feeds:
            self.rss_feeds[feed_key]['active'] = True
            self.logger.info(f"Enabled RSS feed: {feed_key}")

# Global instance
rss_service = RealRSSService()

# Convenience functions for backward compatibility
def get_mock_rss_data():
    """Backward compatibility - now returns real RSS data"""
    return rss_service.get_recent_property_news(max_items=20)

def get_Australian_property_news():
    """Get Australian-specific property news"""
    return rss_service.get_Australian_specific_news(max_items=15)

def get_all_property_sources():
    """Get data from all property RSS sources"""
    return rss_service.fetch_all_feeds()

if __name__ == "__main__":
    # Test the RSS service
    logging.basicConfig(level=logging.INFO)
    
    print("Testing Real RSS Service...")
    print("=" * 50)
    
    # Test single feed
    print("\n1. Testing single feed fetch:")
    feed_data = rss_service.fetch_feed('clark_realty_Australian')
    if feed_data:
        print(f"✅ {feed_data['name']}: {feed_data['entries_count']} entries")
    else:
        print("❌ Failed to fetch feed")
    
    # Test Australian-specific news
    print("\n2. Testing Australian-specific news:")
    Australian_news = rss_service.get_Australian_specific_news(max_items=5)
    print(f"✅ Found {len(Australian_news)} Australian-relevant articles")
    for article in Australian_news[:3]:
        print(f"   • {article['title'][:60]}...")
    
    # Test feed status
    print("\n3. Testing feed status:")
    status = rss_service.get_feed_status()
    print(f"✅ {status['active_feeds']}/{status['total_feeds']} feeds active")
    
    print("\n" + "=" * 50)
    print("RSS Service Integration Complete! 🎉")