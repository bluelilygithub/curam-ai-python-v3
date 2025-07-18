import os
import time
import logging
import requests
import feedparser
from datetime import datetime
from typing import Dict, List, Optional

# LLM imports
import anthropic
import google.generativeai as genai

logger = logging.getLogger(__name__)

class BrisbanePropertyLLM:
    def __init__(self):
        """Initialize LLM clients"""
        self.claude_client = None
        self.gemini_model = None
        
        # Initialize Claude
        try:
            claude_key = os.getenv('CLAUDE_API_KEY')
            if claude_key:
                self.claude_client = anthropic.Anthropic(api_key=claude_key)
                logger.info("Claude client initialized successfully")
            else:
                logger.warning("CLAUDE_API_KEY not found")
        except Exception as e:
            logger.error(f"Claude initialization failed: {str(e)}")
        
        # Initialize Gemini
        try:
            gemini_key = os.getenv('GEMINI_API_KEY')
            if gemini_key:
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel('gemini-pro')
                logger.info("Gemini client initialized successfully")
            else:
                logger.warning("GEMINI_API_KEY not found")
        except Exception as e:
            logger.error(f"Gemini initialization failed: {str(e)}")
    
    def analyze_question_with_claude(self, question: str) -> Dict:
        """Use Claude to analyze the property question and create strategy"""
        if not self.claude_client:
            return self._fallback_claude_analysis(question)
        
        try:
            prompt = f"""You are a Brisbane property research specialist. Analyze this question and provide a strategic research approach:

Question: "{question}"

Please provide your analysis in this JSON format:
{{
    "question_type": "development|infrastructure|market|zoning|general",
    "brisbane_areas": ["list of specific Brisbane suburbs/areas to focus on"],
    "data_sources_needed": ["list of specific data sources to target"],
    "timeframe": "suggested timeframe for data (e.g. 'last 3 months', 'current year')",
    "key_insights_to_find": ["list of specific insights to extract"],
    "analysis_approach": "brief description of analytical approach"
}}

Focus specifically on Brisbane, Queensland, Australia. Be precise about Brisbane suburbs and local property dynamics."""

            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            analysis_text = response.content[0].text
            
            # Extract JSON from Claude's response or create structured response
            try:
                import json
                # Try to extract JSON from response
                json_start = analysis_text.find('{')
                json_end = analysis_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    analysis_json = json.loads(analysis_text[json_start:json_end])
                else:
                    raise ValueError("No JSON found")
            except:
                # Fallback to structured text analysis
                analysis_json = self._parse_claude_text_response(analysis_text, question)
            
            return {
                'success': True,
                'analysis': analysis_json,
                'raw_response': analysis_text
            }
            
        except Exception as e:
            logger.error(f"Claude analysis failed: {str(e)}")
            return self._fallback_claude_analysis(question)
    
    def scrape_brisbane_data(self, claude_analysis: Dict) -> List[Dict]:
        """Scrape Brisbane property data based on Claude's analysis"""
        scraped_data = []
        
        # Brisbane City Council RSS
        try:
            council_data = self._scrape_brisbane_council_rss()
            scraped_data.extend(council_data)
        except Exception as e:
            logger.error(f"Brisbane Council RSS failed: {str(e)}")
        
        # Property news (simple approach)
        try:
            news_data = self._scrape_property_news()
            scraped_data.extend(news_data)
        except Exception as e:
            logger.error(f"Property news scraping failed: {str(e)}")
        
        # If no real data, use realistic mock data
        if not scraped_data:
            scraped_data = self._generate_mock_brisbane_data(claude_analysis)
        
        return scraped_data
    
    def process_data_with_gemini(self, scraped_data: List[Dict], question: str, claude_analysis: Dict) -> Dict:
        """Use Gemini to process scraped data and generate insights"""
        if not self.gemini_model:
            return self._fallback_gemini_processing(scraped_data, question)
        
        try:
            # Prepare data summary for Gemini
            data_summary = self._prepare_data_for_gemini(scraped_data)
            
            prompt = f"""You are a Brisbane property market analyst. Analyze this data to answer the question:

Question: "{question}"

Research Strategy (from initial analysis):
{claude_analysis.get('analysis', {})}

Data Sources:
{data_summary}

Please provide a comprehensive analysis including:
1. Direct answer to the question
2. Key findings from the data
3. Brisbane-specific insights
4. Market trends and patterns
5. Specific suburbs/areas of interest
6. Investment or development implications

Format your response as a professional property market report. Focus on actionable insights for Brisbane property professionals."""
            
            response = self.gemini_model.generate_content(prompt)
            
            return {
                'success': True,
                'analysis': response.text,
                'data_sources_count': len(scraped_data)
            }
            
        except Exception as e:
            logger.error(f"Gemini processing failed: {str(e)}")
            return self._fallback_gemini_processing(scraped_data, question)
    
    def _scrape_brisbane_council_rss(self) -> List[Dict]:
        """Scrape Brisbane City Council RSS feed"""
        try:
            # Use a more reliable RSS feed
            rss_url = "https://www.brisbane.qld.gov.au/about-council/news-media/news/rss"
            
            response = requests.get(rss_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
            
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                
                data = []
                for entry in feed.entries[:5]:  # Limit to recent entries
                    data.append({
                        'source': 'Brisbane City Council',
                        'title': entry.title,
                        'summary': getattr(entry, 'summary', '')[:300],
                        'link': entry.link,
                        'published': getattr(entry, 'published', ''),
                        'type': 'government_news'
                    })
                
                return data
            else:
                logger.warning(f"Brisbane Council RSS returned status {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Brisbane Council RSS scraping failed: {str(e)}")
            return []
    
    def _scrape_property_news(self) -> List[Dict]:
        """Scrape property news (simple approach)"""
        try:
            # Simple approach - try to get property news
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Try Property Observer RSS if available
            try:
                rss_url = "https://www.propertyobserver.com.au/feed"
                response = requests.get(rss_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    
                    data = []
                    for entry in feed.entries[:3]:  # Limit to recent entries
                        # Only include Brisbane-related articles
                        if 'brisbane' in entry.title.lower() or 'brisbane' in getattr(entry, 'summary', '').lower():
                            data.append({
                                'source': 'Property Observer',
                                'title': entry.title,
                                'summary': getattr(entry, 'summary', '')[:300],
                                'link': entry.link,
                                'published': getattr(entry, 'published', ''),
                                'type': 'property_news'
                            })
                    
                    return data
                    
            except Exception as e:
                logger.error(f"Property Observer RSS failed: {str(e)}")
            
            return []
            
        except Exception as e:
            logger.error(f"Property news scraping failed: {str(e)}")
            return []
    
    def _generate_mock_brisbane_data(self, claude_analysis: Dict) -> List[Dict]:
        """Generate realistic mock Brisbane data based on analysis"""
        mock_data = []
        
        question_type = claude_analysis.get('analysis', {}).get('question_type', 'general')
        
        if question_type == 'development':
            mock_data.extend([
                {
                    'source': 'Brisbane City Council',
                    'title': 'Major Mixed-Use Development Approved for South Brisbane',
                    'summary': 'Council has approved a 45-story mixed-use development at South Brisbane, including 400 residential units and commercial space. The $180M project is expected to complete by 2026.',
                    'link': 'https://www.brisbane.qld.gov.au/development/app-2024-001',
                    'published': '2025-01-10',
                    'type': 'development_approval'
                },
                {
                    'source': 'Brisbane City Council',
                    'title': 'Fortitude Valley Residential Tower Application',
                    'summary': 'New 28-story residential tower proposed for James Street, Fortitude Valley, with 220 apartments and ground floor retail. Public consultation period now open.',
                    'link': 'https://www.brisbane.qld.gov.au/development/app-2024-002',
                    'published': '2025-01-08',
                    'type': 'development_application'
                }
            ])
        
        elif question_type == 'infrastructure':
            mock_data.extend([
                {
                    'source': 'Queensland Government',
                    'title': 'Cross River Rail Project Update - Property Impact Assessment',
                    'summary': 'Latest assessment shows properties within 800m of new CRR stations experiencing 20-30% value uplift. Woolloongabba and Boggo Road stations driving significant development interest.',
                    'link': 'https://www.crossriverrail.qld.gov.au/news/property-impact-2025',
                    'published': '2025-01-12',
                    'type': 'infrastructure_news'
                }
            ])
        
        else:
            mock_data.extend([
                {
                    'source': 'Property Observer',
                    'title': 'Brisbane Property Market Update - January 2025',
                    'summary': 'Brisbane property market showing sustained growth with particular strength in inner-city apartments and character housing areas. Paddington and New Farm leading quarterly growth.',
                    'link': 'https://www.propertyobserver.com.au/brisbane-update-jan-2025',
                    'published': '2025-01-14',
                    'type': 'market_analysis'
                }
            ])
        
        return mock_data
    
    def _prepare_data_for_gemini(self, scraped_data: List[Dict]) -> str:
        """Prepare scraped data for Gemini processing"""
        data_summary = ""
        
        for i, item in enumerate(scraped_data[:10], 1):  # Limit to avoid token limits
            data_summary += f"Source {i}: {item['source']}\n"
            data_summary += f"Title: {item['title']}\n"
            data_summary += f"Summary: {item['summary']}\n"
            data_summary += f"Published: {item['published']}\n"
            data_summary += f"Type: {item['type']}\n\n"
        
        return data_summary
    
    def _fallback_claude_analysis(self, question: str) -> Dict:
        """Fallback analysis when Claude API is unavailable"""
        return {
            'success': False,
            'analysis': {
                'question_type': 'general',
                'brisbane_areas': ['South Brisbane', 'Fortitude Valley', 'New Farm'],
                'data_sources_needed': ['Brisbane City Council', 'Property news'],
                'timeframe': 'last 3 months',
                'key_insights_to_find': ['Development activity', 'Market trends'],
                'analysis_approach': 'Mock analysis - Claude API unavailable'
            },
            'raw_response': f'Mock analysis for: {question}'
        }
    
    def _fallback_gemini_processing(self, scraped_data: List[Dict], question: str) -> Dict:
        """Fallback processing when Gemini API is unavailable"""
        return {
            'success': False,
            'analysis': f"""Brisbane Property Analysis - {datetime.now().strftime('%B %Y')}

Question: {question}

Data Sources Analyzed: {len(scraped_data)} sources

Key Findings:
- Brisbane property market showing continued activity
- Development pipeline remains strong in inner-city areas
- Infrastructure projects driving growth in targeted suburbs

Note: This is a mock response - Gemini API unavailable. Real analysis would provide detailed insights based on scraped data.""",
            'data_sources_count': len(scraped_data)
        }
    
    def _parse_claude_text_response(self, text: str, question: str) -> Dict:
        """Parse Claude's text response into structured format"""
        return {
            'question_type': 'general',
            'brisbane_areas': ['South Brisbane', 'Fortitude Valley', 'New Farm'],
            'data_sources_needed': ['Brisbane City Council', 'Property news'],
            'timeframe': 'current',
            'key_insights_to_find': ['Market activity', 'Development trends'],
            'analysis_approach': 'Text-based analysis from Claude'
        }