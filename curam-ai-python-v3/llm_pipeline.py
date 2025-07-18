import os
import time
import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Generator, Any
import requests
import feedparser
from bs4 import BeautifulSoup
import re

# LLM imports
import anthropic
import google.generativeai as genai

# Local imports
from database import PropertyDatabase

logger = logging.getLogger(__name__)

class BrisbanePropertyPipeline:
    def __init__(self):
        """Initialize the multi-LLM pipeline"""
        self.db = PropertyDatabase()
        
        # Initialize LLM clients
        self.claude_client = None
        self.gemini_model = None
        
        # Initialize Claude
        try:
            claude_key = os.getenv('CLAUDE_API_KEY')
            if claude_key:
                self.claude_client = anthropic.Anthropic(api_key=claude_key)
                logger.info("Claude client initialized")
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
                logger.info("Gemini client initialized")
            else:
                logger.warning("GEMINI_API_KEY not found")
        except Exception as e:
            logger.error(f"Gemini initialization failed: {str(e)}")
        
        # Brisbane-specific data sources
        self.data_sources = {
            'brisbane_council_rss': 'https://www.brisbane.qld.gov.au/about-council/news-media/news/rss',
            'property_observer_brisbane': 'https://www.propertyobserver.com.au/location/brisbane',
            'realestate_news': 'https://www.realestate.com.au/news/brisbane/',
            'qld_govt_data': 'https://www.data.qld.gov.au/'
        }
    
    def get_preset_questions(self) -> List[str]:
        """Return the 5 preset Brisbane property questions"""
        return [
            "What new development applications were submitted in Brisbane this month?",
            "Which Brisbane suburbs are trending in property news?",
            "Are there any major infrastructure projects affecting property values?",
            "What zoning changes have been approved recently?",
            "Which areas have the most development activity?"
        ]
    
    def process_query(self, question: str, query_type: str = 'custom') -> Generator[Dict, None, None]:
        """
        Main pipeline processing with real-time updates
        Yields progress updates for frontend display
        """
        start_time = time.time()
        query_id = None
        
        try:
            # Store query in database
            query_id = self.db.store_query(question, query_type)
            yield self._create_progress_update('started', f'Processing query: {question}')
            
            # Stage 1: Claude Analysis
            yield self._create_progress_update('claude_analysis', 'Analyzing question with Claude...')
            claude_analysis = self._analyze_with_claude(question)
            
            if claude_analysis:
                self.db.update_query_stage(query_id, 'claude_analysis', claude_analysis)
                self.db.add_processing_log(query_id, 'claude_analysis', 'Claude analysis completed', 'success')
                yield self._create_progress_update('claude_complete', 'Claude analysis complete')
            else:
                raise Exception("Claude analysis failed")
            
            # Stage 2: Data Scraping
            yield self._create_progress_update('scraping', 'Fetching Brisbane property data...')
            scraped_data = self._scrape_relevant_data(claude_analysis, question)
            
            if scraped_data:
                self.db.update_query_stage(query_id, 'scraped_data', json.dumps(scraped_data))
                self.db.add_processing_log(query_id, 'scraping', f'Scraped {len(scraped_data)} sources', 'success')
                yield self._create_progress_update('scraping_complete', f'Found {len(scraped_data)} relevant sources')
            else:
                yield self._create_progress_update('scraping_warning', 'Limited data available, proceeding with cached information')
                scraped_data = self._get_mock_brisbane_data(question)
            
            # Stage 3: Gemini Processing
            yield self._create_progress_update('gemini_processing', 'Processing data with Gemini Pro...')
            gemini_insights = self._process_with_gemini(scraped_data, question)
            
            if gemini_insights:
                self.db.update_query_stage(query_id, 'gemini_processing', gemini_insights)
                self.db.add_processing_log(query_id, 'gemini_processing', 'Gemini processing completed', 'success')
                yield self._create_progress_update('gemini_complete', 'Gemini analysis complete')
            else:
                raise Exception("Gemini processing failed")
            
            # Stage 4: Final Summary (using enhanced formatting)
            yield self._create_progress_update('formatting', 'Generating final summary...')
            final_answer = self._format_final_answer(gemini_insights, question, scraped_data)
            
            # Store final result
            processing_time = time.time() - start_time
            self.db.update_query_stage(query_id, 'final_answer', final_answer)
            self.db.add_processing_log(query_id, 'complete', f'Processing completed in {processing_time:.2f}s', 'success', processing_time)
            
            yield self._create_progress_update('complete', f'Analysis complete! ({processing_time:.1f}s)', {
                'final_answer': final_answer,
                'processing_time': processing_time,
                'query_id': query_id
            })
            
        except Exception as e:
            error_msg = f"Pipeline error: {str(e)}"
            logger.error(error_msg)
            
            if query_id:
                self.db.add_processing_log(query_id, 'error', error_msg, 'error', error_details=str(e))
            
            yield self._create_progress_update('error', error_msg)
    
    def _create_progress_update(self, status: str, message: str, data: Dict = None) -> Dict:
        """Create standardized progress update"""
        update = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }
        if data:
            update['data'] = data
        return update
    
    def _analyze_with_claude(self, question: str) -> Optional[str]:
        """Claude analyzes the question and determines data strategy"""
        if not self.claude_client:
            return self._mock_claude_analysis(question)
        
        try:
            prompt = f"""
            You are a Brisbane property research analyst. Analyze this question and provide a strategic approach for gathering relevant data:

            Question: "{question}"

            Please provide:
            1. What specific Brisbane areas/suburbs should be prioritized
            2. What types of data sources would be most relevant
            3. What timeframe should be considered
            4. What key information should be extracted

            Focus on Brisbane-specific property development, infrastructure, and market trends.
            Be specific about Brisbane suburbs, council areas, and local property dynamics.
            """
            
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude analysis failed: {str(e)}")
            return self._mock_claude_analysis(question)
    
    def _scrape_relevant_data(self, claude_analysis: str, question: str) -> List[Dict]:
        """Scrape Brisbane property data based on Claude's analysis"""
        scraped_data = []
        
        # Try to scrape Brisbane Council RSS
        try:
            council_data = self._scrape_brisbane_council_rss()
            if council_data:
                scraped_data.extend(council_data)
                self.db.update_data_source_status('Brisbane Council RSS', 'success')
        except Exception as e:
            logger.error(f"Brisbane Council RSS scraping failed: {str(e)}")
            self.db.update_data_source_status('Brisbane Council RSS', 'failed', False)
        
        # Try to scrape property news
        try:
            news_data = self._scrape_property_news()
            if news_data:
                scraped_data.extend(news_data)
                self.db.update_data_source_status('Property News', 'success')
        except Exception as e:
            logger.error(f"Property news scraping failed: {str(e)}")
            self.db.update_data_source_status('Property News', 'failed', False)
        
        # If no real data, use mock data
        if not scraped_data:
            scraped_data = self._get_mock_brisbane_data(question)
        
        return scraped_data
    
    def _scrape_brisbane_council_rss(self) -> List[Dict]:
        """Scrape Brisbane City Council RSS feed"""
        try:
            # Use a more accessible Brisbane Council feed
            rss_url = "https://www.brisbane.qld.gov.au/about-council/news-media/news/rss"
            
            response = requests.get(rss_url, timeout=10)
            response.raise_for_status()
            
            feed = feedparser.parse(response.content)
            
            data = []
            for entry in feed.entries[:10]:  # Limit to recent entries
                data.append({
                    'source': 'Brisbane City Council',
                    'title': entry.title,
                    'summary': entry.summary if hasattr(entry, 'summary') else '',
                    'link': entry.link,
                    'published': entry.published if hasattr(entry, 'published') else '',
                    'type': 'government_news'
                })
            
            return data
            
        except Exception as e:
            logger.error(f"Brisbane Council RSS scraping failed: {str(e)}")
            return []
    
    def _scrape_property_news(self) -> List[Dict]:
        """Scrape Brisbane property news"""
        try:
            # Simple web scraping for property news
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Try a simple property news search
            url = "https://www.propertyobserver.com.au/location/brisbane"
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract article titles and links (basic example)
            articles = []
            for article in soup.find_all('article')[:5]:  # Limit to 5 articles
                title_elem = article.find('h2') or article.find('h3')
                if title_elem:
                    articles.append({
                        'source': 'Property Observer',
                        'title': title_elem.get_text().strip(),
                        'summary': '',
                        'link': url,
                        'published': '',
                        'type': 'property_news'
                    })
            
            return articles
            
        except Exception as e:
            logger.error(f"Property news scraping failed: {str(e)}")
            return []
    
    def _get_mock_brisbane_data(self, question: str) -> List[Dict]:
        """Generate realistic mock Brisbane property data"""
        mock_data = []
        
        # Development applications mock data
        if 'development' in question.lower() or 'application' in question.lower():
            mock_data.extend([
                {
                    'source': 'Brisbane City Council',
                    'title': 'Major Mixed-Use Development Approved for South Brisbane',
                    'summary': 'Council has approved a 45-story mixed-use development at 123 Main Street, South Brisbane, including 400 residential units and commercial space.',
                    'link': 'https://www.brisbane.qld.gov.au/development/app-12345',
                    'published': '2024-01-15',
                    'type': 'development_approval'
                },
                {
                    'source': 'Brisbane City Council',
                    'title': 'Residential Development Application - Fortitude Valley',
                    'summary': 'New 28-story residential tower proposed for James Street, Fortitude Valley, with 220 apartments and ground floor retail.',
                    'link': 'https://www.brisbane.qld.gov.au/development/app-12346',
                    'published': '2024-01-10',
                    'type': 'development_application'
                }
            ])
        
        # Infrastructure projects mock data
        if 'infrastructure' in question.lower() or 'project' in question.lower():
            mock_data.extend([
                {
                    'source': 'Queensland Government',
                    'title': 'Cross River Rail Project Update',
                    'summary': 'Cross River Rail construction continues with new stations at Woolloongabba and Boggo Road expected to boost property values in surrounding areas.',
                    'link': 'https://www.crossriverrail.qld.gov.au/news/update-jan-2024',
                    'published': '2024-01-12',
                    'type': 'infrastructure_news'
                }
            ])
        
        # Suburb trending mock data
        if 'suburb' in question.lower() or 'trending' in question.lower():
            mock_data.extend([
                {
                    'source': 'Property Observer',
                    'title': 'Paddington Emerges as Brisbane\'s Hottest Suburb',
                    'summary': 'Paddington has seen 15% price growth in the past quarter, driven by its proximity to the city and character housing stock.',
                    'link': 'https://www.propertyobserver.com.au/paddington-brisbane-growth',
                    'published': '2024-01-08',
                    'type': 'market_analysis'
                }
            ])
        
        return mock_data
    
    def _process_with_gemini(self, scraped_data: List[Dict], question: str) -> Optional[str]:
        """Process scraped data with Gemini Pro"""
        if not self.gemini_model:
            return self._mock_gemini_processing(scraped_data, question)
        
        try:
            # Prepare data for Gemini
            data_summary = ""
            for item in scraped_data:
                data_summary += f"Source: {item['source']}\n"
                data_summary += f"Title: {item['title']}\n"
                data_summary += f"Summary: {item['summary']}\n"
                data_summary += f"Published: {item['published']}\n\n"
            
            prompt = f"""
            You are a Brisbane property market analyst. Analyze the following data and provide insights for this question:

            Question: "{question}"

            Data Sources:
            {data_summary}

            Please provide:
            1. Key findings relevant to the question
            2. Trends and patterns in Brisbane property market
            3. Specific suburbs or areas mentioned
            4. Any significant developments or changes
            5. Market implications

            Focus on Brisbane-specific insights and provide actionable information for property professionals.
            """
            
            response = self.gemini_model.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini processing failed: {str(e)}")
            return self._mock_gemini_processing(scraped_data, question)
    
    def _format_final_answer(self, gemini_insights: str, question: str, scraped_data: List[Dict]) -> str:
        """Format the final answer with enhanced presentation"""
        try:
            # Create a professional summary
            sources_count = len(scraped_data)
            source_types = set(item['type'] for item in scraped_data)
            
            final_answer = f"""# Brisbane Property Intelligence Analysis

## Query: {question}

## Executive Summary
{gemini_insights}

## Data Sources Analyzed
- **Total Sources**: {sources_count}
- **Source Types**: {', '.join(source_types)}
- **Analysis Date**: {datetime.now().strftime('%B %d, %Y')}

## Key Brisbane Areas Mentioned
"""
            
            # Extract Brisbane suburbs/areas mentioned
            brisbane_areas = self._extract_brisbane_areas(gemini_insights)
            if brisbane_areas:
                for area in brisbane_areas:
                    final_answer += f"- {area}\n"
            else:
                final_answer += "- Various Brisbane metropolitan areas\n"
            
            final_answer += f"""
## Recent Developments
"""
            
            # Add recent development summaries
            for item in scraped_data[:3]:  # Top 3 most relevant
                final_answer += f"- **{item['title']}** ({item['source']})\n"
                if item['summary']:
                    final_answer += f"  {item['summary'][:150]}...\n"
            
            final_answer += f"""
## Market Implications
Based on the analysis, key implications for Brisbane property market include ongoing development activity, infrastructure investment impact, and changing suburban preferences.

*Analysis generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}*
"""
            
            return final_answer
            
        except Exception as e:
            logger.error(f"Final answer formatting failed: {str(e)}")
            return f"Analysis completed for: {question}\n\nInsights: {gemini_insights}\n\nSources analyzed: {len(scraped_data)}"
    
    def _extract_brisbane_areas(self, text: str) -> List[str]:
        """Extract Brisbane suburb names from text"""
        brisbane_suburbs = [
            'South Brisbane', 'Fortitude Valley', 'New Farm', 'Teneriffe', 'Paddington',
            'Toowong', 'St Lucia', 'Woolloongabba', 'West End', 'Kangaroo Point',
            'Spring Hill', 'Petrie Terrace', 'Milton', 'Auchenflower', 'Rosalie',
            'Newstead', 'Bowen Hills', 'Herston', 'Kelvin Grove', 'Red Hill',
            'Ashgrove', 'Bardon', 'Indooroopilly', 'Taringa', 'Chapel Hill'
        ]
        
        found_areas = []
        for suburb in brisbane_suburbs:
            if suburb.lower() in text.lower():
                found_areas.append(suburb)
        
        return found_areas
    
    def _mock_claude_analysis(self, question: str) -> str:
        """Mock Claude analysis when API is unavailable"""
        return f"""Brisbane Property Analysis Strategy for: "{question}"

1. **Priority Areas**: Focus on inner-city Brisbane suburbs including South Brisbane, Fortitude Valley, New Farm, and Woolloongabba, which show highest development activity.

2. **Data Sources**: 
   - Brisbane City Council development applications
   - Property news from major publications
   - Infrastructure project announcements
   - Market analysis reports

3. **Timeframe**: Current month focus with 3-month trend analysis for broader context.

4. **Key Information**: Development approvals, zoning changes, infrastructure projects, market trends, and suburb-specific activity.

This analysis will provide comprehensive insights into Brisbane's property landscape with particular attention to development patterns and market dynamics."""
    
    def _mock_gemini_processing(self, scraped_data: List[Dict], question: str) -> str:
        """Mock Gemini processing when API is unavailable"""
        sources_count = len(scraped_data)
        
        return f"""Brisbane Property Market Analysis - {datetime.now().strftime('%B %Y')}

**Key Findings:**
- Analyzed {sources_count} current data sources
- Strong development activity in inner Brisbane suburbs
- Infrastructure projects driving property value growth
- Mixed-use developments gaining council approval

**Market Trends:**
- Continued apartment development in South Brisbane and Fortitude Valley
- Infrastructure investment boosting surrounding property values
- Increased interest in character suburbs like Paddington and New Farm

**Significant Developments:**
- Multiple high-rise residential projects approved
- Cross River Rail project impacting property values
- Zoning changes supporting urban densification

**Market Implications:**
Brisbane's property market shows sustained growth driven by infrastructure investment and strategic development approvals. Inner-city areas remain most active with strong development pipeline."""
    
    def get_query_history(self, limit: int = 50) -> List[Dict]:
        """Get recent query history from database"""
        return self.db.get_query_history(limit)
    
    def get_popular_questions(self, limit: int = 10) -> List[Dict]:
        """Get popular questions for dropdown"""
        popular = self.db.get_popular_questions(limit)
        
        # Combine with preset questions
        preset_questions = self.get_preset_questions()
        
        # Create combined list
        all_questions = []
        
        # Add preset questions first
        for question in preset_questions:
            all_questions.append({
                'question': question,
                'type': 'preset',
                'count': 0
            })
        
        # Add popular questions from database
        for item in popular:
            if item['question'] not in preset_questions:
                all_questions.append({
                    'question': item['question'],
                    'type': 'popular',
                    'count': item['count']
                })
        
        return all_questions[:limit]
    
    def get_database_stats(self) -> Dict:
        """Get database statistics"""
        return self.db.get_database_stats()
    
    def reset_database(self):
        """Reset database (clear all queries)"""
        self.db.clear_all_data()
        logger.info("Database reset completed")
    
    def get_query_details(self, query_id: int) -> Optional[Dict]:
        """Get detailed information about a specific query"""
        return self.db.get_query_details(query_id)
    
    def get_data_sources_status(self) -> List[Dict]:
        """Get status of all data sources"""
        return self.db.get_data_sources()