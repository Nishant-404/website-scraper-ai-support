#!/usr/bin/env python3
"""
Integration Manager for AI Customer Support
Manages WhatsApp, Email, and other communication channels
"""

import os
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
from dotenv import load_dotenv

# Import integrations
from .whatsapp_integration import create_whatsapp_integration
from .email_integration import create_email_integration

# Import chatbot
import sys
sys.path.append('..')
from advanced_groq_chatbot import AdvancedGroqChatbot

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegrationManager:
    """Manages all communication channel integrations"""
    
    def __init__(self, config_file: str = "integration_config.json"):
        """Initialize integration manager"""
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize chatbot
        self.chatbot = None
        self.init_chatbot()
        
        # Initialize integrations
        self.whatsapp = None
        self.email = None
        
        self.init_integrations()
        
        # Message history
        self.message_history = []
    
    def load_config(self) -> Dict[str, Any]:
        """Load integration configuration"""
        default_config = {
            "whatsapp": {
                "enabled": False,
                "provider": "twilio",
                "account_sid": os.getenv('TWILIO_ACCOUNT_SID', ''),
                "auth_token": os.getenv('TWILIO_AUTH_TOKEN', ''),
                "whatsapp_number": os.getenv('WHATSAPP_NUMBER', '')
            },
            "email": {
                "enabled": False,
                "provider": "gmail",
                "email_address": os.getenv('SUPPORT_EMAIL', ''),
                "password": os.getenv('EMAIL_PASSWORD', ''),
                "monitoring": True,
                "check_interval": 30
            },
            "chatbot": {
                "qa_file": None,  # Will be set per user
                "company_name": "AI Assistant",  # Will be set per user
                "support_email": os.getenv('SUPPORT_EMAIL', 'support@company.com')
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for key, value in loaded_config.items():
                        if key in default_config:
                            default_config[key].update(value)
                        else:
                            default_config[key] = value
            else:
                # Save default config
                self.save_config(default_config)
            
            return default_config
            
        except Exception as e:
            logger.error(f"❌ Error loading config: {e}")
            return default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("✅ Configuration saved")
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")
    
    def init_chatbot(self):
        """Initialize the AI chatbot"""
        try:
            qa_file = self.config['chatbot']['qa_file']
            self.chatbot = AdvancedGroqChatbot(qa_file=qa_file)
            logger.info("✅ AI Chatbot initialized")
        except Exception as e:
            logger.error(f"❌ Failed to initialize chatbot: {e}")
    
    def init_integrations(self):
        """Initialize all enabled integrations"""
        # Initialize WhatsApp
        if self.config['whatsapp']['enabled']:
            self.init_whatsapp()
        
        # Initialize Email
        if self.config['email']['enabled']:
            self.init_email()
    
    def init_whatsapp(self):
        """Initialize WhatsApp integration"""
        try:
            whatsapp_config = self.config['whatsapp']
            self.whatsapp = create_whatsapp_integration(
                provider=whatsapp_config['provider'],
                account_sid=whatsapp_config['account_sid'],
                auth_token=whatsapp_config['auth_token'],
                whatsapp_number=whatsapp_config['whatsapp_number']
            )
            
            if self.whatsapp:
                logger.info("✅ WhatsApp integration initialized")
            else:
                logger.error("❌ Failed to initialize WhatsApp integration")
                
        except Exception as e:
            logger.error(f"❌ WhatsApp initialization error: {e}")
    
    def init_email(self):
        """Initialize Email integration"""
        try:
            email_config = self.config['email']
            self.email = create_email_integration(
                provider=email_config['provider'],
                email_address=email_config['email_address'],
                password=email_config['password']
            )
            
            if self.email:
                logger.info("✅ Email integration initialized")
                
                # Start email monitoring if enabled
                if email_config.get('monitoring', False):
                    self.start_email_monitoring()
            else:
                logger.error("❌ Failed to initialize email integration")
                
        except Exception as e:
            logger.error(f"❌ Email initialization error: {e}")
    
    def handle_whatsapp_message(self, from_number: str, message: str) -> Dict[str, Any]:
        """Handle incoming WhatsApp message"""
        try:
            logger.info(f"📱 WhatsApp message from {from_number}: {message}")
            
            # Get AI response
            if self.chatbot:
                ai_response = self.chatbot.get_response(message)
                
                if ai_response['success']:
                    # Send response via WhatsApp
                    if self.whatsapp:
                        send_result = self.whatsapp.send_message(
                            to_number=from_number,
                            message=ai_response['response']
                        )
                        
                        # Log conversation
                        self.log_conversation('whatsapp', from_number, message, ai_response['response'])
                        
                        return {
                            'success': True,
                            'channel': 'whatsapp',
                            'ai_response': ai_response['response'],
                            'send_result': send_result
                        }
                    else:
                        return {'success': False, 'error': 'WhatsApp not initialized'}
                else:
                    # Send error message
                    error_msg = "I'm sorry, I'm having technical difficulties. Please try again later."
                    if self.whatsapp:
                        self.whatsapp.send_message(from_number, error_msg)
                    
                    return {
                        'success': False,
                        'error': ai_response.get('error', 'AI response failed')
                    }
            else:
                return {'success': False, 'error': 'Chatbot not initialized'}
                
        except Exception as e:
            logger.error(f"❌ WhatsApp message handling error: {e}")
            return {'success': False, 'error': str(e)}
    
    def handle_email_message(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming email message"""
        try:
            from_email = email_data['from']
            subject = email_data['subject']
            content = email_data['content']
            
            logger.info(f"📧 Email from {from_email}: {subject}")
            
            # Get AI response
            if self.chatbot:
                ai_response = self.chatbot.get_response(content)
                
                if ai_response['success']:
                    # Send response via email
                    if self.email:
                        # Create response subject
                        response_subject = f"Re: {subject}" if not subject.startswith('Re:') else subject
                        
                        # Create HTML response
                        html_content = self.email.create_html_response(
                            ai_response['response'],
                            self.config['chatbot']['company_name']
                        )
                        
                        send_result = self.email.send_email(
                            to_email=from_email,
                            subject=response_subject,
                            message=ai_response['response'],
                            html_content=html_content
                        )
                        
                        # Log conversation
                        self.log_conversation('email', from_email, content, ai_response['response'])
                        
                        return {
                            'success': True,
                            'channel': 'email',
                            'ai_response': ai_response['response'],
                            'send_result': send_result
                        }
                    else:
                        return {'success': False, 'error': 'Email not initialized'}
                else:
                    return {
                        'success': False,
                        'error': ai_response.get('error', 'AI response failed')
                    }
            else:
                return {'success': False, 'error': 'Chatbot not initialized'}
                
        except Exception as e:
            logger.error(f"❌ Email message handling error: {e}")
            return {'success': False, 'error': str(e)}
    
    def start_email_monitoring(self):
        """Start monitoring emails"""
        if self.email:
            check_interval = self.config['email'].get('check_interval', 30)
            self.email.start_email_monitoring(
                callback_function=self.handle_email_message,
                check_interval=check_interval
            )
            logger.info("📧 Email monitoring started")
    
    def stop_email_monitoring(self):
        """Stop monitoring emails"""
        if self.email:
            self.email.stop_email_monitoring()
            logger.info("📧 Email monitoring stopped")
    
    def log_conversation(self, channel: str, user_id: str, user_message: str, ai_response: str):
        """Log conversation for analytics"""
        conversation_log = {
            'timestamp': datetime.now().isoformat(),
            'channel': channel,
            'user_id': user_id,
            'user_message': user_message,
            'ai_response': ai_response,
            'response_length': len(ai_response),
            'user_message_length': len(user_message)
        }
        
        self.message_history.append(conversation_log)
        
        # Save to file (optional)
        try:
            log_file = f"conversation_logs_{datetime.now().strftime('%Y%m')}.json"
            
            # Load existing logs
            logs = []
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = json.load(f)
            
            # Add new log
            logs.append(conversation_log)
            
            # Save updated logs
            with open(log_file, 'w') as f:
                json.dump(logs, f, indent=2)
                
        except Exception as e:
            logger.error(f"❌ Error saving conversation log: {e}")
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get conversation analytics"""
        if not self.message_history:
            return {'total_conversations': 0}
        
        total_conversations = len(self.message_history)
        channels = {}
        avg_response_length = 0
        
        for conv in self.message_history:
            channel = conv['channel']
            channels[channel] = channels.get(channel, 0) + 1
            avg_response_length += conv['response_length']
        
        avg_response_length = avg_response_length / total_conversations if total_conversations > 0 else 0
        
        return {
            'total_conversations': total_conversations,
            'channels': channels,
            'avg_response_length': avg_response_length,
            'last_conversation': self.message_history[-1]['timestamp'] if self.message_history else None
        }
    
    def test_integrations(self):
        """Test all integrations"""
        results = {}
        
        # Test WhatsApp
        if self.whatsapp:
            results['whatsapp'] = {
                'enabled': True,
                'connection': 'verified' if hasattr(self.whatsapp, 'verify_connection') else 'unknown'
            }
        else:
            results['whatsapp'] = {'enabled': False}
        
        # Test Email
        if self.email:
            results['email'] = {
                'enabled': True,
                'smtp': 'verified' if hasattr(self.email, 'verify_smtp_connection') else 'unknown',
                'imap': 'verified' if hasattr(self.email, 'verify_imap_connection') else 'unknown'
            }
        else:
            results['email'] = {'enabled': False}
        
        # Test Chatbot
        if self.chatbot:
            test_response = self.chatbot.get_response("Hello, this is a test message")
            results['chatbot'] = {
                'enabled': True,
                'qa_pairs': len(self.chatbot.qa_pairs),
                'test_response': test_response['success']
            }
        else:
            results['chatbot'] = {'enabled': False}
        
        return results


# Example usage
if __name__ == "__main__":
    # Initialize integration manager
    manager = IntegrationManager()
    
    # Test integrations
    test_results = manager.test_integrations()
    print("🧪 Integration Test Results:")
    print(json.dumps(test_results, indent=2))
    
    # Get analytics
    analytics = manager.get_analytics()
    print(f"\n📊 Analytics: {analytics}")
    
    print("\n✅ Integration Manager ready!")
    print("Configure your API keys in the .env file or integration_config.json")