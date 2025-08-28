#!/usr/bin/env python3
"""
WhatsApp Integration for AI Customer Support
Supports multiple WhatsApp API providers
"""

import json
import requests
import os
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WhatsAppIntegration:
    """WhatsApp integration using Twilio API (most reliable option)"""
    
    def __init__(self, account_sid: str, auth_token: str, whatsapp_number: str):
        """
        Initialize WhatsApp integration
        
        Args:
            account_sid: Twilio Account SID
            auth_token: Twilio Auth Token  
            whatsapp_number: Your WhatsApp Business number (format: whatsapp:+1234567890)
        """
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.whatsapp_number = whatsapp_number
        self.base_url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}"
        
        # Verify credentials
        self.verify_connection()
    
    def verify_connection(self) -> bool:
        """Verify Twilio connection"""
        try:
            response = requests.get(
                f"{self.base_url}.json",
                auth=(self.account_sid, self.auth_token)
            )
            if response.status_code == 200:
                logger.info("✅ WhatsApp (Twilio) connection verified")
                return True
            else:
                logger.error(f"❌ WhatsApp connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ WhatsApp connection error: {e}")
            return False
    
    def send_message(self, to_number: str, message: str, media_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Send WhatsApp message
        
        Args:
            to_number: Recipient WhatsApp number (format: whatsapp:+1234567890)
            message: Message text
            media_url: Optional media URL for images/documents
            
        Returns:
            Dict with success status and message details
        """
        try:
            # Prepare message data
            data = {
                'From': self.whatsapp_number,
                'To': to_number,
                'Body': message
            }
            
            # Add media if provided
            if media_url:
                data['MediaUrl'] = media_url
            
            # Send message via Twilio
            response = requests.post(
                f"{self.base_url}/Messages.json",
                auth=(self.account_sid, self.auth_token),
                data=data
            )
            
            if response.status_code == 201:
                result = response.json()
                logger.info(f"✅ WhatsApp message sent to {to_number}")
                return {
                    'success': True,
                    'message_sid': result.get('sid'),
                    'status': result.get('status'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"❌ Failed to send WhatsApp message: {response.text}")
                return {
                    'success': False,
                    'error': response.text,
                    'status_code': response.status_code
                }
                
        except Exception as e:
            logger.error(f"❌ WhatsApp send error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_message_status(self, message_sid: str) -> Dict[str, Any]:
        """Get status of sent message"""
        try:
            response = requests.get(
                f"{self.base_url}/Messages/{message_sid}.json",
                auth=(self.account_sid, self.auth_token)
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {'error': f'Failed to get status: {response.status_code}'}
                
        except Exception as e:
            return {'error': str(e)}
    
    def format_whatsapp_number(self, phone_number: str) -> str:
        """Format phone number for WhatsApp API"""
        # Remove any non-digit characters
        clean_number = ''.join(filter(str.isdigit, phone_number))
        
        # Add country code if not present (assuming India +91)
        if not clean_number.startswith('91') and len(clean_number) == 10:
            clean_number = '91' + clean_number
        
        return f"whatsapp:+{clean_number}"
    
    def create_webhook_handler(self, chatbot_instance):
        """
        Create webhook handler for incoming WhatsApp messages
        This would be used in a web framework like Flask/FastAPI
        """
        def handle_webhook(request_data):
            try:
                # Extract message details
                from_number = request_data.get('From', '')
                message_body = request_data.get('Body', '')
                message_sid = request_data.get('MessageSid', '')
                
                logger.info(f"📱 Received WhatsApp message from {from_number}: {message_body}")
                
                # Get AI response using chatbot
                ai_response = chatbot_instance.get_response(message_body)
                
                if ai_response['success']:
                    # Send AI response back via WhatsApp
                    response_result = self.send_message(
                        to_number=from_number,
                        message=ai_response['response']
                    )
                    
                    return {
                        'status': 'success',
                        'ai_response': ai_response['response'],
                        'whatsapp_result': response_result
                    }
                else:
                    # Send error message
                    error_msg = "I'm sorry, I'm having technical difficulties. Please try again later."
                    self.send_message(from_number, error_msg)
                    
                    return {
                        'status': 'error',
                        'error': ai_response.get('error', 'Unknown error')
                    }
                    
            except Exception as e:
                logger.error(f"❌ Webhook error: {e}")
                return {'status': 'error', 'error': str(e)}
        
        return handle_webhook


class WhatsAppWebAPI:
    """Alternative WhatsApp integration using web-based APIs (less reliable but easier)"""
    
    def __init__(self, api_url: str, api_key: str):
        """
        Initialize WhatsApp Web API integration
        
        Args:
            api_url: WhatsApp Web API endpoint
            api_key: API key for authentication
        """
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def send_message(self, phone_number: str, message: str) -> Dict[str, Any]:
        """Send message via WhatsApp Web API"""
        try:
            data = {
                'phone': phone_number,
                'message': message
            }
            
            response = requests.post(
                f"{self.api_url}/send-message",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 200:
                logger.info(f"✅ WhatsApp Web message sent to {phone_number}")
                return {
                    'success': True,
                    'response': response.json()
                }
            else:
                logger.error(f"❌ WhatsApp Web API error: {response.text}")
                return {
                    'success': False,
                    'error': response.text
                }
                
        except Exception as e:
            logger.error(f"❌ WhatsApp Web API error: {e}")
            return {
                'success': False,
                'error': str(e)
            }


def create_whatsapp_integration(provider: str = "twilio", **kwargs) -> Optional[WhatsAppIntegration]:
    """
    Factory function to create WhatsApp integration
    
    Args:
        provider: 'twilio' or 'web_api'
        **kwargs: Provider-specific configuration
    """
    try:
        if provider == "twilio":
            return WhatsAppIntegration(
                account_sid=kwargs.get('account_sid'),
                auth_token=kwargs.get('auth_token'),
                whatsapp_number=kwargs.get('whatsapp_number')
            )
        elif provider == "web_api":
            return WhatsAppWebAPI(
                api_url=kwargs.get('api_url'),
                api_key=kwargs.get('api_key')
            )
        else:
            logger.error(f"❌ Unknown WhatsApp provider: {provider}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to create WhatsApp integration: {e}")
        return None


# Example usage and testing
if __name__ == "__main__":
    # Example configuration (use environment variables in production)
    config = {
        'account_sid': os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid'),
        'auth_token': os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token'),
        'whatsapp_number': os.getenv('WHATSAPP_NUMBER', 'whatsapp:+1234567890')
    }
    
    # Create WhatsApp integration
    whatsapp = create_whatsapp_integration('twilio', **config)
    
    if whatsapp:
        # Test message (uncomment to test)
        # result = whatsapp.send_message(
        #     to_number='whatsapp:+919876543210',
        #     message='Hello! This is a test message from your AI customer support system.'
        # )
        # print(f"Send result: {result}")
        
        print("✅ WhatsApp integration ready!")
    else:
        print("❌ Failed to initialize WhatsApp integration")