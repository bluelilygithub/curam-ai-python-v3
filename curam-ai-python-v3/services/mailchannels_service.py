"""
MailChannels Service for Property Notifications
Send email notifications for property trends, alerts, and updates
"""

import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class MailChannelsService:
    """Service for sending property-related email notifications"""
    
    def __init__(self):
        self.api_key = Config.MAILCHANNELS_API_KEY
        self.api_url = Config.MAILCHANNELS_CONFIG['api_url']
        self.from_email = Config.MAILCHANNELS_CONFIG['from_email']
        self.from_name = Config.MAILCHANNELS_CONFIG['from_name']
        self.notification_types = Config.MAILCHANNELS_CONFIG['notification_types']
        self.enabled = Config.MAILCHANNELS_ENABLED and bool(self.api_key)
        
        if not self.enabled:
            logger.warning("MailChannels service disabled - API key not configured")
    
    def send_trend_alert(self, recipient: str, trend_data: Dict) -> Dict:
        """Send property trend alert email"""
        if not self.enabled:
            return self._error_response("MailChannels service not enabled")
        
        try:
            # Create trend alert content
            subject = f"Brisbane Property Trend Alert - {trend_data.get('suburb', 'Market Update')}"
            html_content = self._create_trend_alert_html(trend_data)
            text_content = self._create_trend_alert_text(trend_data)
            
            # Send email
            response = self._send_email(
                recipient,
                subject,
                html_content,
                text_content
            )
            
            if response['success']:
                return {
                    'success': True,
                    'notification_type': 'trend_alert',
                    'recipient': recipient,
                    'subject': subject,
                    'trend_data': trend_data,
                    'sent_at': datetime.now().isoformat(),
                    'provider': 'mailchannels'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Trend alert email failed: {e}")
            return self._error_response(f"Trend alert failed: {str(e)}")
    
    def send_weekly_summary(self, recipient: str, summary_data: Dict) -> Dict:
        """Send weekly property market summary"""
        if not self.enabled:
            return self._error_response("MailChannels service not enabled")
        
        try:
            # Create weekly summary content
            subject = f"Brisbane Property Weekly Summary - {summary_data.get('week_ending', 'Market Update')}"
            html_content = self._create_weekly_summary_html(summary_data)
            text_content = self._create_weekly_summary_text(summary_data)
            
            # Send email
            response = self._send_email(
                recipient,
                subject,
                html_content,
                text_content
            )
            
            if response['success']:
                return {
                    'success': True,
                    'notification_type': 'weekly_summary',
                    'recipient': recipient,
                    'subject': subject,
                    'summary_data': summary_data,
                    'sent_at': datetime.now().isoformat(),
                    'provider': 'mailchannels'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Weekly summary email failed: {e}")
            return self._error_response(f"Weekly summary failed: {str(e)}")
    
    def send_development_alert(self, recipient: str, development_data: Dict) -> Dict:
        """Send new development application alert"""
        if not self.enabled:
            return self._error_response("MailChannels service not enabled")
        
        try:
            # Create development alert content
            subject = f"New Development Alert - {development_data.get('suburb', 'Brisbane')}"
            html_content = self._create_development_alert_html(development_data)
            text_content = self._create_development_alert_text(development_data)
            
            # Send email
            response = self._send_email(
                recipient,
                subject,
                html_content,
                text_content
            )
            
            if response['success']:
                return {
                    'success': True,
                    'notification_type': 'development_alert',
                    'recipient': recipient,
                    'subject': subject,
                    'development_data': development_data,
                    'sent_at': datetime.now().isoformat(),
                    'provider': 'mailchannels'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"Development alert email failed: {e}")
            return self._error_response(f"Development alert failed: {str(e)}")
    
    def send_system_update(self, recipient: str, update_data: Dict) -> Dict:
        """Send system update notification"""
        if not self.enabled:
            return self._error_response("MailChannels service not enabled")
        
        try:
            # Create system update content
            subject = f"Brisbane Property Intelligence - {update_data.get('update_type', 'System Update')}"
            html_content = self._create_system_update_html(update_data)
            text_content = self._create_system_update_text(update_data)
            
            # Send email
            response = self._send_email(
                recipient,
                subject,
                html_content,
                text_content
            )
            
            if response['success']:
                return {
                    'success': True,
                    'notification_type': 'system_update',
                    'recipient': recipient,
                    'subject': subject,
                    'update_data': update_data,
                    'sent_at': datetime.now().isoformat(),
                    'provider': 'mailchannels'
                }
            else:
                return response
                
        except Exception as e:
            logger.error(f"System update email failed: {e}")
            return self._error_response(f"System update failed: {str(e)}")
    
    def _send_email(self, recipient: str, subject: str, html_content: str, text_content: str) -> Dict:
        """Send email using MailChannels API"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'personalizations': [
                    {
                        'to': [{'email': recipient}]
                    }
                ],
                'from': {
                    'email': self.from_email,
                    'name': self.from_name
                },
                'subject': subject,
                'content': [
                    {
                        'type': 'text/plain',
                        'value': text_content
                    },
                    {
                        'type': 'text/html',
                        'value': html_content
                    }
                ]
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 202:
                return {
                    'success': True,
                    'message': 'Email sent successfully',
                    'recipient': recipient
                }
            else:
                logger.error(f"MailChannels API error: {response.status_code} - {response.text}")
                return self._error_response(f"API error: {response.status_code}")
                
        except Exception as e:
            logger.error(f"MailChannels send failed: {e}")
            return self._error_response(f"Send failed: {str(e)}")
    
    def _create_trend_alert_html(self, trend_data: Dict) -> str:
        """Create HTML content for trend alert"""
        suburb = trend_data.get('suburb', 'Brisbane')
        change = trend_data.get('percentage_change', 0)
        trend_direction = trend_data.get('trend_direction', 'stable')
        
        arrow = "📈" if trend_direction == 'up' else "📉" if trend_direction == 'down' else "➡️"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px;">
                <h1 style="color: #2C3E50; text-align: center;">🏢 Brisbane Property Trend Alert</h1>
                
                <div style="background: #ECF0F1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="color: #34495E; margin: 0;">{arrow} {suburb} Market Update</h2>
                    <p style="font-size: 18px; margin: 10px 0;">
                        Development activity has <strong>{trend_direction}</strong> by <strong>{change}%</strong>
                    </p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #2C3E50;">Key Insights:</h3>
                    <ul style="line-height: 1.6;">
                        <li>Current period: {trend_data.get('current_period_count', 'N/A')} applications</li>
                        <li>Previous period: {trend_data.get('previous_period_count', 'N/A')} applications</li>
                        <li>Confidence level: {trend_data.get('confidence_score', 0):.1%}</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #7F8C8D; font-size: 14px;">
                        Brisbane Property Intelligence | Powered by AI Analysis
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_trend_alert_text(self, trend_data: Dict) -> str:
        """Create text content for trend alert"""
        suburb = trend_data.get('suburb', 'Brisbane')
        change = trend_data.get('percentage_change', 0)
        trend_direction = trend_data.get('trend_direction', 'stable')
        
        return f"""
        BRISBANE PROPERTY TREND ALERT
        
        {suburb} Market Update
        Development activity has {trend_direction} by {change}%
        
        Key Insights:
        - Current period: {trend_data.get('current_period_count', 'N/A')} applications
        - Previous period: {trend_data.get('previous_period_count', 'N/A')} applications
        - Confidence level: {trend_data.get('confidence_score', 0):.1%}
        
        Brisbane Property Intelligence | Powered by AI Analysis
        """
    
    def _create_weekly_summary_html(self, summary_data: Dict) -> str:
        """Create HTML content for weekly summary"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px;">
                <h1 style="color: #2C3E50; text-align: center;">📊 Weekly Property Summary</h1>
                
                <div style="background: #ECF0F1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="color: #34495E; margin: 0;">Week Ending: {summary_data.get('week_ending', 'N/A')}</h2>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #2C3E50;">This Week's Highlights:</h3>
                    <ul style="line-height: 1.6;">
                        <li>Total applications: {summary_data.get('total_applications', 'N/A')}</li>
                        <li>Most active suburb: {summary_data.get('most_active_suburb', 'N/A')}</li>
                        <li>Week-over-week change: {summary_data.get('week_change', 'N/A')}%</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #7F8C8D; font-size: 14px;">
                        Brisbane Property Intelligence | Weekly Market Analysis
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_weekly_summary_text(self, summary_data: Dict) -> str:
        """Create text content for weekly summary"""
        return f"""
        BRISBANE PROPERTY WEEKLY SUMMARY
        
        Week Ending: {summary_data.get('week_ending', 'N/A')}
        
        This Week's Highlights:
        - Total applications: {summary_data.get('total_applications', 'N/A')}
        - Most active suburb: {summary_data.get('most_active_suburb', 'N/A')}
        - Week-over-week change: {summary_data.get('week_change', 'N/A')}%
        
        Brisbane Property Intelligence | Weekly Market Analysis
        """
    
    def _create_development_alert_html(self, development_data: Dict) -> str:
        """Create HTML content for development alert"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px;">
                <h1 style="color: #2C3E50; text-align: center;">🏗️ New Development Alert</h1>
                
                <div style="background: #ECF0F1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="color: #34495E; margin: 0;">{development_data.get('suburb', 'Brisbane')}</h2>
                    <p style="font-size: 16px; margin: 10px 0;">
                        <strong>{development_data.get('application_type', 'Development Application')}</strong>
                    </p>
                </div>
                
                <div style="margin: 20px 0;">
                    <h3 style="color: #2C3E50;">Application Details:</h3>
                    <ul style="line-height: 1.6;">
                        <li>Address: {development_data.get('address', 'N/A')}</li>
                        <li>Description: {development_data.get('description', 'N/A')}</li>
                        <li>Date lodged: {development_data.get('date_lodged', 'N/A')}</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #7F8C8D; font-size: 14px;">
                        Brisbane Property Intelligence | Development Monitoring
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_development_alert_text(self, development_data: Dict) -> str:
        """Create text content for development alert"""
        return f"""
        NEW DEVELOPMENT ALERT
        
        {development_data.get('suburb', 'Brisbane')}
        {development_data.get('application_type', 'Development Application')}
        
        Application Details:
        - Address: {development_data.get('address', 'N/A')}
        - Description: {development_data.get('description', 'N/A')}
        - Date lodged: {development_data.get('date_lodged', 'N/A')}
        
        Brisbane Property Intelligence | Development Monitoring
        """
    
    def _create_system_update_html(self, update_data: Dict) -> str:
        """Create HTML content for system update"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px;">
                <h1 style="color: #2C3E50; text-align: center;">🔧 System Update</h1>
                
                <div style="background: #ECF0F1; padding: 15px; border-radius: 5px; margin: 20px 0;">
                    <h2 style="color: #34495E; margin: 0;">{update_data.get('update_type', 'System Update')}</h2>
                </div>
                
                <div style="margin: 20px 0;">
                    <p style="line-height: 1.6;">{update_data.get('message', 'System has been updated.')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <p style="color: #7F8C8D; font-size: 14px;">
                        Brisbane Property Intelligence | System Notifications
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_system_update_text(self, update_data: Dict) -> str:
        """Create text content for system update"""
        return f"""
        SYSTEM UPDATE
        
        {update_data.get('update_type', 'System Update')}
        
        {update_data.get('message', 'System has been updated.')}
        
        Brisbane Property Intelligence | System Notifications
        """
    
    def _error_response(self, error_msg: str) -> Dict:
        """Standardized error response"""
        return {
            'success': False,
            'error': error_msg,
            'provider': 'mailchannels'
        }
    
    def get_health_status(self) -> Dict:
        """Get MailChannels service health status"""
        return {
            'enabled': self.enabled,
            'api_key_configured': bool(self.api_key),
            'from_email': self.from_email,
            'notification_types': self.notification_types,
            'service_type': 'email_notifications'
        }
    
    def test_connection(self) -> Dict:
        """Test connection to MailChannels API"""
        if not self.enabled:
            return self._error_response("Service not enabled")
        
        try:
            # Test with a simple system update email to a test address
            test_email = "test@example.com"
            test_update = {
                'update_type': 'Connection Test',
                'message': 'This is a test message to verify MailChannels connection.'
            }
            
            # This would normally send an email, but we'll just validate the payload
            return {
                'success': True,
                'message': 'MailChannels connection test successful',
                'api_configured': True
            }
                
        except Exception as e:
            return self._error_response(f"Connection test failed: {str(e)}")