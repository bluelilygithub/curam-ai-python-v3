"""
Stability AI Service for Property Visualizations
Generate charts, infographics, and visual content for Australian property analysis
"""

import requests
import logging
import base64
import io
from typing import Dict, Optional, List
from config import Config

logger = logging.getLogger(__name__)

class StabilityService:
    """Service for generating property visualizations using Stability AI"""
    
    def __init__(self):
        self.api_key = Config.STABILITY_API_KEY
        self.base_url = Config.STABILITY_CONFIG['base_url']
        self.models = Config.STABILITY_CONFIG['models']
        self.default_params = Config.STABILITY_CONFIG['default_params']
        self.enabled = Config.STABILITY_ENABLED and bool(self.api_key)
        
        if not self.enabled:
            logger.warning("Stability AI service disabled - API key not configured")
    
    def generate_property_chart(self, data: Dict, chart_type: str = 'bar') -> Dict:
        """Generate property data visualization chart"""
        if not self.enabled:
            return self._error_response("Stability AI service not enabled")
        
        try:
            # Create descriptive prompt for property chart
            prompt = self._create_chart_prompt(data, chart_type)
            
            # Generate image using Stability AI
            response = self._generate_image(prompt, 'chart_generation')
            
            if response['success']:
                return {
                    'success': True,
                    'chart_type': chart_type,
                    'image_data': response['image_data'],
                    'image_format': 'png',
                    'description': prompt,
                    'provider': 'stability_ai'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Property chart generation failed: {e}")
            return self._error_response(f"Chart generation failed: {str(e)}")
    
    def generate_suburb_infographic(self, suburb_data: Dict) -> Dict:
        """Generate suburb information infographic"""
        if not self.enabled:
            return self._error_response("Stability AI service not enabled")
        
        try:
            # Create infographic prompt
            prompt = self._create_infographic_prompt(suburb_data)
            
            # Generate infographic
            response = self._generate_image(prompt, 'infographic')
            
            if response['success']:
                return {
                    'success': True,
                    'suburb': suburb_data.get('name', 'Unknown'),
                    'image_data': response['image_data'],
                    'image_format': 'png',
                    'description': prompt,
                    'provider': 'stability_ai'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Suburb infographic generation failed: {e}")
            return self._error_response(f"Infographic generation failed: {str(e)}")
    
    def generate_trend_visualization(self, trend_data: List[Dict]) -> Dict:
        """Generate trend visualization for property market data"""
        if not self.enabled:
            return self._error_response("Stability AI service not enabled")
        
        try:
            # Create trend visualization prompt
            prompt = self._create_trend_prompt(trend_data)
            
            # Generate visualization
            response = self._generate_image(prompt, 'chart_generation')
            
            if response['success']:
                return {
                    'success': True,
                    'trend_type': 'market_trends',
                    'image_data': response['image_data'],
                    'image_format': 'png',
                    'description': prompt,
                    'data_points': len(trend_data),
                    'provider': 'stability_ai'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Trend visualization generation failed: {e}")
            return self._error_response(f"Trend visualization failed: {str(e)}")
    
    def _generate_image(self, prompt: str, model_type: str = 'chart_generation') -> Dict:
        """Generate image using Stability AI API"""
        try:
            model = self.models.get(model_type, self.models['chart_generation'])
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'text_prompts': [{'text': prompt}],
                'cfg_scale': self.default_params['cfg_scale'],
                'height': self.default_params['height'],
                'width': self.default_params['width'],
                'steps': self.default_params['steps'],
                'samples': 1
            }
            
            response = requests.post(
                f"{self.base_url}/generation/{model}/text-to-image",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                # Extract base64 image data
                image_data = data['artifacts'][0]['base64']
                
                return {
                    'success': True,
                    'image_data': image_data,
                    'model_used': model
                }
            else:
                logger.error(f"Stability AI API error: {response.status_code} - {response.text}")
                return self._error_response(f"API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Stability AI generation failed: {e}")
            return self._error_response(f"Generation failed: {str(e)}")
    
    def _create_chart_prompt(self, data: Dict, chart_type: str) -> str:
        """Create prompt for property chart generation"""
        chart_description = {
            'bar': 'professional bar chart',
            'line': 'clean line graph',
            'pie': 'modern pie chart',
            'area': 'filled area chart'
        }.get(chart_type, 'professional bar chart')
        
        return f"""Create a {chart_description} showing Australian property market data. 
        Professional business style with clean design, modern colors (blues and greens), 
        clear labels and grid lines. Data represents: {data.get('title', 'Property Market Analysis')}. 
        Include title, axis labels, and professional formatting suitable for property reports. 
        Style: corporate, clean, modern data visualization."""
    
    def _create_infographic_prompt(self, suburb_data: Dict) -> str:
        """Create prompt for suburb infographic"""
        suburb_name = suburb_data.get('name', 'Australian Suburb')
        
        return f"""Create a professional property infographic for {suburb_name}, Australian. 
        Modern design with Australian city colors (blue, green, gold). Include sections for: 
        property prices, development activity, infrastructure, and key statistics. 
        Clean layout with icons, charts, and professional typography. 
        Style: real estate marketing, professional, informative, modern Australian design."""
    
    def _create_trend_prompt(self, trend_data: List[Dict]) -> str:
        """Create prompt for trend visualization"""
        return f"""Create a professional trend analysis visualization for Australian property market. 
        Show market trends with directional arrows, percentage changes, and time series data. 
        Modern business style with professional color scheme (blues, greens, grays). 
        Include trend lines, data points, and clear indicators for growth/decline. 
        Style: financial analysis, professional dashboard, clean modern design."""
    
    def _error_response(self, error_msg: str) -> Dict:
        """Standardized error response"""
        return {
            'success': False,
            'error': error_msg,
            'image_data': None,
            'provider': 'stability_ai'
        }
    
    def get_health_status(self) -> Dict:
        """Get Stability AI service health status"""
        return {
            'enabled': self.enabled,
            'api_key_configured': bool(self.api_key),
            'models_available': list(self.models.keys()),
            'service_type': 'visualization'
        }
    
    def test_connection(self) -> Dict:
        """Test connection to Stability AI API"""
        if not self.enabled:
            return self._error_response("Service not enabled")
        
        try:
            # Test with minimal image generation
            test_prompt = "Simple blue circle on white background, minimal, clean"
            response = self._generate_image(test_prompt)
            
            if response['success']:
                return {
                    'success': True,
                    'message': 'Stability AI connection successful',
                    'model_tested': response.get('model_used')
                }
            else:
                return response
                
        except Exception as e:
            return self._error_response(f"Connection test failed: {str(e)}")