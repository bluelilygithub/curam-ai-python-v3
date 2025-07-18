"""
RSS Service for Australian Property Data
Designed to integrate with existing Australian Property Intelligence architecture
"""

import feedparser
import requests
from datetime import datetime
import logging
from typing import List, Dict

class RSSService:
    """Simple RSS service that works with existing architecture"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Australian Property RSS Feeds
        self.feeds = [
            {
                'name': 'RealEstate.com.au',
                'url': 'https://realestate.com.au/news/feed',
                'active': True
            },
            {
                'name': 'Smart Property Investment', 
                'url': 'https://smartpropertyinvestment.com.au/feed',
                'active': True
            },
            {
                'name': 'PropertyMe Blog',
                'url': 'https://propertyme.com.au/blog/feed', 
                'active': True
            },
            {
                'name': 'View.com.au Property News',
                'url': 'https://view.com.au/news/feed',
                'active': True
            }
        ]
        
        self.headers = {
            'User-Agent': 'Australian Property Intelligence API/2.1.0 (+https://curam-ai-python-v2-production.up.railway.app)',
            'Accept': 'application/rss+xml, application/xml, text/xml'
        }
        
        self.logger.info("RSS Service initialized with {} feeds".format(len(self.feeds)))
    
    def get_recent_news(self, max_articles: int = 10) -> List[Dict]:
        """Get recent property news from all feeds"""
        all_articles = []
        
        for feed_config in self.feeds:
            if not feed_config['active']:
                continue
                
            try:
                articles = self._fetch_feed(feed_config)
                all_articles.extend(articles)
                
            except Exception as e:
                self.logger.error(f"Failed to fetch {feed_config['name']}: {e}")
                continue
        
        # Sort by published date (most recent first) and limit results
        all_articles.sort(key=lambda x: x.get('published_timestamp', 0), reverse=True)
        return all_articles[:max_articles]
    
    def get_Australian_news(self, max_articles: int = 5) -> List[Dict]:
        """Get Australian-specific property news"""
        all_news = self.get_recent_news(max_articles * 3)  # Get more to filter
        Australian_news = []
        
        Australian_keywords = [
            'Australian', 'queensland', 'qld', 'gold coast', 'sunshine coast',
            'ipswich', 'logan', 'caboolture', 'toowoomba'
        ]
        
        for article in all_news:
            text = f"{article.get('title', '')} {article.get('summary', '')}".lower()
            if any(keyword in text for keyword in Australian_keywords):
                article['Australian_relevant'] = True
                Australian_news.append(article)
        
        return Australian_news[:max_articles]
    
    def _fetch_feed(self, feed_config: Dict) -> List[Dict]:
        """Fetch a single RSS feed"""
        try:
            response = requests.get(
                feed_config['url'], 
                headers=self.headers, 
                timeout=15,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                self.logger.warning(f"HTTP {response.status_code} for {feed_config['name']}")
                return []
            
            feed = feedparser.parse(response.content)
            
            if feed.bozo:
                self.logger.warning(f"Feed parsing issues for {feed_config['name']}: {feed.bozo_exception}")
            
            articles = []
            
            for entry in feed.entries[:5]:  # Limit to 5 per feed
                # Try to get published timestamp
                published_timestamp = 0
                try:
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        import time
                        published_timestamp = time.mktime(entry.published_parsed)
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        import time
                        published_timestamp = time.mktime(entry.updated_parsed)
                except:
                    pass
                
                # Clean up summary
                summary = getattr(entry, 'summary', '')
                if len(summary) > 300:
                    summary = summary[:300] + "..."
                
                article = {
                    'title': getattr(entry, 'title', 'No title'),
                    'link': getattr(entry, 'link', ''),
                    'summary': summary,
                    'published': getattr(entry, 'published', ''),
                    'published_timestamp': published_timestamp,
                    'source': feed_config['name']
                }
                articles.append(article)
            
            self.logger.info(f"✅ Fetched {len(articles)} articles from {feed_config['name']}")
            return articles
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"❌ Request error for {feed_config['name']}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"❌ Unexpected error for {feed_config['name']}: {e}")
            return []
    
    def get_health_status(self) -> Dict:
        """Get RSS service health status"""
        active_feeds = sum(1 for feed in self.feeds if feed['active'])
        
        return {
            'rss_service': 'operational',
            'total_feeds': len(self.feeds),
            'active_feeds': active_feeds,
            'feeds': [{'name': f['name'], 'active': f['active']} for f in self.feeds]
        }
    
    def test_connection(self) -> Dict:
        """Test RSS connectivity with first 2 feeds"""
        results = {}
        
        test_feeds = self.feeds[:2]  # Test first 2 feeds only
        
        for feed_config in test_feeds:
            try:
                response = requests.get(
                    feed_config['url'], 
                    headers=self.headers, 
                    timeout=10
                )
                
                results[feed_config['name']] = {
                    'status': 'success' if response.status_code == 200 else 'error',
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', 'unknown')
                }
                
            except requests.exceptions.Timeout:
                results[feed_config['name']] = {
                    'status': 'timeout',
                    'error': 'Request timeout'
                }
            except requests.exceptions.RequestException as e:
                results[feed_config['name']] = {
                    'status': 'error',
                    'error': str(e)
                }
            except Exception as e:
                results[feed_config['name']] = {
                    'status': 'error',
                    'error': f"Unexpected error: {str(e)}"
                }
        
        return results
    
    def get_feed_data_for_analysis(self, question: str) -> str:
        """Get formatted RSS data for LLM analysis"""
        try:
            # Determine if Australian-focused question
            Australian_keywords = ['Australian', 'queensland', 'qld']
            is_Australian_focused = any(keyword in question.lower() for keyword in Australian_keywords)
            
            if is_Australian_focused:
                articles = self.get_Australian_news(max_articles=5)
                context_type = "Australian-specific"
            else:
                articles = self.get_recent_news(max_articles=8)
                context_type = "Australian national"
            
            if not articles:
                return self._get_fallback_context()
            
            # Format for LLM
            context = f"""
# Current Australian Property Market Data ({context_type})
Retrieved from live RSS feeds on {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Recent Property News:
"""
            
            for i, article in enumerate(articles, 1):
                context += f"""
### {i}. {article['title']}
- **Source**: {article['source']}
- **Published**: {article['published']}
- **Summary**: {article['summary']}
- **Link**: {article['link']}
"""
                if article.get('Australian_relevant'):
                    context += "- **Australian Relevance**: ✅ Specific to Australian/Queensland\n"
                context += "\n"
            
            context += """
**Analysis Instructions**: This is REAL current Australian property market data from live industry RSS feeds. Provide comprehensive analysis using these actual market conditions and developments.
"""
            
            return context
            
        except Exception as e:
            self.logger.error(f"Failed to get RSS data for analysis: {e}")
            return self._get_fallback_context()
    
    def _get_fallback_context(self) -> str:
        """Fallback context when RSS data is unavailable"""
        return """
# Property Market Analysis Context
Note: Real-time RSS data is temporarily unavailable. Providing analysis based on general Australian property market knowledge.
"""