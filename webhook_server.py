#!/usr/bin/env python3
"""
Webhook server for handling WhatsApp and other integrations
Simple Flask server to receive and respond to messages
"""

from flask import Flask, request, jsonify
import json
import logging
from integrations.integration_manager import IntegrationManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize integration manager
integration_manager = IntegrationManager()

@app.route('/', methods=['GET'])
def home():
    """Home page with integration status"""
    test_results = integration_manager.test_integrations()
    analytics = integration_manager.get_analytics()
    
    html = f"""
    <html>
    <head>
        <title>AI Customer Support - Integration Status</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .status {{ padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .enabled {{ background-color: #d4edda; color: #155724; }}
            .disabled {{ background-color: #f8d7da; color: #721c24; }}
            .analytics {{ background-color: #e2e3e5; padding: 15px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <h1>🤖 AI Customer Support System</h1>
        <h2>Integration Status</h2>
        
        <div class="status {'enabled' if test_results.get('whatsapp', {}).get('enabled') else 'disabled'}">
            📱 WhatsApp: {'✅ Enabled' if test_results.get('whatsapp', {}).get('enabled') else '❌ Disabled'}
        </div>
        
        <div class="status {'enabled' if test_results.get('email', {}).get('enabled') else 'disabled'}">
            📧 Email: {'✅ Enabled' if test_results.get('email', {}).get('enabled') else '❌ Disabled'}
        </div>
        
        <div class="status {'enabled' if test_results.get('chatbot', {}).get('enabled') else 'disabled'}">
            🤖 Chatbot: {'✅ Ready' if test_results.get('chatbot', {}).get('enabled') else '❌ Not Ready'}
            {f"({test_results.get('chatbot', {}).get('qa_pairs', 0)} Q&A pairs)" if test_results.get('chatbot', {}).get('enabled') else ''}
        </div>
        
        <h2>Analytics</h2>
        <div class="analytics">
            <p><strong>Total Conversations:</strong> {analytics.get('total_conversations', 0)}</p>
            <p><strong>Channels:</strong> {json.dumps(analytics.get('channels', {}))}</p>
            <p><strong>Average Response Length:</strong> {analytics.get('avg_response_length', 0):.0f} characters</p>
        </div>
        
        <h2>Webhook Endpoints</h2>
        <ul>
            <li><strong>WhatsApp:</strong> POST /webhook/whatsapp</li>
            <li><strong>Email Test:</strong> POST /webhook/email</li>
            <li><strong>Test Message:</strong> POST /test</li>
        </ul>
        
        <h2>Setup Instructions</h2>
        <p>Configure your API keys in the <code>.env</code> file and enable integrations in <code>integration_config.json</code></p>
    </body>
    </html>
    """
    return html

@app.route('/webhook/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Handle incoming WhatsApp messages"""
    try:
        # Get message data from Twilio
        from_number = request.form.get('From', '')
        message_body = request.form.get('Body', '')
        message_sid = request.form.get('MessageSid', '')
        
        logger.info(f"📱 WhatsApp webhook: {from_number} -> {message_body}")
        
        # Handle message using integration manager
        result = integration_manager.handle_whatsapp_message(from_number, message_body)
        
        if result['success']:
            logger.info(f"✅ WhatsApp response sent: {result['ai_response'][:50]}...")
            return jsonify({
                'status': 'success',
                'message': 'Response sent successfully'
            })
        else:
            logger.error(f"❌ WhatsApp error: {result.get('error')}")
            return jsonify({
                'status': 'error',
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        logger.error(f"❌ WhatsApp webhook error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/webhook/email', methods=['POST'])
def email_webhook():
    """Handle email webhook (for testing)"""
    try:
        data = request.get_json()
        
        # Simulate email data
        email_data = {
            'from': data.get('from', 'test@example.com'),
            'subject': data.get('subject', 'Test Email'),
            'content': data.get('content', 'This is a test email'),
            'date': data.get('date', '2025-08-28'),
            'id': 'webhook_test'
        }
        
        logger.info(f"📧 Email webhook: {email_data['from']} -> {email_data['subject']}")
        
        # Handle email using integration manager
        result = integration_manager.handle_email_message(email_data)
        
        if result['success']:
            logger.info(f"✅ Email response generated: {result['ai_response'][:50]}...")
            return jsonify({
                'status': 'success',
                'ai_response': result['ai_response'],
                'message': 'Response generated successfully'
            })
        else:
            logger.error(f"❌ Email error: {result.get('error')}")
            return jsonify({
                'status': 'error',
                'error': result.get('error')
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Email webhook error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/test', methods=['POST'])
def test_message():
    """Test endpoint for sending messages"""
    try:
        data = request.get_json()
        message = data.get('message', 'Hello, this is a test message')
        
        logger.info(f"🧪 Test message: {message}")
        
        # Get AI response
        if integration_manager.chatbot:
            response = integration_manager.chatbot.get_response(message)
            
            if response['success']:
                return jsonify({
                    'status': 'success',
                    'user_message': message,
                    'ai_response': response['response'],
                    'context_sources': len(response['relevant_context']),
                    'response_time': response.get('response_time', 0)
                })
            else:
                return jsonify({
                    'status': 'error',
                    'error': response.get('error', 'AI response failed')
                }), 500
        else:
            return jsonify({
                'status': 'error',
                'error': 'Chatbot not initialized'
            }), 500
            
    except Exception as e:
        logger.error(f"❌ Test endpoint error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/analytics', methods=['GET'])
def get_analytics():
    """Get conversation analytics"""
    try:
        analytics = integration_manager.get_analytics()
        test_results = integration_manager.test_integrations()
        
        return jsonify({
            'analytics': analytics,
            'integration_status': test_results,
            'timestamp': integration_manager.message_history[-1]['timestamp'] if integration_manager.message_history else None
        })
        
    except Exception as e:
        logger.error(f"❌ Analytics error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/config', methods=['GET', 'POST'])
def manage_config():
    """Get or update configuration"""
    if request.method == 'GET':
        # Return current config (without sensitive data)
        config = integration_manager.config.copy()
        
        # Remove sensitive information
        if 'whatsapp' in config:
            config['whatsapp'].pop('auth_token', None)
        if 'email' in config:
            config['email'].pop('password', None)
        
        return jsonify(config)
    
    elif request.method == 'POST':
        try:
            new_config = request.get_json()
            
            # Update configuration
            integration_manager.config.update(new_config)
            integration_manager.save_config(integration_manager.config)
            
            # Reinitialize integrations
            integration_manager.init_integrations()
            
            return jsonify({
                'status': 'success',
                'message': 'Configuration updated successfully'
            })
            
        except Exception as e:
            logger.error(f"❌ Config update error: {e}")
            return jsonify({
                'status': 'error',
                'error': str(e)
            }), 500

if __name__ == '__main__':
    print("🚀 Starting AI Customer Support Webhook Server...")
    print("📱 WhatsApp webhook: http://localhost:5000/webhook/whatsapp")
    print("📧 Email webhook: http://localhost:5000/webhook/email")
    print("🧪 Test endpoint: http://localhost:5000/test")
    print("📊 Analytics: http://localhost:5000/analytics")
    print("⚙️ Configuration: http://localhost:5000/config")
    print("🏠 Home: http://localhost:5000/")
    
    # Run Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)