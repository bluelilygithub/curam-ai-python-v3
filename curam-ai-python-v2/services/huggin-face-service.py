"""
Hugging Face Service for Property Sentiment Analysis
Analyze sentiment of property descriptions, market news, and development applications
"""

import requests
import logging
import time
from typing import Dict, List, Optional
from config import Config

logger = logging.getLogger(__name__)

class HuggingFaceService:
    """Service for property sentiment analysis using Hugging Face models"""
    
    def __init__(self):
        self.api_key = Config.HUGGING_FACE_API_KEY
        self.base_url = Config.HUGGING_FACE_CONFIG['api_url']
        self.models = Config.HUGGING_FACE_CONFIG['models']
        self.enabled = Config.HUGGING_FACE_ENABLED and bool(self.api_key)
        
        if not self.enabled:
            logger.warning("Hugging Face service disabled - API key not configured")
    
    def analyze_property_sentiment(self, text: str) -> Dict:
        """Analyze sentiment of property-related text"""
        if not self.enabled:
            return self._error_response("Hugging Face service not enabled")
        
        try:
            # Use sentiment analysis model
            response = self._query_model(
                text, 
                self.models['sentiment'],
                'sentiment-analysis'
            )
            
            if response['success']:
                sentiment_data = response['data'][0]
                
                # Convert to property-specific sentiment
                property_sentiment = self._interpret_property_sentiment(sentiment_data)
                
                return {
                    'success': True,
                    'text': text,
                    'sentiment': property_sentiment['sentiment'],
                    'confidence': property_sentiment['confidence'],
                    'property_interpretation': property_sentiment['interpretation'],
                    'raw_analysis': sentiment_data,
                    'provider': 'hugging_face'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Property sentiment analysis failed: {e}")
            return self._error_response(f"Sentiment analysis failed: {str(e)}")
    
    def classify_development_type(self, description: str) -> Dict:
        """Classify development application type from description"""
        if not self.enabled:
            return self._error_response("Hugging Face service not enabled")
        
        try:
            # Define property development categories
            candidate_labels = [
                "residential development",
                "commercial development", 
                "mixed-use development",
                "infrastructure project",
                "renovation/alteration",
                "subdivision",
                "industrial development"
            ]
            
            # Use classification model
            response = self._query_classification(
                description,
                candidate_labels
            )
            
            if response['success']:
                classifications = response['data']
                
                return {
                    'success': True,
                    'description': description,
                    'primary_type': classifications[0]['label'],
                    'confidence': classifications[0]['score'],
                    'all_classifications': classifications,
                    'provider': 'hugging_face'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Development classification failed: {e}")
            return self._error_response(f"Classification failed: {str(e)}")
    
    def analyze_market_news_sentiment(self, news_articles: List[str]) -> Dict:
        """Analyze sentiment of multiple property news articles"""
        if not self.enabled:
            return self._error_response("Hugging Face service not enabled")
        
        try:
            results = []
            overall_sentiment_scores = []
            
            for article in news_articles:
                # Analyze each article
                sentiment_result = self.analyze_property_sentiment(article)
                
                if sentiment_result['success']:
                    results.append({
                        'text': article[:200] + "..." if len(article) > 200 else article,
                        'sentiment': sentiment_result['sentiment'],
                        'confidence': sentiment_result['confidence'],
                        'interpretation': sentiment_result['property_interpretation']
                    })
                    
                    # Add to overall sentiment calculation
                    sentiment_score = sentiment_result['confidence']
                    if sentiment_result['sentiment'] == 'negative':
                        sentiment_score = -sentiment_score
                    elif sentiment_result['sentiment'] == 'neutral':
                        sentiment_score = 0
                    
                    overall_sentiment_scores.append(sentiment_score)
                
                # Rate limiting
                time.sleep(0.1)
            
            # Calculate overall market sentiment
            overall_sentiment = self._calculate_overall_sentiment(overall_sentiment_scores)
            
            return {
                'success': True,
                'articles_analyzed': len(results),
                'individual_results': results,
                'overall_sentiment': overall_sentiment,
                'provider': 'hugging_face'
            }
            
        except Exception as e:
            logger.error(f"Market news sentiment analysis failed: {e}")
            return self._error_response(f"Market analysis failed: {str(e)}")
    
    def summarize_development_applications(self, applications: List[str]) -> Dict:
        """Summarize multiple development applications"""
        if not self.enabled:
            return self._error_response("Hugging Face service not enabled")
        
        try:
            # Combine applications into a single text for summarization
            combined_text = " ".join(applications)
            
            # Limit text length for API
            if len(combined_text) > 1000:
                combined_text = combined_text[:1000] + "..."
            
            response = self._query_model(
                combined_text,
                self.models['summarization'],
                'summarization'
            )
            
            if response['success']:
                summary_data = response['data'][0]
                
                return {
                    'success': True,
                    'applications_count': len(applications),
                    'summary': summary_data['summary_text'],
                    'original_length': len(combined_text),
                    'summary_length': len(summary_data['summary_text']),
                    'provider': 'hugging_face'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Development application summarization failed: {e}")
            return self._error_response(f"Summarization failed: {str(e)}")
    
    def _query_model(self, text: str, model: str, task: str) -> Dict:
        """Query Hugging Face model API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'inputs': text
            }
            
            response = requests.post(
                f"{self.base_url}/{model}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'data': response.json(),
                    'model_used': model,
                    'task': task
                }
            elif response.status_code == 503:
                # Model loading, retry after delay
                time.sleep(2)
                return self._query_model(text, model, task)
            else:
                logger.error(f"Hugging Face API error: {response.status_code} - {response.text}")
                return self._error_response(f"API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Hugging Face query failed: {e}")
            return self._error_response(f"Query failed: {str(e)}")
    
    def _query_classification(self, text: str, candidate_labels: List[str]) -> Dict:
        """Query classification model with candidate labels"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'inputs': text,
                'parameters': {
                    'candidate_labels': candidate_labels
                }
            }
            
            response = requests.post(
                f"{self.base_url}/{self.models['classification']}",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Format response for consistent structure
                formatted_data = []
                for label, score in zip(data['labels'], data['scores']):
                    formatted_data.append({
                        'label': label,
                        'score': score
                    })
                
                return {
                    'success': True,
                    'data': formatted_data,
                    'model_used': self.models['classification']
                }
            else:
                logger.error(f"Hugging Face classification error: {response.status_code}")
                return self._error_response(f"Classification error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Hugging Face classification failed: {e}")
            return self._error_response(f"Classification failed: {str(e)}")
    
    def _interpret_property_sentiment(self, sentiment_data: Dict) -> Dict:
        """Interpret sentiment for property context"""
        label = sentiment_data['label'].lower()
        score = sentiment_data['score']
        
        # Map sentiment to property interpretation
        if 'positive' in label:
            interpretation = "Favorable market conditions" if score > 0.8 else "Positive market outlook"
            sentiment = 'positive'
        elif 'negative' in label:
            interpretation = "Challenging market conditions" if score > 0.8 else "Cautious market outlook"
            sentiment = 'negative'
        else:
            interpretation = "Stable market conditions"
            sentiment = 'neutral'
        
        return {
            'sentiment': sentiment,
            'confidence': score,
            'interpretation': interpretation
        }
    
    def _calculate_overall_sentiment(self, scores: List[float]) -> Dict:
        """Calculate overall sentiment from multiple scores"""
        if not scores:
            return {'sentiment': 'neutral', 'confidence': 0.0, 'interpretation': 'No data'}
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score > 0.2:
            sentiment = 'positive'
            interpretation = 'Overall positive market sentiment'
        elif avg_score < -0.2:
            sentiment = 'negative'
            interpretation = 'Overall negative market sentiment'
        else:
            sentiment = 'neutral'
            interpretation = 'Overall neutral market sentiment'
        
        return {
            'sentiment': sentiment,
            'confidence': abs(avg_score),
            'interpretation': interpretation,
            'sample_size': len(scores)
        }
    
    def _error_response(self, error_msg: str) -> Dict:
        """Standardized error response"""
        return {
            'success': False,
            'error': error_msg,
            'provider': 'hugging_face'
        }
    
    def get_health_status(self) -> Dict:
        """Get Hugging Face service health status"""
        return {
            'enabled': self.enabled,
            'api_key_configured': bool(self.api_key),
            'models_available': list(self.models.keys()),
            'service_type': 'sentiment_analysis'