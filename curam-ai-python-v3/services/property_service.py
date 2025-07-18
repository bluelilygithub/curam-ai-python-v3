"""
Property Analysis Service
High-level service for Australian property intelligence with real RSS data
UPDATED: Location detection moved here for reliability
"""

from typing import Dict, List
from datetime import datetime
import logging

from config import Config

logger = logging.getLogger(__name__)

class PropertyAnalysisService:
    """High-level property analysis service with real RSS integration"""
    
    def __init__(self, llm_service, rss_service=None):
        self.llm_service = llm_service
        self.rss_service = rss_service
        logger.info(f"PropertyAnalysisService initialized with RSS: {rss_service is not None}")
    
    def analyze_property_question(self, question: str) -> Dict:
        """Complete property analysis pipeline with real RSS data"""
        try:
            question_type = self._determine_question_type(question)
            
            # Stage 1: Detect location using ORIGINAL question (not enhanced)
            location_info = self._detect_location_scope(question)
            logger.info(f"LOCATION DETECTION RESULT: {location_info}")
            
            # Stage 2: Get Real Australian Property Data
            data_sources = self._get_real_property_data_sources(question)
            
            # Stage 3: Build enhanced question with RSS context
            enhanced_question = self._build_enhanced_question(question, data_sources)
            
            # Stage 4: Claude Analysis with location info
            claude_result = self.llm_service.analyze_with_claude_location(enhanced_question, location_info)
            
            # Stage 5: Gemini Processing with location info
            gemini_result = self.llm_service.analyze_with_gemini_location(
                enhanced_question, 
                claude_result.get('analysis', ''),
                location_info
            )
            
            # Stage 6: Format Final Answer
            final_answer = self._format_comprehensive_answer(
                question, claude_result, gemini_result, data_sources, has_real_data=bool(data_sources)
            )
            
            return {
                'success': True,
                'question': question,
                'question_type': question_type,
                'final_answer': final_answer,
                'processing_stages': {
                    'claude_success': claude_result['success'],
                    'gemini_success': gemini_result['success'],
                    'rss_data_sources': len(data_sources),
                    'data_sources_count': len(data_sources),
                    'claude_model': claude_result.get('model_used'),
                    'gemini_model': gemini_result.get('model_used'),
                    'real_data_used': self._has_real_data(data_sources),
                    'location_detected': location_info['scope']
                },
                'claude_result': claude_result,
                'gemini_result': gemini_result,
                'data_sources': data_sources
            }
            
        except Exception as e:
            logger.error(f"Property analysis pipeline failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'final_answer': self._generate_fallback_answer(question)
            }
    
    def _determine_question_type(self, question: str) -> str:
        """Determine if question is preset or custom"""
        return 'preset' if question in Config.PRESET_QUESTIONS else 'custom'
    
    def _detect_location_scope(self, question: str) -> Dict:
        """Detect if question is location-specific or national - MOVED FROM LLM SERVICE"""
        question_lower = question.lower()
        
        logger.info(f"LOCATION DETECTION: Question='{question}', Lowercase='{question_lower}'")
        
        # Brisbane/Queensland specific keywords
        brisbane_keywords = ['brisbane', 'queensland', 'qld', 'gold coast', 'sunshine coast',
                           'ipswich', 'logan', 'caboolture', 'toowoomba', 'redland', 'moreton bay']
        
        # Other major Australian cities
        sydney_keywords = ['sydney', 'nsw', 'new south wales', 'parramatta', 'penrith']
        melbourne_keywords = ['melbourne', 'victoria', 'vic', 'geelong', 'ballarat']
        perth_keywords = ['perth', 'western australia', 'wa', 'fremantle', 'joondalup']
        adelaide_keywords = ['adelaide', 'south australia', 'sa']
        
        # Check for specific locations
        if any(keyword in question_lower for keyword in brisbane_keywords):
            result = {'scope': 'brisbane', 'focus': 'Brisbane and Queensland'}
        elif any(keyword in question_lower for keyword in sydney_keywords):
            result = {'scope': 'sydney', 'focus': 'Sydney and New South Wales'}
        elif any(keyword in question_lower for keyword in melbourne_keywords):
            result = {'scope': 'melbourne', 'focus': 'Melbourne and Victoria'}
        elif any(keyword in question_lower for keyword in perth_keywords):
            result = {'scope': 'perth', 'focus': 'Perth and Western Australia'}
        elif any(keyword in question_lower for keyword in adelaide_keywords):
            result = {'scope': 'adelaide', 'focus': 'Adelaide and South Australia'}
        else:
            result = {'scope': 'national', 'focus': 'Australian national property market'}
        
        logger.info(f"LOCATION DETECTION FINAL RESULT: {result}")
        return result
    
    def _get_real_property_data_sources(self, question: str) -> List[Dict]:
        """Get real Australian property data from RSS feeds"""
        try:
            if not self.rss_service:
                logger.warning("RSS service not available, using fallback")
                return []
            
            # Determine if question is location-specific
            question_lower = question.lower()
            brisbane_keywords = ['brisbane', 'queensland', 'qld', 'gold coast', 'sunshine coast']
            is_brisbane_focused = any(keyword in question_lower for keyword in brisbane_keywords)
            
            # Get real RSS articles
            if is_brisbane_focused:
                articles = self.rss_service.get_brisbane_news(max_articles=5)
                logger.info(f"Retrieved {len(articles)} Brisbane-specific articles")
            else:
                articles = self.rss_service.get_recent_news(max_articles=6)
                logger.info(f"Retrieved {len(articles)} Australian property articles")
            
            # Convert articles to data sources format
            data_sources = []
            for article in articles:
                data_sources.append({
                    'source': article['source'],
                    'title': article['title'],
                    'summary': article['summary'][:200] + "..." if len(article['summary']) > 200 else article['summary'],
                    'link': article.get('link', ''),
                    'published': article.get('published', ''),
                    'type': 'rss_news',
                    'relevance': 'high' if article.get('brisbane_relevant') else 'medium',
                    'investment_focus': article.get('investment_relevant', False),
                    'real_data': True
                })
            
            logger.info(f"Converted {len(data_sources)} articles to data sources")
            return data_sources
            
        except Exception as e:
            logger.error(f"Failed to get RSS data: {e}")
            return []
    
    def _has_real_data(self, data_sources: List[Dict]) -> bool:
        """Check if we have real RSS data"""
        return len(data_sources) > 0 and any(source.get('real_data') for source in data_sources)
    
    def _build_enhanced_question(self, question: str, data_sources: List[Dict]) -> str:
        """Build enhanced question with RSS context for LLM analysis"""
        if not data_sources or not self._has_real_data(data_sources):
            return f"""Analyze this Australian property question using general market knowledge:

{question}

Note: Provide comprehensive analysis based on current Australian property market understanding."""
        
        # Detect location focus for context
        question_lower = question.lower()
        brisbane_keywords = ['brisbane', 'queensland', 'qld', 'gold coast', 'sunshine coast']
        is_brisbane_focused = any(keyword in question_lower for keyword in brisbane_keywords)
        
        location_context = "Brisbane/Queensland property market" if is_brisbane_focused else "Australian property market"
        
        enhanced_question = f"""Analyze this Australian property question using the following REAL current market data:

QUESTION: {question}

CURRENT {location_context.upper()} DATA (from RSS feeds on {datetime.now().strftime('%Y-%m-%d')}):
"""
        
        for i, source in enumerate(data_sources[:4], 1):  # Limit to top 4 to avoid token limits
            investment_indicator = "💰" if source.get('investment_focus') else "📊"
            relevance_indicator = "🔥" if source.get('relevance') == 'high' else "📈"
            
            enhanced_question += f"""
{i}. {source['title']} {investment_indicator} {relevance_indicator}
   Source: {source['source']}
   Published: {source['published']}
   Summary: {source['summary']}
"""
        
        enhanced_question += f"""

ANALYSIS INSTRUCTIONS:
- Use this REAL current {location_context} data in your analysis
- Reference specific articles and developments mentioned above
- Provide insights based on actual market conditions and investment implications
- Focus on current trends and developments shown in the data
- Give a comprehensive, professional analysis that demonstrates the value of real-time market intelligence
- Prioritize investment-relevant insights and actionable information

Please provide a detailed analysis that incorporates these real market developments."""
        
        return enhanced_question
    
    def _format_comprehensive_answer(self, question: str, claude_result: Dict, 
                                   gemini_result: Dict, data_sources: List[Dict], has_real_data: bool = True) -> str:
        """Format final comprehensive answer with real data attribution"""
        
        answer_parts = []
        
        # Main Analysis (Gemini if successful, otherwise Claude)
        if gemini_result['success']:
            answer_parts.append(gemini_result['analysis'])
        elif claude_result['success']:
            answer_parts.append(claude_result['analysis'])
        else:
            # Fallback analysis
            answer_parts.append(self._generate_fallback_answer(question))
        
        # Only add sections if we have space and real data
        if has_real_data and data_sources:
            answer_parts.append("")
            answer_parts.append("### Current Market Data Sources")
            answer_parts.append("")
            
            for i, source in enumerate(data_sources[:3], 1):  # Show top 3 sources
                relevance_indicator = "🔥" if source.get('relevance') == 'high' else "📊"
                investment_indicator = " 💰" if source.get('investment_focus') else ""
                answer_parts.append(f"{i}. **{source['source']}** {relevance_indicator}{investment_indicator}: {source['title']}")
            
            answer_parts.append("")
            answer_parts.append("---")
            answer_parts.append("*Analysis based on real-time RSS data from Australian property investment industry sources*")
        
        return "\n".join(answer_parts)
    
    def _generate_fallback_answer(self, question: str) -> str:
        """Generate enhanced fallback answer for Australian property questions"""
        # Detect if Brisbane focused
        location_info = self._detect_location_scope(question)
        
        if location_info['scope'] == 'brisbane':
            return f"""Based on current Brisbane and Queensland property market understanding:

The Brisbane and Queensland property market continues to show strong fundamentals driven by interstate migration, infrastructure investment, and lifestyle factors. Key factors influencing current market conditions include Olympic preparations, Cross River Rail development, population growth from southern states, and evolving work-from-home trends.

**Current Brisbane Market Overview:**
- Strong demand in inner-city suburbs due to infrastructure improvements
- Growth corridors along major transport routes showing consistent appreciation
- Regional Queensland markets benefiting from lifestyle migration trends  
- Development activity concentrated in transit-oriented locations
- Rental markets showing strength due to interstate migration

**Key Brisbane Investment Considerations:**
- Infrastructure connectivity remains crucial for capital growth
- Olympic Games 2032 infrastructure already influencing property values
- Government policy settings supporting first home buyers and investors
- Population growth supporting rental demand across greater Brisbane
- Regional Queensland offering yield opportunities for investors

**Investment Focus Areas:**
- Cross River Rail corridor suburbs for future capital growth
- Established inner-ring suburbs for rental yield stability
- Growth areas in Logan, Ipswich, and Moreton Bay for affordability
- Gold Coast and Sunshine Coast for lifestyle investment opportunities

*Note: This analysis is based on general Brisbane market knowledge. Our system typically provides enhanced analysis using real-time RSS feeds from Smart Property Investment, Brisbane Times, and other industry sources when available.*"""
        
        elif location_info['scope'] == 'national':
            return f"""Based on current Australian property market understanding:

The Australian property market continues to show diverse performance across major metropolitan and regional areas. Key factors influencing current market conditions include interest rate environment, population growth patterns, infrastructure development, and government policy settings across all major cities.

**Current National Market Overview:**
- Sydney and Melbourne showing selective growth in premium locations
- Brisbane benefiting from interstate migration and infrastructure investment
- Perth experiencing resource sector-driven demand
- Adelaide showing steady growth with affordability advantages
- Regional markets across all states benefiting from lifestyle migration trends

**Key National Investment Considerations:**
- Market conditions vary significantly by location and property type across all cities
- Infrastructure connectivity remains a key value driver nationally
- Government policy and regulatory changes continue to shape market dynamics
- Economic fundamentals support continued investment activity across major centers
- Regional markets offering yield opportunities as city prices moderate

**Investment Opportunities Across Major Cities:**
- Growth corridors in Sydney, Melbourne, Brisbane, Perth, and Adelaide for capital appreciation
- Regional centers with strong economic fundamentals in all states
- Transit-oriented developments for long-term growth across major cities
- Established suburbs for rental yield stability in all markets

*Note: This analysis is based on general Australian market knowledge. Our system typically provides enhanced analysis using real-time RSS feeds from Smart Property Investment, Your Investment Property, and other industry sources when available.*"""
        
        else:
            # City-specific fallback
            city_focus = location_info['focus']
            return f"""Based on current {city_focus} property market understanding:

The {city_focus} property market shows unique characteristics within the broader Australian property landscape. Local factors including infrastructure development, population growth, economic conditions, and government policy settings influence market dynamics.

**Current Market Considerations:**
- Local market conditions vary by suburb and property type
- Infrastructure connectivity important for capital growth
- Economic fundamentals support continued market activity
- Regional variations within the broader market area

**Investment Opportunities:**
- Growth areas with infrastructure development
- Established suburbs for rental yield
- Transit-oriented locations for long-term appreciation

*Note: This analysis is based on general market knowledge. Our system typically provides enhanced analysis using real-time RSS feeds from property industry sources when available.*"""
    
    def get_analysis_summary(self, analysis_result: Dict) -> Dict:
        """Get summary of analysis for quick overview"""
        return {
            'question_type': analysis_result.get('question_type'),
            'success': analysis_result.get('success'),
            'providers_used': [
                provider for provider in ['claude', 'gemini'] 
                if analysis_result.get('processing_stages', {}).get(f'{provider}_success')
            ],
            'data_sources_count': analysis_result.get('processing_stages', {}).get('data_sources_count', 0),
            'real_data_used': analysis_result.get('processing_stages', {}).get('real_data_used', False),
            'answer_length': len(analysis_result.get('final_answer', '')),
            'location_detected': analysis_result.get('processing_stages', {}).get('location_detected', 'unknown')
        }