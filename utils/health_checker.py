"""
Health Checker for Australian Property Intelligence
Professional health monitoring for all services
"""

import sys
import logging
from datetime import datetime
from typing import Dict
from config import Config

logger = logging.getLogger(__name__)

class HealthChecker:
    """Comprehensive health checking for all services"""
    
    def __init__(self, services: Dict):
        self.services = services
    
    def get_service_status(self) -> Dict:
        """Get basic service status for API responses"""
        return {
            'database': 'connected' if self.services.get('database') else 'disconnected',
            'llm_service': 'connected' if self.services.get('llm') else 'disconnected',
            'property_service': 'connected' if self.services.get('property') else 'disconnected',
            'claude': self._get_claude_status(),
            'gemini': self._get_gemini_status()
        }
    
    def get_comprehensive_health(self) -> Dict:
        """Get comprehensive health check for detailed monitoring"""
        try:
            health_data = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'python_version': sys.version.split()[0],
                'environment': self._get_environment_info(),
                'services': self._check_all_services(),
                'configuration': self._check_configuration(),
                'llm_providers': self._check_llm_providers()
            }
            
            # Determine overall status
            service_issues = [
                name for name, status in health_data['services'].items() 
                if not status.get('healthy', True)
            ]
            
            if service_issues:
                health_data['status'] = 'degraded'
                health_data['issues'] = service_issues
            
            return health_data
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _get_claude_status(self) -> str:
        """Get Claude-specific status"""
        llm_service = self.services.get('llm')
        if not llm_service:
            return 'service_unavailable'
        
        health = llm_service.get_health_status()
        claude_health = health.get('claude', {})
        
        if claude_health.get('available'):
            return 'connected'
        elif claude_health.get('enabled') and claude_health.get('api_key_configured'):
            return 'configured_but_failed'
        elif claude_health.get('enabled'):
            return 'enabled_no_key'
        else:
            return 'disabled'
    
    def _get_gemini_status(self) -> str:
        """Get Gemini-specific status"""
        llm_service = self.services.get('llm')
        if not llm_service:
            return 'service_unavailable'
        
        health = llm_service.get_health_status()
        gemini_health = health.get('gemini', {})
        
        if gemini_health.get('available'):
            return 'connected'
        elif gemini_health.get('enabled') and gemini_health.get('api_key_configured'):
            return 'configured_but_failed'
        elif gemini_health.get('enabled'):
            return 'enabled_no_key'
        else:
            return 'disabled'
    
    def _get_environment_info(self) -> Dict:
        """Get environment information"""
        return {
            'python_version': sys.version,
            'platform': sys.platform,
            'config_valid': Config.validate_config(),
            'enabled_providers': Config.get_enabled_llm_providers()
        }
    
    def _check_all_services(self) -> Dict:
        """Check all services health"""
        services_health = {}
        
        # Database Health
        services_health['database'] = self._check_database_health()
        
        # LLM Service Health
        services_health['llm_service'] = self._check_llm_service_health()
        
        # Property Service Health
        services_health['property_service'] = self._check_property_service_health()
        
        return services_health
    
    def _check_database_health(self) -> Dict:
        """Check database service health"""
        db = self.services.get('database')
        if not db:
            return {
                'healthy': False,
                'status': 'not_initialized',
                'error': 'Database service not available'
            }
        
        try:
            # Test database connection with stats query
            stats = db.get_database_stats()
            return {
                'healthy': True,
                'status': 'connected',
                'stats': stats,
                'database_path': Config.DATABASE_PATH
            }
        except Exception as e:
            return {
                'healthy': False,
                'status': 'connection_failed',
                'error': str(e)
            }
    
    def _check_llm_service_health(self) -> Dict:
        """Check LLM service health"""
        llm_service = self.services.get('llm')
        if not llm_service:
            return {
                'healthy': False,
                'status': 'not_initialized',
                'error': 'LLM service not available'
            }
        
        try:
            health_status = llm_service.get_health_status()
            available_providers = llm_service.get_available_providers()
            
            return {
                'healthy': len(available_providers) > 0,
                'status': 'operational' if available_providers else 'no_providers',
                'providers': health_status,
                'available_providers': available_providers
            }
        except Exception as e:
            return {
                'healthy': False,
                'status': 'health_check_failed',
                'error': str(e)
            }
    
    def _check_property_service_health(self) -> Dict:
        """Check property analysis service health"""
        property_service = self.services.get('property')
        if not property_service:
            return {
                'healthy': False,
                'status': 'not_initialized',
                'error': 'Property service not available'
            }
        
        # Property service health depends on LLM service
        llm_health = self._check_llm_service_health()
        
        return {
            'healthy': llm_health['healthy'],
            'status': 'operational' if llm_health['healthy'] else 'dependent_service_failed',
            'depends_on': 'llm_service',
            'llm_status': llm_health['status']
        }
    
    def _check_configuration(self) -> Dict:
        """Check configuration status"""
        return {
            'valid': Config.validate_config(),
            'api_keys': {
                'claude_configured': bool(Config.CLAUDE_API_KEY),
                'gemini_configured': bool(Config.GEMINI_API_KEY),
                'openai_configured': bool(Config.OPENAI_API_KEY)
            },
            'feature_flags': {
                'claude_enabled': Config.CLAUDE_ENABLED,
                'gemini_enabled': Config.GEMINI_ENABLED
            },
            'timeouts': {
                'llm_timeout': Config.LLM_TIMEOUT,
                'max_retries': Config.LLM_MAX_RETRIES
            }
        }
    
    def _check_llm_providers(self) -> Dict:
        """Detailed LLM provider health checks"""
        llm_service = self.services.get('llm')
        if not llm_service:
            return {
                'available': [],
                'details': {}
            }
        
        health_status = llm_service.get_health_status()
        
        provider_details = {}
        
        # Claude details
        claude_info = health_status.get('claude', {})
        provider_details['claude'] = {
            'enabled': claude_info.get('enabled', False),
            'api_key_configured': claude_info.get('api_key_configured', False),
            'client_available': claude_info.get('available', False),
            'working_model': claude_info.get('working_model'),
            'supported_models': Config.CLAUDE_MODELS
        }
        
        # Gemini details  
        gemini_info = health_status.get('gemini', {})
        provider_details['gemini'] = {
            'enabled': gemini_info.get('enabled', False),
            'api_key_configured': gemini_info.get('api_key_configured', False),
            'client_available': gemini_info.get('available', False),
            'working_model': gemini_info.get('working_model'),
            'supported_models': Config.GEMINI_MODELS
        }
        
        return {
            'available': llm_service.get_available_providers(),
            'details': provider_details
        }
    
    def perform_deep_health_check(self) -> Dict:
        """Perform deep health check with actual API calls"""
        deep_check = {
            'timestamp': datetime.now().isoformat(),
            'basic_health': self.get_comprehensive_health(),
            'api_tests': {}
        }
        
        llm_service = self.services.get('llm')
        if llm_service:
            # Test Claude with minimal call
            if llm_service.claude_client:
                try:
                    claude_test = llm_service.analyze_with_claude("Test connection")
                    deep_check['api_tests']['claude'] = {
                        'success': claude_test['success'],
                        'response_time': claude_test.get('processing_time', 0),
                        'model_used': claude_test.get('model_used'),
                        'error': claude_test.get('error')
                    }
                except Exception as e:
                    deep_check['api_tests']['claude'] = {
                        'success': False,
                        'error': str(e)
                    }
            
            # Test Gemini with minimal call
            if llm_service.gemini_model:
                try:
                    gemini_test = llm_service.analyze_with_gemini("Test connection")
                    deep_check['api_tests']['gemini'] = {
                        'success': gemini_test['success'],
                        'response_time': gemini_test.get('processing_time', 0),
                        'model_used': gemini_test.get('model_used'),
                        'error': gemini_test.get('error')
                    }
                except Exception as e:
                    deep_check['api_tests']['gemini'] = {
                        'success': False,
                        'error': str(e)
                    }
        
        return deep_check